from flask import Blueprint, jsonify, render_template, redirect, url_for, flash, request, flash
from .models import User, HistoryReports, FailedConnection, FailedIp, CreatedUser, BlockedUsers, BlockedIp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_required, current_user
from .forms import ReportForm
from . import db, create_app
import csv
from flask import request, session
from werkzeug.utils import secure_filename
from .forms import UploadCSVForm
import os
from datetime import datetime, timedelta
import re

# Crear un Blueprint para las rutas principales
main_bp = Blueprint('main', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app' , 'uploads')  # 👈 Define la ruta completa
ALLOWED_EXTENSIONS = {"csv"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    if not filename:
        return False
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    return extension in ALLOWED_EXTENSIONS


@main_bp.route('/')
def index():
    """Redirigir al login si el usuario no está autenticado"""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))  # Si está autenticado, va al dashboard
        else:
            return redirect(url_for('main.create_report'))  # Si está autenticado, va a la creación de reportes
    return redirect(url_for('auth.login'))  # Si no está autenticado, va al login

@main_bp.route('/history_reports')
@login_required
def history_reports():
    """Muestra los reportes creados por el usuario (o todos si es admin)."""
    if current_user.role == 'admin' or current_user.role == 'visualizacion':
        reports = HistoryReports.query.order_by(HistoryReports.created_at.desc()).all()
    else:
        reports = HistoryReports.query.filter_by(user_id=current_user.id).order_by(HistoryReports.created_at.desc()).all()

    return render_template('history_reports.html', reports=reports)

@main_bp.route('/report/<int:report_id>')
@login_required
def reporte(report_id):
    report = HistoryReports.query.get_or_404(report_id)

    if current_user.role not in ['admin', 'visualizacion'] and report.user_id != current_user.id:
        session['swal'] = {
                        "title": "Acceso denegado",
                        "text": "No tenés permiso para acceder a este reporte.",
                        "icon": "error"
                    }
        return redirect(url_for('main.history_reports'))
    
    return render_template('report.html', report=report)

@main_bp.route('/create_report', methods=['GET', 'POST'])
@login_required
def create_report():
    form = UploadCSVForm()

    if request.method == "GET":
        return render_template('create_report.html', form=form)

    if form.validate_on_submit():

        # 🔹 Asegurar que `report_date` siempre tenga un valor
        if current_user.role == "admin":
            report_date = form.report_date.data  # Mantenerlo como `date`
            report_date = datetime.combine(report_date, datetime.utcnow().time())  # Convertir a `datetime`
        else:
            report_date = datetime.utcnow() - timedelta(hours=3)  # UTC-3

        # 🔹 Redondear a minutos eliminando segundos y microsegundos
        report_date = report_date.replace(second=0, microsecond=0)

        files = {
            "failed_users": form.failed_users_csv.data,
            "failed_ips": form.failed_ips_csv.data,
            "blocked_users": form.blocked_users_csv.data,
            "blocked_ips": form.blocked_ips_csv.data,
            "users_added": form.users_added_csv.data
        }

        file_paths = {}
        for key, file in files.items():
            if file:  # Solo validar si el archivo realmente fue subido
                if allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(file_path)
                    file_paths[key] = file_path
                else:
                    file_paths[key] = None 
            else:
                file_paths[key] = None

        if any(file_paths.values()):
            process_csvs(file_paths, current_user, report_date)
            session['swal'] = {
                                "title": "Reporte generado",
                                "text": "El informe fue creado correctamente y está disponible en el historial.",
                                "icon": "success"
                            }
            delete_files(file_paths)  # 🔹 Elimina los archivos después de procesarlos
        else:
            session['swal'] = {
                                "title": "Error al cargar",
                                "text": "Uno o más archivos cargados no tienen el formato permitido.",
                                "icon": "warning"
                            }

        return redirect(url_for('main.create_report'))


    print("❌ ERROR: Formulario no pasó la validación.")
    print(f"🔍 Errores de validación: {form.errors}")
    return render_template('create_report.html', form=form)

