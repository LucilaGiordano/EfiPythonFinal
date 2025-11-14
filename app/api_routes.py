from flask import Blueprint
from flask_restful import Api
# Asegúrate de que esta importación sea correcta según tu estructura:
# Si las vistas están en `app/views/comment_views.py`, esta importación está bien.
from .views.comment_views import CommentListAPI, CommentDetailAPI 

# -----------------------------------------------------------
# CONFIGURACIÓN DEL BLUEPRINT PARA LA API
# El prefijo '/api' significa que todas las rutas empezarán con esa URL
# -----------------------------------------------------------
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Inicializar Flask-RESTful con el Blueprint
api = Api(api_bp)

# -----------------------------------------------------------
# REGISTRO DE RECURSOS RESTful (Tus Clases API)
# -----------------------------------------------------------

# Ruta para: GET (Listar todos) y POST (Crear uno nuevo)
# Endpoint completo: /api/posts/<post_id>/comments
api.add_resource(CommentListAPI, '/posts/<int:post_id>/comments')

# Ruta para: GET (Detalle), PUT (Editar) y DELETE (Eliminar)
# Endpoint completo: /api/comments/<comment_id>
api.add_resource(CommentDetailAPI, '/comments/<int:comment_id>')