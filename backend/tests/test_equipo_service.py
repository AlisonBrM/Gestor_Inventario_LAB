from datetime import date
from unittest.mock import create_autospec
import pytest

from app.models.categoria import Categoria
from app.models.equipo import Equipo
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.equipo_repository import EquipoRepository
from app.schemas.equipo import EquipoCreate, EquipoUpdate
from app.services.equipo_service import (
    EquipoAlreadyExistsError,
    EquipoNotFoundError,
    EquipoService,
    EquipoValidationError,
)


@pytest.fixture
def mock_equipo_repository():
    """Fixture que crea un mock tipado del repositorio de Equipo."""
    return create_autospec(EquipoRepository, instance=True)


@pytest.fixture
def mock_categoria_repository():
    """Fixture que crea un mock tipado del repositorio de Categoría."""
    return create_autospec(CategoriaRepository, instance=True)


@pytest.fixture
def service(mock_equipo_repository, mock_categoria_repository):
    """Fixture que instancia EquipoService con los repositorios mockeados."""
    return EquipoService(
        repository=mock_equipo_repository,
        categoria_repository=mock_categoria_repository,
    )


# =========================================================================
# 1. Pruebas de Creación (RN-EQ-01, RN-EQ-02, RN-EQ-03, RN-EQ-04)
# =========================================================================

def test_crear_equipo_exito(service, mock_equipo_repository, mock_categoria_repository):
    """Verifica que un equipo válido se cree con valores por defecto y persista."""
    mock_categoria_repository.get_by_id.return_value = Categoria(
        id=1, nombre="Cómputo", plazo_entrega=15, activo=True
    )
    mock_equipo_repository.get_by_secuencial.return_value = None

    def simular_creacion(eq: Equipo) -> Equipo:
        eq.id = 1
        return eq

    mock_equipo_repository.create.side_effect = simular_creacion

    datos = EquipoCreate(
        id_categoria=1,
        nombre="Laptop Dell Latitude",
        secuencial="EQ-001",
        descripcion="Core i7, 16GB RAM",
    )

    resultado = service.crear_equipo(datos)

    assert resultado.id == 1
    assert resultado.nombre == "Laptop Dell Latitude"
    assert resultado.secuencial == "EQ-001"
    assert resultado.descripcion == "Core i7, 16GB RAM"
    assert resultado.mantenimiento is False  # RN-EQ-03
    assert resultado.activo is True          # RN-EQ-03
    assert resultado.fecha_creacion == date.today()  # RN-EQ-03

    mock_categoria_repository.get_by_id.assert_called_once_with(1)
    mock_equipo_repository.get_by_secuencial.assert_called_once_with("EQ-001")
    mock_equipo_repository.create.assert_called_once()


def test_crear_equipo_categoria_no_existe(service, mock_equipo_repository, mock_categoria_repository):
    """RN-EQ-01: Rechaza creación si la categoría no existe."""
    mock_categoria_repository.get_by_id.return_value = None

    datos = EquipoCreate(
        id_categoria=999,
        nombre="Proyector Epson",
        secuencial="EQ-002",
    )

    with pytest.raises(EquipoValidationError) as exc_info:
        service.crear_equipo(datos)

    assert "categoría con ID 999 no existe" in str(exc_info.value)
    mock_equipo_repository.create.assert_not_called()


def test_crear_equipo_categoria_inactiva(service, mock_equipo_repository, mock_categoria_repository):
    """RN-EQ-01: Rechaza creación si la categoría existe pero está inactiva."""
    mock_categoria_repository.get_by_id.return_value = Categoria(
        id=2, nombre="Equipos Antiguos", plazo_entrega=10, activo=False
    )

    datos = EquipoCreate(
        id_categoria=2,
        nombre="Monitor CRT",
        secuencial="EQ-003",
    )

    with pytest.raises(EquipoValidationError) as exc_info:
        service.crear_equipo(datos)

    assert "se encuentra inactiva" in str(exc_info.value)
    mock_equipo_repository.create.assert_not_called()


def test_crear_equipo_secuencial_duplicado(service, mock_equipo_repository, mock_categoria_repository):
    """RN-EQ-02: Rechaza creación si ya existe un equipo con el mismo secuencial."""
    mock_categoria_repository.get_by_id.return_value = Categoria(
        id=1, nombre="Cómputo", plazo_entrega=15, activo=True
    )
    mock_equipo_repository.get_by_secuencial.return_value = Equipo(
        id=5, id_categoria=1, nombre="Existente", secuencial="EQ-001", activo=True
    )

    datos = EquipoCreate(
        id_categoria=1,
        nombre="Otro Equipo",
        secuencial="EQ-001",
    )

    with pytest.raises(EquipoAlreadyExistsError) as exc_info:
        service.crear_equipo(datos)

    assert "EQ-001" in str(exc_info.value)
    mock_equipo_repository.create.assert_not_called()


