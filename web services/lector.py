import pymssql
from unidecode import unidecode

def normalizar(texto):
    return unidecode(texto.strip().lower())

conn = pymssql.connect(server='localhost', user='sa', password='YourPassword123!', database='Data')
cursor = conn.cursor()

cursor.execute("SELECT matricula, nombre, apellidoPaterno, apellidoMaterno FROM Profesor")
profesores = cursor.fetchall()

print("\n>>> Profesores en BD (normalizados):")
for prof in profesores:
    matricula, nombre, ap_pat, ap_mat = prof
    clave = f"{normalizar(ap_pat)}, {normalizar(nombre)} {normalizar(ap_mat)}"
    print(f"Matricula: {matricula} → '{clave}'")