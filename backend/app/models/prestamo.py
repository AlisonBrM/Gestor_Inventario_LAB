from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Prestamo(Base):
    """Modelo ORM para Préstamo.

    Representa el préstamo de un equipo físico del laboratorio a una persona.
    """

    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    cedula_persona = Column(
        String(20), ForeignKey("personas.cedula"), nullable=False, index=True
    )
    id_equipo = Column(
        Integer, ForeignKey("equipos.id"), nullable=False, index=True
    )
    fecha_prestamo = Column(Date, nullable=False, default=date.today)
    fecha_devolucion_esperada = Column(Date, nullable=False)

    persona = relationship("Persona", backref="prestamos", lazy="joined")
    equipo = relationship("Equipo", backref="prestamos", lazy="joined")
    devolucion = relationship(
        "Devolucion", back_populates="prestamo", uselist=False, lazy="joined"
    )

    @property
    def devuelto(self) -> bool:
        return self.devolucion is not None

    @property
    def nombre_persona(self) -> str | None:
        return self.persona.nombre_completo if self.persona else None

    @property
    def nombre_equipo(self) -> str | None:
        return self.equipo.nombre if self.equipo else None

    @property
    def secuencial_equipo(self) -> str | None:
        return self.equipo.secuencial if self.equipo else None

    @property
    def id_categoria(self) -> int | None:
        return self.equipo.id_categoria if self.equipo else None

    @property
    def nombre_categoria(self) -> str | None:
        return self.equipo.nombre_categoria if self.equipo else None

    @property
    def equipo_mantenimiento(self) -> bool | None:
        return self.equipo.mantenimiento if self.equipo else None

    @property
    def estado(self) -> str:
        if self.devuelto:
            return "devuelto"
        if self.fecha_devolucion_esperada < date.today():
            return "vencido"
        return "vigente"

    def __repr__(self) -> str:
        return (
            f"<Prestamo(id={self.id}, cedula_persona='{self.cedula_persona}', "
            f"id_equipo={self.id_equipo}, fecha_prestamo={self.fecha_prestamo}, "
            f"fecha_devolucion_esperada={self.fecha_devolucion_esperada})>"
        )
