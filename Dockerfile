# Imagen base de Python
FROM python:3.11.9

# Definir directorio de trabajo
WORKDIR /app

# Copiar la carpeta `app/` dentro del contenedor
COPY app /app/

# Copiar `run.py` en la raíz del contenedor
COPY run.py /run.py

# Copiar `requirements.txt`
COPY requirements.txt /requirements.txt

# Instalar dependencias desde `requirements.txt`
RUN pip install --no-cache-dir -r /requirements.txt

# Establecer `PYTHONPATH` para que Python reconozca `app/`
ENV PYTHONPATH=/app

# Exponer el puerto Flask
EXPOSE 5000

# Ejecutar `run.py` desde la raíz
CMD ["python3", "/run.py"]