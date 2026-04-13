"""
Schemas Pydantic: Team (Time).

Define contratos de entrada (Create/Update) e saída (Response).
Ref: api_spec.md §3 | §6
"""

from datetime import datetime

from pydantic import BaseModel, Field


class TeamCreate(BaseModel):
    """Payload para criação de time. RF-01"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class TeamUpdate(BaseModel):
    """Payload para atualização de time. RF-02"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)


class TeamResponse(BaseModel):
    """Representação de time na resposta — inclui person_count. RF-04"""
    id: int
    name: str
    description: str | None
    person_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TeamSummary(BaseModel):
    """Resumo de time para uso na listagem de férias (api_spec.md §5.1)."""
    id: int
    name: str

    model_config = {"from_attributes": True}
