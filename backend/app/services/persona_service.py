import re
from typing import Optional, Sequence

from app.models.persona import Persona
from app.repositories.persona_repository import PersonaRepository
from app.schemas.persona import PersonaCreate, PersonaUpdate, TipoPersona

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")
DIGITS_REGEX = re.compile(r"^\d+$")


class PersonaNotFoundError(Exception):
    """Lanzada cuando una persona no existe en el sistema."""

    def __init__(self, cedula: str) -> None:
        super().__init__(f"Persona con cédula '{cedula}' no encontrada.")
        self.cedula = cedula


class PersonaAlreadyExistsError(Exception):
    """Lanzada cuando ya existe una persona con la misma cédula."""

    def __init__(self, cedula: str) -> None:
        super().__init__(f"Ya existe una persona registrada con la cédula '{cedula}'.")
        self.cedula = cedula


class PersonaValidationError(Exception):
    """Lanzada cuando falla una validación de dominio de la persona."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class PersonaService:
    """Servicio con la lógica y reglas de negocio para Persona."""

    MIN_CEDULA_DIGITOS: int = 6
    MAX_CEDULA_DIGITOS: int = 15
    MIN_TEL_DIGITOS: int = 7
    MAX_TEL_DIGITOS: int = 15
    MAX_NOMBRE_LEN: int = 100
    MAX_FACULTAD_LEN: int = 150
    MAX_CORREO_LEN: int = 150

    def __init__(self, repository: PersonaRepository) -> None:
        self.repository = repository

    def _validar_cedula(self, cedula: str) -> str:
        """RN-PER-01: Valida que la cédula contenga solo dígitos y entre 6 y 15 caracteres."""
        if not cedula or not cedula.strip():
            raise PersonaValidationError("La cédula de la persona es obligatoria.")
        limpia = cedula.strip()
        if not DIGITS_REGEX.match(limpia):
            raise PersonaValidationError("La cédula debe contener exclusivamente dígitos numéricos.")
        if len(limpia) < self.MIN_CEDULA_DIGITOS or len(limpia) > self.MAX_CEDULA_DIGITOS:
            raise PersonaValidationError(
                f"La cédula debe tener entre {self.MIN_CEDULA_DIGITOS} y "
                f"{self.MAX_CEDULA_DIGITOS} dígitos numéricos."
            )
        return limpia

    def _validar_nombre_completo(self, nombre: str) -> str:
        """RN-PER-02: Valida que el nombre completo no esté vacío y no exceda longitud."""
        if not nombre or not nombre.strip():
            raise PersonaValidationError("El nombre completo es obligatorio y no puede estar vacío.")
        limpio = nombre.strip()
        if len(limpio) > self.MAX_NOMBRE_LEN:
            raise PersonaValidationError(
                f"El nombre completo no puede superar los {self.MAX_NOMBRE_LEN} caracteres."
            )
        return limpio

    def _validar_telefono(self, telefono: str) -> str:
        """RN-PER-04: Valida formato exclusivamente numérico de teléfono celular."""
        if not telefono or not telefono.strip():
            raise PersonaValidationError("El teléfono de contacto es obligatorio.")
        limpio = telefono.strip()
        if not DIGITS_REGEX.match(limpio):
            raise PersonaValidationError("El teléfono debe contener exclusivamente dígitos numéricos.")
        if len(limpio) < self.MIN_TEL_DIGITOS or len(limpio) > self.MAX_TEL_DIGITOS:
            raise PersonaValidationError(
                f"El teléfono debe tener entre {self.MIN_TEL_DIGITOS} y "
                f"{self.MAX_TEL_DIGITOS} dígitos numéricos."
            )
        return limpio

    def _validar_facultad(self, facultad: str) -> str:
        """RN-PER-05: Valida que la facultad no esté vacía (SUP-09)."""
        if not facultad or not facultad.strip():
            raise PersonaValidationError("La facultad es obligatoria y no puede estar vacía.")
        limpia = facultad.strip()
        if len(limpia) > self.MAX_FACULTAD_LEN:
            raise PersonaValidationError(
                f"La facultad no puede superar los {self.MAX_FACULTAD_LEN} caracteres."
            )
        return limpia

    def _validar_tipo_persona(self, tipo: TipoPersona | str) -> str:
        """RN-PER-03: Valida que el tipo de persona sea profesor o estudiante."""
        val = tipo.value if isinstance(tipo, TipoPersona) else str(tipo).strip().lower()
        if val not in {TipoPersona.profesor.value, TipoPersona.estudiante.value}:
            raise PersonaValidationError("El tipo de persona debe ser 'profesor' o 'estudiante'.")
        return val

    def _validar_correo(self, correo: Optional[str]) -> Optional[str]:
        """RN-PER-06: Valida formato de correo si se proporciona."""
        if correo is None:
            return None
        limpio = correo.strip()
        if not limpio:
            return None
        if not EMAIL_REGEX.match(limpio) or len(limpio) > self.MAX_CORREO_LEN:
            raise PersonaValidationError("El formato del correo electrónico es inválido.")
        return limpio.lower()

    def listar_personas(
        self,
        solo_activas: bool = True,
        tipo_persona: Optional[str] = None,
        facultad: Optional[str] = None,
        busqueda: Optional[str] = None,
    ) -> Sequence[Persona]:
        """Obtiene la lista de personas aplicando los filtros indicados."""
        tipo_val = None
        if tipo_persona:
            tipo_val = self._validar_tipo_persona(tipo_persona)
        return self.repository.get_all(
            solo_activas=solo_activas,
            tipo_persona=tipo_val,
            facultad=facultad,
            busqueda=busqueda,
        )

    def obtener_persona_por_cedula(self, cedula: str) -> Persona:
        """Obtiene una persona por su cédula o lanza PersonaNotFoundError."""
        cedula_limpia = self._validar_cedula(cedula)
        persona = self.repository.get_by_cedula(cedula_limpia)
        if not persona:
            raise PersonaNotFoundError(cedula_limpia)
        return persona

    def crear_persona(self, datos: PersonaCreate) -> Persona:
        """Crea una nueva persona aplicando las reglas de negocio."""
        cedula_limpia = self._validar_cedula(datos.cedula)
        nombre_limpio = self._validar_nombre_completo(datos.nombre_completo)
        telefono_limpio = self._validar_telefono(datos.telefono)
        facultad_limpia = self._validar_facultad(datos.facultad)
        tipo_val = self._validar_tipo_persona(datos.tipo_persona)
        correo_limpio = self._validar_correo(datos.correo)

        # RN-PER-01: Unicidad de la cédula
        existente = self.repository.get_by_cedula(cedula_limpia)
        if existente:
            raise PersonaAlreadyExistsError(cedula_limpia)

        nueva_persona = Persona(
            cedula=cedula_limpia,
            nombre_completo=nombre_limpio,
            correo=correo_limpio,
            telefono=telefono_limpio,
            tipo_persona=tipo_val,
            facultad=facultad_limpia,
            activo=True,
        )
        return self.repository.create(nueva_persona)

    def actualizar_persona(self, cedula: str, datos: PersonaUpdate) -> Persona:
        """Actualiza una persona existente aplicando las reglas de negocio."""
        persona = self.obtener_persona_por_cedula(cedula)

        if datos.nombre_completo is not None:
            persona.nombre_completo = self._validar_nombre_completo(datos.nombre_completo)

        if datos.telefono is not None:
            persona.telefono = self._validar_telefono(datos.telefono)

        if datos.tipo_persona is not None:
            persona.tipo_persona = self._validar_tipo_persona(datos.tipo_persona)

        if datos.facultad is not None:
            persona.facultad = self._validar_facultad(datos.facultad)

        if datos.correo is not None:
            persona.correo = self._validar_correo(datos.correo)

        if datos.activo is not None:
            persona.activo = datos.activo

        return self.repository.update(persona)

    def eliminar_persona_logica(self, cedula: str) -> Persona:
        """RN-PER-07: Borrado lógico de la persona (activo = False)."""
        persona = self.obtener_persona_por_cedula(cedula)
        return self.repository.delete_logical(persona)
