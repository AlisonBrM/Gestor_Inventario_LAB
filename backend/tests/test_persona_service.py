from unittest.mock import create_autospec
import pytest

from app.models.persona import Persona
from app.repositories.persona_repository import PersonaRepository
from app.schemas.persona import PersonaCreate, PersonaUpdate, TipoPersona
from app.services.persona_service import (
    PersonaAlreadyExistsError,
    PersonaNotFoundError,
    PersonaService,
    PersonaValidationError,
)


@pytest.fixture
def mock_repository():
    """Fixture que crea un mock tipado del repositorio de Persona."""
    return create_autospec(PersonaRepository, instance=True)


@pytest.fixture
def service(mock_repository):
    """Fixture que instancia PersonaService con el repositorio mockeado."""
    return PersonaService(repository=mock_repository)


# =========================================================================
# 1. Pruebas de Creación (RN-PER-01 a RN-PER-07)
# =========================================================================

def test_crear_persona_estudiante_exito(service, mock_repository):
    """Verifica que una persona de tipo estudiante se cree exitosamente."""
    datos = PersonaCreate(
        cedula="1001234567",
        nombre_completo="Ana María Gómez",
        correo="ana.gomez@universidad.edu.co",
        telefono="3001234567",
        tipo_persona=TipoPersona.estudiante,
        facultad="Facultad de Ingeniería",
    )
    mock_repository.get_by_cedula.return_value = None

    def simular_creacion(p: Persona) -> Persona:
        return p

    mock_repository.create.side_effect = simular_creacion

    resultado = service.crear_persona(datos)

    assert resultado.cedula == "1001234567"
    assert resultado.nombre_completo == "Ana María Gómez"
    assert resultado.correo == "ana.gomez@universidad.edu.co"
    assert resultado.telefono == "3001234567"
    assert resultado.tipo_persona == "estudiante"
    assert resultado.facultad == "Facultad de Ingeniería"
    assert resultado.activo is True
    mock_repository.get_by_cedula.assert_called_once_with("1001234567")
    mock_repository.create.assert_called_once()


def test_crear_persona_profesor_sin_correo_exito(service, mock_repository):
    """Verifica que un profesor pueda crearse sin correo electrónico (opcional)."""
    datos = PersonaCreate(
        cedula="987654321",
        nombre_completo="Carlos Andrés López",
        correo=None,
        telefono="3119876543",
        tipo_persona=TipoPersona.profesor,
        facultad="Facultad de Ciencias Básicas",
    )
    mock_repository.get_by_cedula.return_value = None
    mock_repository.create.side_effect = lambda p: p

    resultado = service.crear_persona(datos)

    assert resultado.cedula == "987654321"
    assert resultado.correo is None
    assert resultado.tipo_persona == "profesor"
    assert resultado.activo is True


def test_crear_persona_cedula_duplicada(service, mock_repository):
    """RN-PER-01: Rechaza creación cuando la cédula ya existe."""
    datos = PersonaCreate(
        cedula="1001234567",
        nombre_completo="Pedro Pérez",
        telefono="3009998877",
        tipo_persona=TipoPersona.estudiante,
        facultad="Ingeniería",
    )
    mock_repository.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Persona Existente",
        telefono="3001112233",
        tipo_persona="estudiante",
        facultad="Ingeniería",
        activo=True,
    )

    with pytest.raises(PersonaAlreadyExistsError) as exc_info:
        service.crear_persona(datos)

    assert "1001234567" in str(exc_info.value)
    mock_repository.create.assert_not_called()


def test_crear_persona_cedula_no_numerica(service):
    """RN-PER-01: Rechaza cédula que contenga caracteres no numéricos."""
    with pytest.raises(PersonaValidationError, match="dígitos numéricos"):
        service._validar_cedula("10012A456")


def test_crear_persona_cedula_longitud_invalida(service):
    """RN-PER-01: Rechaza cédula con longitud menor a 6 o mayor a 15 dígitos."""
    with pytest.raises(PersonaValidationError, match="entre 6 y 15 dígitos"):
        service._validar_cedula("12345")

    with pytest.raises(PersonaValidationError, match="entre 6 y 15 dígitos"):
        service._validar_cedula("1234567890123456")


def test_crear_persona_nombre_vacio(service):
    """RN-PER-02: Rechaza nombre vacío o de solo espacios."""
    with pytest.raises(PersonaValidationError, match="El nombre completo es obligatorio"):
        service._validar_nombre_completo("   ")


def test_crear_persona_nombre_demasiado_largo(service):
    """RN-PER-02: Rechaza nombre que supere 100 caracteres."""
    nombre_largo = "A" * 101
    with pytest.raises(PersonaValidationError, match="superar los 100 caracteres"):
        service._validar_nombre_completo(nombre_largo)


def test_crear_persona_telefono_no_numerico(service):
    """RN-PER-04: Rechaza teléfono no numérico."""
    with pytest.raises(PersonaValidationError, match="dígitos numéricos"):
        service._validar_telefono("300-123456")


def test_crear_persona_telefono_longitud_invalida(service):
    """RN-PER-04: Rechaza teléfono con menos de 7 o más de 15 dígitos."""
    with pytest.raises(PersonaValidationError, match="entre 7 y 15 dígitos"):
        service._validar_telefono("123456")

    with pytest.raises(PersonaValidationError, match="entre 7 y 15 dígitos"):
        service._validar_telefono("1234567890123456")


