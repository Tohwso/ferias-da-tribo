# Estratégia de Testes — ferias

> **Artefato RUP:** Estratégia de Testes (Qualidade)
> **Proprietário:** [RUP] Analista de Qualidade
> **Status:** Completo
> **Última atualização:** 2026-07-18

---

## 1. Objetivos da Estratégia

Garantir que a implementação do sistema **ferias** satisfaça os 20 requisitos funcionais (RF-01 a RF-20), 8 requisitos não-funcionais (NFR-01 a NFR-08) e 15 regras de negócio (BR-001 a BR-015) documentados nas fases anteriores do pipeline SDD.

---

## 2. Pirâmide de Testes

```
        ┌──────────────┐
        │    E2E /      │  ⬜ NÃO IMPLEMENTADO
        │   Frontend    │  (testes visuais, Playwright/Selenium)
        ├──────────────┤
        │  Integração   │  ✅ 25 testes — TestClient + SQLite in-memory
        │  (API)        │  Cobre: endpoints REST, status codes, payloads,
        │               │  regras de negócio via HTTP
        ├──────────────┤
        │   Unitários   │  ⬜ NÃO IMPLEMENTADO
        │  (Services)   │  (services testados indiretamente via integração)
        └──────────────┘
```

### Análise da pirâmide

A suíte atual concentra-se **exclusivamente** na camada de integração (API). Isso cobre o fluxo completo routes→services→models→banco, o que é eficiente para um projeto deste porte. Porém:

- **Testes unitários de services** não existem como camada separada. Os services são exercitados indiretamente pelos testes de API, mas sem isolamento — se um teste falha, a causa pode estar no service, no router ou no banco.
- **Testes de frontend** (E2E) não existem. O template Jinja2, o JavaScript de `app.js` e o comportamento de `style.css` não são verificados automaticamente. Isso é relevante para RF-17 (exibição de dados na tela), RF-18 (filtro por time na UI), RF-19 (toggle passadas) e RF-20 (highlight de sobreposição).

---

## 3. Frameworks e Ferramentas

| Ferramenta | Versão | Propósito | Status |
|------------|--------|-----------|--------|
| `pytest` | >=8.0 | Framework de testes (runner, fixtures, assertions) | ✅ Em uso |
| `httpx` | >=0.27 | HTTP client usado pelo `TestClient` do FastAPI | ✅ Em uso |
| `pytest-cov` | >=5.0 | Relatório de cobertura de código | ✅ Declarado, uso não evidenciado |
| `ruff` | >=0.5 | Linter/formatter (qualidade de código, não testes) | ✅ Declarado |
| Playwright/Selenium | — | Testes E2E de frontend | ⬜ Não instalado |
| `mypy` | — | Type checking estático | ⬜ Opcional, não instalado |

---

## 4. Estratégia de Dados de Teste

### 4.1 Fixture `seed_data`

O `conftest.py` define uma fixture `seed_data` que popula o banco in-memory com:

| Entidade | Quantidade | Detalhes |
|----------|-----------|----------|
| Teams | 2 | Engenharia, Produto |
| Persons | 3 | Alice e Bob em Engenharia, Carol em Produto |
| Vacations | 4 | 2 futuras (Alice, Bob), 2 passadas (Alice, Carol) |

**Pontos positivos:**
- Dados cobrem cenários multi-time, multi-pessoa e passado/futuro
- Fixture `seeded_client` combina client + seed para facilitar uso

**Gaps identificados:**
- Não há seed com sobreposição de férias entre pessoas do mesmo time (necessário para RF-20)
- Não há seed com volume (~30 pessoas) para validar NFR-07
- Não há seed com dados de borda (datas iguais start=end, dias=1)

### 4.2 Isolamento

Cada teste usa um banco SQLite in-memory com `StaticPool`, criado e destruído por fixture. Isso garante:
- Isolamento total entre testes
- Nenhum artefato persistente
- Reprodutibilidade

### 4.3 PRAGMA foreign_keys

O `conftest.py` replica corretamente o `PRAGMA foreign_keys = ON` do `database.py` de produção. Isso é **crítico** para que os testes de cascata (BR-009) reflitam o comportamento real.

---

## 5. Perfis de Teste

### 5.1 Integração (API) — ✅ Implementado

- **O que testa:** Endpoints REST (`/api/v1/*`) via `TestClient`
- **Como:** Request HTTP → assert status code + body
- **Banco:** SQLite in-memory (mesmo dialect de produção)
- **Cobertura:** CRUD completo (teams, persons, vacations) + regras de negócio (BR-009, BR-010, BR-011, BR-012)

### 5.2 Unitário (Services) — ⬜ Não implementado

