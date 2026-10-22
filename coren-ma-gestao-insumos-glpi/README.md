# COREN-MA — Gestão de Insumos de TI & GLPI

Aplicação acadêmica local para controle de materiais de TI. Registra baixas de estoque vinculadas a chamados GLPI, conserva histórico do técnico e horário, apresenta indicadores de estoque crítico e oferece telas responsivas com requisitos de acessibilidade como objetivo de projeto.

> **Limite importante:** o backend registra o número do chamado informado; não chama nem sincroniza com a API do GLPI. A URL exibida para consulta do chamado deve ser confirmada e ajustada pela instituição. O JWT e as credenciais padrão servem apenas para demonstração em máquina local.

# Estrutura 


coren-ma-gestao-insumos-glpi/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   ├── requirements.txt
│   └── estoque.db       # criado na primeira execução; ignorado pelo Git
├── frontend/
│   ├── tela1_dashboard.html
│   ├── tela2_formulario.html
│   └── tela3_resultado.html
├── docs/
│   └── requisitos_e_arquitetura.md
├── .gitignore
└── README.md
```



 Requisitos

- Python 3.10 ou superior.
- Navegador atualizado.
- Internet para carregar Bootstrap 5.3.3 via CDN; sem rede, a lógica funciona, mas o estilo Bootstrap não carrega.

## Instalação e execução — Windows PowerShell

Abra um terminal na raiz do projeto:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Defina credenciais locais **antes de iniciar** (troque a senha e gere uma chave longa e aleatória para `AUTH_SECRET`):

```powershell
$env:AUTH_USERNAME = "danilo"
$env:AUTH_PASSWORD = "defina-uma-senha-local-forte"
$env:AUTH_SECRET = "substitua-por-um-segredo-aleatorio-longo"
$env:AUTH_DISPLAY_NAME = "Danilo Lopes da Silva | Assessor de Tecnologia II"
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Para gerar uma chave local, use o gerador de segredos do seu sistema e não a publique. Não use os valores padrão em qualquer ambiente compartilhado. O token expira em uma hora.

A API estará em `http://localhost:8000`; Swagger em `http://localhost:8000/docs`. Na primeira inicialização cria `backend/estoque.db` e insere dados fictícios (Fonte Elgin BR240, Cabo Cat6 e toner). O seed só é incluído se o catálogo estiver vazio.

# Abrir o frontend

Abra `frontend/tela1_dashboard.html` diretamente no navegador ou com Live Server. O backend escuta em `127.0.0.1`; o CORS permite origem local `null` sem credenciais de cookie, para possibilitar `fetch` de arquivos HTML locais. Se preferir servir frontend por HTTP, configure CORS para essa origem antes de usar. As telas chamam `http://localhost:8000`.

No dashboard, entre com `AUTH_USERNAME` e `AUTH_PASSWORD` definidos no terminal. A tela de baixa compartilha o Bearer token apenas na sessão do navegador. Use **Registrar baixa**, selecione item, informe número do chamado GLPI, quantidade e observação. A operação é transacional: saldo é debitado e movimentação auditável gravada. O endpoint rejeita baixa acima do saldo com HTTP 422.

# Credenciais de demonstração

Se variáveis de ambiente não forem definidas, o padrão local do projeto é `danilo` / `admin123`. Troque imediatamente mesmo para demonstração compartilhada. O `AUTH_SECRET` padrão também é somente local e não deve ser considerado seguro.

# API

| Método | Rota | Requer token | Descrição |
|---|---|---:|---|
| `POST` | `/api/auth/token` | Não | Recebe `username` e `password`, retorna JWT Bearer |
| `GET` | `/api/insumos` | Sim | Lista itens (`?busca=` opcional) e informa `estoque_critico` |
| `POST` | `/api/insumos` | Sim | Cadastra insumo |
| `GET` | `/api/insumos/{id}` | Sim | Consulta item |
| `PATCH` | `/api/insumos/{id}` | Sim | Atualização parcial |
| `DELETE` | `/api/insumos/{id}` | Sim | Remove item sem histórico |
| `POST` | `/api/insumos/baixa` | Sim | Debita saldo e registra chamado/técnico/horário |
| `GET` | `/api/movimentacoes?limite=10` | Sim | Histórico recente (limite de 1 a 100) |
| `GET` | `/api/relatorios/resumo` | Sim | Contagem de itens, críticos, saldo e baixas do dia |

Exemplo do corpo para baixa:

```json
{
  "chamado_glpi_id": 12345,
  "insumo_id": 1,
  "quantidade": 1,
  "observacao": "Substituição de fonte no atendimento",
  "tecnico_responsavel": "Danilo Lopes da Silva | Assessor de Tecnologia II"
}
```

A API define o técnico salvo com base na configuração autenticada e rejeita divergência do valor enviado. O cadastro atual aceita saldo no POST/PATCH por conveniência de protótipo; em produção, alterações de saldo devem ocorrer exclusivamente por movimentações auditáveis.

# Persistência, backup e segurança

- Banco em arquivo: `backend/estoque.db`; faça cópia consistente com a aplicação parada. Defina rotina de retenção e teste a restauração.
- JWT com HS256 e validade de 60 minutos. O esquema é uma autenticação simulada de usuário único, sem bloqueio de tentativas, revogação de token, MFA ou controle de papéis.
- O endpoint de token não substitui autenticação institucional. Não colocar credenciais reais no frontend nem compartilhar o padrão `admin123`.
- CORS amplo é necessário para arquivos locais; a API deve permanecer limitada ao loopback. Não alterar `--host` para `0.0.0.0` sem definir origens, autenticação real e controles de rede.
- GLPI não é consultado nem validado automaticamente; não existe garantia de que o chamado informado esteja aberto ou pertença ao solicitante.
- Para uso real, adicionar migrações Alembic, testes, logs/auditoria protegidos, rate limit, política de sessão/CSRF apropriada, gestão de segredos e revisão de privacidade.
## Acessibilidade: Em conformidade com WCAG 2.1


