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
    # Mutiprocessing para tener propia memoria y espacio, si notificador deja de funcionar los workers siguen funcionando
    proc_notificador.start()
    
# 4. Configurar Socket Inteligente (Gateway)
    puerto = 8080 
    
    # AI_PASSIVE y 'None' significan: "Buscame en mi propia máquina dónde puedo escuchar"
    opciones = socket.getaddrinfo(None, puerto, socket.AF_UNSPEC, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)
    server_socket = None
    
    for familia, tipo, protocolo, canonname, direccion in opciones: #Recorre la tupla 
        try:
            server_socket = socket.socket(familia, tipo, protocolo) #Crea el objeto en Mem. 
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #Permite volver a usar el puerto
            server_socket.bind(direccion) #Usa el socket en Mem. y lo "ata" a la tarjeta de red y al puerto
            server_socket.listen(10) #Empezar a escuchar
            
            print(f"\n[GATEWAY ACTIVO] Escuchando de forma independiente del protocolo en: {direccion}\n")
            break # Si logró abrir el puerto, sale del ciclo
            
        except OSError:
            if server_socket:
                server_socket.close()
            server_socket = None
            continue
            
    if server_socket is None:
        print("\n[ERROR FATAL] El Gateway no pudo abrir el puerto en ninguna interfaz de red.")
        sys.exit(1)
    
    try:
        while True:
    # 5. Esperar bloqueado hasta que llegue un sensor
            conexion, direccion = server_socket.accept() #Con accept se queda esperando a que lo llamen (Lo llama el Sensor)
            
            # 6. Crear un Hilo para este box específico 
            hilo_worker = threading.Thread(target=atender_sensor, args=(conexion, direccion, cola_ipc)) #Cada worker tiene su cola_ipc
            hilo_worker.start()
            
    except KeyboardInterrupt:
        print("\n[APAGANDO] Deteniendo el servidor y los procesos...")
        proc_notificador.terminate()
        server_socket.close()

if __name__ == '__main__':
    iniciar_gateway()