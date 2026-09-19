import re
from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class TipoPersona(str, Enum):
    """Tipos de persona permitidos según MODELS.md."""

    profesor = "profesor"
    estudiante = "estudiante"


EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
DIGITS_REGEX = re.compile(r"^\d+$")


class PersonaBase(BaseModel):
    """Esquema base para Persona."""

    cedula: str = Field(
        ...,
        min_length=6,
        max_length=15,
        description="Cédula de identificación (6 a 15 dígitos numéricos)",
        examples=["1001234567"],
    )
    nombre_completo: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Nombre completo de la persona (máx 100 caracteres)",
        examples=["Ana María Gómez"],
    )
    correo: Optional[str] = Field(
        None,
        max_length=150,
        description="Correo electrónico de contacto (opcional)",
        examples=["ana.gomez@universidad.edu.co"],
    )
    telefono: str = Field(
        ...,
        min_length=7,
        max_length=15,
        description="Teléfono celular de contacto (7 a 15 dígitos numéricos)",
        examples=["3001234567"],
    )
    tipo_persona: TipoPersona = Field(
        ...,
        description="Tipo de persona: profesor o estudiante",
        examples=[TipoPersona.estudiante],
    )
    facultad: str = Field(
        ...,
        min_length=1,
        max_length=150,
        description="Facultad a la que pertenece (texto libre)",
        examples=["Facultad de Ingeniería"],
    )

    @field_validator("cedula")
    @classmethod
    def validar_cedula(cls, value: str) -> str:
        trimmed = value.strip()
        if not DIGITS_REGEX.match(trimmed) or len(trimmed) < 6 or len(trimmed) > 15:
            raise ValueError("La cédula debe contener exclusivamente entre 6 y 15 dígitos numéricos.")
        return trimmed

    @field_validator("nombre_completo")
    @classmethod
    def validar_nombre(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("El nombre completo es obligatorio y no puede estar vacío.")
        if len(trimmed) > 100:
            raise ValueError("El nombre completo no puede superar los 100 caracteres.")
        return trimmed

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, value: str) -> str:
        trimmed = value.strip()
        if not DIGITS_REGEX.match(trimmed) or len(trimmed) < 7 or len(trimmed) > 15:
            raise ValueError("El teléfono debe contener exclusivamente entre 7 y 15 dígitos numéricos.")
        return trimmed

    @field_validator("facultad")
    @classmethod
    def validar_facultad(cls, value: str) -> str:
        trimmed = value.strip()
        if not trimmed:
            raise ValueError("La facultad es obligatoria y no puede estar vacía.")
        if len(trimmed) > 150:
            raise ValueError("La facultad no puede superar los 150 caracteres.")
        return trimmed

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                return None
            if not EMAIL_REGEX.match(trimmed) or len(trimmed) > 150:
                raise ValueError("El formato del correo electrónico es inválido.")
            return trimmed.lower()
        return None


class PersonaCreate(PersonaBase):
    """Esquema para registrar una nueva Persona."""

    pass


class PersonaUpdate(BaseModel):
    """Esquema para actualización de Persona. La cédula es inmutable."""

    nombre_completo: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Nuevo nombre completo",
    )
    correo: Optional[str] = Field(
        None,
        max_length=150,
        description="Nuevo correo electrónico",
    )
    telefono: Optional[str] = Field(
        None,
        min_length=7,
        max_length=15,
        description="Nuevo teléfono celular",
    )
    tipo_persona: Optional[TipoPersona] = Field(
        None,
        description="Nuevo tipo de persona: profesor o estudiante",
    )
    facultad: Optional[str] = Field(
        None,
        min_length=1,
        max_length=150,
        description="Nueva facultad",
    )
    activo: Optional[bool] = Field(
        None,
        description="Estado activo o inactivo",
    )

    @field_validator("nombre_completo")
    @classmethod
    def validar_nombre_opt(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("El nombre completo no puede estar vacío.")
            if len(trimmed) > 100:
                raise ValueError("El nombre completo no puede superar los 100 caracteres.")
            return trimmed
        return value

    @field_validator("telefono")
    @classmethod
    def validar_telefono_opt(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not DIGITS_REGEX.match(trimmed) or len(trimmed) < 7 or len(trimmed) > 15:
                raise ValueError("El teléfono debe contener exclusivamente entre 7 y 15 dígitos numéricos.")
            return trimmed
        return value

    @field_validator("facultad")
    @classmethod
    def validar_facultad_opt(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                raise ValueError("La facultad no puede estar vacía.")
            if len(trimmed) > 150:
                raise ValueError("La facultad no puede superar los 150 caracteres.")
            return trimmed
        return value

    @field_validator("correo")
    @classmethod
    def validar_correo_opt(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            trimmed = value.strip()
            if not trimmed:
                return None
            if not EMAIL_REGEX.match(trimmed) or len(trimmed) > 150:
                raise ValueError("El formato del correo electrónico es inválido.")
            return trimmed.lower()
        return value


class PersonaResponse(PersonaBase):
    """Esquema de respuesta para Persona."""

    activo: bool

    model_config = ConfigDict(from_attributes=True)
