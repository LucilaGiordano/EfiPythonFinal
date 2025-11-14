from app import ma
from ..models import Usuario
from marshmallow import fields, validate

# --- 1. Schema Base para DUMP (Mostrar datos) ---
class UsuarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Usuario
        # El campo 'created_at' ahora existe en el modelo y funcionará.
        load_instance = True
        fields = ('id', 'username', 'email', 'role', 'created_at')

# Instancia para serializar un solo usuario
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)

# --- 2. Schema para REGISTRO (LOAD) ---
# Incluye el campo 'password' para la entrada, que no es parte del modelo final.
class RegisterSchema(ma.Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    # 'role' es opcional y por defecto 'user' si no se provee.
    role = fields.Str(required=False, validate=validate.OneOf(['user', 'admin']))

# --- 3. Schema para LOGIN (LOAD) ---
class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True)