from datetime import date, timedelta
from unittest.mock import create_autospec
import pytest

from app.models.categoria import Categoria
from app.models.devolucion import Devolucion
from app.models.equipo import Equipo
from app.models.persona import Persona
from app.models.prestamo import Prestamo
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.equipo_repository import EquipoRepository
from app.repositories.persona_repository import PersonaRepository
from app.repositories.prestamo_repository import PrestamoRepository
from app.schemas.devolucion import DevolucionCreate
from app.schemas.prestamo import PrestamoCreate
from app.services.prestamo_service import (
    PrestamoNotFoundError,
    PrestamoService,
    PrestamoValidationError,
)


@pytest.fixture
def mock_prestamo_repo():
    return create_autospec(PrestamoRepository, instance=True)


@pytest.fixture
def mock_persona_repo():
    return create_autospec(PersonaRepository, instance=True)


@pytest.fixture
def mock_equipo_repo():
    return create_autospec(EquipoRepository, instance=True)


@pytest.fixture
def mock_categoria_repo():
    return create_autospec(CategoriaRepository, instance=True)


@pytest.fixture
def service(mock_prestamo_repo, mock_persona_repo, mock_equipo_repo, mock_categoria_repo):
    return PrestamoService(
        prestamo_repository=mock_prestamo_repo,
        persona_repository=mock_persona_repo,
        equipo_repository=mock_equipo_repo,
        categoria_repository=mock_categoria_repo,
    )


# =========================================================================
# 1. Pruebas de Creación Exitosa y Cálculo de Fechas (RN-PREST-05)
# =========================================================================

def test_crear_prestamo_exitoso(
    service, mock_prestamo_repo, mock_persona_repo, mock_equipo_repo, mock_categoria_repo
):
    """Verifica que un préstamo válido se crea calculando fecha_devolucion_esperada."""
    hoy = date.today()
    mock_persona_repo.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Carlos Pérez",
        tipo_persona="estudiante",
        telefono="3001234567",
        facultad="Ingeniería",
        activo=True,
    )
    mock_prestamo_repo.get_prestamos_no_devueltos_por_persona.return_value = []
    mock_equipo_repo.get_by_id.return_value = Equipo(
        id=1,
        id_categoria=2,
        nombre="Osciloscopio",
        secuencial="OSC-01",
        mantenimiento=False,
        activo=True,
    )
    mock_prestamo_repo.get_prestamo_activo_por_equipo.return_value = None
    mock_categoria_repo.get_by_id.return_value = Categoria(
        id=2, nombre="Electrónica", plazo_entrega=15, activo=True
    )

    def simular_creacion(prestamo: Prestamo) -> Prestamo:
        prestamo.id = 10
        return prestamo

    mock_prestamo_repo.create.side_effect = simular_creacion

    datos = PrestamoCreate(cedula_persona="1001234567", id_equipo=1, fecha_prestamo=hoy)
    resultado = service.crear_prestamo(datos)

    assert resultado.id == 10
    assert resultado.cedula_persona == "1001234567"
    assert resultado.id_equipo == 1
    assert resultado.fecha_prestamo == hoy
    assert resultado.fecha_devolucion_esperada == hoy + timedelta(days=15)
    mock_prestamo_repo.create.assert_called_once()


# =========================================================================
# 2. RN-PREST-01: Préstamo vencido sin devolver
# =========================================================================

def test_crear_prestamo_rechaza_solicitante_con_prestamo_vencido_sin_devolver(
    service, mock_prestamo_repo, mock_persona_repo
):
    """RN-PREST-01: Rechaza el préstamo si el solicitante tiene un préstamo vencido no devuelto."""
    hoy = date.today()
    mock_persona_repo.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Carlos Pérez",
        tipo_persona="estudiante",
        telefono="3001234567",
        facultad="Ingeniería",
        activo=True,
    )

    prestamo_vencido = Prestamo(
        id=5,
        cedula_persona="1001234567",
        id_equipo=2,
        fecha_prestamo=hoy - timedelta(days=30),
        fecha_devolucion_esperada=hoy - timedelta(days=10),
    )
    mock_prestamo_repo.get_prestamos_no_devueltos_por_persona.return_value = [prestamo_vencido]

    datos = PrestamoCreate(cedula_persona="1001234567", id_equipo=1, fecha_prestamo=hoy)

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.crear_prestamo(datos)

    assert "préstamo vencido sin devolver" in str(exc_info.value)
    mock_prestamo_repo.create.assert_not_called()


