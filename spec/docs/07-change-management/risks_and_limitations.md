# Riscos e Limitações — ferias

> **Artefato RUP:** Riscos Operacionais e Limitações Conhecidas (Gestão de Mudanças)
> **Proprietário:** [RUP] Analista de Qualidade
> **Status:** Completo
> **Última atualização:** 2026-07-18

---

## 1. Riscos Operacionais

| ID | Risco | Probabilidade | Impacto | Categoria | Mitigação Existente | Mitigação Recomendada |
|----|-------|---------------|---------|-----------|--------------------|-----------------------|
| RISK-001 | **Rotas duplicadas podem gerar comportamento inesperado** — `routes/api.py` registra 12 endpoints duplicados de `routers/*.py`, com bugs (métodos inexistentes, tratamento de erros ausente). Se o FastAPI resolver a rota pelo arquivo errado, o usuário pode receber errors 500 ou respostas malformadas. | Alta | Alto | Arquitetura | Nenhuma — ambos os routers são registrados em `main.py` | **Remover `routes/api.py` imediatamente** (TD-001) |
| RISK-002 | **Perda de dados por falta de backup automatizado** — o banco SQLite é um arquivo único (`ferias.db`) sem backup automático. Exclusão acidental ou corrupção do arquivo resulta em perda total. | Média | Alto | Operação | Documentação de procedimento manual: `cp ferias.db backup.db` (ci_cd_pipeline.md §7) | Criar script/cron de backup periódico. Adicionar `.db` ao .gitignore (já feito) |
| RISK-003 | **Sem autenticação — alterações indevidas** — qualquer pessoa na rede local pode criar, editar ou excluir qualquer registro. Um clique acidental em "excluir" remove dados sem possibilidade de recuperação (sem soft delete ou undo). | Média | Médio | Segurança | Risco conscientemente aceito pelo stakeholder (BR-013, BR-014, NFR-08) | Considerar confirmação modal no frontend antes de exclusões (UI safety net). Backup regular mitiga parcialmente. |
| RISK-004 | **Exclusão em cascata de pessoa remove férias silenciosamente** — ao excluir uma pessoa, todas as suas férias são removidas automaticamente (ON DELETE CASCADE, BR-009). O usuário pode não perceber que está perdendo dados de férias. | Baixa | Médio | Operação | O frontend deveria exibir confirmação com contagem de férias antes de excluir (não verificável — sem testes E2E) | Adicionar teste E2E que verifique a mensagem de confirmação |
| RISK-005 | **Corrupção do SQLite em acesso concorrente** — SQLite usa file-level locking. Se múltiplos usuários fizerem operações de escrita simultâneas, pode haver `SQLITE_BUSY` ou, em cenários extremos, corrupção. | Baixa | Alto | Infraestrutura | `connect_args={"check_same_thread": False}` permite acesso multi-thread. FastAPI (async) pode ter múltiplas threads de I/O. | Aceitável para ~30 usuários com escrita esporádica. Se o volume crescer, migrar para PostgreSQL (SQLAlchemy abstrai o dialect). |
| RISK-006 | **Overlap detection com complexidade O(n²)** — `_detect_team_overlaps` compara todos os pares de férias do mesmo time. Para 30 pessoas com ~3 férias cada (~90 eventos), são ~90² = 8.100 comparações por time. | Baixa | Baixo | Performance | Premissa AS-01 limita a ~30 pessoas — carga aceitável | Se crescer, otimizar com ordenação + sweep line (O(n log n)). Por ora, aceitável. |
| RISK-007 | **Sem validação de formato de email** — `PersonCreate.email` aceita qualquer string de 1-254 caracteres. Não há validação de formato (presença de `@`, domínio). Dados inconsistentes podem ser cadastrados. | Média | Baixo | Qualidade de Dados | Premissa AS-05: "formato-independente" — aceito | Se for desejável, adicionar `EmailStr` do Pydantic (1 linha de mudança). Por ora, comportamento conforme spec. |
| RISK-008 | **Frontend não testado — bugs visuais invisíveis** — nenhum teste automatizado verifica a camada de apresentação (templates Jinja2, JavaScript, CSS). Bugs no filtro por time, no toggle de passadas, ou no highlight de sobreposição não seriam detectados até uso manual. | Média | Médio | Qualidade | Nenhuma — todos os testes são de API | Implementar testes E2E com Playwright para os 4 fluxos visuais (UC-001 a UC-004) |

---

## 2. Limitações Conhecidas

### 2.1 Limitações de Design (Intencionais)

