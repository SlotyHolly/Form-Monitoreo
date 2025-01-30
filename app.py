import io
import datetime
import pandas as pd
from flask import (
    Flask, render_template, request, redirect, url_for, session,
    send_file, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, logout_user,
    login_required, current_user
)
from passlib.hash import pbkdf2_sha256  # Para hashear contraseñas

# -----------------------------------------------------------------------------
# CONFIGURACIÓN INICIAL DE FLASK
# -----------------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "clave-secreta"  # Cambiar por algo más robusto en prod

# Configuración de la base de datos (usar SQLite como ejemplo)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///wazuh_reports.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Manejo de login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"  # Redirige a "login" si se intenta acceder sin iniciar sesión


# -----------------------------------------------------------------------------
# MODELOS DE BASE DE DATOS
# -----------------------------------------------------------------------------
class User(db.Model, UserMixin):
    """
    Modelo para usuarios del sistema.
    Campos principales:
        - username
        - password_hash (almacenamos la contraseña hasheada)
        - role (p. ej. 'admin' o 'operador')
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default="operador")

    def set_password(self, password):
        self.password_hash = pbkdf2_sha256.hash(password)

    def check_password(self, password):
        return pbkdf2_sha256.verify(password, self.password_hash)


# Ejemplos de tablas para almacenar los datos subidos de CSV.
# Podríamos simplificar o unificar, pero lo mantenemos separado para ilustrar.

class FailedConnection(db.Model):
    """
    Usuarios con Conexiones Fallidas
    Campos: Usuario, Servidor, Cantidad
    """
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100))
    servidor = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
    # Relacionado con el usuario que cargó el registro (opcional):
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)


class FailedIP(db.Model):
    """
    Conexiones Fallidas por Dirección IP
    Campos: Dirección IP, País, Servidor, Cantidad
    """
    id = db.Column(db.Integer, primary_key=True)
    direccion_ip = db.Column(db.String(100))
    pais = db.Column(db.String(50))
    servidor = db.Column(db.String(100))
    cantidad = db.Column(db.Integer)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)


class BlockedUser(db.Model):
    """
    Bloqueos de Active Response por Usuarios
    Campos: Usuario, Servidor, Hora del Bloqueo
    """
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100))
    servidor = db.Column(db.String(100))
    hora_bloqueo = db.Column(db.String(50))  # o DateTime
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)


class BlockedIP(db.Model):
    """
    Bloqueos de Active Response por Dirección IP
    Campos: Dirección IP, País, Servidor, Hora del Bloqueo
    """
    id = db.Column(db.Integer, primary_key=True)
    direccion_ip = db.Column(db.String(100))
    pais = db.Column(db.String(50))
    servidor = db.Column(db.String(100))
    hora_bloqueo = db.Column(db.String(50))
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)


class CreatedUser(db.Model):
    """
    Usuarios Creados en los Servidores
    Campos: Usuario, UID, Directorio, Shell, Servidor, Fecha y Hora
    """
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(100))
    uid = db.Column(db.String(20))
    directorio = db.Column(db.String(200))
    shell = db.Column(db.String(50))
    servidor = db.Column(db.String(100))
    fecha_hora = db.Column(db.String(50))  # o DateTime
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.datetime.now)


# -----------------------------------------------------------------------------
# FLASK-LOGIN: CARGAR USUARIO DESDE ID
# -----------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# -----------------------------------------------------------------------------
# RUTAS DE REGISTRO/LOGIN/LOGOUT
# -----------------------------------------------------------------------------

@app.before_first_request
def create_tables():
    """
    Crear las tablas en la BD si no existen. (Modo didáctico)
    En producción usaríamos migraciones con Alembic.
    """
    db.create_all()
    # Crear un usuario admin de ejemplo si no existe
    if not User.query.filter_by(username="admin").first():
        admin_user = User(username="admin", role="admin")
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        db.session.commit()


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        role = request.form.get("role", "operador")

        # Validar que no exista ya el usuario
        if User.query.filter_by(username=username).first():
            flash("El usuario ya existe.", "error")
            return render_template("register.html")

        new_user = User(username=username, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash("Usuario registrado exitosamente.", "success")
        return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Has iniciado sesión.", "success")
            return redirect(url_for("index"))
        else:
            flash("Credenciales inválidas.", "error")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesión.", "success")
    return redirect(url_for("login"))


# -----------------------------------------------------------------------------
# PÁGINA PRINCIPAL / MENÚ
# -----------------------------------------------------------------------------
@app.route("/index")
@login_required
def index():
    return render_template("index.html", usuario=current_user.username, role=current_user.role)


# -----------------------------------------------------------------------------
# SUBIDA DE CSV (almacena en BD)
# -----------------------------------------------------------------------------
def process_csv_failed_connection(df, user_id):
    """
    Procesa el DataFrame de Conexiones Fallidas (Usuarios),
    guardando cada fila como un registro en la tabla FailedConnection.
    """
    for idx, row in df.iterrows():
        fc = FailedConnection(
            usuario=row.get("Usuario"),
            servidor=row.get("Servidor"),
            cantidad=row.get("Cantidad", 0),
            created_by=user_id
        )
        db.session.add(fc)
    db.session.commit()


def process_csv_failed_ip(df, user_id):
    for idx, row in df.iterrows():
        fip = FailedIP(
            direccion_ip=row.get("Dirección IP"),
            pais=row.get("País"),
            servidor=row.get("Servidor"),
            cantidad=row.get("Cantidad", 0),
            created_by=user_id
        )
        db.session.add(fip)
    db.session.commit()


def process_csv_blocked_user(df, user_id):
    for idx, row in df.iterrows():
        bu = BlockedUser(
            usuario=row.get("Usuario"),
            servidor=row.get("Servidor"),
            hora_bloqueo=row.get("Hora del Bloqueo"),
            created_by=user_id
        )
        db.session.add(bu)
    db.session.commit()


def process_csv_blocked_ip(df, user_id):
    for idx, row in df.iterrows():
        bip = BlockedIP(
            direccion_ip=row.get("Dirección IP"),
            pais=row.get("País"),
            servidor=row.get("Servidor"),
            hora_bloqueo=row.get("Hora del Bloqueo"),
            created_by=user_id
        )
        db.session.add(bip)
    db.session.commit()


def process_csv_created_user(df, user_id):
    for idx, row in df.iterrows():
        cu = CreatedUser(
            usuario=row.get("Usuario"),
            uid=row.get("UID"),
            directorio=row.get("Directorio"),
            shell=row.get("Shell"),
            servidor=row.get("Servidor"),
            fecha_hora=row.get("Fecha y Hora"),
            created_by=user_id
        )
        db.session.add(cu)
    db.session.commit()


@app.route("/upload/<categoria>", methods=["GET", "POST"])
@login_required
def upload_csv(categoria):
    """
    categorías esperadas:
        - usuarios_fallidos
        - ips_fallidas
        - bloqueos_usuarios
        - bloqueos_ips
        - usuarios_creados
    """
    if request.method == "POST":
        file = request.files.get("csv_file")
        if not file:
            flash("No se recibió ningún archivo CSV.", "error")
            return render_template("upload.html", categoria=categoria)

        try:
            df = pd.read_csv(file)
            if df.empty:
                flash("El CSV está vacío o no contiene datos.", "error")
                return render_template("upload.html", categoria=categoria)

            # Procesar y guardar en la BD
            if categoria == "usuarios_fallidos":
                process_csv_failed_connection(df, current_user.id)
            elif categoria == "ips_fallidas":
                process_csv_failed_ip(df, current_user.id)
            elif categoria == "bloqueos_usuarios":
                process_csv_blocked_user(df, current_user.id)
            elif categoria == "bloqueos_ips":
                process_csv_blocked_ip(df, current_user.id)
            elif categoria == "usuarios_creados":
                process_csv_created_user(df, current_user.id)
            else:
                flash("Categoría desconocida.", "error")
                return render_template("upload.html", categoria=categoria)

            flash("Archivo subido y procesado correctamente.", "success")
            return render_template(
                "upload.html",
                categoria=categoria,
            )

        except Exception as e:
            flash(f"Error al procesar el CSV: {str(e)}", "error")
            return render_template("upload.html", categoria=categoria)

    return render_template("upload.html", categoria=categoria)


# -----------------------------------------------------------------------------
# VISTA DEL REPORTE
# -----------------------------------------------------------------------------
@app.route("/reporte")
@login_required
def reporte():
    """
    Muestra un resumen de los primeros 10 registros de cada categoría.
    - Si el usuario es 'admin', ve todos los registros.
    - Si es otro rol, ve únicamente los que creó.
    """
    fecha_reporte = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    responsable = current_user.username

    if current_user.role == "admin":
        fc_data = FailedConnection.query.all()
        fip_data = FailedIP.query.all()
        bu_data = BlockedUser.query.all()
        bip_data = BlockedIP.query.all()
        cu_data = CreatedUser.query.all()
    else:
        # Filtra solo los registros creados por el usuario actual
        fc_data = FailedConnection.query.filter_by(created_by=current_user.id).all()
        fip_data = FailedIP.query.filter_by(created_by=current_user.id).all()
        bu_data = BlockedUser.query.filter_by(created_by=current_user.id).all()
        bip_data = BlockedIP.query.filter_by(created_by=current_user.id).all()
        cu_data = CreatedUser.query.filter_by(created_by=current_user.id).all()

    # Convertimos a DataFrames para mostrar en tablas
    df_fc = pd.DataFrame([{
        "Usuario": x.usuario,
        "Servidor": x.servidor,
        "Cantidad": x.cantidad,
        "Fecha Carga": x.created_at
    } for x in fc_data])

    df_fip = pd.DataFrame([{
        "Dirección IP": x.direccion_ip,
        "País": x.pais,
        "Servidor": x.servidor,
        "Cantidad": x.cantidad,
        "Fecha Carga": x.created_at
    } for x in fip_data])

    df_bu = pd.DataFrame([{
        "Usuario": x.usuario,
        "Servidor": x.servidor,
        "Hora Bloqueo": x.hora_bloqueo,
        "Fecha Carga": x.created_at
    } for x in bu_data])

    df_bip = pd.DataFrame([{
        "Dirección IP": x.direccion_ip,
        "País": x.pais,
        "Servidor": x.servidor,
        "Hora Bloqueo": x.hora_bloqueo,
        "Fecha Carga": x.created_at
    } for x in bip_data])

    df_cu = pd.DataFrame([{
        "Usuario": x.usuario,
        "UID": x.uid,
        "Directorio": x.directorio,
        "Shell": x.shell,
        "Servidor": x.servidor,
        "Fecha y Hora": x.fecha_hora,
        "Fecha Carga": x.created_at
    } for x in cu_data])

    # Convertir a HTML con head(10) para muestra
    tablas = {
        "usuarios_fallidos": df_fc.head(10).to_html(classes="table table-striped", index=False) if not df_fc.empty else "<p>No hay datos</p>",
        "ips_fallidas": df_fip.head(10).to_html(classes="table table-striped", index=False) if not df_fip.empty else "<p>No hay datos</p>",
        "bloqueos_usuarios": df_bu.head(10).to_html(classes="table table-striped", index=False) if not df_bu.empty else "<p>No hay datos</p>",
        "bloqueos_ips": df_bip.head(10).to_html(classes="table table-striped", index=False) if not df_bip.empty else "<p>No hay datos</p>",
        "usuarios_creados": df_cu.head(10).to_html(classes="table table-striped", index=False) if not df_cu.empty else "<p>No hay datos</p>"
    }

    return render_template(
        "report.html",
        fecha_reporte=fecha_reporte,
        responsable=responsable,
        tablas=tablas
    )


# -----------------------------------------------------------------------------
# EXPORTAR DATOS A JSON O EXCEL
# -----------------------------------------------------------------------------
@app.route("/export/json/<categoria>")
@login_required
def export_json(categoria):
    # Dependiendo de la categoría, recuperamos los datos
    # Aplicando la misma lógica de admin vs. operador
    if current_user.role == "admin":
        query = _get_query_for_categoria(categoria).all()
    else:
        query = _get_query_for_categoria(categoria).filter_by(created_by=current_user.id).all()

    if not query:
        return "No hay datos para esta categoría", 400

    df = convert_query_to_df(query, categoria)
    json_data = df.to_json(orient="records", force_ascii=False)

    return (
        json_data,
        200,
        {
            "Content-Type": "application/json",
            "Content-Disposition": f'attachment; filename="{categoria}.json"'
        }
    )


@app.route("/export/excel/<categoria>")
@login_required
def export_excel(categoria):
    if current_user.role == "admin":
        query = _get_query_for_categoria(categoria).all()
    else:
        query = _get_query_for_categoria(categoria).filter_by(created_by=current_user.id).all()

    if not query:
        return "No hay datos para esta categoría", 400

    df = convert_query_to_df(query, categoria)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=categoria)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=f"{categoria}.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def _get_query_for_categoria(categoria):
    """
    Retorna la Query base para la categoría solicitada.
    """
    if categoria == "usuarios_fallidos":
        return FailedConnection.query
    elif categoria == "ips_fallidas":
        return FailedIP.query
    elif categoria == "bloqueos_usuarios":
        return BlockedUser.query
    elif categoria == "bloqueos_ips":
        return BlockedIP.query
    elif categoria == "usuarios_creados":
        return CreatedUser.query
    else:
        # Categoría desconocida
        return None


def convert_query_to_df(query, categoria):
    """
    Convierte una lista de objetos de la BD (según categoría) a DataFrame.
    """
    if categoria == "usuarios_fallidos":
        data = [{
            "Usuario": x.usuario,
            "Servidor": x.servidor,
            "Cantidad": x.cantidad,
            "Fecha Carga": x.created_at
        } for x in query]
    elif categoria == "ips_fallidas":
        data = [{
            "Dirección IP": x.direccion_ip,
            "País": x.pais,
            "Servidor": x.servidor,
            "Cantidad": x.cantidad,
            "Fecha Carga": x.created_at
        } for x in query]
    elif categoria == "bloqueos_usuarios":
        data = [{
            "Usuario": x.usuario,
            "Servidor": x.servidor,
            "Hora del Bloqueo": x.hora_bloqueo,
            "Fecha Carga": x.created_at
        } for x in query]
    elif categoria == "bloqueos_ips":
        data = [{
            "Dirección IP": x.direccion_ip,
            "País": x.pais,
            "Servidor": x.servidor,
            "Hora del Bloqueo": x.hora_bloqueo,
            "Fecha Carga": x.created_at
        } for x in query]
    elif categoria == "usuarios_creados":
        data = [{
            "Usuario": x.usuario,
            "UID": x.uid,
            "Directorio": x.directorio,
            "Shell": x.shell,
            "Servidor": x.servidor,
            "Fecha y Hora": x.fecha_hora,
            "Fecha Carga": x.created_at
        } for x in query]
    else:
        data = []
    return pd.DataFrame(data)


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Ejecutar la app
    app.run(debug=True)
