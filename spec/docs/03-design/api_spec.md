# Especificação da API — ferias

> **Artefato RUP:** Especificação de API (Análise & Design)
> **Proprietário:** [RUP] Arquiteto
> **Status:** Completo
> **Última atualização:** 2026-07-17

---

## 1. Convenções Gerais

- **Base URL:** `http://localhost:8000`
- **Prefixo API:** `/api/v1`
- **Content-Type:** `application/json` (request e response)
- **Autenticação:** Nenhuma (BR-013, NFR-08)
- **Formato de datas:** `YYYY-MM-DD` (ISO 8601, sem hora)
- **IDs:** Inteiros auto-incrementados pelo banco

### Códigos de Status Padrão

| Código | Significado | Quando |
|--------|-------------|--------|
| 200 | OK | Leitura ou atualização bem-sucedida |
| 201 | Created | Criação bem-sucedida |
| 204 | No Content | Exclusão bem-sucedida |
| 404 | Not Found | Entidade não encontrada |
| 409 | Conflict | Violação de unicidade ou integridade (BR-010, BR-011) |
| 422 | Unprocessable Entity | Dados inválidos (validação Pydantic/BR-002) |
| 500 | Internal Server Error | Erro inesperado |

---

## 2. Páginas HTML (Server-Side Rendering)

Estas rotas servem páginas completas renderizadas com Jinja2:

| Método | Path | Descrição | UC |
|--------|------|-----------|-----|
| GET | `/` | Tela inicial — agenda de férias | UC-004 |
| GET | `/teams` | Gestão de times | UC-001 |
| GET | `/people` | Gestão de pessoas | UC-002 |
| GET | `/vacations` | Gestão de eventos de férias | UC-003 |

> As páginas usam `fetch()` (JavaScript) para consumir os endpoints da API REST abaixo.

---

## 3. API REST — Times

### 3.1 Listar Times

```
GET /api/v1/teams
```

**Resposta 200:**
```json
[
  {
    "id": 1,
    "name": "Backend",
    "description": "Time de backend",
    "person_count": 5,
    "created_at": "2026-07-17T10:30:00",
    "updated_at": "2026-07-17T10:30:00"
  }
]
```

> Inclui `person_count` para informar na UI quantas pessoas o time possui (útil para BR-010 — o usuário vê se pode excluir).

**RF:** RF-04

---

### 3.2 Obter Time por ID

```
GET /api/v1/teams/{team_id}
```

**Resposta 200:** Objeto time (mesmo formato acima, sem array)

**Resposta 404:**
```json
{
  "detail": "Time não encontrado"
}
```

---

### 3.3 Criar Time

```
POST /api/v1/teams
```

**Request body:**
```json
{
  "name": "Backend",
  "description": "Time de backend"
}
```

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| name | string | Sim | 1-100 caracteres, não-vazio |
| description | string | Não | 0-500 caracteres |

**Resposta 201:** Objeto time criado (com id)

**Resposta 422:** Campos inválidos

**RF:** RF-01 | **BR:** BR-008

---

### 3.4 Atualizar Time

```
PUT /api/v1/teams/{team_id}
```

**Request body:** Mesmo formato de criação

**Resposta 200:** Objeto time atualizado

**Resposta 404:** Time não encontrado

**Resposta 422:** Campos inválidos

**RF:** RF-02

---

### 3.5 Excluir Time

```
DELETE /api/v1/teams/{team_id}
```

**Resposta 204:** Sem corpo (excluído com sucesso)

**Resposta 404:** Time não encontrado

**Resposta 409:**
```json
{
  "detail": "Não é possível excluir o time: existem pessoas vinculadas. Remova ou mova as pessoas antes."
}
```

**RF:** RF-03 | **BR:** BR-010

---

## 4. API REST — Pessoas

### 4.1 Listar Pessoas

```
GET /api/v1/people
```

**Query parameters:**

| Param | Tipo | Obrigatório | Descrição |
|-------|------|-------------|-----------|
| team_id | int | Não | Filtra por time |

