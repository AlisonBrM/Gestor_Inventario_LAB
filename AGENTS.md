
## Contexto

Estás desarrollando un Sistema de Información para préstamos en un Laboratorio en una Universidad

## Stack Tecnológico

### Frontend 
React sobre Javascript
Es importante que se entregue un frontend limpio y minimalista, sin profundidad de desarrollo ni sobre complejidad técnica, utilizado especialmente para probar las funcionalidades realizadas

### Backend
Python (FastAPI)
Se utilizará Python como lenguaje para el backend, sobre un venv, así como la arquitectura estándar de backend para proyectos FastAPI:


### Base de Datos
MySQL (Docker)
Se expondrá un servicio docker de MySQL para que sea consumido por el backend, este debe tener un volumen y persistir entre lanzamientos

## Documentos Importantes

Los siguientes documentos se encuentran en la carpeta raíz del repositorio, y los utilizarás como guía para el proceso de desarrollo de funcionalidades

- ADR.md: Registro de las decisiones de arquitectura realizadas con el formato estándar de las ADR, el ADR #1 por instrucción será el modelo de IA a usar, no tener en cuenta.
- ASSUMPTIONS.md: Registro de las suposiciones realizadas para el desarrollo del sistema, como reglas de negocio o reglas de funcionamiento.
- MODELS.md: Registro del modelo de clases esperado para el sistema, cada uno con la definición de los campos que tiene, y su explicación.

## Proceso de Desarrollo de funcionalidades

1. Definición de la funcionalidad a realizar: Se te definirá una funcionalidad, o en su defecto, un conjunto de funcionalidades relacionadas. Se te describirá qué se pretende hacer, qué reglas o validaciones de negocio posee, y demás información que pueda ser importante (contratos, requerimientos especiales, limitaciones, etc). Con este conjunto de funcionalidades crearás el plan de implementación
2. Definición del alcance de la funcionalidad: Primeramente, debes definir cuál será el alcance de la funcionalidad: sus limitaciones, sus reglas de validación, y será el espacio para resolver dudas: no puedes asumir reglas de validación, debes de preguntarlas al usuario, con incluso el caso de que se deban definir en ASSUMPTIONS.md (no debes registrar suposiciones si no se te indica)
3. Definición de los contratos: La comunicación frontend <-> backend debe hacerse mediante una API REST con JSON, por lo que debes definir el contrato de el/los DTO(s) y endpoint(s) para la(s) funcionalidad(es) requeridas.
4. Definición de las reglas de negocio: Debes consolidar las reglas y validaciones de negocio que aplicarás en esta(s) funcionalidad(es)
5. Definición de las pruebas unitarias: Las validaciones de dominio deben llevar pruebas unitarias correctamente utilizadas con pytest y mocks adecuados de las dependencias no críticas para la validación de un service (repositorios de acceso a datos). Este será el conjunto de pruebas que deberás implementar en backend
6. Implementación backend: Procederás a implementar el código backend, siguiendo principios de código limpio y eficiente, se espera la implementación de los modelos de datos relacionados, las migraciones a base de datos, repositorios, servicios con reglas de negocio según el paso 4 y pruebas unitarias según el plan definido en el paso 5, y endpoints según el contrato definido en el paso 3. Terminarás exponiendo los contratos de la API.
7. Implementación frontend: Procederás a implementar las interfaces necesarias para probar los endpoints desarrollados en el paso 6, utilizando React con JavaScript
8. Pruebas: las pruebas se realizarán manualmente contra frontend, por lo que deberás mantener actualizada la documentación del README.md