- **O que testaria:** Funções de `team_service`, `person_service`, `vacation_service` isoladas
- **Como:** Mock de `Session` do SQLAlchemy, testar lógica pura
- **Valor:** Isolaria falhas mais rapidamente; testaria `_detect_team_overlaps()` com datasets controlados

### 5.3 E2E (Frontend) — ⬜ Não implementado

- **O que testaria:** Navegação, formulários, filtros, toggle, highlight de sobreposição
- **Como:** Playwright ou Selenium contra o servidor real
- **Valor:** Verificaria RF-17, RF-18, RF-19, RF-20 na camada visual

---

## 6. Estratégia de Mocking

O projeto **não usa mocks**. Todos os testes são de integração, exercitando a stack completa (router → service → model → banco SQLite in-memory).

**Avaliação:**
- Para um projeto deste porte (~3 entidades, ~12 endpoints), a abordagem é adequada — o custo de mocking superaria o benefício.
- O único ponto onde mocking agregaria valor é no teste isolado de `_detect_team_overlaps()` (função pura que recebe lista de dicts).

---

## 7. Metas de Cobertura

| Camada | Meta Sugerida | Estado Atual | Gap |
|--------|---------------|--------------|-----|
| Services (lógica de negócio) | ≥ 90% | ~80% (estimado — via integração indireta) | Faltam testes de `_detect_team_overlaps` com cenários variados |
| Routers (API) | ≥ 85% | ~85% (estimado) | Faltam testes de validação Pydantic em borda |
| Models | ≥ 70% | ~60% (estimado — CHECK constraints não testados diretamente) | CHECK constraints do banco não exercitados |
| Frontend (JS/HTML) | ≥ 50% | 0% | Sem testes E2E |

> **Nota:** Percentuais estimados — `pytest-cov` está declarado como dependência mas não há evidência de relatório de cobertura gerado. Recomenda-se rodar `pytest --cov=app --cov-report=term-missing` e documentar o resultado.

---

## 8. Gaps Críticos

| # | Gap | Impacto | Requisitos Afetados | Prioridade |
|---|-----|---------|---------------------|------------|
| G-01 | Sem testes para RF-20 (overlap detection entre times) | A lógica de `_detect_team_overlaps` não é exercitada com dados que geram sobreposição | RF-20 | Alta |
| G-02 | Sem testes de frontend (E2E) | RF-17 (exibição), RF-18 (filtro UI), RF-19 (toggle), RF-20 (highlight visual) não verificados | RF-17, RF-18, RF-19, RF-20 | Média |
| G-03 | Sem teste de CHECK constraint (`days > 0`) | O constraint `ck_vacation_days_positive` do banco não é exercitado | BR-003 | Baixa |
| G-04 | Sem teste de volume (~30 pessoas) | NFR-07 não validado | NFR-07 | Baixa |
| G-05 | Sem teste de dados de borda (start_date == end_date, days=1) | Comportamento limítrofe não verificado | BR-002, BR-003 | Média |
| G-06 | Campo `notes` no model Vacation não existe na spec | O model tem `notes: Mapped[str | None]` mas api_spec.md e domain_model.md não definem esse campo | — | Baixa |

---

## 9. Rastreabilidade — Estratégia × Requisitos

| Requisito | Verificação Planejada | Status |
|-----------|-----------------------|--------|
| RF-01 a RF-04 (Times) | Testes de integração API | ✅ Coberto |
| RF-05 a RF-10 (Pessoas) | Testes de integração API | ✅ Coberto |
| RF-11 a RF-15 (Férias CRUD) | Testes de integração API | ✅ Coberto |
| RF-16 (ordenação) | Verificação indireta via `test_list_vacations` | 🟡 Parcial — não asserta ordenação explicitamente |
| RF-17 (campos na tela) | Sem teste E2E | ⬜ Não coberto |
| RF-18 (filtro por time) | `test_filter_vacations_by_team` | ✅ Coberto (API) |
| RF-19 (toggle passadas) | `test_filter_include_past` | ✅ Coberto (API) |
| RF-20 (sobreposição visual) | Sem teste de overlap detection com dados reais | ⬜ Não coberto |
| NFR-01 a NFR-02 (performance) | Sem teste de performance | ⬜ Não coberto |
| NFR-05 (100% local) | Verificação manual — sem dependências externas | ✅ Coberto (inspeção) |
| BR-002 (datas válidas) | `test_create_vacation_invalid_dates_returns_422` | ✅ Coberto |
| BR-009 (cascata) | `test_delete_person_cascades_vacations` | ✅ Coberto |
| BR-010 (bloqueio exclusão time) | `test_delete_team_with_persons_returns_409` | ✅ Coberto |
| BR-011 (email único) | `test_create_person_duplicate_email_returns_409` | ✅ Coberto |
| BR-012 (sobreposição mesma pessoa) | `test_create_vacation_overlap_same_person_returns_409` | ✅ Coberto |
