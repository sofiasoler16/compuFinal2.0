import multiprocessing
import time

# 600 segundos = 10 minutos
COOLDOWN_NOTIFICACION = 600

def proceso_notificador(cola_ipc):
    """
    Este es el proceso Notificador IPC. 
    Vive en un bucle infinito esperando alertas.
    """
    # Diccionario para guardar { 'ID_CABALLO': timestamp_ultima_alerta }
    ultimas_notificaciones = {}

    print("Notificador IPC iniciado y esperando alertas...")
    while True:
        # El método .get() bloquea el proceso hasta que haya algo en la cola
        alerta = cola_ipc.get()
        horse_id = alerta['data']['horse_id']
        ahora = time.time()
        
        # 1. Siempre mostramos en la terminal local (para control interno)
        print(f"\n[LOG LOCAL] Alerta detectada en {horse_id}: {alerta['mensaje']}")

        # 2. Verificar si debemos enviar la notificación externa (Email/Sms)
        ultimo_aviso = ultimas_notificaciones.get(horse_id, 0)

        if (ahora - ultimo_aviso) > COOLDOWN_NOTIFICACION:
            # HA PASADO SUFICIENTE TIEMPO: Enviamos la notificación real
            enviar_notificacion_externa(alerta)
            # Actualizamos el registro del tiempo
            ultimas_notificaciones[horse_id] = ahora
        else:
            # NO HA PASADO EL TIEMPO: Solo ignoramos el envío externo
            tiempo_restante = int(COOLDOWN_NOTIFICACION - (ahora - ultimo_aviso))
            print(f"[SPAM CONTROL] Notificación externa silenciada para {horse_id}. "
                  f"Faltan {tiempo_restante}s para el próximo aviso permitido.")

def enviar_notificacion_externa(alerta):
    """
    Aquí iría el código real de smtplib para el email.
    """
    print(">>> [EMAIL ENVIADO AL VETERINARIO] <<<")
    print(f"Asunto: Emergencia en {alerta['data']['horse_id']}")
    
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