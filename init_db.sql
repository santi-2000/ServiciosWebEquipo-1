IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'Data')
BEGIN
    CREATE DATABASE Data;
END;
GO

-- Cambiar al contexto de la base de datos 'Data'
USE Data;
GO

-- Eliminar las tablas dependientes primero
DROP TABLE IF EXISTS Responde;
DROP TABLE IF EXISTS Comenta;
DROP TABLE IF EXISTS ProfesorGrupo;
DROP TABLE IF EXISTS GrupoMateria;
DROP TABLE IF EXISTS GrupoClasifClase;
DROP TABLE IF EXISTS Usuario;            
DROP TABLE IF EXISTS Grupo;
DROP TABLE IF EXISTS Permisos;
DROP TABLE IF EXISTS Materia;
DROP TABLE IF EXISTS Profesor;         
DROP TABLE IF EXISTS Departamento;
DROP TABLE IF EXISTS PeriodoEscolar;
DROP TABLE IF EXISTS Pregunta;
DROP TABLE IF EXISTS Alumno;
GO


-- Crear las tablas en el orden adecuado

CREATE TABLE Departamento (
  idDepartamento INT NOT NULL IDENTITY(1,1),
  nombreDepartamento VARCHAR(20) NOT NULL,
  PRIMARY KEY (idDepartamento)
);

ALTER TABLE Departamento ALTER COLUMN nombreDepartamento VARCHAR(50);

CREATE TABLE PeriodoEscolar (
  idPeriodo INT NOT NULL IDENTITY(1,1),
  fecha DATE NOT NULL,
  PRIMARY KEY (idPeriodo)
);

CREATE TABLE Materia (
  clave INT NOT NULL,
  nombre VARCHAR(50) NOT NULL,
  idDepartamento INT NOT NULL,
  PRIMARY KEY (clave),
  FOREIGN KEY (idDepartamento) REFERENCES Departamento(idDepartamento)
);

CREATE TABLE Profesor (
  matricula INT NOT NULL,  
  nombre VARCHAR(20) NOT NULL,
  apellidoPaterno VARCHAR(30) NOT NULL,
  apellidoMaterno VARCHAR(30) NOT NULL,
  rol VARCHAR(20) NOT NULL,
  idDepartamento INT NOT NULL,
  PRIMARY KEY (matricula),
  FOREIGN KEY (idDepartamento) REFERENCES Departamento(idDepartamento)
);

CREATE TABLE Alumno (
  matricula VARCHAR(7) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  apellidoPaterno VARCHAR(30) NOT NULL,
  apellidoMaterno VARCHAR(30) NOT NULL,
  matricula_Responde INT NULL,
  PRIMARY KEY (matricula)
);

CREATE TABLE Pregunta (
  idPregunta INT NOT NULL IDENTITY(1,1),
  pregunta VARCHAR(60) NOT NULL,
  PRIMARY KEY (idPregunta)
);

CREATE TABLE Grupo (
  CRN INT NOT NULL,
  idPeriodo INT NOT NULL,
  clave INT NOT NULL,
  PRIMARY KEY (CRN),
  FOREIGN KEY (idPeriodo) REFERENCES PeriodoEscolar(idPeriodo),
  FOREIGN KEY (clave) REFERENCES Materia(clave)
);

CREATE TABLE Responde (
  matricula VARCHAR(7) NOT NULL,
  idPregunta INT NOT NULL,
  CRN INT NOT NULL,
  respuesta VARCHAR(MAX) NULL,
  PRIMARY KEY (matricula, idPregunta, CRN),
  FOREIGN KEY (matricula) REFERENCES Alumno(matricula),
  FOREIGN KEY (idPregunta) REFERENCES Pregunta(idPregunta),
  FOREIGN KEY (CRN) REFERENCES Grupo(CRN)
);

CREATE TABLE Comenta (
  idPregunta INT NOT NULL,
  matricula VARCHAR(7) NOT NULL,
  CRN INT NOT NULL,
  comentario VARCHAR(MAX) NULL,
  PRIMARY KEY (idPregunta, matricula, CRN),
  FOREIGN KEY (idPregunta) REFERENCES Pregunta(idPregunta),
  FOREIGN KEY (matricula) REFERENCES Alumno(matricula),
  FOREIGN KEY (CRN) REFERENCES Grupo(CRN)
);

