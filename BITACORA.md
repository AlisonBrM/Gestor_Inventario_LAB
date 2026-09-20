# Bitácora de Desarrollo del Sistema

Este documento registra cronológicamente las funcionalidades implementadas en el **Sistema de Información para préstamos del Laboratorio Universitario**, basado en el historial real de git, las decisiones de arquitectura ([ADR.md](file:///C:/Users/Alison%20Martinez/Documents/SEMESTRE9/Empleabilidad/GestionInventarioLab/ADR.md)), las suposiciones y reglas de negocio ([ASSUMPTIONS.md](file:///C:/Users/Alison%20Martinez/Documents/SEMESTRE9/Empleabilidad/GestionInventarioLab/ASSUMPTIONS.md)), el modelo de datos ([MODELS.md](file:///C:/Users/Alison%20Martinez/Documents/SEMESTRE9/Empleabilidad/GestionInventarioLab/MODELS.md)) y la documentación de uso ([README.md](file:///C:/Users/Alison%20Martinez/Documents/SEMESTRE9/Empleabilidad/GestionInventarioLab/README.md)).

---

## Tabla de Entradas

1. [2026-09-18 — Configuración Inicial y Esqueleto del Sistema](#1-2026-09-18--configuración-inicial-y-esqueleto-del-sistema)
2. [2026-09-18 — Feature del CRUD de la Categoría](#2-2026-09-18--feature-del-crud-de-la-categoría)
3. [2026-09-18 — Feature del CRUD de Equipos](#3-2026-09-18--feature-del-crud-de-equipos)
4. [2026-09-18 — Feature de CRUD de Persona](#4-2026-09-18--feature-de-crud-de-persona)
5. [2026-09-19 — Feature de Creación de Préstamos con Validación de Reglas de Negocio](#5-2026-09-19--feature-de-creación-de-préstamos-con-validación-de-reglas-de-negocio)
6. [2026-09-19 — Funcionalidad: Listar Préstamos](#6-2026-09-19--funcionalidad-listar-préstamos)
7. [2026-09-19 — Funcionalidad: Crear Devolución de un Equipo](#7-2026-09-19--funcionalidad-crear-devolución-de-un-equipo)
8. [2026-09-20 — Funcionalidad: Prorrogar Préstamo](#8-2026-09-20--funcionalidad-prorrogar-préstamo)
9. [2026-09-20 — Funcionalidad: Cambiar el Estado de un Equipo en Mantenimiento a Vigente para ser Prestado](#9-2026-09-20--funcionalidad-cambiar-el-estado-de-un-equipo-en-mantenimiento-a-vigente-para-ser-prestado)

---

## 1. 2026-09-18 — Configuración Inicial y Esqueleto del Sistema

- **Commit:** `06793a9` (*Esqueleto del sistema y configuración*)
- **Resumen:**
  - Configuración inicial de la arquitectura del proyecto siguiendo la estructura por capas especificada en [AGENTS.md](file:///C:/Users/Alison%20Martinez/Documents/SEMESTRE9/Empleabilidad/GestionInventarioLab/AGENTS.md).
  - Creación del archivo `docker-compose.yml` para desplegar el motor de base de datos MySQL 8.0 con volumen persistente `mysql_data`.
  - Configuración del backend con Python y FastAPI sobre entorno virtual (`venv`), incluyendo manejo de variables de entorno (`pydantic-settings`), configuración de base de datos con SQLAlchemy (`database.py`) y endpoints de diagnóstico (`GET /` y `GET /api/health`).
  - Creación del frontend minimalista con React + Vite y JavaScript, con configuración de proxy hacia el backend (`http://127.0.0.1:8000`) en `vite.config.js`.
  - Configuración de dependencias en `backend/requirements.txt` y `frontend/package.json`.
- **Decisiones y reglas de negocio aplicadas:**
  - **ADR-001:** Uso de Antigravity CLI como asistente de desarrollo con IA.
  - **ADR-002:** Adopción del stack tecnológico React + JavaScript en frontend, Python + FastAPI en backend y MySQL en contenedor Docker con volumen persistente.
  - **ADR-003:** Arquitectura por capas estricta en el backend: `Routers → Services → Repositories → Models`.
  - **SUP-01:** Sistema de uso exclusivo para el administrador; no se requiere autenticación ni autorización de usuarios.
- **Archivos creados o modificados:**
  - **Creados:**
    - `.gitignore`
    - `docker-compose.yml`
    - `backend/.env.example`
    - `backend/requirements.txt`
    - `backend/app/__init__.py`
    - `backend/app/core/__init__.py`
    - `backend/app/core/config.py`
    - `backend/app/core/database.py`
    - `backend/app/main.py`
    - `backend/app/models/__init__.py`
    - `backend/app/repositories/__init__.py`
    - `backend/app/routers/__init__.py`
    - `backend/app/schemas/__init__.py`
    - `backend/app/services/__init__.py`
    - `backend/migrations/.gitkeep`
    - `backend/tests/__init__.py`
    - `backend/tests/test_health.py`
    - `frontend/index.html`
    - `frontend/package.json`
    - `frontend/package-lock.json`
    - `frontend/vite.config.js`
    - `frontend/src/main.jsx`
    - `frontend/src/App.jsx`
    - `frontend/src/index.css`
  - **Modificados:**
    - `README.md`
- **Pruebas realizadas:**
  - **Unitarias (pytest):**
    - `backend/tests/test_health.py::test_read_root`: Valida respuesta del endpoint raíz con estado 200 y mensaje de bienvenida.
    - `backend/tests/test_health.py::test_health_check`: Valida respuesta del endpoint de salud `/api/health`.
  - **Manuales:**
    - Verificación del levantamiento de MySQL en Docker mediante `docker compose up -d`.
    - Inicio de FastAPI con Uvicorn en el puerto 8000 y consulta interactiva en Swagger UI (`/docs`).
    - Ejecución de Vite con `npm run dev` en el puerto 5173 comprobando la comunicación vía proxy hacia el backend.
- **Pendientes o puntos por confirmar:**
  - Ninguno. Queda establecido el esqueleto base para el desarrollo de los módulos de dominio.

---

## 2. 2026-09-18 — Feature del CRUD de la Categoría

- **Commit:** `1d8ed1c` (*Feature del CRUD de la Categoria*)
- **Resumen:**
  - Implementación completa del ciclo de vida para las categorías de equipos (crear, listar, consultar por ID, actualizar y borrado lógico).
  - Definición del modelo ORM `Categoria` y script SQL de migración inicial `001_create_categorias.sql`.
  - Creación del runner de migraciones `backend/migrations/migrate.py`.
  - Capa de acceso a datos `CategoriaRepository` y reglas de dominio en `CategoriaService`.
  - Endpoints REST bajo `/api/categorias` en `categoria_router.py`.
  - Interfaz de usuario en React `Categorias.jsx` con formulario de registro, edición reactiva, lista y toggle de borrado lógico.
- **Decisiones y reglas de negocio aplicadas:**
  - **ADR-002 y ADR-003:** Separación estricta de capas y contratos DTO con Pydantic.
  - **SUP-04:** El plazo de entrega de cada categoría es definido por el administrador y no puede superar los 6 meses.
  - **SUP-05:** El plazo de entrega se expresa en días calendario (entre 1 y 180 días).
  - **RN-CAT-01:** Validación de plazo de entrega en rango de 1 a 180 días calendario inclusive.
  - **RN-CAT-02:** Nombre obligatorio, no vacío, longitud máxima de 100 caracteres.
  - **RN-CAT-03:** Unicidad del nombre de la categoría (insensible a mayúsculas/minúsculas).
  - **RN-CAT-04:** Verificación de existencia previa antes de consultar, actualizar o desactivar.
  - **RN-CAT-05:** Borrado lógico mediante `activo = False` para no romper integridad con equipos existentes.
  - **RN-CAT-06:** Soporte para reactivación de categorías inactivas.
- **Archivos creados o modificados:**
  - **Creados:**
    - `backend/app/models/categoria.py`
    - `backend/app/schemas/categoria.py`
    - `backend/app/repositories/categoria_repository.py`
    - `backend/app/services/categoria_service.py`
    - `backend/app/routers/categoria_router.py`
    - `backend/migrations/001_create_categorias.sql`
    - `backend/migrations/migrate.py`
    - `backend/tests/test_categoria_service.py`
    - `backend/tests/test_categoria_router.py`
    - `frontend/src/components/Categorias.jsx`
  - **Modificados:**
    - `backend/app/core/database.py`
    - `backend/app/main.py`
    - `backend/app/models/__init__.py`
    - `backend/app/repositories/__init__.py`
    - `backend/app/routers/__init__.py`
    - `backend/app/schemas/__init__.py`
    - `backend/app/services/__init__.py`
    - `frontend/src/App.jsx`
    - `frontend/src/index.css`
    - `README.md`
- **Pruebas realizadas:**
  - **Unitarias (pytest):**
    - `backend/tests/test_categoria_service.py` (14 pruebas): creación exitosa, control de nombre duplicado, rechazo por plazo < 1 o > 180, validación de nombre vacío, obtención por ID existente e inexistente, listado total y solo activas, actualización con validación de unicidad y plazo, borrado lógico.
    - `backend/tests/test_categoria_router.py` (11 pruebas): verificación de respuestas HTTP 201 Created, 200 OK, 400 Bad Request, 404 Not Found y 422 Unprocessable Content.
  - **Manuales:**
    - Registro de categorías con plazos válidos desde la interfaz React.
    - Verificación del bloqueo al intentar ingresar plazos superiores a 180 días o nombres duplicados.
    - Actualización de plazos y descripciones.
    - Desactivación lógica y filtrado con la casilla "Ver solo activas".
- **Pendientes o puntos por confirmar:**
  - Ninguno. Módulo funcional y persistente.

---

## 3. 2026-09-18 — Feature del CRUD de Equipos

- **Commit:** `37a2a2c` (*Feature del CRUD de Equipos*)
- **Resumen:**
  - Implementación del ciclo de vida para los equipos del laboratorio asignados a categorías, con control de número secuencial único, estado de mantenimiento y borrado lógico.
  - Modelo ORM `Equipo` y migración SQL `002_create_equipos.sql` con llave foránea hacia `categoria.id`.
  - Capa de datos `EquipoRepository` y reglas en `EquipoService`.
  - Endpoints REST en `equipo_router.py` bajo `/api/equipos` con filtros por categoría, mantenimiento y estado activo.
  - Componente React `Equipos.jsx` con navegación por pestañas (`Categorías` y `Equipos`), formularios con validaciones, listado con badges de estado y opciones de edición.
- **Decisiones y reglas de negocio aplicadas:**
  - **ADR-002 y ADR-003:** Persistencia relacional en MySQL y separación de responsabilidades por capas.
  - **MODELS.md (Sección 3):** Campos requeridos: `secuencial` único, `id_categoria`, `mantenimiento`, `fecha_creacion`, `activo`.
  - **RN-EQ-01:** La categoría asociada debe existir y encontrarse activa (`activo == True`).
  - **RN-EQ-02:** El secuencial interno del laboratorio es obligatorio y debe ser único en el sistema (insensible a mayúsculas/minúsculas).
  - **RN-EQ-03:** Valores por defecto al registrar: `mantenimiento = False`, `activo = True`, `fecha_creacion = date.today()`.
  - **RN-EQ-04:** Nombre (máx. 150) y secuencial (máx. 50) obligatorios y no vacíos.
  - **RN-EQ-05:** Comprobación de existencia para consulta y actualización.
  - **RN-EQ-06:** Borrado lógico mediante `activo = False`.
- **Archivos creados o modificados:**
  - **Creados:**
    - `backend/app/models/equipo.py`
    - `backend/app/schemas/equipo.py`
    - `backend/app/repositories/equipo_repository.py`
    - `backend/app/services/equipo_service.py`
    - `backend/app/routers/equipo_router.py`
    - `backend/migrations/002_create_equipos.sql`
    - `backend/tests/test_equipo_service.py`
    - `backend/tests/test_equipo_router.py`
    - `frontend/src/components/Equipos.jsx`
  - **Modificados:**
    - `backend/app/core/database.py`
    - `backend/app/main.py`
    - `backend/app/models/__init__.py`
    - `backend/app/repositories/__init__.py`
    - `backend/app/routers/__init__.py`
    - `backend/app/schemas/__init__.py`
    - `backend/app/services/__init__.py`
    - `backend/migrations/migrate.py`
    - `frontend/src/App.jsx`
    - `frontend/src/index.css`
    - `README.md`
- **Pruebas realizadas:**
  - **Unitarias (pytest):**
    - `backend/tests/test_equipo_service.py` (17 pruebas): registro exitoso, rechazo por categoría inexistente o inactiva, rechazo por secuencial duplicado, rechazo por campos vacíos, consulta por ID, filtros de búsqueda, actualización de datos, borrado lógico y reactivación.
    - `backend/tests/test_equipo_router.py` (12 pruebas): endpoints `POST`, `GET`, `PUT`, `DELETE` con códigos 200, 201, 400, 404, 422.
  - **Manuales:**
    - Registro de equipos asociándolos a categorías activas en el frontend.
    - Verificación del bloqueo si la categoría está inactiva o si el secuencial ya existe.
    - Filtros en tiempo real por categoría y por estado de mantenimiento.
    - Edición de información y cambio manual de estado a mantenimiento.
- **Pendientes o puntos por confirmar:**
  - Inicialmente, sacar un equipo de mantenimiento dependía del formulario de edición general; quedó pendiente habilitar una acción operativa directa para rehabilitarlo.

---

## 4. 2026-09-18 — Feature de CRUD de Persona

- **Commit:** `3423748` (*Feature de CRUD de Persona*)
- **Resumen:**
  - Implementación del ciclo de vida para los solicitantes de préstamos (`Persona`), admitiendo roles de estudiante o profesor.
  - Modelo ORM `Persona` con llave primaria en el campo `cedula` y migración SQL `003_create_personas.sql`.
  - Capa de datos `PersonaRepository` y servicio `PersonaService` con validaciones de formatos numéricos, longitudes y expresiones regulares.
  - Endpoints REST en `persona_router.py` bajo `/api/personas` con filtros por tipo, facultad y búsqueda de texto.
  - Componente React `Personas.jsx` con formulario de alta, validación en cliente, visualización en tabla, filtros combinados y edición inmutable de la cédula.
- **Decisiones y reglas de negocio aplicadas:**
  - **ADR-002 y ADR-003:** Arquitectura limpia y DTOs en Pydantic.
  - **SUP-01:** La persona es administrada por el encargado del laboratorio; no son usuarios que inicien sesión.
  - **SUP-09:** La facultad a la que pertenece la persona se almacena como texto libre.
  - **RN-PER-01:** Cédula obligatoria, exclusivamente numérica, entre 6 y 15 dígitos, única en el sistema e inmutable tras creación.
  - **RN-PER-02:** Nombre completo obligatorio, no vacío, longitud máxima de 100 caracteres.
  - **RN-PER-03:** Tipo de persona restringido al enum `profesor` o `estudiante`.
  - **RN-PER-04:** Teléfono obligatorio, exclusivamente numérico, entre 7 y 15 dígitos.
  - **RN-PER-05:** Facultad obligatoria, no vacía, máximo 150 caracteres.
  - **RN-PER-06:** Correo electrónico opcional; si se suministra debe cumplir formato de email válido.
  - **RN-PER-07:** Borrado lógico mediante `activo = False`.
- **Archivos creados o modificados:**
  - **Creados:**
    - `backend/app/models/persona.py`
    - `backend/app/schemas/persona.py`
    - `backend/app/repositories/persona_repository.py`
    - `backend/app/services/persona_service.py`
    - `backend/app/routers/persona_router.py`
    - `backend/migrations/003_create_personas.sql`
    - `backend/tests/test_persona_service.py`
    - `backend/tests/test_persona_router.py`
    - `frontend/src/components/Personas.jsx`
  - **Modificados:**
    - `backend/app/core/database.py`
    - `backend/app/main.py`
    - `backend/app/models/__init__.py`
    - `backend/app/repositories/__init__.py`
    - `backend/app/routers/__init__.py`
    - `backend/app/schemas/__init__.py`
    - `backend/app/services/__init__.py`
    - `backend/migrations/migrate.py`
    - `frontend/src/App.jsx`
    - `frontend/src/index.css`
    - `README.md`
- **Pruebas realizadas:**
  - **Unitarias (pytest):**
    - `backend/tests/test_persona_service.py` (17 pruebas): alta de profesor y estudiante, duplicidad de cédula, validación de cédula numérica y longitud, validación de nombre, teléfono numérico, facultad obligatoria, tipo de persona, correo con formato inválido, búsqueda por cédula, filtros y borrado lógico.
    - `backend/tests/test_persona_router.py` (9 pruebas): respuestas HTTP para todos los métodos REST sobre `/api/personas`.
  - **Manuales:**
    - Registro de personas profesor y estudiante desde la interfaz.
    - Comprobación del rechazo al ingresar letras en cédula o teléfono, o correos mal formateados.
    - Búsqueda en tiempo real por nombre o cédula.
    - Desactivación lógica y persistencia del estado en la base de datos.
- **Pendientes o puntos por confirmar:**
  - Ninguno. El catálogo de personas quedó listo para integrarse al módulo de préstamos.

---

## 5. 2026-09-19 — Feature de Creación de Préstamos con Validación de Reglas de Negocio

- **Commit:** `513bc74` (*Feature de creacion de Prestamos con validacion de reglas de negocio*)
- **Resumen:**
  - Implementación del núcleo funcional para el registro de préstamos de equipos de laboratorio.
  - Creación de los modelos ORM `Prestamo` y `Devolucion` con sus respectivas relaciones de integridad referencial.
  - Script SQL de migración `004_create_prestamos_y_devoluciones.sql` con llaves foráneas e índices.
  - Creación de `PrestamoRepository` y desarrollo de las reglas de dominio en `PrestamoService`.
  - Endpoints REST en `prestamo_router.py` (`POST /api/prestamos` y `GET /api/prestamos/{id}`).
  - Pestaña de interfaz React `Prestamos.jsx` con formulario de solicitud, selección guiada de persona y equipo, cálculo reactivo de la fecha estimada de devolución y feedback de errores.
- **Decisiones y reglas de negocio aplicadas:**
  - **ADR-002 y ADR-003:** Lógica de negocio rigurosamente aislada en la capa de servicios.
  - **SUP-04 y SUP-05:** La fecha esperada de entrega se calcula automáticamente sumando el plazo de la categoría del equipo en días calendario.
  - **SUP-06:** La fecha esperada se calcula y persiste en el préstamo; futuros cambios en el plazo de la categoría no modifican los préstamos ya concedidos.
  - **RN-PREST-01:** Bloqueo de préstamo a solicitantes que tengan algún préstamo vencido sin devolver.
  - **RN-PREST-02:** Bloqueo de préstamo si el equipo está marcado en mantenimiento (`mantenimiento == True`).
  - **RN-PREST-03:** Bloqueo de préstamo simultáneo si el equipo ya se encuentra prestado y no ha sido devuelto.
  - **RN-PREST-04:** Verificación de que la persona, el equipo y la categoría existan y estén activos (`activo == True`).
  - **RN-PREST-05:** Cálculo automático: `fecha_devolucion_esperada = fecha_prestamo + categoria.plazo_entrega`.
  - **RN-PREST-06:** La fecha del préstamo no puede ser posterior a la fecha actual (`fecha_prestamo <= date.today()`).
- **Archivos creados o modificados:**
  - **Creados:**
    - `backend/app/models/prestamo.py`
    - `backend/app/models/devolucion.py`
    - `backend/app/schemas/prestamo.py`
    - `backend/app/repositories/prestamo_repository.py`
    - `backend/app/services/prestamo_service.py`
    - `backend/app/routers/prestamo_router.py`
    - `backend/migrations/004_create_prestamos_y_devoluciones.sql`
    - `backend/tests/test_prestamo_service.py`
    - `backend/tests/test_prestamo_router.py`
    - `frontend/src/components/Prestamos.jsx`
  - **Modificados:**
    - `backend/app/core/database.py`
    - `backend/app/main.py`
    - `backend/app/models/__init__.py`
    - `backend/app/repositories/__init__.py`
    - `backend/app/routers/__init__.py`
    - `backend/app/schemas/__init__.py`
    - `backend/app/services/__init__.py`
    - `backend/migrations/migrate.py`
    - `frontend/src/App.jsx`
    - `README.md`
- **Pruebas realizadas:**
  - **Unitarias (pytest):**
    - `backend/tests/test_prestamo_service.py` (13 pruebas): creación exitosa, rechazo por préstamo vencido sin devolver, aprobación si préstamos vencidos anteriores ya fueron devueltos, aprobación si préstamos vigentes no están vencidos, rechazo por equipo en mantenimiento, rechazo por equipo ya prestado, rechazo por persona o equipo inexistente o inactivo, rechazo por categoría inactiva, rechazo por fecha futura, consulta por ID.
    - `backend/tests/test_prestamo_router.py` (7 pruebas): endpoints de creación y consulta con códigos 201, 400, 404, 422.
  - **Manuales:**
    - Registro exitoso de un préstamo verificando el cálculo exacto de la fecha límite según la categoría.
    - Intento de préstamo a un usuario con préstamo vencido no devuelto (bloqueo con mensaje descriptivo).
    - Intento de préstamo a un equipo en mantenimiento o ya prestado (bloqueo validado).
- **Pendientes o puntos por confirmar:**
  - Quedó pendiente incorporar la visualización completa del historial de préstamos con filtros y la gestión de devoluciones.

---

## 6. 2026-09-19 — Funcionalidad: Listar Préstamos

- **Commit:** `37a1f6a` (*Funcionalidad- Listar Prestamos*)
- **Resumen:**
  - Implementación del listado general e historial de préstamos con soporte para múltiples filtros combinados.
  - Métodos de consulta con filtros dinámicos en `PrestamoRepository.listar` y `PrestamoService.listar_prestamos`.
  - Endpoint REST `GET /api/prestamos` con query parameters: `id_categoria`, `fecha_desde`, `fecha_hasta`, y `estado` (`vigente` o `vencido`).
  - Interfaz gráfica enriquecida en `Prestamos.jsx` con panel de filtros, badges de estado (`🟢 Vigente`, `🔴 Vencido`, `⚪ Devuelto`) y recarga automática tras registrar nuevos préstamos.
- **Decisiones y reglas de negocio aplicadas:**
  - **ADR-003:** Las validaciones de los parámetros de consulta se ubican en `PrestamoService`.
  - **RN-PREST-LIST-01:** Si se envían `fecha_desde` y `fecha_hasta`, se valida que `fecha_desde <= fecha_hasta`; de lo contrario se rechaza con error 400.
  - **RN-PREST-LIST-02:** El parámetro `estado` solo admite valores `vigente` o `vencido` (case-insensitive).
  - **RN-PREST-LIST-03:** El parámetro `id_categoria` debe ser un entero positivo (> 0).
  - Cálculo dinámico de la propiedad de estado (`devuelto`, `vencido`, `vigente`) según la fecha actual del sistema y la presencia del registro de devolución.
- **Archivos creados o modificados:**
  - **Modificados:**
    - `backend/app/models/prestamo.py`
    - `backend/app/schemas/prestamo.py`
    - `backend/app/repositories/prestamo_repository.py`
    - `backend/app/services/prestamo_service.py`
    - `backend/app/routers/prestamo_router.py`
    - `backend/tests/test_prestamo_service.py`
    - `backend/tests/test_prestamo_router.py`
    - `frontend/src/components/Prestamos.jsx`
    - `frontend/src/index.css`
    - `README.md`
- **Pruebas realizadas:**
  - **Unitarias (pytest):**
    - `backend/tests/test_prestamo_service.py` (9 pruebas adicionales): listado sin filtros, filtro por categoría, filtro por rango de fechas válido, error por rango de fechas invertido, filtro por estado vigente, filtro por estado vencido, error por estado inválido, error por categoría <= 0, combinación de múltiples filtros.
    - `backend/tests/test_prestamo_router.py` (3 pruebas adicionales): endpoint `GET /api/prestamos` con parámetros y manejo de error 400.
  - **Manuales:**
    - Filtrado del historial por categoría desde el select de React.
    - Filtrado por rango de fechas inicio/fin comprobando la consistencia de los resultados.
    - Filtrado por estado `vigente` vs `vencido`.
    - Botón de limpieza de filtros restableciendo el listado completo.
- **Pendientes o puntos por confirmar:**
  - Faltaba la acción de registrar la devolución efectiva de los equipos desde las filas de la tabla.

---

## 7. 2026-09-19 — Funcionalidad: Crear Devolución de un Equipo

- **Commit:** `f38a11b` (*Funcionalidad- Crear Devolucion de un equipo*)
- **Resumen:**
  - Implementación del registro de devolución de equipos prestados, cerrando el ciclo de vida del préstamo.
  - Creación del esquema Pydantic `DevolucionCreate` en `backend/app/schemas/devolucion.py`.
  - Método `registrar_devolucion` en `PrestamoService` que persiste el registro en la tabla `devolucion`, actualiza la relación del préstamo y modifica el estado de mantenimiento del equipo según lo determine el administrador.
  - Endpoint REST `POST /api/prestamos/{id}/devolucion`.
  - Componente frontend `Prestamos.jsx` actualizado con el botón **📥 Devolver Equipo**, formulario modal/tarjeta de recepción con fecha, checkbox de mantenimiento y validación obligatoria de novedades ante daños reportados.
- **Decisiones y reglas de negocio aplicadas:**
  - **ADR-003:** Integración coordinada de `PrestamoRepository` y `EquipoRepository` a nivel de servicio.
  - **SUP-08:** Cuando un equipo se devuelve con novedad, el administrador decide si debe enviarse a mantenimiento.
  - **RN-DEV-01:** El préstamo a devolver debe existir en la base de datos.
  - **RN-DEV-02:** No se puede devolver un préstamo que ya fue devuelto previamente.
  - **RN-DEV-03:** La fecha de devolución no puede ser posterior a la fecha actual ni anterior a la fecha de inicio del préstamo.
  - **RN-DEV-04:** Si el equipo se marca para pasar a mantenimiento, el campo `novedades` es estrictamente obligatorio.
  - **RN-DEV-05:** Se actualiza automáticamente el campo `mantenimiento` del equipo asociado en función de la decisión del administrador.
  - **RN-DEV-06:** Se persiste el registro de devolución y el préstamo queda marcado como `⚪ Devuelto`, liberando al solicitante de bloqueos por préstamos vencidos.
- **Archivos creados o modificados:**
  - **Creados:**
    - `backend/app/schemas/devolucion.py`
  - **Modificados:**
    - `backend/app/models/prestamo.py`
    - `backend/app/schemas/__init__.py`
    - `backend/app/schemas/prestamo.py`
    - `backend/app/repositories/prestamo_repository.py`
    - `backend/app/services/prestamo_service.py`
    - `backend/app/routers/prestamo_router.py`
    - `backend/tests/test_prestamo_service.py`
    - `backend/tests/test_prestamo_router.py`
    - `frontend/src/components/Prestamos.jsx`
    - `frontend/src/index.css`
    - `README.md`
- **Pruebas realizadas:**
  - **Unitarias (pytest):**
    - `backend/tests/test_prestamo_service.py` (9 pruebas adicionales): devolución exitosa sin mantenimiento, devolución exitosa con mantenimiento y novedades, fecha por defecto hoy, error por préstamo inexistente, error por préstamo ya devuelto, error por fecha futura, error por fecha anterior al préstamo, error por marcar mantenimiento sin novedades, error si equipo no existe.
    - `backend/tests/test_prestamo_router.py` (3 pruebas adicionales): endpoint `POST /api/prestamos/{id}/devolucion` con códigos 200, 404 y 400.
  - **Manuales:**
    - Devolución operativa sin mantenimiento: verificar que el préstamo pasa a estado devuelto y el equipo queda disponible para nuevos préstamos.
    - Devolución con envío a mantenimiento intentando omitir las novedades: verificar que el sistema detiene la operación y exige la descripción.
    - Devolución completada con novedades y mantenimiento: verificar que el equipo pasa a `🔧 En Mantenimiento` y no puede prestarse nuevamente hasta ser reparado.
- **Pendientes o puntos por confirmar:**
  - Quedó pendiente la opción de prorrogar préstamos activos antes de su devolución.

---

## 8. 2026-09-20 — Funcionalidad: Prorrogar Préstamo

- **Commit:** `258bc86` (*Funcionalidad: Prorrogar prestamo*)
- **Resumen:**
  - Implementación del flujo de prórroga para extender la fecha esperada de entrega de préstamos vigentes.
  - Esquema Pydantic `PrestamoProrrogaCreate` en `backend/app/schemas/prestamo.py`.
  - Método `prorrogar_prestamo` en `PrestamoService` con validaciones de vigencia, coherencia temporal y límite máximo de duración.
  - Endpoint REST `POST /api/prestamos/{id}/prorroga`.
  - Interfaz de prórroga en `Prestamos.jsx`: botón interactivo **⏱️ Prorrogar**, tarjeta desplegable con cálculo automático de la fecha máxima permitida (6 meses / 180 días desde el inicio) y actualización en vivo en la tabla de préstamos.
- **Decisiones y reglas de negocio aplicadas:**
  - **ADR-003:** Reglas de prórroga encapsuladas en `PrestamoService`.
  - **SUP-07:** Un préstamo puede prorrogarse hasta un máximo de 6 meses contados a partir de la fecha de entrega/inicio del equipo (`fecha_prestamo + 180 días calendario`). La duración total, incluidas las prórrogas, no puede superar los 6 meses.
  - **RN-PRORR-01:** El préstamo a prorrogar debe existir en el sistema.
  - **RN-PRORR-02:** No se puede prorrogar un préstamo que ya haya sido devuelto.
  - **RN-PRORR-03:** Solo se pueden prorrogar préstamos vigentes (`fecha_devolucion_esperada >= date.today()`); los préstamos vencidos no admiten prórroga.
  - **RN-PRORR-04:** La nueva fecha esperada debe ser estrictamente posterior a la fecha esperada actual.
  - **RN-PRORR-05:** La nueva fecha esperada no puede exceder el límite absoluto de 180 días calendario desde la fecha de inicio del préstamo.
  - **RN-PRORR-06:** Se actualiza `fecha_devolucion_esperada` en el registro y se persiste en base de datos.
- **Archivos creados o modificados:**
  - **Modificados:**
    - `backend/app/schemas/prestamo.py`
    - `backend/app/repositories/prestamo_repository.py`
    - `backend/app/services/prestamo_service.py`
    - `backend/app/routers/prestamo_router.py`
    - `backend/tests/test_prestamo_service.py`
    - `backend/tests/test_prestamo_router.py`
    - `frontend/src/components/Prestamos.jsx`
    - `README.md`
- **Pruebas realizadas:**
  - **Unitarias (pytest):**
    - `backend/tests/test_prestamo_service.py` (7 pruebas adicionales): prórroga exitosa, prórroga en el límite exacto de 180 días, error si el préstamo no existe, error si el préstamo ya fue devuelto, error si el préstamo está vencido, error si la nueva fecha es igual o menor a la actual esperada, error si la nueva fecha supera los 180 días calendario.
    - `backend/tests/test_prestamo_router.py` (4 pruebas adicionales): endpoint `POST /api/prestamos/{id}/prorroga` con respuestas 200 OK, 400 Bad Request, 404 Not Found y 422 Unprocessable Content.
  - **Manuales:**
    - Prórroga exitosa seleccionando una fecha válida dentro del límite permitido en frontend.
    - Intento de prorrogar seleccionando una fecha anterior o igual a la actual esperada (mensaje de validación mostrado).
    - Intento de prorrogar seleccionando una fecha más allá de los 180 días desde el inicio (rechazo inmediato).
    - Comprobación de que préstamos vencidos o devueltos no permiten iniciar el flujo de prórroga.
- **Pendientes o puntos por confirmar:**
  - Faltaba una vía operativa directa para que el administrador pudiera rehabilitar un equipo en mantenimiento una vez concluida su reparación técnica.

---

## 9. 2026-09-20 — Funcionalidad: Cambiar el Estado de un Equipo en Mantenimiento a Vigente para ser Prestado

- **Commit:** `46fad84` (*Funcionalidad: Cambiar el estado de un equipo en mantenimiento a vigente para ser prestado*)
- **Resumen:**
  - Implementación de la acción operativa que permite al administrador cambiar el estado de un equipo que se encuentra en mantenimiento a vigente / disponible (`mantenimiento = False`).
  - Creación del método `sacar_de_mantenimiento` en `EquipoService` con validaciones de existencia, estado activo y verificación de que el equipo esté efectivamente en mantenimiento.
  - Creación del endpoint REST dedicado `POST /api/equipos/{id}/sacar-mantenimiento` en `equipo_router.py`.
  - Integración en frontend `Equipos.jsx` con el botón directo **✅ Disponible** en la tabla de equipos para los registros que posean estado `🔧 En Mantenimiento`, con confirmación y refresco inmediato.
- **Decisiones y reglas de negocio aplicadas:**
  - **ADR-003:** Cumplimiento de la arquitectura en capas con la lógica encapsulada en `EquipoService`.
  - **SUP-08:** Cierre del ciclo de mantenimiento de equipos para su reintegración al catálogo de equipos prestables.
  - **RN-EQ-MANT-01:** El equipo debe existir en el sistema (error 404 si no se encuentra).
  - **RN-EQ-MANT-02:** El equipo debe encontrarse actualmente en mantenimiento (`mantenimiento == True`). Si ya estaba disponible, se rechaza la solicitud (error 400).
  - **RN-EQ-MANT-03:** El equipo debe encontrarse activo (`activo == True`); un equipo desactivado por borrado lógico no puede cambiar de estado de mantenimiento.
  - **RN-EQ-MANT-04:** El sistema cambia el campo `mantenimiento = False`, persiste la entidad y permite que el equipo vuelva a ser seleccionado inmediatamente en nuevos préstamos.
- **Archivos creados o modificados:**
  - **Modificados:**
    - `backend/app/services/equipo_service.py`
    - `backend/app/routers/equipo_router.py`
    - `backend/tests/test_equipo_service.py`
    - `backend/tests/test_equipo_router.py`
    - `frontend/src/components/Equipos.jsx`
    - `frontend/src/index.css`
    - `README.md`
- **Pruebas realizadas:**
  - **Unitarias (pytest):**
    - `backend/tests/test_equipo_service.py` (4 pruebas adicionales): reactivación exitosa de equipo en mantenimiento a disponible, error si el equipo no existe, error si el equipo no estaba en mantenimiento, error si el equipo está inactivo.
    - `backend/tests/test_equipo_router.py` (3 pruebas adicionales): endpoint `POST /api/equipos/{id}/sacar-mantenimiento` con respuestas 200 OK, 404 Not Found y 400 Bad Request.
    - Suite completa ejecutada: 148 pruebas unitarias pasando al 100%.
  - **Manuales:**
    - Envío de un equipo a mantenimiento (mediante devolución con daños o desde el formulario de edición).
    - Clic en el botón **✅ Disponible** en la tabla de equipos en frontend y confirmación de la acción.
    - Verificación del cambio visual a `✅ Operativo`.
    - Comprobación en la pestaña **📋 Préstamos** de que el equipo rehabilitado reaparece disponible y puede ser prestado sin bloqueos.
- **Pendientes o puntos por confirmar:**
  - Ninguno. El ciclo completo de gestión de inventario, solicitantes, préstamos, devoluciones, prórrogas y rehabilitación de mantenimiento se encuentra cubierto, probado y documentado.
