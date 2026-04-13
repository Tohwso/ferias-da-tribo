"""
Service: Vacation (Evento de Férias).

CRUD de férias com:
- Cálculo automático de 'days' (end_date - start_date + 1)
- Validação BR-011 (start_date <= end_date) — feita no schema Pydantic
- Validação BR-012 (sem sobreposição para a mesma pessoa)
- Detecção de sobreposição entre pessoas do mesmo time (RF-20)

Ref: api_spec.md §5 | domain_model.md §3.3, §5
"""

from datetime import date

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.person import Person
from app.models.team import Team
from app.models.vacation import Vacation
from app.schemas.team import TeamSummary
from app.schemas.vacation import (
    VacationCreate,
    VacationListResponse,
    VacationResponse,
    VacationUpdate,
)


def _calc_days(start_date: date, end_date: date) -> int:
    """Calcula dias de férias (inclusivo nas duas pontas)."""
    return (end_date - start_date).days + 1


def _check_overlap_same_person(
    db: Session, person_id: int, start_date: date, end_date: date,
    exclude_vacation_id: int | None = None,
) -> bool:
    """
    BR-012: Verifica se existe sobreposição de férias para a MESMA pessoa.
    Retorna True se há sobreposição (conflito).
    """
    query = db.query(Vacation).filter(
        Vacation.person_id == person_id,
        Vacation.start_date <= end_date,
        Vacation.end_date >= start_date,
    )
    if exclude_vacation_id is not None:
        query = query.filter(Vacation.id != exclude_vacation_id)
    return query.first() is not None


def _detect_team_overlaps(vacations: list[dict]) -> set[int]:
    """
    RF-20: Detecta sobreposição entre pessoas do MESMO time.
    Dois eventos se sobrepõem quando:
      evento_a.start_date <= evento_b.end_date
      AND evento_a.end_date >= evento_b.start_date
      AND mesmo team_id
      AND person_id diferente

    Retorna set de vacation_ids que possuem sobreposição.
    """
    overlap_ids: set[int] = set()

    # Agrupa por team_id para comparar apenas dentro do mesmo time
    by_team: dict[int, list[dict]] = {}
    for v in vacations:
        by_team.setdefault(v["team_id"], []).append(v)

    for _team_id, team_vacations in by_team.items():
        n = len(team_vacations)
        for i in range(n):
            for j in range(i + 1, n):
                a = team_vacations[i]
                b = team_vacations[j]
                # Só compara pessoas diferentes
                if a["person_id"] == b["person_id"]:
                    continue
                # Teste de sobreposição de intervalos
                if a["start_date"] <= b["end_date"] and a["end_date"] >= b["start_date"]:
                    overlap_ids.add(a["id"])
                    overlap_ids.add(b["id"])

    return overlap_ids


def _to_response(vac: Vacation, has_overlap: bool = False) -> VacationResponse:
    """Converte model Vacation para VacationResponse com dados desnormalizados."""
    person = vac.person
    return VacationResponse(
        id=vac.id,
        person_id=vac.person_id,
        person_name=person.name if person else "",
        team_id=person.team_id if person else 0,
        team_name=person.team.name if person and person.team else "",
        start_date=vac.start_date,
        end_date=vac.end_date,
        days=vac.days,
        notes=vac.notes,
        has_overlap=has_overlap,
        created_at=vac.created_at,
        updated_at=vac.updated_at,
    )


