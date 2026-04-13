"""
Testes de integração: Persons (Pessoas).

CRUD completo + BR-009 (cascade delete) + BR-011 (email único).
Endpoint prefix: /api/v1/people
"""

import pytest


# ── CRUD ────────────────────────────────────────────────────────────


def test_create_person(seeded_client):
    """POST /api/v1/people → 201 + retorna PersonResponse."""
    client, seed = seeded_client
    team_id = seed["teams"]["prod"].id
    resp = client.post(
        "/api/v1/people",
        json={"name": "Daniel Souza", "email": "daniel@example.com", "team_id": team_id},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Daniel Souza"
    assert body["email"] == "daniel@example.com"
    assert body["team_id"] == team_id
    assert body["team_name"] == "Produto"
    assert body["vacation_count"] == 0
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_list_persons(seeded_client):
    """GET /api/v1/people → 200 + lista de pessoas ordenada por nome."""
    client, seed = seeded_client
    resp = client.get("/api/v1/people")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 3

    # Ordenação por nome: Alice, Bob, Carol
    names = [p["name"] for p in body]
    assert names == ["Alice Silva", "Bob Santos", "Carol Lima"]


def test_list_persons_filter_by_team(seeded_client):
    """GET /api/v1/people?team_id=X → filtra por time."""
    client, seed = seeded_client
    team_id = seed["teams"]["eng"].id
    resp = client.get(f"/api/v1/people?team_id={team_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 2
    assert all(p["team_id"] == team_id for p in body)


def test_get_person(seeded_client):
    """GET /api/v1/people/{id} → 200 + PersonResponse."""
    client, seed = seeded_client
    person_id = seed["persons"]["alice"].id
    resp = client.get(f"/api/v1/people/{person_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == person_id
    assert body["name"] == "Alice Silva"
    assert body["email"] == "alice@example.com"
    assert body["team_name"] == "Engenharia"
    # Alice tem 2 férias (1 futura + 1 passada)
    assert body["vacation_count"] == 2


def test_get_person_not_found(client):
    """GET /api/v1/people/999 → 404."""
    resp = client.get("/api/v1/people/999")
    assert resp.status_code == 404


def test_update_person(seeded_client):
    """PUT /api/v1/people/{id} → 200 + dados atualizados."""
    client, seed = seeded_client
    person_id = seed["persons"]["bob"].id
    team_id = seed["teams"]["prod"].id

    resp = client.put(
        f"/api/v1/people/{person_id}",
        json={"name": "Bob Oliveira", "email": "bob.new@example.com", "team_id": team_id},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Bob Oliveira"
    assert body["email"] == "bob.new@example.com"
    assert body["team_id"] == team_id
    assert body["team_name"] == "Produto"


# ── Regras de negócio ───────────────────────────────────────────────


def test_delete_person_cascades_vacations(seeded_client):
    """
    BR-009: DELETE /api/v1/people/{id} → 204 + férias da pessoa são deletadas em cascata.
    """
    client, seed = seeded_client
    person_id = seed["persons"]["alice"].id

    # Captura o ID da férias ANTES do delete (o objeto ORM fica detached após cascade)
    vac_alice_future_id = seed["vacations"]["alice_future"].id

    # Alice tem férias; deletar a pessoa deve funcionar (cascade)
    resp = client.delete(f"/api/v1/people/{person_id}")
    assert resp.status_code == 204

    # Confirma pessoa excluída
    get_resp = client.get(f"/api/v1/people/{person_id}")
    assert get_resp.status_code == 404

    # Confirma que férias da Alice foram excluídas em cascata
    vac_resp = client.get(f"/api/v1/vacations/{vac_alice_future_id}")
    assert vac_resp.status_code == 404


def test_create_person_duplicate_email_returns_409(seeded_client):
    """
    BR-011: POST /api/v1/people com email duplicado → 409.
    """
    client, seed = seeded_client
    team_id = seed["teams"]["eng"].id
    resp = client.post(
        "/api/v1/people",
        json={"name": "Alice Clone", "email": "alice@example.com", "team_id": team_id},
    )
    assert resp.status_code == 409
    assert "email" in resp.json()["detail"].lower()
