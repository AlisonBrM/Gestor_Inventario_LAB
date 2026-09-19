from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class DevolucionCreate(BaseModel):
    """Esquema para registrar la devolución de un equipo prestado."""

    fecha_devolucion: Optional[date] = Field(
        None,
        description="Fecha en que se devuelve el equipo (por defecto hoy).",
        examples=["2026-09-19"],
    )
    novedades: Optional[str] = Field(
        None,
        max_length=255,
        description="Novedades u observaciones del equipo al momento de la devolución. Obligatorio si el equipo se envía a mantenimiento.",
        examples=["Equipo devuelto con raspones leves en carcasa."],
    )
    enviar_a_mantenimiento: bool = Field(
        False,
        description="Determina si el equipo debe pasar a marcarse como 'en mantenimiento'.",
    )


class DevolucionResponse(BaseModel):
    """Esquema de respuesta para los datos de una devolución."""

    id_prestamo: int
    fecha_devolucion: date
    novedades: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
