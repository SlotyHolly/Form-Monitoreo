from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from .models import User, HistoryReports
from . import db
from .forms import CreateUserForm, ChangePasswordForm, DeleteUserForm

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role != 'admin':
        session['swal'] = {
                            "title": "Acceso denegado",
                            "text": "No tenés permiso para acceder a esta sección.",
                            "icon": "error"
                        }
        return redirect(url_for('auth.login'))

    users = User.query.all()
    create_user_form = CreateUserForm()
    change_password_form = ChangePasswordForm()
    delete_user_form = DeleteUserForm()

    if create_user_form.validate_on_submit():
        username = create_user_form.username.data
        name = create_user_form.name.data
        password = create_user_form.password.data
        role = create_user_form.role.data

        print(f"[DEBUG] Recibido: Usuario={username}, Role={role}")

        if User.query.filter_by(username=username).first():
            session['swal'] = {
                                "title": "Usuario en uso",
                                "text": "El nombre de usuario ya está en uso.",
                                "icon": "warning"
                            }
            return redirect(url_for('admin.dashboard'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, name=name ,password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        session['swal'] = {
                            "title": "Usuario creado",
                            "text": f"Usuario {username} creado exitosamente.",
                            "icon": "success"
                        }
        return redirect(url_for('admin.dashboard'))
    
    return render_template('dashboard.html', 
                           users=users, 
                           create_user_form=create_user_form,
                           change_password_form=change_password_form,
                           delete_user_form=delete_user_form)

# Ruta para cambiar la contraseña de un usuario
@admin_bp.route('/change_password/<int:user_id>', methods=['POST'])
@login_required
def change_password(user_id):
    if current_user.role != 'admin':
        session['swal'] = {
                    "title": "Acceso denegado",
                    "text": "No tenés permiso para cambiar la contraseña de otros usuarios.",
                    "icon": "error"
                }
        return redirect(url_for('auth.login'))

    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.get(user_id)
        if user:
            new_password = form.new_password.data
            user.password = generate_password_hash(new_password)
            db.session.commit()
            session['swal'] = {
                "title": "Contraseña actualizada",
                "text": f"La contraseña del usuario {user.username} fue guardada correctamente.",
                "icon": "success"
            }
    return redirect(url_for('admin.dashboard'))

# Ruta para eliminar un usuario
@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.role != 'admin':
        session['swal'] = {
                            "title": "Acceso denegado",
                            "text": "No tenés permiso para acceder a esta sección.",
                            "icon": "error"
                        }
        return redirect(url_for('auth.login'))

    form = DeleteUserForm()
    if form.validate_on_submit():
        user = User.query.get(user_id)
        if user:
            
            # 🔹 Primero, desvincular los reportes para que no queden huérfanos
            HistoryReports.query.filter_by(user_id=user.id).update({'user_id': None})
            db.session.commit()


            db.session.delete(user)
            db.session.commit()

            session['swal'] = {
                "title": "Usuario eliminado",
                "text": f"El usuario {user.username} fue eliminado exitosamente.",
                "icon": "success"
            }

    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/delete_report/<int:report_id>')
@login_required
def delete_report(report_id):
    if current_user.role != 'admin':
        session['swal'] = {
                            "title": "Acceso denegado",
                            "text": "No tenés permiso para eliminar reportes.",
                            "icon": "error"
                        }
        return redirect(url_for('main.history_reports'))

    report = HistoryReports.query.get(report_id)

    if report:
        db.session.delete(report)
        db.session.commit()
        session['swal'] = {
                            "title": "Reporte eliminado",
                            "text": f"Reporte {report.id} eliminado correctamente.",
                            "icon": "success"
                        }
    else:
        session['swal'] = {
                            "title": "Reporte inexistente",
                            "text": f"El reporte {report.id} no existe.",
                            "icon": "error"
                        }
    return redirect(url_for('admin.dashboard'))