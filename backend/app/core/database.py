import logging
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from app.core.config import settings

logger = logging.getLogger(__name__)

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea las tablas en la base de datos si no existen."""
    try:
        # Importar modelos aquí para asegurar su registro en Base.metadata
        from app.models.categoria import Categoria  # noqa: F401
        from app.models.devolucion import Devolucion  # noqa: F401
        from app.models.equipo import Equipo  # noqa: F401
        from app.models.persona import Persona  # noqa: F401
        from app.models.prestamo import Prestamo  # noqa: F401
        Base.metadata.create_all(bind=engine)
        logger.info("Tablas de la base de datos verificadas/inicializadas correctamente.")
    except Exception as exc:
        logger.warning("No se pudo inicializar las tablas en la base de datos: %s", exc)
