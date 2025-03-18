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

##### Descargar la Última Versión de la Imagen:
```git
docker pull slotyholly/form-monitoreo:latest
```
##### Verifica que la imagen se descargó correctamente:
```git
docker images
```

##### Iniciar el Contenedor con docker-compose:

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