CREATE TABLE ProfesorGrupo (
  CRN INT NOT NULL,
  matricula INT NOT NULL,
  PRIMARY KEY (CRN, matricula),
  FOREIGN KEY (CRN) REFERENCES Grupo(CRN),
  FOREIGN KEY (matricula) REFERENCES Profesor(matricula)
);

CREATE TABLE Permisos (
  idPermisos INT NOT NULL IDENTITY(1,1),
  rol VARCHAR(20) NOT NULL,
  PRIMARY KEY (idPermisos)
);

CREATE TABLE GrupoClasifClase (
  CRN INT NOT NULL,
  clasifClase VARCHAR(30) NOT NULL,
  PRIMARY KEY (CRN, clasifClase),
  FOREIGN KEY (CRN) REFERENCES Grupo(CRN)
);

CREATE TABLE Usuario (
  matricula INT NOT NULL PRIMARY KEY, 
  passwordHash VARBINARY(64) NOT NULL,
  FOREIGN KEY (matricula) REFERENCES Profesor(matricula)
);

--
-- ---
-- --- Test Data ---

-- Insertar Departamentos
INSERT INTO Departamento (nombreDepartamento) VALUES
('Ciencias Comp.'),
('Matemáticas'),
('Física');

-- Insertar Materias
INSERT INTO Materia (clave, nombre, idDepartamento) VALUES
(101, 'Álgebra', 2),
(202, 'Estructuras de Datos', 1),
(303, 'Mecánica', 3);

-- Insertar Profesores (asegurando que los departamentos existen)
INSERT INTO Profesor (matricula, nombre, apellidoPaterno, apellidoMaterno, rol, idDepartamento) VALUES
(1111, 'Carlos', 'López', 'Martínez', 'Administrador', 1),
(2222, 'Ana', 'González', 'Ruiz', 'Coordinador', 2),
(3333, 'Luis', 'Fernández', 'Soto', 'Director', 3);

-- Insertar Periodos Escolares
INSERT INTO PeriodoEscolar (fecha) VALUES
('2024-01-01'),
('2024-08-01');

-- Insertar Grupos (asegurando que los CRN y claves existen)
INSERT INTO Grupo (CRN, idPeriodo, clave) VALUES
(1001,  1, 101),
(1002,  1, 202),
(1003,  2, 303);

-- Insertar Alumnos
INSERT INTO Alumno (matricula, nombre, apellidoPaterno, apellidoMaterno, matricula_Responde) VALUES
('A001', 'Juan', 'Pérez', 'Sánchez', NULL),
('A002', 'María', 'Ramírez', 'López', NULL),
('A003', 'Pedro', 'Díaz', 'Torres', NULL);

-- Insertar Preguntas
INSERT INTO Pregunta (pregunta) VALUES
('¿Te gusta la materia?'),
('¿Cómo calificarías al profesor?');

-- Insertar ProfesorGrupo
INSERT INTO ProfesorGrupo (CRN, matricula) VALUES
(1001, 1),
(1002, 2),
(1003, 3);

-- Insertar Respuestas
INSERT INTO Responde (matricula, idPregunta, CRN, respuesta) VALUES
('A001', 1, 1001, 'Sí'),
('A002', 2, 1002, 'Regular');

-- Insertar Comentarios
INSERT INTO Comenta (idPregunta, matricula, CRN, comentario) VALUES
(1, 'A001', 1001, 'Me gusta la materia'),
(2, 'A002', 1002, 'El profesor explica bien');

-- Insertar Permisos
INSERT INTO Permisos (rol) VALUES
('Administrador'),
('Director'),
('Coordinador'),
('Profesor');

-- Insertar GrupoClasifClase
INSERT INTO GrupoClasifClase (CRN, clasifClase) VALUES
(1001, 'Teoría'),
(1002, 'Laboratorio'),
(1003, 'Teoría');

INSERT INTO Usuario (matricula, passwordHash) VALUES
(1, HASHBYTES('SHA2_256', CONVERT(VARCHAR, 'Renata'))),
(2, HASHBYTES('SHA2_256', CONVERT(VARCHAR, 'Renlo'))),
(3, HASHBYTES('SHA2_256', CONVERT(VARCHAR, 'Dania')));