from flask.views import MethodView
from flask import request, jsonify
from app.extensions import db
from ..models import Post, Categoria
from ..schemas.post_schemas import PostSchema
from ..decorators.auth_decorators import check_ownership, roles_required, post_owner_required
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound
import functools

# Instanciamos los schemas
post_schema = PostSchema()
posts_schema = PostSchema(many=True)

class PostListAPI(MethodView):
    """
    Maneja GET (lista de posts) y POST (crear nuevo post).
    """

    def get(self):
        posts = Post.query.filter_by(is_published=True).order_by(Post.timestamp.desc()).all()
        return jsonify(posts_schema.dump(posts)), 200

    @jwt_required()
    def post(self):
        user_id_from_token = get_jwt_identity()
        data = request.json
        try:
            validated_data = post_schema.load(data)
        except Exception as e:
            return jsonify({"errors": str(e)}), 400
        
        try:
            user_id = int(user_id_from_token)
        except ValueError:
            return jsonify({"msg": "Error de token: ID de usuario inválido."}), 400

        new_post = Post(
            titulo=validated_data['titulo'],
            contenido=validated_data['contenido'],
            usuario_id=user_id
        )

        categoria_ids = validated_data.get('categoria_ids', [])
        if categoria_ids:
            categorias = Categoria.query.filter(Categoria.id.in_(categoria_ids)).all()
            if len(categorias) != len(set(categoria_ids)):
                return jsonify({"msg": "Una o más IDs de categoría son inválidas."}), 400
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
    Maneja GET, PUT, DELETE de un post específico.
    """

    def get(self, post_id):
        try:
            post = Post.query.filter_by(id=post_id, is_published=True).one()
            return jsonify(post_schema.dump(post)), 200
        except NoResultFound:
            return jsonify({"msg": "Post no encontrado o no publicado."}), 404

    @jwt_required()
    @post_owner_required()
    def put(self, post_id, post):
        data = request.json
        try:
            validated_data = post_schema.load(data, partial=True)
        except Exception as e:
            return jsonify({"errors": str(e)}), 400

        post.titulo = validated_data.get('titulo', post.titulo)
        post.contenido = validated_data.get('contenido', post.contenido)
        post.is_published = validated_data.get('is_published', post.is_published)

        if 'categoria_ids' in validated_data:
            categoria_ids = validated_data['categoria_ids']
            post.categorias.clear()
            if categoria_ids:
                categorias = Categoria.query.filter(Categoria.id.in_(categoria_ids)).all()
                if len(categorias) != len(set(categoria_ids)):
                    return jsonify({"msg": "IDs de categoría inválidas."}), 400
                post.categorias.extend(categorias)

        try:
            db.session.commit()
            return jsonify({"msg": "Post actualizado exitosamente.", "post": post_schema.dump(post)}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al actualizar el post.", "details": str(e)}), 500

    @jwt_required()
    @roles_required('admin')  # Solo admin puede eliminar posts
    def delete(self, post_id):
        try:
            post = Post.query.get_or_404(post_id)
            db.session.delete(post)
            db.session.commit()
            return jsonify({"msg": f"Post ID {post_id} eliminado exitosamente."}), 204
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al eliminar el post.", "details": str(e)}), 500