def test_crear_prestamo_permite_si_prestamos_vencidos_fueron_devueltos(
    service, mock_prestamo_repo, mock_persona_repo, mock_equipo_repo, mock_categoria_repo
):
    """Permite el préstamo si los préstamos previos ya fueron devueltos."""
    hoy = date.today()
    mock_persona_repo.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Carlos Pérez",
        tipo_persona="estudiante",
        telefono="3001234567",
        facultad="Ingeniería",
        activo=True,
    )
    # Lista vacía porque todos los anteriores fueron devueltos
    mock_prestamo_repo.get_prestamos_no_devueltos_por_persona.return_value = []
    mock_equipo_repo.get_by_id.return_value = Equipo(
        id=1, id_categoria=1, nombre="Multímetro", secuencial="MUL-01", mantenimiento=False, activo=True
    )
    mock_prestamo_repo.get_prestamo_activo_por_equipo.return_value = None
    mock_categoria_repo.get_by_id.return_value = Categoria(
        id=1, nombre="General", plazo_entrega=7, activo=True
    )
    mock_prestamo_repo.create.side_effect = lambda p: p

    datos = PrestamoCreate(cedula_persona="1001234567", id_equipo=1, fecha_prestamo=hoy)
    resultado = service.crear_prestamo(datos)

    assert resultado.fecha_devolucion_esperada == hoy + timedelta(days=7)


def test_crear_prestamo_permite_si_prestamos_vigentes_no_estan_vencidos(
    service, mock_prestamo_repo, mock_persona_repo, mock_equipo_repo, mock_categoria_repo
):
    """Permite el préstamo si el solicitante tiene un préstamo activo que todavía no ha vencido."""
    hoy = date.today()
    mock_persona_repo.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Carlos Pérez",
        tipo_persona="estudiante",
        telefono="3001234567",
        facultad="Ingeniería",
        activo=True,
    )

    prestamo_vigente = Prestamo(
        id=3,
        cedula_persona="1001234567",
        id_equipo=2,
        fecha_prestamo=hoy - timedelta(days=2),
        fecha_devolucion_esperada=hoy + timedelta(days=5),
    )
    mock_prestamo_repo.get_prestamos_no_devueltos_por_persona.return_value = [prestamo_vigente]
    mock_equipo_repo.get_by_id.return_value = Equipo(
        id=1, id_categoria=1, nombre="Multímetro", secuencial="MUL-01", mantenimiento=False, activo=True
    )
    mock_prestamo_repo.get_prestamo_activo_por_equipo.return_value = None
    mock_categoria_repo.get_by_id.return_value = Categoria(
        id=1, nombre="General", plazo_entrega=7, activo=True
    )
    mock_prestamo_repo.create.side_effect = lambda p: p

    datos = PrestamoCreate(cedula_persona="1001234567", id_equipo=1, fecha_prestamo=hoy)
    resultado = service.crear_prestamo(datos)

    assert resultado.fecha_devolucion_esperada == hoy + timedelta(days=7)


# =========================================================================
# 3. RN-PREST-02: Equipo marcado en mantenimiento
# =========================================================================

def test_crear_prestamo_rechaza_equipo_en_mantenimiento(
    service, mock_prestamo_repo, mock_persona_repo, mock_equipo_repo
):
    """RN-PREST-02: Rechaza prestar un equipo marcado en mantenimiento."""
    mock_persona_repo.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Carlos Pérez",
        tipo_persona="estudiante",
        telefono="3001234567",
        facultad="Ingeniería",
        activo=True,
    )
    mock_prestamo_repo.get_prestamos_no_devueltos_por_persona.return_value = []
    mock_equipo_repo.get_by_id.return_value = Equipo(
        id=1,
        id_categoria=1,
        nombre="Generador de Señales",
        secuencial="GEN-01",
        mantenimiento=True,
        activo=True,
    )

    datos = PrestamoCreate(cedula_persona="1001234567", id_equipo=1)

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.crear_prestamo(datos)

    assert "mantenimiento" in str(exc_info.value)
    mock_prestamo_repo.create.assert_not_called()


