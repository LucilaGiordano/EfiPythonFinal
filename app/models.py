ROLE_USER = 'user'
ROLE_MODERATOR = 'moderator'
ROLE_ADMIN = 'admin'

from datetime import datetime
from . import db, login_manager 
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from itsdangerous import URLSafeTimedSerializer as Serializer
import os # Aseguramos la importación de os para get_reset_token

@login_manager.user_loader
def load_user(user_id):
    # Asegúrate de que el nombre del modelo aquí sea el correcto (Usuario)
    return Usuario.query.get(int(user_id))

# Tabla de relación muchos a muchos entre Post y Categoria
post_categoria = db.Table('post_categoria',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True),
    db.Column('categoria_id', db.Integer, db.ForeignKey('categoria.id'), primary_key=True)
)

class Usuario(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(64), default='user')
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    posts = db.relationship('Post', backref='autor', lazy='dynamic')
    comentarios = db.relationship('Comentario', backref='autor', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_token(self, expires_sec=1800):
        try:
            key = os.environ.get('SECRET_KEY') or 'default-secret-key-for-token'
            s = Serializer(key, expires_sec)
            return s.dumps({'user_id': self.id}).decode('utf-8')
        except Exception as e:
            print(f"Advertencia: Error al crear token: {e}")
            return None 

    @staticmethod
    def verify_reset_token(token):
        try:
            key = os.environ.get('SECRET_KEY') or 'default-secret-key-for-token'
            s = Serializer(key)
            user_id = s.loads(token)['user_id']
        except:
            return None
        return Usuario.query.get(user_id)

    def __repr__(self):
        return f'<Usuario {self.username}>'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(140), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    
    comentarios = db.relationship('Comentario', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    categorias = db.relationship('Categoria', secondary=post_categoria, backref=db.backref('posts', lazy='dynamic'))

    def __repr__(self):
        return f'<Post {self.titulo}>'

class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text, nullable=False) 
    created_at = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    # CAMBIO: Campo updated_at añadido para rastrear modificaciones
    updated_at = db.Column(db.DateTime, index=True, default=datetime.utcnow, onupdate=datetime.utcnow) 
    is_visible = db.Column(db.Boolean, default=True)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

    def __repr__(self):
        return f'<Comentario {self.contenido[:20]}>'

class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), index=True, unique=True, nullable=False)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'