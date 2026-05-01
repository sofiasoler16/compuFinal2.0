import multiprocessing
import time

# 300 segundos = 5 minutos de espera para el veterinario
COOLDOWN_EMAIL = 300 
# 10 segundos de espera para no saturar la pantalla con logs locales
COOLDOWN_LOG = 10 

def proceso_notificador(cola_ipc): 
    """Este es el proceso Notificador IPC. Vive esperando alertas."""

    # Diccionarios independientes para controlar los tiempos
    ultimos_emails = {}
    ultimos_logs = {}

    print("Notificador IPC iniciado (modo silencioso contra spam)...")
    while True:
        # El método .get() bloquea el proceso hasta que haya algo en la cola
        alerta = cola_ipc.get()
        horse_id = alerta['data']['horse_id']
        ahora = time.time()
        
        # 1. CONTROL DEL LOG LOCAL (Pantalla)
        ultimo_log = ultimos_logs.get(horse_id, 0)
        
        # Si ya pasaron 10 segundos desde el último mensaje en pantalla print log
        if (ahora - ultimo_log) > COOLDOWN_LOG:
            print(f"\n[LOG LOCAL] Alerta detectada en {horse_id}: {alerta['mensaje']}")
            ultimos_logs[horse_id] = ahora # Reseteamos el reloj del log de pantalla

        # 2. CONTROL DEL EMAIL AL VETERINARIO
        ultimo_email = ultimos_emails.get(horse_id, 0)

        # Si ya pasaron 5 minutos desde el último email print email ahora, despues enviar mail
        if (ahora - ultimo_email) > COOLDOWN_EMAIL:
            enviar_notificacion_externa(alerta)
            ultimos_emails[horse_id] = ahora # Reseteamos el reloj del email
            

def enviar_notificacion_externa(alerta):
    """
    Aquí iría el código real de smtplib para el email.
    """
    print(">>> [EMAIL ENVIADO AL VETERINARIO] <<<")
    print(f"Asunto: Emergencia en {alerta['data']['horse_id']}")