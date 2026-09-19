from datetime import date
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.devolucion import Devolucion
from app.models.equipo import Equipo
from app.models.prestamo import Prestamo


class PrestamoRepository:
    """Repositorio para operaciones de persistencia de Préstamo."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, prestamo_id: int) -> Optional[Prestamo]:
        """Obtiene un préstamo por su identificador primario."""
        return self.db.execute(
            select(Prestamo).where(Prestamo.id == prestamo_id)
        ).scalar_one_or_none()

    def listar(
        self,
        id_categoria: Optional[int] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
        estado: Optional[str] = None,
        fecha_referencia: Optional[date] = None,
    ) -> Sequence[Prestamo]:
        """Retorna una lista de préstamos aplicando filtros de categoría, fecha y estado."""
        ref_date = fecha_referencia or date.today()
        stmt = (
            select(Prestamo)
            .join(Equipo, Prestamo.id_equipo == Equipo.id)
            .outerjoin(Devolucion, Prestamo.id == Devolucion.id_prestamo)
        )
        if id_categoria is not None:
            stmt = stmt.where(Equipo.id_categoria == id_categoria)
        if fecha_desde is not None:
            stmt = stmt.where(Prestamo.fecha_prestamo >= fecha_desde)
        if fecha_hasta is not None:
            stmt = stmt.where(Prestamo.fecha_prestamo <= fecha_hasta)
        if estado == "vigente":
            stmt = stmt.where(
                Devolucion.id_prestamo.is_(None),
                Prestamo.fecha_devolucion_esperada >= ref_date,
            )
        elif estado == "vencido":
            stmt = stmt.where(
                Devolucion.id_prestamo.is_(None),
                Prestamo.fecha_devolucion_esperada < ref_date,
            )

        stmt = stmt.order_by(Prestamo.fecha_prestamo.desc(), Prestamo.id.desc())
        return self.db.execute(stmt).scalars().all()

    def get_prestamos_no_devueltos_por_persona(self, cedula: str) -> Sequence[Prestamo]:
        """Obtiene todos los préstamos de una persona que no han sido devueltos."""
        stmt = (
            select(Prestamo)
            .outerjoin(Devolucion, Prestamo.id == Devolucion.id_prestamo)
            .where(
                Prestamo.cedula_persona == cedula.strip(),
                Devolucion.id_prestamo.is_(None),
            )
            .order_by(Prestamo.fecha_devolucion_esperada.asc())
        )
        return self.db.execute(stmt).scalars().all()

    def get_prestamo_activo_por_equipo(self, id_equipo: int) -> Optional[Prestamo]:
        """Obtiene el préstamo activo de un equipo si no ha sido devuelto."""
        stmt = (
            select(Prestamo)
            .outerjoin(Devolucion, Prestamo.id == Devolucion.id_prestamo)
            .where(
                Prestamo.id_equipo == id_equipo,
                Devolucion.id_prestamo.is_(None),
            )
        )
        return self.db.execute(stmt).scalars().first()

    def create(self, prestamo: Prestamo) -> Prestamo:
        """Persiste un nuevo préstamo en la base de datos."""
        self.db.add(prestamo)
        self.db.commit()
        self.db.refresh(prestamo)
        return prestamo

    def create_devolucion(self, devolucion: Devolucion) -> Devolucion:
        """Persiste una devolución en la base de datos."""
        self.db.add(devolucion)
        self.db.commit()
        self.db.refresh(devolucion)
        return devolucion
