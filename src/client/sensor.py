import socket
import json
import time
import random
import argparse

HOST = '::1'
PORT = 8080

MOVIMIENTOS = [
    "revolcandose", "parado", "comiendo", 
    "rascar piso", "mirar la panza", "guaneando"
]

TEMPERATURAS = [36.0, 37.5, 38.0, 39.0, 40.0, 41.0, 42.0]

def generar_datos(horse_id, perfil):
    """Genera datos basados en el perfil de salud asignado."""
    
    # Definimos los pesos de probabilidad según el perfil
    if perfil == "saludable":
        # Baja probabilidad de síntomas de cólico, temperaturas normales
        pesos_mov = [0, 45, 45, 0, 0, 10] 
        pesos_temp = [5, 40, 50, 5, 0, 0, 0] 
    elif perfil == "colico":
        # Alta probabilidad de comportamientos de colico y fiebre
        pesos_mov = [20, 10, 0, 25, 25, 0]
        pesos_temp = [0, 5, 10, 15, 30, 25, 15]

    movimiento = random.choices(MOVIMIENTOS, weights=pesos_mov, k=1)[0]
    temperatura = random.choices(TEMPERATURAS, weights=pesos_temp, k=1)[0]
    
    # Lógica de BPM
    bpm = random.randint(28, 44)
    if temperatura >= 40.0 or movimiento in ["revolcandose", "mirar la panza", "rascar piso"]:
        bpm = random.randint(55, 80)

    return {
        "horse_id": horse_id,
        "bpm": bpm,
        "temperatura": temperatura,
        "movimiento": movimiento
    }

def iniciar_sensor(horse_id, perfil, ip_version): #Enciendo el sensor
    print(f"--- Iniciando Sensor Simulador ---")
    print(f"Box: {horse_id} | Perfil: {perfil.upper()} | Red: {ip_version.upper()}")
    
    # Configuramos el socket dependiendo de si es IPv4 o IPv6
    if ip_version == "ipv4":
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host_conexion = '127.0.0.1' # Localhost en IPv4
    else:
        cliente = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        host_conexion = '::1'       # Localhost en IPv6
        
    try:
        # IPv4 usa una tupla de 2 (host, puerto). IPv6 usa una tupla de 4.
        if ip_version == "ipv4":
            cliente.connect((host_conexion, PORT)) #Aca llama al puerto 8080 que espera ser llamado en notifier_process
        else:
            cliente.connect((host_conexion, PORT, 0, 0)) #Aca tambien
            
        print(f"[CONECTADO] Transmitiendo datos a {host_conexion}:{PORT}...\n")
        # COMO VIAJAN LOS DATOS
        while True:
            datos = generar_datos(horse_id, perfil)
            mensaje_json = json.dumps(datos) #Los empaqueta en JSON. Por que? 
            cliente.send(mensaje_json.encode('utf-8')) #Lo manda a ...
            
            alerta_visual = "⚠️" if datos['temperatura'] >= 40.0 or datos['movimiento'] in ["revolcandose", "mirar la panza", "rascar piso"] else "✅"
            print(f"[{alerta_visual} ENVIADO] Temp: {datos['temperatura']}°C | Mov: {datos['movimiento']:<15} | BPM: {datos['bpm']}")
            time.sleep(1)
            
    except ConnectionRefusedError:
        print("\n[ERROR] No se pudo conectar. ¿Está el servidor encendido?")
    except KeyboardInterrupt:
        print("\n[APAGANDO] Sensor desconectado.")
    finally:
        cliente.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Simulador de Sensores HorseWatch")
    parser.add_argument("--id", required=True, help="Nombre o ID del Box (ej. Box_Luna)")
    parser.add_argument("--perfil", choices=["saludable", "colico"], required=True, help="Perfil de salud del caballo")
    # Nuevo argumento para probar la red:
    parser.add_argument("--ipv", choices=["ipv4", "ipv6"], default="ipv6", help="Versión de IP a utilizar")
    
    args = parser.parse_args()
    iniciar_sensor(args.id, args.perfil, args.ipv)