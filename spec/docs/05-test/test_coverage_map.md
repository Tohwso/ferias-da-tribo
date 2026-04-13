# Mapa de Cobertura de Testes — ferias

> **Artefato RUP:** Mapa de Cobertura e Rastreabilidade (Qualidade)
> **Proprietário:** [RUP] Analista de Qualidade
> **Status:** Completo
> **Última atualização:** 2026-07-18

---

## 1. Matriz de Rastreabilidade — RF × Teste

| RF | Descrição | UC | Endpoint | Arquivo Fonte | Arquivo Teste | Status |
|----|-----------|-----|----------|---------------|---------------|--------|
| RF-01 | Criar time (nome + descrição) | UC-001 | POST /api/v1/teams | `app/services/team_service.py:70` | `tests/test_teams.py::test_create_team` | ✅ COBERTO |
| RF-02 | Editar time | UC-001 | PUT /api/v1/teams/{id} | `app/services/team_service.py:86` | `tests/test_teams.py::test_update_team` | ✅ COBERTO |
| RF-03 | Excluir time (sem pessoas) | UC-001 | DELETE /api/v1/teams/{id} | `app/services/team_service.py:110` | `tests/test_teams.py::test_delete_team` | ✅ COBERTO |
| RF-04 | Listar times | UC-001 | GET /api/v1/teams | `app/services/team_service.py:16` | `tests/test_teams.py::test_list_teams` | ✅ COBERTO |
| RF-05 | Criar pessoa (nome, email, time) | UC-002 | POST /api/v1/people | `app/services/person_service.py:68` | `tests/test_persons.py::test_create_person` | ✅ COBERTO |
| RF-06 | Validar email único | UC-002 | POST /api/v1/people | `app/services/person_service.py:85-88` | `tests/test_persons.py::test_create_person_duplicate_email_returns_409` | ✅ COBERTO |
| RF-07 | Editar pessoa | UC-002 | PUT /api/v1/people/{id} | `app/services/person_service.py:95` | `tests/test_persons.py::test_update_person` | ✅ COBERTO |
| RF-08 | Excluir pessoa (cascata) | UC-002 | DELETE /api/v1/people/{id} | `app/services/person_service.py:131` | `tests/test_persons.py::test_delete_person_cascades_vacations` | ✅ COBERTO |
| RF-09 | Listar pessoas com time | UC-002 | GET /api/v1/people | `app/services/person_service.py:41` | `tests/test_persons.py::test_list_persons` | ✅ COBERTO |
| RF-10 | Time obrigatório na pessoa | UC-002 | POST /api/v1/people | `app/services/person_service.py:78-81` | — | 🟡 PARCIAL — validado pelo Pydantic (`team_id: int` obrigatório), mas sem teste explícito de envio sem `team_id` |
| RF-11 | Criar evento de férias | UC-003 | POST /api/v1/vacations | `app/services/vacation_service.py:182` | `tests/test_vacations.py::test_create_vacation` | ✅ COBERTO |
| RF-12 | Validar start_date ≤ end_date | UC-003 | POST /api/v1/vacations | `app/schemas/vacation.py:26-31` | `tests/test_vacations.py::test_create_vacation_invalid_dates_returns_422` | ✅ COBERTO |
| RF-13 | Editar evento de férias | UC-003 | PUT /api/v1/vacations/{id} | `app/services/vacation_service.py:220` | `tests/test_vacations.py::test_update_vacation` | ✅ COBERTO |
| RF-14 | Excluir evento de férias | UC-003 | DELETE /api/v1/vacations/{id} | `app/services/vacation_service.py:261` | `tests/test_vacations.py::test_delete_vacation` | ✅ COBERTO |
| RF-15 | Múltiplos eventos por pessoa | UC-003 | POST /api/v1/vacations | `app/models/person.py:38-43` (relação 1:N) | — | 🟡 PARCIAL — seed_data tem 2 férias para Alice, mas sem teste explícito que asserte a quantidade |
| RF-16 | Ordenação por start_date ASC | UC-004 | GET /api/v1/vacations | `app/services/vacation_service.py:134` | — | ⬜ NÃO COBERTO — `test_list_vacations` não verifica ordenação |
| RF-17 | Exibir nome, dias, início, fim | UC-004 | GET /api/v1/vacations | `app/services/vacation_service.py:88-104` | `tests/test_vacations.py::test_get_vacation` (asserta person_name, days) | 🟡 PARCIAL — asserta campos no GET by ID, não na listagem |
| RF-18 | Filtro por time | UC-004 | GET /api/v1/vacations?team_id=X | `app/services/vacation_service.py:127-128` | `tests/test_vacations.py::test_filter_vacations_by_team` | ✅ COBERTO |
| RF-19 | Toggle férias passadas | UC-004 | GET /api/v1/vacations?include_past=true | `app/services/vacation_service.py:130-132` | `tests/test_vacations.py::test_filter_include_past` | ✅ COBERTO |
| RF-20 | Sobreposição visual (has_overlap) | UC-004 | GET /api/v1/vacations (campo `has_overlap`) | `app/services/vacation_service.py:53-85` | — | ⬜ NÃO COBERTO — nenhum teste cria dados que gerem `has_overlap=true` |

