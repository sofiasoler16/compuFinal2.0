import json
import sys
import os
from collections import deque # <--- Importar la estructura con MEMORIA

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.horsedb import guardar_lectura
from server.diagnostics import analizar_riesgo_ventana 

def atender_sensor(conexion, direccion, cola_ipc):
    print(f"[NUEVO BOX CONECTADO] Dirección IPv6: {direccion}")
    
    # CREAMOS LA MEMORIA DEL CABALLO (La ventana deslizante) DE CADA CABALLO (Cada Hilo tiene la suya)
    # 180 lecturas = 3 minutos a 1 lectura por segundo
    memoria_movimientos = deque(maxlen=180)
    memoria_temperaturas = deque(maxlen=180)
    
    try:
        while True:
            datos_crudos = conexion.recv(1024)
            if not datos_crudos:
                break
            
            datos = json.loads(datos_crudos.decode('utf-8')) #Lo de-codifica de utf-8 a texto otra vez
            #Con json.loads lo convierte de json a diccionario python
            
            # 1. Agregamos el nuevo dato a la memoria (si está llena, el más viejo se borra)
            memoria_movimientos.append(datos['movimiento'])
            memoria_temperaturas.append(datos['temperatura'])
            
            # 2. Analizamos TODA la memoria junta (los últimos 3 minutos)
            alertas = analizar_riesgo_ventana(list(memoria_movimientos), list(memoria_temperaturas)) #analizar_riesgo_ventana en diagnostic.py
            alertas_str = ", ".join(alertas) if alertas else "Ninguna" 
            
            # 3. Guardar el log individual en la BD siempre
            guardar_lectura(
                datos['horse_id'], 
                datos['bpm'], 
                datos['temperatura'], 
                datos['movimiento'], 
                alertas_str
            )
            
            # 4. Si la ventana entera dictaminó que hay peligro, avisamos al Notificador
            if alertas:
                alerta_msg = {
                    'mensaje': alertas_str, # Envia el texto del patrón encontrado
                    'data': datos
                }
                cola_ipc.put(alerta_msg) #pone la alerta en la cola
                
    except json.JSONDecodeError:
        print(f"[ERROR] Datos corruptos recibidos de {direccion}")
    except Exception as e:
        print(f"[ERROR EN WORKER] {e}")
    finally:
        conexion.close()
        print(f"[BOX DESCONECTADO] {direccion}")