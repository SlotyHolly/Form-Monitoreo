import os

# Asegurar que la base de datos se almacene en el volumen correcto
BASE_DIR = "/app/instance"

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "nyrmcwznsrQHzCkTCdpPFzUubqZQBa")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'reports_wazuh.sqlite')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False