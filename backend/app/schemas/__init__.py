"""Esquemas y DTOs (Pydantic)."""
from app.schemas.categoria import (
    CategoriaBase,
    CategoriaCreate,
    CategoriaUpdate,
    CategoriaResponse,
)
from app.schemas.equipo import (
    EquipoBase,
    EquipoCreate,
    EquipoUpdate,
    EquipoResponse,
)
from app.schemas.persona import (
    PersonaBase,
    PersonaCreate,
    PersonaUpdate,
    PersonaResponse,
    TipoPersona,
)

__all__ = [
    "CategoriaBase",
    "CategoriaCreate",
    "CategoriaUpdate",
    "CategoriaResponse",
    "EquipoBase",
    "EquipoCreate",
    "EquipoUpdate",
    "EquipoResponse",
    "PersonaBase",
    "PersonaCreate",
    "PersonaUpdate",
    "PersonaResponse",
    "TipoPersona",
]
