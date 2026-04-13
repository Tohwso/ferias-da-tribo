# Requisitos do Sistema — ferias

> **Artefato RUP:** Especificação de Requisitos (Requisitos)
> **Proprietário:** [RUP] Analista de Requisitos (📋)
> **Status:** Completo
> **Última atualização:** 2026-07-17

---

## 1. Requisitos Funcionais

### 1.1 Gestão de Times

| ID | Descrição | Fonte | Prioridade | Rastreabilidade |
|----|-----------|-------|------------|-----------------|
| RF-01 | O sistema deve permitir criar um time com nome e descrição | BP-01 | Must Have | BR-008 |
| RF-02 | O sistema deve permitir editar o nome e a descrição de um time existente | BP-01 | Must Have | — |
| RF-03 | O sistema deve permitir excluir um time, desde que não possua pessoas vinculadas | BP-01, UQ: decisão stakeholder | Must Have | BR-010 |
| RF-04 | O sistema deve exibir uma listagem de todos os times cadastrados | BP-01 | Must Have | — |

### 1.2 Gestão de Pessoas

| ID | Descrição | Fonte | Prioridade | Rastreabilidade |
|----|-----------|-------|------------|-----------------|
| RF-05 | O sistema deve permitir criar uma pessoa com nome, email e vínculo a um time | BP-02 | Must Have | BR-001 |
| RF-06 | O sistema deve validar que o email de uma pessoa é único no sistema | BP-02 | Must Have | BR-011 |
| RF-07 | O sistema deve permitir editar os dados de uma pessoa (nome, email, time) | BP-02 | Must Have | — |
| RF-08 | O sistema deve permitir excluir uma pessoa, excluindo em cascata todos os seus eventos de férias | BP-02, UQ-002 | Must Have | BR-009 |
| RF-09 | O sistema deve exibir uma listagem de todas as pessoas cadastradas, com indicação do time | BP-02 | Must Have | — |
| RF-10 | Toda pessoa deve estar vinculada a exatamente um time — o campo time é obrigatório na criação e edição | BP-02 | Must Have | BR-001 |

### 1.3 Registro de Férias

| ID | Descrição | Fonte | Prioridade | Rastreabilidade |
|----|-----------|-------|------------|-----------------|
| RF-11 | O sistema deve permitir criar um evento de férias informando: pessoa, data de início, data de fim e quantidade de dias | BP-03 | Must Have | BR-003, BR-007 |
| RF-12 | O sistema deve validar que a data de início é anterior ou igual à data de fim | BP-03 | Must Have | BR-002 |
| RF-13 | O sistema deve permitir editar os dados de um evento de férias (datas e quantidade de dias) | BP-03 | Must Have | — |
| RF-14 | O sistema deve permitir excluir um evento de férias | BP-03 | Must Have | — |
| RF-15 | Uma pessoa pode ter múltiplos eventos de férias cadastrados (períodos distintos) | BP-03 | Must Have | BR-007 |

### 1.4 Consulta e Visualização (Tela Inicial)

| ID | Descrição | Fonte | Prioridade | Rastreabilidade |
|----|-----------|-------|------------|-----------------|
| RF-16 | A tela inicial deve exibir os eventos de férias ordenados por data de início (mais próximo primeiro) | BP-04 | Must Have | BR-004 |
| RF-17 | Cada evento na tela inicial deve exibir: nome da pessoa, quantidade de dias, data de início e data de fim | BP-04 | Must Have | BR-012 |
| RF-18 | A tela inicial deve oferecer um filtro por time, com opção padrão "Todos" exibindo eventos de todos os times | BP-04 | Must Have | BR-005, BR-006 |
| RF-19 | A tela inicial deve exibir por padrão apenas os eventos de férias futuros (data de fim ≥ hoje), com um toggle para incluir eventos passados | BP-04, UQ-003 | Must Have | — |
| RF-20 | A sobreposição de férias entre membros do mesmo time deve ser identificável visualmente na tela inicial, sem alerta explícito | BP-04, UQ-001 | Should Have | — |

---

## 2. Requisitos Não-Funcionais

### 2.1 Performance

| ID | Categoria | Descrição | Métrica | Meta |
|----|-----------|-----------|---------|------|
| NFR-01 | Performance | A tela inicial deve carregar a lista de férias em tempo imperceptível para o usuário | Tempo de resposta P95 | < 500ms |
| NFR-02 | Performance | Operações de CRUD (criar, editar, excluir) devem responder rapidamente | Tempo de resposta P95 | < 300ms |

### 2.2 Usabilidade

| ID | Categoria | Descrição | Métrica | Meta |
|----|-----------|-----------|---------|------|
| NFR-03 | Usabilidade | Um novo usuário deve conseguir cadastrar um evento de férias sem instrução | Tempo para primeira tarefa | < 2 minutos |
| NFR-04 | Usabilidade | A interface deve funcionar em navegadores modernos (Chrome, Firefox, Safari, Edge) | Compatibilidade | Últimas 2 versões |

### 2.3 Disponibilidade e Operação

