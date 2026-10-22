"""API REST local para estoque de TI e baixas relacionadas a chamados GLPI."""
from contextlib import asynccontextmanager
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from auth import AUTH_DISPLAY_NAME, authenticate, create_access_token, get_current_username
from database import Base, SessionLocal, engine, get_db
from models import Insumo, Movimentacao
from schemas import (
    BaixaCreate,
    InsumoCreate,
    InsumoRead,
    InsumoUpdate,
    LoginRequest,
    MensagemRead,
    MovimentacaoRead,
    ResumoRead,
    TokenRead,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Cria esquema e carrega catálogo fictício somente no banco vazio."""
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        if db.scalar(select(func.count()).select_from(Insumo)) == 0:
            db.add_all(
                [
                    Insumo(codigo="FON-ELG-BR240", nome="Fonte Elgin BR240", categoria="Fontes", saldo=1, estoque_minimo=2, unidade="un"),
                    Insumo(codigo="CAB-CAT6-001", nome="Cabo de rede Cat6", categoria="Cabos", saldo=25, estoque_minimo=10, unidade="un"),
                    Insumo(codigo="TON-HP-001", nome="Toner HP compatível", categoria="Toners", saldo=4, estoque_minimo=3, unidade="un"),
                ]
            )
            db.commit()
    yield


app = FastAPI(
    title="COREN-MA | Gestão de Insumos de TI",
    description="Controle local de estoque, com baixas vinculadas a chamados GLPI.",
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Necessário para a origem null de HTML local; sem cookies/credenciais.
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

CurrentUser = Annotated[str, Depends(get_current_username)]
Database = Annotated[Session, Depends(get_db)]


def _insumo_read(item: Insumo) -> InsumoRead:
    return InsumoRead(
        id=item.id,
        codigo=item.codigo,
        nome=item.nome,
        categoria=item.categoria,
        saldo=item.saldo,
        estoque_minimo=item.estoque_minimo,
        unidade=item.unidade,
        estoque_critico=item.saldo <= item.estoque_minimo,
    )


def _movement_read(movement: Movimentacao, item: Insumo) -> MovimentacaoRead:
    return MovimentacaoRead(
        id=movement.id,
        chamado_glpi_id=movement.chamado_glpi_id,
        insumo_id=movement.insumo_id,
        insumo_codigo=item.codigo,
        insumo_nome=item.nome,
        quantidade=movement.quantidade,
        observacao=movement.observacao,
        tecnico_responsavel=movement.tecnico_responsavel,
        data_hora=movement.data_hora,
    )


@app.get("/", tags=["Sistema"])
def raiz() -> dict[str, str]:
    return {"sistema": "COREN-MA Gestão de Insumos", "documentacao": "/docs"}


@app.post("/api/auth/token", response_model=TokenRead, tags=["Autenticação"])
def login(dados: LoginRequest) -> TokenRead:
    if not authenticate(dados.username, dados.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha inválidos.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token, expires_in = create_access_token(dados.username)
    return TokenRead(access_token=token, expires_in=expires_in)


@app.get("/api/insumos", response_model=list[InsumoRead], tags=["Insumos"])
def listar_insumos(
    db: Database,
    _: CurrentUser,
    busca: str | None = Query(default=None, max_length=120),
) -> list[InsumoRead]:
    consulta = select(Insumo).order_by(Insumo.nome)
    if busca and busca.strip():
        termo = f"%{busca.strip()}%"
        consulta = consulta.where(
            (Insumo.nome.ilike(termo)) | (Insumo.codigo.ilike(termo)) | (Insumo.categoria.ilike(termo))
        )
    return [_insumo_read(item) for item in db.scalars(consulta).all()]


@app.post("/api/insumos", response_model=InsumoRead, status_code=status.HTTP_201_CREATED, tags=["Insumos"])
def criar_insumo(dados: InsumoCreate, db: Database, _: CurrentUser) -> InsumoRead:
    item = Insumo(**dados.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe um insumo com esse código.") from exc
    db.refresh(item)
    return _insumo_read(item)


@app.post("/api/insumos/baixa", response_model=MovimentacaoRead, status_code=status.HTTP_201_CREATED, tags=["Movimentações"])
def registrar_baixa(dados: BaixaCreate, db: Database, _: CurrentUser) -> MovimentacaoRead:
    """Debita saldo e grava chamado/técnico em uma operação transacional."""
    if dados.tecnico_responsavel.strip() != AUTH_DISPLAY_NAME:
        raise HTTPException(status_code=403, detail="O técnico informado não corresponde ao usuário autenticado.")
    item = db.get(Insumo, dados.insumo_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado.")
    if dados.quantidade > item.saldo:
        raise HTTPException(
            status_code=422,
            detail=f"Saldo insuficiente para {item.nome}: solicitado {dados.quantidade} {item.unidade}, disponível {item.saldo}.",
        )

    resultado = db.execute(
        update(Insumo)
        .where(Insumo.id == dados.insumo_id, Insumo.saldo >= dados.quantidade)
        .values(saldo=Insumo.saldo - dados.quantidade)
    )
    if resultado.rowcount != 1:
        db.rollback()
        saldo_atual = db.scalar(select(Insumo.saldo).where(Insumo.id == dados.insumo_id))
        if saldo_atual is None:
            raise HTTPException(status_code=404, detail="Insumo não encontrado.")
        raise HTTPException(
            status_code=422,
            detail=f"Saldo insuficiente: solicitado {dados.quantidade}, disponível {saldo_atual}.",
        )

    movimento = Movimentacao(
        chamado_glpi_id=dados.chamado_glpi_id,
        insumo_id=dados.insumo_id,
        quantidade=dados.quantidade,
        observacao=dados.observacao,
        tecnico_responsavel=AUTH_DISPLAY_NAME,
    )
    db.add(movimento)
    db.commit()
    db.refresh(movimento)
    db.refresh(item)
    return _movement_read(movimento, item)


@app.get("/api/insumos/{insumo_id}", response_model=InsumoRead, tags=["Insumos"])
def obter_insumo(insumo_id: int, db: Database, _: CurrentUser) -> InsumoRead:
    item = db.get(Insumo, insumo_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado.")
    return _insumo_read(item)


@app.patch("/api/insumos/{insumo_id}", response_model=InsumoRead, tags=["Insumos"])
def atualizar_insumo(insumo_id: int, dados: InsumoUpdate, db: Database, _: CurrentUser) -> InsumoRead:
    item = db.get(Insumo, insumo_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado.")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(item, campo, valor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Código já utilizado por outro insumo.") from exc
    db.refresh(item)
    return _insumo_read(item)


@app.delete("/api/insumos/{insumo_id}", response_model=MensagemRead, tags=["Insumos"])
def excluir_insumo(insumo_id: int, db: Database, _: CurrentUser) -> MensagemRead:
    item = db.get(Insumo, insumo_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Insumo não encontrado.")
    if item.movimentacoes:
        raise HTTPException(status_code=409, detail="Não é possível excluir um insumo com movimentações registradas.")
    db.delete(item)
    db.commit()
    return MensagemRead(mensagem="Insumo removido.")


@app.get("/api/movimentacoes", response_model=list[MovimentacaoRead], tags=["Relatórios"])
def listar_movimentacoes(
    db: Database,
    _: CurrentUser,
    limite: int = Query(default=10, ge=1, le=100),
) -> list[MovimentacaoRead]:
    registros = db.execute(
        select(Movimentacao, Insumo)
        .join(Insumo, Movimentacao.insumo_id == Insumo.id)
        .order_by(Movimentacao.data_hora.desc(), Movimentacao.id.desc())
        .limit(limite)
    ).all()
    return [_movement_read(movement, item) for movement, item in registros]


@app.get("/api/relatorios/resumo", response_model=ResumoRead, tags=["Relatórios"])
def relatorio_resumo(db: Database, _: CurrentUser) -> ResumoRead:
    today = date.today().isoformat()
    total = db.scalar(select(func.count()).select_from(Insumo)) or 0
    criticos = db.scalar(select(func.count()).select_from(Insumo).where(Insumo.saldo <= Insumo.estoque_minimo)) or 0
    saldo_total = db.scalar(select(func.coalesce(func.sum(Insumo.saldo), 0))) or 0
    hoje = db.scalar(
        select(func.count()).select_from(Movimentacao).where(func.date(Movimentacao.data_hora) == today)
    ) or 0
    return ResumoRead(total_insumos=total, itens_criticos=criticos, saldo_total=saldo_total, movimentacoes_hoje=hoje)
