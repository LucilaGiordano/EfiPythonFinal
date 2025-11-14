from app.models import Comentario
from app import ma
from marshmallow import fields # Importamos 'fields'

class ComentarioSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Comentario
        # El campo 'updated_at' está ahora disponible para la serialización
        fields = (
            'id', 
            'contenido', 
            'created_at', 
            'updated_at', 
            # 🚨 CORRECCIÓN CLAVE: Incluir explícitamente las claves foráneas
            'post_id', 
            'usuario_id', 
            'is_visible', 
            'autor'
        )
        load_instance = True
    
    # Declarar las claves foráneas como campos Integer de Marshmallow
    post_id = fields.Int(required=False)
    usuario_id = fields.Int(required=False)
    
    # Usamos la cadena 'UsuarioSchema' para la anidación.
    autor = ma.Nested('UsuarioSchema', only=('id', 'username'))

comentario_schema = ComentarioSchema()
comentarios_schema = ComentarioSchema(many=True)