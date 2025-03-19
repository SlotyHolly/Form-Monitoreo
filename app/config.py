import os

# Definir directorio donde se almacenará la base de datos dentro del volumen de Docker
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database")

# Asegurarse de que el directorio exista con permisos adecuados
os.makedirs(BASE_DIR, exist_ok=True, mode=0o755)

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "nyrmcwznsrQHzCkTCdpPFzUubqZQBa")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'reports_wazuh.sqlite')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
