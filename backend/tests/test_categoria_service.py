from unittest.mock import create_autospec
import pytest

from app.models.categoria import Categoria
from app.repositories.categoria_repository import CategoriaRepository
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate
from app.services.categoria_service import (
    CategoriaAlreadyExistsError,
    CategoriaNotFoundError,
    CategoriaService,
    CategoriaValidationError,
)


@pytest.fixture
def mock_repository():
    """Fixture que crea un mock tipado del repositorio de Categoría."""
    return create_autospec(CategoriaRepository, instance=True)


@pytest.fixture
def service(mock_repository):
    """Fixture que instancia CategoriaService con el repositorio mockeado."""
    return CategoriaService(repository=mock_repository)


# =========================================================================
# 1. Pruebas de Creación (RN-CAT-01, RN-CAT-02, RN-CAT-03)
# =========================================================================

def test_crear_categoria_exito(service, mock_repository):
    """Verifica que una categoría válida se cree y persista exitosamente."""
    datos = CategoriaCreate(
        nombre="Equipos de Cómputo",
        descripcion="Laptops y periféricos",
        plazo_entrega=15,
    )
    mock_repository.get_by_nombre.return_value = None

    def simular_creacion(cat: Categoria) -> Categoria:
        cat.id = 1
        return cat

    mock_repository.create.side_effect = simular_creacion

    resultado = service.crear_categoria(datos)

    assert resultado.id == 1
    assert resultado.nombre == "Equipos de Cómputo"
    assert resultado.descripcion == "Laptops y periféricos"
    assert resultado.plazo_entrega == 15
    assert resultado.activo is True
    mock_repository.get_by_nombre.assert_called_once_with("Equipos de Cómputo")
    mock_repository.create.assert_called_once()


def test_crear_categoria_nombre_duplicado(service, mock_repository):
    """RN-CAT-03: Rechaza la creación si ya existe una categoría con el mismo nombre."""
    datos = CategoriaCreate(
        nombre="Audio y Video",
        descripcion=None,
        plazo_entrega=7,
    )
    mock_repository.get_by_nombre.return_value = Categoria(
        id=2, nombre="Audio y Video", plazo_entrega=7, activo=True
    )

    with pytest.raises(CategoriaAlreadyExistsError) as exc_info:
        service.crear_categoria(datos)

    assert "Audio y Video" in str(exc_info.value)
    mock_repository.create.assert_not_called()


def test_crear_categoria_plazo_menor_a_1(service, mock_repository):
    """RN-CAT-01: Rechaza plazos menores a 1 día calendario."""
    # Instanciamos manualmente sin validación Pydantic para probar la regla de dominio del Service
    datos = CategoriaCreate.model_construct(
        nombre="Microscopios",
        descripcion=None,
        plazo_entrega=0,
    )
    mock_repository.get_by_nombre.return_value = None

    with pytest.raises(CategoriaValidationError) as exc_info:
        service.crear_categoria(datos)

    assert "El plazo de entrega debe estar entre 1 y 180" in str(exc_info.value)
    mock_repository.create.assert_not_called()


def test_crear_categoria_plazo_mayor_a_180(service, mock_repository):
    """RN-CAT-01 / SUP-04: Rechaza plazos superiores a 180 días (6 meses)."""
    datos = CategoriaCreate.model_construct(
        nombre="Herramientas Pesadas",
        descripcion=None,
        plazo_entrega=181,
    )
    mock_repository.get_by_nombre.return_value = None

    with pytest.raises(CategoriaValidationError) as exc_info:
        service.crear_categoria(datos)

    assert "El plazo de entrega debe estar entre 1 y 180" in str(exc_info.value)
    mock_repository.create.assert_not_called()


def test_crear_categoria_nombre_vacio(service, mock_repository):
    """RN-CAT-02: Rechaza nombres vacíos o que solo contienen espacios."""
    datos = CategoriaCreate.model_construct(
        nombre="   ",
        descripcion=None,
        plazo_entrega=10,
    )

    with pytest.raises(CategoriaValidationError) as exc_info:
        service.crear_categoria(datos)

    assert "El nombre de la categoría es obligatorio" in str(exc_info.value)
    mock_repository.create.assert_not_called()


# =========================================================================
# 2. Pruebas de Lectura y Listado (RN-CAT-04)
# =========================================================================

def test_obtener_categoria_por_id_exito(service, mock_repository):
    """Verifica la consulta exitosa por ID existente."""
    categoria_esperada = Categoria(
        id=10, nombre="Redes", descripcion="Routers y switches", plazo_entrega=30, activo=True
    )
    mock_repository.get_by_id.return_value = categoria_esperada

    resultado = service.obtener_categoria_por_id(10)

    assert resultado.id == 10
    assert resultado.nombre == "Redes"
    mock_repository.get_by_id.assert_called_once_with(10)


def test_obtener_categoria_por_id_no_encontrada(service, mock_repository):
    """RN-CAT-04: Lanza CategoriaNotFoundError si no existe la categoría consultada."""
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CategoriaNotFoundError) as exc_info:
        service.obtener_categoria_por_id(999)

    assert exc_info.value.categoria_id == 999