# =========================================================================
# 4. RN-PREST-03: Disponibilidad de equipo (ya prestado)
# =========================================================================

def test_crear_prestamo_rechaza_equipo_ya_prestado(
    service, mock_prestamo_repo, mock_persona_repo, mock_equipo_repo
):
    """RN-PREST-03: Rechaza si el equipo ya está prestado a alguien y no ha sido devuelto."""
    hoy = date.today()
    mock_persona_repo.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Carlos Pérez",
        tipo_persona="estudiante",
        telefono="3001234567",
        facultad="Ingeniería",
        activo=True,
    )
    mock_prestamo_repo.get_prestamos_no_devueltos_por_persona.return_value = []
    mock_equipo_repo.get_by_id.return_value = Equipo(
        id=1,
        id_categoria=1,
        nombre="Fuente de Poder",
        secuencial="FTE-01",
        mantenimiento=False,
        activo=True,
    )
    mock_prestamo_repo.get_prestamo_activo_por_equipo.return_value = Prestamo(
        id=99,
        cedula_persona="99999999",
        id_equipo=1,
        fecha_prestamo=hoy - timedelta(days=2),
        fecha_devolucion_esperada=hoy + timedelta(days=5),
    )

    datos = PrestamoCreate(cedula_persona="1001234567", id_equipo=1)

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.crear_prestamo(datos)

    assert "ya se encuentra actualmente prestado" in str(exc_info.value)
    mock_prestamo_repo.create.assert_not_called()


# =========================================================================
# 5. RN-PREST-04: Estados y Existencias de Persona, Equipo y Categoría
# =========================================================================

def test_crear_prestamo_rechaza_persona_inexistente(service, mock_persona_repo):
    """RN-PREST-04: Lanza PrestamoNotFoundError si la cédula no existe."""
    mock_persona_repo.get_by_cedula.return_value = None
    datos = PrestamoCreate(cedula_persona="00000000", id_equipo=1)

    with pytest.raises(PrestamoNotFoundError):
        service.crear_prestamo(datos)


def test_crear_prestamo_rechaza_persona_inactiva(service, mock_persona_repo):
    """RN-PREST-04: Lanza PrestamoValidationError si la persona está inactiva."""
    mock_persona_repo.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Persona Inactiva",
        tipo_persona="estudiante",
        telefono="3001234567",
        facultad="Ingeniería",
        activo=False,
    )
    datos = PrestamoCreate(cedula_persona="1001234567", id_equipo=1)

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.crear_prestamo(datos)

    assert "inactiva" in str(exc_info.value)


def test_crear_prestamo_rechaza_equipo_inexistente(
    service, mock_prestamo_repo, mock_persona_repo, mock_equipo_repo
):
    """RN-PREST-04: Lanza PrestamoNotFoundError si el equipo no existe."""
    mock_persona_repo.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Carlos Pérez",
        tipo_persona="estudiante",
        telefono="3001234567",
        facultad="Ingeniería",
        activo=True,
    )
    mock_prestamo_repo.get_prestamos_no_devueltos_por_persona.return_value = []
    mock_equipo_repo.get_by_id.return_value = None

    datos = PrestamoCreate(cedula_persona="1001234567", id_equipo=999)

    with pytest.raises(PrestamoNotFoundError):
        service.crear_prestamo(datos)


def test_crear_prestamo_rechaza_equipo_inactivo(
    service, mock_prestamo_repo, mock_persona_repo, mock_equipo_repo
):
    """RN-PREST-04: Lanza PrestamoValidationError si el equipo está inactivo."""
    mock_persona_repo.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Carlos Pérez",
        tipo_persona="estudiante",
        telefono="3001234567",
        facultad="Ingeniería",
        activo=True,
    )
    mock_prestamo_repo.get_prestamos_no_devueltos_por_persona.return_value = []
    mock_equipo_repo.get_by_id.return_value = Equipo(
        id=1,
        id_categoria=1,
        nombre="Equipo Inactivo",
        secuencial="INACT-01",
        mantenimiento=False,
        activo=False,
    )

    datos = PrestamoCreate(cedula_persona="1001234567", id_equipo=1)

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.crear_prestamo(datos)

    assert "inactivo" in str(exc_info.value)