def test_crear_equipo_nombre_vacio(service, mock_equipo_repository, mock_categoria_repository):
    """RN-EQ-04: Rechaza nombres vacíos o de puros espacios."""
    datos = EquipoCreate.model_construct(
        id_categoria=1,
        nombre="   ",
        secuencial="EQ-004",
    )

    with pytest.raises(EquipoValidationError) as exc_info:
        service.crear_equipo(datos)

    assert "El campo 'nombre' es obligatorio" in str(exc_info.value)
    mock_equipo_repository.create.assert_not_called()


def test_crear_equipo_secuencial_vacio(service, mock_equipo_repository, mock_categoria_repository):
    """RN-EQ-04: Rechaza secuenciales vacíos o de puros espacios."""
    datos = EquipoCreate.model_construct(
        id_categoria=1,
        nombre="Multímetro",
        secuencial="   ",
    )

    with pytest.raises(EquipoValidationError) as exc_info:
        service.crear_equipo(datos)

    assert "El campo 'secuencial' es obligatorio" in str(exc_info.value)
    mock_equipo_repository.create.assert_not_called()


# =========================================================================
# 2. Pruebas de Lectura y Listado
# =========================================================================

def test_obtener_equipo_por_id_exito(service, mock_equipo_repository):
    """Verifica consulta exitosa por ID existente."""
    equipo = Equipo(
        id=10, id_categoria=1, nombre="Osciloscopio", secuencial="OSC-01", activo=True
    )
    mock_equipo_repository.get_by_id.return_value = equipo

    resultado = service.obtener_equipo_por_id(10)

    assert resultado.id == 10
    assert resultado.secuencial == "OSC-01"
    mock_equipo_repository.get_by_id.assert_called_once_with(10)


def test_obtener_equipo_por_id_no_encontrado(service, mock_equipo_repository):
    """Lanza EquipoNotFoundError si el ID no existe."""
    mock_equipo_repository.get_by_id.return_value = None

    with pytest.raises(EquipoNotFoundError) as exc_info:
        service.obtener_equipo_por_id(999)

    assert exc_info.value.equipo_id == 999


def test_listar_equipos_filtros(service, mock_equipo_repository):
    """Verifica que los filtros se pasen correctamente al repositorio."""
    lista = [
        Equipo(id=1, id_categoria=1, nombre="Eq 1", secuencial="E-1", activo=True),
        Equipo(id=2, id_categoria=1, nombre="Eq 2", secuencial="E-2", activo=True),
    ]
    mock_equipo_repository.get_all.return_value = lista

    resultado = service.listar_equipos(solo_activos=True, id_categoria=1, en_mantenimiento=False)

    assert len(resultado) == 2
    mock_equipo_repository.get_all.assert_called_once_with(
        solo_activos=True, id_categoria=1, en_mantenimiento=False
    )


# =========================================================================
# 3. Pruebas de Actualización (RN-EQ-01, RN-EQ-02, RN-EQ-05)
# =========================================================================

def test_actualizar_equipo_exito(service, mock_equipo_repository, mock_categoria_repository):
    """Verifica actualización exitosa de datos y estado de mantenimiento."""
    equipo_actual = Equipo(
        id=1,
        id_categoria=1,
        nombre="Impresora 3D",
        secuencial="IMP-01",
        descripcion="Original",
        mantenimiento=False,
        activo=True,
    )
    mock_equipo_repository.get_by_id.return_value = equipo_actual
    mock_equipo_repository.update.side_effect = lambda e: e

    datos = EquipoUpdate(
        nombre="Impresora 3D Ender",
        descripcion="Modificada con cama caliente",
        mantenimiento=True,
    )

    resultado = service.actualizar_equipo(1, datos)

    assert resultado.nombre == "Impresora 3D Ender"
    assert resultado.descripcion == "Modificada con cama caliente"
    assert resultado.mantenimiento is True
    mock_equipo_repository.update.assert_called_once_with(equipo_actual)


