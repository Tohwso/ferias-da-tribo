# Padrões de Teste — ferias

> **Artefato RUP:** Padrões de Teste por Padrão de Implementação (Qualidade)
> **Proprietário:** [RUP] Analista de Qualidade
> **Status:** Completo
> **Última atualização:** 2026-07-18

---

## 1. Padrão: Tuple Return (Service Layer)

**Referência:** implementation_patterns.md §1

### Abordagem de teste

Os services retornam `tuple[T | None, str]`. O teste verifica AMBOS os valores da tupla:
- Sucesso: `(response, "")` — verificar que o response tem os dados esperados e reason é vazio
- Falha: `(None, "codigo_erro")` — verificar que result é None e reason corresponde ao cenário

### Como é testado atualmente

Via integração (API): os routers convertem as tuplas em status codes HTTP. Os testes verificam o status code e o body.

```python
# Exemplo real — tests/test_persons.py::test_create_person_duplicate_email_returns_409
resp = client.post("/api/v1/people", json={...email duplicado...})
assert resp.status_code == 409          # Router converteu ("email_duplicate") → 409
assert "email" in resp.json()["detail"]  # Mensagem do HTTPException
```

### Armadilhas

- Se o router não tratar um código de erro (ex: `reason == "xyz"` sem `if`), a função retorna `None` e o FastAPI pode retornar 200 com body nulo — silencioso e perigoso.
- **Finding atual:** `routes/api.py` NÃO trata tuplas corretamente (retorna a tupla inteira). Os routers em `routers/*.py` tratam adequadamente.

### Teste recomendado (unitário)

```python
def test_create_person_returns_team_not_found():
    result, reason = person_service.create_person(db, data_com_team_invalido)
    assert result is None
    assert reason == "team_not_found"
```

---

## 2. Padrão: Desnormalização no Response

**Referência:** implementation_patterns.md §2

### Abordagem de teste

Verificar que os campos desnormalizados (`team_name`, `person_name`, `vacation_count`) estão presentes e corretos na resposta JSON.

### Como é testado atualmente

```python
# tests/test_persons.py::test_create_person
body = resp.json()
assert body["team_name"] == "Produto"      # Desnormalizado
assert body["vacation_count"] == 0         # Calculado via COUNT

# tests/test_vacations.py::test_get_vacation
body = resp.json()
assert body["person_name"] == "Alice Silva"  # Desnormalizado
assert body["team_name"] == "Engenharia"     # Desnormalizado
```

### Armadilhas

- Se o join falhar (pessoa sem time — impossível pela FK, mas defensivamente), os defaults `""` e `0` dos schemas mascaram o erro silenciosamente.
- Verificar que após UPDATE de time (nome), os responses de pessoa/férias refletem o novo nome.

### Teste recomendado

```python
def test_person_response_reflects_team_name_change():
    # Cria time, cria pessoa, atualiza nome do time
    # GET pessoa → assert team_name == novo_nome
```

---

## 3. Padrão: Overlap Detection (RF-20)

**Referência:** implementation_patterns.md §3

### Abordagem de teste

A função `_detect_team_overlaps(vacations: list[dict])` é pura — recebe lista de dicts e retorna `set[int]` de IDs com sobreposição. Ideal para teste unitário direto.

### Como é testado atualmente

**⬜ NÃO TESTADO.** A seed de dados no `conftest.py` cria férias que NÃO se sobrepõem entre pessoas do mesmo time:
- Alice (Engenharia): dias 30-44 futuro
- Bob (Engenharia): dias 60-74 futuro
- Intervalos disjuntos → `has_overlap` sempre `false`

### Cenários que deveriam ser testados

| Cenário | Dados | Resultado Esperado |
|---------|-------|--------------------|
| Sem sobreposição | Alice: Jan 1-15, Bob: Fev 1-15 | `has_overlap=false` para ambos |
| Sobreposição parcial | Alice: Jan 1-15, Bob: Jan 10-25 | `has_overlap=true` para ambos |
| Sobreposição total | Alice: Jan 1-30, Bob: Jan 5-10 | `has_overlap=true` para ambos |
| Sobreposição exata | Alice: Jan 1-15, Bob: Jan 1-15 | `has_overlap=true` para ambos |
| Limite adjacente | Alice: Jan 1-15, Bob: Jan 15-30 | `has_overlap=true` (dia 15 compartilhado) |
| Adjacente sem overlap | Alice: Jan 1-14, Bob: Jan 15-30 | `has_overlap=false` |
| Times diferentes | Alice (Eng): Jan 1-15, Carol (Prod): Jan 1-15 | `has_overlap=false` (times diferentes) |
| Mesma pessoa | Alice: Jan 1-15, Alice: Fev 1-15 | `has_overlap=false` (mesmo person_id, sem comparação) |

### Teste recomendado (unitário)

```python
def test_detect_team_overlaps_partial():
    vacations = [
        {"id": 1, "person_id": 1, "team_id": 1, "start_date": date(2026, 1, 1), "end_date": date(2026, 1, 15)},
        {"id": 2, "person_id": 2, "team_id": 1, "start_date": date(2026, 1, 10), "end_date": date(2026, 1, 25)},
    ]
    overlap_ids = _detect_team_overlaps(vacations)
    assert overlap_ids == {1, 2}
```

---

## 4. Padrão: Overlap Prevention (BR-012)

