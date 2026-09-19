"""Modelos de datos (ORM)."""
from app.models.categoria import Categoria
from app.models.devolucion import Devolucion
from app.models.equipo import Equipo
from app.models.persona import Persona
from app.models.prestamo import Prestamo

__all__ = ["Categoria", "Devolucion", "Equipo", "Persona", "Prestamo"]
