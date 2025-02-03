from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from .models import User
from .forms import LoginForm
from . import db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        # 🔹 Si el usuario ya está autenticado, redirigirlo a la página correspondiente
        return redirect(url_for('admin.dashboard') if current_user.role == 'admin' else url_for('main.create_report'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()  # 👈 Usamos `username` en vez de `email`
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Inicio de sesión exitoso', 'success')

            # 🔹 Redirigir según el tipo de usuario
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            else:
                return redirect(url_for('main.create_report'))  # 👈 Redirige a create_report

        else:
            flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html', form=form)
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada correctamente', 'success')
    return redirect(url_for('auth.login'))
