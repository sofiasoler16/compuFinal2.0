import multiprocessing
import time

# 300 segundos = 5 minutos
COOLDOWN_NOTIFICACION = 300

def proceso_notificador(cola_ipc): #Este es el proceso Notificador IPC. Vive esperando alertas.

    # Diccionario para guardar { 'ID_CABALLO': timestamp_ultima_alerta }
    ultimas_notificaciones = {}

    print("Notificador IPC iniciado (modo silencioso contra spam)...")
    while True:
        # El método .get() bloquea el proceso hasta que haya algo en la cola
        alerta = cola_ipc.get()
        horse_id = alerta['data']['horse_id']
        ahora = time.time()
        
        # 1. Siempre mostramos en la terminal local (para control interno)
        print(f"\n[LOG LOCAL] Alerta detectada en {horse_id}: {alerta['mensaje']}")

        # 2. Verificar si debemos enviar la notificación externa (Email/Sms)
        # (Dentro del while True: de proceso_notificador)
        ultimo_aviso = ultimas_notificaciones.get(horse_id, 0)

        if (ahora - ultimo_aviso) > COOLDOWN_NOTIFICACION:
            # Ahora el LOG LOCAL solo se imprime cada 5 minutos
            print(f"\n[LOG LOCAL] Alerta detectada en {horse_id}: {alerta['mensaje']}")
            enviar_notificacion_externa(alerta)
            ultimas_notificaciones[horse_id] = ahora
            

def enviar_notificacion_externa(alerta):
    """
    Aquí iría el código real de smtplib para el email.
    """
    print(">>> [EMAIL ENVIADO AL VETERINARIO] <<<")
    print(f"Asunto: Emergencia en {alerta['data']['horse_id']}")
    
