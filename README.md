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

### Instalar sqlcmd y otras librerias
```sh
sudo apt update
sudo apt install mssql-tools unixodbc-dev
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc

pip install pandas openpyxl
pip install unidecode
```

### Usar sqlcmd para conectarse desde la terminal
```sh
sqlcmd -S localhost -U sa -P YourPassword123! -i ./init_db.sql
```

# Probar servicios web

## Prerequisitos

- Se ejecutaron los comandos SQL previos


### Ejecución de servidor de servicios web

Ejecuta el siguiente comando en la terminal de tu **GitHub Codespace** para iniciar la base de datos, con esto ya deberian estar funcionando los endpionts:

```sh
cd web\ services/
python ws.py

```

