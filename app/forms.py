from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from app.models import Usuario, Categoria

# ==================================================
# Formulario de Login
# ==================================================
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recuérdame')
    submit = SubmitField('Iniciar Sesión')

# ==================================================
# Formulario de Registro
# ==================================================
class RegisterForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=2, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    password2 = PasswordField(
        'Repetir Contraseña', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        user = Usuario.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Por favor usa un nombre de usuario diferente.')

    def validate_email(self, email):
        user = Usuario.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Por favor usa una dirección de email diferente.')

# ==================================================
# Formulario de Post
# ==================================================
class PostForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(min=1, max=140)])
    contenido = TextAreaField('Contenido', validators=[DataRequired()])
    categorias = SelectField('Categoría', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Publicar')

# ==================================================
# Formulario de Comentario
# ==================================================
class ComentarioForm(FlaskForm):
    # 🚨 CAMBIO CLAVE: Renombrado de 'texto' a 'contenido'
    contenido = TextAreaField('Comentario', validators=[DataRequired(), Length(min=5)])
    submit = SubmitField('Comentar')