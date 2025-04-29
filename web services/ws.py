from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pymssql
import hashlib
import pandas as pd

app = Flask(__name__)
CORS(app)

app.secret_key = 'Equipo1'

SERVER = 'localhost'
DATABASE = 'Data'
USERNAME = 'sa'
PASSWORD = 'YourPassword123!'

def get_db_connection():
    try:
        conn = pymssql.connect(
            server=SERVER, port=1433, database=DATABASE, user=USERNAME, password=PASSWORD)
        return conn
    except Exception as e:
        print(f"Error conectando a BD: {e}")
        return None

def verify_password(stored_password_hash, provided_password):
    hashed_provided_password = hashlib.sha256(provided_password.encode()).digest()
    return stored_password_hash == hashed_provided_password

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Se requiere usuario y contraseña'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("""
                SELECT u.matricula, u.passwordHash, p.rol
                FROM Usuario u
                JOIN Profesor p ON u.matricula = p.matricula
                WHERE u.matricula = %s
            """, (username,))

            user = cursor.fetchone()

            if user:
                hashed_provided_password = hashlib.sha256(password.encode()).digest()

                if user['passwordHash'] == hashed_provided_password:
                    session['username'] = username
                    session['rol'] = user['rol']
                    if user['rol'] == 'Administrador':
                        return jsonify({'redirect': '/admin'})
                    elif user['rol'] == 'Director':
                        return jsonify({'redirect': '/director'})
                    elif user['rol'] == 'Coordinador':
                        return jsonify({'redirect': '/coordinador'})
                    else:
                        return jsonify({'redirect': '/profesor'})
                else:
                    return jsonify({'error': 'Usuario o contraseña incorrectos'}), 401
            else:
                return jsonify({'error': 'Usuario no encontrado'}), 404

        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    

@app.route('/usuario', methods=['GET'])
def obtener_usuario():
    if 'username' not in session:
        return jsonify({'error': 'No has iniciado sesión'}), 401

    username = session['username']

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("""
                SELECT nombre, apellidoPaterno, apellidoMaterno, rol
                FROM Profesor
                WHERE matricula = %s
            """, (username,))
            profesor = cursor.fetchone()

            if profesor:
                nombre_completo = f"{profesor['nombre']} {profesor['apellidoPaterno']} {profesor['apellidoMaterno']}"
                return nombre_completo
            else:
                return jsonify({'error': 'Profesor no encontrado'}), 404

        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/profesores/nombres', methods=['GET'])
def get_nombres_profesores():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("""
                SELECT nombre, apellidoPaterno, apellidoMaterno
                FROM Profesor
            """)
            profesores = cursor.fetchall()

            # Construir lista de nombres completos
            nombres = [f"{p['nombre']} {p['apellidoPaterno']} {p['apellidoMaterno']}" for p in profesores]

            return jsonify(nombres), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener profesores: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


@app.route('/profesor/<int:profesor_id>', methods=['GET'])
def get_profesor_by_id(profesor_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

    try:
        cursor = conn.cursor(as_dict=True)
        cursor.execute("""
            SELECT p.matricula, p.nombre, p.apellidoPaterno, p.apellidoMaterno, p.rol,
                   d.nombreDepartamento
            FROM Profesor p
            JOIN Departamento d ON p.idDepartamento = d.idDepartamento
            WHERE p.matricula = %s
        """, (profesor_id,))
        profesor = cursor.fetchone()

        if profesor:
            return jsonify(profesor)
        else:
            return jsonify({'error': 'Profesor no encontrado'}), 404

    except Exception as e:
        return jsonify({'error': f'Error en la consulta: {e}'}), 500
    finally:
        conn.close()

@app.route('/profesores', methods=['POST'])
def create_profesor():
    data = request.get_json()
    matricula = data.get('matricula')
    nombre = data.get('nombre')
    apellidoPaterno = data.get('apellidoPaterno')
    apellidoMaterno = data.get('apellidoMaterno')
    rol = data.get('rol')
    nombreDepartamento = data.get('departamento')  

    if not matricula or not nombre or not apellidoPaterno or not apellidoMaterno or not rol or not nombreDepartamento:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Buscar idDepartamento basado en el nombre
            cursor.execute("""
                SELECT idDepartamento FROM Departamento WHERE nombreDepartamento = %s
            """, (nombreDepartamento,))
            result = cursor.fetchone()

            if not result:
                return jsonify({'error': f'El departamento "{nombreDepartamento}" no existe'}), 400

            idDepartamento = result[0]

            # Insertar el profesor
            cursor.execute("""
                INSERT INTO Profesor (matricula, nombre, apellidoPaterno, apellidoMaterno, rol, idDepartamento)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (matricula, nombre, apellidoPaterno, apellidoMaterno, rol, idDepartamento))

            conn.commit()
            return jsonify({'mensaje': 'Profesor creado exitosamente'}), 201
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'Error al crear profesor: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


