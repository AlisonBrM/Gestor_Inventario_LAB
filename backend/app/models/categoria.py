from sqlalchemy import Boolean, Column, Integer, String
from app.core.database import Base


class Categoria(Base):
    """Modelo ORM para Categoría.

    Representa la clasificación de equipos del laboratorio y define
    el plazo máximo de devolución en días calendario.
    """

    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    nombre = Column(String(100), nullable=False, unique=True, index=True)
    descripcion = Column(String(255), nullable=True)
    plazo_entrega = Column(Integer, nullable=False)
    activo = Column(Boolean, nullable=False, default=True)

    def __repr__(self) -> str:
        return f"<Categoria(id={self.id}, nombre='{self.nombre}', plazo_entrega={self.plazo_entrega}, activo={self.activo})>"
