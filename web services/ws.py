import pymssql
from flask import Flask, request, jsonify, session, redirect, url_for
from flask_cors import CORS
import hashlib

app = Flask(__name__)
CORS(app)

app.secret_key = 'your_secret_key'  # Replace with a strong, random secret key

SERVER = 'localhost'
DATABASE = 'master'
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
    hashed_provided_password = hashlib.sha1(
        provided_password.encode()).hexdigest()
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
            cursor.execute(
                "SELECT username, contrasena FROM usuarios WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and verify_password(user['contrasena'], password):
                session['username'] = username
                return jsonify({'mensaje': 'Autenticacion exitosa'}), 200
            else:
                return jsonify({'error': 'Usuario o password incorrectas'}), 401
        except Exception as e:
            return jsonify({'error': f'Error en BD {e}'}), 500
        finally:
            conn.close()
    else:
        return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
