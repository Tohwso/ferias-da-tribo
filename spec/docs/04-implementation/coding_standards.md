# Padrões de Codificação — ferias

> **Artefato RUP:** Padrões de Codificação (Implementação)
> **Proprietário:** [RUP] Desenvolvedor
> **Status:** Completo
> **Última atualização:** 2026-07-18

---

## 1. Estrutura de Pacotes

```
app/
├── __init__.py           # Pacote raiz (vazio)
├── main.py               # Entry point — FastAPI app, routers, CORS, lifespan
├── database.py           # Engine, SessionLocal, Base, get_db(), create_tables()
├── models/               # SQLAlchemy ORM models (1 arquivo por entidade)
├── schemas/              # Pydantic schemas (1 arquivo por entidade)
├── services/             # Lógica de negócio (1 arquivo por entidade)
└── routers/              # FastAPI routers REST (1 arquivo por entidade)
```

## 2. Convenções de Nomenclatura

| Elemento | Convenção | Exemplo |
|----------|-----------|---------|
| Módulos/pacotes | `snake_case` | `team_service.py` |
| Classes (models) | `PascalCase`, singular | `Team`, `Person`, `Vacation` |
| Classes (schemas) | `PascalCase`, sufixo por finalidade | `TeamCreate`, `TeamResponse` |
| Funções (services) | `snake_case`, verbo + substantivo | `create_team()`, `list_persons()` |
| Funções (routers) | `snake_case`, verbo em português | `listar_times()`, `criar_pessoa()` |
| Variáveis | `snake_case` | `team_id`, `person_count` |
| Constantes | `UPPER_SNAKE_CASE` | `DATABASE_URL` |

## 3. Tratamento de Erros

Os services retornam **tuplas** `(resultado, motivo_erro)` ao invés de lançar exceções:
- Sucesso: `(objeto, "")`
- Falha: `(None, "codigo_erro")`

Os routers convertem esses códigos em `HTTPException` com status e mensagem adequados (conforme api_spec.md).

Códigos de erro padrão:
- `"not_found"` → 404
- `"has_persons"` → 409 (BR-010)
- `"email_duplicate"` → 409 (BR-011)
- `"team_not_found"` → 422
- `"person_not_found"` → 422
- `"overlap_same_person"` → 409 (BR-012)

## 4. Padrão de Timestamps

- `created_at`: preenchido via `default=_utcnow` (factory function retornando `datetime.now(UTC)`)
- `updated_at`: preenchido via `default=_utcnow` + `onupdate=_utcnow`
- Todos os timestamps são UTC

## 5. Organização de Imports

Ordem: stdlib → third-party → app (separados por linha em branco).

```python
from datetime import datetime, timezone       # stdlib

from sqlalchemy.orm import Session            # third-party

from app.models.team import Team              # app
from app.schemas.team import TeamResponse     # app
```
