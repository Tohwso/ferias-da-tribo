"""
Router: Teams (Times).

Endpoints REST para CRUD de times.
Ref: api_spec.md §3 | RF-01..RF-04 | BR-008, BR-010
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.team import TeamCreate, TeamResponse, TeamUpdate
from app.services import team_service

router = APIRouter(prefix="/api/v1/teams", tags=["times"])


@router.get("", response_model=list[TeamResponse])
def listar_times(db: Session = Depends(get_db)):
    """
    Lista todos os times com contagem de pessoas.
    RF-04
    """
    return team_service.list_teams(db)


@router.get("/{team_id}", response_model=TeamResponse)
def obter_time(team_id: int, db: Session = Depends(get_db)):
    """
    Obtém time por ID.
    Retorna 404 se não encontrado.
    """
    result = team_service.get_team_response(db, team_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado",
        )
    return result


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def criar_time(data: TeamCreate, db: Session = Depends(get_db)):
    """
    Cria novo time.
    RF-01 | BR-008
    """
    return team_service.create_team(db, data)


@router.put("/{team_id}", response_model=TeamResponse)
def atualizar_time(team_id: int, data: TeamUpdate, db: Session = Depends(get_db)):
    """
    Atualiza time existente.
    RF-02 | Retorna 404 se não encontrado.
    """
    result = team_service.update_team(db, team_id, data)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado",
        )
    return result


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_time(team_id: int, db: Session = Depends(get_db)):
    """
    Exclui time por ID.
    RF-03 | BR-010: Retorna 409 se houver pessoas vinculadas.
    """
    success, reason = team_service.delete_team(db, team_id)
    if success:
        return None

    if reason == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Time não encontrado",
        )
    if reason == "has_persons":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir o time: existem pessoas vinculadas. "
                   "Remova ou mova as pessoas antes.",
        )
