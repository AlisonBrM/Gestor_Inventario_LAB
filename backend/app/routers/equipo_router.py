from typing import Optional, Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.equipo_repository import EquipoRepository
from app.schemas.equipo import EquipoCreate, EquipoResponse, EquipoUpdate
from app.services.equipo_service import (
    EquipoAlreadyExistsError,
    EquipoNotFoundError,
    EquipoService,
    EquipoValidationError,
)

router = APIRouter(prefix="/equipos", tags=["Equipos"])


def get_equipo_service(db: Session = Depends(get_db)) -> EquipoService:
    """Inyección de dependencias para EquipoService."""
    equipo_repo = EquipoRepository(db)
    categoria_repo = CategoriaRepository(db)
    return EquipoService(
        repository=equipo_repo,
        categoria_repository=categoria_repo,
    )


@router.post(
    "",
    response_model=EquipoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear un nuevo equipo",
)
def crear_equipo(
    datos: EquipoCreate,
    service: EquipoService = Depends(get_equipo_service),
) -> EquipoResponse:
    """Registra un nuevo equipo en el laboratorio asociado a una categoría activa."""
    try:
        return service.crear_equipo(datos)
    except (EquipoAlreadyExistsError, EquipoValidationError) as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.get(
    "",
    response_model=list[EquipoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar equipos",
)
def listar_equipos(
    solo_activos: bool = Query(
        True,
        description="Indica si solo se deben listar los equipos activos (True por defecto)",
    ),
    id_categoria: Optional[int] = Query(
        None,
        description="Filtrar por ID de categoría",
    ),
    en_mantenimiento: Optional[bool] = Query(
        None,
        description="Filtrar por estado de mantenimiento (True/False)",
    ),
    service: EquipoService = Depends(get_equipo_service),
) -> Sequence[EquipoResponse]:
    """Retorna la lista de equipos registrados con filtros opcionales."""
    return service.listar_equipos(
        solo_activos=solo_activos,
        id_categoria=id_categoria,
        en_mantenimiento=en_mantenimiento,
    )


@router.get(
    "/{equipo_id}",
    response_model=EquipoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un equipo por ID",
)
def obtener_equipo(
    equipo_id: int,
    service: EquipoService = Depends(get_equipo_service),
) -> EquipoResponse:
    """Retorna la información detallada de un equipo específico."""
    try:
        return service.obtener_equipo_por_id(equipo_id)
    except EquipoNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@router.put(
    "/{equipo_id}",
    response_model=EquipoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un equipo",
)
def actualizar_equipo(
    equipo_id: int,
    datos: EquipoUpdate,
    service: EquipoService = Depends(get_equipo_service),
) -> EquipoResponse:
    """Actualiza los campos de un equipo existente."""
    try:
        return service.actualizar_equipo(equipo_id, datos)
    except EquipoNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except (EquipoAlreadyExistsError, EquipoValidationError) as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.delete(
    "/{equipo_id}",
    response_model=EquipoResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar lógicamente un equipo",
)
def eliminar_equipo(
    equipo_id: int,
    service: EquipoService = Depends(get_equipo_service),
) -> EquipoResponse:
    """Realiza el borrado lógico de un equipo estableciendo activo = False."""
    try:
        return service.eliminar_equipo_logico(equipo_id)
    except EquipoNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