def test_crear_persona_facultad_vacia(service):
    """RN-PER-05: Rechaza facultad vacía."""
    with pytest.raises(PersonaValidationError, match="La facultad es obligatoria"):
        service._validar_facultad("  ")


def test_crear_persona_tipo_persona_invalido(service):
    """RN-PER-03: Rechaza tipo de persona que no sea profesor o estudiante."""
    with pytest.raises(PersonaValidationError, match="profesor' o 'estudiante'"):
        service._validar_tipo_persona("visitante")


def test_crear_persona_correo_invalido(service):
    """RN-PER-06: Rechaza formato de correo electrónico inválido."""
    with pytest.raises(PersonaValidationError, match="formato del correo electrónico es inválido"):
        service._validar_correo("correo_invalido_sin_arroba.com")


# =========================================================================
# 2. Pruebas de Consulta y Búsqueda
# =========================================================================

def test_obtener_persona_por_cedula_exito(service, mock_repository):
    """Verifica la consulta exitosa por cédula."""
    persona_mock = Persona(
        cedula="1001234567",
        nombre_completo="María Paz",
        correo="maria@uni.edu",
        telefono="3151234567",
        tipo_persona="estudiante",
        facultad="Artes",
        activo=True,
    )
    mock_repository.get_by_cedula.return_value = persona_mock

    resultado = service.obtener_persona_por_cedula("1001234567")

    assert resultado.cedula == "1001234567"
    assert resultado.nombre_completo == "María Paz"
    mock_repository.get_by_cedula.assert_called_once_with("1001234567")


def test_obtener_persona_por_cedula_no_encontrada(service, mock_repository):
    """RN-PER-08: Lanza PersonaNotFoundError si la persona no existe."""
    mock_repository.get_by_cedula.return_value = None

    with pytest.raises(PersonaNotFoundError) as exc_info:
        service.obtener_persona_por_cedula("999999999")

    assert "999999999" in str(exc_info.value)


def test_listar_personas_con_filtros(service, mock_repository):
    """Verifica que listar_personas delegue correctamente al repositorio con filtros."""
    personas_lista = [
        Persona(
            cedula="1001234567",
            nombre_completo="Ana María Gómez",
            telefono="3001234567",
            tipo_persona="profesor",
            facultad="Ingeniería",
            activo=True,
        )
    ]
    mock_repository.get_all.return_value = personas_lista

    resultado = service.listar_personas(
        solo_activas=True,
        tipo_persona="profesor",
        facultad="Ingeniería",
        busqueda="Gómez",
    )

    assert len(resultado) == 1
    assert resultado[0].cedula == "1001234567"
    mock_repository.get_all.assert_called_once_with(
        solo_activas=True,
        tipo_persona="profesor",
        facultad="Ingeniería",
        busqueda="Gómez",
    )


# =========================================================================
# 3. Pruebas de Actualización
# =========================================================================

def test_actualizar_persona_exito(service, mock_repository):
    """Verifica la actualización de campos permitidos en Persona."""
    persona_existente = Persona(
        cedula="1001234567",
        nombre_completo="Laura Ramos",
        correo="laura@uni.edu",
        telefono="3101234567",
        tipo_persona="estudiante",
        facultad="Medicina",
        activo=True,
    )
    mock_repository.get_by_cedula.return_value = persona_existente
    mock_repository.update.side_effect = lambda p: p

    datos_update = PersonaUpdate(
        nombre_completo="Laura Ramos Silva",
        telefono="3129876543",
        facultad="Salud Pública",
        tipo_persona=TipoPersona.profesor,
        correo="laura.ramos@uni.edu",
        activo=True,
    )

    resultado = service.actualizar_persona("1001234567", datos_update)

    assert resultado.nombre_completo == "Laura Ramos Silva"
    assert resultado.telefono == "3129876543"
    assert resultado.facultad == "Salud Pública"
    assert resultado.tipo_persona == "profesor"
    assert resultado.correo == "laura.ramos@uni.edu"
    mock_repository.update.assert_called_once()


def test_actualizar_persona_no_encontrada(service, mock_repository):
    """Lanza PersonaNotFoundError si la persona a actualizar no existe."""
    mock_repository.get_by_cedula.return_value = None
    datos = PersonaUpdate(nombre_completo="Nuevo Nombre")

    with pytest.raises(PersonaNotFoundError):
        service.actualizar_persona("888888888", datos)


# =========================================================================
# 4. Pruebas de Borrado Lógico (RN-PER-07)
# =========================================================================

def test_eliminar_persona_logica_exito(service, mock_repository):
    """RN-PER-07: Borrado lógico establece activo en False."""
    persona_existente = Persona(
        cedula="1001234567",
        nombre_completo="Jorge Vega",
        telefono="3201234567",
        tipo_persona="profesor",
        facultad="Humanidades",
        activo=True,
    )
    mock_repository.get_by_cedula.return_value = persona_existente

    def simular_borrado(p: Persona) -> Persona:
        p.activo = False
        return p

    mock_repository.delete_logical.side_effect = simular_borrado

    resultado = service.eliminar_persona_logica("1001234567")

    assert resultado.activo is False
    mock_repository.delete_logical.assert_called_once_with(persona_existente)


def test_eliminar_persona_no_encontrada(service, mock_repository):
    """Lanza PersonaNotFoundError si la persona a eliminar no existe."""
    mock_repository.get_by_cedula.return_value = None

    with pytest.raises(PersonaNotFoundError):
        service.eliminar_persona_logica("777777777")
