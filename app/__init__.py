import os
from flask import Flask 

# 1. Importar las extensiones desde el nuevo módulo 'extensions.py'
from .extensions import db, ma, jwt, bcrypt, login_manager, migrate  # <-- Agregado migrate

# Importamos los modelos para que SQLAlchemy los conozca antes de db.create_all()
from . import models

# Función principal para crear la aplicación (Patrón Factory)
def create_app(test_config=None):
    # Crear y configurar la aplicación
    app = Flask(__name__, instance_relative_config=True) 

    # -----------------------------------------------------------
    # CONFIGURACIÓN
    # -----------------------------------------------------------
    
    # Configuración por defecto 
    app.config.from_mapping(
        SECRET_KEY='dev',  # ¡Cambia esto en producción!
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URL') or 'sqlite:///miniblog.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY='super-secreto', # ¡Cambia esto en producción!
        JWT_TOKEN_LOCATION=['headers'],
    )

    if test_config is None:
        # Cargar la configuración desde config.py al mismo nivel que app/
        from config import Config
        app.config.from_object(Config)

    # Asegurarse de que el directorio de instancia exista
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # -----------------------------------------------------------
    # INICIALIZAR EXTENSIONES
    # -----------------------------------------------------------
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)  # <-- Habilita Flask-Migrate

    # Crear las tablas de la base de datos si no existen
    with app.app_context():
        db.create_all()

    # -----------------------------------------------------------
    # REGISTRAR RUTAS Y BLUEPRINTS (Importaciones al final)
    # -----------------------------------------------------------
    
    # Rutas API (Auth)
    from .views.auth_views import RegisterAPI, LoginAPI, UserDetailAPI
    
    app.add_url_rule('/api/register', view_func=RegisterAPI.as_view('register_api'), methods=['POST'])
    app.add_url_rule('/api/login', view_func=LoginAPI.as_view('login_api'), methods=['POST'])
    app.add_url_rule('/api/user', view_func=UserDetailAPI.as_view('user_detail_api'), methods=['GET'])

    # Registra el Blueprint de la API 
    from .api_routes import api_bp
    app.register_blueprint(api_bp)

    # Ruta de ejemplo
    @app.route('/hello')
    def hello():
        return 'Hello, World!'
    @app.route('/')
    def home():
        return {
        "project": "MiniBlog API",
        "version": "1.0",
        "status": "OK",
        "endpoints": {
            "login": "/api/login",
            "register": "/api/register",
            "posts": "/api/posts",
            "categories": "/api/categories",
            "comments": "/api/comments",
            "users": "/api/users"
        }
    }

    

    return app

# La aplicación debe ser accesible globalmente para el comando 'flask run'
app = create_app()
