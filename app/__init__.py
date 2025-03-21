from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from .config import Config
import os

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Leer versión desde archivo
    version_path = os.path.join(os.path.dirname(__file__), '..', 'VERSION')
    try:
        with open(version_path, 'r') as f:
            app.config['APP_VERSION'] = f.read().strip()
    except FileNotFoundError:
        app.config['APP_VERSION'] = 'desconocida'

    db.init_app(app)
    login_manager.init_app(app)

    from .models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # 🔹 Corregimos la vista de login
    login_manager.login_view = 'auth.login'  
    login_manager.login_message_category = "info"  # Opcional: para mensajes flash

    from .routes import main_bp
    from .auth import auth_bp
    from .admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')  # 🔹 Aseguramos que las rutas de auth tienen el prefijo '/auth'
    app.register_blueprint(admin_bp, url_prefix='/admin')

    print("🔍 Ruta de la base de datos:", app.config["SQLALCHEMY_DATABASE_URI"])
    print("📁 Existe carpeta?", os.path.exists(os.path.dirname(app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", ""))))


    with app.app_context():
        db.create_all()
        create_admin_user()

    @app.context_processor
    def inject_version():
        return dict(app_version=app.config['APP_VERSION'])

    return app

    
def create_admin_user():
    """Crea un usuario admin por defecto si no existe"""
    from .models import User

    admin_username = "admin"
    admin_name = "Administrador"
    admin_hashed_password = "scrypt:32768:8:1$N70q7zbhlYwgpHWd$8f8346400eb23548f1c82bbc8a281511ff677bf486988fa91b35ada48bff6582f0c172d9b791b2394e3836a9e9a187c836fb90bcb972e6645a77253f3c100b02"
    admin_role = "admin"

    # Verificar si ya existe un usuario admin
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        admin = User(username=admin_username, name=admin_name, password=admin_hashed_password, role=admin_role)
        db.session.add(admin)
        db.session.commit()
        print("✅ Usuario admin creado correctamente.")
    else:
        print("✅ Usuario admin ya existe.")
