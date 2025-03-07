# Imagen base de Python
FROM python:3.11.9

# Definir directorio de trabajo
WORKDIR /app

# Instalar Node.js y npm para usar PM2
RUN apt-get update && apt-get install -y nodejs npm

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias desde PyPI
RUN pip install --no-cache-dir -r /app/requirements.txt

# Instalar PM2 globalmente con npm
RUN npm install -g pm2

# Exponer el puerto Flask
EXPOSE 5000

# Comando por defecto al iniciar el contenedor
CMD ["python3", "/run.py"]
