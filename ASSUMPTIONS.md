# Suposiciones del sistema

Este documento registra las suposiciones, reglas de negocio y límites de alcance del Sistema de Información para préstamos del Laboratorio universitario. Cada suposición tiene un identificador para poder referenciarla.

## Alcance y usuarios

- **SUP-01.** El sistema es utilizado únicamente por el administrador. Por lo tanto, no incluye módulos de autenticación ni de autorización.
- **SUP-02.** El sistema de multas y penalizaciones por demoras o daños está fuera del alcance del sistema.
- **SUP-03.** Los módulos de pasarela de pagos están fuera del alcance del sistema.

## Categorías y tiempos de entrega

- **SUP-04.** El administrador define el tiempo de entrega de cada categoría, el tiempo de entrega no puede ser superior a 6 meses.
- **SUP-05.** El tiempo de entrega de cada categoría se expresa en días calendario.
- **SUP-06.** Si el administrador modifica el tiempo de entrega de una categoría, los préstamos vigentes conservan su fecha de vencimiento. El nuevo tiempo aplica solo a los préstamos que se creen después del cambio.

## Préstamos

- **SUP-07.** Un préstamo puede prorrogarse hasta un máximo de 6 meses, contados a partir de la fecha de entrega del equipo. Es decir, la duración total del préstamo, incluidas las prórrogas, no puede superar los 6 meses.

## Devoluciones y mantenimiento

- **SUP-08.** Cuando un equipo se devuelve con novedad, el administrador decide si debe enviarse a mantenimiento.

## Personas

- **SUP-09.** La facultad a la que pertenece una persona se almacena como un campo de texto.