@main_bp.route('/change_password', methods=['GET'])
@login_required
def perfil():
    return render_template('change_password.html')

@main_bp.route('/change_password', methods=['POST'])
@login_required
def change_password():
    current_pwd = request.form.get('current_password')
    new_pwd = request.form.get('new_password')
    confirm_pwd = request.form.get('confirm_password')

    # Verifica campos vacíos
    if not all([current_pwd, new_pwd, confirm_pwd]):
        flash("Todos los campos son obligatorios.", "warning")
        return redirect(url_for('main.change_password'))

    # Verifica contraseña actual
    if not check_password_hash(current_user.password, current_pwd):
        flash("La contraseña actual es incorrecta.", "danger")
        return redirect(url_for('main.change_password'))

    # Verifica coincidencia
    if new_pwd != confirm_pwd:
        flash("Las nuevas contraseñas no coinciden.", "warning")
        return redirect(url_for('main.change_password'))

    # Verifica fortaleza
    error_msg = validar_password_segura(new_pwd)
    if error_msg:
        flash(error_msg, "warning")
        return redirect(url_for('main.change_password'))

    # Actualiza
    current_user.password = generate_password_hash(new_pwd)
    db.session.commit()

    session['swal'] = {
                        "title": "Contraseña actualizada",
                        "text": "Se aplicaron los cambios correctamente.",
                        "icon": "success"
}
    return redirect(url_for('main.create_report'))

