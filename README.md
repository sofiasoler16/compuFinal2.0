# 🐴 HorseWatch - Sistema de Telemetría y Alertas Equinas

HorseWatch es un sistema distribuido y concurrente diseñado para el monitoreo de la salud equina en tiempo real. Utiliza sensores (simulados) en los boxes para enviar telemetría a un servidor central multihilo, el cual analiza patrones clínicos mediante ventanas deslizantes para detectar signos tempranos de cólico equino.

## 🏗️ Arquitectura del Sistema

### Componentes Principales y Responsabilidades

El proyecto está dividido en tres módulos físicos: Cliente, Servidor y Base de Datos.

#### 1. El Cliente (Sensores)
* **`src/client/sensor.py`**: Actúa como el hardware físico en el box. Su única responsabilidad es conectarse al servidor vía Socket y enviar ráfagas de datos JSON (temperatura, movimiento, BPM) cada segundo. Acepta parámetros por consola para simular caballos sanos o con perfiles de cólico.

#### 2. El Servidor Central (Gateway y Workers)
* **`src/server/gateway.py` (El Director)**: Es el punto de entrada del sistema. Abre el puerto de red (`8080`) y escucha conexiones entrantes. Su única función es aceptar el *handshake* del sensor y crear un `Thread` nuevo e independiente para atender a ese box específico.
* **`src/server/worker.py` (El Operario)**: Es el hilo dedicado a un solo caballo. Mantiene una "memoria a corto plazo" (Ventana Deslizante usando `deque`) con los últimos 3 minutos de actividad del animal. Coordina el guardado de datos y el envío de alertas.
* **`src/server/diagnostics.py` (El Cerebro Clínico)**: Contiene exclusivamente las reglas de medicina veterinaria. Recibe la ventana de tiempo del Worker y evalúa si existe un patrón obstructivo (ej: revolcones + rascadas sin guanear) o fiebre sostenida.
* **`src/server/notifier_process.py` (El Comunicador)**: Es un proceso paralelo (`Multiprocessing`) que vive escuchando una Cola IPC. Recibe las alertas de los Workers y aplica un mecanismo de *Cooldown* (Anti-Spam de 5 minutos) antes de notificar al exterior (Email/SMS).

#### 3. Almacenamiento
* **`src/db/horsedb.py` (El Archivo)**: Maneja la conexión a la base de datos `SQLite`. Implementa un `threading.Lock()` estricto para evitar condiciones de carrera, garantizando que múltiples Workers puedan registrar el historial clínico en el disco físico sin corromper el archivo.

---

## 🔄 Flujo de Vida de un Dato

1. **Nacimiento**: `sensor.py` empaqueta la telemetría en JSON y llama al `.connect()` del servidor.
2. **Recepción**: `gateway.py` detecta la llamada en su `.accept()`, "atiende" y lanza un `worker.py` para esa conexión.
3. **Análisis**: El dato entra al Worker, que lo suma a su ventana de 3 minutos y le pregunta a `diagnostics.py`: *"¿Este historial representa un peligro?"*.
4. **Bifurcación Segura**: 
   * **Siempre**: El Worker le pide la llave (`Lock`) a `horsedb.py`, guarda la lectura en SQLite y devuelve la llave.
   * **En caso de peligro**: El Worker empuja la alerta a la Cola IPC.
5. **Notificación**: `notifier_process.py` captura la alerta de la cola, evalúa si pasaron más de 5 minutos desde el último aviso de ese caballo y despacha el correo al veterinario.

---

## 🚀 Cómo ejecutar el proyecto

Para levantar el ecosistema completo, necesitas usar múltiples terminales.

**Paso 1: Iniciar el Servidor Central**
Esto preparará la base de datos, arrancará el proceso notificador y abrirá el Gateway para escuchar redes IPv4 e IPv6.
```bash
python3 src/server/gateway.py
```

**Paso 2: Conectar un Sensor (Caballo Sano)**
En una nueva terminal, iniciaremos el simulador para un caballo con un perfil saludable .
```bash
python3 src/client/sensor.py --id Box_Condor --perfil saludable --ipv ipv6
```

**Paso 3: Conectar un Sensor (Caballo con Cólico)**
En una tercera terminal, forzaremos un perfil clínico de riesgo para observar el diagnóstico en tiempo real y el mecanismo anti-spam del notificador.
```bash
python3 src/client/sensor.py --id Box_WhiteBoots --perfil colico --ipv ipv4
```