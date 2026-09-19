from unittest.mock import MagicMock
import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.models.categoria import Categoria
from app.routers.categoria_router import get_categoria_service
from app.services.categoria_service import (
    CategoriaAlreadyExistsError,
    CategoriaNotFoundError,
    CategoriaService,
    CategoriaValidationError,
)

client = TestClient(app)


@pytest.fixture
def mock_service():
    """Mock del CategoriaService para pruebas de endpoints en el router."""
    service = MagicMock(spec=CategoriaService)
    app.dependency_overrides[get_categoria_service] = lambda: service
    yield service
    app.dependency_overrides.clear()


# =========================================================================
# Pruebas de Endpoints POST /api/categorias
# =========================================================================

def test_endpoint_crear_categoria_exito(mock_service):
    mock_service.crear_categoria.return_value = Categoria(
        id=1,
        nombre="Laptops",
        descripcion="Portátiles para préstamo",
        plazo_entrega=15,
        activo=True,
    )

    payload = {
        "nombre": "Laptops",
        "descripcion": "Portátiles para préstamo",
        "plazo_entrega": 15,
    }
    response = client.post("/api/categorias", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["id"] == 1
    assert data["nombre"] == "Laptops"
    assert data["plazo_entrega"] == 15
    assert data["activo"] is True


def test_endpoint_crear_categoria_nombre_duplicado(mock_service):
    mock_service.crear_categoria.side_effect = CategoriaAlreadyExistsError("Laptops")

    payload = {"nombre": "Laptops", "plazo_entrega": 15}
    response = client.post("/api/categorias", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Ya existe una categoría" in response.json()["detail"]


def test_endpoint_crear_categoria_error_validacion_schema():
    # plazo_entrega > 180 es rechazado a nivel Pydantic (HTTP 422)
    payload = {"nombre": "Laptops", "plazo_entrega": 200}
    response = client.post("/api/categorias", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT



# =========================================================================
# Pruebas de Endpoints GET /api/categorias
# =========================================================================

def test_endpoint_listar_categorias(mock_service):
    mock_service.listar_categorias.return_value = [
        Categoria(id=1, nombre="Cat 1", descripcion=None, plazo_entrega=5, activo=True),
        Categoria(id=2, nombre="Cat 2", descripcion=None, plazo_entrega=10, activo=True),
    ]

    response = client.get("/api/categorias")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2
    assert data[0]["nombre"] == "Cat 1"
    mock_service.listar_categorias.assert_called_once_with(solo_activas=True)


def test_endpoint_obtener_categoria_por_id_exito(mock_service):
    mock_service.obtener_categoria_por_id.return_value = Categoria(
        id=1, nombre="Microscopios", descripcion="Óptica", plazo_entrega=30, activo=True
    )

    response = client.get("/api/categorias/1")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["nombre"] == "Microscopios"


def test_endpoint_obtener_categoria_por_id_no_encontrada(mock_service):
    mock_service.obtener_categoria_por_id.side_effect = CategoriaNotFoundError(99)

    response = client.get("/api/categorias/99")

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no encontrada" in response.json()["detail"]


# =========================================================================
# Pruebas de Endpoints PUT /api/categorias/{id}
# =========================================================================

def test_endpoint_actualizar_categoria_exito(mock_service):
    mock_service.actualizar_categoria.return_value = Categoria(
        id=1, nombre="Laptops Pro", descripcion="Actualizado", plazo_entrega=20, activo=True
    )

    payload = {"nombre": "Laptops Pro", "descripcion": "Actualizado", "plazo_entrega": 20}
    response = client.put("/api/categorias/1", json=payload)

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["nombre"] == "Laptops Pro"
    assert data["plazo_entrega"] == 20


def test_endpoint_actualizar_categoria_no_encontrada(mock_service):
    mock_service.actualizar_categoria.side_effect = CategoriaNotFoundError(88)

    response = client.put("/api/categorias/88", json={"nombre": "Nuevo"})

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_endpoint_actualizar_categoria_nombre_duplicado(mock_service):
    mock_service.actualizar_categoria.side_effect = CategoriaAlreadyExistsError("Duplicado")

    response = client.put("/api/categorias/1", json={"nombre": "Duplicado"})

    assert response.status_code == status.HTTP_400_BAD_REQUEST


# =========================================================================
# Pruebas de Endpoints DELETE /api/categorias/{id}
# =========================================================================

def test_endpoint_eliminar_categoria_logico_exito(mock_service):
    mock_service.eliminar_categoria_logica.return_value = Categoria(
        id=1, nombre="Obsoletos", descripcion=None, plazo_entrega=5, activo=False
    )

    response = client.delete("/api/categorias/1")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == 1
    assert data["activo"] is False


def test_endpoint_eliminar_categoria_no_encontrada(mock_service):
    mock_service.eliminar_categoria_logica.side_effect = CategoriaNotFoundError(999)

    response = client.delete("/api/categorias/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