def process_csvs(file_paths, current_user, report_date=None, debug=False):
    """Procesa los 5 archivos CSV y guarda los datos en la base de datos."""
    print(f"📂 Abriendo archivo: {file_paths}")
    history = HistoryReports(user_id=current_user.id, name=current_user.name, created_at=report_date)
    db.session.add(history)
    db.session.commit()

    if debug:
        
        if debug:
            print(f"✅ Se creó HistoryReports con ID: {history.id}")

    for csv_type, file_path in file_paths.items():


        if file_path is None:
            if debug:
                print(f"⚠️ ADVERTENCIA: Archivo {csv_type} no encontrado. Saltando...")
            continue

        if not os.path.exists(file_path):
            if debug:
                print(f"⚠️ ADVERTENCIA: Archivo {csv_type} no encontrado. Saltando...")
            continue  # 👈 Salta al siguiente CSV

        if debug:
            print(f"📂 Abriendo archivo {csv_type}: {file_path}")

        with open(file_path, newline='', encoding='utf-8-sig') as csvfile:  # 👈 Usa utf-8-sig
            reader = csv.DictReader(csvfile)
            # 🔹 Normalizar nombres de columnas eliminando espacios y comillas
            reader.fieldnames = [col.strip().replace('"', '') for col in reader.fieldnames]
            
            if debug:
                print(f"📌 Encabezados detectados en {csv_type}: {reader.fieldnames}")

            # 🔹 Mostrar las primeras 5 líneas del CSV
            rows = list(reader)
            
            if debug:
                print(f"📊 Primeras 5 filas de {csv_type}: {rows[:5]}")

            # Si no hay filas, mostrar un mensaje de error
            if not rows:
                if debug:
                    print(f"❌ ERROR: El archivo {csv_type} está vacío o mal formateado.")
                continue  # Saltamos este archivo y pasamos al siguiente

            reader.fieldnames = [col.strip().replace('"', '') for col in reader.fieldnames]

            if csv_type == "failed_users":
                for row in rows:
                    
                    if debug:
                        print(f"Procesando fila: {row}")  # 🔹 Verificar cada fila antes de insertar

                    user = row.get("Usuario", "").strip()
                    server = row.get("Servidor", "").strip()
                    count = row.get("Cantidad", "0").strip()

                    if user and server:
                        failed_connection = FailedConnection(
                            user=user,
                            server=server,
                            count=int(count) if count.isdigit() else 0,
                            id_history=history.id
                        )
                        db.session.add(failed_connection)
                        db.session.commit()
                        
                        if debug:
                            print(f"✅ Agregado FailedConnection: {user} en {server}, Intentos: {count}")

            elif csv_type == "failed_ips":
                for row in rows:
                    ip_address = row.get("Direccion IP", "").strip()
                    country = row.get("Pais de la IP", "").strip()
                    server = row.get("Servidor", "").strip()
                    count = row.get("Count", "0").strip()

                    if ip_address and server:
                        failed_ip = FailedIp(
                            ip_address=ip_address,
                            country=country,
                            server=server,
                            count=int(count) if count.isdigit() else 0,
                            id_history=history.id
                        )
                        db.session.add(failed_ip)
                        db.session.commit()
                        
                        if debug:
                            print(f"✅ Agregado FailedIp: {ip_address} - {server}")

            elif csv_type == "blocked_users":
                for row in rows:
                    user = row.get("Usuario Bloqueado", "").strip()
                    server = row.get("Nombre del Servidor", "").strip()
                    date = row.get("Hora del Bloqueo", "").strip()

                    if user and server:
                        blocked_user = BlockedUsers(
                            user=user,
                            server=server,
                            date=date,
                            id_history=history.id
                        )
                        db.session.add(blocked_user)
                        db.session.commit()
                        
                        if debug:
                            print(f"✅ Agregado BlockedUser: {user} - {server}")

            elif csv_type == "blocked_ips":
                for row in rows:
                    ip_address = row.get("Direccion IP", "").strip()
                    country = row.get("Pais de la IP", "").strip()
                    server = row.get("Nombre del Servidor", "").strip()
                    date = row.get("Hora del Bloqueo", "").strip()

                    if ip_address and server:
                        blocked_ip = BlockedIp(
                            ip_address=ip_address,
                            country=country,
                            server=server,
                            date=date,
                            id_history=history.id
                        )
                        db.session.add(blocked_ip)
                        db.session.commit()
                        
                        if debug:
                            print(f"✅ Agregado BlockedIp: {ip_address} - {server}")

            elif csv_type == "users_added":
                for row in rows:
                    user = row.get("Usuario", "").strip()
                    uid = row.get("UID", "").strip()
                    path = row.get("Directorio", "").strip()
                    shell = row.get("Shell", "").strip()
                    server = row.get("Servidor", "").strip()
                    date = row.get("Fecha y Hora", "").strip()

                    if user and server:
                        created_user = CreatedUser(
                            user=user,
                            uid=uid,
                            path=path,
                            shell=shell,
                            server=server,
                            date=date,
                            id_history=history.id
                        )
                        db.session.add(created_user)
                        db.session.commit()
                        
                        if debug:
                            print(f"✅ Agregado CreatedUser: {user} - {server}")

        db.session.commit()  # 🔹 Se asegura de guardar todo en la BD
        if debug:
            print(f"📦 Registros de {csv_type} guardados en la BD")

def validar_password_segura(password: str) -> str | None:
    """Valida si la contraseña cumple con los requisitos mínimos. Devuelve un mensaje si falla, None si es válida."""
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r"[A-Z]", password):
        return "La contraseña debe contener al menos una letra mayúscula."
    if not re.search(r"[a-z]", password):
        return "La contraseña debe contener al menos una letra minúscula."
    if not re.search(r"\d", password):
        return "La contraseña debe contener al menos un número."
    if not re.search(r"[!@#$%^&*()_+=\[{\]};:<>|./?,-]", password):
        return "La contraseña debe contener al menos un carácter especial."
    return None

def delete_files(file_paths):
    """Elimina los archivos CSV después de procesarlos."""
    for file_path in file_paths.values():
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Archivo eliminado: {file_path}")
