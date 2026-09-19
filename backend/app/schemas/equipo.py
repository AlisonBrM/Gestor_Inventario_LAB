from datetime import date
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class EquipoBase(BaseModel):
    """Esquema base para Equipo."""

    id_categoria: int = Field(
        ...,
        ge=1,
        description="ID de la categoría a la que pertenece el equipo",
        examples=[1],
    )
    nombre: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Nombre del equipo (máx 150 caracteres)",
        examples=["Osciloscopio Digital 100MHz"],
    )
    secuencial: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Secuencial interno único del laboratorio",
        examples=["EQ-001"],
    )
    descripcion: Optional[str] = Field(
        None,
        max_length=255,
        description="Descripción opcional del equipo",
        examples=["Osciloscopio de dos canales con puntas de prueba"],
    )

    @field_validator("nombre")
    @classmethod
    def validar_nombre_no_vacio(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("El nombre del equipo no puede estar vacío ni contener solo espacios.")
        return trimmed

    @field_validator("secuencial")
    @classmethod
    def validar_secuencial_no_vacio(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("El secuencial del equipo no puede estar vacío ni contener solo espacios.")
        return trimmed


class EquipoCreate(EquipoBase):
    """Esquema para la creación de un nuevo Equipo."""
    pass


class EquipoUpdate(BaseModel):
    """Esquema para actualización de un Equipo."""

    id_categoria: Optional[int] = Field(
        None,
        ge=1,
        description="Nuevo ID de categoría",
    )
    nombre: Optional[str] = Field(
        None,
        min_length=1,
        max_length=150,
        description="Nuevo nombre del equipo",
    )
    secuencial: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Nuevo secuencial del equipo",
    )
    descripcion: Optional[str] = Field(
        None,
        max_length=255,
        description="Nueva descripción del equipo",
    )
    mantenimiento: Optional[bool] = Field(
        None,
        description="Estado de mantenimiento del equipo",
    )
    activo: Optional[bool] = Field(
        None,
        description="Estado activo o inactivo del equipo",
    )

    @field_validator("nombre")
    @classmethod
    def validar_nombre_actualizado(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("El nombre del equipo no puede estar vacío ni contener solo espacios.")
            return trimmed
        return value

    @field_validator("secuencial")
    @classmethod
    def validar_secuencial_actualizado(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("El secuencial del equipo no puede estar vacío ni contener solo espacios.")
            return trimmed
        return value


class EquipoResponse(EquipoBase):
    """Esquema de respuesta para Equipo."""

    id: int
    mantenimiento: bool
    fecha_creacion: date
    activo: bool
    nombre_categoria: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
