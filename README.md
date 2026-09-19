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
- Abre [http://localhost:5173](http://localhost:5173) en el navegador.
- **Crear Categoría:** Ingresa un nombre (ej. "Equipos de Cómputo"), plazo de entrega (ej. 15 días) y descripción opcional. Haz clic en **+ Registrar Categoría**.
- **Validación de reglas:**
  - Intenta crear una categoría con un plazo mayor a 180 días o menor a 1 día; el formulario o el backend lo rechazarán.
  - Intenta crear una categoría con un nombre ya existente; se mostrará un mensaje de error indicando la duplicidad.
- **Listar y Filtrar:** Observa las categorías en la tabla inferior y usa la casilla "Ver solo activas" para alternar la visualización.
- **Editar Categoría:** Haz clic en ✏️ **Editar**, modifica el plazo o descripción y haz clic en **Guardar Cambios**. También puedes reactivar una categoría inactiva.
- **Borrado Lógico:** Haz clic en 🗑️ **Desactivar**. La categoría pasará a estado inactiva (`activo = false`) sin eliminarse físicamente de la base de datos.