**Referência:** implementation_patterns.md §4

### Abordagem de teste

Verifica que uma pessoa NÃO pode ter dois eventos de férias com datas sobrepostas.

### Como é testado atualmente

```python
# tests/test_vacations.py::test_create_vacation_overlap_same_person_returns_409
# Cria férias sobrepostas para Alice → 409
resp = client.post("/api/v1/vacations", json={
    "person_id": alice_id,
    "start_date": existing.start_date + 5 dias,
    "end_date": existing.end_date + 10 dias,
})
assert resp.status_code == 409
assert "sobrepõe" in resp.json()["detail"]
```

### Armadilhas

- O teste de update com sobreposição (`exclude_vacation_id`) não está coberto — um update que move o período para sobrepor outro da mesma pessoa deveria retornar 409.
- Cenário de borda: update com o mesmo período (sem alterar) deveria passar (o `exclude_vacation_id` garante isso, mas não há teste).

---

## 5. Padrão: SQLite PRAGMA foreign_keys

**Referência:** implementation_patterns.md §5

### Abordagem de teste

O `conftest.py` replica o PRAGMA corretamente:

```python
@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, _connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()
```

### Como é testado atualmente

Indiretamente via `test_delete_person_cascades_vacations` — se o PRAGMA não estivesse habilitado, o `ON DELETE CASCADE` não funcionaria e as férias ficariam órfãs.

### Teste recomendado

```python
def test_foreign_key_constraint_prevents_orphan_person():
    """Tenta criar pessoa com team_id inválido diretamente no banco."""
    with pytest.raises(IntegrityError):
        db.add(Person(name="X", email="x@x.com", team_id=99999))
        db.commit()
```

---

## 6. Padrão: Cálculo Automático de Days

**Referência:** implementation_patterns.md §6

### Abordagem de teste

Verifica que `days` no response = `(end_date - start_date).days + 1`.

### Como é testado atualmente

```python
# tests/test_vacations.py::test_create_vacation
start = date.today() + timedelta(days=90)
end = start + timedelta(days=9)  # 10 dias
resp = client.post("/api/v1/vacations", json={...})
assert body["days"] == 10  # end - start + 1 = 10
```

```python
# tests/test_vacations.py::test_update_vacation
new_end = new_start + timedelta(days=4)  # 5 dias
assert body["days"] == 5
```

### Armadilhas

- Cenário de borda NÃO testado: `start_date == end_date` → `days` deveria ser 1
- Cenário com dias negativos é impedido pelo validator Pydantic (testado em `test_create_vacation_invalid_dates_returns_422`)

---

## 7. Padrão: Lifespan para Inicialização

**Referência:** implementation_patterns.md §7

### Abordagem de teste

O `conftest.py` usa `create_app()` (factory) e cria as tabelas via `Base.metadata.create_all()` na fixture `db_session`. O lifespan da app real (que também chama `create_tables()`) é executado pelo `TestClient` ao entrar no context manager.

### Como é testado atualmente

Indiretamente — se o lifespan falhasse, todos os testes falhariam ao tentar operar no banco.

### Armadilha

- O lifespan executa `create_tables()` que é idempotente (via `create_all`). Não há risco de falha, mas também não há teste explícito de que o lifespan funciona.

---

## 8. Padrão: Filtro por Time + Toggle Passadas

**Referência:** api_spec.md §5.1

### Abordagem de teste

Testa os query parameters `team_id` e `include_past` do endpoint GET /api/v1/vacations.

### Como é testado atualmente

```python
# test_filter_vacations_by_team — Filtra por time Engenharia
resp = client.get(f"/api/v1/vacations?team_id={team_eng_id}&include_past=true")
assert len(vacations) == 3  # Alice(2) + Bob(1)
assert all(v["team_id"] == team_eng_id for v in vacations)

# test_filter_include_past — Toggle passadas
resp_no_past = client.get("/api/v1/vacations")
assert len(resp_no_past.json()["vacations"]) == 2  # apenas futuras

resp_with_past = client.get("/api/v1/vacations?include_past=true")
assert len(resp_with_past.json()["vacations"]) == 4  # todas
```

### Armadilhas

- Não testa combinação `team_id` + `include_past=false` (filtro por time sem passadas)
- Não testa `team_id` inválido (time inexistente) — deveria retornar lista vazia, não erro

---

## 9. Resumo de Cobertura por Padrão

| # | Padrão | Testado? | Qualidade | Recomendação |
|---|--------|----------|-----------|--------------|
| 1 | Tuple Return | ✅ Indiretamente | 🟡 Boa — mas só via integração | Adicionar testes unitários de services |
| 2 | Desnormalização | ✅ | 🟢 Boa | Testar consistência após update de entidade referenciada |
| 3 | Overlap Detection | ⬜ Não | 🔴 Ausente | **Prioridade alta** — adicionar seed com overlap |
| 4 | Overlap Prevention | ✅ | 🟡 Boa | Adicionar teste de update com overlap |
| 5 | PRAGMA foreign_keys | ✅ Indiretamente | 🟢 Boa | Teste já validado pela cascata |
| 6 | Days Calculado | ✅ | 🟡 Boa | Testar borda (start == end → days=1) |
| 7 | Lifespan | ✅ Indiretamente | 🟢 Boa | Não necessita teste adicional |
| 8 | Filtros | ✅ | 🟡 Boa | Testar combinações e team_id inválido |
