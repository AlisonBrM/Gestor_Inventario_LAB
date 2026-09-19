-- Migración 003: Crear tabla de personas
CREATE TABLE IF NOT EXISTS personas (
    cedula VARCHAR(20) PRIMARY KEY,
    nombre_completo VARCHAR(100) NOT NULL,
    correo VARCHAR(150) NULL,
    telefono VARCHAR(20) NOT NULL,
    tipo_persona ENUM('profesor', 'estudiante') NOT NULL,
    facultad VARCHAR(150) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_personas_activo (activo),
    INDEX idx_personas_tipo (tipo_persona)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
