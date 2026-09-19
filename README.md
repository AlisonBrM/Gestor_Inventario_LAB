# Gestor de Inventario y Préstamos de Laboratorio

Sistema de Información para gestionar los préstamos de equipos en un laboratorio universitario.

## Estructura del Proyecto

```text
GestionInventarioLab/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuración y conexión a base de datos
│   │   ├── models/        # Modelos de datos (ORM)
│   │   ├── schemas/       # DTOs y validaciones (Pydantic)
│   │   ├── repositories/  # Acceso a datos
│   │   ├── services/      # Lógica y reglas de negocio
│   │   ├── routers/       # Endpoints REST de la API
│   │   └── main.py        # Instancia y configuración principal de FastAPI
│   ├── migrations/        # Migraciones de base de datos
│   ├── tests/             # Pruebas unitarias y de integración (pytest)
│   ├── requirements.txt   # Dependencias de Python
│   └── .env.example       # Plantilla de variables de entorno
├── frontend/
│   ├── src/
│   │   ├── App.jsx        # Componente principal de prueba
│   │   ├── main.jsx       # Punto de entrada de React
│   │   └── index.css      # Estilos base
│   ├── package.json       # Dependencias de npm
│   ├── vite.config.js     # Configuración de Vite con proxy hacia backend
│   └── index.html         # HTML base
├── docker-compose.yml     # Servicio de base de datos MySQL con volumen persistente
└── README.md
```

---

## Requisitos Previos

- **Docker y Docker Compose** (Docker Desktop en Windows)
- **Python 3.11+**
- **Node.js 18+** y **npm**

---

## 1. Base de Datos (MySQL en Docker)

El servicio de base de datos se ejecuta en un contenedor MySQL 8.0 con un volumen persistente (`mysql_data`) para mantener los datos entre ejecuciones.

### Iniciar el contenedor:

```bash
docker compose up -d
```

### Detener el contenedor:

```bash
docker compose down
```

### Credenciales por defecto:
- **Host:** `localhost`
- **Puerto:** `3306`
- **Base de datos:** `lab_inventory`
- **Usuario:** `lab_user`
- **Contraseña:** `lab_password`
- **Root Password:** `root_password`

---

## 2. Backend (FastAPI + Python `venv`)

### Configurar el entorno virtual:

Si no existe, crea el entorno virtual e instala las dependencias:

```bash
# En Windows (PowerShell / CMD):
python -m venv backend/venv

# Activar el entorno virtual:
# En PowerShell:
.\backend\venv\Scripts\Activate.ps1
# O en CMD:
backend\venv\Scripts\activate.bat

# Instalar dependencias:
pip install -r backend/requirements.txt
```

### Variables de entorno:

Copia el archivo `.env.example` a `.env` dentro de `backend/`:

```bash
copy backend\.env.example backend\.env
```

### Ejecutar el servidor de desarrollo:

Desde la carpeta raíz del proyecto:

```bash
backend\venv\Scripts\uvicorn app.main:app --app-dir backend --reload --port 8000
```

O desde la carpeta `backend/`:

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### Documentación interactiva de la API:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Ejecutar pruebas con pytest:

```bash
# Desde la raíz del proyecto con la variable de entorno PYTHONPATH configurada:
backend\venv\Scripts\pytest backend\tests
```

---

## 3. Frontend (React + Vite)

Frontend minimalista diseñado para probar las funcionalidades del backend.

### Instalar dependencias:

```bash
cd frontend
npm install
```

### Iniciar el servidor de desarrollo:

```bash
npm run dev
```

