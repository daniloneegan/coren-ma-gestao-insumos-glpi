# Requisitos e arquitetura — COREN-MA Gestão de Insumos de TI

## 1. Objetivo e escopo

Sistema web local para inventário de insumos de TI, com baixa associada a um identificador de chamado GLPI e registro de técnico, observação e data/hora. O backend mantém o saldo e fornece relatórios. O frontend oferece dashboard, formulário e confirmação.

**Não implementado:** integração real à API GLPI, validação do estado do chamado, login institucional/SSO, autorização por papéis e implantação em rede. A associação ao chamado é somente o registro do número fornecido pelo operador.

## 2. Arquitetura

- **Cliente:** três documentos HTML5 independentes com Bootstrap 5.3.3 e JavaScript Fetch.
- **API:** FastAPI, validação Pydantic 2, documentação OpenAPI automática, Bearer JWT simulado.
- **Persistência:** SQLAlchemy 2 com SQLite local em `backend/estoque.db`.
- **Domínio:** `Insumo` guarda código, nome, categoria, saldo, unidade e ponto mínimo. `Movimentacao` guarda chamado GLPI, insumo, quantidade, observação, técnico e timestamp.
- **Baixa:** transação SQL com atualização condicional de saldo (`saldo >= quantidade`) e inserção da movimentação na mesma transação. Isso impede saldo negativo mesmo em baixas concorrentes dentro do SQLite.
- **Seed:** catálogo fictício criado na inicialização apenas quando ainda não há insumos.
- **CORS:** permite chamadas sem cookies de páginas locais; backend deve ficar restrito a `127.0.0.1`.

## 3. Requisitos funcionais (RF)

| ID | Requisito | Critério de aceite |
|---|---|---|
| RF-01 | Inicializar banco e catálogo fictício automaticamente. | Banco e três registros são criados quando o catálogo está vazio; reiniciar não duplica seed. |
| RF-02 | Autenticar operador via endpoint de token. | Credenciais válidas emitem Bearer JWT com expiração; inválidas retornam 401. |
| RF-03 | Consultar e pesquisar insumos. | Listagem autenticada inclui estado crítico; busca parcial considera nome/código/categoria. |
| RF-04 | Cadastrar, atualizar e remover insumo. | CRUD autenticado; código único; impedir exclusão com histórico vinculado. |
| RF-05 | Registrar baixa vinculada a chamado GLPI. | Persistir chamado, item, quantidade, observação, técnico autenticado e timestamp. |
| RF-06 | Bloquear saldo insuficiente. | HTTP 422 explica saldo e quantidade; saldo e histórico permanecem inalterados. |
| RF-07 | Apresentar estoque crítico multimodal. | Dashboard/formulário mostram cor, ícone e texto “CRÍTICO”; saldo igual ou inferior ao mínimo é crítico. |
| RF-08 | Consultar histórico recente. | Exibir data, chamado, item, quantidade e técnico. |
| RF-09 | Apresentar relatório de resumo. | Informar total de itens, itens críticos, saldo total e baixas do dia. |
| RF-10 | Confirmar resultado da baixa. | Tela mostra detalhes vindos do retorno da API e recarrega histórico do servidor. |

## 4. Requisitos não funcionais (RNF)

- **RNF-01 — Acessibilidade:** WCAG 2.1 AA como objetivo; rótulos persistentes, foco visível, altura de controles >=48px, mensagens de erro associadas e alertas não dependentes apenas de cor.
- **RNF-02 — Responsividade:** layout compatível com desktop e telas móveis.
- **RNF-03 — Integridade:** saldo nunca negativo; baixa e histórico em uma transação.
- **RNF-04 — Validação:** tipos estritos, quantidades inteiras positivas, campos extras proibidos e limites de tamanho.
- **RNF-05 — Segurança local:** endpoints de negócio exigem Bearer; não armazenar credenciais em código HTML; token fica em `sessionStorage`.
- **RNF-06 — Privacidade:** não registrar dados pessoais de solicitantes em observações sem necessidade; o projeto usa catálogo fictício.
- **RNF-07 — Rastreabilidade:** toda baixa concluída preserva autor, data/hora, chamado, item e quantidade.
- **RNF-08 — Limite de implantação:** aplicação destina-se a localhost; autenticação não equivale a sistema institucional pronto para produção.