def test_crear_prestamo_rechaza_categoria_inactiva(
    service, mock_prestamo_repo, mock_persona_repo, mock_equipo_repo, mock_categoria_repo
):
    """RN-PREST-04: Lanza PrestamoValidationError si la categoría del equipo está inactiva."""
    mock_persona_repo.get_by_cedula.return_value = Persona(
        cedula="1001234567",
        nombre_completo="Carlos Pérez",
        tipo_persona="estudiante",
        telefono="3001234567",
        facultad="Ingeniería",
        activo=True,
    )
    mock_prestamo_repo.get_prestamos_no_devueltos_por_persona.return_value = []
    mock_equipo_repo.get_by_id.return_value = Equipo(
        id=1,
        id_categoria=5,
        nombre="Equipo Válido",
        secuencial="VAL-01",
        mantenimiento=False,
        activo=True,
    )
    mock_prestamo_repo.get_prestamo_activo_por_equipo.return_value = None
    mock_categoria_repo.get_by_id.return_value = Categoria(
        id=5, nombre="Categoría Inactiva", plazo_entrega=10, activo=False
    )

    datos = PrestamoCreate(cedula_persona="1001234567", id_equipo=1)

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.crear_prestamo(datos)

    assert "inactiva" in str(exc_info.value)


# =========================================================================
# 6. RN-PREST-06: Fecha de préstamo futura
# =========================================================================

def test_crear_prestamo_rechaza_fecha_futura(service):
    """RN-PREST-06: Rechaza fechas de préstamo posteriores a la fecha actual."""
    fecha_futura = date.today() + timedelta(days=2)
    datos = PrestamoCreate(
        cedula_persona="1001234567",
        id_equipo=1,
        fecha_prestamo=fecha_futura,
    )

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.crear_prestamo(datos)

    assert "posterior a la fecha actual" in str(exc_info.value)


# =========================================================================
# 7. Obtener Préstamo por ID
# =========================================================================

def test_obtener_prestamo_por_id_exitoso(service, mock_prestamo_repo):
    """Obtiene un préstamo existente por su ID."""
    mock_prestamo = Prestamo(
        id=10,
        cedula_persona="1001234567",
        id_equipo=1,
        fecha_prestamo=date.today(),
        fecha_devolucion_esperada=date.today() + timedelta(days=7),
    )
    mock_prestamo_repo.get_by_id.return_value = mock_prestamo

    resultado = service.obtener_prestamo_por_id(10)
    assert resultado.id == 10
    assert resultado.cedula_persona == "1001234567"


def test_obtener_prestamo_por_id_inexistente(service, mock_prestamo_repo):
    """Lanza PrestamoNotFoundError si el ID no existe."""
    mock_prestamo_repo.get_by_id.return_value = None

    with pytest.raises(PrestamoNotFoundError):
        service.obtener_prestamo_por_id(999)


# =========================================================================
# 8. Listar Préstamos con Filtros (RN-PREST-LIST-01 a 05)
# =========================================================================

def test_listar_prestamos_sin_filtros(service, mock_prestamo_repo):
    """Verifica listar préstamos sin ningún filtro."""
    p1 = Prestamo(id=1, cedula_persona="1001", id_equipo=1, fecha_prestamo=date.today(), fecha_devolucion_esperada=date.today())
    p2 = Prestamo(id=2, cedula_persona="1002", id_equipo=2, fecha_prestamo=date.today(), fecha_devolucion_esperada=date.today())
    mock_prestamo_repo.listar.return_value = [p2, p1]

    resultado = service.listar_prestamos()

    mock_prestamo_repo.listar.assert_called_once_with(
        id_categoria=None,
        fecha_desde=None,
        fecha_hasta=None,
        estado=None,
    )
    assert len(resultado) == 2
    assert resultado[0].id == 2


def test_listar_prestamos_filtro_categoria(service, mock_prestamo_repo):
    """Verifica listar préstamos filtrando por categoría."""
    mock_prestamo_repo.listar.return_value = []

    resultado = service.listar_prestamos(id_categoria=3)

    mock_prestamo_repo.listar.assert_called_once_with(
        id_categoria=3,
        fecha_desde=None,
        fecha_hasta=None,
        estado=None,
    )
    assert resultado == []