@app.route('/departamentos', methods=['GET'])
def get_departamentos():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT * FROM Departamento")
            departamentos = cursor.fetchall()
            return jsonify(departamentos), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener departamentos: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/Departamento/nombres', methods=['GET'])
def get_nombres_grupos():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT nombreDepartamento FROM Departamento")
            Departamento = cursor.fetchall()
            delete = [g['nombreDepartamento'] for g in Departamento]
            return jsonify(delete)
        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/Departamento/nombres', methods=['GET'])
def get_nombres_departamentos():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT nombreDepartamento FROM Departamento")
            Departamento = cursor.fetchall()
            delete = [g['nombreDepartamento'] for g in Departamento]
            return jsonify(delete)
        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

@app.route('/Permisos', methods=['GET'])
def get_nombres_permisos():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT * FROM Permisos")
            Permisos = cursor.fetchall()
            crnn = [g['rol'] for g in Permisos]
            return jsonify(crnn)
        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

@app.route('/alumnos', methods=['GET'])
def get_alumnos():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT * FROM Alumno")
            alumnos = cursor.fetchall()
            return jsonify(alumnos), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener alumnos: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


@app.route('/comentarios', methods=['GET'])
def get_comentarios():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT * FROM Comenta")
            comentarios = cursor.fetchall()
            return jsonify(comentarios), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener comentarios: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/comentarios/<int:idPregunta>/<string:matricula>/<int:CRN>', methods=['PUT'])
