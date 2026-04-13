"""
Service: Team (Time).

CRUD de times com validação BR-010 (não exclui time com pessoas).
Ref: api_spec.md §3 | domain_model.md §3.1
"""

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.person import Person
from app.models.team import Team
from app.schemas.team import TeamCreate, TeamResponse, TeamUpdate


def list_teams(db: Session) -> list[TeamResponse]:
    """
    Lista todos os times com contagem de pessoas (person_count).
    RF-04: Ordenação pelo nome.
    """
    results = (
        db.query(Team, func.count(Person.id).label("person_count"))
        .outerjoin(Person, Person.team_id == Team.id)
        .group_by(Team.id)
        .order_by(Team.name)
        .all()
    )

    return [
        TeamResponse(
            id=team.id,
            name=team.name,
            description=team.description,
            person_count=count,
            created_at=team.created_at,
            updated_at=team.updated_at,
        )
        for team, count in results
    ]


def get_team(db: Session, team_id: int) -> Team | None:
    """Busca time por ID. Retorna None se não encontrado."""
    return db.query(Team).filter(Team.id == team_id).first()


def get_team_response(db: Session, team_id: int) -> TeamResponse | None:
    """Busca time por ID e retorna como TeamResponse com person_count."""
    result = (
        db.query(Team, func.count(Person.id).label("person_count"))
        .outerjoin(Person, Person.team_id == Team.id)
        .filter(Team.id == team_id)
        .group_by(Team.id)
        .first()
    )
    if result is None:
        return None

    team, count = result
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        person_count=count,
        created_at=team.created_at,
        updated_at=team.updated_at,
    )


def create_team(db: Session, data: TeamCreate) -> TeamResponse:
    """Cria um novo time. RF-01, BR-008."""
    team = Team(name=data.name, description=data.description)
    db.add(team)
    db.commit()
    db.refresh(team)
    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        person_count=0,
        created_at=team.created_at,
        updated_at=team.updated_at,
    )


def update_team(db: Session, team_id: int, data: TeamUpdate) -> TeamResponse | None:
    """Atualiza time existente. RF-02. Retorna None se não encontrado."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        return None

    team.name = data.name
    team.description = data.description
    db.commit()
    db.refresh(team)

    # Conta pessoas vinculadas
    count = db.query(func.count(Person.id)).filter(Person.team_id == team_id).scalar()

    return TeamResponse(
        id=team.id,
        name=team.name,
        description=team.description,
        person_count=count or 0,
        created_at=team.created_at,
        updated_at=team.updated_at,
    )


def delete_team(db: Session, team_id: int) -> tuple[bool, str]:
    """
    Exclui time por ID.
    RF-03, BR-010: Não permite exclusão se houver pessoas vinculadas.

    Retorna:
        (True, "")        — excluído com sucesso
        (False, "not_found") — time não encontrado
        (False, "has_persons") — time possui pessoas vinculadas
    """
    team = db.query(Team).filter(Team.id == team_id).first()
    if team is None:
        return False, "not_found"

    person_count = (
        db.query(func.count(Person.id))
        .filter(Person.team_id == team_id)
        .scalar()
    )
    if person_count and person_count > 0:
        return False, "has_persons"

    db.delete(team)
    db.commit()
    return True, ""
