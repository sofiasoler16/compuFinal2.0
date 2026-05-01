import socket
import threading
import multiprocessing
import sys
import os

# Ajustamos el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from server.notifier_process import proceso_notificador
from server.worker import atender_sensor
from db.horsedb import inicializar_db

def iniciar_gateway():
    # 1. Inicializar la Base de Datos 
    inicializar_db() # Ve que este la BD iniciada

    # 2. Crear la Cola IPC para memoria compartida. De quienes? POr que?
    cola_ipc = multiprocessing.Queue()
    
    # 3. Iniciar el proceso Notificador en un núcleo separado
    proc_notificador = multiprocessing.Process(target=proceso_notificador, args=(cola_ipc,)) #Crea el proceso notificador como multiprocessing no como HILO
    # MUltiprocessing porque 
    proc_notificador.start()
    
    # 4. Configurar Socket IPv6 (Gateway)
    
    server_socket = socket.socket(socket.AF_INET6, socket.SOCK_STREAM) # AF_INET6 es clave para soportar IPv6
    
    # Puerto de escucha y bind ("::" significa escuchar en todas las interfaces IPv6)
    puerto = 8080 #Abre el puerto 8080
    server_socket.bind(('::', puerto))
    server_socket.listen(10) # Permite encolar hasta 10 sensores conectándose al mismo milisegundo
    print(f"\n[GATEWAY ACTIVO] Escuchando conexiones IPv6 en el puerto {puerto}...\n")
    
    try:
        while True:
    # 5. Esperar bloqueado hasta que llegue un sensor
            conexion, direccion = server_socket.accept() #Con accept se queda esperando a que lo llamen (Lo llama el Sensor)
            
            # 6. Crear un Hilo para este box específico y soltarlo a trabajar
            hilo_worker = threading.Thread(target=atender_sensor, args=(conexion, direccion, cola_ipc)) #Cada worker tiene su cola_ipc
            hilo_worker.start()
            
    except KeyboardInterrupt:
        print("\n[APAGANDO] Deteniendo el servidor y los procesos...")
        proc_notificador.terminate()
        server_socket.close()

if __name__ == '__main__':
    iniciar_gateway()