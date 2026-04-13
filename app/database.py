"""
Configuração do banco de dados via SQLAlchemy.

Suporta PostgreSQL (produção) e SQLite (desenvolvimento local).
A connection string é lida de DATABASE_URL (env var).
"""

import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Caminho default: SQLite local para desenvolvimento
_BASE_DIR = Path(__file__).resolve().parent.parent
_DEFAULT_URL = f"sqlite:///{_BASE_DIR / 'ferias.db'}"

DATABASE_URL = os.getenv("DATABASE_URL", _DEFAULT_URL)

# Detecta se é SQLite para ajustar configurações
_is_sqlite = DATABASE_URL.startswith("sqlite")

_engine_kwargs = {}
if _is_sqlite:
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, echo=False, **_engine_kwargs)


# Habilita PRAGMA foreign_keys para SQLite (desabilitado por padrão)
if _is_sqlite:
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Classe base declarativa para todos os models SQLAlchemy."""
    pass


def create_tables() -> None:
    """Cria todas as tabelas definidas nos models (idempotente)."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dependency FastAPI — fornece uma sessão de banco por request.
    Garante fechamento mesmo em caso de exceção.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
