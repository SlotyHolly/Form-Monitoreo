# Generador de Reportes Monitoreo Flask

Este proyecto es una aplicación web basada en Flask para la generación de reportes en distintos formatos (HTML, CSV) a partir de datos estructurados.
.

## Características

- API REST con Flask
- Generación de reportes en PDF, HTML y CSV
- Plantillas personalizadas
- Integración con bases de datos SQLite
- Endpoint para carga de datos
- Interfaz web para generar y visualizar reportes.

## Instalación

Instrucciones paso a paso sobre cómo instalar y configurar el bot en un servidor de Discord.

### Requisitos Previos

- Python --> 3.11.9
- Flask --> 3.1.0
- SQLAlchemy --> 2.0.36
- Flask-SQLAlchemy --> 3.0.0
- flask_login --> 0.6.3
- flask_wtf --> 1.2.2

### Pasos de Instalación

#### Descargar la Última Versión de la Imagen:
```git
docker pull slotyholly/form-monitoreo:latest
```
#### Verifica que la imagen se descargó correctamente:
```git
docker images
```
#### Crear el docker-compose.yml con la siguiente estructura:
```git
nano docker-compose.yml
```

```git
version: '3.8'

services:
  form-monitoreo:
    container_name: Form-Monitoreo
    image: slotyholly/form-monitoreo:latest
    volumes:
      - sqlite_data:/app/instance
    environment:
      - FLASK_APP=/run.py
      - FLASK_ENV=production
      - SECRET_KEY=nyrmcwznsrQHzCkTCdpPFzUubqZQBa
    command: gunicorn -w 4 -b 0.0.0.0:5000 run:app
    restart: always

  nginx:
    image: nginx:stable
    container_name: nginx-proxy
    ports:
      - "5000:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
    depends_on:
      - form-monitoreo

volumes:
  sqlite_data:
    driver: local

```

#### Crear los certificados para HTTPS:

##### PowerShell:

```git
mkdir -p nginx/ssl
```

```git
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/key.pem -out nginx/ssl/cert.pem -subj "/CN=form-monitoreo.local"
```

##### Bash:

```git
mkdir -p nginx/ssl
```

```git
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/CN=form-monitoreo.local"

```

#### Iniciar el Contenedor con docker-compose:

```git
docker-compose up -d
```

### Acceder a la Aplicación

##### Prueba el acceso a la interfaz web en http://localhost:5000

## Contacto

SlotyHolly - [@SlotyHolly](https://twitter.com/SlotyHolly)

Discord - [Discord](https://discord.gg/SlotyHolly)

Docker Hub - [Docker Hub](https://hub.docker.com/u/slotyholly)

Link del Proyecto: [https://github.com/SlotyHolly/Bot-Musica-Discord.git](https://github.com/SlotyHolly/Form-Monitoreo)
