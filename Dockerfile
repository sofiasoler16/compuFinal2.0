# Usamos una versión oficial y liviana de Python
FROM python:3.12-slim

# Le decimos a Docker en qué carpeta interna vamos a trabajar
WORKDIR /app

# Copiamos primero el archivo de dependencias
COPY requirements.txt .

# Instalamos matplotlib
RUN pip install --no-cache-dir -r requirements.txt

# El código en sí NO lo copiamos acá, lo vamos a montar con un Volumen en el Compose