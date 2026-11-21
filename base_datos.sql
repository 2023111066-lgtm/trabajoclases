CREATE TABLE IF NOT EXISTS paciente (
    id_paciente INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT NOT NULL UNIQUE,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    fecha_nacimiento TEXT NOT NULL,
    sexo TEXT NOT NULL,
    telefono TEXT
);

CREATE TABLE IF NOT EXISTS cita (
    id_cita INTEGER PRIMARY KEY AUTOINCREMENT,
    dni TEXT NOT NULL,
    fecha TEXT NOT NULL,
    hora TEXT NOT NULL,
    motivo TEXT NOT NULL,
    estado TEXT NOT NULL DEFAULT 'Programada',
    FOREIGN KEY (dni) REFERENCES paciente (dni)
);

INSERT OR IGNORE INTO paciente (dni, nombres, apellidos, fecha_nacimiento, sexo, telefono) VALUES
('12345678', 'Ana', 'Torres Ramos', '1995-03-14', 'F', '987654321'),
('87654321', 'Luis', 'Mendoza Quispe', '2000-05-10', 'M', '912345678'),
('70000003', 'María Elena', 'Rojas Vega', '1988-11-02', 'F', '934567890'),
('70000004', 'Carlos', 'Huamán Flores', '1979-07-25', 'M', '945678901'),
('70001125', 'Lucía', 'Paredes Cruz', '2003-01-19', 'F', '956789012'),
('70044446', 'Jorge', 'Salazar Díaz', '1992-09-08', 'M', '967890123');

INSERT INTO cita (dni, fecha, hora, motivo, estado) VALUES
('12345678', '2026-12-12', '12:12', 'revision', 'Programada'),
('87654321', '2026-12-15', '09:30', 'control', 'Programada');