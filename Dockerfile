# Imagen base
FROM python:3.11

# Definir directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias desde PyPI
RUN pip install --no-cache-dir -r /app/requirements.txt

# Instalar PM2 globalmente
RUN pip install pm2

# Exponer el puerto Flask
EXPOSE 5000

# Comando por defecto al iniciar el contenedor
CMD ["pm2", "start", "/app/run.py", "--interpreter", "python3", "--name", "Form-Monitoreo"]
