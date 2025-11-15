import os
from datetime import timedelta

class Config:
    # 🚨 Ajuste de la clave secreta para que tome de ENV o use un valor por defecto
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-flask'
    
    # --- CONFIGURACIÓN PARA MySQL (usando pymysql) ---
    # Asegúrate de que el usuario 'flaskuser' y la DB 'miniblog' existan.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'mysql+pymysql://flaskuser:1234@localhost/miniblog'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # --- CONFIGURACIÓN PARA JWT ---
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'super-secreto-jwt-api'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)