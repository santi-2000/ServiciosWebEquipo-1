IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'Data')
BEGIN
    CREATE DATABASE Data;
END;
GO

USE Data;
GO

-- Eliminar tablas en orden de dependencias
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

-- Crear las tablas

CREATE TABLE Departamento (
  idDepartamento INT NOT NULL IDENTITY(1,1),
  nombreDepartamento VARCHAR(50) NOT NULL,
  PRIMARY KEY (idDepartamento)
);

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
  matricula VARCHAR(10) NOT NULL,  
  nombre VARCHAR(20) NOT NULL,
  apellidoPaterno VARCHAR(30) NOT NULL,
  apellidoMaterno VARCHAR(30) NOT NULL,
  rol VARCHAR(20) NOT NULL,
  idDepartamento INT NOT NULL,
  PRIMARY KEY (matricula),
  FOREIGN KEY (idDepartamento) REFERENCES Departamento(idDepartamento)
);

CREATE TABLE Usuario (
  matricula VARCHAR(10) NOT NULL PRIMARY KEY, 
  passwordHash VARBINARY(64) NOT NULL,
  FOREIGN KEY (matricula) REFERENCES Profesor(matricula)
);

CREATE TABLE Alumno (
  matricula VARCHAR(7) NOT NULL,
  nombre VARCHAR(30) NOT NULL,
  apellidoPaterno VARCHAR(30) NOT NULL,
  apellidoMaterno VARCHAR(30) NOT NULL,
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
  matricula VARCHAR(10) NOT NULL,
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

-- Datos de prueba

INSERT INTO Departamento (nombreDepartamento) VALUES
('Ciencias Comp.'),
('Matemáticas'),
('Física');

INSERT INTO Materia (clave, nombre, idDepartamento) VALUES
(101, 'Álgebra', 2),
(202, 'Estructuras de Datos', 1),
(303, 'Mecánica', 3);

INSERT INTO Profesor (matricula, nombre, apellidoPaterno, apellidoMaterno, rol, idDepartamento) VALUES
('A001', 'Carlos', 'López', 'Martínez', 'Administrador', 1),
('A002', 'Ana', 'González', 'Ruiz', 'Coordinador', 2),
('A003', 'Luis', 'Fernández', 'Soto', 'Director', 3);

INSERT INTO PeriodoEscolar (fecha) VALUES
('2024-01-01'),
('2024-08-01');

INSERT INTO Grupo (CRN, idPeriodo, clave) VALUES
(1001,  1, 101),
(1002,  1, 202),
(1003,  2, 303);

INSERT INTO Alumno (matricula, nombre, apellidoPaterno, apellidoMaterno) VALUES
('A001', 'Juan', 'Pérez', 'Sánchez'),
('A002', 'María', 'Ramírez', 'López'),
('A003', 'Pedro', 'Díaz', 'Torres');

INSERT INTO Pregunta (pregunta) VALUES
('¿Te gusta la materia?'),
('¿Cómo calificarías al profesor?');

INSERT INTO ProfesorGrupo (CRN, matricula) VALUES
(1001, 'A001'),
(1002, 'A002'),
(1003, 'A003');

INSERT INTO Responde (matricula, idPregunta, CRN, respuesta) VALUES
('A001', 1, 1001, 'Sí'),
('A002', 2, 1002, 'Regular');

INSERT INTO Comenta (idPregunta, matricula, CRN, comentario) VALUES
(1, 'A001', 1001, 'Me gusta la materia'),
(2, 'A002', 1002, 'El profesor explica bien');

INSERT INTO Permisos (rol) VALUES
('Administrador'),
('Director'),
('Coordinador'),
('Profesor');

INSERT INTO GrupoClasifClase (CRN, clasifClase) VALUES
(1001, 'Teoría'),
(1002, 'Laboratorio'),
(1003, 'Teoría');

INSERT INTO Usuario (matricula, passwordHash) VALUES
('A001', HASHBYTES('SHA2_256', CONVERT(VARCHAR, 'Renata'))),
('A002', HASHBYTES('SHA2_256', CONVERT(VARCHAR, 'Renlo'))),
('A003', HASHBYTES('SHA2_256', CONVERT(VARCHAR, 'Dania')));