"""Capa de servicios (lógica y reglas de negocio)."""
from app.services.categoria_service import (
    CategoriaService,
    CategoriaNotFoundError,
    CategoriaAlreadyExistsError,
    CategoriaValidationError,
)

__all__ = [
    "CategoriaService",
    "CategoriaNotFoundError",
    "CategoriaAlreadyExistsError",
    "CategoriaValidationError",
]
