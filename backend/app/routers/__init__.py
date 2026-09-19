"""Capa de routers (endpoints REST)."""
from app.routers.categoria_router import router as categoria_router
from app.routers.equipo_router import router as equipo_router

__all__ = ["categoria_router", "equipo_router"]
