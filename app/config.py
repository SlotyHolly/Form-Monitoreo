import os
from pathlib import Path

# Asegurar que la base de datos se almacene en el volumen correcto
if os.getenv("ENVIRONMENT") == "docker":
    BASE_DIR = "/app/instance"
else:
    BASE_DIR = Path(__file__).resolve().parent.parent / "instance"

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "nyrmcwznsrQHzCkTCdpPFzUubqZQBa")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'reports_wazuh.sqlite')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False