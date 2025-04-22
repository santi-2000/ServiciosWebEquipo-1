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
PASSWORD = 'Pioner0s:D'

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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
