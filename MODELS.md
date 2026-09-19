# Modelos del sistema

Modelo de clases esperado para el Sistema de Información para préstamos del Laboratorio universitario. Convenciones:

- Nombres de tablas y campos en `snake_case`, sin tildes.
- `PK`: llave primaria. `FK`: llave foránea.
- Las referencias `SUP-XX` apuntan a `ASSUMPTIONS.md`.

## Relaciones

| Relación | Cardinalidad |
|---|---|
| Categoría → Equipo | 1 a N (un equipo pertenece a una sola categoría) |
| Persona → Préstamo | 1 a N |
| Equipo → Préstamo | 1 a N |
| Préstamo → Devolución | 1 a 1 |

---

## 1. Persona

Persona que solicita préstamos de equipos. Puede ser profesor o estudiante.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `cedula` | String | PK | Cédula de identificación de la persona. |
| `nombre_completo` | String(100) | NOT NULL | Nombre completo de la persona. |
| `correo` | String | NULL | Correo electrónico de la persona. Opcional. |
| `telefono` | String | NOT NULL | Teléfono celular de la persona. Obligatorio. |
| `tipo_persona` | Enum(`profesor`, `estudiante`) | Not Null | Tipo de persona. Solo admite estos dos valores. |
| `facultad` | String | Not null | Facultad a la que pertenece la persona, como texto libre (SUP-07). |

## 2. Categoría

Agrupa los equipos y define el plazo en que deben devolverse.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | int | PK | Identificador en la base de datos. |
| `nombre` | String | NOT NULL | Nombre de la categoría. |
| `descripcion` | String | NULL | Descripción de la categoría. Opcional. |
| `plazo_entrega` | int (días) | Not Null | Plazo de entrega en días, definido por el administrador (SUP-01, SUP-02). La fecha en que debe devolverse un equipo depende de la categoría a la que pertenece. |

## 3. Equipo

Equipo del laboratorio que puede prestarse.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | int | PK | Identificador en la base de datos. |
| `id_categoria` | int | NOT NULL, FK → `categoria.id` | Categoría del equipo. Un equipo pertenece a una sola categoría. |
| `nombre` | String | NOT NULL | Nombre del equipo. |
| `secuencial` | String | NOT NULL, UNIQUE | Secuencial interno del laboratorio para el equipo. |
| `descripcion` | String | NULL | Descripción del equipo. Opcional. |
| `mantenimiento` | bool | Not Null | Indica si el equipo está en mantenimiento (SUP-05). |
| `fecha_creacion` | date | NOT NULL | Fecha de creación del equipo en el sistema. |

## 4. Préstamo

Préstamo de un equipo a una persona.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | int | PK | Identificador en la base de datos. |
| `cedula_persona` | String | FK → `persona.cedula` | Cédula de la persona solicitante. |
| `id_equipo` | int | FK → `equipo.id` | Equipo prestado. |
| `fecha_prestamo` | date | Not Null | Fecha de inicio del préstamo. |
| `fecha_devolucion_esperada` | date | Not Null | Fecha en que debe devolverse el equipo, definida por el plazo de su categoría. Se conserva aunque el plazo de la categoría cambie después (SUP-03). |

## 5. Devolución

Registro de la devolución efectiva de un préstamo.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id_prestamo` | int | PK, FK → `prestamo.id` | Préstamo que se devuelve. Es a la vez PK y FK porque la relación es 1 a 1. |
| `fecha_devolucion` | date | Not Null | Fecha en que se efectuó la devolución. |
| `novedades` | String | Null | Novedades encontradas en el equipo al momento de la devolución. |