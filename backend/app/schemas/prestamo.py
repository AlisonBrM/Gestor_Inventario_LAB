from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PrestamoCreate(BaseModel):
    """Esquema para la creación de un nuevo Préstamo."""

    cedula_persona: str = Field(
        ...,
        min_length=1,
        max_length=20,
        description="Cédula de la persona solicitante",
        examples=["1001234567"],
    )
    id_equipo: int = Field(
        ...,
        ge=1,
        description="ID del equipo del laboratorio a prestar",
        examples=[1],
    )
    fecha_prestamo: Optional[date] = Field(
        None,
        description="Fecha de inicio del préstamo (por defecto la fecha actual)",
        examples=["2026-09-19"],
    )

    @field_validator("cedula_persona")
    @classmethod
    def validar_cedula_no_vacia(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("La cédula de la persona no puede estar vacía.")
        return trimmed


class PrestamoResponse(BaseModel):
    """Esquema de respuesta detallada para un Préstamo."""

    id: int
    cedula_persona: str
    nombre_persona: Optional[str] = None
    id_equipo: int
    nombre_equipo: Optional[str] = None
    secuencial_equipo: Optional[str] = None
    id_categoria: Optional[int] = None
    nombre_categoria: Optional[str] = None
    fecha_prestamo: date
    fecha_devolucion_esperada: date
    devuelto: bool = False
    estado: str = "vigente"

    model_config = ConfigDict(from_attributes=True)
