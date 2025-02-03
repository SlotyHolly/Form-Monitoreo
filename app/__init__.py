from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from werkzeug.security import generate_password_hash
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

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

    with app.app_context():
        db.create_all()
        create_admin_user()

    return app


def create_admin_user():
    """Crea un usuario admin por defecto si no existe"""
    from .models import User

    admin_username = "admin"
    admin_password = "admin123"  # Cambiar esto en producción
    admin_role = "admin"

    # Verificar si ya existe un usuario admin
    admin = User.query.filter_by(username=admin_username).first()
    if not admin:
        hashed_password = generate_password_hash(admin_password)
        admin = User(username=admin_username, password=hashed_password, role=admin_role)
        db.session.add(admin)
        db.session.commit()
        print(f"🔹 Usuario admin creado: {admin_username} / Contraseña: {admin_password}")
    else:
        print("✅ Usuario admin ya existe.")
