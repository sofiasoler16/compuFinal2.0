import http.server
import socketserver
import sqlite3
import os
from urllib.parse import urlparse, parse_qs
import sys

# Ajuste del path para importar tu función de gráficos
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from src.web.graficos import graficar_signos_vitales

PORT = 8000
DB_PATH = "horsewatch.db"

class HorseWatchWebHandler(http.server.BaseHTTPRequestHandler):
    
    def do_GET(self):
        """
        Este método se ejecuta cada vez que el navegador pide una URL.
        Sección 2.5 del apunte de teoría clase 
        """
        # Parseamos la URL para extraer la ruta principal y los parámetros
        parsed_url = urlparse(self.path)
        ruta = parsed_url.path

        # --- RUTA 1: Servir los archivos de imagen JPG ---
        # Si el navegador web pide una imagen, la leemos del disco y se la mandamos cruda
        if ruta.endswith('.jpg'):
            nombre_archivo = ruta.lstrip('/') # Le sacamos la barra inicial
            try:
                with open(nombre_archivo, 'rb') as file:
                    self.send_response(200)
                    self.send_header('Content-type', 'image/jpeg')
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_error(404, 'Imagen no encontrada en el servidor')
            return

        # --- RUTA 2: Página Principal (Dashboard) ---
        if ruta == '/':
            self.mostrar_dashboard()

        # --- RUTA 3: Detalle Clínico del Caballo ---
        elif ruta == '/caballo':
            # Extraemos el parámetro 'id' de la URL (Ej: /caballo?id=Box_WhiteBoots)
            query_params = parse_qs(parsed_url.query)
            if 'id' in query_params:
                horse_id = query_params['id'][0]
                self.mostrar_detalle_caballo(horse_id)
            else:
                self.send_error(400, "Error HTTP 400 (Bad Request): Falta el ID del caballo en la URL")
        
        # --- RUTA 4: Error 404 por defecto ---
        else:
            self.send_error(404, "Error HTTP 404 (Not Found): Página no encontrada")

    def mostrar_dashboard(self):
        """Genera el HTML de la página de inicio dinámicamente."""
        try:
            conexion = sqlite3.connect(DB_PATH)
            cursor = conexion.cursor()
            cursor.execute("SELECT DISTINCT horse_id FROM lecturas WHERE timestamp >= datetime('now', '-30 seconds')")
            caballos = [fila[0] for fila in cursor.fetchall()]
            conexion.close()
        except sqlite3.OperationalError:
            caballos = []

        # Armamos el cuerpo del mensaje HTTP (El HTML)
        html = "<!DOCTYPE html><html><head><title>HorseWatch Dashboard</title><meta charset='utf-8'></head>"
        html += "<body style='font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px;'>"
        html += "<h1 style='color: #2c3e50;'>🐴 Dashboard Central de HorseWatch</h1>"
        html += "<p>Seleccioná un box para ver su estado clínico en tiempo real:</p>"
        html += "<ul>"
        
        for caballo in caballos:
            html += f"<li style='margin-bottom: 10px;'><a href='/caballo?id={caballo}' style='font-size: 18px; text-decoration: none; color: #2980b9; padding: 5px; border: 1px solid #2980b9; border-radius: 5px; display: inline-block;'>Ver monitor de <b>{caballo}</b></a></li>"
            
        if not caballos:
            html += "<p style='color: red;'>No hay datos registrados aún. Asegurate de que el Gateway y los sensores estén funcionando.</p>"
            
        html += "</ul></body></html>"

        # Aplicamos la estructura estricta HTTP que pide tu teoría
        self.send_response(200) # Código 200 OK
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

    def mostrar_detalle_caballo(self, horse_id):
        """Genera el HTML con el detalle y la foto del gráfico."""
        
        # 1. ACTUALIZAR GRÁFICO: Llamamos a tu otro archivo para que genere un JPG fresco
        graficar_signos_vitales(horse_id)
        
        # 2. BUSCAR ÚLTIMO DATO: Leemos la BD para mostrar cómo está ahora mismo
        conexion = sqlite3.connect(DB_PATH)
        cursor = conexion.cursor()
        cursor.execute("SELECT temperatura, bpm, actividad, alertas_generadas FROM lecturas WHERE horse_id = ? ORDER BY id DESC LIMIT 1", (horse_id,))
        resultado = cursor.fetchone()
        conexion.close()

        html = f"<!DOCTYPE html><html><head><title>Monitor - {horse_id}</title><meta charset='utf-8'></head>"
        html += "<body style='font-family: Arial, sans-serif; padding: 20px;'>"
        html += f"<h2 style='color: #34495e;'>Monitor Clínico: {horse_id}</h2>"
        html += "<a href='/' style='text-decoration: none; color: #7f8c8d;'>🔙 Volver al Dashboard</a><hr>"
        
        if resultado:
            temp, bpm, act, alertas = resultado
            html += "<h3>Último registro detectado:</h3>"
            html += f"<p><b>🌡️ Temperatura:</b> {temp}°C</p>"
            html += f"<p><b>❤️ Ritmo Cardíaco:</b> {bpm} BPM</p>"
            html += f"<p><b>🐎 Actividad Actual:</b> {act}</p>"
            
            color_alerta = "red" if alertas != "Ninguna" else "green"
            texto_alerta = alertas if alertas else "Ninguna"
            html += f"<p><b>⚠️ Diagnóstico del Sistema:</b> <span style='color: {color_alerta}; font-weight: bold;'>{texto_alerta}</span></p>"
            
            # 3. INSERTAR IMAGEN: Usamos la etiqueta HTML para incrustar el JPG
            # Cuando el navegador lea esto, hará otra petición automática a la ruta de la imagen
            html += f"<br><img src='/reporte_{horse_id}.jpg' alt='Gráfico Clínico' style='max-width: 100%; border: 1px solid #ccc; box-shadow: 2px 2px 10px rgba(0,0,0,0.1);'>"
        else:
            html += "<p>No se encontraron datos para este caballo en la base de datos.</p>"

        html += "</body></html>"

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))

if __name__ == "__main__":
    # Usamos ThreadingHTTPServer como indica tu teoría para manejar a varios usuarios a la vez
    with socketserver.ThreadingTCPServer(("", PORT), HorseWatchWebHandler) as httpd:
        print(f"\n[WEB SERVER HTTP] Servidor de visualización activo.")
        print(f"👉 Abrí tu navegador de internet y entrá a: http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nApagando servidor web HTTP...")