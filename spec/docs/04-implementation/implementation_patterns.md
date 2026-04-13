# Padrões de Implementação — ferias

> **Artefato RUP:** Padrões de Implementação (Implementação)
> **Proprietário:** [RUP] Desenvolvedor
> **Status:** Completo
> **Última atualização:** 2026-07-18

---

## 1. Padrão: Tuple Return (Service Layer)

**Onde:** Todos os services (`team_service.py`, `person_service.py`, `vacation_service.py`)

**Como funciona:** Funções de escrita (create/update/delete) retornam `tuple[T | None, str]` em vez de lançar exceções. O router interpreta o código de erro e levanta `HTTPException`.

```python
# Service
def create_person(db, data) -> tuple[PersonResponse | None, str]:
    if team_nao_existe:
        return None, "team_not_found"
    return response, ""

# Router
result, reason = person_service.create_person(db, data)
if reason == "team_not_found":
    raise HTTPException(status_code=422, detail="...")
```

**Motivação:** Separa decisão de negócio (service) de decisão HTTP (router). Services são testáveis sem dependência do FastAPI.

---

## 2. Padrão: Desnormalização no Response

**Onde:** `PersonResponse.team_name`, `VacationResponse.person_name`, `VacationResponse.team_name`

**Como funciona:** O schema de resposta inclui campos que não existem no model (são desnormalizados do relacionamento). O service monta esses campos via joins.

**Motivação:** Evita chamadas extras no frontend. A api_spec.md define explicitamente esses campos.

---

## 3. Padrão: Overlap Detection (RF-20)

**Onde:** `vacation_service._detect_team_overlaps()`

**Como funciona:**
1. Agrupa férias por `team_id`
2. Para cada par de férias do mesmo time, com `person_id` diferente, verifica sobreposição de intervalos
3. A regra de sobreposição: `a.start <= b.end AND a.end >= b.start`
4. Retorna `set[vacation_id]` dos que possuem sobreposição
5. O campo `has_overlap` é populado no `VacationResponse`

**Complexidade:** O(n²) por time — aceitável para ~30 pessoas (AS-01).

---

## 4. Padrão: Overlap Prevention (BR-012)

**Onde:** `vacation_service._check_overlap_same_person()`

**Como funciona:** Antes de criar/atualizar férias, busca no banco se existe outro evento da **mesma pessoa** com sobreposição. Exclui o próprio registro no caso de update.

---

## 5. Padrão: SQLite PRAGMA foreign_keys

**Onde:** `database.py`, event listener no `engine.connect`

**Como funciona:** SQLite desabilita foreign keys por padrão. O listener executa `PRAGMA foreign_keys = ON` em toda conexão nova. Isso é essencial para `ON DELETE CASCADE` funcionar na exclusão de pessoas (BR-009).

---

## 6. Padrão: Cálculo Automático de Days

**Onde:** `vacation_service._calc_days()`

**Como funciona:** `days = (end_date - start_date).days + 1` (inclusivo nas duas pontas). O campo `days` NÃO é aceito no input — é sempre calculado pelo backend.

**Divergência da spec:** O domain_model.md define BR-003 como "informado manualmente". A implementação optou por cálculo automático por instrução da tarefa — mais seguro e evita inconsistências.

---

## 7. Padrão: Lifespan para Inicialização

**Onde:** `main.py`

**Como funciona:** Usa `@asynccontextmanager` com `lifespan` para executar `create_tables()` na inicialização da app. Isso garante que as tabelas existem antes do primeiro request.
