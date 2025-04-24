from flask import Flask, request, jsonify
import pandas as pd
import mysql.connector

app = Flask(__name__)

# Función para obtener la conexión a la base de datos MySQL
def obtener_conexion():
    return mysql.connector.connect(
        host="tuhost",  # Cambia esto por el host de tu servidor MySQL
        user="tuusuario",  # Cambia esto por tu usuario de MySQL
        password="tucontraseña",  # Cambia esto por tu contraseña de MySQL
        database="tu_base_de_datos"  # Cambia esto por el nombre de tu base de datos
    )

# Ruta para subir y procesar el archivo
@app.route('/subir_encuesta', methods=['POST'])
def subir_encuesta():
    if 'file' not in request.files:
        return jsonify({'error': 'No se encontró el archivo'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No se seleccionó un archivo'}), 400

    if file and file.filename.endswith('.xlsx'):
        # Leer el archivo Excel
        df = pd.read_excel(file)

        # Identificar las preguntas: buscar columnas con valores numéricos
        preguntas = [col for col in df.columns if df[col].dtype in ['int64', 'float64']]

        # Asegurarse de que las columnas necesarias estén presentes
        columnas_necesarias = ['Grupo', 'Comentarios', 'Profesor', 'Clase', 'Departamento', 'Periodo']
        if not all(col in df.columns for col in columnas_necesarias):
            return jsonify({'error': 'Faltan columnas necesarias'}), 400

        # Insertar los datos en la base de datos
        conexion = obtener_conexion()
        cursor = conexion.cursor()

        for _, row in df.iterrows():
            consulta = """
                INSERT INTO encuestas (grupo, comentarios, profesor, clase, departamento, periodo)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            valores = [row['Grupo'], row['Comentarios'], row['Profesor'], row['Clase'], row['Departamento'], row['Periodo']]
            
            # Añadir los puntajes de las preguntas
            for pregunta in preguntas:
                valores.append(row[pregunta])

            cursor.execute(consulta, valores)

        conexion.commit()
        cursor.close()
        conexion.close()

        return jsonify({'mensaje': 'Archivo procesado con éxito'}), 200

    return jsonify({'error': 'Formato de archivo no soportado. Por favor sube un archivo .xlsx'}), 400


# Ruta para obtener los resultados de las encuestas
@app.route('/resultados', methods=['GET'])
def resultados():
    conexion = obtener_conexion()
    cursor = conexion.cursor(dictionary=True)

    # Consultamos todos los resultados de las encuestas
    cursor.execute("SELECT * FROM encuestas")
    resultados = cursor.fetchall()

    # Identificamos las preguntas dinámicamente: buscar columnas numéricas
    preguntas = [col for col in resultados[0].keys() if isinstance(resultados[0][col], (int, float))]

    promedios = {}
    comentarios = {}

    for encuesta in resultados:
        key = f"{encuesta['profesor']} - {encuesta['clase']}"

        if key not in promedios:
            promedios[key] = {pregunta: 0 for pregunta in preguntas}
            promedios[key]['cantidad'] = 0
            comentarios[key] = []

        # Sumar los puntajes de cada pregunta
        for pregunta in preguntas:
            promedios[key][pregunta] += encuesta[pregunta]

        promedios[key]['cantidad'] += 1

        if encuesta['comentarios']:
            comentarios[key].append(encuesta['comentarios'])

    # Calcular los promedios dividiendo por la cantidad de respuestas
    for key in promedios:
        for pregunta in preguntas:
            promedios[key][pregunta] /= promedios[key]['cantidad']

    # Crear los resultados finales
    resultados_finales = []
    for key, promedios_profesor_clase in promedios.items():
        resultado = {
            "profesor_clase": key,
            "comentarios": comentarios[key],
            "promedios": {pregunta: promedios_profesor_clase[pregunta] for pregunta in preguntas}
        }
        resultados_finales.append(resultado)

    return jsonify(resultados_finales)


if __name__ == "__main__":
    app.run(debug=True)