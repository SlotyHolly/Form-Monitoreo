from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FileField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional

class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=50)])  # 👈 Asegúrate de que sea `username`
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class CreateUserForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Rol', choices=[('user', 'Usuario'), ('admin', 'Administrador')], validators=[DataRequired()])
    submit = SubmitField('Crear Usuario')
    
class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('Nueva Contraseña', validators=[DataRequired(), Length(min=6)])
    submit = SubmitField('Cambiar Contraseña')

class DeleteUserForm(FlaskForm):
    submit = SubmitField('Eliminar Usuario')

class ReportForm(FlaskForm):
    # Campos generales del reporte
    user_id = IntegerField('ID de Usuario', validators=[DataRequired()])
    title = StringField('Título del Reporte', validators=[DataRequired(), Length(min=5, max=100)])
    
    # Datos de eventos de seguridad
    failed_user = StringField('Usuario con Fallos de Conexión')
    failed_server = StringField('Servidor con Fallos de Conexión')
    failed_count = IntegerField('Intentos Fallidos')
    
    failed_ip = StringField('IP Fallida')
    country = StringField('País de la IP')
    
    created_user = StringField('Usuario Creado')
    created_uid = StringField('UID del Usuario')
    created_path = StringField('Ruta del Usuario')
    created_shell = StringField('Shell')
    created_server = StringField('Servidor del Usuario')
    
    blocked_user = StringField('Usuario Bloqueado')
    blocked_ip = StringField('IP Bloqueada')

    submit = SubmitField('Guardar Reporte')

class UploadCSVForm(FlaskForm):
    failed_users_csv = FileField('Lista de Usuarios con Fallos de Conexión', validators=[Optional()])
    failed_ips_csv = FileField('Lista de IPs con Fallos de Conexión', validators=[Optional()])
    blocked_users_csv = FileField('Lista de Usuarios Bloqueados', validators=[Optional()])
    blocked_ips_csv = FileField('Lista de IPs Bloqueadas', validators=[Optional()])
    users_added_csv = FileField('Lista de Usuarios Agregados', validators=[Optional()])  # ✅ Ahora es opcional
    submit = SubmitField('Cargar Reportes')
