"""Schemas de entrada/saída estritos da API."""
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator


class StrictSchema(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class InsumoCreate(StrictSchema):
    codigo: StrictStr = Field(min_length=2, max_length=40)
    nome: StrictStr = Field(min_length=2, max_length=160)
    categoria: StrictStr = Field(min_length=2, max_length=80)
    saldo: StrictInt = Field(ge=0)
    estoque_minimo: StrictInt = Field(ge=0)
    unidade: StrictStr = Field(default="un", min_length=1, max_length=20)


class InsumoUpdate(StrictSchema):
    codigo: StrictStr | None = Field(default=None, min_length=2, max_length=40)
    nome: StrictStr | None = Field(default=None, min_length=2, max_length=160)
    categoria: StrictStr | None = Field(default=None, min_length=2, max_length=80)
    saldo: StrictInt | None = Field(default=None, ge=0)
    estoque_minimo: StrictInt | None = Field(default=None, ge=0)
    unidade: StrictStr | None = Field(default=None, min_length=1, max_length=20)


class InsumoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    nome: str
    categoria: str
    saldo: int
    estoque_minimo: int
    unidade: str
    estoque_critico: bool


class BaixaCreate(StrictSchema):
    chamado_glpi_id: StrictInt = Field(gt=0)
    insumo_id: StrictInt = Field(gt=0)
    quantidade: StrictInt = Field(gt=0)
    observacao: StrictStr | None = Field(default=None, max_length=1000)
    tecnico_responsavel: StrictStr = Field(min_length=3, max_length=120)


class MovimentacaoRead(BaseModel):
    id: int
    chamado_glpi_id: int
    insumo_id: int
    insumo_codigo: str
    insumo_nome: str
    quantidade: int
    observacao: str | None
    tecnico_responsavel: str
    data_hora: datetime


class LoginRequest(StrictSchema):
    username: StrictStr = Field(min_length=1, max_length=80)
    password: StrictStr = Field(min_length=1, max_length=200)


class TokenRead(BaseModel):
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    expires_in: int


class ResumoRead(BaseModel):
    total_insumos: int
    itens_criticos: int
    saldo_total: int
    movimentacoes_hoje: int


class MensagemRead(BaseModel):
    mensagem: str


class InsumoNome(BaseModel):
    id: int
    nome: str
    codigo: str
    saldo: int
    unidade: str
