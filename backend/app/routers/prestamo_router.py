from datetime import date
from typing import Optional, Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.equipo_repository import EquipoRepository
from app.repositories.persona_repository import PersonaRepository
from app.repositories.prestamo_repository import PrestamoRepository
from app.schemas.devolucion import DevolucionCreate
from app.schemas.prestamo import PrestamoCreate, PrestamoResponse
from app.services.prestamo_service import (
    PrestamoNotFoundError,
    PrestamoService,
    PrestamoValidationError,
)

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])


def get_prestamo_service(db: Session = Depends(get_db)) -> PrestamoService:
    """Inyección de dependencias para PrestamoService."""
    prestamo_repo = PrestamoRepository(db)
    persona_repo = PersonaRepository(db)
    equipo_repo = EquipoRepository(db)
    categoria_repo = CategoriaRepository(db)
    return PrestamoService(
        prestamo_repository=prestamo_repo,
        persona_repository=persona_repo,
        equipo_repository=equipo_repo,
        categoria_repository=categoria_repo,
    )


@router.post(
    "",
    response_model=PrestamoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo préstamo",
)
def crear_prestamo(
    datos: PrestamoCreate,
    service: PrestamoService = Depends(get_prestamo_service),
) -> PrestamoResponse:
    """Registra un nuevo préstamo de un equipo a una persona aplicando las reglas de negocio."""
    try:
        return service.crear_prestamo(datos)
    except PrestamoNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except PrestamoValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.get(
    "",
    response_model=list[PrestamoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar préstamos con filtros",
)
def listar_prestamos(
    id_categoria: Optional[int] = Query(
        None,
        description="Filtrar por ID de la categoría",
    ),
    fecha_desde: Optional[date] = Query(
        None,
        description="Fecha inicial del rango (aplica a fecha_prestamo)",
    ),
    fecha_hasta: Optional[date] = Query(
        None,
        description="Fecha final del rango (aplica a fecha_prestamo)",
    ),
    estado: Optional[str] = Query(
        None,
        description="Filtrar por estado: 'vigente' o 'vencido'",
    ),
    service: PrestamoService = Depends(get_prestamo_service),
) -> Sequence[PrestamoResponse]:
    """Retorna la lista de préstamos aplicando los filtros opcionales."""
    try:
        return service.listar_prestamos(
            id_categoria=id_categoria,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            estado=estado,
        )
    except PrestamoValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.get(
    "/{id}",
    response_model=PrestamoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un préstamo por ID",
)
def obtener_prestamo(
    id: int,
    service: PrestamoService = Depends(get_prestamo_service),
) -> PrestamoResponse:
    """Retorna los datos de un préstamo específico por su identificador primario."""
    try:
        return service.obtener_prestamo_por_id(id)
    except PrestamoNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@router.post(
    "/{id}/devolucion",
    response_model=PrestamoResponse,
    status_code=status.HTTP_200_OK,
    summary="Registrar la devolución de un préstamo",
)
def registrar_devolucion(
    id: int,
    datos: DevolucionCreate,
    service: PrestamoService = Depends(get_prestamo_service),
) -> PrestamoResponse:
    """Registra la devolución de un préstamo de equipo recibido por el administrador."""
    try:
        return service.registrar_devolucion(id, datos)
    except PrestamoNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except PrestamoValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
