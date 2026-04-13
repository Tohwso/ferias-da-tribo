"""
Testes de integração: Vacations (Férias).

CRUD completo + BR-011 (datas inválidas) + BR-012 (sobreposição).
Filtros por time e include_past.
Endpoint prefix: /api/v1/vacations
"""

from datetime import date, timedelta

import pytest


# ── CRUD ────────────────────────────────────────────────────────────

def test_create_vacation(seeded_client):
    """POST /api/v1/vacations → 201 + retorna VacationResponse com days calculados."""
    client, seed = seeded_client
    person_id = seed["persons"]["carol"].id

    start = date.today() + timedelta(days=90)
    end = start + timedelta(days=9)  # 10 dias

    resp = client.post(
        "/api/v1/vacations",
        json={
            "person_id": person_id,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "notes": "Férias de Carol",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["person_id"] == person_id
    assert body["person_name"] == "Carol Lima"
    assert body["team_name"] == "Produto"
    assert body["start_date"] == start.isoformat()
    assert body["end_date"] == end.isoformat()
    assert body["days"] == 10  # end - start + 1
    assert body["notes"] == "Férias de Carol"
    assert "id" in body
    assert "created_at" in body


def test_list_vacations(seeded_client):
    """
    GET /api/v1/vacations → 200 + wrapper {vacations: [...], teams: [...]}.
    Por padrão, sem include_past, retorna apenas férias futuras.
    """
    client, seed = seeded_client
    resp = client.get("/api/v1/vacations")
    assert resp.status_code == 200
    body = resp.json()

    assert "vacations" in body
    assert "teams" in body

    # Sem include_past: apenas as 2 férias futuras
    assert len(body["vacations"]) == 2

    # Teams no filtro: 2 times
    assert len(body["teams"]) == 2


def test_get_vacation(seeded_client):
    """GET /api/v1/vacations/{id} → 200 + VacationResponse."""
    client, seed = seeded_client
    vac_id = seed["vacations"]["alice_future"].id
    resp = client.get(f"/api/v1/vacations/{vac_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == vac_id
    assert body["person_name"] == "Alice Silva"
    assert body["team_name"] == "Engenharia"
    assert body["days"] == 15


def test_get_vacation_not_found(client):
    """GET /api/v1/vacations/999 → 404."""
    resp = client.get("/api/v1/vacations/999")
    assert resp.status_code == 404


def test_update_vacation(seeded_client):
    """PUT /api/v1/vacations/{id} → 200 + dados atualizados + days recalculados."""
    client, seed = seeded_client
    vac_id = seed["vacations"]["bob_future"].id
    person_id = seed["persons"]["bob"].id

    new_start = date.today() + timedelta(days=100)
    new_end = new_start + timedelta(days=4)  # 5 dias

    resp = client.put(
        f"/api/v1/vacations/{vac_id}",
        json={
            "person_id": person_id,
            "start_date": new_start.isoformat(),
            "end_date": new_end.isoformat(),
            "notes": "Atualizado",
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["start_date"] == new_start.isoformat()
    assert body["end_date"] == new_end.isoformat()
    assert body["days"] == 5
    assert body["notes"] == "Atualizado"


def test_delete_vacation(seeded_client):
    """DELETE /api/v1/vacations/{id} → 204."""
    client, seed = seeded_client
    vac_id = seed["vacations"]["bob_future"].id

    resp = client.delete(f"/api/v1/vacations/{vac_id}")
    assert resp.status_code == 204

    # Confirma excluído
    get_resp = client.get(f"/api/v1/vacations/{vac_id}")
    assert get_resp.status_code == 404


# ── Regras de negócio ───────────────────────────────────────────────


def test_create_vacation_invalid_dates_returns_422(seeded_client):
    """
    BR-011: POST com start_date > end_date → 422 (validação do Pydantic).
    """
    client, seed = seeded_client
    person_id = seed["persons"]["carol"].id

    resp = client.post(
        "/api/v1/vacations",
        json={
            "person_id": person_id,
            "start_date": "2025-12-31",
            "end_date": "2025-12-01",
        },
    )
    assert resp.status_code == 422


def test_create_vacation_overlap_same_person_returns_409(seeded_client):
    """
    BR-012: POST com período sobrepondo férias existente da mesma pessoa → 409.
    """
    client, seed = seeded_client
    person_id = seed["persons"]["alice"].id
    existing = seed["vacations"]["alice_future"]

    # Cria férias que sobrepõem as férias futuras da Alice
    overlap_start = existing.start_date + timedelta(days=5)
    overlap_end = existing.end_date + timedelta(days=10)

    resp = client.post(
        "/api/v1/vacations",
        json={
            "person_id": person_id,
            "start_date": overlap_start.isoformat(),
            "end_date": overlap_end.isoformat(),
        },
    )
    assert resp.status_code == 409
    assert "sobrepõe" in resp.json()["detail"].lower()


# ── Filtros ─────────────────────────────────────────────────────────


def test_filter_vacations_by_team(seeded_client):
    """GET /api/v1/vacations?team_id=X → filtra férias por time."""
    client, seed = seeded_client
    team_eng_id = seed["teams"]["eng"].id

    resp = client.get(f"/api/v1/vacations?team_id={team_eng_id}&include_past=true")
    assert resp.status_code == 200
    body = resp.json()
    vacations = body["vacations"]

    # Engenharia: Alice(2) + Bob(1) = 3 férias
    assert len(vacations) == 3
    assert all(v["team_id"] == team_eng_id for v in vacations)


def test_filter_include_past(seeded_client):
    """GET /api/v1/vacations?include_past=true → inclui férias passadas."""
    client, seed = seeded_client

    # Sem include_past: apenas futuras (2)
    resp_no_past = client.get("/api/v1/vacations")
    assert len(resp_no_past.json()["vacations"]) == 2

    # Com include_past: todas (4)
    resp_with_past = client.get("/api/v1/vacations?include_past=true")
    assert resp_with_past.status_code == 200
    assert len(resp_with_past.json()["vacations"]) == 4