---

## 2. Matriz de Rastreabilidade — BR × Verificação

| BR | Regra | Implementação | Teste | Status |
|----|-------|---------------|-------|--------|
| BR-001 | Pessoa vinculada a exatamente 1 time | `Person.team_id` NOT NULL FK (models/person.py:26) | `test_create_person` asserta `team_id` no response | ✅ COBERTO |
| BR-002 | start_date ≤ end_date | Pydantic validator (schemas/vacation.py:26-31) + CHECK constraint (models/vacation.py:44-45) | `test_create_vacation_invalid_dates_returns_422` | ✅ COBERTO |
| BR-003 | Dias informados manualmente | **⚠️ DIVERGÊNCIA:** implementação calcula automaticamente via `_calc_days()` (vacation_service.py:30-31). Schema `VacationCreate` não aceita campo `days` — é calculado no service | Teste `test_create_vacation` asserta `days == 10` (calculado) | 🔴 DIVERGENTE — ver §6 |
| BR-004 | Ordenação por start_date ASC | `query.order_by(Vacation.start_date.asc())` (vacation_service.py:134) | Nenhum teste verifica ordenação explicitamente | ⬜ NÃO COBERTO |
| BR-005 | Filtro por time | `query.filter(Person.team_id == team_id)` (vacation_service.py:127-128) | `test_filter_vacations_by_team` | ✅ COBERTO |
| BR-006 | Sem filtro = todos os times | Sem `team_id`, query retorna tudo (vacation_service.py:127) | `test_list_vacations` (sem filtro, retorna 2) | ✅ COBERTO |
| BR-007 | Múltiplos eventos por pessoa | Relação 1:N sem restrição (models/person.py:38) | Seed data com 2 férias para Alice (implícito) | 🟡 PARCIAL |
| BR-008 | Time pode existir sem pessoas | Nenhuma validação impede (team_service.py:70) | `test_create_team` cria time sem pessoas, `person_count=0` | ✅ COBERTO |
| BR-009 | Exclusão de pessoa: cascata | `cascade="all, delete-orphan"` + `ondelete="CASCADE"` (models/person.py:38-43, models/vacation.py:26) | `test_delete_person_cascades_vacations` | ✅ COBERTO |
| BR-010 | Exclusão de time: bloqueio | Validação no service (team_service.py:124-129) | `test_delete_team_with_persons_returns_409` | ✅ COBERTO |
| BR-011 | Email único | UNIQUE constraint (models/person.py:25) + IntegrityError handler (person_service.py:85-88) | `test_create_person_duplicate_email_returns_409` | ✅ COBERTO |
| BR-012 | Não consta na spec original | **⚠️ ADIÇÃO:** implementação adiciona validação de sobreposição na mesma pessoa (vacation_service.py:36-50) | `test_create_vacation_overlap_same_person_returns_409` | ✅ COBERTO (mas regra não está na spec) |
| BR-013 | Sem autenticação | Nenhum middleware de auth em main.py | Verificação manual — todos os endpoints são públicos | ✅ COBERTO (inspeção) |
| BR-014 | Qualquer um pode CRUD tudo | Nenhuma verificação de permissão | Verificação manual | ✅ COBERTO (inspeção) |
| BR-015 | 100% local | Nenhuma chamada HTTP externa; CSS/fontes locais | Verificação manual — sem imports de SDK cloud | ✅ COBERTO (inspeção) |