def update_comentario(idPregunta, matricula, CRN):
    data = request.get_json()
    nuevo_comentario = data.get('comentario')
    nueva_fecha = data.get('fecha') 

    if not nuevo_comentario:
        return jsonify({'error': 'El campo comentario es obligatorio'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Comenta
                SET comentario = %s
                WHERE idPregunta = %s AND matricula = %s AND CRN = %s
            """, (nuevo_comentario, idPregunta, matricula, CRN))

            if cursor.rowcount == 0:
                return jsonify({'error': 'Comentario no encontrado'}), 404

            conn.commit()
            return jsonify({'mensaje': 'Comentario actualizado exitosamente'}), 200
        except Exception as e:
            conn.rollback()
            return jsonify({'error': f'Error al actualizar comentario: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500



@app.route('/materias', methods=['GET'])
def get_materias():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT * FROM Grupo")
            materias = cursor.fetchall()
            return jsonify(materias), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener materias: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    

@app.route('/usuarios', methods=['GET'])
def get_usuarios():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT matricula FROM Usuario")
            usuarios = cursor.fetchall()
            return jsonify(usuarios), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener usuarios: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
  
@app.route('/materias/nombres', methods=['GET'])
def get_nombres_materias():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT nombre FROM Materia")
            materias = cursor.fetchall()
            crns = [g['nombre'] for g in materias]
            return jsonify(crns), 200
        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

@app.route('/periodos', methods=['GET'])
def get_periodos():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT * FROM PeriodoEscolar")
            periodos = cursor.fetchall()
            return jsonify(periodos), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener periodos: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/grupos', methods=['GET'])
def get_grupo():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT CRN FROM Grupo")  # <-- Tabla correcta: Grupo
            grupos = cursor.fetchall()
            
            # Sacar solo los CRN en lista
            crns = [g['CRN'] for g in grupos]

            return jsonify(crns), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener grupos: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/subir_encuesta', methods=['POST'])
def subir_encuesta():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No se seleccionó un archivo'}), 400

    if file and file.filename.endswith('.xlsx'):
        # Leer el archivo Excel
        df = pd.read_excel(file, engine='openpyxl')
        expected_columns = ['Matricula', 'Grupo', 'Comentarios', 'Profesor', 'Clase']

        if not all(col in df.columns for col in expected_columns):
            return jsonify({'error': 'El archivo no contiene todas las columnas requeridas'}), 400

        data_json = df.to_dict(orient='records')

        conexion = get_db_connection()
        if conexion is None:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

        cursor = conexion.cursor()

        try:
            for row in data_json:
                matricula = str(row['Matricula']).strip()
                grupo_nombre = str(row['Grupo']).strip()
                comentario = row['Comentarios']
                profesor_nombre = row['Profesor']
                clase_nombre = row['Clase']
                respuestas = {k: v for k, v in row.items() if k not in expected_columns}

                # Insertar o verificar Alumno
                cursor.execute("SELECT matricula FROM Alumno WHERE matricula = %s", (matricula,))
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO Alumno (matricula, nombre, apellidoPaterno, apellidoMaterno)
                        VALUES (%s, 'Pendiente', 'Pendiente', 'Pendiente')
                    """, (matricula,))

                # Verificar o crear Materia
                cursor.execute("SELECT clave FROM Materia WHERE nombre = %s", (clase_nombre,))
                materia = cursor.fetchone()
                if materia:
                    clave_materia = materia[0]
                else:
                    cursor.execute("""
                        INSERT INTO Materia (clave, nombre, idDepartamento)
                        VALUES ((SELECT ISNULL(MAX(clave), 100) + 1 FROM Materia), %s, 1)
                    """, (clase_nombre,))
                    conexion.commit()
                    cursor.execute("SELECT clave FROM Materia WHERE nombre = %s", (clase_nombre,))
                    clave_materia = cursor.fetchone()[0]

                # Verificar o crear Grupo
                cursor.execute("SELECT CRN FROM Grupo WHERE grupo = %s AND clave = %s", (grupo_nombre, clave_materia))
                grupo = cursor.fetchone()
                if grupo:
                    crn = grupo[0]
                else:
                    cursor.execute("""
                        INSERT INTO Grupo (idPeriodo, clave, grupo)
                        VALUES (1, %s, %s)
                    """, (clave_materia, grupo_nombre))
                    conexion.commit()
                    cursor.execute("SELECT CRN FROM Grupo WHERE grupo = %s AND clave = %s", (grupo_nombre, clave_materia))
                    crn = cursor.fetchone()[0]

                # Verificar o crear Profesor
                if "," in profesor_nombre:
                    apellido_paterno, nombre_profesor = map(str.strip, profesor_nombre.split(",", 1))
                else:
                    return jsonify({'error': f'Formato incorrecto para el nombre del profesor: {profesor_nombre}'}), 400

                cursor.execute("""
                    SELECT matricula FROM Profesor
                    WHERE nombre = %s AND apellidoPaterno = %s
                """, (nombre_profesor, apellido_paterno))
                profesor = cursor.fetchone()
                if profesor:
                    matricula_profesor = profesor[0]
                else:
                    nueva_matricula_profesor = f"P{clave_materia}{grupo_nombre}"
                    cursor.execute("""
                        INSERT INTO Profesor (matricula, nombre, apellidoPaterno, apellidoMaterno, rol, idDepartamento)
                        VALUES (%s, %s, %s, 'Pendiente', 'Profesor', 1)
                    """, (nueva_matricula_profesor, nombre_profesor, apellido_paterno))
                    conexion.commit()
                    matricula_profesor = nueva_matricula_profesor

                # Relacionar Profesor con Grupo
                cursor.execute("""
                    SELECT 1 FROM ProfesorGrupo WHERE CRN = %s AND matricula = %s
                """, (crn, matricula_profesor))
                if not cursor.fetchone():
                    cursor.execute("INSERT INTO ProfesorGrupo (CRN, matricula) VALUES (%s, %s)", (crn, matricula_profesor))

                # Insertar Comentario
                if comentario and not pd.isna(comentario):
                    cursor.execute("""
                        IF NOT EXISTS (
                            SELECT 1 FROM Comenta
                            WHERE idPregunta = 1 AND matricula = %s AND CRN = %s
                        )
                        BEGIN
                            INSERT INTO Comenta (idPregunta, matricula, CRN, comentario)
                            VALUES (1, %s, %s, %s)
                        END
                    """, (matricula, crn, matricula, crn, comentario))

                # Insertar Respuestas
                for idx, (pregunta, valor) in enumerate(respuestas.items(), start=1):
                    if not pd.isna(valor):
                        cursor.execute("""
                            IF NOT EXISTS (
                                SELECT 1 FROM Responde
                                WHERE matricula = %s AND idPregunta = %s AND CRN = %s
                            )
                            BEGIN
                                INSERT INTO Responde (matricula, idPregunta, CRN, respuesta)
                                VALUES (%s, %s, %s, %s)
                            END
                        """, (matricula, idx, crn, matricula, idx, crn, str(valor)))

            conexion.commit()
            return jsonify({'mensaje': 'Archivo procesado con éxito y registros creados si no existían'}), 200

        except Exception as e:
            conexion.rollback()
            return jsonify({'error': f'Ocurrió un error al procesar el archivo: {str(e)}'}), 500

        finally:
            cursor.close()
            conexion.close()

    return jsonify({'error': 'Formato de archivo no soportado. Por favor sube un archivo .xlsx'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
