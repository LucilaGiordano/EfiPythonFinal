import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from datetime import timedelta
from flask_marshmallow import Marshmallow 
from flask_login import LoginManager 

# Inicializaciones fuera de la función de fábrica (factory function)
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow() 
login_manager = LoginManager()
login_manager.login_view = 'login_api' 
login_manager.login_message_category = 'info'


def create_app(config_class=None):
    app = Flask(__name__)

    # Configuración
    if config_class:
        app.config.from_object(config_class)
    else:
        try:
            from ..config import Config 
        except ImportError:
            class Config:
                SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-flask'
                SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///miniblog.db'
                SQLALCHEMY_TRACK_MODIFICATIONS = False
                JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secreto-jwt-api'
                JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
            
        app.config.from_object(Config)

    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app) 
    login_manager.init_app(app) 

    # --- FIX CLAVE PARA EL ERROR 'Subject must be a string' (422) ---
    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        # Asegura que el ID de usuario siempre sea un string para el token.
        return str(user_id) 

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        # Importación de modelos DENTRO de la función para el JWT callback
        from .models import Usuario 
        identity = jwt_data["sub"]
        try:
            # Convierte el string de vuelta a int para la consulta
            return Usuario.query.filter_by(id=int(identity)).one_or_none()
        except ValueError:
            return None
    # -----------------------------------------------------------------------

    # Registro de Vistas (Blueprints)
    
    # Rutas API (Auth) - Mantenidas con registro manual
    from .views.auth_views import RegisterAPI, LoginAPI, UserDetailAPI
    app.add_url_rule('/api/register', view_func=RegisterAPI.as_view('register_api'), methods=['POST'])
    app.add_url_rule('/api/login', view_func=LoginAPI.as_view('login_api'), methods=['POST'])
    app.add_url_rule('/api/user', view_func=UserDetailAPI.as_view('user_detail_api'), methods=['GET'])

    # Rutas API (Category) - Mantenidas con registro manual
    from .views.category_views import CategoryListAPI, CategoryDetailAPI
    app.add_url_rule('/api/categories', view_func=CategoryListAPI.as_view('category_list_api'), methods=['GET', 'POST'])
    app.add_url_rule('/api/categories/<int:category_id>', view_func=CategoryDetailAPI.as_view('category_detail_api'), methods=['GET', 'PUT', 'DELETE'])
    
    # Rutas API (Post) - Mantenidas con registro manual
    from .views.post_views import PostListAPI, PostDetailAPI
    app.add_url_rule('/api/posts', view_func=PostListAPI.as_view('post_list_api'), methods=['GET', 'POST'])
    app.add_url_rule('/api/posts/<int:post_id>', view_func=PostDetailAPI.as_view('post_detail_api'), methods=['GET', 'PUT', 'DELETE'])
    
    # -----------------------------------------------------------------------------
    # Se eliminaron las dos líneas de registro manual de la CommentListAPI y CommentDetailAPI
    # para evitar duplicidad, ya que ahora se registran en api_routes.py con Flask-RESTful.
    # -----------------------------------------------------------------------------

    # Registra el Blueprint de la API, el cual contiene SOLO las rutas de Comentarios.
    from .api_routes import api_bp
    app.register_blueprint(api_bp)

    return app