---

## 3. Matriz de Rastreabilidade — NFR × Verificação

| NFR | Descrição | Abordagem de Verificação | Status |
|-----|-----------|--------------------------|--------|
| NFR-01 | Tela inicial < 500ms P95 | Sem teste de performance | ⬜ NÃO VERIFICADO — aceitável dada a escala (AS-01), mas não mensurado |
| NFR-02 | CRUD < 300ms P95 | Sem teste de performance | ⬜ NÃO VERIFICADO |
| NFR-03 | Cadastro em < 2min sem instrução | Sem teste de usabilidade | ⬜ NÃO VERIFICADO — requer teste manual |
| NFR-04 | Navegadores modernos | Sem teste cross-browser | ⬜ NÃO VERIFICADO |
| NFR-05 | 100% local | Inspeção de requirements.txt + imports — zero dependências cloud | ✅ VERIFICADO |
| NFR-06 | Backup = copiar 1 arquivo | SQLite em arquivo único `ferias.db` | ✅ VERIFICADO |
| NFR-07 | Suportar ~30 pessoas | Sem teste de volume/carga | ⬜ NÃO VERIFICADO |
| NFR-08 | Sem autenticação | Nenhum middleware de auth; CORS allow_origins=["*"] | ✅ VERIFICADO |

---

## 4. Cobertura por Módulo de Código

| Módulo | Arquivo | Funções | Testadas Diretamente | Testadas Indiretamente | Não Testadas |
|--------|---------|---------|---------------------|----------------------|-------------|
| Models | `models/team.py` | Team | — | Via testes de API | — |
| Models | `models/person.py` | Person | — | Via testes de API | — |
| Models | `models/vacation.py` | Vacation | — | Via testes de API | CHECK constraints (direto) |
| Schemas | `schemas/team.py` | TeamCreate, TeamUpdate, TeamResponse, TeamSummary | — | Via testes de API | Validações de borda (max_length) |
| Schemas | `schemas/person.py` | PersonCreate, PersonUpdate, PersonResponse | — | Via testes de API | Validações de borda |
| Schemas | `schemas/vacation.py` | VacationCreate, VacationUpdate, VacationResponse, VacationListResponse | — | Via testes de API | `check_dates` com start==end |
| Services | `services/team_service.py` | list, get, get_response, create, update, delete | — | 6/6 via API | — |
| Services | `services/person_service.py` | _to_response, list, get, get_response, create, update, delete | — | 7/7 via API | — |
| Services | `services/vacation_service.py` | _calc_days, _check_overlap, _detect_team_overlaps, _to_response, list, get, get_response, create, update, delete | — | 8/10 via API | `_detect_team_overlaps` (com overlap real), `_calc_days` (borda) |
| Routers | `routers/teams.py` | 5 endpoints | 5/5 | — | — |
| Routers | `routers/persons.py` | 5 endpoints | 5/5 | — | — |
| Routers | `routers/vacations.py` | 5 endpoints | 5/5 | — | — |
| Routes | `routes/pages.py` | page_index | — | — | ⬜ Não testada |
| Routes | `routes/api.py` | 12 endpoints | — | — | ⬜ Duplicados dos routers — ver finding [ARCH-001] |
| Database | `database.py` | engine, get_db, create_tables | — | Via conftest.py | — |

---

## 5. Conformidade com a Especificação da API

