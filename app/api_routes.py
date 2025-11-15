from flask import Blueprint, jsonify
from flask_restful import Api
from flask_jwt_extended import jwt_required

# Importaciones de vistas
from .views.auth_views import RegisterAPI, LoginAPI, UserDetailAPI, UserListAPI 
from .views.category_views import CategoryListAPI, CategoryDetailAPI 
from .views.post_views import PostListAPI, PostDetailAPI 
from .views.comment_views import CommentListAPI, CommentDetailAPI 

from app.models import Post, Comentario, Usuario
from app.decorators.auth_decorators import roles_required

# -----------------------------------------------------------
# CONFIGURACIÓN DEL BLUEPRINT PARA LA API
# -----------------------------------------------------------
api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

# -----------------------------------------------------------
# AUTENTICACIÓN Y USUARIOS
# -----------------------------------------------------------
api_bp.add_url_rule('/register', view_func=RegisterAPI.as_view('register_api'), methods=['POST']) 
api_bp.add_url_rule('/login', view_func=LoginAPI.as_view('login_api'), methods=['POST']) 
api_bp.add_url_rule('/users/me', view_func=UserDetailAPI.as_view('user_detail_api'), methods=['GET']) 
api_bp.add_url_rule('/users/', view_func=UserListAPI.as_view('user_list_api'), methods=['GET']) 

# -----------------------------------------------------------
# CATEGORÍAS
# -----------------------------------------------------------
api_bp.add_url_rule('/categories/', view_func=CategoryListAPI.as_view('category_list_api'), methods=['GET', 'POST']) 
api_bp.add_url_rule('/categories/<int:category_id>', view_func=CategoryDetailAPI.as_view('category_detail_api'), methods=['GET', 'PUT', 'DELETE']) 

# -----------------------------------------------------------
# POSTS
# -----------------------------------------------------------
api_bp.add_url_rule('/posts/', view_func=PostListAPI.as_view('post_list_api'), methods=['GET', 'POST']) 
api_bp.add_url_rule('/posts/<int:post_id>', view_func=PostDetailAPI.as_view('post_detail_api'), methods=['GET', 'PUT', 'DELETE']) 

# -----------------------------------------------------------
# COMENTARIOS
# -----------------------------------------------------------
api.add_resource(CommentListAPI, '/posts/<int:post_id>/comments')
api.add_resource(CommentDetailAPI, '/comments/<int:comment_id>')

# -----------------------------------------------------------
# ESTADÍSTICAS BÁSICAS (Moderador/Admin)
# -----------------------------------------------------------
@api_bp.route('/stats', methods=['GET'])
@jwt_required()
@roles_required('admin', 'moderator')
def stats():
    try:
        total_posts = Post.query.count()
        total_comments = Comentario.query.count()
        total_users = Usuario.query.count()
        return jsonify({
            "total_posts": total_posts,
            "total_comments": total_comments,
            "total_users": total_users
        }), 200
    except Exception as e:
        return jsonify({"error": "Error al obtener estadísticas", "details": str(e)}), 500