def test_listar_categorias(service, mock_repository):
    """Verifica el listado de categorías filtrado por activas o todas."""
    lista = [
        Categoria(id=1, nombre="Cat 1", plazo_entrega=5, activo=True),
        Categoria(id=2, nombre="Cat 2", plazo_entrega=10, activo=True),
    ]
    mock_repository.get_all.return_value = lista

    resultado = service.listar_categorias(solo_activas=True)

    assert len(resultado) == 2
    mock_repository.get_all.assert_called_once_with(solo_activas=True)


# =========================================================================
# 3. Pruebas de Actualización (RN-CAT-01, RN-CAT-02, RN-CAT-03, RN-CAT-04, RN-CAT-06)
# =========================================================================

def test_actualizar_categoria_exito(service, mock_repository):
    """Verifica actualización correcta de campos y persistencia."""
    categoria_actual = Categoria(
        id=5, nombre="Sensores", descripcion="Sensores varios", plazo_entrega=14, activo=True
    )
    mock_repository.get_by_id.return_value = categoria_actual
    mock_repository.get_by_nombre.return_value = None
    mock_repository.update.side_effect = lambda c: c

    datos = CategoriaUpdate(
        nombre="Sensores e IoT",
        descripcion="Sensores analógicos y digitales para IoT",
        plazo_entrega=20,
    )

    resultado = service.actualizar_categoria(5, datos)

    assert resultado.nombre == "Sensores e IoT"
    assert resultado.descripcion == "Sensores analógicos y digitales para IoT"
    assert resultado.plazo_entrega == 20
    mock_repository.update.assert_called_once_with(categoria_actual)


def test_actualizar_categoria_no_encontrada(service, mock_repository):
    """RN-CAT-04: Lanza CategoriaNotFoundError al intentar actualizar una categoría inexistente."""
    mock_repository.get_by_id.return_value = None
    datos = CategoriaUpdate(nombre="Nuevo Nombre")

    with pytest.raises(CategoriaNotFoundError):
        service.actualizar_categoria(888, datos)

    mock_repository.update.assert_not_called()


def test_actualizar_categoria_nombre_duplicado(service, mock_repository):
    """RN-CAT-03: Rechaza la actualización si el nuevo nombre ya está asignado a otra categoría."""
    categoria_actual = Categoria(
        id=3, nombre="Cables", descripcion=None, plazo_entrega=7, activo=True
    )
    otra_categoria = Categoria(
        id=4, nombre="Conectores", descripcion=None, plazo_entrega=7, activo=True
    )
    mock_repository.get_by_id.return_value = categoria_actual
    mock_repository.get_by_nombre.return_value = otra_categoria

    datos = CategoriaUpdate(nombre="Conectores")

    with pytest.raises(CategoriaAlreadyExistsError) as exc_info:
        service.actualizar_categoria(3, datos)

    assert "Conectores" in str(exc_info.value)
    mock_repository.update.assert_not_called()


def test_actualizar_categoria_plazo_invalido(service, mock_repository):
    """RN-CAT-01: Rechaza actualización con plazo fuera de los límites (1 a 180 días)."""
    categoria_actual = Categoria(
        id=1, nombre="Robótica", descripcion=None, plazo_entrega=30, activo=True
    )
    mock_repository.get_by_id.return_value = categoria_actual

    datos_bajo = CategoriaUpdate.model_construct(plazo_entrega=0)
    with pytest.raises(CategoriaValidationError):
        service.actualizar_categoria(1, datos_bajo)

    datos_alto = CategoriaUpdate.model_construct(plazo_entrega=200)
    with pytest.raises(CategoriaValidationError):
        service.actualizar_categoria(1, datos_alto)

    mock_repository.update.assert_not_called()


# =========================================================================
# 4. Pruebas de Eliminación Lógica (RN-CAT-04, RN-CAT-05)
# =========================================================================

def test_eliminar_categoria_logico_exito(service, mock_repository):
    """RN-CAT-05: Verifica que la eliminación lógica delegue y marque activo = False."""
    categoria = Categoria(
        id=7, nombre="Química", descripcion=None, plazo_entrega=10, activo=True
    )
    mock_repository.get_by_id.return_value = categoria

    def simular_delete_logico(cat: Categoria) -> Categoria:
        cat.activo = False
        return cat

    mock_repository.delete_logical.side_effect = simular_delete_logico

    resultado = service.eliminar_categoria_logica(7)

    assert resultado.id == 7
    assert resultado.activo is False
    mock_repository.get_by_id.assert_called_once_with(7)
    mock_repository.delete_logical.assert_called_once_with(categoria)


def test_eliminar_categoria_no_encontrada(service, mock_repository):
    """RN-CAT-04: Lanza CategoriaNotFoundError al intentar eliminar una categoría inexistente."""
    mock_repository.get_by_id.return_value = None

    with pytest.raises(CategoriaNotFoundError):
        service.eliminar_categoria_logica(99)

    mock_repository.delete_logical.assert_not_called()
