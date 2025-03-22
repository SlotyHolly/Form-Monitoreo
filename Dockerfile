# Imagen base de Python con menos paquetes innecesarios
FROM python:3.13.2-slim

# Definir directorio de trabajo
WORKDIR /app

# Copiar la carpeta `app/` dentro del contenedor
COPY app /app/

# Copiar `run.py` en la raíz del contenedor
COPY run.py /run.py

COPY VERSION /VERSION

# Instalar paquetes del sistema necesarios y actualizar dependencias de seguridad
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copiar `requirements.txt`
COPY requirements.txt /requirements.txt

# Instalar dependencias en un solo paso optimizado
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /requirements.txt

# Establecer `PYTHONPATH` para que Python reconozca `app/`
ENV PYTHONPATH=/:/app

# Exponer el puerto Flask
EXPOSE 5000

# Ejecutar `run.py` desde la raíz
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
