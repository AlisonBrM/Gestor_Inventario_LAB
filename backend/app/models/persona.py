from sqlalchemy import Boolean, Column, Enum as SAEnum, String

from app.core.database import Base


class Persona(Base):
    """Modelo ORM para Persona.

    Representa a un estudiante o profesor que solicita préstamos de equipos
    en el laboratorio universitario.
    """

    __tablename__ = "personas"

    cedula = Column(String(20), primary_key=True, index=True)
    nombre_completo = Column(String(100), nullable=False)
    correo = Column(String(150), nullable=True)
    telefono = Column(String(20), nullable=False)
    tipo_persona = Column(
        SAEnum("profesor", "estudiante", name="tipo_persona_enum"),
        nullable=False,
    )
    facultad = Column(String(150), nullable=False)
    activo = Column(Boolean, nullable=False, default=True, index=True)

    def __repr__(self) -> str:
        return (
            f"<Persona(cedula='{self.cedula}', nombre_completo='{self.nombre_completo}', "
            f"tipo_persona='{self.tipo_persona}', facultad='{self.facultad}', activo={self.activo})>"
        )
