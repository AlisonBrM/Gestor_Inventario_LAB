from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.routers import categoria_router, equipo_router, persona_router, prestamo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicializa las tablas al iniciar la aplicación si la base de datos está disponible
    init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclusión de routers
app.include_router(categoria_router, prefix=settings.API_PREFIX)
app.include_router(equipo_router, prefix=settings.API_PREFIX)
app.include_router(persona_router, prefix=settings.API_PREFIX)
app.include_router(prestamo_router, prefix=settings.API_PREFIX)


@app.get("/")
def read_root():
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get(f"{settings.API_PREFIX}/health")
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