| # | Limitação | Razão | Referência |
|---|-----------|-------|------------|
| L-01 | **Sem autenticação** — qualquer pessoa na rede pode alterar qualquer dado | Simplicidade deliberada — ferramenta interna para ~30 pessoas | BR-013, BR-014, NFR-08 |
| L-02 | **Sem workflow de aprovação** — férias são confirmadas no cadastro, sem aprovação de gestor | Fora de escopo — não é sistema de RH | vision.md §4.2 |
| L-03 | **Sem integração externa** — não conecta com RH, calendários, Slack ou email | Operação 100% local por requisito | BR-015, NFR-05 |
| L-04 | **Sem cálculo de saldo de férias CLT** — o sistema não sabe quantos dias de férias a pessoa tem direito | Fora de escopo — simplificação deliberada | vision.md §4.2 |
| L-05 | **Sem notificações** — ninguém é avisado quando férias são cadastradas ou alteradas | Fora de escopo | vision.md §4.2 |
| L-06 | **Sem auditoria/histórico** — não é possível saber quem alterou o quê e quando | Premissa AS-02 — ferramenta de visibilidade, não de compliance | AS-02 |
| L-07 | **Sem multi-tenancy** — apenas um time/organização por instância | Fora de escopo | vision.md §4.2 |

### 2.2 Limitações Técnicas

| # | Limitação | Impacto | Mitigação Possível |
|---|-----------|---------|-------------------|
| L-08 | **SQLite não suporta acesso concorrente pesado** — WAL mode não habilitado explicitamente. Escritas simultâneas podem gerar erro `SQLITE_BUSY`. | Leve para ~30 usuários esporádicos | Habilitar `PRAGMA journal_mode=WAL` ou migrar para PostgreSQL se escala crescer |
| L-09 | **Sem paginação na API** — `GET /api/v1/vacations` retorna TODOS os eventos. Com volume alto (centenas de eventos), a resposta pode ficar pesada. | Negligível para o volume esperado (AS-01: ~100 eventos) | Adicionar query params `offset` e `limit` se necessário |
| L-10 | **Sem soft delete** — exclusões são permanentes. Não há lixeira ou undo. | Dados excluídos acidentalmente não podem ser recuperados (exceto via backup do banco) | Implementar flag `deleted_at` com filtro automático. Por ora, backup é a mitigação. |
| L-11 | **Sem log de aplicação persistente** — logging configurado (config.py `LOG_LEVEL`) mas sem output para arquivo. Logs vão para stdout e se perdem ao reiniciar. | Diagnóstico pós-incidente impossível | Redirecionar logs para arquivo ou usar `logging.FileHandler` |
| L-12 | **`days` calculado automaticamente vs spec manual** — a spec (BR-003) define `days` como input manual, mas a implementação calcula `end_date - start_date + 1`. O campo `days` não aceita input do usuário. | Divergência documentada (implementation_patterns.md §6). Comportamento mais seguro que a spec. | Atualizar a spec para refletir a realidade |
| L-13 | **Sem validação de data futura** — é possível cadastrar férias no passado (e.g., 2020-01-01). O toggle `include_past` filtra na consulta, mas não impede o cadastro. | Dados inconsistentes possíveis — mas pode ser intencional (registrar retroativamente) | Se não desejável, adicionar validação `start_date >= today` no schema |

---

## 3. Cenários de Falha e Tratamento

| Cenário | Como Falha | Tratamento Atual | Adequado? |
|---------|-----------|-----------------|-----------|
| Banco de dados corrompido | Erro ao iniciar a app ou ao executar queries | FastAPI retorna 500 genérico | 🟡 Parcial — sem mensagem útil para o usuário |
| Banco de dados deletado | App cria novo banco vazio ao reiniciar (via `create_tables()`) | Dados perdidos, mas app funcional | 🟢 Sim — auto-recovery, desde que haja backup |
| Disco cheio | Escrita no SQLite falha com `SQLITE_FULL` | FastAPI retorna 500 | 🔴 Não — sem mensagem explicativa |
| Porta 8000 ocupada | Uvicorn falha ao iniciar | Erro claro no terminal: `Address already in use` | 🟢 Sim |
| Request com body inválido | Pydantic valida e rejeita | 422 com detalhes da validação | 🟢 Sim |
| Request com `team_id` inexistente na criação de pessoa | Service valida e rejeita | 422 "Time informado não existe" | 🟢 Sim |
| Exclusão de time com pessoas | Service valida e rejeita | 409 "Existem pessoas vinculadas" | 🟢 Sim |
| Email duplicado | IntegrityError capturado pelo service | 409 "Já existe uma pessoa com este email" | 🟢 Sim |
| Datas inválidas (start > end) | Pydantic validator rejeita | 422 "Data de início deve ser anterior ou igual à data de fim" | 🟢 Sim |
| Sobreposição mesma pessoa | Service valida e rejeita | 409 "Já existe um evento de férias que se sobrepõe" | 🟢 Sim |

---

## 4. Gaps de Compliance

| Dimensão | Status | Comentário |
|----------|--------|------------|
| LGPD | ⚠️ Parcial | O sistema armazena nome e email (dados pessoais). Sem consentimento explícito, sem funcionalidade de anonimização ou exclusão sob demanda (direito ao esquecimento). Mitigação: escopo interno e acesso restrito à rede local. |
| Acessibilidade (WCAG) | ⬜ Não verificado | Frontend não auditado para acessibilidade. Sem evidência de labels ARIA, contraste, navegação por teclado. |
| Backup e Recuperação | 🟡 Manual | Backup documentado mas manual (`cp ferias.db`). Sem RPO/RTO definidos. |
