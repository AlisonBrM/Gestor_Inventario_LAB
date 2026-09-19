from typing import Optional, Sequence
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.categoria import Categoria


class CategoriaRepository:
    """Repositorio para operaciones de persistencia de Categoría."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, categoria_id: int) -> Optional[Categoria]:
        """Obtiene una categoría por su identificador primario."""
        return self.db.execute(
            select(Categoria).where(Categoria.id == categoria_id)
        ).scalar_one_or_none()

    def get_by_nombre(self, nombre: str) -> Optional[Categoria]:
        """Obtiene una categoría por su nombre (insensible a mayúsculas y minúsculas)."""
        return self.db.execute(
            select(Categoria).where(func.lower(Categoria.nombre) == func.lower(nombre.strip()))
        ).scalar_one_or_none()

    def get_all(self, solo_activas: bool = True) -> Sequence[Categoria]:
        """Lista las categorías registradas, opcionalmente filtrando solo las activas."""
        stmt = select(Categoria)
        if solo_activas:
            stmt = stmt.where(Categoria.activo.is_(True))
        stmt = stmt.order_by(Categoria.id.asc())
        return self.db.execute(stmt).scalars().all()

    def create(self, categoria: Categoria) -> Categoria:
        """Persiste una nueva categoría en la base de datos."""
        self.db.add(categoria)
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def update(self, categoria: Categoria) -> Categoria:
        """Guarda los cambios efectuados sobre una categoría existente."""
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def delete_logical(self, categoria: Categoria) -> Categoria:
        """Realiza el borrado lógico de una categoría marcándola como inactiva."""
        categoria.activo = False
        self.db.commit()
        self.db.refresh(categoria)
        return categoria
