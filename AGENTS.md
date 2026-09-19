# AGENTS.md

## Contexto

Sistema de Información para gestionar los préstamos de un laboratorio universitario.

## Stack

| Capa | Tecnología | Requisitos |
|---|---|---|
| Frontend | React + JavaScript | Limpio y minimalista. Su único fin es probar las funcionalidades del backend: sin sobreingeniería ni complejidad técnica. |
| Backend | Python + FastAPI, sobre `venv` | Arquitectura por capas estándar de FastAPI (ver más abajo). |
| Base de datos | MySQL en Docker | Servicio Docker consumido por el backend, con volumen para persistir datos entre ejecuciones. |
| Pruebas | pytest | Solo backend. Mocks para repositorios y dependencias no críticas. |

## Estructura del backend

Si el repositorio ya tiene una estructura, respétala. Si no, usa esta:

```
backend/
├── app/
│   ├── main.py
│   ├── core/          # configuración y conexión a BD
│   ├── models/        # modelos de datos (ORM)
│   ├── schemas/       # DTOs (Pydantic)
│   ├── repositories/  # acceso a datos, sin reglas de negocio
│   ├── services/      # reglas y validaciones de negocio
│   └── routers/       # endpoints, delgados: solo delegan en services
├── migrations/
└── tests/
```

## Documentos de referencia

Están en la raíz del repositorio. Consúltalos antes de planificar cualquier funcionalidad. Si lo solicitado contradice alguno, avisa al usuario antes de continuar.

| Documento | Contenido | Notas |
|---|---|---|
| `ADR.md` | Decisiones de arquitectura (formato ADR estándar). | Ignora el ADR #1 (modelo de IA a usar). |
| `ASSUMPTIONS.md` | Suposiciones, reglas de negocio y reglas de funcionamiento. | Solo se modifica cuando el usuario lo indique de forma explícita. |
| `MODELS.md` | Modelo de clases esperado: campos y su explicación. | Referencia para los modelos de datos. |

## Flujo de desarrollo por funcionalidad

El usuario define una funcionalidad o un conjunto de funcionalidades relacionadas: qué se pretende, reglas de negocio, contratos, requerimientos especiales y limitaciones. Con eso, sigue estos pasos en orden.

### Fase 1: Planificación (pasos 1 a 4)

1. **Alcance.** Define el alcance, las limitaciones y las reglas de validación. Todo lo que no esté especificado se pregunta al usuario; nunca se asume.
2. **Contratos.** La comunicación frontend ↔ backend es una API REST con JSON. Define los DTOs y endpoints (método, ruta, request, response y errores).
3. **Reglas de negocio.** Consolida en una lista las reglas y validaciones que se aplicarán.
4. **Plan de pruebas.** Define las pruebas unitarias con pytest para las validaciones de dominio de los services. Mockea los repositorios y demás dependencias no críticas.

> **Punto de control:** presenta al usuario el resultado de la Fase 1 y espera su confirmación antes de implementar.

### Fase 2: Implementación (pasos 5 y 6)

5. **Backend.** Implementa con código limpio y eficiente, en este orden:
   modelos de datos → migraciones → repositorios → services (reglas del paso 3) → pruebas unitarias (plan del paso 4) → endpoints (contrato del paso 2).
   Al terminar, deja los contratos expuestos en la API.
6. **Frontend.** Implementa las interfaces mínimas necesarias para probar los endpoints del paso 5, con React y JavaScript.

### Fase 3: Verificación (paso 7)

7. **Pruebas manuales.** El usuario prueba manualmente contra el frontend. Mantén `README.md` actualizado: cómo levantar el entorno (venv, Docker, backend, frontend), y las funcionalidades nuevas con sus endpoints y cómo probarlas.

## Reglas transversales

- No asumas reglas de negocio ni de validación: pregúntalas.
- No registres suposiciones en `ASSUMPTIONS.md` si el usuario no lo indica.
- Las reglas de negocio viven en los services; los routers no las contienen.
- Las validaciones de dominio siempre llevan pruebas unitarias.

## Checklist de entrega

- [ ] Alcance, contratos, reglas y plan de pruebas confirmados por el usuario
- [ ] Modelos y migraciones creados; la BD persiste entre lanzamientos
- [ ] Services con reglas de negocio y pruebas pytest pasando
- [ ] Endpoints según el contrato acordado
- [ ] Frontend mínimo que permite probar cada endpoint
- [ ] `README.md` actualizado