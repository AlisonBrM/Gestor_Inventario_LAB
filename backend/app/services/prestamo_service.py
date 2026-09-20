from datetime import date, timedelta
from typing import Optional, Sequence

from app.models.devolucion import Devolucion
from app.models.prestamo import Prestamo
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.equipo_repository import EquipoRepository
from app.repositories.persona_repository import PersonaRepository
from app.repositories.prestamo_repository import PrestamoRepository
from app.schemas.devolucion import DevolucionCreate
from app.schemas.prestamo import PrestamoCreate, PrestamoProrrogaCreate



class PrestamoNotFoundError(Exception):
    """Lanzada cuando un préstamo, persona o equipo no existe."""

    def __init__(self, identificador: str | int) -> None:
        if isinstance(identificador, int):
            super().__init__(f"Préstamo con ID {identificador} no encontrado.")
            self.identificador = identificador
        else:
            super().__init__(identificador)
            self.identificador = identificador


class PrestamoValidationError(Exception):
    """Lanzada cuando falla una regla o validación de dominio del préstamo."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class PrestamoService:
    """Servicio con la lógica y reglas de negocio para Préstamos."""

    def __init__(
        self,
        prestamo_repository: PrestamoRepository,
        persona_repository: PersonaRepository,
        equipo_repository: EquipoRepository,
        categoria_repository: CategoriaRepository,
    ) -> None:
        self.prestamo_repository = prestamo_repository
        self.persona_repository = persona_repository
        self.equipo_repository = equipo_repository
        self.categoria_repository = categoria_repository

    def obtener_prestamo_por_id(self, prestamo_id: int) -> Prestamo:
        """Obtiene un préstamo por su ID o lanza PrestamoNotFoundError."""
        prestamo = self.prestamo_repository.get_by_id(prestamo_id)
        if not prestamo:
            raise PrestamoNotFoundError(prestamo_id)
        return prestamo

    def listar_prestamos(
        self,
        id_categoria: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        estado: Optional[str] = None,
    ) -> Sequence[Prestamo]:
        """Retorna la lista de préstamos aplicando los filtros y validaciones de dominio.

        Reglas aplicadas:
        - RN-PREST-LIST-01: Si se envían fecha_desde y fecha_hasta, fecha_desde <= fecha_hasta.
        - RN-PREST-LIST-02: Si se envía estado, debe ser 'vigente' o 'vencido'.
        - RN-PREST-LIST-03: Si se envía id_categoria, debe ser un entero positivo (> 0).
        """
        # RN-PREST-LIST-01: Validación de rango de fechas
        if fecha_desde is not None and fecha_hasta is not None and fecha_desde > fecha_hasta:
            raise PrestamoValidationError(
                "La fecha inicial ('fecha_desde') no puede ser posterior a la fecha final ('fecha_hasta')."
            )

        # RN-PREST-LIST-02: Validación de estado
        estado_normalizado = None
        if estado is not None:
            estado_normalizado = estado.strip().lower()
            if estado_normalizado not in ("vigente", "vencido"):
                raise PrestamoValidationError(
                    "El estado debe ser 'vigente' o 'vencido'."
                )

        # RN-PREST-LIST-03: Validación de categoría
        if id_categoria is not None and id_categoria <= 0:
            raise PrestamoValidationError(
                "El ID de la categoría debe ser un número entero positivo."
            )

        return self.prestamo_repository.listar(
            id_categoria=id_categoria,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            estado=estado_normalizado,
        )

    def crear_prestamo(self, datos: PrestamoCreate) -> Prestamo:
        """Crea un nuevo préstamo aplicando todas las reglas de negocio.

        Reglas aplicadas:
        - RN-PREST-01: Un solicitante con un préstamo vencido sin devolver no puede pedir otro equipo.
        - RN-PREST-02: Un equipo marcado en mantenimiento no puede ser prestado.
        - RN-PREST-03: Un equipo ya prestado y no devuelto no puede ser prestado simultáneamente.
        - RN-PREST-04: Solicitante, equipo y categoría deben existir y estar activos.
        - RN-PREST-05: Cálculo automático de fecha de devolución esperada = fecha_prestamo + categoría.plazo_entrega.
        - RN-PREST-06: La fecha del préstamo no puede ser posterior a la fecha actual.
        """
        fecha_inicio = datos.fecha_prestamo or date.today()

        # RN-PREST-06: Validación de fecha de préstamo
        if fecha_inicio > date.today():
            raise PrestamoValidationError(
                "La fecha de inicio del préstamo no puede ser posterior a la fecha actual."
            )

        # RN-PREST-04: Validar existencia y estado de la persona
        persona = self.persona_repository.get_by_cedula(datos.cedula_persona)
        if not persona:
            raise PrestamoNotFoundError(
                f"La persona con cédula '{datos.cedula_persona}' no existe en el sistema."
            )
        if not persona.activo:
            raise PrestamoValidationError(
                f"La persona '{persona.nombre_completo}' (cédula: {datos.cedula_persona}) "
                "se encuentra inactiva. No puede solicitar préstamos."
            )

        # RN-PREST-01: Verificar si el solicitante tiene préstamos vencidos sin devolver
        prestamos_pendientes = (
            self.prestamo_repository.get_prestamos_no_devueltos_por_persona(
                datos.cedula_persona
            )
        )
        for p in prestamos_pendientes:
            if p.fecha_devolucion_esperada < fecha_inicio:
                raise PrestamoValidationError(
                    f"El solicitante con cédula '{datos.cedula_persona}' tiene un préstamo vencido "
                    f"sin devolver (Préstamo #{p.id}, fecha límite esperada: {p.fecha_devolucion_esperada}). "
                    "No puede solicitar otro equipo hasta devolver los equipos vencidos."
                )

        # RN-PREST-04: Validar existencia y estado del equipo
        equipo = self.equipo_repository.get_by_id(datos.id_equipo)
        if not equipo:
            raise PrestamoNotFoundError(
                f"El equipo con ID {datos.id_equipo} no existe en el sistema."
            )
        if not equipo.activo:
            raise PrestamoValidationError(
                f"El equipo '{equipo.nombre}' (ID: {datos.id_equipo}) se encuentra inactivo."
            )

        # RN-PREST-02: Validar si el equipo está en mantenimiento
        if equipo.mantenimiento:
            raise PrestamoValidationError(
                f"El equipo '{equipo.nombre}' (secuencial: {equipo.secuencial}) "
                "se encuentra marcado en mantenimiento. No puede ser prestado."
            )

        # RN-PREST-03: Validar que el equipo no esté prestado actualmente
        prestamo_activo_equipo = (
            self.prestamo_repository.get_prestamo_activo_por_equipo(datos.id_equipo)
        )
        if prestamo_activo_equipo:
            raise PrestamoValidationError(
                f"El equipo '{equipo.nombre}' (secuencial: {equipo.secuencial}) "
                f"ya se encuentra actualmente prestado (Préstamo #{prestamo_activo_equipo.id}) "
                "y no ha sido devuelto."
            )

        # RN-PREST-04: Validar categoría asociada al equipo
        categoria = self.categoria_repository.get_by_id(equipo.id_categoria)
        if not categoria:
            raise PrestamoValidationError(
                f"La categoría con ID {equipo.id_categoria} asociada al equipo no existe."
            )
        if not categoria.activo:
            raise PrestamoValidationError(
                f"La categoría '{categoria.nombre}' asociada al equipo se encuentra inactiva. "
                "No es posible prestar equipos pertenecientes a una categoría inactiva."
            )

        # RN-PREST-05: Cálculo automático de la fecha de devolución esperada
        fecha_devolucion_esperada = fecha_inicio + timedelta(days=categoria.plazo_entrega)

        nuevo_prestamo = Prestamo(
            cedula_persona=datos.cedula_persona.strip(),
            id_equipo=datos.id_equipo,
            fecha_prestamo=fecha_inicio,
            fecha_devolucion_esperada=fecha_devolucion_esperada,
        )

        return self.prestamo_repository.create(nuevo_prestamo)

    def registrar_devolucion(self, prestamo_id: int, datos: DevolucionCreate) -> Prestamo:
        """Registra la devolución de un préstamo aplicando las reglas de negocio.

        Reglas aplicadas:
        - RN-DEV-01: El préstamo debe existir (o lanza PrestamoNotFoundError).
        - RN-DEV-02: El préstamo no debe haber sido devuelto previamente (o lanza PrestamoValidationError).
        - RN-DEV-03: La fecha de devolución no puede ser posterior a la fecha actual ni anterior a la fecha de inicio del préstamo.
        - RN-DEV-04: Si el equipo se marca para mantenimiento, el administrador debe escribir obligatoriamente las novedades.
        - RN-DEV-05: Se actualiza el estado de mantenimiento del equipo según lo indicado por el administrador.
        - RN-DEV-06: Se persiste la devolución y el préstamo pasa a estar devuelto.
        """
        # RN-DEV-01: Validar existencia del préstamo
        prestamo = self.prestamo_repository.get_by_id(prestamo_id)
        if not prestamo:
            raise PrestamoNotFoundError(prestamo_id)

        # RN-DEV-02: Validar que no haya sido devuelto previamente
        if prestamo.devuelto:
            raise PrestamoValidationError(
                f"El préstamo #{prestamo_id} ya fue devuelto previamente."
            )

        # RN-DEV-03: Validación de fecha de devolución
        fecha_efectiva = datos.fecha_devolucion or date.today()
        if fecha_efectiva > date.today():
            raise PrestamoValidationError(
                "La fecha de devolución no puede ser posterior a la fecha actual."
            )
        if fecha_efectiva < prestamo.fecha_prestamo:
            raise PrestamoValidationError(
                f"La fecha de devolución ({fecha_efectiva}) no puede ser anterior a la fecha de inicio del préstamo ({prestamo.fecha_prestamo})."
            )

        # RN-DEV-04: Novedades obligatorias únicamente si se envía a mantenimiento
        novedades_limpias = datos.novedades.strip() if datos.novedades else None
        if datos.enviar_a_mantenimiento and not novedades_limpias:
            raise PrestamoValidationError(
                "Debe registrar las novedades u observaciones cuando el equipo pasa a mantenimiento."
            )

        # RN-DEV-05: Actualizar estado de mantenimiento del equipo
        equipo = self.equipo_repository.get_by_id(prestamo.id_equipo)
        if not equipo:
            raise PrestamoValidationError(
                f"El equipo asociado (ID: {prestamo.id_equipo}) no fue encontrado."
            )
        equipo.mantenimiento = datos.enviar_a_mantenimiento
        self.equipo_repository.update(equipo)

        # RN-DEV-06: Crear y persistir la devolución
        devolucion = Devolucion(
            id_prestamo=prestamo.id,
            fecha_devolucion=fecha_efectiva,
            novedades=novedades_limpias,
        )
        self.prestamo_repository.create_devolucion(devolucion)

        # Actualizar relación en memoria para respuesta inmediata
        prestamo.devolucion = devolucion
        return prestamo

    def prorrogar_prestamo(
        self, prestamo_id: int, datos: PrestamoProrrogaCreate
    ) -> Prestamo:
        """Prorroga la fecha de devolución esperada de un préstamo vigente.

        Reglas aplicadas:
        - RN-PRORR-01: El préstamo debe existir (o lanza PrestamoNotFoundError).
        - RN-PRORR-02: El préstamo no debe haber sido devuelto (o lanza PrestamoValidationError).
        - RN-PRORR-03: Solo se pueden prorrogar préstamos vigentes (fecha esperada actual >= hoy).
        - RN-PRORR-04: La nueva fecha esperada debe ser estrictamente posterior a la actual fecha esperada.
        - RN-PRORR-05: La duración total del préstamo no puede superar los 180 días contados desde fecha_prestamo.
        - RN-PRORR-06: Si es válido, se actualiza fecha_devolucion_esperada y se persiste.
        """
        # RN-PRORR-01: Validar existencia del préstamo
        prestamo = self.prestamo_repository.get_by_id(prestamo_id)
        if not prestamo:
            raise PrestamoNotFoundError(prestamo_id)

        # RN-PRORR-02: Validar que no haya sido devuelto previamente
        if prestamo.devuelto:
            raise PrestamoValidationError(
                f"El préstamo #{prestamo_id} ya fue devuelto previamente y no puede ser prorrogado."
            )

        # RN-PRORR-03: Validar que el préstamo se encuentre vigente (no vencido)
        if prestamo.fecha_devolucion_esperada < date.today():
            raise PrestamoValidationError(
                f"El préstamo #{prestamo_id} se encuentra vencido. Solo se pueden prorrogar préstamos vigentes."
            )

        # RN-PRORR-04: La nueva fecha debe ser estrictamente posterior a la actual
        if datos.nueva_fecha_devolucion_esperada <= prestamo.fecha_devolucion_esperada:
            raise PrestamoValidationError(
                f"La nueva fecha esperada de devolución ({datos.nueva_fecha_devolucion_esperada}) "
                f"debe ser posterior a la fecha actual esperada ({prestamo.fecha_devolucion_esperada})."
            )

        # RN-PRORR-05: No superar los 180 días calendario desde fecha_prestamo (6 meses)
        fecha_maxima = prestamo.fecha_prestamo + timedelta(days=180)
        if datos.nueva_fecha_devolucion_esperada > fecha_maxima:
            raise PrestamoValidationError(
                f"La fecha máxima permitida para prorrogar este préstamo es {fecha_maxima} "
                "(máximo 180 días desde el inicio del préstamo)."
            )

        # RN-PRORR-06: Actualizar y persistir
        prestamo.fecha_devolucion_esperada = datos.nueva_fecha_devolucion_esperada
        return self.prestamo_repository.update(prestamo)