### 5.1 Endpoints — Spec vs Implementação

| Endpoint (api_spec.md) | Router (routers/) | Routes (routes/api.py) | Status |
|------------------------|-------------------|----------------------|--------|
| GET /api/v1/teams | ✅ teams.py:18 | ✅ api.py:24 | ⚠️ DUPLICADO |
| GET /api/v1/teams/{id} | ✅ teams.py:27 | ✅ api.py:30 | ⚠️ DUPLICADO |
| POST /api/v1/teams | ✅ teams.py:42 | ✅ api.py:36 | ⚠️ DUPLICADO |
| PUT /api/v1/teams/{id} | ✅ teams.py:51 | ✅ api.py:42 | ⚠️ DUPLICADO |
| DELETE /api/v1/teams/{id} | ✅ teams.py:66 | ✅ api.py:48 | ⚠️ DUPLICADO |
| GET /api/v1/people | ✅ persons.py:18 | ✅ api.py:57 | ⚠️ DUPLICADO |
| GET /api/v1/people/{id} | ✅ persons.py:30 | ✅ api.py:63 | ⚠️ DUPLICADO |
| POST /api/v1/people | ✅ persons.py:45 | ✅ api.py:69 | ⚠️ DUPLICADO |
| PUT /api/v1/people/{id} | ✅ persons.py:67 | ✅ api.py:75 | ⚠️ DUPLICADO |
| DELETE /api/v1/people/{id} | ✅ persons.py:96 | ✅ api.py:81 | ⚠️ DUPLICADO |
| GET /api/v1/vacations | ✅ vacations.py:23 | ✅ api.py:90 | ⚠️ DUPLICADO |
| GET /api/v1/vacations/{id} | ✅ vacations.py:38 | ✅ api.py:100 | ⚠️ DUPLICADO |
| POST /api/v1/vacations | ✅ vacations.py:53 | ✅ api.py:106 | ⚠️ DUPLICADO |
| PUT /api/v1/vacations/{id} | ✅ vacations.py:75 | ✅ api.py:112 | ⚠️ DUPLICADO |
| DELETE /api/v1/vacations/{id} | ✅ vacations.py:104 | ✅ api.py:118 | ⚠️ DUPLICADO |

**[ARCH-001]** Todos os 12 endpoints estão **duplicados**: existem em `app/routers/*.py` (com tratamento de erros e HTTPException) E em `app/routes/api.py` (sem tratamento de erros adequado). O `main.py` registra AMBOS, criando 24 endpoints em vez de 12. Os endpoints de `routes/api.py` têm problemas:
- `api_get_team` retorna `Team` model (não `TeamResponse`) — pode retornar None sem 404
- `api_delete_team` não trata o retorno `(success, reason)` — ignora erros
- `api_create_person` retorna `tuple` em vez de `PersonResponse` (porque `create_person` retorna tupla)
- `api_list_people` chama `person_service.list_people` que NÃO EXISTE (o método se chama `list_persons`)

### 5.2 Status Codes — Spec vs Implementação

| Cenário | Spec (api_spec.md) | Implementação (routers/) | Status |
|---------|-------------------|-------------------------|--------|
| Criação bem-sucedida | 201 | 201 | ✅ |
| Exclusão bem-sucedida | 204 | 204 | ✅ |
| Entidade não encontrada | 404 | 404 | ✅ |
| Email duplicado (BR-011) | 409 | 409 | ✅ |
| Time com pessoas (BR-010) | 409 | 409 | ✅ |
| Dados inválidos (BR-002) | 422 | 422 | ✅ |
| Time inexistente na criação de pessoa | 422 | 422 | ✅ |

### 5.3 Campos de Resposta — Spec vs Implementação