def test_listar_prestamos_filtro_rango_fechas_valido(service, mock_prestamo_repo):
    """RN-PREST-LIST-01: Verifica rango de fechas válido fecha_desde <= fecha_hasta."""
    f_desde = date(2026, 9, 1)
    f_hasta = date(2026, 9, 15)
    mock_prestamo_repo.listar.return_value = []

    service.listar_prestamos(fecha_desde=f_desde, fecha_hasta=f_hasta)

    mock_prestamo_repo.listar.assert_called_once_with(
        id_categoria=None,
        fecha_desde=f_desde,
        fecha_hasta=f_hasta,
        estado=None,
    )


def test_listar_prestamos_error_rango_fechas_invalido(service, mock_prestamo_repo):
    """RN-PREST-LIST-01: Rechaza fecha_desde posterior a fecha_hasta."""
    f_desde = date(2026, 9, 20)
    f_hasta = date(2026, 9, 10)

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.listar_prestamos(fecha_desde=f_desde, fecha_hasta=f_hasta)

    assert "no puede ser posterior a la fecha final" in str(exc_info.value)
    mock_prestamo_repo.listar.assert_not_called()


def test_listar_prestamos_filtro_estado_vigente(service, mock_prestamo_repo):
    """RN-PREST-LIST-02: Filtra por estado 'vigente' normalizado."""
    mock_prestamo_repo.listar.return_value = []

    service.listar_prestamos(estado="Vigente ")

    mock_prestamo_repo.listar.assert_called_once_with(
        id_categoria=None,
        fecha_desde=None,
        fecha_hasta=None,
        estado="vigente",
    )


def test_listar_prestamos_filtro_estado_vencido(service, mock_prestamo_repo):
    """RN-PREST-LIST-02: Filtra por estado 'vencido' normalizado."""
    mock_prestamo_repo.listar.return_value = []

    service.listar_prestamos(estado=" VENCIDO")

    mock_prestamo_repo.listar.assert_called_once_with(
        id_categoria=None,
        fecha_desde=None,
        fecha_hasta=None,
        estado="vencido",
    )


def test_listar_prestamos_error_estado_invalido(service, mock_prestamo_repo):
    """RN-PREST-LIST-02: Rechaza estados no válidos."""
    with pytest.raises(PrestamoValidationError) as exc_info:
        service.listar_prestamos(estado="otro_estado")

    assert "El estado debe ser 'vigente' o 'vencido'" in str(exc_info.value)
    mock_prestamo_repo.listar.assert_not_called()


def test_listar_prestamos_error_id_categoria_invalido(service, mock_prestamo_repo):
    """RN-PREST-LIST-03: Rechaza id_categoria <= 0."""
    with pytest.raises(PrestamoValidationError) as exc_info:
        service.listar_prestamos(id_categoria=0)

    assert "entero positivo" in str(exc_info.value)

    with pytest.raises(PrestamoValidationError) as exc_info2:
        service.listar_prestamos(id_categoria=-5)

    assert "entero positivo" in str(exc_info2.value)
    mock_prestamo_repo.listar.assert_not_called()


def test_listar_prestamos_combinacion_filtros(service, mock_prestamo_repo):
    """Verifica la combinación simultánea de filtros."""
    f_desde = date(2026, 9, 1)
    f_hasta = date(2026, 9, 30)
    mock_prestamo_repo.listar.return_value = []

    service.listar_prestamos(
        id_categoria=2,
        fecha_desde=f_desde,
        fecha_hasta=f_hasta,
        estado="vigente",
    )

    mock_prestamo_repo.listar.assert_called_once_with(
        id_categoria=2,
        fecha_desde=f_desde,
        fecha_hasta=f_hasta,
        estado="vigente",
    )


# =========================================================================
# 5. Pruebas de Registro de Devolución (RN-DEV-01 a RN-DEV-06)
# =========================================================================

