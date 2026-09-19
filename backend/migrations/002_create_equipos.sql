-- Migración 002: Crear tabla de equipos
CREATE TABLE IF NOT EXISTS equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    id_categoria INT NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    secuencial VARCHAR(50) NOT NULL UNIQUE,
    descripcion VARCHAR(255) NULL,
    mantenimiento BOOLEAN NOT NULL DEFAULT FALSE,
    fecha_creacion DATE NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_equipos_categoria (id_categoria),
    INDEX idx_equipos_secuencial (secuencial),
    INDEX idx_equipos_activo (activo),
    CONSTRAINT fk_equipos_categoria FOREIGN KEY (id_categoria) REFERENCES categorias (id) ON UPDATE CASCADE ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
