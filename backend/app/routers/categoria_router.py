from typing import Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.categoria_repository import CategoriaRepository
from app.schemas.categoria import CategoriaCreate, CategoriaResponse, CategoriaUpdate
from app.services.categoria_service import (
    CategoriaAlreadyExistsError,
    CategoriaNotFoundError,
    CategoriaService,
    CategoriaValidationError,
)

router = APIRouter(prefix="/categorias", tags=["Categorías"])


def get_categoria_service(db: Session = Depends(get_db)) -> CategoriaService:
    """Inyección de dependencias para CategoriaService."""
    repository = CategoriaRepository(db)
    return CategoriaService(repository)


@router.post(
    "",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear una nueva categoría",
)
def crear_categoria(
    datos: CategoriaCreate,
    service: CategoriaService = Depends(get_categoria_service),
) -> CategoriaResponse:
    """Crea una nueva categoría de equipos con un plazo de entrega."""
    try:
        return service.crear_categoria(datos)
    except (CategoriaAlreadyExistsError, CategoriaValidationError) as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.get(
    "",
    response_model=list[CategoriaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar categorías",
)
def listar_categorias(
    solo_activas: bool = Query(
        True,
        description="Indica si solo se deben listar las categorías activas (True por defecto)",
    ),
    service: CategoriaService = Depends(get_categoria_service),
) -> Sequence[CategoriaResponse]:
    """Retorna la lista de categorías registradas en el sistema."""
    return service.listar_categorias(solo_activas=solo_activas)


@router.get(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener una categoría por ID",
)
def obtener_categoria(
    categoria_id: int,
    service: CategoriaService = Depends(get_categoria_service),
) -> CategoriaResponse:
    """Retorna la información de una categoría específica."""
    try:
        return service.obtener_categoria_por_id(categoria_id)
    except CategoriaNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err


@router.put(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar una categoría",
)
def actualizar_categoria(
    categoria_id: int,
    datos: CategoriaUpdate,
    service: CategoriaService = Depends(get_categoria_service),
) -> CategoriaResponse:
    """Actualiza los campos de una categoría existente."""
    try:
        return service.actualizar_categoria(categoria_id, datos)
    except CategoriaNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except (CategoriaAlreadyExistsError, CategoriaValidationError) as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.delete(
    "/{categoria_id}",
    response_model=CategoriaResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar lógicamente una categoría",
)
def eliminar_categoria(
    categoria_id: int,
    service: CategoriaService = Depends(get_categoria_service),
) -> CategoriaResponse:
    """Realiza el borrado lógico de una categoría estableciendo su estado activo en False."""
    try:
        return service.eliminar_categoria_logica(categoria_id)
    except CategoriaNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
