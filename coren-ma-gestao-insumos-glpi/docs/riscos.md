# Matriz de riscos e mitigação

Escala qualitativa preliminar: probabilidade e impacto baixos, médios ou altos. Avaliar novamente com responsáveis técnicos e institucionais antes de implantação.

| Risco | Probabilidade | Impacto | Mitigação recomendada |
|---|---|---|---|
| Acesso indevido ou alteração de saldo sem autorização | Alta no protótipo (sem login) | Alto | Não expor fora do ambiente local; implementar autenticação, autorização por perfil, sessão segura e logs de auditoria. |
| Credenciais ou dados sensíveis em repositório | Média | Alto | Segredos fora do Git, rotação de credenciais, `.env` ignorado, revisão de histórico e secret scanning. |
| Integração GLPI incompatível ou não autorizada | Média | Alto | Descoberta de versão/API com administrador, escopo aprovado, credencial de privilégio mínimo e ambiente de homologação. |
| Divergência de estoque por atualizações concorrentes | Média | Alto | Operação transacional/atômica, controle de concorrência, chave de idempotência e histórico imutável. |
| Perda ou corrupção do banco | Média | Alto | Backups automáticos, retenção definida e testes de restauração; monitorar espaço e integridade. |
| Origem CORS excessivamente ampla | Alta no protótipo | Médio/alto | Restringir `allow_origins` aos domínios necessários antes de produção. |
| Dependências vulneráveis ou incompatíveis | Média | Médio/alto | Fixar e atualizar dependências com processo de revisão, scanner e testes em CI. |
| Uso de dados institucionais em ambiente acadêmico | Baixa/média | Alto | Usar registros fictícios/anonimizados, obter autorização e revisar requisitos de privacidade. |
| Falta de rastreabilidade de movimentações | Alta (não há histórico) | Alto | Criar entidade de movimentação com autor, data, tipo, quantidade, saldo anterior/posterior e justificativa. |
| Confusão entre protótipo e produto homologado | Média | Alto | Identificar claramente ambiente demonstrativo, publicar limitações e exigir homologação formal. |
| Senha padrão no Compose | Alta se implantado sem mudança | Alto | A senha é apenas local/de desenvolvimento; usar secrets/variáveis protegidas, alterar antes de qualquer ambiente compartilhado e nunca publicar portas sem controles. |

## Condições mínimas antes de qualquer piloto

- Aprovação institucional e definição de responsável pelo sistema e pelos dados.
- Autenticação, autorização, auditoria e CORS restritivo implementados e revisados.
- Credenciais fora do código e política de rotação/backup documentada.
- Testes de segurança, integridade de saldo, concorrência e restauração.
- Homologação da integração e definição de fonte oficial de cada dado.
- Monitoramento, resposta a incidentes e processo de atualização de dependências.
