import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-flask'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flaskuser:1234@localhost/miniblog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- CONFIGURACIÓN PARA JWT ---
    # Clave secreta para firmar los tokens JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secreto-jwt-api'
    # Tiempo de expiración de los tokens de acceso (24 horas, según consigna)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24) 
    # Asegúrate de que timedelta esté importado arriba