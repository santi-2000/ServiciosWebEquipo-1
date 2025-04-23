from flask import Flask, request, jsonify, session
from flask_cors import CORS
import pymssql
import hashlib

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
                return jsonify({'nombre': nombre_completo, 'rol': profesor['rol']})
            else:
                return jsonify({'error': 'Profesor no encontrado'}), 404

        except Exception as e:
            return jsonify({'error': f'Error en BD: {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
    
@app.route('/profesores', methods=['GET'])
def get_profesores():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor(as_dict=True)
            cursor.execute("""
                SELECT p.matricula, p.nombre, p.apellidoPaterno, p.apellidoMaterno, p.rol, d.nombreDepartamento
                FROM Profesor p
                JOIN Departamento d ON p.idDepartamento = d.idDepartamento
            """)
            profesores = cursor.fetchall()
            return jsonify(profesores), 200
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
    idDepartamento = data.get('idDepartamento')

    if not matricula or not nombre or not apellidoPaterno or not apellidoMaterno or not rol or not idDepartamento:
        return jsonify({'error': 'Todos los campos son obligatorios'}), 400

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
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
            cursor.execute("SELECT nombreDepartamento FROM Departamento")  # seleccionamos solo la columna grupo
            Departamento = cursor.fetchall()
            return jsonify(Departamento)
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
    nueva_fecha = data.get('fecha')  # Esto lo puedes ignorar si no usas fechas

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
    
    
if __name__ == '__main__':
    app.run(debug=True, port=5000)

