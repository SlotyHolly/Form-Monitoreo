from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from flask_session import Session
from .config import Config

# 🔹 Inicializar extensiones sin crear una nueva app
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Crea y configura la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    from .models import User
    from flask_cors import CORS
    
    # 🔹 Configurar almacenamiento de sesión en cookies
    app.config["SESSION_TYPE"] = "filesystem"  # Almacena sesiones en archivos temporales
    app.config["SESSION_PERMANENT"] = False
    app.config["SESSION_USE_SIGNER"] = True
    app.config["SESSION_KEY_PREFIX"] = "flask_login_"  
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SECURE"] = False  # ⚠️ Cambia a True en producción con HTTPS
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # Permitir compartir cookies con frontend

    # 🔹 Inicializar Flask-Session correctamente
    Session(app)

    db.init_app(app)
    login_manager.init_app(app)

    # 🔹 Configurar Flask-Login
    login_manager.login_view = "auth.api_login"
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))  # Obtener usuario desde la BD

    # 🔹 Configurar CORS correctamente para permitir envío de cookies
    CORS(app, supports_credentials=True)

    from .routes import main_bp
    from .auth import auth_bp
    from .admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

def create_admin_user():
    """Crea un usuario admin por defecto si no existe."""
    from .models import User  # Importación dentro de la función para evitar errores de importación circular

    admin_username = "admin"
    admin_password = "admin123"  # Cambiar esto en producción
    admin_role = "admin"

    # Verificar si ya existe un usuario admin
    with db.session.begin():
        admin = User.query.filter_by(username=admin_username).first()
        if not admin:
            hashed_password = generate_password_hash(admin_password)
            admin = User(username=admin_username, password=hashed_password, role=admin_role)
            db.session.add(admin)
            print(f"🔹 Usuario admin creado: {admin_username} / Contraseña: {admin_password}")
        else:
            print("✅ Usuario admin ya existe.")
