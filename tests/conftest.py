"""
Configuração de testes — fixtures compartilhadas.

Sobrescreve a dependência get_db para usar SQLite in-memory,
cria TestClient e seed de dados para os testes de integração.
"""

from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import create_app
from app.models import Team, Person, Vacation


# ── Engine in-memory (isolada por sessão de teste) ──────────────────

@pytest.fixture()
def db_session():
    """
    Cria um engine SQLite in-memory com foreign keys habilitadas,
    gera as tabelas e fornece uma Session limpa para cada teste.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Habilita PRAGMA foreign_keys (igual ao database.py de produção)
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)

    TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session):
    """
    TestClient do FastAPI com dependência get_db sobrescrita
    para usar a sessão in-memory.
    """
    app = create_app()

    def _override_get_db():
        try:
            yield db_session
        finally:
            pass  # session gerenciada pela fixture db_session

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()


# ── Seed data ───────────────────────────────────────────────────────

@pytest.fixture()
def seed_data(db_session):
    """
    Popula o banco in-memory com dados de teste:
    - 2 times (Engenharia, Produto)
    - 3 pessoas (Alice e Bob em Engenharia, Carol em Produto)
    - 4 férias: 2 futuras, 2 passadas
    """
    today = date.today()

    # Times
    team_eng = Team(name="Engenharia", description="Time de engenharia")
    team_prod = Team(name="Produto", description="Time de produto")
    db_session.add_all([team_eng, team_prod])
    db_session.flush()

    # Pessoas
    alice = Person(name="Alice Silva", email="alice@example.com", team_id=team_eng.id)
    bob = Person(name="Bob Santos", email="bob@example.com", team_id=team_eng.id)
    carol = Person(name="Carol Lima", email="carol@example.com", team_id=team_prod.id)
    db_session.add_all([alice, bob, carol])
    db_session.flush()

    # Férias futuras
    vac_alice_future = Vacation(
        person_id=alice.id,
        start_date=today + timedelta(days=30),
        end_date=today + timedelta(days=44),
        days=15,
        notes="Férias de verão",
    )
    vac_bob_future = Vacation(
        person_id=bob.id,
        start_date=today + timedelta(days=60),
        end_date=today + timedelta(days=74),
        days=15,
        notes="Viagem internacional",
    )

    # Férias passadas
    vac_alice_past = Vacation(
        person_id=alice.id,
        start_date=today - timedelta(days=60),
        end_date=today - timedelta(days=46),
        days=15,
        notes="Férias passadas Alice",
    )
    vac_carol_past = Vacation(
        person_id=carol.id,
        start_date=today - timedelta(days=30),
        end_date=today - timedelta(days=16),
        days=15,
        notes="Férias passadas Carol",
    )

    db_session.add_all([vac_alice_future, vac_bob_future, vac_alice_past, vac_carol_past])
    db_session.commit()

    return {
        "teams": {"eng": team_eng, "prod": team_prod},
        "persons": {"alice": alice, "bob": bob, "carol": carol},
        "vacations": {
            "alice_future": vac_alice_future,
            "bob_future": vac_bob_future,
            "alice_past": vac_alice_past,
            "carol_past": vac_carol_past,
        },
    }


@pytest.fixture()
def seeded_client(client, seed_data):
    """TestClient já com dados de seed carregados."""
    return client, seed_data
