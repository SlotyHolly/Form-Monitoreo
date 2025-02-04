from flask import Blueprint, jsonify, render_template, redirect, url_for, flash
from .models import User, HistoryReports, FailedConnection, FailedIp, CreatedUser, BlockedUsers, BlockedIp
from flask_login import login_required, current_user
from .forms import ReportForm
from . import db, create_app
import csv
from flask import request 
from werkzeug.utils import secure_filename
from .forms import UploadCSVForm
import os

# Crear un Blueprint para las rutas principales
main_bp = Blueprint('main', __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'app' ,'instance', 'uploads')  # 👈 Define la ruta completa
ALLOWED_EXTENSIONS = {"csv"}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    if not filename:
        print("⚠️ No hay nombre de archivo, ignorando validación.")
        return False
    extension = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
    print(f"🔍 Verificando formato de archivo: {filename} (Extensión detectada: {extension})")
    return extension in ALLOWED_EXTENSIONS


@main_bp.route('/')
def index():
    """Redirigir al login si el usuario no está autenticado"""
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))  # Si está autenticado, va al dashboard
        else:
            return redirect(url_for('main.create_report'))  # Si está autenticado, va a la creación de reportes
    return redirect("http://localhost:5173/")  # ✅ Ahora sí existe

@main_bp.route('/history_reports')
@login_required
def history_reports():
    """Muestra los reportes creados por el usuario (o todos si es admin)."""
    if current_user.role == 'admin':
        reports = HistoryReports.query.order_by(HistoryReports.created_at.desc()).all()
    else:
        reports = HistoryReports.query.filter_by(user_id=current_user.id).order_by(HistoryReports.created_at.desc()).all()

    return render_template('history_reports.html', reports=reports)

@main_bp.route('/report/<int:report_id>')
@login_required
def reporte(report_id):
    """Muestra la información detallada de un reporte."""
    report = HistoryReports.query.get_or_404(report_id)

    # Verificación de permisos: Un usuario normal solo puede ver sus reportes
    if current_user.role != 'admin' and report.user_id != current_user.id:
        flash("No tienes permiso para ver este reporte.", "danger")
        return redirect(url_for('main.history_reports'))

    return render_template('report.html', report=report)


@main_bp.route("/api/upload_report", methods=["POST"])
@login_required
def upload_report():
    """Maneja la subida de archivos CSV y los procesa en la base de datos."""
    print(f"🔍 Usuario actual: {current_user}")
    if "failed_users" not in request.files:
        return jsonify({"error": "Debes subir al menos un archivo."}), 400

    file_paths = {}
    for key in ["failed_users", "failed_ips", "blocked_users", "blocked_ips", "users_added"]:
        file = request.files.get(key)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            file_paths[key] = file_path

    # Crear un registro en HistoryReports
    history = HistoryReports(user_id=current_user.id)
    db.session.add(history)
    db.session.commit()

    # Procesar los archivos
    process_csvs(file_paths, history.id)

    return jsonify({"message": "Reportes subidos y procesados correctamente."}), 200


def process_csvs(file_paths, user_id, debug=False):
    """Procesa los 5 archivos CSV y guarda los datos en la base de datos."""
    print(f"📂 Abriendo archivo: {file_paths}")
    history = HistoryReports(user_id=user_id)
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
        delete_files(file_paths)  # 🔹 Elimina los archivos después de procesarlos
        if debug:
            print(f"📦 Registros de {csv_type} guardados en la BD")

"""" ----------------------------------------------
# Ejecutar el proceso de CSV con archivos de prueba
# ----------------------------------------------
"""

def delete_files(file_paths):
    """Elimina los archivos CSV después de procesarlos."""
    for file_path in file_paths.values():
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
            print(f"🗑️ Archivo eliminado: {file_path}")

if __name__ == "__main__":

    def get_csv_files(folder_path):
        """Devuelve un diccionario con las rutas de los archivos CSV esperados."""
        return {
            "failed_users": os.path.join(folder_path, "List_Users_Failed.csv"),
            "failed_ips": os.path.join(folder_path, "List_IP_Failed.csv"),
            "blocked_users": os.path.join(folder_path, "List_Users_Blocked.csv"),
            "blocked_ips": os.path.join(folder_path, "List_IPS_Blocked.csv"),
            "users_added": os.path.join(folder_path, "List_User_Sudo_Add.csv")
        }

    CSV_FOLDER_PATH = "E:\Form-Monitoreo\CSV"
    app = create_app()
    
    with app.app_context():
        print("\n🚀 **EJECUTANDO TEST DE PROCESO CSV** 🚀\n")

        # Simulación de archivos CSV en E:\Form-Monitoreo\CSV
        csv_files = get_csv_files(CSV_FOLDER_PATH)

        # Llamar a `process_csvs()` con los archivos de prueba
        process_csvs(csv_files, user_id=1, debug=True)

        print("\n✅ **PROCESO DE CSV TERMINADO** ✅")
