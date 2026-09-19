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

__all__ = [
    "CategoriaBase",
    "CategoriaCreate",
    "CategoriaUpdate",
    "CategoriaResponse",
    "EquipoBase",
    "EquipoCreate",
    "EquipoUpdate",
    "EquipoResponse",
]
