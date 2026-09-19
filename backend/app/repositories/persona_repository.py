from typing import Optional, Sequence
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.persona import Persona


class PersonaRepository:
    """Repositorio para operaciones de persistencia de Persona."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_cedula(self, cedula: str) -> Optional[Persona]:
        """Obtiene una persona por su cédula de identificación."""
        return self.db.execute(
            select(Persona).where(Persona.cedula == cedula.strip())
        ).scalar_one_or_none()

    def get_all(
        self,
        solo_activas: bool = True,
        tipo_persona: Optional[str] = None,
        facultad: Optional[str] = None,
        busqueda: Optional[str] = None,
    ) -> Sequence[Persona]:
        """Lista las personas registradas aplicando los filtros provistos."""
        stmt = select(Persona)
        if solo_activas:
            stmt = stmt.where(Persona.activo.is_(True))
        if tipo_persona:
            stmt = stmt.where(Persona.tipo_persona == tipo_persona)
        if facultad:
            stmt = stmt.where(func.lower(Persona.facultad).contains(func.lower(facultad.strip())))
        if busqueda:
            termino = f"%{busqueda.strip().lower()}%"
            stmt = stmt.where(
                or_(
                    func.lower(Persona.cedula).like(termino),
                    func.lower(Persona.nombre_completo).like(termino),
                )
            )
        stmt = stmt.order_by(Persona.nombre_completo.asc())
        return self.db.execute(stmt).scalars().all()

    def create(self, persona: Persona) -> Persona:
        """Persiste una nueva persona en la base de datos."""
        self.db.add(persona)
        self.db.commit()
        self.db.refresh(persona)
        return persona

    def update(self, persona: Persona) -> Persona:
        """Guarda los cambios efectuados sobre una persona existente."""
        self.db.commit()
        self.db.refresh(persona)
        return persona

    def delete_logical(self, persona: Persona) -> Persona:
        """Realiza el borrado lógico de una persona marcándola como inactiva."""
        persona.activo = False
        self.db.commit()
        self.db.refresh(persona)
        return persona
