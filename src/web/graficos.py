import sqlite3
import matplotlib.pyplot as plt
import os
# AGREGADO: Importamos Counter para poder hacer el gráfico de torta
from collections import Counter

DB_PATH = "horsewatch.db"

def graficar_signos_vitales(horse_id):
    print(f"\nGenerando reporte clínico para: {horse_id}...")
    
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor() #Que es cursor?
    
    # Extraer los datos 
    cursor.execute('''
            SELECT temperatura, bpm, actividad 
            FROM lecturas 
            WHERE horse_id = ? 
            ORDER BY id DESC 
            LIMIT 180
        ''', (horse_id,))

    resultados = cursor.fetchall()
    conexion.close()

    if not resultados:
        print(f"[ERROR] No hay datos registrados para {horse_id}.")
        return

    # Invertir para que el tiempo vaya de pasado a presente
    resultados.reverse() 
    
    temperaturas = [fila[0] for fila in resultados]
    bpms = [fila[1] for fila in resultados]
    # Usamos los nombres de variables que coinciden con el bloque de dibujo
    movimientos = [fila[2] for fila in resultados]
    tiempos = list(range(len(resultados))) 

    # ELIMINADO: El 'subplots' de 2 que tenías antes
    
    # Configuramos el lienzo de 3 gráficos
    fig, (ax_temp, ax_bpm, ax_mov) = plt.subplots(3, 1, figsize=(10, 12))
    fig.suptitle(f"Monitor Clínico - {horse_id}", fontsize=16, fontweight='bold')

    # --- GRÁFICO 1: TEMPERATURA ---
    ax_temp.plot(tiempos, temperaturas, color='blue', marker='.')
    ax_temp.axhline(y=40.0, color='red', linestyle='--', label='Umbral Fiebre')
    ax_temp.set_title("Evolución de la Temperatura")
    ax_temp.set_ylabel("Temperatura (°C)")
    ax_temp.grid(True, linestyle=':', alpha=0.6)
    ax_temp.legend()

    # --- GRÁFICO 2: BPM LIMPIO ---
    ax_bpm.plot(tiempos, bpms, color='green', marker='.')
    ax_bpm.axhline(y=50, color='orange', linestyle='--', label='Taquicardia')
    ax_bpm.set_title("Evolución del Ritmo Cardíaco")
    ax_bpm.set_ylabel("Latidos (BPM)")
    ax_bpm.grid(True, linestyle=':', alpha=0.6)
    ax_bpm.legend()

    # --- GRÁFICO 3: NUEVO RESUMEN DE MOVIMIENTOS ---
    conteo_movimientos = Counter(movimientos)
    etiquetas = list(conteo_movimientos.keys())
    cantidades = list(conteo_movimientos.values())

    colores_mov = []
    for mov in etiquetas:
        if mov in ["revolcandose", "mirar la panza", "rascar piso"]:
            colores_mov.append('#ff9999') # Rojo suave (Alerta)
        else:
            colores_mov.append('#99ff99') # Verde suave (Normal)

    # Dibujamos el gráfico de torta
    ax_mov.pie(cantidades, labels=etiquetas, colors=colores_mov, autopct='%1.1f%%', startangle=90)
    ax_mov.set_title("Comportamiento en los últimos 3 minutos")

    # Ajustamos los espacios para que no se choquen los títulos
    plt.tight_layout()

    nombre_archivo = f"reporte_{horse_id}.jpg"
    
    plt.savefig(nombre_archivo, format='jpg', dpi=300) 
    plt.close()
    
    print(f"✅ ¡Éxito! Gráfico guardado en tu carpeta como: {nombre_archivo}")

def menu_interactivo():
    """Genera un menú dinámico leyendo los caballos que existen en la BD."""
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] No se encontró la BD en: {DB_PATH}")
        print("Asegurate de que el Gateway esté corriendo y haya guardado datos.")
        return

    # EL BUCLE ARRANCA ACÁ ARRIBA AHORA
    while True:
        # 1. Abrimos conexión y consultamos los 30 segundos EN CADA VUELTA
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        
        try:
            cursor.execute("SELECT DISTINCT horse_id FROM lecturas WHERE timestamp >= datetime('now', '-30 seconds')")
            caballos = [fila[0] for fila in cursor.fetchall()]
        except sqlite3.OperationalError:
            print("[ERROR] La tabla 'lecturas' no existe todavía. Conectá un sensor primero.")
            conexion.close()
            return
            
        conexion.close() # Cerramos la conexión rápido para no bloquear

        # 2. Dibujamos el menú con la información fresquita
        print("\n" + "="*30)
        print("🐴 MENÚ DE MONITOREO CLÍNICO")
        print("="*30)
        
        if not caballos:
            print("Ningún caballo transmitiendo en los últimos 30 segundos...")
        else:
            for i, caballo in enumerate(caballos):
                print(f"{i + 1}. Generar informe de {caballo}")
            
        print("0. Salir del programa")
        print("="*30)
        
        opcion = input("\nIngresá el número de opción o apretá Enter para actualizar: ").strip()
        
        if opcion == "0":
            print("Cerrando generador de gráficos...")
            break
            
        # Si el usuario solo apretó Enter, el bucle vuelve a empezar y actualiza la lista silenciosamente
        if opcion == "":
            continue
            
        # 3. Validamos la opción elegida
        if caballos:
            try:
                indice = int(opcion) - 1
                if 0 <= indice < len(caballos):
                    graficar_signos_vitales(caballos[indice])
                else:
                    print("[ERROR] Número fuera de la lista. Intentá de nuevo.")
            except ValueError:
                print("[ERROR] Tenés que ingresar un número válido.")
        else:
            print("[INFO] Esperando datos... Apretá Enter para actualizar o 0 para salir.")

if __name__ == '__main__':
    menu_interactivo()