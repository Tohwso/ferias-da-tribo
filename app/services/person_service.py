"""
Service: Person (Pessoa).

CRUD de pessoas com cascata BR-009 e validação de e-mail único BR-011.
Ref: api_spec.md §4 | domain_model.md §3.2
"""

from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.person import Person
from app.models.team import Team
from app.models.vacation import Vacation
from app.schemas.person import PersonCreate, PersonResponse, PersonUpdate


def _to_response(person: Person, db: Session) -> PersonResponse:
    """Converte model Person para PersonResponse com campos desnormalizados."""
    team_name = ""
    if person.team:
        team_name = person.team.name
    vacation_count = (
        db.query(func.count(Vacation.id))
        .filter(Vacation.person_id == person.id)
        .scalar()
        or 0
    )
    return PersonResponse(
        id=person.id,
        name=person.name,
        email=person.email,
        team_id=person.team_id,
        team_name=team_name,
        vacation_count=vacation_count,
        created_at=person.created_at,
        updated_at=person.updated_at,
    )


def list_persons(db: Session, team_id: int | None = None) -> list[PersonResponse]:
    """
    Lista pessoas, opcionalmente filtradas por time.
    RF-09: Inclui team_name e vacation_count.
    """
    query = db.query(Person).join(Team, Person.team_id == Team.id)
    if team_id is not None:
        query = query.filter(Person.team_id == team_id)
    query = query.order_by(Person.name)

    persons = query.all()
    return [_to_response(p, db) for p in persons]


def get_person(db: Session, person_id: int) -> Person | None:
    """Busca pessoa por ID. Retorna None se não encontrada."""
    return db.query(Person).filter(Person.id == person_id).first()


def get_person_response(db: Session, person_id: int) -> PersonResponse | None:
    """Busca pessoa por ID e retorna como PersonResponse."""
    person = db.query(Person).join(Team).filter(Person.id == person_id).first()
    if person is None:
        return None
    return _to_response(person, db)


def create_person(db: Session, data: PersonCreate) -> tuple[PersonResponse | None, str]:
    """
    Cria nova pessoa.
    RF-05, RF-06, RF-10 | BR-001, BR-011

    Retorna:
        (PersonResponse, "")          — sucesso
        (None, "team_not_found")      — team_id inválido
        (None, "email_duplicate")     — e-mail já existe
    """
    # Valida existência do time
    team = db.query(Team).filter(Team.id == data.team_id).first()
    if team is None:
        return None, "team_not_found"

    person = Person(name=data.name, email=data.email, team_id=data.team_id)
    db.add(person)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None, "email_duplicate"

    db.refresh(person)
    return _to_response(person, db), ""


def update_person(
    db: Session, person_id: int, data: PersonUpdate
) -> tuple[PersonResponse | None, str]:
    """
    Atualiza pessoa existente.
    RF-07 | BR-001, BR-011

    Retorna:
        (PersonResponse, "")          — sucesso
        (None, "not_found")           — pessoa não encontrada
        (None, "team_not_found")      — team_id inválido
        (None, "email_duplicate")     — e-mail já existe em outra pessoa
    """
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        return None, "not_found"

    # Valida existência do time
    team = db.query(Team).filter(Team.id == data.team_id).first()
    if team is None:
        return None, "team_not_found"

    person.name = data.name
    person.email = data.email
    person.team_id = data.team_id

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        return None, "email_duplicate"

    db.refresh(person)
    return _to_response(person, db), ""


def delete_person(db: Session, person_id: int) -> bool:
    """
    Exclui pessoa e suas férias em cascata.
    RF-08, BR-009: CASCADE configurado no model.

    Retorna True se excluída, False se não encontrada.
    """
    person = db.query(Person).filter(Person.id == person_id).first()
    if person is None:
        return False

    db.delete(person)
    db.commit()
    return True
