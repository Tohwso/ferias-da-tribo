"""Rotas de páginas HTML — renderização Jinja2."""

from fastapi import APIRouter, Request

router = APIRouter(tags=["pages"])


@router.get("/")
def page_index(request: Request):
    """Tela inicial — SPA-like com tabs para agenda, times, pessoas e férias."""
    return request.app.state.templates.TemplateResponse(
        request=request,
        name="index.html",
    )
