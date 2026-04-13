# Dívida Técnica — ferias

> **Artefato RUP:** Catálogo de Dívida Técnica (Gestão de Mudanças)
> **Proprietário:** [RUP] Analista de Qualidade
> **Status:** Completo
> **Última atualização:** 2026-07-18

---

## Catálogo

| ID | Categoria | Descrição | Impacto | Esforço | Prioridade | Ref |
|----|-----------|-----------|---------|---------|------------|-----|
| TD-001 | Arquitetura | **Rotas REST duplicadas em `routes/api.py`** — 12 endpoints idênticos aos de `routers/*.py` são registrados pelo `main.py`. O arquivo `routes/api.py` contém bugs: chama `person_service.list_people` (inexistente — o método é `list_persons`), retorna objetos model em vez de response schemas, não trata erros (ignora tuplas de retorno dos services). Se ambos forem montados no FastAPI, o comportamento depende da ordem de registro. | Alto — comportamento imprevisível, bugs em produção se acessado pela rota errada | Baixo — deletar ou desativar o arquivo | **P0** |
| TD-002 | Testes | **RF-20 (overlap detection) sem cobertura** — a função `_detect_team_overlaps` nunca é exercitada com dados que produzam `has_overlap=true`. A seed de testes cria férias sem sobreposição. Um bug nessa lógica seria invisível até o uso em produção. | Alto — funcionalidade crítica sem verificação | Baixo — adicionar fixture com overlap e 1 teste | **P1** |
| TD-003 | Documentação | **Spec desatualizada: `days` calculado vs manual** — BR-003, api_spec.md §5.3 e domain_model.md definem `days` como input manual. A implementação calcula automaticamente (`end_date - start_date + 1`). Divergência intencional documentada em implementation_patterns.md §6, mas a spec raiz não foi atualizada. | Médio — confusão para futuros contribuidores que lerem a spec sem ler o código | Baixo — atualizar 3 arquivos | **P2** |
| TD-004 | Documentação | **Campo `notes` não documentado** — `Vacation.notes` (String(500), nullable) existe no model, schema e API mas NÃO consta em domain_model.md, api_spec.md ou business-rules.md. | Baixo — funcionalidade extra, não causa bugs | Baixo — adicionar campo na spec | **P2** |
| TD-005 | Documentação | **Regra BR-012 inexistente na spec** — a implementação adiciona validação de sobreposição de férias para a mesma pessoa (impede 2 férias com datas sobrepostas para o mesmo person_id). O código referencia "BR-012" em docstrings e comentários, mas o catálogo de regras em business-rules.md vai só até BR-015 e não contém BR-012. | Baixo — regra sensata mas não documentada | Baixo — adicionar BR-012 à spec | **P2** |
| TD-006 | Testes | **RF-16 (ordenação por start_date) sem teste explícito** — `test_list_vacations` asserta quantidade de resultados mas não verifica a ordem. A ordenação está implementada em `vacation_service.py:134` (`order_by start_date ASC`) mas não é verificada mecanicamente. | Médio — regressão na ordenação passaria despercebida | Baixo — adicionar assert de ordenação no teste | **P1** |
| TD-007 | Testes | **Sem testes de borda para datas** — cenário `start_date == end_date` (1 dia de férias) nunca é testado. O `_calc_days` retorna 1 corretamente, mas uma mudança acidental não seria detectada. | Baixo — cenário de borda válido | Baixo — 1 teste adicional | **P2** |
| TD-008 | Testes | **Sem testes de frontend (E2E)** — RF-17 (campos na tela), RF-18 (filtro na UI), RF-19 (toggle), RF-20 (highlight visual) não são verificados na camada de apresentação. Apenas a API é testada. | Médio — bugs visuais não detectados | Médio — requer setup de Playwright/Selenium | **P3** |
| TD-009 | Qualidade | **Docstring com referência errada** — `test_create_vacation_invalid_dates_returns_422` referencia "BR-011" na docstring, mas a regra testada é BR-002 (datas inválidas). BR-011 é unicidade de email. | Baixo — confusão ao ler testes | Baixo — corrigir 1 linha | **P3** |
| TD-010 | Qualidade | **pytest-cov declarado mas sem evidência de uso** — o pacote está em requirements.txt mas não há configuração (`pyproject.toml`, `.coveragerc`) nem CI/Makefile que execute com cobertura. Sem relatório de cobertura documentado. | Baixo — não há baseline de cobertura | Baixo — adicionar target `pytest --cov` | **P2** |
| TD-011 | Arquitetura | **`routes/pages.py` define apenas 1 rota** — api_spec.md §2 especifica 4 páginas (/, /teams, /people, /vacations). A implementação usa SPA-like com abas em index.html. Funcionalmente equivalente, mas diverge da spec. A página /teams, /people, /vacations não existem como rotas separadas. | Baixo — divergência arquitetural aceitável (SPA vs MPA) | N/A — decisão de design, não bug | **P3** |
| TD-012 | Testes | **Sem teste de update de férias com sobreposição** — `_check_overlap_same_person` tem lógica de `exclude_vacation_id` para permitir update sem falso positivo, mas nenhum teste verifica o cenário de update que CAUSA sobreposição (deveria retornar 409). | Médio — regressão no update não seria detectada | Baixo — 1 teste adicional | **P2** |
| TD-013 | Qualidade | **`config.py` define DATABASE_URL mas `database.py` calcula independentemente** — ambos os arquivos definem `DATABASE_URL` usando lógica similar mas independente. `main.py` importa `database.py`, ignorando `config.py` para o banco. Inconsistência que pode causar confusão. | Baixo — não causa bug (ambos apontam para `ferias.db`) | Baixo — centralizar em `config.py` | **P3** |

---

## Resumo por Prioridade

| Prioridade | Quantidade | IDs |
|------------|-----------|-----|
| **P0 — Crítico** | 1 | TD-001 |
| **P1 — Importante** | 2 | TD-002, TD-006 |
| **P2 — Desejável** | 5 | TD-003, TD-004, TD-005, TD-007, TD-010, TD-012 |
| **P3 — Baixo** | 4 | TD-008, TD-009, TD-011, TD-013 |

---

## Resumo por Categoria

| Categoria | Quantidade | IDs |
|-----------|-----------|-----|
| Testes | 5 | TD-002, TD-006, TD-007, TD-008, TD-012 |
| Documentação | 3 | TD-003, TD-004, TD-005 |
| Arquitetura | 2 | TD-001, TD-011 |
| Qualidade | 3 | TD-009, TD-010, TD-013 |

---

## Plano de Ação Sugerido

### Sprint Imediata (antes do uso em produção)

1. **TD-001 (P0):** Deletar `app/routes/api.py` e remover `from app.routes import api` / `app.include_router(api.router)` de `main.py`. Os routers em `app/routers/*.py` são a implementação correta e completa.
2. **TD-002 (P1):** Adicionar fixture de overlap e teste em `test_vacations.py`
3. **TD-006 (P1):** Adicionar assert de ordenação em `test_list_vacations`

### Sprint de Consolidação

4. **TD-003, TD-004, TD-005 (P2):** Atualizar spec (BR-003, notes, BR-012)
5. **TD-007 + TD-012 (P2):** Adicionar testes de borda
6. **TD-010 (P2):** Configurar pytest-cov com target mínimo

### Backlog

7. **TD-008 (P3):** Avaliar necessidade de E2E (Playwright)
8. **TD-009, TD-011, TD-013 (P3):** Correções menores
