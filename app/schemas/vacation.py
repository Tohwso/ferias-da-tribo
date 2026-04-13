"""
Schemas Pydantic: Vacation (Evento de Férias).

Define contratos de entrada (Create/Update) e saída (Response/List).
Ref: api_spec.md §5 | §6 | BR-002, BR-003, BR-007
"""

from datetime import date, datetime

from pydantic import BaseModel, Field, model_validator

from app.schemas.team import TeamSummary


class VacationCreate(BaseModel):
    """
    Payload para criação de evento de férias. RF-11, RF-12, RF-15
    O campo 'days' é calculado automaticamente (end_date - start_date + 1).
    O campo 'notes' é opcional.
    """
    person_id: int
    start_date: date
    end_date: date
    notes: str | None = Field(None, max_length=500)

    @model_validator(mode="after")
    def check_dates(self) -> "VacationCreate":
        """BR-011: start_date <= end_date"""
        if self.start_date > self.end_date:
            raise ValueError(
                "Data de início deve ser anterior ou igual à data de fim"
            )
        return self


class VacationUpdate(BaseModel):
    """Payload para atualização de evento de férias. RF-13"""
    person_id: int
    start_date: date
    end_date: date
    notes: str | None = Field(None, max_length=500)

    @model_validator(mode="after")
    def check_dates(self) -> "VacationUpdate":
        """BR-011: start_date <= end_date"""
        if self.start_date > self.end_date:
            raise ValueError(
                "Data de início deve ser anterior ou igual à data de fim"
            )
        return self


class VacationResponse(BaseModel):
    """
    Representação de evento de férias na resposta.
    Inclui person_name, team_id, team_name e has_overlap (RF-20).
    """
    id: int
    person_id: int
    person_name: str = ""
    team_id: int = 0
    team_name: str = ""
    start_date: date
    end_date: date
    days: int
    notes: str | None = None
    has_overlap: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VacationListResponse(BaseModel):
    """
    Resposta para GET /api/v1/vacations.
    Inclui lista de férias + lista resumida de times para filtro na UI.
    Ref: api_spec.md §5.1
    """
    vacations: list[VacationResponse]
    teams: list[TeamSummary]
