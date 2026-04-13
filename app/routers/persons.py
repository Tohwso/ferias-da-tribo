"""
Router: Persons (Pessoas).

Endpoints REST para CRUD de pessoas.
Ref: api_spec.md §4 | RF-05..RF-10 | BR-001, BR-009, BR-011
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.person import PersonCreate, PersonResponse, PersonUpdate
from app.services import person_service

router = APIRouter(prefix="/api/v1/people", tags=["pessoas"])


@router.get("", response_model=list[PersonResponse])
def listar_pessoas(
    team_id: int | None = Query(None, description="Filtra por time"),
    db: Session = Depends(get_db),
):
    """
    Lista pessoas, opcionalmente filtradas por time.
    RF-09
    """
    return person_service.list_persons(db, team_id=team_id)


@router.get("/{person_id}", response_model=PersonResponse)
def obter_pessoa(person_id: int, db: Session = Depends(get_db)):
    """
    Obtém pessoa por ID.
    Retorna 404 se não encontrada.
    """
    result = person_service.get_person_response(db, person_id)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada",
        )
    return result


@router.post("", response_model=PersonResponse, status_code=status.HTTP_201_CREATED)
def criar_pessoa(data: PersonCreate, db: Session = Depends(get_db)):
    """
    Cria nova pessoa.
    RF-05, RF-06, RF-10 | BR-001, BR-011
    """
    result, reason = person_service.create_person(db, data)
    if result is not None:
        return result

    if reason == "team_not_found":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Time informado não existe",
        )
    if reason == "email_duplicate":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma pessoa cadastrada com este email",
        )


@router.put("/{person_id}", response_model=PersonResponse)
def atualizar_pessoa(
    person_id: int, data: PersonUpdate, db: Session = Depends(get_db)
):
    """
    Atualiza pessoa existente.
    RF-07 | BR-001, BR-011
    """
    result, reason = person_service.update_person(db, person_id, data)
    if result is not None:
        return result

    if reason == "not_found":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada",
        )
    if reason == "team_not_found":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Time informado não existe",
        )
    if reason == "email_duplicate":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma pessoa cadastrada com este email",
        )


@router.delete("/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_pessoa(person_id: int, db: Session = Depends(get_db)):
    """
    Exclui pessoa e suas férias em cascata.
    RF-08, BR-009
    """
    deleted = person_service.delete_person(db, person_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pessoa não encontrada",
        )
    return None
