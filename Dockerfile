# Imagen base
FROM python:3.11.9

# Definir directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Copiar paquetes descargados previamente
COPY ../paquetes /app/paquetes
COPY requirements.txt /app/

# Instalar dependencias desde la carpeta local
RUN pip install --no-index --find-links=/app/paquetes -r requirements.txt

# Instalar PM2 globalmente (si está en los paquetes descargados)
RUN pip install --no-index --find-links=/app/paquetes pm2

# Exponer el puerto Flask
EXPOSE 5000

# Comando por defecto al iniciar el contenedor
CMD ["pm2", "start", "/app/run.py", "--interpreter", "python3", "--name", "Form-Monitoreo"]
