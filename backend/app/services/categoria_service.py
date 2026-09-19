from typing import Optional, Sequence

from app.models.categoria import Categoria
from app.repositories.categoria_repository import CategoriaRepository
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate


class CategoriaNotFoundError(Exception):
    """Lanzada cuando una categoría no existe."""

    def __init__(self, categoria_id: int) -> None:
        super().__init__(f"Categoría con ID {categoria_id} no encontrada.")
        self.categoria_id = categoria_id


class CategoriaAlreadyExistsError(Exception):
    """Lanzada cuando ya existe una categoría con el mismo nombre."""

    def __init__(self, nombre: str) -> None:
        super().__init__(f"Ya existe una categoría con el nombre '{nombre}'.")
        self.nombre = nombre


class CategoriaValidationError(Exception):
    """Lanzada cuando falla una regla o validación de dominio de la categoría."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class CategoriaService:
    """Servicio con la lógica y reglas de negocio para Categorías."""

    MIN_PLAZO_ENTREGA: int = 1
    MAX_PLAZO_ENTREGA: int = 180  # SUP-04: Máximo 6 meses expresado en días calendario (SUP-05)

    def __init__(self, repository: CategoriaRepository) -> None:
        self.repository = repository

    def _validar_plazo_entrega(self, plazo: int) -> None:
        """RN-CAT-01: Valida que el plazo de entrega esté entre 1 y 180 días calendario."""
        if plazo < self.MIN_PLAZO_ENTREGA or plazo > self.MAX_PLAZO_ENTREGA:
            raise CategoriaValidationError(
                f"El plazo de entrega debe estar entre {self.MIN_PLAZO_ENTREGA} y "
                f"{self.MAX_PLAZO_ENTREGA} días calendario."
            )

    def _validar_nombre(self, nombre: str) -> str:
        """RN-CAT-02: Valida que el nombre no esté vacío ni contenga solo espacios."""
        if not nombre or not nombre.strip():
            raise CategoriaValidationError(
                "El nombre de la categoría es obligatorio y no puede estar vacío."
            )
        trimmed = nombre.strip()
        if len(trimmed) > 100:
            raise CategoriaValidationError(
                "El nombre de la categoría no puede superar los 100 caracteres."
            )
        return trimmed

    def listar_categorias(self, solo_activas: bool = True) -> Sequence[Categoria]:
        """Obtiene la lista de categorías, opcionalmente filtrando solo las activas."""
        return self.repository.get_all(solo_activas=solo_activas)

    def obtener_categoria_por_id(self, categoria_id: int) -> Categoria:
        """RN-CAT-04: Obtiene una categoría por ID o lanza CategoriaNotFoundError."""
        categoria = self.repository.get_by_id(categoria_id)
        if not categoria:
            raise CategoriaNotFoundError(categoria_id)
        return categoria

    def crear_categoria(self, datos: CategoriaCreate) -> Categoria:
        """Crea una nueva categoría aplicando las reglas de negocio."""
        nombre_limpio = self._validar_nombre(datos.nombre)
        self._validar_plazo_entrega(datos.plazo_entrega)

        # RN-CAT-03: Unicidad del nombre (insensible a mayúsculas y minúsculas)
        categoria_existente = self.repository.get_by_nombre(nombre_limpio)
        if categoria_existente:
            raise CategoriaAlreadyExistsError(nombre_limpio)

        descripcion_limpia = datos.descripcion.strip() if datos.descripcion else None

        nueva_categoria = Categoria(
            nombre=nombre_limpio,
            descripcion=descripcion_limpia,
            plazo_entrega=datos.plazo_entrega,
            activo=True,
        )
        return self.repository.create(nueva_categoria)

    def actualizar_categoria(self, categoria_id: int, datos: CategoriaUpdate) -> Categoria:
        """Actualiza una categoría existente aplicando las reglas de negocio."""
        # RN-CAT-04: Verifica existencia
        categoria = self.obtener_categoria_por_id(categoria_id)

        # Validación y actualización de nombre
        if datos.nombre is not None:
            nombre_limpio = self._validar_nombre(datos.nombre)
            # RN-CAT-03: Si cambia el nombre, validar que no esté ocupado por otra categoría
            if nombre_limpio.lower() != categoria.nombre.lower():
                existente = self.repository.get_by_nombre(nombre_limpio)
                if existente and existente.id != categoria_id:
                    raise CategoriaAlreadyExistsError(nombre_limpio)
            categoria.nombre = nombre_limpio

        # Validación y actualización de plazo de entrega
        if datos.plazo_entrega is not None:
            self._validar_plazo_entrega(datos.plazo_entrega)
            categoria.plazo_entrega = datos.plazo_entrega

        # Actualización de descripción
        if datos.descripcion is not None:
            categoria.descripcion = datos.descripcion.strip() if datos.descripcion else None

        # RN-CAT-06: Reactivación o cambio de estado activo
        if datos.activo is not None:
            categoria.activo = datos.activo

        return self.repository.update(categoria)

    def eliminar_categoria_logica(self, categoria_id: int) -> Categoria:
        """RN-CAT-05: Realiza el borrado lógico de la categoría (activo = False)."""
        # RN-CAT-04: Verifica existencia
        categoria = self.obtener_categoria_por_id(categoria_id)
        return self.repository.delete_logical(categoria)