| ID | Categoria | Descrição | Métrica | Meta |
|----|-----------|-----------|---------|------|
| NFR-05 | Disponibilidade | O sistema deve operar 100% localmente, sem dependência de serviços externos | Dependências externas | Zero |
| NFR-06 | Operação | O banco de dados SQLite deve ser um arquivo único, facilmente copiável para backup | Procedimento de backup | Copiar 1 arquivo |

### 2.4 Escalabilidade

| ID | Categoria | Descrição | Métrica | Meta |
|----|-----------|-----------|---------|------|
| NFR-07 | Escalabilidade | O sistema deve suportar adequadamente até 30 pessoas e seus respectivos eventos de férias | Volume de dados | ~30 pessoas, ~100 eventos |

### 2.5 Segurança

| ID | Categoria | Descrição | Métrica | Meta |
|----|-----------|-----------|---------|------|
| NFR-08 | Segurança | O sistema não implementa autenticação — acesso aberto a qualquer pessoa na rede local | Controle de acesso | Nenhum (risco aceito) |

---

## 3. Regras de Negócio — Interpretação Sistêmica

Esta seção referencia as regras definidas em `spec/docs/01-business/business-rules.md` e descreve como cada uma se traduz em comportamento do sistema.

| BR | Regra Original | Interpretação Sistêmica |
|----|----------------|------------------------|
| BR-001 | Toda pessoa deve estar vinculada a exatamente um time | Campo `time` é obrigatório e de seleção única no formulário de pessoa. A API rejeita criação/edição sem time. |
| BR-002 | Evento de férias deve ter data de início ≤ data de fim | Validação tanto no frontend (formulário) quanto no backend (API retorna erro 422). |
| BR-003 | Dias de férias informados manualmente | Campo `dias` é de entrada livre (número inteiro positivo). Não há cálculo automático. |
| BR-004 | Tela inicial ordenada por data de início | A query de listagem aplica `ORDER BY data_inicio ASC`. |
| BR-005 | Filtro por time mostra apenas eventos do time selecionado | A API aceita parâmetro `team_id` na listagem de férias. Quando informado, filtra por time. |
| BR-006 | Sem filtro = todos os times | O filtro inicia com valor "Todos" (sem `team_id`), retornando todos os eventos. |
| BR-007 | Uma pessoa pode ter múltiplos eventos de férias | Relação 1:N entre pessoa e evento de férias, sem restrição de quantidade. |
| BR-008 | Time pode existir sem pessoas | Não há restrição de integridade que exija pessoas para um time existir. |
| BR-009 | Exclusão de pessoa com férias: cascata | `DELETE` de pessoa dispara exclusão automática de todos os eventos de férias vinculados (ON DELETE CASCADE). Decisão UQ-002. |
| BR-010 | Time não pode ser excluído com pessoas vinculadas | `DELETE` de time retorna erro se houver pessoas vinculadas. O usuário deve mover ou remover as pessoas antes. |
| BR-011 | Email de pessoa deve ser único | Constraint UNIQUE no campo email. API retorna erro 409 em caso de duplicidade. |
| BR-012 | Tela inicial exibe nome, dias, início e fim | Campos obrigatórios no card/linha do evento de férias na interface. |
| BR-013 | Sem autenticação | Nenhum middleware de auth. Todos os endpoints são públicos. Risco aceito. |
| BR-014 | Qualquer usuário pode CRUD tudo | Nenhuma verificação de permissão em nenhuma operação. Risco aceito. |
| BR-015 | Operação 100% local | Nenhuma chamada HTTP para serviços externos. Sem CDN, sem fontes remotas, sem telemetria. |

---

## 4. Matriz de Rastreabilidade — Requisitos × Regras de Negócio

| BR | RF |
|----|----|
| BR-001 | RF-05, RF-10 |
| BR-002 | RF-12 |
| BR-003 | RF-11 |
| BR-004 | RF-16 |
| BR-005 | RF-18 |
| BR-006 | RF-18 |
| BR-007 | RF-11, RF-15 |
| BR-008 | RF-01 |
| BR-009 | RF-08 |
| BR-010 | RF-03 |
| BR-011 | RF-06 |
| BR-012 | RF-17 |
| BR-013 | NFR-08 |
| BR-014 | NFR-08 |
| BR-015 | NFR-05, NFR-06 |

---

## 5. Requisitos Implícitos (sem origem de negócio explícita)

Estes requisitos foram identificados como necessários para uma aplicação funcional, mas não possuem regra de negócio correspondente.

| ID | Descrição | Justificativa | Risco |
|----|-----------|---------------|-------|
| RF-19 | Toggle futuras/passadas | Decisão do stakeholder (UQ-003), mas não havia BR formal | Baixo — decisão já validada |
| RF-20 | Sobreposição visível sem alerta | Decisão do stakeholder (UQ-001), mas não havia BR formal | Baixo — decisão já validada |

> ⚠️ Ambos os requisitos implícitos foram validados pelo stakeholder via Governante (UQ-001 e UQ-003). Não representam premissas pendentes.
