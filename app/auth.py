from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .models import User
from flask_cors import cross_origin

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["POST", "OPTIONS"])
@cross_origin(origins="http://localhost:5173", supports_credentials=True)
def api_login():
    """Maneja login y solicitudes OPTIONS para preflight CORS."""
    if request.method == "OPTIONS":
        print("✅ Respuesta a OPTIONS en /api/login")  # Debugging
        return jsonify({"message": "CORS preflight OK"}), 200  # ✅ Responde correctamente a OPTIONS

    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        login_user(user)
        return jsonify({"message": "Login exitoso"}), 200

    return jsonify({"error": "Credenciales incorrectas"}), 401


@auth_bp.route("/check_session", methods=["GET"])
@cross_origin(origins="http://localhost:5173", supports_credentials=True)
def check_session():
    """Verifica si el usuario sigue autenticado."""
    if current_user.is_authenticated:
        return jsonify({"logged_in": True, "username": current_user.username, "role": current_user.role}), 200
    return jsonify({"logged_in": False}), 401


@auth_bp.route("/logout", methods=["POST"])
@cross_origin(origins="http://localhost:5173", supports_credentials=True)
@login_required
def api_logout():
    """Cierra la sesión del usuario."""
    logout_user()
    return jsonify({"message": "Sesión cerrada"}), 200

