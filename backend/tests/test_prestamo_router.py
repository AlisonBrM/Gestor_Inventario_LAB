from datetime import date, timedelta
from unittest.mock import MagicMock
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.prestamo import Prestamo
from app.routers.prestamo_router import get_prestamo_service
from app.services.prestamo_service import (
    PrestamoNotFoundError,
    PrestamoService,
    PrestamoValidationError,
)

client = TestClient(app)


@pytest.fixture
def mock_service():
    """Mock del PrestamoService para pruebas de endpoints del router."""
    service = MagicMock(spec=PrestamoService)
    app.dependency_overrides[get_prestamo_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


# =========================================================================
# Pruebas del Endpoint POST /api/prestamos
# =========================================================================

def test_endpoint_crear_prestamo_exito(mock_service):
    """Verifica que POST /api/prestamos retorne 201 y los datos del préstamo."""
    hoy = date.today()
    fecha_esperada = hoy + timedelta(days=15)

    mock_service.crear_prestamo.return_value = Prestamo(
        id=1,
        cedula_persona="1001234567",
        id_equipo=2,
        fecha_prestamo=hoy,
        fecha_devolucion_esperada=fecha_esperada,
    )

    payload = {
        "cedula_persona": "1001234567",
        "id_equipo": 2,
        "fecha_prestamo": str(hoy),
    }
    response = client.post("/api/prestamos", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == 1
    assert data["cedula_persona"] == "1001234567"
    assert data["id_equipo"] == 2
    assert data["fecha_prestamo"] == str(hoy)
    assert data["fecha_devolucion_esperada"] == str(fecha_esperada)


def test_endpoint_crear_prestamo_rechazo_vencido_400(mock_service):
    """RN-PREST-01: Verifica que retorne 400 si el solicitante tiene préstamos vencidos sin devolver."""
    mock_service.crear_prestamo.side_effect = PrestamoValidationError(
        "El solicitante con cédula '1001234567' tiene un préstamo vencido sin devolver."
    )

    payload = {
        "cedula_persona": "1001234567",
        "id_equipo": 2,
    }
    response = client.post("/api/prestamos", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "préstamo vencido sin devolver" in response.json()["detail"]


def test_endpoint_crear_prestamo_rechazo_mantenimiento_400(mock_service):
    """RN-PREST-02: Verifica que retorne 400 si el equipo está en mantenimiento."""
    mock_service.crear_prestamo.side_effect = PrestamoValidationError(
        "El equipo se encuentra marcado en mantenimiento. No puede ser prestado."
    )

    payload = {
        "cedula_persona": "1001234567",
        "id_equipo": 2,
    }
    response = client.post("/api/prestamos", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "mantenimiento" in response.json()["detail"]


def test_endpoint_crear_prestamo_no_encontrado_404(mock_service):
    """Verifica que retorne 404 si la persona o equipo no existen."""
    mock_service.crear_prestamo.side_effect = PrestamoNotFoundError(
        "La persona con cédula '99999999' no existe en el sistema."
    )

    payload = {
        "cedula_persona": "99999999",
        "id_equipo": 2,
    }
    response = client.post("/api/prestamos", json=payload)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no existe" in response.json()["detail"]


def test_endpoint_crear_prestamo_validacion_schema_422():
    """Verifica que retorne 422 si el body es inválido según Pydantic."""
    payload = {
        "cedula_persona": "   ",
        "id_equipo": 0,  # ge=1 requerido
    }
    response = client.post("/api/prestamos", json=payload)

    assert response.status_code == 422


# =========================================================================
# Pruebas del Endpoint GET /api/prestamos/{id}
# =========================================================================

def test_endpoint_obtener_prestamo_exito(mock_service):
    """Verifica que GET /api/prestamos/{id} retorne 200 y el préstamo."""
    hoy = date.today()
    mock_service.obtener_prestamo_por_id.return_value = Prestamo(
        id=5,
        cedula_persona="1001234567",
        id_equipo=1,
        fecha_prestamo=hoy,
        fecha_devolucion_esperada=hoy + timedelta(days=10),
    )

    response = client.get("/api/prestamos/5")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["id"] == 5
    assert response.json()["cedula_persona"] == "1001234567"


def test_endpoint_obtener_prestamo_no_encontrado_404(mock_service):
    """Verifica que GET /api/prestamos/{id} retorne 404 si no existe."""
    mock_service.obtener_prestamo_por_id.side_effect = PrestamoNotFoundError(99)

    response = client.get("/api/prestamos/99")

    assert response.status_code == status.HTTP_404_NOT_FOUND
