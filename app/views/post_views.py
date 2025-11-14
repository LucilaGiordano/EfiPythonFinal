from flask.views import MethodView
from flask import request, jsonify, g
from app import db # Asume que 'db' es tu instancia de SQLAlchemy
from ..models import Post, Usuario, Categoria
from ..schemas.post_schemas import PostSchema
from ..schemas.category_schemas import CategoriaSchema # Usado para serializar categorías
from ..decorators.auth_decorators import check_ownership # ✅ CORRECCIÓN RELATIVA
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

# Instanciamos los schemas
post_schema = PostSchema()
posts_schema = PostSchema(many=True)
category_schema = CategoriaSchema() # Lo necesitamos para obtener instancias

class PostListAPI(MethodView):
    """
    Maneja GET (lista de posts) y POST (crear nuevo post).
    """

    # Endpoint público: Obtener todos los posts
    def get(self):
        # Solo mostramos posts publicados
        posts = Post.query.filter_by(is_published=True).order_by(Post.timestamp.desc()).all()
        return jsonify(posts_schema.dump(posts)), 200

    # Endpoint privado: Crear un nuevo post
    @jwt_required()
    def post(self):
        # 🛑 CORRECCIÓN CLAVE: Convertir la identidad (string) a int antes de usarla como FK.
        user_id = int(get_jwt_identity())
        
        # 1. Validar los datos de entrada
        data = request.json
        try:
            validated_data = post_schema.load(data)
        except Exception as e:
            return jsonify({"errors": str(e)}), 400
        
        # 2. Crear el Post base
        new_post = Post(
            titulo=validated_data['titulo'],
            contenido=validated_data['contenido'],
            usuario_id=user_id, # Usamos el ID convertido a int
        )
        
        # 3. Manejar Categorías (Relación Muchos a Muchos)
        categoria_ids = validated_data.get('categoria_ids', [])
        
        if categoria_ids:
            # Buscamos las instancias de Categoría por los IDs
            categorias = Categoria.query.filter(Categoria.id.in_(categoria_ids)).all()
            
            if len(categorias) != len(set(categoria_ids)):
                return jsonify({"msg": "Una o más IDs de categoría son inválidas o inexistentes."}), 400
            
            # Asignamos las categorías al nuevo post
            new_post.categorias.extend(categorias)

        db.session.add(new_post)
        try:
            db.session.commit()
            return jsonify({
                "msg": "Post creado exitosamente.",
                "post": post_schema.dump(new_post)
            }), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al guardar el post.", "details": str(e)}), 500


class PostDetailAPI(MethodView):
    """
    Maneja GET (detalle), PUT (editar), DELETE (eliminar) de un post específico.
    """

    # Endpoint público: Obtener detalle de un post
    def get(self, post_id):
        try:
            # Solo mostramos si está publicado
            post = Post.query.filter_by(id=post_id, is_published=True).one()
            return jsonify(post_schema.dump(post)), 200
        except NoResultFound:
            return jsonify({"msg": "Post no encontrado o no publicado."}), 404
    
    # Endpoint privado: Editar un post
    @jwt_required()
    def put(self, post_id):
        post = Post.query.get_or_404(post_id)
        
        # Obtenemos el ID del usuario dueño del recurso.
        # En este caso, el dueño del recurso es el usuario_id del Post.
        if not check_ownership(post.usuario_id):
            return jsonify({"msg": "Acceso denegado. No eres el autor de este post ni administrador."}), 403

        # 1. Validar los datos de entrada (permitimos actualización parcial)
        data = request.json
        try:
            validated_data = post_schema.load(data, partial=True)
        except Exception as e:
            return jsonify({"errors": str(e)}), 400

        # 2. Actualizar campos
        post.titulo = validated_data.get('titulo', post.titulo)
        post.contenido = validated_data.get('contenido', post.contenido)
        post.is_published = validated_data.get('is_published', post.is_published)
        
        # 3. Manejar la actualización de Categorías
        if 'categoria_ids' in validated_data:
            categoria_ids = validated_data['categoria_ids']
            
            # Limpiamos las categorías existentes
            post.categorias.clear()
            
            if categoria_ids:
                # Buscamos las nuevas instancias de Categoría
                categorias = Categoria.query.filter(Categoria.id.in_(categoria_ids)).all()
                
                if len(categorias) != len(set(categoria_ids)):
                    return jsonify({"msg": "Una o más IDs de categoría son inválidas o inexistentes."}), 400
                
                # Asignamos las nuevas categorías
                post.categorias.extend(categorias)


        # 4. Guardar cambios en la DB
        try:
            db.session.commit()
            return jsonify({
                "msg": "Post actualizado exitosamente.",
                "post": post_schema.dump(post)
            }), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al actualizar el post.", "details": str(e)}), 500

    # Endpoint privado: Eliminar un post
    @jwt_required()
    def delete(self, post_id):
        post = Post.query.get_or_404(post_id)
        
        # Obtenemos el ID del usuario dueño del recurso.
        if not check_ownership(post.usuario_id):
            return jsonify({"msg": "Acceso denegado. No eres el autor de este post ni administrador."}), 403

        db.session.delete(post)
        try:
            db.session.commit()
            return jsonify({"msg": f"Post ID {post_id} eliminado exitosamente."}), 204
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al eliminar el post.", "details": str(e)}), 500