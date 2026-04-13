"""
Entry point da aplicação Férias.

Cria a app FastAPI via factory, registra routers, configura
Jinja2, Static Files e cria tabelas no banco na inicialização.

Ref: infrastructure.md §2, §6
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.database import create_tables

# Importa models para garantir que estão registrados no metadata ANTES do create_tables
from app.models import Team, Person, Vacation  # noqa: F401

from app.routers import teams, persons, vacations
from app.routes import pages

_APP_DIR = Path(__file__).resolve().parent


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Cria tabelas do banco na inicialização (idempotente)."""
    create_tables()
    yield


def create_app() -> FastAPI:
    """Factory da aplicação — usado por testes e pelo módulo."""
    application = FastAPI(
        title="Férias",
        description="Sistema de gestão de férias por time",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS — permite acesso de qualquer origem (app local, sem autenticação)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Jinja2 templates
    templates = Jinja2Templates(directory=str(_APP_DIR / "templates"))
    application.state.templates = templates

    # Static files (CSS, JS)
    application.mount(
        "/static",
        StaticFiles(directory=str(_APP_DIR / "static")),
        name="static",
    )

    # Registra routers REST (prefixo /api/v1 definido em cada router)
    application.include_router(teams.router)
    application.include_router(persons.router)
    application.include_router(vacations.router)

    # Registra rotas de páginas HTML
    application.include_router(pages.router)

    @application.get("/health", tags=["infra"])
    def health_check():
        """Healthcheck simples para verificar se a app está de pé."""
        return {"status": "ok"}

    return application


app = create_app()