def test_actualizar_equipo_secuencial_duplicado(service, mock_equipo_repository):
    """RN-EQ-02: Rechaza actualización si el nuevo secuencial ya pertenece a otro equipo."""
    equipo_actual = Equipo(
        id=1, id_categoria=1, nombre="Equipo A", secuencial="SEC-A", activo=True
    )
    otro_equipo = Equipo(
        id=2, id_categoria=1, nombre="Equipo B", secuencial="SEC-B", activo=True
    )
    mock_equipo_repository.get_by_id.return_value = equipo_actual
    mock_equipo_repository.get_by_secuencial.return_value = otro_equipo

    datos = EquipoUpdate(secuencial="SEC-B")

    with pytest.raises(EquipoAlreadyExistsError) as exc_info:
        service.actualizar_equipo(1, datos)

    assert "SEC-B" in str(exc_info.value)
    mock_equipo_repository.update.assert_not_called()


def test_actualizar_equipo_mismo_secuencial(service, mock_equipo_repository):
    """Permite guardar si el secuencial es el mismo del equipo."""
    equipo_actual = Equipo(
        id=1, id_categoria=1, nombre="Equipo A", secuencial="SEC-A", activo=True
    )
    mock_equipo_repository.get_by_id.return_value = equipo_actual
    mock_equipo_repository.update.side_effect = lambda e: e

    datos = EquipoUpdate(secuencial="SEC-A", nombre="Nuevo Nombre")

    resultado = service.actualizar_equipo(1, datos)

    assert resultado.nombre == "Nuevo Nombre"
    mock_equipo_repository.get_by_secuencial.assert_not_called()
    mock_equipo_repository.update.assert_called_once()


def test_actualizar_equipo_cambio_categoria_invalida(service, mock_equipo_repository, mock_categoria_repository):
    """RN-EQ-01: Rechaza cambio a una categoría inexistente."""
    equipo_actual = Equipo(
        id=1, id_categoria=1, nombre="Equipo A", secuencial="SEC-A", activo=True
    )
    mock_equipo_repository.get_by_id.return_value = equipo_actual
    mock_categoria_repository.get_by_id.return_value = None

    datos = EquipoUpdate(id_categoria=99)

    with pytest.raises(EquipoValidationError):
        service.actualizar_equipo(1, datos)

    mock_equipo_repository.update.assert_not_called()


def test_actualizar_equipo_no_encontrado(service, mock_equipo_repository):
    """Lanza EquipoNotFoundError si se intenta actualizar un equipo inexistente."""
    mock_equipo_repository.get_by_id.return_value = None

    with pytest.raises(EquipoNotFoundError):
        service.actualizar_equipo(888, EquipoUpdate(nombre="Test"))

    mock_equipo_repository.update.assert_not_called()


# =========================================================================
# 4. Pruebas de Borrado Lógico y Reactivación (RN-EQ-06)
# =========================================================================

def test_eliminar_equipo_logico_exito(service, mock_equipo_repository):
    """RN-EQ-06: Verifica borrado lógico marcando activo = False."""
    equipo = Equipo(
        id=3, id_categoria=1, nombre="Fuente de Poder", secuencial="FP-01", activo=True
    )
    mock_equipo_repository.get_by_id.return_value = equipo

    def simular_delete_logico(eq: Equipo) -> Equipo:
        eq.activo = False
        return eq

    mock_equipo_repository.delete_logical.side_effect = simular_delete_logico

    resultado = service.eliminar_equipo_logico(3)

    assert resultado.id == 3
    assert resultado.activo is False
    mock_equipo_repository.get_by_id.assert_called_once_with(3)
    mock_equipo_repository.delete_logical.assert_called_once_with(equipo)


def test_eliminar_equipo_logico_no_encontrado(service, mock_equipo_repository):
    """Lanza EquipoNotFoundError si no existe el equipo a eliminar."""
    mock_equipo_repository.get_by_id.return_value = None

    with pytest.raises(EquipoNotFoundError):
        service.eliminar_equipo_logico(777)

    mock_equipo_repository.delete_logical.assert_not_called()


def test_reactivar_equipo(service, mock_equipo_repository):
    """Verifica que se pueda reactivar un equipo inactivo pasando activo = True."""
    equipo = Equipo(
        id=4, id_categoria=1, nombre="Osciloscopio", secuencial="OSC-02", activo=False
    )
    mock_equipo_repository.get_by_id.return_value = equipo
    mock_equipo_repository.update.side_effect = lambda e: e

    datos = EquipoUpdate(activo=True)
    resultado = service.actualizar_equipo(4, datos)

    assert resultado.activo is True
    mock_equipo_repository.update.assert_called_once_with(equipo)
