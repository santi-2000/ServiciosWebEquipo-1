# Servicios Web para login usando MSSQLServer como base de datos

Este repositorio contiene un ejercicio de conexión a una instancia de **SQL Server** que corre dentro de un contenedor Docker en **GitHub Codespaces** utilizando el paquete **pymssql** para Python.

## Prerequisitos

Antes de comenzar, asegúrate de tener:

- **GitHub Codespaces** habilitado.
- **Docker** ejecutándose en tu Codespace.
- **Python 3** instalado.
- **pymssql** instalado en tu entorno Python.

### Iniciar la instancia de SQL Server en Docker

Para iniciar una instancia de **SQL Server** en un contenedor Docker, ejecuta el siguiente comando en la terminal de tu **GitHub Codespace**:

```sh
docker run -e 'ACCEPT_EULA=Y' -e 'SA_PASSWORD=YourPassword123!' \
   -p 1433:1433 --name sqlserver -d mcr.microsoft.com/mssql/server:2022-latest
```

### Instalar sqlcmd
```sh
sudo apt update
sudo apt install mssql-tools unixodbc-dev
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc
```

### Usar sqlcmd para conectarse desde la terminal
```sh
sqlcmd -S localhost -U sa -P YourPassword123! -i ./init_db.sql
```

### Crear tabla de usuarios
```sh
CREATE TABLE usuarios (
   username VARCHAR(50) PRIMARY KEY,
   nombre_completo VARCHAR(255) NOT NULL,
   contrasena CHAR(40) NOT NULL
);
GO
```

### Agregar un usuario ejemplo (la contraseña es 'luke')
```sh
INSERT INTO usuarios VALUES ('dvader', 'Darth Vader', '6b3799be4300e44489a08090123f3842e6419da5');
GO
```

# Probar servicios web

## Prerequisitos

- Se ejecutaron los comandos SQL previos


### Ejecución de servidor de servicios web

Ejecuta el siguiente comando en la terminal de tu **GitHub Codespace**:

```sh
cd web\ services/
python ws.py

```
### Ejemplos para consumir servicios web desde la terminal

Abra **otra terminal**  (no cierre la terminal que está ejecutando el servidor), y ejecute el siguiente comando para probar el servicio web:

```sh
curl -X POST http://127.0.0.1:5000/login -H "Content-Type: application/json" -d '{"username": "dvader", "password": "luke"}'
```
