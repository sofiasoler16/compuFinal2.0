import sqlite3
import matplotlib.pyplot as plt
import os

DB_PATH = "horsewatch.db"

def graficar_signos_vitales(horse_id):
    print(f"\nGenerando reporte clínico para: {horse_id}...")
    
    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    # Extraer los datos (limitado a la ventana de 3 min)
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
    actividades = [fila[2] for fila in resultados]
    tiempo = list(range(len(resultados))) 

    # Configurar el lienzo
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
    fig.suptitle(f"Monitor Clínico - {horse_id}", fontsize=16, fontweight='bold')

    # Gráfico Superior: TEMPERATURA
    ax1.plot(tiempo, temperaturas, color='blue', linestyle='-', marker='.')
    ax1.axhline(y=40.0, color='red', linestyle='--', label='Umbral de Fiebre (40°C)')
    ax1.set_ylabel('Temperatura (°C)')
    ax1.set_title('Evolución de la Temperatura')
    ax1.legend()
    ax1.grid(True, linestyle=':', alpha=0.7)

    # Gráfico Inferior: BPM Y MOVIMIENTOS
    ax2.plot(tiempo, bpms, color='green', linestyle='-', marker='.')
    ax2.axhline(y=50, color='orange', linestyle='--', label='Taquicardia (>50 BPM)')
    
    for i, actividad in enumerate(actividades):
        if actividad in ["revolcandose", "rascar piso", "mirar la panza"]:
            ax2.plot(i, bpms[i], 'ro', markersize=8) 
            ax2.annotate(actividad, (i, bpms[i]), textcoords="offset points", xytext=(0,10), ha='center', fontsize=8, color='red')

    ax2.set_xlabel('Tiempo (Últimas lecturas/segundos)')
    ax2.set_ylabel('Latidos por Minuto (BPM)')
    ax2.set_title('Evolución del Ritmo Cardíaco y Eventos Críticos')
    ax2.legend()
    ax2.grid(True, linestyle=':', alpha=0.7)

    plt.tight_layout()
    
    # --- ACÁ ESTÁ LA MAGIA DEL JPG ---
    nombre_archivo = f"reporte_{horse_id}.jpg"
    
    # Guardamos la figura. dpi=300 asegura que la imagen se vea en alta resolución
    plt.savefig(nombre_archivo, format='jpg', dpi=300) 
    
    # Cerramos la figura para liberar memoria RAM del servidor
    plt.close(fig) 
    
    print(f"✅ ¡Éxito! Gráfico guardado en tu carpeta como: {nombre_archivo}")

def menu_interactivo():
    """Genera un menú dinámico leyendo los caballos que existen en la BD."""
    if not os.path.exists(DB_PATH):
        print(f"[ERROR] No se encontró la BD en: {DB_PATH}")
        print("Asegurate de que el Gateway esté corriendo y haya guardado datos.")
        return

    conexion = sqlite3.connect(DB_PATH)
    cursor = conexion.cursor()
    
    try:
        cursor.execute("SELECT DISTINCT horse_id FROM lecturas")
        caballos = [fila[0] for fila in cursor.fetchall()]
    except sqlite3.OperationalError:
        print("[ERROR] La tabla 'lecturas' no existe todavía. Conectá un sensor primero.")
        conexion.close()
        return
        
    conexion.close()

    if not caballos:
        print("\nTodavía no hay ningún caballo registrado en la base de datos.")
        return

    while True:
        print("\n" + "="*30)
        print("🐴 MENÚ DE MONITOREO CLÍNICO")
        print("="*30)
        
        for i, caballo in enumerate(caballos):
            print(f"{i + 1}. Generar informe de {caballo}")
            
        print("0. Salir del programa")
        print("="*30)
        
        opcion = input("\nIngresá el número de opción: ").strip()
        
        if opcion == "0":
            print("Cerrando generador de gráficos...")
            break
            
        try:
            indice = int(opcion) - 1
            if 0 <= indice < len(caballos):
                graficar_signos_vitales(caballos[indice])
            else:
                print("[ERROR] Número fuera de la lista. Intentá de nuevo.")
        except ValueError:
            print("[ERROR] Tenés que ingresar un número válido.")

if __name__ == '__main__':
    menu_interactivo()