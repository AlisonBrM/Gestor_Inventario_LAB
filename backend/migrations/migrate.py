"""Módulo para inicializar las tablas de la base de datos."""
import logging
from app.core.database import Base, engine
from app.models import Categoria, Devolucion, Equipo, Persona, Prestamo  # noqa: F401

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Crea todas las tablas definidas en los modelos si no existen."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas de la base de datos inicializadas correctamente.")
    except Exception as exc:
        logger.warning("No se pudo conectar a la base de datos para inicializar tablas: %s", exc)


if __name__ == "__main__":
    init_db()