def test_registrar_devolucion_exitosa_sin_mantenimiento(
    service, mock_prestamo_repo, mock_equipo_repo
):
    """RN-DEV-01 a RN-DEV-06: Devolución exitosa de un equipo que se entrega operativo sin novedades."""
    hoy = date.today()
    prestamo = Prestamo(
        id=1,
        cedula_persona="1001234567",
        id_equipo=10,
        fecha_prestamo=hoy - timedelta(days=5),
        fecha_devolucion_esperada=hoy + timedelta(days=5),
    )
    equipo = Equipo(id=10, nombre="Multímetro Digital", secuencial="EQ-010", mantenimiento=False, id_categoria=1)
    mock_prestamo_repo.get_by_id.return_value = prestamo
    mock_equipo_repo.get_by_id.return_value = equipo

    datos = DevolucionCreate(
        fecha_devolucion=hoy,
        novedades=None,
        enviar_a_mantenimiento=False,
    )

    resultado = service.registrar_devolucion(1, datos)

    assert resultado.devuelto is True
    assert resultado.devolucion is not None
    assert resultado.devolucion.fecha_devolucion == hoy
    assert resultado.devolucion.novedades is None
    assert equipo.mantenimiento is False
    mock_equipo_repo.update.assert_called_once_with(equipo)
    mock_prestamo_repo.create_devolucion.assert_called_once()


def test_registrar_devolucion_exitosa_con_mantenimiento_y_novedades(
    service, mock_prestamo_repo, mock_equipo_repo
):
    """RN-DEV-04, RN-DEV-05: Devolución con envío a mantenimiento y novedades registradas."""
    hoy = date.today()
    prestamo = Prestamo(
        id=2,
        cedula_persona="1001234567",
        id_equipo=10,
        fecha_prestamo=hoy - timedelta(days=3),
        fecha_devolucion_esperada=hoy + timedelta(days=5),
    )
    equipo = Equipo(id=10, nombre="Osciloscopio", secuencial="EQ-020", mantenimiento=False, id_categoria=1)
    mock_prestamo_repo.get_by_id.return_value = prestamo
    mock_equipo_repo.get_by_id.return_value = equipo

    datos = DevolucionCreate(
        fecha_devolucion=hoy,
        novedades="Sonda dañada durante uso en laboratorio.",
        enviar_a_mantenimiento=True,
    )

    resultado = service.registrar_devolucion(2, datos)

    assert resultado.devuelto is True
    assert resultado.devolucion.novedades == "Sonda dañada durante uso en laboratorio."
    assert equipo.mantenimiento is True
    mock_equipo_repo.update.assert_called_once_with(equipo)
    mock_prestamo_repo.create_devolucion.assert_called_once()


def test_registrar_devolucion_fecha_por_defecto_hoy(
    service, mock_prestamo_repo, mock_equipo_repo
):
    """RN-DEV-03: Si fecha_devolucion no se especifica, toma date.today()."""
    hoy = date.today()
    prestamo = Prestamo(
        id=3,
        cedula_persona="1001234567",
        id_equipo=10,
        fecha_prestamo=hoy - timedelta(days=2),
        fecha_devolucion_esperada=hoy + timedelta(days=5),
    )
    equipo = Equipo(id=10, nombre="Osciloscopio", secuencial="EQ-020", mantenimiento=False, id_categoria=1)
    mock_prestamo_repo.get_by_id.return_value = prestamo
    mock_equipo_repo.get_by_id.return_value = equipo

    datos = DevolucionCreate(
        fecha_devolucion=None,
        novedades="Todo en orden",
        enviar_a_mantenimiento=False,
    )

    resultado = service.registrar_devolucion(3, datos)

    assert resultado.devolucion.fecha_devolucion == hoy


def test_registrar_devolucion_prestamo_inexistente_lanza_error(
    service, mock_prestamo_repo
):
    """RN-DEV-01: Lanza PrestamoNotFoundError si el préstamo no existe."""
    mock_prestamo_repo.get_by_id.return_value = None
    datos = DevolucionCreate(enviar_a_mantenimiento=False)

    with pytest.raises(PrestamoNotFoundError) as exc_info:
        service.registrar_devolucion(999, datos)

    assert "999" in str(exc_info.value)


def test_registrar_devolucion_prestamo_ya_devuelto_lanza_error(
    service, mock_prestamo_repo
):
    """RN-DEV-02: Lanza PrestamoValidationError si el préstamo ya fue devuelto."""
    hoy = date.today()
    prestamo = Prestamo(
        id=4,
        cedula_persona="1001234567",
        id_equipo=10,
        fecha_prestamo=hoy - timedelta(days=5),
        fecha_devolucion_esperada=hoy,
    )
    prestamo.devolucion = Devolucion(id_prestamo=4, fecha_devolucion=hoy, novedades=None)
    mock_prestamo_repo.get_by_id.return_value = prestamo

    datos = DevolucionCreate(enviar_a_mantenimiento=False)

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.registrar_devolucion(4, datos)

    assert "ya fue devuelto previamente" in str(exc_info.value)


