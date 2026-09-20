from datetime import date
from typing import Optional, Sequence

from app.models.equipo import Equipo
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.equipo_repository import EquipoRepository
from app.schemas.equipo import EquipoCreate, EquipoUpdate


class EquipoNotFoundError(Exception):
    """Lanzada cuando un equipo no existe."""

    def __init__(self, equipo_id: int) -> None:
        super().__init__(f"Equipo con ID {equipo_id} no encontrado.")
        self.equipo_id = equipo_id


class EquipoAlreadyExistsError(Exception):
    """Lanzada cuando ya existe un equipo con el mismo secuencial."""

    def __init__(self, secuencial: str) -> None:
        super().__init__(f"Ya existe un equipo registrado con el secuencial '{secuencial}'.")
        self.secuencial = secuencial


class EquipoValidationError(Exception):
    """Lanzada cuando falla una regla o validación de dominio del equipo."""

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class EquipoService:
    """Servicio con la lógica y reglas de negocio para Equipos."""

    def __init__(
        self,
        repository: EquipoRepository,
        categoria_repository: CategoriaRepository,
    ) -> None:
        self.repository = repository
        self.categoria_repository = categoria_repository

    def _validar_categoria_activa(self, id_categoria: int) -> None:
        """RN-EQ-01: Valida que la categoría exista y esté activa."""
        categoria = self.categoria_repository.get_by_id(id_categoria)
        if not categoria:
            raise EquipoValidationError(
                f"La categoría con ID {id_categoria} no existe en el sistema."
            )
        if not categoria.activo:
            raise EquipoValidationError(
                f"La categoría '{categoria.nombre}' (ID: {id_categoria}) se encuentra inactiva. "
                "No es posible asignarle equipos."
            )

    def _validar_cadena_no_vacia(self, valor: str, nombre_campo: str, max_longitud: int) -> str:
        """RN-EQ-04: Valida longitud y que no esté vacía."""
        if not valor or not valor.strip():
            raise EquipoValidationError(
                f"El campo '{nombre_campo}' es obligatorio y no puede estar vacío."
            )
        limpio = valor.strip()
        if len(limpio) > max_longitud:
            raise EquipoValidationError(
                f"El campo '{nombre_campo}' no puede superar los {max_longitud} caracteres."
            )
        return limpio

    def listar_equipos(
        self,
        solo_activos: bool = True,
        id_categoria: Optional[int] = None,
        en_mantenimiento: Optional[bool] = None,
    ) -> Sequence[Equipo]:
        """Obtiene la lista de equipos aplicando los filtros provistos."""
        return self.repository.get_all(
            solo_activos=solo_activos,
            id_categoria=id_categoria,
            en_mantenimiento=en_mantenimiento,
        )

    def obtener_equipo_por_id(self, equipo_id: int) -> Equipo:
        """Obtiene un equipo por su ID o lanza EquipoNotFoundError."""
        equipo = self.repository.get_by_id(equipo_id)
        if not equipo:
            raise EquipoNotFoundError(equipo_id)
        return equipo

    def crear_equipo(self, datos: EquipoCreate) -> Equipo:
        """Crea un nuevo equipo aplicando las reglas de negocio."""
        # Sanitización y validaciones básicas
        nombre_limpio = self._validar_cadena_no_vacia(datos.nombre, "nombre", 150)
        secuencial_limpio = self._validar_cadena_no_vacia(datos.secuencial, "secuencial", 50)

        # RN-EQ-01: Validar existencia y estado activo de la categoría
        self._validar_categoria_activa(datos.id_categoria)

        # RN-EQ-02: Unicidad del secuencial (insensible a mayúsculas/minúsculas)
        equipo_existente = self.repository.get_by_secuencial(secuencial_limpio)
        if equipo_existente:
            raise EquipoAlreadyExistsError(secuencial_limpio)

        descripcion_limpia = datos.descripcion.strip() if datos.descripcion else None

        # RN-EQ-03: Valores iniciales
        nuevo_equipo = Equipo(
            id_categoria=datos.id_categoria,
            nombre=nombre_limpio,
            secuencial=secuencial_limpio,
            descripcion=descripcion_limpia,
            mantenimiento=False,
            fecha_creacion=date.today(),
            activo=True,
        )
        return self.repository.create(nuevo_equipo)

    def actualizar_equipo(self, equipo_id: int, datos: EquipoUpdate) -> Equipo:
        """Actualiza un equipo existente aplicando las reglas de negocio."""
        # RN-EQ-05: Verificar existencia previa
        equipo = self.obtener_equipo_por_id(equipo_id)

        # RN-EQ-01: Validar cambio de categoría
        if datos.id_categoria is not None:
            if datos.id_categoria != equipo.id_categoria:
                self._validar_categoria_activa(datos.id_categoria)
            equipo.id_categoria = datos.id_categoria

        # RN-EQ-04: Validar y actualizar nombre
        if datos.nombre is not None:
            equipo.nombre = self._validar_cadena_no_vacia(datos.nombre, "nombre", 150)

        # RN-EQ-02: Validar y actualizar secuencial si cambia
        if datos.secuencial is not None:
            secuencial_limpio = self._validar_cadena_no_vacia(datos.secuencial, "secuencial", 50)
            if secuencial_limpio.lower() != equipo.secuencial.lower():
                existente = self.repository.get_by_secuencial(secuencial_limpio)
                if existente and existente.id != equipo_id:
                    raise EquipoAlreadyExistsError(secuencial_limpio)
            equipo.secuencial = secuencial_limpio

        # Actualización de descripción
        if datos.descripcion is not None:
            equipo.descripcion = datos.descripcion.strip() if datos.descripcion else None

        # Actualización de estado de mantenimiento (SUP-08)
        if datos.mantenimiento is not None:
            equipo.mantenimiento = datos.mantenimiento

        # Reactivación o cambio de estado activo
        if datos.activo is not None:
            equipo.activo = datos.activo

        return self.repository.update(equipo)

    def eliminar_equipo_logico(self, equipo_id: int) -> Equipo:
        """RN-EQ-06: Borrado lógico del equipo (activo = False)."""
        equipo = self.obtener_equipo_por_id(equipo_id)
        return self.repository.delete_logical(equipo)

    def sacar_de_mantenimiento(self, equipo_id: int) -> Equipo:
        """Marca un equipo como disponible cambiando su estado de mantenimiento a False.

        Reglas aplicadas:
        - RN-EQ-MANT-01: El equipo debe existir en el sistema (o lanza EquipoNotFoundError).
        - RN-EQ-MANT-02: El equipo debe encontrarse actualmente en mantenimiento (mantenimiento == True).
        - RN-EQ-MANT-03: El equipo debe encontrarse activo (activo == True).
        - RN-EQ-MANT-04: Se actualiza el estado a mantenimiento = False y se persiste en base de datos.
        """
        equipo = self.obtener_equipo_por_id(equipo_id)

        if not equipo.activo:
            raise EquipoValidationError(
                f"No es posible sacar de mantenimiento el equipo '{equipo.nombre}' porque se encuentra inactivo."
            )

        if not equipo.mantenimiento:
            raise EquipoValidationError(
                f"El equipo '{equipo.nombre}' (secuencial: {equipo.secuencial}) no se encuentra en mantenimiento."
            )

        equipo.mantenimiento = False
        return self.repository.update(equipo)
