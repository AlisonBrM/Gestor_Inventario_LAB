# Registro de Decisiones de Arquitectura (ADR)

Este documento registra las decisiones de arquitectura del Sistema de Información para préstamos del Laboratorio universitario, siguiendo el formato estándar de ADR (título, estado, contexto, decisión y consecuencias).

| # | Título | Estado | Fecha |
|---|---|---|---|
| 1 | Uso de Antigravity CLI como herramienta de desarrollo asistido por IA | Aceptada | 2026-09-18 |
| 2 | Stack tecnológico: React, Python con FastAPI y MySQL | Aceptada | 2026-09-18 |
| 3 | Arquitectura por capas en el backend | Aceptada | 2026-09-18 |

---

## ADR-001: Uso de Antigravity CLI como herramienta de desarrollo asistido por IA

- **Estado:** Aceptada
- **Fecha:** 2026-09-18

### Contexto

El desarrollo del sistema se apoya en una herramienta de IA que asiste en la implementación del código. Se cuenta con una licencia de pago de Antigravity CLI, por lo que su uso no implica un costo adicional para el proyecto.

### Decisión

Se utilizará **Antigravity CLI** como herramienta de desarrollo asistido por IA, aprovechando la licencia de pago disponible.

### Alternativas descartadas

| Alternativa | Motivo del descarte |
|---|---|
| Otras herramientas de IA de pago (por ejemplo, Claude Code o Cursor) | Implicarían adquirir una licencia adicional, cuando ya se cuenta con la de Antigravity CLI. |
| Versiones gratuitas de asistentes de IA | Sus límites de uso y capacidades son menores que los de la licencia de pago disponible. |


### Consecuencias

**Positivas**
- Se aprovecha una licencia ya adquirida, sin costos adicionales.
- Se cuenta con las capacidades del plan de pago (límites de uso ampliados).

**Negativas / Riesgos**
- El desarrollo del proyecto depende de que la licencia se mantenga vigente.
- La licencia de AntiGravity expone un diversidad limitada de modelos.

---

## ADR-002: Stack tecnológico: React, Python con FastAPI y MySQL

- **Estado:** Aceptada
- **Fecha:** 2026-09-18

### Contexto

El sistema requiere una interfaz para probar las funcionalidades, una API que exponga la lógica de negocio de los préstamos y una base de datos relacional que persista la información. El frontend es intencionalmente mínimo, pues su propósito es validar las funcionalidades del backend.

### Decisión

Se adopta el siguiente stack:

- **Frontend:** React con JavaScript.
- **Backend:** Python con FastAPI, sobre un entorno virtual (`venv`).
- **Base de datos:** MySQL, ejecutada como servicio en Docker con un volumen para persistir los datos entre lanzamientos.

La comunicación entre frontend y backend se realiza mediante una API REST con JSON.

### Alternativas descartadas

| Capa | Alternativa | Motivo del descarte |
|---|---|---|
| Frontend | Vue o Angular | React basta para un frontend mínimo de pruebas; Angular o Vue añade más estructura y complejidad de la necesaria. |
| Frontend | React con TypeScript | El frontend solo sirve para probar funcionalidades; se prioriza mantenerlo simple, sin sobrecomplejidad técnica. |
| Backend | Django (con Django REST Framework) | Framework más pesado y con más convenciones de las necesarias; FastAPI ofrece validación y documentación OpenAPI integradas con menos código. |
| Backend | Flask | No incluye validación de datos ni documentación de contratos de serie; habría que añadirlas con librerías externas. |
| Backend | Node.js (Express) | Unificaría el lenguaje con el frontend, pero se tiene experiencia desarrollando con python en FastAPI |
| Base de datos | PostgreSQL | Alternativa relacional válida, pero no aporta ventajas para el alcance del proyecto frente a MySQL. |
| Base de datos | SQLite | No representa un entorno de servicio real y tiene limitaciones de concurrencia. |
| Base de datos | MongoDB | Los datos de préstamos (usuarios, equipos, préstamos) son naturalmente relacionales. |

### Consecuencias

**Positivas**
- FastAPI genera documentación OpenAPI automáticamente, lo que facilita exponer y probar los contratos de la API.
- React permite construir rápidamente interfaces simples para probar los endpoints.
- MySQL en Docker hace el entorno reproducible y los datos persisten gracias al volumen.
- Pydantic (incluido en FastAPI) da validación de DTOs desde el contrato.

**Negativas / Riesgos**
- El proyecto usa dos lenguajes (Python y JavaScript), lo que exige manejar dos ecosistemas de dependencias.
- El desarrollo local requiere Docker instalado para la base de datos.

---

## ADR-003: Arquitectura por capas en el backend

- **Estado:** Aceptada
- **Fecha:** 2026-09-18

### Contexto

El backend concentrará reglas y validaciones de negocio propias de los préstamos del laboratorio, que deben poder probarse de forma aislada. Se necesita una organización del código que separe responsabilidades, facilite las pruebas unitarias con mocks y mantenga el código limpio a medida que crezca el sistema.

### Decisión

El backend se organiza en una **arquitectura por capas**, con las siguientes responsabilidades:

| Capa | Responsabilidad |
|---|---|
| **Routers** (presentación) | Exponen los endpoints REST, reciben y devuelven DTOs. No contienen reglas de negocio; delegan en los services. |
| **Schemas** (DTOs) | Definen los contratos de entrada y salida de la API (Pydantic). |
| **Services** (negocio) | Contienen las reglas y validaciones de negocio. Dependen de los repositorios, no de la base de datos directamente. |
| **Repositories** (acceso a datos) | Encapsulan el acceso a la base de datos. No contienen reglas de negocio. |
| **Models** (dominio/persistencia) | Definen las entidades de datos y su mapeo a la base de datos. |

Las dependencias fluyen en un solo sentido: `Routers → Services → Repositories → Models`.

### Alternativas descartadas

| Alternativa | Motivo del descarte |
|---|---|
| Sin capas (lógica de negocio directamente en los endpoints) | Mezcla responsabilidades, dificulta las pruebas unitarias y vuelve el código difícil de mantener al crecer. |
| Arquitectura hexagonal o Clean Architecture | Su nivel de abstracción y número de interfaces excede la complejidad del sistema. |
| Microservicios | Sobredimensionada para el alcance del proyecto; añade complejidad de despliegue y comunicación sin beneficio. |

### Consecuencias

**Positivas**
- Separación clara de responsabilidades, con código más legible y mantenible.
- Los services pueden probarse con pytest mockeando los repositorios, sin necesidad de base de datos.
- Cambiar la forma de acceso a datos afecta solo a los repositorios.

**Negativas / Riesgos**
- Mayor cantidad de archivos y de código de transición entre capas (por ejemplo, conversión entre DTOs y modelos) incluso en funcionalidades simples.
- Requiere disciplina para no colocar reglas de negocio en routers o repositorios.