| Endpoint | Campo (spec) | Implementação | Status |
|----------|-------------|---------------|--------|
| GET /api/v1/teams | `person_count` | ✅ Calculado via JOIN | ✅ |
| GET /api/v1/people | `team_name`, `vacation_count` | ✅ Desnormalizados | ✅ |
| GET /api/v1/vacations | `has_overlap`, `teams[]` | ✅ Calculados | ✅ |
| GET /api/v1/vacations | `person_name`, `team_id`, `team_name` | ✅ Desnormalizados | ✅ |
| POST /api/v1/vacations | Input: `days` (manual, BR-003) | ❌ **DIVERGENTE** — `days` não aceito no input, calculado automaticamente | 🔴 |
| All vacation endpoints | `notes` | ✅ Aceito e retornado | ⚠️ **ADIÇÃO** — não consta na spec |

---

## 6. Findings de Conformidade

### [API-001] Campo `days` — Spec define input manual, implementação calcula automaticamente

**Severidade:** 🟡 Média
**Spec:** BR-003 / api_spec.md §5.3 — `days` é campo obrigatório no request body, informado manualmente pelo usuário
**Código:** `VacationCreate` (schemas/vacation.py:15-24) NÃO tem campo `days`. O `vacation_service.py:204` calcula `days = (end_date - start_date).days + 1`
**Impacto:** O Dev documentou explicitamente esta divergência em `implementation_patterns.md §6`: "A implementação optou por cálculo automático por instrução da tarefa — mais seguro e evita inconsistências"
**Avaliação:** Divergência **intencional e documentada**. O resultado é mais robusto que a spec original. Recomenda-se atualizar BR-003 e api_spec.md para refletir a decisão.

### [API-002] Campo `notes` — Não consta na spec

**Severidade:** 🟢 Baixa
**Spec:** api_spec.md e domain_model.md NÃO definem campo `notes` em Vacation
**Código:** `Vacation.notes` (models/vacation.py:33), `VacationCreate.notes` (schemas/vacation.py:24), `VacationResponse.notes` (schemas/vacation.py:67)
**Impacto:** Funcionalidade extra — não quebra nada, agrega valor
**Avaliação:** Adição benigna. Recomenda-se documentar retroativamente na spec.

### [API-003] Regra BR-012 — Não consta na spec de negócios

**Severidade:** 🟢 Baixa
**Spec:** business-rules.md define BR-001 a BR-015. NÃO existe BR-012.
**Código:** `_check_overlap_same_person()` (vacation_service.py:36-50) impede sobreposição de férias da mesma pessoa. O docstring referencia "BR-012" que não existe.
**Impacto:** Regra extra de proteção — positiva
**Avaliação:** Adição sensata. Recomenda-se adicionar BR-012 ao business-rules.md.

### [ARCH-001] Rotas duplicadas — routes/api.py duplica routers/*.py

**Severidade:** 🔴 Alta
**Spec:** api_spec.md define 12 endpoints REST. Architecture.md define camada de routers.
**Código:** `app/routes/api.py` implementa 12 endpoints idênticos aos de `app/routers/*.py`. O `main.py` registra AMBOS.
**Impacto:** 
1. `routes/api.py` tem **bugs**: chama `person_service.list_people` (não existe — o método é `list_persons`), retorna objetos errados (model em vez de response), não trata erros
2. Se ambos respondem na mesma rota, o FastAPI registra o **primeiro** — os de `routes/api.py` podem nunca ser alcançados (ou vice-versa), causando comportamento confuso
**Avaliação:** Provavelmente um artefato de desenvolvimento que ficou. O arquivo `routes/api.py` deve ser **removido** — os routers em `app/routers/*.py` são a implementação correta.

### [DOM-001] Modelo Vacation — Campo `notes` não documentado

**Severidade:** 🟢 Baixa  
**Spec:** domain_model.md §3.3 NÃO lista campo `notes`
**Código:** `Vacation.notes: Mapped[str | None] = mapped_column(String(500), nullable=True)` (models/vacation.py:33)
**Impacto:** Nenhum impacto negativo — funcionalidade extra

### [DOM-002] Páginas HTML — Spec define 4 rotas, implementação tem 1

