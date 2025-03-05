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
git clone https://github.com/SlotyHolly/Bot-Discord.git
cd Form-Monitoreo
```
##### Crea un entorno virtual e instálalo:
```git
python -m venv venv
source venv/bin/activate
```
### Instalación de Dependencias sin Acceso a Internet

Si el servidor no tiene acceso a Internet, puedes instalar las dependencias desde un equipo con conexión siguiendo estos pasos:

##### En un equipo con acceso a Internet, crea un directorio para almacenar los paquetes:
```git
mkdir paquetes
pip download -r requirements.txt -d paquetes
```

##### Copia el directorio paquetes al servidor sin acceso a Internet.

##### En el servidor, instala las dependencias desde el directorio copiado:

```git
pip install --no-index --find-links=paquetes -r requirements.txt
```

#### Configuración y Ejecución

##### Ejecuta la aplicación con PM2:
```git
pm2 start run.py --interpreter python3 --name Form-Monitoreo
```

#####  Configuración Automática de Reinicio:
```terminal
pm2 startup
```
Después de ejecutar este comando, PM2 te proporcionará un comando que necesitas copiar y ejecutar para completar la configuración.

#####  Guardar la Lista de Procesos:
```terminal
pm2 save
```

##### Prueba el acceso a la interfaz web en http://localhost:5000


## Contacto

SlotyHolly - [@SlotyHolly](https://twitter.com/SlotyHolly)

Discord - [Discord](https://discord.gg/SlotyHolly)

Link del Proyecto: [https://github.com/SlotyHolly/Bot-Musica-Discord.git](https://github.com/SlotyHolly/Form-Monitoreo)
