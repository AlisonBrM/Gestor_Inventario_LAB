from datetime import date
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


class Devolucion(Base):
    """Modelo ORM para Devolución.

    Registro de la devolución efectiva de un préstamo (relación 1 a 1).
    """

    __tablename__ = "devoluciones"

    id_prestamo = Column(
        Integer,
        ForeignKey("prestamos.id", ondelete="CASCADE"),
        primary_key=True,
    )
    fecha_devolucion = Column(Date, nullable=False, default=date.today)
    novedades = Column(String(255), nullable=True)

    prestamo = relationship("Prestamo", back_populates="devolucion")

    def __repr__(self) -> str:
        return (
            f"<Devolucion(id_prestamo={self.id_prestamo}, "
            f"fecha_devolucion={self.fecha_devolucion})>"
        )
