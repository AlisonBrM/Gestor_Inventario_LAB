from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoriaBase(BaseModel):
    """Esquema base para Categoría."""

    nombre: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre de la categoría (máx 100 caracteres)",
        examples=["Equipos de Cómputo"],
    )
    descripcion: Optional[str] = Field(
        None,
        max_length=255,
        description="Descripción opcional de la categoría",
        examples=["Portátiles, tabletas y accesorios de computación"],
    )
    plazo_entrega: int = Field(
        ...,
        ge=1,
        le=180,
        description="Plazo de entrega en días calendario (entre 1 y 180 días)",
        examples=[15],
    )

    @field_validator("nombre")
    @classmethod
    def validar_nombre_no_vacio(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("El nombre de la categoría no puede estar vacío ni contener solo espacios.")
        return trimmed


class CategoriaCreate(CategoriaBase):
    """Esquema para la creación de una Categoría."""
    pass


class CategoriaUpdate(BaseModel):
    """Esquema para actualización parcial o total de una Categoría."""

    nombre: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Nuevo nombre para la categoría",
    )
    descripcion: Optional[str] = Field(
        None,
        max_length=255,
        description="Nueva descripción de la categoría",
    )
    plazo_entrega: Optional[int] = Field(
        None,
        ge=1,
        le=180,
        description="Nuevo plazo de entrega en días (entre 1 y 180)",
    )
    activo: Optional[bool] = Field(
        None,
        description="Estado activo o inactivo de la categoría",
    )

    @field_validator("nombre")
    @classmethod
    def validar_nombre_actualizado(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("El nombre de la categoría no puede estar vacío ni contener solo espacios.")
            return trimmed
        return value


class CategoriaResponse(CategoriaBase):
    """Esquema de respuesta para Categoría."""

    id: int
    activo: bool

    model_config = ConfigDict(from_attributes=True)
