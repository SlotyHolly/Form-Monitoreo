from flask import (
    Flask, render_template, request, redirect, url_for, session, send_file
)
import pandas as pd
import io
import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta_para_las_sesiones"  # Cambia esto en producción

# Simulación de usuarios registrados (ejemplo)
USUARIOS_VALIDOS = {
    "admin": "admin123",
    "operador": "op123"
}

# Almacén en memoria para DataFrames (cada categoría)
data_frames = {
    "usuarios_fallidos": None,
    "ips_fallidas": None,
    "bloqueos_usuarios": None,
    "bloqueos_ips": None,
    "usuarios_creados": None
}

# -----------------------------------------------------------------------------
# RUTA DE LOGIN
# -----------------------------------------------------------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        password = request.form.get("password")
        if usuario in USUARIOS_VALIDOS and USUARIOS_VALIDOS[usuario] == password:
            session["logged_in"] = True
            session["usuario_actual"] = usuario
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Credenciales inválidas")

    return render_template("login.html")


# -----------------------------------------------------------------------------
# PÁGINA PRINCIPAL (MENÚ)
# -----------------------------------------------------------------------------
@app.route("/index")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    return render_template("index.html", usuario=session["usuario_actual"])


# -----------------------------------------------------------------------------
# SUBIDA DE CSV (PARA CADA CATEGORÍA)
# -----------------------------------------------------------------------------
@app.route("/upload/<categoria>", methods=["GET", "POST"])
def upload_csv(categoria):
    """
    categorías esperadas:
      - 'usuarios_fallidos'
      - 'ips_fallidas'
      - 'bloqueos_usuarios'
      - 'bloqueos_ips'
      - 'usuarios_creados'
    """
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    if request.method == "POST":
        file = request.files.get("csv_file")
        if file:
            try:
                df = pd.read_csv(file)
                # Realizar validaciones según la categoría (ejemplo simple)
                
                # Ejemplo de validación mínima: que no esté vacío
                if df.empty:
                    return render_template(
                        "upload.html",
                        categoria=categoria,
                        error="El CSV está vacío o no contiene datos válidos."
                    )
                
                # Guardar en memoria
                data_frames[categoria] = df
                return render_template(
                    "upload.html",
                    categoria=categoria,
                    success="Archivo subido y procesado correctamente",
                    df_preview=df.head(10).to_html(classes="table table-striped")
                )
            except Exception as e:
                return render_template(
                    "upload.html",
                    categoria=categoria,
                    error=f"Error al procesar el CSV: {str(e)}"
                )
        else:
            return render_template(
                "upload.html",
                categoria=categoria,
                error="No se recibió ningún archivo"
            )
    
    return render_template("upload.html", categoria=categoria)


# -----------------------------------------------------------------------------
# VISTA DEL REPORTE (UNIFICA LOS DATOS DE TODAS LAS CATEGORÍAS)
# -----------------------------------------------------------------------------
@app.route("/reporte")
def reporte():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    # Fecha del reporte (día actual)
    fecha_reporte = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    responsable = session["usuario_actual"]

    # Preparamos un diccionario para enviar la vista previa
    tablas = {}
    for cat, df in data_frames.items():
        if df is not None:
            tablas[cat] = df.head(10).to_html(classes="table table-striped")
        else:
            tablas[cat] = "<p>No hay datos cargados</p>"
    
    return render_template(
        "report.html",
        fecha_reporte=fecha_reporte,
        responsable=responsable,
        tablas=tablas
    )


# -----------------------------------------------------------------------------
# EXPORTAR DATOS A JSON
# -----------------------------------------------------------------------------
@app.route("/export/json/<categoria>")
def export_json(categoria):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    df = data_frames.get(categoria)
    if df is None:
        return "No hay datos para esta categoría", 400
    
    # Convertir DataFrame a JSON
    json_data = df.to_json(orient="records", force_ascii=False)
    
    # Retornar como archivo descargable
    return (
        json_data,
        200,
        {
            "Content-Type": "application/json",
            "Content-Disposition": f'attachment; filename="{categoria}.json"'
        }
    )


# -----------------------------------------------------------------------------
# EXPORTAR DATOS A EXCEL
# -----------------------------------------------------------------------------
@app.route("/export/excel/<categoria>")
def export_excel(categoria):
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    
    df = data_frames.get(categoria)
    if df is None:
        return "No hay datos para esta categoría", 400
    
    # Crear un buffer en memoria para guardar el Excel
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


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    # Instalar dependencias con: pip install flask pandas openpyxl
    app.run(debug=True)
