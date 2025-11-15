from app.extensions import ma
from app.models import Usuario
from marshmallow import fields, validate

# --- 1. Schema Base para DUMP (Mostrar datos) ---
# Definimos EXPLICITAMENTE los campos que se van a exponer.
class UsuarioSchema(ma.Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    role = fields.Str()
    # Aseguramos el formato de fecha para la exportación
    created_at = fields.DateTime(format='%Y-%m-%d %H:%M:%S', dump_only=True)
    
# Instancia para serializar un solo usuario
usuario_schema = UsuarioSchema()
usuarios_schema = UsuarioSchema(many=True)


# --- 2. Schema para REGISTRO (LOAD) ---
class RegisterSchema(ma.Schema):
    username = fields.Str(required=True, validate=validate.Length(min=3, max=64))
    email = fields.Email(required=True, validate=validate.Length(max=120))
    # load_only=True: Este campo es solo para entrada (registro), NUNCA se exporta.
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=8))
    role = fields.Str(required=False, 
                      validate=validate.OneOf(["user", "admin", "moderator"]),
                      load_default="user")

# --- 3. Schema para LOGIN (LOAD) ---
class LoginSchema(ma.Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)