**Severidade:** 🟡 Média
**Spec:** api_spec.md §2 define GET /, /teams, /people, /vacations (4 páginas)
**Código:** `routes/pages.py` define apenas GET / (1 página — SPA-like com tabs)
**Impacto:** A implementação usa abordagem SPA com abas dentro de uma única página HTML. O comportamento é equivalente — as 4 áreas existem como abas, não como páginas separadas. A diferença é arquitetural, não funcional.
**Avaliação:** Divergência aceitável — o Dev optou por SPA-like e as 4 áreas estão presentes.

---

## 7. Validação de Premissas (AS-01 a AS-07)

| ID | Premissa | Fase | Validação contra o Código | Resultado |
|----|----------|------|---------------------------|-----------|
| AS-01 | Máximo ~30 pessoas | Negócios | Nenhuma paginação implementada. `_detect_team_overlaps` tem complexidade O(n²) por time. Para 30 pessoas, n² ≈ 900 comparações — aceitável. | ✅ COERENTE — sem paginação é adequado para o volume |
| AS-02 | Sem histórico/auditoria | Negócios | `created_at` e `updated_at` existem nos models, mas sem tabela de auditoria ou log de alterações. | ✅ COERENTE — timestamps existem mas não há audit trail |
| AS-03 | Dias informados manualmente | Negócios | **VIOLADA** — `VacationCreate` não aceita `days`. O service calcula automaticamente: `days = (end_date - start_date).days + 1`. | 🔴 VIOLADA — divergência intencional (ver [API-001]) |
| AS-04 | Todos com acesso igual | Negócios | Nenhum middleware de auth. CORS `allow_origins=["*"]`. Sem roles ou permissões. | ✅ COERENTE |
| AS-05 | Email formato-independente | Requisitos | `PersonCreate.email` valida apenas `min_length=1, max_length=254`. Sem validação de formato (regex, `@`). | ✅ COERENTE — aceita qualquer string |
| AS-06 | ruff como linter/formatter | Design | Declarado em `requirements.txt`. Sem configuração `ruff.toml` ou `pyproject.toml` encontrada. | 🟡 PARCIAL — declarado mas sem evidência de execução integrada |
| AS-07 | Schema SQLAlchemy ≈ DDL documentado | Design | Models reproduzem fielmente o DDL de infrastructure.md §4: mesmos tipos, constraints, indexes. Campo extra `notes` em Vacation é a única diferença. | 🟡 PARCIAL — campo `notes` não documentado no DDL |

---

## 8. Qualidade dos Testes Existentes

### 8.1 Anti-padrões identificados

| ID | Arquivo | Teste | Anti-padrão | Descrição |
|----|---------|-------|-------------|-----------|
| [TQ-001] | test_vacations.py | `test_create_vacation_invalid_dates_returns_422` | **Docstring incorreta** | Docstring diz "BR-011" mas a regra testada é BR-002 (datas inválidas). BR-011 é email único. |
| [TQ-002] | test_vacations.py | `test_list_vacations` | **Asserção fraca** | Asserta `len(body["vacations"]) == 2` mas não verifica se são as férias corretas, nem verifica ordenação (RF-16/BR-004) |
| [TQ-003] | test_vacations.py | `test_get_vacation` | **Sem verificação de has_overlap** | Asserta person_name, team_name, days mas NÃO verifica o campo `has_overlap` que é central para RF-20 |
| [TQ-004] | test_teams.py | `test_create_team` | **Boa qualidade** | Verifica status code, campos do body, presence de id/timestamps. Sem anti-padrões. |
| [TQ-005] | conftest.py | `seed_data` | **Sem cenário de overlap** | Os dados de seed não criam sobreposição entre pessoas do mesmo time. Isso impede testar `has_overlap=true`. |

### 8.2 Avaliação geral

- **Positivo:** Testes são claros, bem nomeados, seguem padrão `test_<ação>_<cenário>`. Uso adequado de fixtures. Isolamento por banco in-memory.
- **Negativo:** Concentração exclusiva em integração (sem unitários), ausência de testes para RF-20, asserções fracas em listagens (não verificam ordenação nem conteúdo).
- **Cobertura de regras de negócio:** 11/15 BRs verificadas. Faltam: BR-003 (divergente), BR-004 (ordenação), BR-007 (múltiplos explícito), BR-012 (overlap visual).

