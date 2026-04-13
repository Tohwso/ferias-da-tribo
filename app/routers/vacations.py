"""
Router: Vacations (Férias).

Endpoints REST para CRUD de eventos de férias com filtros e sobreposição.
Ref: api_spec.md §5 | RF-11..RF-20 | BR-002..BR-012
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.vacation import (
    VacationCreate,
    VacationListResponse,
    VacationResponse,
    VacationUpdate,
)
from app.services import vacation_service

router = APIRouter(prefix="/api/v1/vacations", tags=["férias"])


@router.get("", response_model=VacationListResponse)
def listar_ferias(
    team_id: int | None = Query(None, description="Filtra por time"),
    include_past: bool = Query(False, description="Inclui eventos passados"),
    db: Session = Depends(get_db),
):
    """
    Lista eventos de férias com filtros e detecção de sobreposição.
    RF-16..RF-20 | BR-004, BR-005, BR-006
    """
    return vacation_service.list_vacations(
        db, team_id=team_id, include_past=include_past
    )


@router.get("/{vacation_id}", response_model=VacationResponse)
def obter_ferias(vacation_id: int, db: Session = Depends(get_db)):
    """
    Obtém evento de férias por ID.
    Retorna 404 se não encontrado.
    """
    result = vacation_service.get_vacation_response(db, vacation_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento de férias não encontrado",
        )
    return result


@router.post("", response_model=VacationResponse, status_code=status.HTTP_201_CREATED)
def criar_ferias(data: VacationCreate, db: Session = Depends(get_db)):
    """
    Cria evento de férias com cálculo automático de dias.
    RF-11, RF-12, RF-15 | BR-002, BR-003, BR-007, BR-012
    """
    result, reason = vacation_service.create_vacation(db, data)
    if result is not None:
        return result

    if reason == "person_not_found":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pessoa informada não existe",
        )
    if reason == "overlap_same_person":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um evento de férias que se sobrepõe a este período para a mesma pessoa",
        )


@router.put("/{vacation_id}", response_model=VacationResponse)
def atualizar_ferias(
    vacation_id: int, data: VacationUpdate, db: Session = Depends(get_db)
):
    """
    Atualiza evento de férias.
    RF-13 | BR-002, BR-003, BR-012
    """
    result, reason = vacation_service.update_vacation(db, vacation_id, data)
    if result is not None:
        return result

    if reason == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento de férias não encontrado",
        )
    if reason == "person_not_found":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Pessoa informada não existe",
        )
    if reason == "overlap_same_person":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um evento de férias que se sobrepõe a este período para a mesma pessoa",
        )


@router.delete("/{vacation_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_ferias(vacation_id: int, db: Session = Depends(get_db)):
    """
    Exclui evento de férias.
    RF-14
    """
    deleted = vacation_service.delete_vacation(db, vacation_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Evento de férias não encontrado",
        )
    return None
