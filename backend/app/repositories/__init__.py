"""Capa de repositorios (acceso a datos)."""
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.equipo_repository import EquipoRepository
from app.repositories.persona_repository import PersonaRepository
from app.repositories.prestamo_repository import PrestamoRepository

__all__ = [
    "CategoriaRepository",
    "EquipoRepository",
    "PersonaRepository",
    "PrestamoRepository",
]
