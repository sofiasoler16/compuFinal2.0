import sqlite3
import threading

# 1. Crea el candado (Lock) 
db_lock = threading.Lock()

def inicializar_db():
    # Creamos la conexión (se crea el archivo si no existe)
    conexion = sqlite3.connect('horsewatch.db')
    cursor = conexion.cursor()
    
    # Tabla con los campos necesarios para el monitoreo
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lecturas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            horse_id TEXT NOT NULL,
            bpm REAL,
            temperatura REAL,
            actividad TEXT,
            alertas_generadas TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conexion.commit()
    conexion.close()
    print("Base de datos 'horsewatch.db' e inicializada correctamente.")

# 2. Función que usarán los Workers para escribir sin pisarse
def guardar_lectura(horse_id, bpm, temperatura, actividad, alertas_generadas):
    """
    Guarda una lectura en la BD de forma segura usando un Lock.
    """
    # El bloque 'with db_lock:' pide la llave, ejecuta el código 
    # de adentro, y devuelve la llave automáticamente al terminar o si hay un error.
    with db_lock:
        try:
            conexion = sqlite3.connect('horsewatch.db')
            cursor = conexion.cursor()
            
            # Usamos '?' para evitar inyecciones SQL y formatear bien los datos
            cursor.execute('''
                INSERT INTO lecturas (horse_id, bpm, temperatura, actividad, alertas_generadas)
                VALUES (?, ?, ?, ?, ?)
            ''', (horse_id, bpm, temperatura, actividad, alertas_generadas))
            
            conexion.commit()
            print(f"Datos guardados para {horse_id} de forma segura.")
            
        except sqlite3.Error as e:
            print(f"Error al escribir en la base de datos: {e}")
            
        finally:
            if 'conexion' in locals():
                conexion.close()

if __name__ == "__main__":
    inicializar_db()

    # 2. Simulamos que llegó un dato de un sensor y lo guardamos
    guardar_lectura("Box_Luna", 45.0, 38.5, "Inquieta, escarbando", "Posible dolor abdominal")
    guardar_lectura("Box_Coca", 38.0, 37.8, "Tranquila, comiendo", "Ninguna")





