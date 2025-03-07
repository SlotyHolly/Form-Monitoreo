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

##### Clonar el repositorio:
```git
git clone --branch main --single-branch https://github.com/SlotyHolly/Form-Monitoreo.git
cd Form-Monitoreo
```
##### Construir y Levantar el Contenedor en el Servidor
```git
docker-compose build
```

Construir la imagen desde el código clonado:
```git
docker-compose build
```

Levantar los contenedores en segundo plano:

```git
docker-compose up -d
```
Ver los logs en tiempo real:

```git
docker-compose logs -f
```
Verificar que el contenedor está corriendo:
```git
docker ps
```

### Verificar Persistencia de SQLite

Dado que SQLite se encuentra en app/instance/, se debe comprobar que el volumen funciona correctamente:

```git
docker exec -it flask_report_generator ls -lh /app/instance
```

Si todo está bien, deberías ver el archivo reports_wazuh.sqlite

### Acceder a la Aplicación


##### Prueba el acceso a la interfaz web en http://localhost:5000


## Contacto

SlotyHolly - [@SlotyHolly](https://twitter.com/SlotyHolly)

Discord - [Discord](https://discord.gg/SlotyHolly)

Link del Proyecto: [https://github.com/SlotyHolly/Bot-Musica-Discord.git](https://github.com/SlotyHolly/Form-Monitoreo)