## 5. Contrato da API

- `POST /api/auth/token`: `{ "username": "...", "password": "..." }` → `{ "access_token": "...", "token_type": "bearer", "expires_in": 3600 }`.
- `GET /api/insumos`: lista e flags `estoque_critico`.
- `POST /api/insumos/baixa`: requer `chamado_glpi_id`, `insumo_id`, `quantidade`, `tecnico_responsavel`; `observacao` opcional. Retorna a movimentação ou `404`/`422`.
- `GET /api/movimentacoes?limite=10`: histórico recente autenticado.
- `GET /api/relatorios/resumo`: métricas gerais.

O técnico responsável não é confiado a partir do request: deve corresponder ao nome configurado e o nome gravado é o nome institucional definido pelo backend. Em uma futura evolução, mapear a identidade do usuário do JWT para a tabela de operadores.

## 6. Segurança, riscos e recomendações

1. Os valores `danilo`, `admin123` e segredo JWT embutido são **somente de demonstração**. Definir variáveis de ambiente seguras antes de iniciar, sem gravá-las no Git.
2. Manter Uvicorn em `127.0.0.1`; CORS `*` é usado por compatibilidade com `file://` e não deve ser reaproveitado em exposição de rede.
3. Não usar diretamente em operação institucional. Substituir autenticação simulada por SSO/OIDC, perfis, política de tentativas, rotação/revogação e auditoria.
4. Endereço da instância GLPI mostrado nas telas é demonstrativo; confirmar URL institucional antes de uso. O backend não consulta GLPI.
5. O SQLite é adequado ao escopo local; definir backup/restauração, retenção e migrações antes da evolução do schema.
6. O CRUD atual permite criar/editar saldo diretamente; para operação real, exigir lançamentos auditáveis para qualquer ajuste e inventário.
7. Implementar testes automatizados de integridade/transações, limitações de acesso, acessibilidade e interface.

## 7. Plano de verificação WCAG 2.1

- **1.1.1 Conteúdo não textual:** ícones decorativos marcados como ocultos a tecnologias assistivas; símbolos reforçados por texto.
- **1.3.1 Informação e relações:** tabelas com cabeçalhos/captions, campos com labels e mensagens relacionadas.
- **1.4.1 Uso de cor:** crítico é mostrado com cor, ícone de alerta e texto literal “CRÍTICO”; disponível também possui texto/ícone.
- **1.4.3/1.4.11 Contraste:** validar combinação final de texto, bordas, controles e estados com ferramenta de contraste WCAG; estilos são ponto de partida, não certificação automática.
- **2.1.1 Teclado / 2.4.7 Foco visível:** controles nativos, link de salto e anel de foco de 3px; testar tabulação completa em navegador real.
- **2.4.6 Rótulos e instruções:** labels descritivos, campos obrigatórios e instruções de quantidade.
- **3.3.1/3.3.3 Erros:** mensagens textuais anunciam erro e orientam correção; HTTP 422 preserva a explicação do servidor.
- **4.1.2/4.1.3 Nome, papel, valor e mensagens de status:** inputs nativos e regiões `aria-live` anunciam alertas/resultado.

### Verificações manuais antes de declarar conformidade

1. Navegar todas as telas apenas por teclado, observando ordem e foco.
2. Testar com leitor de tela (NVDA/Firefox ou NVDA/Chrome) os formulários, alertas e tabelas.
3. Medir contraste WCAG de estados normal, foco, erro e crítico.
4. Testar zoom de 200% e largura equivalente a 320 CSS px.
5. Conferir que mensagens de erro permanecem visíveis e associadas aos campos após envio.

Este documento descreve objetivos e plano de verificação; não constitui certificação WCAG ou autorização de produção.
