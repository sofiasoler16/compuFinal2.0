import multiprocessing
import time
import smtplib
from email.message import EmailMessage
from queue import Empty

# 300 segundos = 5 minutos de espera para el veterinario
COOLDOWN_EMAIL = 300 
# 10 segundos de espera para no saturar la pantalla con logs locales
COOLDOWN_LOG = 10 

# --- CONFIGURACIÓN DE CORREO ---
EMAIL_ORIGEN = "sofiasoler16044@gmail.com"
PASSWORD_APP = "awvq pyyv arfa fglk" 
EMAIL_VETERINARIO = "sofi@sofiasoler.com.ar"

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
        # AGREGAR envio de EMAIL REAL (Esperar OK)
        ultimo_email = ultimos_emails.get(horse_id, 0)

        # Si ya pasaron 5 minutos desde el último email print email ahora, despues enviar mail
        if (ahora - ultimo_email) > COOLDOWN_EMAIL:
            enviar_notificacion_externa(alerta)
            ultimos_emails[horse_id] = ahora # Reseteamos el reloj del email
            

def enviar_notificacion_externa(alerta):
    """
    Se conecta al servidor SMTP de Google y envía la alerta real.
    """
    # Extraemos los datos del diccionario (usamos .get por seguridad por si algún dato falta)
    horse_id = alerta['data']['horse_id']
    temperatura = alerta['data'].get('temperatura', 'N/A')
    movimiento = alerta['data'].get('movimiento', 'N/A')
    bpm = alerta['data'].get('bpm', 'N/A')
    mensaje_motivo = alerta.get('mensaje', 'Se detectaron síntomas de cólico.')

    print(f"\n>>> [EMAIL] Conectando con servidor para notificar emergencia en {horse_id}...")
    
    # Armamos el texto del mail
    cuerpo = f"URGENTE: {mensaje_motivo}\n\n"
    cuerpo += f"Datos Clínicos actuales del paciente:\n"
    cuerpo += f"- Box: {horse_id}\n"
    cuerpo += f"- Temperatura: {temperatura}°C\n"
    cuerpo += f"- Movimiento: {movimiento}\n"
    cuerpo += f"- Ritmo Cardíaco: {bpm} BPM\n\n"
    cuerpo += "Por favor, acceda al monitor web para ver el gráfico clínico en tiempo real."

    # Preparamos el sobre del mail
    msg = EmailMessage()
    msg.set_content(cuerpo)
    msg['Subject'] = f'⚠️ EMERGENCIA HORSEWATCH: {horse_id}'
    msg['From'] = EMAIL_ORIGEN
    msg['To'] = EMAIL_VETERINARIO

    max_reintentos = 3
    for intento in range(max_reintentos):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls() 
            server.login(EMAIL_ORIGEN, PASSWORD_APP)
            server.send_message(msg)
            server.quit()
            print(f">>> [✅ EMAIL ENVIADO EXITOSAMENTE] <<<")
            break # Si funcionó, rompemos el bucle y terminamos
            
        except Exception as e:
            print(f"[❌ INTENTO {intento + 1} FALLÓ] Sin internet: {e}")
            if intento < max_reintentos - 1:
                print("Esperando 10 segundos antes de reintentar...")
                time.sleep(10) # Espera un ratito a ver si vuelve el Wi-Fi