def list_vacations(
    db: Session,
    team_id: int | None = None,
    include_past: bool = False,
) -> VacationListResponse:
    """
    Lista eventos de férias com filtros e detecção de sobreposição.
    RF-16..RF-20 | BR-004, BR-005, BR-006

    - team_id: filtra por time
    - include_past: se False (padrão), exclui eventos com end_date < hoje
    - Ordenação: start_date ASC (BR-004)
    - has_overlap calculado por time (RF-20)
    """
    query = (
        db.query(Vacation)
        .join(Person, Vacation.person_id == Person.id)
        .join(Team, Person.team_id == Team.id)
    )

    if team_id is not None:
        query = query.filter(Person.team_id == team_id)

    if not include_past:
        today = date.today()
        query = query.filter(Vacation.end_date >= today)

    query = query.order_by(Vacation.start_date.asc())
    vacations = query.all()

    # Monta lista de dicts para detecção de overlap
    vac_dicts = [
        {
            "id": v.id,
            "person_id": v.person_id,
            "team_id": v.person.team_id,
            "start_date": v.start_date,
            "end_date": v.end_date,
        }
        for v in vacations
    ]
    overlap_ids = _detect_team_overlaps(vac_dicts)

    # Monta responses
    vac_responses = [
        _to_response(v, has_overlap=(v.id in overlap_ids))
        for v in vacations
    ]

    # Lista resumida de times para o filtro na UI
    all_teams = db.query(Team).order_by(Team.name).all()
    team_summaries = [TeamSummary(id=t.id, name=t.name) for t in all_teams]

    return VacationListResponse(vacations=vac_responses, teams=team_summaries)


def get_vacation(db: Session, vacation_id: int) -> Vacation | None:
    """Busca evento de férias por ID. Retorna None se não encontrado."""
    return (
        db.query(Vacation)
        .join(Person)
        .join(Team)
        .filter(Vacation.id == vacation_id)
        .first()
    )


def get_vacation_response(db: Session, vacation_id: int) -> VacationResponse | None:
    """Busca evento de férias por ID e retorna como VacationResponse."""
    vac = get_vacation(db, vacation_id)
    if vac is None:
        return None
    return _to_response(vac)


def create_vacation(
    db: Session, data: VacationCreate
) -> tuple[VacationResponse | None, str]:
    """
    Cria evento de férias.
    RF-11, RF-12, RF-15 | BR-002, BR-003, BR-007, BR-012

    Retorna:
        (VacationResponse, "")           — sucesso
        (None, "person_not_found")       — person_id inválido
        (None, "overlap_same_person")    — BR-012: sobreposição na mesma pessoa
    """
    # Valida existência da pessoa
    person = db.query(Person).filter(Person.id == data.person_id).first()
    if person is None:
        return None, "person_not_found"

    # BR-012: verifica sobreposição na mesma pessoa
    if _check_overlap_same_person(db, data.person_id, data.start_date, data.end_date):
        return None, "overlap_same_person"

    # Calcula dias automaticamente
    days = _calc_days(data.start_date, data.end_date)

    vac = Vacation(
        person_id=data.person_id,
        start_date=data.start_date,
        end_date=data.end_date,
        days=days,
        notes=data.notes,
    )
    db.add(vac)
    db.commit()
    db.refresh(vac)

    return _to_response(vac), ""


def update_vacation(
    db: Session, vacation_id: int, data: VacationUpdate
) -> tuple[VacationResponse | None, str]:
    """
    Atualiza evento de férias.
    RF-13 | BR-002, BR-003, BR-012

    Retorna:
        (VacationResponse, "")           — sucesso
        (None, "not_found")              — evento não encontrado
        (None, "person_not_found")       — person_id inválido
        (None, "overlap_same_person")    — BR-012: sobreposição na mesma pessoa
    """
    vac = db.query(Vacation).filter(Vacation.id == vacation_id).first()
    if vac is None:
        return None, "not_found"

    # Valida existência da pessoa
    person = db.query(Person).filter(Person.id == data.person_id).first()
    if person is None:
        return None, "person_not_found"

    # BR-012: verifica sobreposição (exclui o próprio registro da busca)
    if _check_overlap_same_person(
        db, data.person_id, data.start_date, data.end_date,
        exclude_vacation_id=vacation_id,
    ):
        return None, "overlap_same_person"

    vac.person_id = data.person_id
    vac.start_date = data.start_date
    vac.end_date = data.end_date
    vac.days = _calc_days(data.start_date, data.end_date)
    vac.notes = data.notes

    db.commit()
    db.refresh(vac)

    return _to_response(vac), ""


def delete_vacation(db: Session, vacation_id: int) -> bool:
    """
    Exclui evento de férias. RF-14.
    Retorna True se excluído, False se não encontrado.
    """
    vac = db.query(Vacation).filter(Vacation.id == vacation_id).first()
    if vac is None:
        return False

    db.delete(vac)
    db.commit()
    return True