def test_registrar_devolucion_fecha_futura_lanza_error(
    service, mock_prestamo_repo
):
    """RN-DEV-03: Lanza PrestamoValidationError si la fecha de devolución es futura."""
    hoy = date.today()
    prestamo = Prestamo(
        id=5,
        cedula_persona="1001234567",
        id_equipo=10,
        fecha_prestamo=hoy - timedelta(days=2),
        fecha_devolucion_esperada=hoy + timedelta(days=5),
    )
    mock_prestamo_repo.get_by_id.return_value = prestamo

    datos = DevolucionCreate(
        fecha_devolucion=hoy + timedelta(days=1),
        enviar_a_mantenimiento=False,
    )

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.registrar_devolucion(5, datos)

    assert "no puede ser posterior a la fecha actual" in str(exc_info.value)


def test_registrar_devolucion_fecha_anterior_a_prestamo_lanza_error(
    service, mock_prestamo_repo
):
    """RN-DEV-03: Lanza PrestamoValidationError si la fecha de devolución es anterior al inicio del préstamo."""
    hoy = date.today()
    prestamo = Prestamo(
        id=6,
        cedula_persona="1001234567",
        id_equipo=10,
        fecha_prestamo=hoy - timedelta(days=2),
        fecha_devolucion_esperada=hoy + timedelta(days=5),
    )
    mock_prestamo_repo.get_by_id.return_value = prestamo

    datos = DevolucionCreate(
        fecha_devolucion=hoy - timedelta(days=3),
        enviar_a_mantenimiento=False,
    )

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.registrar_devolucion(6, datos)

    assert "no puede ser anterior a la fecha de inicio del préstamo" in str(exc_info.value)


def test_registrar_devolucion_mantenimiento_sin_novedades_lanza_error(
    service, mock_prestamo_repo
):
    """RN-DEV-04: Lanza PrestamoValidationError si se envía a mantenimiento sin novedades."""
    hoy = date.today()
    prestamo = Prestamo(
        id=7,
        cedula_persona="1001234567",
        id_equipo=10,
        fecha_prestamo=hoy - timedelta(days=2),
        fecha_devolucion_esperada=hoy + timedelta(days=5),
    )
    mock_prestamo_repo.get_by_id.return_value = prestamo

    # Con novedades=None
    datos1 = DevolucionCreate(
        fecha_devolucion=hoy,
        novedades=None,
        enviar_a_mantenimiento=True,
    )
    with pytest.raises(PrestamoValidationError) as exc_info1:
        service.registrar_devolucion(7, datos1)

    assert "Debe registrar las novedades" in str(exc_info1.value)

    # Con novedades solo espacios en blanco
    datos2 = DevolucionCreate(
        fecha_devolucion=hoy,
        novedades="   ",
        enviar_a_mantenimiento=True,
    )
    with pytest.raises(PrestamoValidationError) as exc_info2:
        service.registrar_devolucion(7, datos2)

    assert "Debe registrar las novedades" in str(exc_info2.value)


def test_registrar_devolucion_equipo_no_encontrado_lanza_error(
    service, mock_prestamo_repo, mock_equipo_repo
):
    """RN-DEV-05: Lanza PrestamoValidationError si el equipo asociado no existe."""
    hoy = date.today()
    prestamo = Prestamo(
        id=8,
        cedula_persona="1001234567",
        id_equipo=999,
        fecha_prestamo=hoy - timedelta(days=2),
        fecha_devolucion_esperada=hoy + timedelta(days=5),
    )
    mock_prestamo_repo.get_by_id.return_value = prestamo
    mock_equipo_repo.get_by_id.return_value = None

    datos = DevolucionCreate(
        fecha_devolucion=hoy,
        enviar_a_mantenimiento=False,
    )

    with pytest.raises(PrestamoValidationError) as exc_info:
        service.registrar_devolucion(8, datos)

    assert "no fue encontrado" in str(exc_info.value)
