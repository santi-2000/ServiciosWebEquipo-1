from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pymssql
import hashlib
import pandas as pd
import hashlib
from unidecode import unidecode


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

def normalizar(texto):
    return unidecode(texto.strip().lower())

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
    
    
@app.route('/profesores/rol', methods=['GET'])
def get_roles_profesor():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("""
                SELECT DISTINCT rol
                FROM Profesor
            """)
            roles = cursor.fetchall()

            # Extrae solo el campo 'rol' de cada fila
            roles_list = [r['rol'] for r in roles]

            return jsonify(roles_list), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener roles: {e}'}), 500
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

            cursor.execute("""
                SELECT idDepartamento FROM Departamento WHERE nombreDepartamento = %s
            """, (nombreDepartamento,))
            result = cursor.fetchone()

            if not result:
                return jsonify({'error': f'El departamento "{nombreDepartamento}" no existe'}), 400

            idDepartamento = result[0]

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
    
@app.route('/calificacion/maxima', methods=['GET'])
def obtener_calificacion_maxima():
    if 'username' not in session:
        return jsonify({'error': 'No has iniciado sesión'}), 401

    username = session['username']  # matrícula del profesor

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("""
                SELECT MAX(CAST(r.respuesta AS FLOAT)) AS calificacion_maxima
                FROM Responde r
                JOIN ProfesorGrupo pg ON r.CRN = pg.CRN
                WHERE pg.matricula = %s
                  AND ISNUMERIC(r.respuesta) = 1
                  AND TRY_CAST(r.respuesta AS FLOAT) BETWEEN 1 AND 10
            """, (username,))
            resultado = cursor.fetchone()

            if resultado and resultado['calificacion_maxima'] is not None:
                return jsonify({'calificacion_maxima': round(resultado['calificacion_maxima'], 2)})
            else:
                return jsonify({'error': 'No se encontraron calificaciones válidas'}), 404

        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/promedio_pregunta/<int:idPregunta>', methods=['GET'])
def promedio_pregunta(idPregunta):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(CAST(respuesta AS FLOAT)) 
                FROM Responde 
                WHERE idPregunta = %s
            """, (idPregunta,))
            promedio = cursor.fetchone()[0]
            return jsonify({'idPregunta': idPregunta, 'promedio': promedio})
        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/max_pregunta/<int:idPregunta>', methods=['GET'])
def max_pregunta(idPregunta):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT MAX(CAST(respuesta AS FLOAT)) 
                FROM Responde 
                WHERE idPregunta = %s
            """, (idPregunta,))
            maxima = cursor.fetchone()[0]
            return jsonify({'idPregunta': idPregunta, 'maxima_calificacion': maxima})
        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/promedio_profesor_grupo/<string:matricula>/<int:CRN>', methods=['GET'])
