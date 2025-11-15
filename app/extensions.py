from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate  # <-- IMPORTAR Migrate

# Inicializamos las extensiones sin vincularlas a la aplicación
db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
bcrypt = Bcrypt()
login_manager = LoginManager()  # <-- NUEVA DEFINICIÓN
migrate = Migrate()              # <-- NUEVA DEFINICIÓN

# Opcional: Configuración del gestor de inicio de sesión
login_manager.login_view = 'main.login'  # Define la vista de login si usas un Blueprint 'main'
login_manager.login_message_category = 'info'
