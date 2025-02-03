from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import User
from . import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Acceso denegado: No eres administrador.', 'danger')
        return redirect(url_for('auth.login'))

    users = User.query.all()

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if not username or not password:
            flash('Todos los campos son obligatorios.', 'danger')
            return redirect(url_for('admin.dashboard'))

        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('admin.dashboard'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Usuario {username} creado exitosamente.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('dashboard.html', users=users)
