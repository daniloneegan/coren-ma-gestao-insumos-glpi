# Requisitos do sistema

## Objetivo

Oferecer um protótipo web para registrar insumos, consultar disponibilidade e acompanhar níveis de estoque, com base técnica preparada para avaliar uma futura integração com GLPI.

## Atores

- **Gestor de estoque:** cadastra e atualiza itens, consulta níveis e registra movimentações.
- **Consulta (futuro):** perfil somente leitura; não existe autenticação/perfil nesta versão.
- **Administrador técnico:** configura execução, banco e integrações.

## Requisitos funcionais

| ID | Requisito | Critério de aceite |
|---|---|---|
| RF-01 | Cadastrar insumo com nome, categoria, unidade, saldo inicial, mínimo e localização. | Dados válidos são persistidos e devolvidos com identificador. |
| RF-02 | Listar e pesquisar insumos por nome, categoria ou localização. | Lista reflete o banco; busca parcial não diferencia maiúsculas/minúsculas. |
| RF-03 | Filtrar a lista por categoria. | Seleção limita resultados e pode ser removida. |
| RF-04 | Consultar, editar e excluir insumo. | API oferece leitura individual, atualização parcial e exclusão com resposta apropriada. |
| RF-05 | Registrar entradas e saídas. | Entrada soma; saída subtrai; saldo não pode ser negativo. |
| RF-06 | Sinalizar saldo igual ou inferior ao mínimo. | Painel e linha do insumo mostram estado de estoque baixo. |
| RF-07 | Exibir indicadores agregados. | Painel informa total, itens baixos, categorias e locais distintos. |
| RF-08 | Exportar a lista para CSV. | Arquivo gerado no navegador contém os itens cadastrados. |
| RF-09 | Expor documentação da API. | Swagger disponível em `/docs` e OpenAPI em `/openapi.json`. |
| RF-10 | Avaliar integração futura com GLPI. | A integração só é implementada após descoberta e validação documentadas. |

## Requisitos não funcionais

- **RNF-01 — Responsividade:** interface utilizável em celular, tablet e desktop.
- **RNF-02 — Validação:** campos e quantidades são validados tanto na API quanto no formulário.
- **RNF-03 — Integridade:** operações de saída não podem gerar estoque negativo.
- **RNF-04 — Configuração:** conexão de banco pode ser definida por `DATABASE_URL`.
- **RNF-05 — Segurança:** antes de implantação, incluir autenticação, autorização, CORS restritivo e gestão de segredos.
- **RNF-06 — Privacidade:** evitar dados pessoais; não incluir dados reais nas demonstrações.
- **RNF-07 — Manutenibilidade:** manter API, interface e documentação separadas; adotar migrações e testes para evolução.
- **RNF-08 — Disponibilidade e recuperação:** definir backup, restauração e monitoramento antes de uso institucional.

## Regras de negócio iniciais

1. Quantidade e estoque mínimo são inteiros não negativos.
2. Nome, categoria, unidade e localização são obrigatórios.
3. Movimentação tem tipo `entrada` ou `saida` e quantidade inteira positiva.
4. O saldo resultante de uma saída deve ser maior ou igual a zero.
5. Estado de alerta: quantidade menor ou igual ao mínimo definido.
6. O modelo atual não mantém histórico de movimentações; o endpoint altera o saldo diretamente.

## Fora do escopo atual

Autenticação/SSO, aprovação de requisições, fornecedores, compras, lotes/validade, inventário, trilha histórica, relatórios avançados, integração real com GLPI, alertas por e-mail e operação multiunidade.

## Critérios gerais de aceite acadêmico

- Aplicação inicia pelas instruções do README.
- Endpoints principais podem ser exercitados em `/docs`.
- Interface renderiza sem conexão e indica falha de API com mensagem clara.
- Cadastro, pesquisa, filtros, CSV e movimentação funcionam com backend disponível.
- Fluxos básicos e layout são verificados em largura desktop e móvel.
