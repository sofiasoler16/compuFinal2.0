import multiprocessing
import time

def proceso_notificador(cola_ipc):
    """
    Este es el proceso Notificador IPC. 
    Vive en un bucle infinito esperando alertas.
    """
    print("Notificador IPC iniciado y esperando alertas...")
    while True:
        # El método .get() bloquea el proceso hasta que haya algo en la cola
        alerta = cola_ipc.get()
        
        # Aquí iría la lógica de envío (Email, WhatsApp, SMS, etc.)
        print("\n[!] NOTIFICACIÓN CRÍTICA ENVIADA AL VETERINARIO")
        print(f"Detalle: {alerta['mensaje']}")
        print(f"Datos: {alerta['data']}")
        print("-" * 40)

def analizar_riesgo(movimiento, temperatura):
    """
    Lógica de decisión: Determina si un conjunto de datos 
    merece generar una alerta o es solo un log normal.
    """
    alertas = []
    
    # Lógica para temperatura (Fiebre/Dolor)
    if temperatura >= 40:
        alertas.append(f"Temperatura alta ({temperatura}°C)")
        
    # Lógica para comportamientos de cólico
    comportamientos_criticos = ["revolcandose", "mirar la panza", "rascar piso"]
    if movimiento in comportamientos_criticos:
        alertas.append(f"Comportamiento de dolor: {movimiento}")
        
    return alertas