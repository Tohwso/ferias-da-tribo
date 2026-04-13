"""Importa todos os schemas para acesso centralizado."""

from app.schemas.team import TeamCreate, TeamUpdate, TeamResponse, TeamSummary
from app.schemas.person import PersonCreate, PersonUpdate, PersonResponse
from app.schemas.vacation import (
    VacationCreate,
    VacationUpdate,
    VacationResponse,
    VacationListResponse,
)

__all__ = [
    "TeamCreate",
    "TeamUpdate",
    "TeamResponse",
    "TeamSummary",
    "PersonCreate",
    "PersonUpdate",
    "PersonResponse",
    "VacationCreate",
    "VacationUpdate",
    "VacationResponse",
    "VacationListResponse",
]