**Resposta 200:**
```json
[
  {
    "id": 1,
    "name": "João Silva",
    "email": "joao@empresa.com",
    "team_id": 1,
    "team_name": "Backend",
    "vacation_count": 2,
    "created_at": "2026-07-17T10:30:00",
    "updated_at": "2026-07-17T10:30:00"
  }
]
```

> Inclui `team_name` (desnormalizado na resposta) para evitar join no frontend e `vacation_count` para contexto.

**RF:** RF-09

---

### 4.2 Obter Pessoa por ID

```
GET /api/v1/people/{person_id}
```

**Resposta 200:** Objeto pessoa

**Resposta 404:**
```json
{
  "detail": "Pessoa não encontrada"
}
```

---

### 4.3 Criar Pessoa

```
POST /api/v1/people
```

**Request body:**
```json
{
  "name": "João Silva",
  "email": "joao@empresa.com",
  "team_id": 1
}
```

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| name | string | Sim | 1-150 caracteres |
| email | string | Sim | 1-254 caracteres, UNIQUE |
| team_id | int | Sim | Deve existir na tabela team |

**Resposta 201:** Objeto pessoa criado

**Resposta 409:**
```json
{
  "detail": "Já existe uma pessoa cadastrada com este email"
}
```

**Resposta 422:** Campos inválidos ou team_id inexistente

**RF:** RF-05, RF-06, RF-10 | **BR:** BR-001, BR-011

---

### 4.4 Atualizar Pessoa

```
PUT /api/v1/people/{person_id}
```

**Request body:** Mesmo formato de criação

**Resposta 200:** Objeto pessoa atualizado

**Resposta 404:** Pessoa não encontrada

**Resposta 409:** Email duplicado

**Resposta 422:** Campos inválidos

**RF:** RF-07 | **BR:** BR-001, BR-011

---

### 4.5 Excluir Pessoa

```
DELETE /api/v1/people/{person_id}
```

**Resposta 204:** Sem corpo. Pessoa e todos os seus eventos de férias excluídos em cascata.

**Resposta 404:** Pessoa não encontrada

**RF:** RF-08 | **BR:** BR-009

---

## 5. API REST — Férias

### 5.1 Listar Férias

```
GET /api/v1/vacations
```

**Query parameters:**

| Param | Tipo | Obrigatório | Descrição | Regra |
|-------|------|-------------|-----------|-------|
| team_id | int | Não | Filtra por time | BR-005, BR-006 |
| include_past | bool | Não (default: false) | Se true, inclui eventos com end_date < hoje | RF-19 |

**Resposta 200:**
```json
{
  "vacations": [
    {
      "id": 1,
      "person_id": 1,
      "person_name": "João Silva",
      "team_id": 1,
      "team_name": "Backend",
      "start_date": "2026-08-01",
      "end_date": "2026-08-15",
      "days": 15,
      "has_overlap": true,
      "created_at": "2026-07-17T10:30:00",
      "updated_at": "2026-07-17T10:30:00"
    }
  ],
  "teams": [
    {
      "id": 1,
      "name": "Backend"
    }
  ]
}
```

> **`has_overlap`:** Flag calculada pelo backend — indica se este evento se sobrepõe com outro evento de pessoa do mesmo time (RF-20, ADR-007).
>
> **`teams`:** Lista resumida de times para popular o filtro na tela inicial sem chamada extra.
>
> **Ordenação:** `ORDER BY start_date ASC` (BR-004).
>
> **Filtro padrão:** Sem `include_past`, retorna apenas eventos com `end_date >= hoje` (RF-19).

**RF:** RF-16, RF-17, RF-18, RF-19, RF-20

---

### 5.2 Obter Férias por ID

```
GET /api/v1/vacations/{vacation_id}
```

**Resposta 200:** Objeto vacation (mesmo formato acima, sem array wrapper)

**Resposta 404:**
```json
{
  "detail": "Evento de férias não encontrado"
}
```