---

## 9. Relatório de Verificação

### 9.1 Resumo

| Dimensão | Total | Verificado | Gap | Divergente |
|----------|-------|------------|-----|------------|
| Requisitos Funcionais (RF) | 20 | 15 | 3 (RF-16, RF-17, RF-20) | 2 parciais (RF-10, RF-15) |
| Requisitos Não-Funcionais (NFR) | 8 | 4 | 4 (NFR-01..NFR-04) | 0 |
| Regras de Negócio (BR) | 15 | 12 | 2 (BR-004, BR-007) | 1 (BR-003) |
| Premissas (AS) | 7 | 4 | 2 parciais (AS-06, AS-07) | 1 (AS-03) |

### 9.2 Conformidade da Especificação

**Requisitos implementados corretamente:** RF-01 a RF-09, RF-11 a RF-14, RF-18, RF-19 (15/20)
**Requisitos com divergência:**
- RF-11/BR-003: `days` calculado em vez de manual — divergência intencional, resultado melhor que a spec

**Requisitos NÃO implementados (ou não verificáveis):**
- RF-16: Ordenação implementada no código mas sem teste que valide
- RF-17: Campos na tela — implementados na API, sem verificação da UI
- RF-20: `has_overlap` implementado mas nunca testado com dados reais

### 9.3 Conformidade Arquitetural

- **ADR-001 (Monolito em camadas):** ✅ Seguido — routers → services → models
- **ADR-002 (SQLite):** ✅ Seguido
- **ADR-003 (Jinja2 SSR):** ✅ Seguido (single page com tabs em vez de 4 páginas)
- **ADR-004 (API REST /api/v1):** ⚠️ **Parcialmente** — rotas duplicadas em `routes/api.py` [ARCH-001]
- **ADR-005 (Sem auth):** ✅ Seguido
- **ADR-006 (CASCADE pessoa, RESTRICT time):** ✅ Seguido
- **ADR-007 (Overlap via highlight):** 🟡 Backend implementado (`has_overlap`), frontend não verificado

### 9.4 Avaliação de Risco

| Risco | Severidade | Descrição |
|-------|------------|-----------|
| Rotas duplicadas [ARCH-001] | 🔴 ALTA | `routes/api.py` contém bugs e duplica `routers/*.py`. Pode causar comportamento imprevisível se ambos forem registrados. |
| RF-20 sem cobertura | 🟡 MÉDIA | Overlap detection implementada mas não testada — pode ter bugs não detectados |
| BR-003 divergente | 🟡 MÉDIA | Divergência intencional e documentada — risco baixo, mas spec desatualizada |
| Frontend não testado | 🟡 MÉDIA | 4 RFs da tela inicial (RF-16 a RF-20) sem verificação visual |

### 9.5 Veredicto de Prontidão

## **CONDITIONAL_GO** ✅🟡

**Justificativa:**

O sistema está **funcional e estável** para uso. Dos 20 RFs, 15 estão cobertos por testes e verificados. Todas as regras de negócio críticas (BR-009 cascata, BR-010 bloqueio, BR-011 email único, BR-002 datas) estão implementadas e testadas.

**Condições para GO pleno:**

1. **[CRÍTICO]** Remover ou desativar `app/routes/api.py` — contém bugs e duplica rotas [ARCH-001]
2. **[IMPORTANTE]** Adicionar teste para RF-20 (`has_overlap=true`) com seed de sobreposição
3. **[IMPORTANTE]** Adicionar teste para RF-16 (verificar ordenação por start_date)
4. **[DESEJÁVEL]** Atualizar spec: BR-003 (days calculado), adicionar BR-012, documentar `notes`
5. **[DESEJÁVEL]** Corrigir docstring em test_vacations.py (BR-011 → BR-002)
