"""
Testes de integração: Teams (Times).

CRUD completo + BR-010 (não excluir time com pessoas).
Endpoint prefix: /api/v1/teams
"""

import pytest


# ── CRUD ────────────────────────────────────────────────────────────


def test_create_team(client):
    """POST /api/v1/teams → 201 + retorna TeamResponse."""
    resp = client.post(
        "/api/v1/teams",
        json={"name": "Backend", "description": "Time de backend"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "Backend"
    assert body["description"] == "Time de backend"
    assert body["person_count"] == 0
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_list_teams(seeded_client):
    """GET /api/v1/teams → 200 + lista de times com person_count."""
    client, seed = seeded_client
    resp = client.get("/api/v1/teams")
    assert resp.status_code == 200
    body = resp.json()
    assert isinstance(body, list)
    assert len(body) == 2

    # Ordenados por nome: Engenharia, Produto
    names = [t["name"] for t in body]
    assert names == ["Engenharia", "Produto"]

    # person_count: Engenharia=2, Produto=1
    eng = next(t for t in body if t["name"] == "Engenharia")
    prod = next(t for t in body if t["name"] == "Produto")
    assert eng["person_count"] == 2
    assert prod["person_count"] == 1


def test_get_team(seeded_client):
    """GET /api/v1/teams/{id} → 200 + TeamResponse."""
    client, seed = seeded_client
    team_id = seed["teams"]["eng"].id
    resp = client.get(f"/api/v1/teams/{team_id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == team_id
    assert body["name"] == "Engenharia"
    assert body["person_count"] == 2


def test_get_team_not_found(client):
    """GET /api/v1/teams/999 → 404."""
    resp = client.get("/api/v1/teams/999")
    assert resp.status_code == 404


def test_update_team(seeded_client):
    """PUT /api/v1/teams/{id} → 200 + dados atualizados."""
    client, seed = seeded_client
    team_id = seed["teams"]["eng"].id
    resp = client.put(
        f"/api/v1/teams/{team_id}",
        json={"name": "Engenharia v2", "description": "Atualizado"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["name"] == "Engenharia v2"
    assert body["description"] == "Atualizado"
    assert body["id"] == team_id


def test_delete_team(client):
    """DELETE /api/v1/teams/{id} → 204 quando time não tem pessoas."""
    # Cria um time sem pessoas
    create_resp = client.post(
        "/api/v1/teams",
        json={"name": "Temporário"},
    )
    team_id = create_resp.json()["id"]

    resp = client.delete(f"/api/v1/teams/{team_id}")
    assert resp.status_code == 204

    # Confirma que foi excluído
    get_resp = client.get(f"/api/v1/teams/{team_id}")
    assert get_resp.status_code == 404


# ── Regras de negócio ───────────────────────────────────────────────


def test_delete_team_with_persons_returns_409(seeded_client):
    """
    BR-010: DELETE /api/v1/teams/{id} → 409 quando time tem pessoas vinculadas.
    """
    client, seed = seeded_client
    team_id = seed["teams"]["eng"].id  # Engenharia tem Alice e Bob
    resp = client.delete(f"/api/v1/teams/{team_id}")
    assert resp.status_code == 409
    assert "pessoas vinculadas" in resp.json()["detail"].lower()