---

### 5.3 Criar Evento de Férias

```
POST /api/v1/vacations
```

**Request body:**
```json
{
  "person_id": 1,
  "start_date": "2026-08-01",
  "end_date": "2026-08-15",
  "days": 15
}
```

| Campo | Tipo | Obrigatório | Validação |
|-------|------|-------------|-----------|
| person_id | int | Sim | Deve existir na tabela person |
| start_date | date (YYYY-MM-DD) | Sim | — |
| end_date | date (YYYY-MM-DD) | Sim | >= start_date (BR-002) |
| days | int | Sim | > 0 (BR-003) |

**Resposta 201:** Objeto vacation criado

**Resposta 422:**
```json
{
  "detail": "Data de início deve ser anterior ou igual à data de fim"
}
```

**RF:** RF-11, RF-12, RF-15 | **BR:** BR-002, BR-003, BR-007

---

### 5.4 Atualizar Evento de Férias

```
PUT /api/v1/vacations/{vacation_id}
```

**Request body:**
```json
{
  "person_id": 1,
  "start_date": "2026-08-01",
  "end_date": "2026-08-20",
  "days": 20
}
```

**Resposta 200:** Objeto vacation atualizado

**Resposta 404:** Evento não encontrado

**Resposta 422:** Dados inválidos

**RF:** RF-13 | **BR:** BR-002, BR-003

---

### 5.5 Excluir Evento de Férias

```
DELETE /api/v1/vacations/{vacation_id}
```

**Resposta 204:** Sem corpo

**Resposta 404:** Evento não encontrado

**RF:** RF-14

---

## 6. Schemas Pydantic (Resumo)

```python
# === Teams ===
class TeamCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)

class TeamResponse(BaseModel):
    id: int
    name: str
    description: str | None
    person_count: int
    created_at: datetime
    updated_at: datetime

# === People ===
class PersonCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    email: str = Field(..., min_length=1, max_length=254)
    team_id: int

class PersonResponse(BaseModel):
    id: int
    name: str
    email: str
    team_id: int
    team_name: str
    vacation_count: int
    created_at: datetime
    updated_at: datetime

# === Vacations ===
class VacationCreate(BaseModel):
    person_id: int
    start_date: date
    end_date: date
    days: int = Field(..., gt=0)

    @model_validator(mode="after")
    def check_dates(self):
        if self.start_date > self.end_date:
            raise ValueError("Data de início deve ser anterior ou igual à data de fim")
        return self

class VacationResponse(BaseModel):
    id: int
    person_id: int
    person_name: str
    team_id: int
    team_name: str
    start_date: date
    end_date: date
    days: int
    has_overlap: bool
    created_at: datetime
    updated_at: datetime

class VacationListResponse(BaseModel):
    vacations: list[VacationResponse]
    teams: list[TeamSummary]
```

---

## 7. Rastreabilidade — Endpoints × Requisitos

| Endpoint | RF | BR |
|----------|----|----|
| GET /api/v1/teams | RF-04 | — |
| POST /api/v1/teams | RF-01 | BR-008 |
| PUT /api/v1/teams/{id} | RF-02 | — |
| DELETE /api/v1/teams/{id} | RF-03 | BR-010 |
| GET /api/v1/people | RF-09 | — |
| POST /api/v1/people | RF-05, RF-06, RF-10 | BR-001, BR-011 |
| PUT /api/v1/people/{id} | RF-07 | BR-001, BR-011 |
| DELETE /api/v1/people/{id} | RF-08 | BR-009 |
| GET /api/v1/vacations | RF-16, RF-17, RF-18, RF-19, RF-20 | BR-004, BR-005, BR-006 |
| POST /api/v1/vacations | RF-11, RF-12, RF-15 | BR-002, BR-003, BR-007 |
| PUT /api/v1/vacations/{id} | RF-13 | BR-002, BR-003 |
| DELETE /api/v1/vacations/{id} | RF-14 | — |