La aplicación estará disponible en [http://localhost:5173](http://localhost:5173). Tiene configurado un proxy automático hacia el backend en `http://127.0.0.1:8000`.

---

## Endpoints Disponibles

### Base y Diagnóstico
| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/` | Información general de la API y estado de ejecución |
| `GET` | `/api/health` | Verificación de salud (Health check) |
| `GET` | `/docs` | Documentación interactiva OpenAPI (Swagger UI) |
| `GET` | `/redoc` | Documentación ReDoc |

### Módulo de Categorías (`/api/categorias`)
| Método | Ruta | Parámetros / Body | Descripción | Códigos de Respuesta |
|---|---|---|---|---|
| `POST` | `/api/categorias` | Body JSON: `CategoriaCreate` | Crea una nueva categoría con nombre y plazo de entrega | `201 Created`, `400 Bad Request` |
| `GET` | `/api/categorias` | Query: `solo_activas=true` (opcional) | Lista las categorías registradas | `200 OK` |
| `GET` | `/api/categorias/{id}` | Path: `id` (entero) | Retorna los detalles de una categoría | `200 OK`, `404 Not Found` |
| `PUT` | `/api/categorias/{id}` | Path: `id`, Body JSON: `CategoriaUpdate` | Actualiza los datos de una categoría | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/categorias/{id}` | Path: `id` (entero) | Borrado lógico: establece `activo = False` | `200 OK`, `404 Not Found` |

### Módulo de Equipos (`/api/equipos`)
| Método | Ruta | Parámetros / Body | Descripción | Códigos de Respuesta |
|---|---|---|---|---|
| `POST` | `/api/equipos` | Body JSON: `EquipoCreate` | Registra un nuevo equipo con `mantenimiento=False`, `activo=True` y `fecha_creacion=hoy` | `201 Created`, `400 Bad Request` |
| `GET` | `/api/equipos` | Query:<br>- `solo_activos=true` (opcional)<br>- `id_categoria={id}` (opcional)<br>- `en_mantenimiento={true/false}` (opcional) | Lista los equipos registrados aplicando los filtros especificados | `200 OK` |
| `GET` | `/api/equipos/{id}` | Path: `id` (entero) | Retorna los detalles de un equipo | `200 OK`, `404 Not Found` |
| `PUT` | `/api/equipos/{id}` | Path: `id`, Body JSON: `EquipoUpdate` | Actualiza los datos de un equipo (nombre, descripción, categoría, mantenimiento, activo) | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/equipos/{id}` | Path: `id` (entero) | Borrado lógico: establece `activo = False` | `200 OK`, `404 Not Found` |

### Módulo de Personas (`/api/personas`)
| Método | Ruta | Parámetros / Body | Descripción | Códigos de Respuesta |
|---|---|---|---|---|
| `POST` | `/api/personas` | Body JSON: `PersonaCreate` | Registra una nueva persona (profesor o estudiante) con `activo=True` | `201 Created`, `400 Bad Request` |
| `GET` | `/api/personas` | Query:<br>- `solo_activas=true` (opcional)<br>- `tipo_persona={profesor/estudiante}` (opcional)<br>- `facultad={texto}` (opcional)<br>- `busqueda={texto}` (opcional) | Lista las personas registradas aplicando los filtros especificados | `200 OK` |
| `GET` | `/api/personas/{cedula}` | Path: `cedula` (string) | Retorna los detalles de una persona por su cédula | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `PUT` | `/api/personas/{cedula}` | Path: `cedula`, Body JSON: `PersonaUpdate` | Actualiza los datos de una persona (la cédula es inmutable) | `200 OK`, `400 Bad Request`, `404 Not Found` |
| `DELETE` | `/api/personas/{cedula}` | Path: `cedula` (string) | Borrado lógico: establece `activo = False` | `200 OK`, `400 Bad Request`, `404 Not Found` |

### Módulo de Préstamos (`/api/prestamos`)
| Método | Ruta | Parámetros / Body | Descripción | Códigos de Respuesta |
|---|---|---|---|---|
| `POST` | `/api/prestamos` | Body JSON: `PrestamoCreate` | Registra un nuevo préstamo validando reglas de negocio (solicitante sin préstamos vencidos, equipo operativo, etc.) y calcula la fecha de devolución esperada | `201 Created`, `400 Bad Request`, `404 Not Found`, `422 Unprocessable Content` |
| `GET` | `/api/prestamos` | Query:<br>- `id_categoria={id}` (opcional)<br>- `fecha_desde={YYYY-MM-DD}` (opcional)<br>- `fecha_hasta={YYYY-MM-DD}` (opcional)<br>- `estado={vigente/vencido}` (opcional) | Lista todos los préstamos registrados aplicando los filtros opcionales de categoría, rango de fechas y estado | `200 OK`, `400 Bad Request` |
| `GET` | `/api/prestamos/{id}` | Path: `id` (entero) | Retorna los datos detallados de un préstamo por su ID | `200 OK`, `404 Not Found` |

---

## Cómo Probar las Funcionalidades

### 1. Iniciar los servicios:
1. Asegúrate de tener MySQL corriendo con Docker (`docker compose up -d`).
2. Inicia el backend:
   ```bash
   backend\venv\Scripts\uvicorn app.main:app --app-dir backend --reload --port 8000
   ```
3. En otra terminal, inicia el frontend:
   ```bash
   cd frontend
   npm.cmd run dev
   ```

### 2. Pruebas manuales desde el Frontend:
Abre [http://localhost:5173](http://localhost:5173) en el navegador. La aplicación cuenta con navegación por pestañas en la parte superior: **👤 Personas**, **📦 Equipos de Laboratorio**, **🏷️ Categorías** y **📋 Préstamos**.

#### A. Pruebas del Módulo de Personas:
- Cambia a la pestaña **👤 Personas**.
- **Crear Persona:**
  - Ingresa una cédula válida de 6 a 15 dígitos numéricos (ej. `1001234567`).
  - Ingresa el nombre completo (ej. `Ana María Gómez`).
  - Selecciona el tipo de persona (`Estudiante` o `Profesor`).
  - Ingresa el número celular de 7 a 15 dígitos numéricos (ej. `3001234567`).
  - Opcionalmente añade un correo electrónico válido (ej. `ana.gomez@universidad.edu.co`).
  - Ingresa la facultad a la que pertenece (ej. `Facultad de Ingeniería`).
  - Haz clic en **+ Registrar Persona**. La persona se creará con estado `Activo`.
- **Validación de reglas:**
  - Intenta registrar otra persona con la misma cédula `1001234567`; el sistema rechazará la creación por duplicidad (RN-PER-01).
  - Intenta ingresar una cédula o teléfono con letras o con longitud fuera del rango permitido; el sistema mostrará un mensaje de validación.
  - Intenta ingresar un correo electrónico con formato inválido; el sistema no lo admitirá.
- **Listar y Filtrar:**
  - Filtra por **Tipo de Persona** (Estudiantes o Profesores).
  - Busca por **Cédula o Nombre** en tiempo real.
  - Filtra por nombre de **Facultad**.
  - Alterna la casilla **Solo activas** para visualizar personas con borrado lógico.
- **Editar Persona:**
  - Haz clic en ✏️ **Editar** en una fila del directorio.
  - Nota que la cédula permanece fija (inmutable).
  - Modifica el nombre, teléfono, facultad, tipo o correo.
  - Marca o desmarca la casilla **Persona Activa** para reactivarla o desactivarla.
  - Haz clic en **Guardar Cambios**.
- **Borrado Lógico:**
  - Haz clic en 🗑️ **Desactivar** sobre una persona activa.
  - La persona pasará al estado `Inactivo` (`activo = false`) preservando su registro para integridad de préstamos futuros.

#### B. Pruebas del Módulo de Categorías:
- Cambia a la pestaña **🏷️ Categorías**.
- **Crear Categoría:** Ingresa un nombre (ej. "Equipos de Cómputo"), plazo de entrega (ej. 15 días) y descripción opcional. Haz clic en **+ Registrar Categoría**.
- **Validación de reglas:**
  - Intenta crear una categoría con un plazo mayor a 180 días o menor a 1 día; el formulario o el backend lo rechazarán.
  - Intenta crear una categoría con un nombre ya existente; se mostrará un mensaje de error indicando la duplicidad.
- **Listar y Filtrar:** Observa las categorías en la tabla inferior y usa la casilla "Ver solo activas" para alternar la visualización.
- **Editar Categoría:** Haz clic en ✏️ **Editar**, modifica el plazo o descripción y haz clic en **Guardar Cambios**. También puedes reactivar una categoría inactiva.
- **Borrado Lógico:** Haz clic en 🗑️ **Desactivar**. La categoría pasará a estado inactiva (`activo = false`) sin eliminarse físicamente de la base de datos.

#### C. Pruebas del Módulo de Equipos:
- Cambia a la pestaña **📦 Equipos de Laboratorio**.
- **Crear Equipo:**
  - Selecciona una categoría del desplegable (solo muestra categorías activas).
  - Ingresa un secuencial único (ej. `OSC-001`) y el nombre del equipo (ej. `Osciloscopio Digital Rigol 100MHz`).
  - Opcionalmente añade una descripción.
  - Haz clic en **+ Registrar Equipo**. El equipo se creará con estado `✅ Operativo` (`mantenimiento = false`), `Activo` (`activo = true`) y con la fecha del día asignada automáticamente.
- **Validación de reglas:**
  - Intenta registrar otro equipo con el mismo secuencial `OSC-001` (o en minúsculas `osc-001`); el sistema rechazará la creación por duplicidad.
  - Si una categoría es desactivada en la pestaña de categorías, no aparecerá disponible para registrar nuevos equipos.
- **Filtrar Equipos:**
  - Filtra por **Categoría** para ver únicamente los equipos asociados a ella.
  - Filtra por **Estado de Mantenimiento** (Operativos o En Mantenimiento).
  - Alterna la casilla **Solo activos** para incluir o excluir equipos con borrado lógico.
- **Editar Equipo:**
  - Haz clic en ✏️ **Editar** sobre un equipo.
  - Puedes cambiar el nombre, descripción, o cambiar su categoría a otra activa.
  - Puedes marcar la casilla **En Mantenimiento** para enviar el equipo a reparación (SUP-08). Al guardar, su estado cambiará a `🔧 En Mantenimiento`.
  - Puedes desmarcar/marcar **Equipo Activo** para gestionar su reactivación.
- **Borrado Lógico:**
  - Haz clic en 🗑️ **Desactivar**. El equipo se marcará como `Inactivo` (`activo = false`) preservando su registro en la base de datos.

#### D. Pruebas del Módulo de Préstamos:
- Cambia a la pestaña **📋 Préstamos**.
- **Crear un Préstamo Exitoso:**
  - Selecciona un solicitante activo en el menú desplegable (o escribe su cédula en el campo correspondiente).
  - Selecciona un equipo operativo (`✅ [Operativo]`) perteneciente a una categoría activa.
  - Verifica o ajusta la fecha de inicio del préstamo (por defecto la fecha de hoy).
  - Haz clic en **+ Registrar Préstamo**.
  - Observa el mensaje de éxito y la tarjeta verde con los detalles del préstamo:
    - ID asignado.
    - Nombre y cédula del solicitante.
    - Nombre, secuencial y categoría del equipo.
    - **Fecha de Devolución Esperada** calculada automáticamente sumando los días de plazo de la categoría a la fecha de préstamo.
- **Validación de Regla de Negocio 1 (Solicitante con préstamo vencido sin devolver):**
  - Si un solicitante tiene un préstamo cuya fecha esperada de devolución ya venció y no ha sido devuelto, intenta registrar un nuevo préstamo para él.
  - El sistema rechazará inmediatamente la solicitud con un mensaje de alerta: *"El solicitante con cédula '...' tiene un préstamo vencido sin devolver (Préstamo #X, fecha límite esperada: YYYY-MM-DD). No puede solicitar otro equipo hasta devolver los equipos vencidos."*
- **Validación de Regla de Negocio 2 (Equipo en mantenimiento):**
  - Ve a la pestaña **📦 Equipos de Laboratorio**, edita cualquier equipo y marca la casilla **En Mantenimiento**.
  - Regresa a la pestaña **📋 Préstamos** y selecciona ese equipo (marcado como `⚠️ [EN MANTENIMIENTO]`).
  - Haz clic en **+ Registrar Préstamo**.
  - El sistema rechazará la creación con el mensaje de error: *"El equipo '...' se encuentra marcado en mantenimiento. No puede ser prestado."*
- **Validación de Reglas Adicionales:**
  - **Equipo ya prestado:** Intenta prestar un equipo que ya fue asignado en un préstamo activo no devuelto; el sistema impedirá el préstamo duplicado.
  - **Persona o Equipo inactivo:** Si se ingresa la cédula de una persona inactiva o se intenta prestar un equipo inactivo, el sistema rechazará la operación.
  - **Fecha futura:** Si se ingresa una fecha posterior al día actual, el sistema lo rechazará indicando que no se admiten fechas futuras.
- **Listar Préstamos con Filtros:**
  - En la parte inferior de la pestaña **📋 Préstamos**, observa la tabla **Historial de Préstamos**.
  - **Filtrar por Categoría:** Selecciona una categoría en el menú desplegable. La tabla se actualizará mostrando únicamente los préstamos de equipos asociados a esa categoría.
  - **Filtrar por Rango de Fechas:** Ingresa una fecha en el campo **Desde** y/o en el campo **Hasta** para filtrar por la fecha en que se inició el préstamo (`fecha_prestamo`). Nota: Si intentas colocar una fecha "Desde" posterior a "Hasta", se mostrará un mensaje de validación.
  - **Filtrar por Estado:** Selecciona `🟢 Vigente` (préstamos activos cuya fecha límite aún no vence) o `🔴 Vencido` (préstamos activos cuya fecha esperada de devolución ya pasó) o `Todos los estados` (para incluir todos, incluso si hay devueltos).
  - **Limpiar Filtros:** Haz clic en el botón **✕ Limpiar** para restablecer todos los filtros a sus valores por defecto.
  - **Refresco Automático:** Al registrar un nuevo préstamo, la tabla se actualiza automáticamente mostrando el nuevo registro en la parte superior.