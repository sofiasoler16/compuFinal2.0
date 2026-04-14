import json
import sys
import os

# Ajustamos el path para poder importar módulos de otras carpetas
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.horsedb import guardar_lectura
from server.notifier_process import analizar_riesgo

def atender_sensor(conexion, direccion, cola_ipc):
    print(f"[NUEVO BOX CONECTADO] Dirección IPv6: {direccion}")
    try:
        while True:
            # Recibimos hasta 1024 bytes (suficiente para un JSON de sensores)
            datos_crudos = conexion.recv(1024)
            if not datos_crudos:
                break # El sensor se desconectó
            
            # Convertimos el texto recibido a un diccionario de Python
            datos = json.loads(datos_crudos.decode('utf-8'))
            
            # 1. Analizar riesgo de cólico
            alertas = analizar_riesgo(datos['movimiento'], datos['temperatura'])
            alertas_str = ", ".join(alertas) if alertas else "Ninguna"
            
            # 2. Guardar en SQLite (usando función con Lock seguro)
            guardar_lectura(
                datos['horse_id'], 
                datos['bpm'], 
                datos['temperatura'], 
                datos['movimiento'], 
                alertas_str
            )
            
            # 3. Notificar vía IPC si hay alerta
            if alertas:
                alerta_msg = {
                    'mensaje': f"¡Signos de dolor abdominal en {datos['horse_id']}!",
                    'data': datos
                }
                cola_ipc.put(alerta_msg)
                
    except json.JSONDecodeError:
        print(f"[ERROR] Datos corruptos recibidos de {direccion}")
    except Exception as e:
        print(f"[ERROR EN WORKER] {e}")
    finally:
        conexion.close()
        print(f"[BOX DESCONECTADO] {direccion}")