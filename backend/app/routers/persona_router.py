from typing import Optional, Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repositories.persona_repository import PersonaRepository
from app.schemas.persona import (
    PersonaCreate,
    PersonaResponse,
    PersonaUpdate,
    TipoPersona,
)
from app.services.persona_service import (
    PersonaAlreadyExistsError,
    PersonaNotFoundError,
    PersonaService,
    PersonaValidationError,
)

router = APIRouter(prefix="/personas", tags=["Personas"])


def get_persona_service(db: Session = Depends(get_db)) -> PersonaService:
    """Inyección de dependencias para PersonaService."""
    repository = PersonaRepository(db)
    return PersonaService(repository)


@router.post(
    "",
    response_model=PersonaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva persona",
)
def crear_persona(
    datos: PersonaCreate,
    service: PersonaService = Depends(get_persona_service),
) -> PersonaResponse:
    """Registra una nueva persona (estudiante o profesor) en el sistema."""
    try:
        return service.crear_persona(datos)
    except (PersonaAlreadyExistsError, PersonaValidationError) as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.get(
    "",
    response_model=list[PersonaResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar personas",
)
def listar_personas(
    solo_activas: bool = Query(
        True,
        description="Indica si solo se deben listar las personas activas (True por defecto)",
    ),
    tipo_persona: Optional[TipoPersona] = Query(
        None,
        description="Filtro opcional por tipo de persona ('profesor' o 'estudiante')",
    ),
    facultad: Optional[str] = Query(
        None,
        description="Filtro opcional por facultad (búsqueda parcial)",
    ),
    busqueda: Optional[str] = Query(
        None,
        description="Filtro opcional de búsqueda por cédula o nombre completo",
    ),
    service: PersonaService = Depends(get_persona_service),
) -> Sequence[PersonaResponse]:
    """Retorna la lista de personas registradas aplicando los filtros provistos."""
    return service.listar_personas(
        solo_activas=solo_activas,
        tipo_persona=tipo_persona.value if tipo_persona else None,
        facultad=facultad,
        busqueda=busqueda,
    )


@router.get(
    "/{cedula}",
    response_model=PersonaResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener una persona por cédula",
)
def obtener_persona(
    cedula: str,
    service: PersonaService = Depends(get_persona_service),
) -> PersonaResponse:
    """Retorna la información detallada de una persona según su cédula."""
    try:
        return service.obtener_persona_por_cedula(cedula)
    except PersonaNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except PersonaValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.put(
    "/{cedula}",
    response_model=PersonaResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar los datos de una persona",
)
def actualizar_persona(
    cedula: str,
    datos: PersonaUpdate,
    service: PersonaService = Depends(get_persona_service),
) -> PersonaResponse:
    """Actualiza la información de una persona. La cédula es inmutable."""
    try:
        return service.actualizar_persona(cedula, datos)
    except PersonaNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except PersonaValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err


@router.delete(
    "/{cedula}",
    response_model=PersonaResponse,
    status_code=status.HTTP_200_OK,
    summary="Eliminar lógicamente una persona",
)
def eliminar_persona(
    cedula: str,
    service: PersonaService = Depends(get_persona_service),
) -> PersonaResponse:
    """Realiza el borrado lógico de una persona estableciendo su estado activo en False."""
    try:
        return service.eliminar_persona_logica(cedula)
    except PersonaNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        ) from err
    except PersonaValidationError as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
