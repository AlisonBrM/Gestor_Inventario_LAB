from unittest.mock import MagicMock
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.persona import Persona
from app.routers.persona_router import get_persona_service
from app.services.persona_service import (
    PersonaAlreadyExistsError,
    PersonaNotFoundError,
    PersonaService,
    PersonaValidationError,
)

client = TestClient(app)


@pytest.fixture
def mock_service():
    """Mock del PersonaService para pruebas de endpoints en el router."""
    service = MagicMock(spec=PersonaService)
    app.dependency_overrides[get_persona_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


# =========================================================================
# Pruebas de Endpoints POST /api/personas
# =========================================================================

def test_endpoint_crear_persona_exito(mock_service):
    mock_service.crear_persona.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Carlos Mendoza",
        correo="carlos@uni.edu",
        telefono="3001234567",
        tipo_persona="estudiante",
        facultad="Ingeniería",
        activo=True,
    )

    payload = {
        "cedula": "1001234567",
        "nombre_completo": "Carlos Mendoza",
        "correo": "carlos@uni.edu",
        "telefono": "3001234567",
        "tipo_persona": "estudiante",
        "facultad": "Ingeniería",
    }
    response = client.post("/api/personas", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["cedula"] == "1001234567"
    assert data["nombre_completo"] == "Carlos Mendoza"
    assert data["tipo_persona"] == "estudiante"
    assert data["activo"] is True


def test_endpoint_crear_persona_duplicada(mock_service):
    mock_service.crear_persona.side_effect = PersonaAlreadyExistsError("1001234567")

    payload = {
        "cedula": "1001234567",
        "nombre_completo": "Carlos Mendoza",
        "correo": "carlos@uni.edu",
        "telefono": "3001234567",
        "tipo_persona": "estudiante",
        "facultad": "Ingeniería",
    }
    response = client.post("/api/personas", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ya existe una persona registrada" in response.json()["detail"]


def test_endpoint_crear_persona_validacion_pydantic():
    """Valida que Pydantic rechace payloads con campos faltantes o inválidos."""
    payload = {
        "cedula": "abc",  # Inválido, no numérico
        "nombre_completo": "",
    }
    response = client.post("/api/personas", json=payload)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


# =========================================================================
# Pruebas de Endpoints GET /api/personas
# =========================================================================

def test_endpoint_listar_personas(mock_service):
    mock_service.listar_personas.return_value = [
        Persona(
            cedula="1001234567",
            nombre_completo="Ana Gómez",
            telefono="3001234567",
            tipo_persona="profesor",
            facultad="Ciencias",
            activo=True,
        )
    ]

    response = client.get("/api/personas?solo_activas=true&tipo_persona=profesor")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["cedula"] == "1001234567"


def test_endpoint_obtener_persona_exito(mock_service):
    mock_service.obtener_persona_por_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Ana Gómez",
        telefono="3001234567",
        tipo_persona="profesor",
        facultad="Ciencias",
        activo=True,
    )

    response = client.get("/api/personas/1001234567")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["cedula"] == "1001234567"


def test_endpoint_obtener_persona_no_encontrada(mock_service):
    mock_service.obtener_persona_por_cedula.side_effect = PersonaNotFoundError("999999999")

    response = client.get("/api/personas/999999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrada" in response.json()["detail"]


# =========================================================================
# Pruebas de Endpoints PUT /api/personas/{cedula}
# =========================================================================

def test_endpoint_actualizar_persona_exito(mock_service):
    mock_service.actualizar_persona.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Ana Gómez Actualizada",
        telefono="3111234567",
        tipo_persona="profesor",
        facultad="Ciencias",
        activo=True,
    )

    payload = {"nombre_completo": "Ana Gómez Actualizada", "telefono": "3111234567"}
    response = client.put("/api/personas/1001234567", json=payload)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["nombre_completo"] == "Ana Gómez Actualizada"


def test_endpoint_actualizar_persona_no_encontrada(mock_service):
    mock_service.actualizar_persona.side_effect = PersonaNotFoundError("999999999")

    payload = {"nombre_completo": "Nuevo Nombre"}
    response = client.put("/api/personas/999999999", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND


# =========================================================================
# Pruebas de Endpoints DELETE /api/personas/{cedula}
# =========================================================================

def test_endpoint_eliminar_persona_exito(mock_service):
    mock_service.eliminar_persona_logica.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Ana Gómez",
        telefono="3001234567",
        tipo_persona="profesor",
        facultad="Ciencias",
        activo=False,
    )

    response = client.delete("/api/personas/1001234567")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["activo"] is False


def test_endpoint_eliminar_persona_no_encontrada(mock_service):
    mock_service.eliminar_persona_logica.side_effect = PersonaNotFoundError("999999999")

    response = client.delete("/api/personas/999999999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
