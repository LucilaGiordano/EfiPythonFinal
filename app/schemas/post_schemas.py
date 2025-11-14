from app import ma
from marshmallow import fields, validate

# Importamos el schema de Categoría 
from .category_schemas import CategoriaSchema 
# 🚨 CORRECCIÓN CLAVE: Se elimina la importación directa para romper el ciclo
# from .comment_schemas import ComentarioSchema

class PostSchema(ma.Schema):
    """Schema para serializar y validar los Posts, incluyendo Categorías y Comentarios."""
    id = fields.Int(dump_only=True)
    
    # Campos requeridos
    titulo = fields.Str(required=True, validate=validate.Length(min=5, max=120))
    contenido = fields.Str(required=True, validate=validate.Length(min=10))
    
    # Campo para recibir las CATEGORIAS (lista de IDs al cargar/validar)
    categoria_ids = fields.List(fields.Int(), load_only=True, required=False)

    # Campo para mostrar las CATEGORIAS (serializar)
    categorias = fields.List(fields.Nested(CategoriaSchema(only=('id', 'nombre'))), dump_only=True)
    
    # 🚨 CAMBIO CLAVE: Usamos la cadena 'ComentarioSchema'.
    comentarios = fields.List(fields.Nested('ComentarioSchema'), dump_only=True)
    
    # Campos de relaciones y metadata (solo lectura al enviar datos)
    autor_id = fields.Int(dump_only=True, attribute='usuario_id')
    created_at = fields.DateTime(dump_only=True, attribute='created_at')
    updated_at = fields.DateTime(dump_only=True, attribute='updated_at')
    is_published = fields.Bool()
    
    class Meta:
        load_instance = True

post_schema = PostSchema()
posts_schema = PostSchema(many=True)