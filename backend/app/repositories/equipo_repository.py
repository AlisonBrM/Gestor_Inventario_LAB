from typing import Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.equipo import Equipo


class EquipoRepository:
    """Repositorio para operaciones de persistencia de Equipo."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, equipo_id: int) -> Optional[Equipo]:
        """Obtiene un equipo por su identificador primario."""
        return self.db.execute(
            select(Equipo).where(Equipo.id == equipo_id)
        ).scalar_one_or_none()

    def get_by_secuencial(self, secuencial: str) -> Optional[Equipo]:
        """Obtiene un equipo por su secuencial (insensible a mayúsculas y minúsculas)."""
        return self.db.execute(
            select(Equipo).where(func.lower(Equipo.secuencial) == func.lower(secuencial.strip()))
        ).scalar_one_or_none()

    def get_all(
        self,
        solo_activos: bool = True,
        id_categoria: Optional[int] = None,
        en_mantenimiento: Optional[bool] = None,
    ) -> Sequence[Equipo]:
        """Lista los equipos registrados con filtros opcionales."""
        stmt = select(Equipo)
        if solo_activos:
            stmt = stmt.where(Equipo.activo.is_(True))
        if id_categoria is not None:
            stmt = stmt.where(Equipo.id_categoria == id_categoria)
        if en_mantenimiento is not None:
            stmt = stmt.where(Equipo.mantenimiento.is_(en_mantenimiento))
        stmt = stmt.order_by(Equipo.id.asc())
        return self.db.execute(stmt).scalars().all()

    def create(self, equipo: Equipo) -> Equipo:
        """Persiste un nuevo equipo en la base de datos."""
        self.db.add(equipo)
        self.db.commit()
        self.db.refresh(equipo)
        return equipo

    def update(self, equipo: Equipo) -> Equipo:
        """Guarda los cambios efectuados sobre un equipo existente."""
        self.db.commit()
        self.db.refresh(equipo)
        return equipo

    def delete_logical(self, equipo: Equipo) -> Equipo:
        """Realiza el borrado lógico de un equipo marcándolo como inactivo."""
        equipo.activo = False
        self.db.commit()
        self.db.refresh(equipo)
        return equipo