def promedio_profesor_grupo(matricula, CRN):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT AVG(CAST(r.respuesta AS FLOAT))
                FROM Responde r
                JOIN ProfesorGrupo pg ON r.CRN = pg.CRN
                WHERE pg.matricula = %s AND r.CRN = %s
            """, (matricula, CRN))
            promedio = cursor.fetchone()[0]
            return jsonify({'matricula': matricula, 'CRN': CRN, 'promedio': promedio})
        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    

@app.route('/calificacion/minima', methods=['GET'])
def obtener_calificacion_minima():
    if 'username' not in session:
        return jsonify({'error': 'No has iniciado sesión'}), 401

    username = session['username']  # Esto es la matrícula del profesor

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("""
                SELECT MIN(CAST(r.respuesta AS FLOAT)) AS calificacion_minima
                FROM Responde r
                JOIN ProfesorGrupo pg ON r.CRN = pg.CRN
                WHERE pg.matricula = %s
                  AND ISNUMERIC(r.respuesta) = 1
                  AND TRY_CAST(r.respuesta AS FLOAT) BETWEEN 1 AND 10
            """, (username,))
            resultado = cursor.fetchone()

            if resultado and resultado['calificacion_minima'] is not None:
                return jsonify({'calificacion_minima': round(resultado['calificacion_minima'], 2)})
            else:
                return jsonify({'error': 'No se encontraron calificaciones válidas'}), 404

        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


@app.route('/promedio_general_profesor/<string:matricula>', methods=['GET'])
def promedio_general_profesor(matricula):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            # Solo respuestas numéricas válidas (1 al 10)
            cursor.execute("""
                SELECT AVG(CAST(r.respuesta AS FLOAT))
                FROM Responde r
                JOIN ProfesorGrupo pg ON r.CRN = pg.CRN
                WHERE pg.matricula = %s
                  AND ISNUMERIC(r.respuesta) = 1
                  AND TRY_CAST(r.respuesta AS FLOAT) BETWEEN 1 AND 10
            """, (matricula,))

            promedio = cursor.fetchone()[0]

            if promedio is None:
                return jsonify({
                    'matricula': matricula,
                    'promedio_general': None,
                    'mensaje': 'Sin respuestas válidas (del 1 al 10)'
                }), 200

            return jsonify({
                'matricula': matricula,
                'promedio_general': round(promedio, 2)
            }), 200

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

@app.route('/preguntas', methods=['GET'])
def get_preguntas():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT * FROM Pregunta")
            pregunta = cursor.fetchall()
            return jsonify(pregunta), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener usuarios: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/respuestas', methods=['GET'])
def get_respuestas():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("SELECT * FROM Responde")
            respuesta = cursor.fetchall()
            return jsonify(respuesta), 200
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
            cursor.execute("SELECT CRN FROM Grupo")  
            grupos = cursor.fetchall()
            
            crns = [g['CRN'] for g in grupos]

            return jsonify(crns), 200
        except Exception as e:
            return jsonify({'error': f'Error al obtener grupos: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/total_preguntas', methods=['GET'])
def total_preguntas():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Pregunta")
            total = cursor.fetchone()[0]
            return jsonify({'total_preguntas': total})
        except Exception as e:
            return jsonify({'error': f'Error al contar preguntas: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

@app.route('/total_respuestas', methods=['GET'])
def total_respuestas():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Responde")
            total = cursor.fetchone()[0]
            return jsonify({'total_respuestas': total})
        except Exception as e:
            return jsonify({'error': f'Error al contar respuestas: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500

    

@app.route('/subir_encuesta', methods=['POST'])
def subir_encuesta():
    if 'file' not in request.files:
        return "No se encontró el archivo", 400

    file = request.files['file']
    if file.filename == '':
        return "El nombre del archivo está vacío", 400

    try:
        df = pd.read_excel(file)
    except Exception as e:
        return f"Error al leer el archivo Excel: {str(e)}", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    preguntas = df.columns[5:]
    pregunta_ids = []
    for pregunta in preguntas:
        cursor.execute("SELECT idPregunta FROM Pregunta WHERE pregunta = %s", (pregunta,))
        row = cursor.fetchone()
        if row:
            pregunta_ids.append(row[0])
        else:
            cursor.execute("INSERT INTO Pregunta(pregunta) VALUES (%s)", (pregunta,))
            cursor.execute("SELECT SCOPE_IDENTITY()")
            pregunta_ids.append(cursor.fetchone()[0])

    for _, row in df.iterrows():
        matricula = row['Matricula']
        grupo_str = row['Grupo']
        comentario = row['Comentarios']
        profesor_nombre = row['Profesor']
        clase = row['Clase']

        partes = profesor_nombre.strip().split(',')
        if len(partes) != 2:
            continue

        apellido_paterno = normalizar(partes[0])
        nombre_completo = normalizar(partes[1])
        nombre_parts = nombre_completo.split()

        nombre_prof = nombre_parts[0] if nombre_parts else ''
        apellido_materno = nombre_parts[-1] if len(nombre_parts) > 1 else ''

        cursor.execute("SELECT matricula, nombre, apellidoPaterno, apellidoMaterno FROM Profesor")
        profesores = cursor.fetchall()

        matricula_prof = None
        for prof in profesores:
            if (
                normalizar(prof[1]) == nombre_prof and
                normalizar(prof[2]) == apellido_paterno and
                normalizar(prof[3]) == apellido_materno
            ):
                matricula_prof = prof[0]
                break

        if not matricula_prof:
            matricula_prof = f"P{hash(profesor_nombre) % 10000}"
            cursor.execute("""
                INSERT INTO Profesor(matricula, nombre, apellidoPaterno, apellidoMaterno, rol, idDepartamento)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (matricula_prof, nombre_prof, apellido_paterno, apellido_materno, 'Profesor', 1))

        cursor.execute("SELECT clave FROM Materia WHERE nombre = %s", (clase,))
        row_mat = cursor.fetchone()
        if row_mat:
            clave = row_mat[0]
        else:
            clave = hash(clase) % 10000
            cursor.execute("INSERT INTO Materia(clave, nombre, idDepartamento) VALUES (%s, %s, %s)",
                           (clave, clase, 1))

        cursor.execute("SELECT CRN FROM Grupo WHERE clave = %s", (clave,))
        row_grp = cursor.fetchone()
        if row_grp:
            crn = row_grp[0]
        else:
            crn = hash(grupo_str + clase) % 10000
            cursor.execute("INSERT INTO Grupo(CRN, idPeriodo, clave) VALUES (%s, %s, %s)", (crn, 1, clave))

        cursor.execute("SELECT * FROM ProfesorGrupo WHERE CRN = %s AND matricula = %s", (crn, matricula_prof))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO ProfesorGrupo(CRN, matricula) VALUES (%s, %s)", (crn, matricula_prof))

        cursor.execute("SELECT * FROM Alumno WHERE matricula = %s", (matricula,))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO Alumno(matricula, nombre, apellidoPaterno, apellidoMaterno) VALUES (%s, %s, %s, %s)",
                           (matricula, 'Nombre', 'ApellidoP', 'ApellidoM'))

        for i, pid in enumerate(pregunta_ids):
            respuesta = row[i + 5]
            cursor.execute("""
                SELECT 1 FROM Responde WHERE matricula = %s AND idPregunta = %s AND CRN = %s
            """, (matricula, pid, crn))
            if cursor.fetchone():
                cursor.execute("""
                    UPDATE Responde SET respuesta = %s
                    WHERE matricula = %s AND idPregunta = %s AND CRN = %s
                """, (str(respuesta), matricula, pid, crn))
            else:
                cursor.execute("""
                    INSERT INTO Responde(matricula, idPregunta, CRN, respuesta)
                    VALUES (%s, %s, %s, %s)
                """, (matricula, pid, crn, str(respuesta)))

        cursor.execute("SELECT 1 FROM Comenta WHERE matricula = %s AND CRN = %s", (matricula, crn))
        if cursor.fetchone():
            cursor.execute("UPDATE Comenta SET comentario = %s WHERE matricula = %s AND CRN = %s",
                           (comentario, matricula, crn))
        else:
            cursor.execute("INSERT INTO Comenta(matricula, CRN, comentario) VALUES (%s, %s, %s)",
                           (matricula, crn, comentario))

    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Datos cargados correctamente"}), 200

if __name__ == '__main__':
    app.run(debug=True)