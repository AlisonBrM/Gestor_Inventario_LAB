from datetime import date
from unittest.mock import MagicMock
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.equipo import Equipo
from app.routers.equipo_router import get_equipo_service
from app.services.equipo_service import (
    EquipoAlreadyExistsError,
    EquipoNotFoundError,
    EquipoService,
    EquipoValidationError,
)

client = TestClient(app)


@pytest.fixture
def mock_service():
    """Mock del EquipoService para pruebas de endpoints del router."""
    service = MagicMock(spec=EquipoService)
    app.dependency_overrides[get_equipo_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


# =========================================================================
# Pruebas de Endpoints POST /api/equipos
# =========================================================================

def test_endpoint_crear_equipo_exito(mock_service):
    mock_service.crear_equipo.return_value = Equipo(
        id=1,
        id_categoria=2,
        nombre="Osciloscopio Digital",
        secuencial="OSC-001",
        descripcion="2 canales",
        mantenimiento=False,
        fecha_creacion=date.today(),
        activo=True,
    )

    payload = {
        "id_categoria": 2,
        "nombre": "Osciloscopio Digital",
        "secuencial": "OSC-001",
        "descripcion": "2 canales",
    }
    response = client.post("/api/equipos", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == 1
    assert data["nombre"] == "Osciloscopio Digital"
    assert data["secuencial"] == "OSC-001"
    assert data["mantenimiento"] is False
    assert data["activo"] is True


def test_endpoint_crear_equipo_secuencial_duplicado(mock_service):
    mock_service.crear_equipo.side_effect = EquipoAlreadyExistsError("OSC-001")

    payload = {
        "id_categoria": 2,
        "nombre": "Osciloscopio",
        "secuencial": "OSC-001",
    }
    response = client.post("/api/equipos", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ya existe un equipo registrado con el secuencial" in response.json()["detail"]


def test_endpoint_crear_equipo_categoria_invalida(mock_service):
    mock_service.crear_equipo.side_effect = EquipoValidationError("Categoría inactiva")

    payload = {
        "id_categoria": 9,
        "nombre": "Osciloscopio",
        "secuencial": "OSC-002",
    }
    response = client.post("/api/equipos", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Categoría inactiva" in response.json()["detail"]


def test_endpoint_crear_equipo_error_schema():
    payload = {
        "id_categoria": 0,  # ge=1 falla
        "nombre": "",       # min_length=1 falla
        "secuencial": "EQ-1",
    }
    response = client.post("/api/equipos", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


# =========================================================================
# Pruebas de Endpoints GET /api/equipos
# =========================================================================

def test_endpoint_listar_equipos(mock_service):
    mock_service.listar_equipos.return_value = [
        Equipo(
            id=1,
            id_categoria=2,
            nombre="Eq 1",
            secuencial="E-1",
            descripcion=None,
            mantenimiento=False,
            fecha_creacion=date.today(),
            activo=True,
        ),
    ]

    response = client.get("/api/equipos?solo_activos=true&id_categoria=2")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["secuencial"] == "E-1"
    mock_service.listar_equipos.assert_called_once_with(
        solo_activos=True, id_categoria=2, en_mantenimiento=None
    )


def test_endpoint_obtener_equipo_por_id_exito(mock_service):
    mock_service.obtener_equipo_por_id.return_value = Equipo(
        id=5,
        id_categoria=1,
        nombre="Multímetro Fluke",
        secuencial="MUL-01",
        descripcion=None,
        mantenimiento=False,
        fecha_creacion=date.today(),
        activo=True,
    )

    response = client.get("/api/equipos/5")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 5
    assert data["secuencial"] == "MUL-01"


def test_endpoint_obtener_equipo_por_id_no_encontrado(mock_service):
    mock_service.obtener_equipo_por_id.side_effect = EquipoNotFoundError(99)

    response = client.get("/api/equipos/99")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrado" in response.json()["detail"]


# =========================================================================
# Pruebas de Endpoints PUT /api/equipos/{id}
# =========================================================================

def test_endpoint_actualizar_equipo_exito(mock_service):
    mock_service.actualizar_equipo.return_value = Equipo(
        id=1,
        id_categoria=2,
        nombre="Osciloscopio Actualizado",
        secuencial="OSC-001",
        descripcion="Calibrado",
        mantenimiento=True,
        fecha_creacion=date.today(),
        activo=True,
    )

    payload = {
        "nombre": "Osciloscopio Actualizado",
        "descripcion": "Calibrado",
        "mantenimiento": True,
    }
    response = client.put("/api/equipos/1", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nombre"] == "Osciloscopio Actualizado"
    assert data["mantenimiento"] is True


def test_endpoint_actualizar_equipo_no_encontrado(mock_service):
    mock_service.actualizar_equipo.side_effect = EquipoNotFoundError(88)

    response = client.put("/api/equipos/88", json={"nombre": "Nuevo"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_endpoint_actualizar_equipo_secuencial_duplicado(mock_service):
    mock_service.actualizar_equipo.side_effect = EquipoAlreadyExistsError("DUP-01")

    response = client.put("/api/equipos/1", json={"secuencial": "DUP-01"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# =========================================================================
# Pruebas de Endpoints DELETE /api/equipos/{id}
# =========================================================================

def test_endpoint_eliminar_equipo_logico_exito(mock_service):
    mock_service.eliminar_equipo_logico.return_value = Equipo(
        id=1,
        id_categoria=2,
        nombre="Obsoleto",
        secuencial="OBS-01",
        descripcion=None,
        mantenimiento=False,
        fecha_creacion=date.today(),
        activo=False,
    )

    response = client.delete("/api/equipos/1")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["activo"] is False


def test_endpoint_eliminar_equipo_no_encontrado(mock_service):
    mock_service.eliminar_equipo_logico.side_effect = EquipoNotFoundError(404)

    response = client.delete("/api/equipos/404")

    assert response.status_code == status.HTTP_404_NOT_FOUND
