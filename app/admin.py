from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import User
from . import db
from .forms import CreateUserForm, ChangePasswordForm, DeleteUserForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role != 'admin':
        flash('Acceso denegado: No eres administrador.', 'danger')
        return redirect(url_for('auth.login'))

    users = User.query.all()
    create_user_form = CreateUserForm()
    change_password_form = ChangePasswordForm()
    delete_user_form = DeleteUserForm()

    # Manejar la creación de usuario con Flask-WTF
    if create_user_form.validate_on_submit():
        username = create_user_form.username.data
        password = create_user_form.password.data
        role = create_user_form.role.data

        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya está en uso.', 'danger')
            return redirect(url_for('admin.dashboard'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Usuario {username} creado exitosamente.', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('dashboard_admin.html', 
                           users=users, 
                           create_user_form=create_user_form,
                           change_password_form=change_password_form,
                           delete_user_form=delete_user_form)

# Ruta para cambiar la contraseña de un usuario
@admin_bp.route('/change_password/<int:user_id>', methods=['POST'])
@login_required
def change_password(user_id):
    if current_user.role != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('auth.login'))

    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.get(user_id)
        if user:
            new_password = form.new_password.data
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash(f'Contraseña de {user.username} actualizada.', 'success')

    return redirect(url_for('admin.dashboard'))

# Ruta para eliminar un usuario
@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        flash('Acceso denegado.', 'danger')
        return redirect(url_for('auth.login'))

    form = DeleteUserForm()
    if form.validate_on_submit():
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            flash(f'Usuario {user.username} eliminado correctamente.', 'success')

    return redirect(url_for('admin.dashboard'))
