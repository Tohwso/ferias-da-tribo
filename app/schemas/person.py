"""
Schemas Pydantic: Person (Pessoa).

Define contratos de entrada (Create/Update) e saída (Response).
Ref: api_spec.md §4 | §6 | BR-001, BR-011
"""

from datetime import datetime

from pydantic import BaseModel, Field


class PersonCreate(BaseModel):
    """Payload para criação de pessoa. RF-05, RF-06, RF-10"""
    name: str = Field(..., min_length=1, max_length=150)
    email: str = Field(..., min_length=1, max_length=254)
    team_id: int


class PersonUpdate(BaseModel):
    """Payload para atualização de pessoa. RF-07"""
    name: str = Field(..., min_length=1, max_length=150)
    email: str = Field(..., min_length=1, max_length=254)
    team_id: int


class PersonResponse(BaseModel):
    """
    Representação de pessoa na resposta.
    Inclui team_name (desnormalizado) e vacation_count. RF-09
    """
    id: int
    name: str
    email: str
    team_id: int
    team_name: str = ""
    vacation_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
