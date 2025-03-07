# Imagen base de Python
FROM python:3.11.9

# Definir directorio de trabajo
WORKDIR /app

# Copiar archivos del proyecto
COPY . /app

# Instalar dependencias desde PyPI
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exponer el puerto Flask
EXPOSE 5000

# Comando por defecto al iniciar el contenedor
CMD ["python3", "/run.py"]
