-- Migración 004: Crear tablas de préstamos y devoluciones
CREATE TABLE IF NOT EXISTS prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cedula_persona VARCHAR(20) NOT NULL,
    id_equipo INT NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_devolucion_esperada DATE NOT NULL,
    INDEX idx_prestamos_persona (cedula_persona),
    INDEX idx_prestamos_equipo (id_equipo),
    INDEX idx_prestamos_fecha_devolucion_esperada (fecha_devolucion_esperada),
    CONSTRAINT fk_prestamos_persona FOREIGN KEY (cedula_persona) REFERENCES personas (cedula) ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_prestamos_equipo FOREIGN KEY (id_equipo) REFERENCES equipos (id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS devoluciones (
    id_prestamo INT PRIMARY KEY,
    fecha_devolucion DATE NOT NULL,
    novedades VARCHAR(255) NULL,
    CONSTRAINT fk_devoluciones_prestamo FOREIGN KEY (id_prestamo) REFERENCES prestamos (id) ON UPDATE CASCADE ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
