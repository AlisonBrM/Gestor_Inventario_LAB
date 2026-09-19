from datetime import date
from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Equipo(Base):
    """Modelo ORM para Equipo.

    Representa un equipo físico del laboratorio disponible para préstamo.
    """

    __tablename__ = "equipos"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_categoria = Column(Integer, ForeignKey("categorias.id"), nullable=False, index=True)
    nombre = Column(String(150), nullable=False)
    secuencial = Column(String(50), nullable=False, unique=True, index=True)
    descripcion = Column(String(255), nullable=True)
    mantenimiento = Column(Boolean, nullable=False, default=False)
    fecha_creacion = Column(Date, nullable=False, default=date.today)
    activo = Column(Boolean, nullable=False, default=True, index=True)

    categoria = relationship("Categoria", backref="equipos", lazy="joined")

    @property
    def nombre_categoria(self) -> str | None:
        return self.categoria.nombre if self.categoria else None

    def __repr__(self) -> str:
        return (
            f"<Equipo(id={self.id}, secuencial='{self.secuencial}', "
            f"nombre='{self.nombre}', id_categoria={self.id_categoria}, "
            f"mantenimiento={self.mantenimiento}, activo={self.activo})>"
        )
