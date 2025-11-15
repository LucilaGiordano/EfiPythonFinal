from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from datetime import datetime

from app import db
from app.models import Comentario, Post, Usuario
from app.schemas.comment_schemas import comentarios_schema, comentario_schema
from app.decorators.auth_decorators import roles_required, check_ownership

class CommentListAPI(Resource):
    def get(self, post_id):
        """Retorna la lista de comentarios para un Post específico."""
        try:
            Post.query.get_or_404(post_id)
            comentarios = Comentario.query.filter_by(post_id=post_id, is_visible=True).all()
            result = comentarios_schema.dump(comentarios)
            return {'status': 'success', 'data': result}, 200
        except Exception as e:
            print(f"Error al obtener comentarios: {e}")
            return {'message': f'Error al obtener comentarios: {e}'}, 500

    @jwt_required()
    def post(self, post_id):
        """Crea un nuevo comentario para un Post específico."""
        try:
            current_user_id = int(get_jwt_identity())
            Post.query.get_or_404(post_id)

            json_data = request.get_json()
            if not json_data:
                return {'message': 'No input data provided'}, 400

            try:
                data = comentario_schema.load(json_data)
                data.usuario_id = current_user_id
                data.post_id = post_id
            except ValidationError as err:
                return {'message': 'Error de validación', 'errors': err.messages}, 400

            db.session.add(data)
            db.session.commit()
            result = comentario_schema.dump(data)
            return {'status': 'success', 'data': result}, 201

        except Exception as e:
            db.session.rollback()
            print(f"Error al crear comentario: {e}")
            return {'message': f'Error al crear comentario: {e}'}, 500

class CommentDetailAPI(Resource):
    def get(self, comment_id):
        comment = Comentario.query.get_or_404(comment_id)
        if not comment or not comment.is_visible:
            return {"message": "Comentario no encontrado"}, 404
        result = comentario_schema.dump(comment)
        return {'status': 'success', 'data': result}, 200

    @jwt_required()
    def put(self, comment_id):
        """Actualiza un comentario existente."""
        try:
            comentario = Comentario.query.get_or_404(comment_id)
            current_user_id = int(get_jwt_identity())
            current_user = Usuario.query.get(current_user_id)

            # Permiso: propietario o admin/moderator
            if comentario.usuario_id != current_user_id and current_user.role not in ['admin', 'moderator']:
                return {'message': 'Permiso denegado: No tienes autorización para editar este recurso.'}, 403

            json_data = request.get_json()
            if not json_data:
                return {'message': 'No input data provided'}, 400

            data = comentario_schema.load(json_data, instance=comentario, partial=True)
            db.session.add(data)
            db.session.commit()
            result = comentario_schema.dump(data)
            return {'status': 'success', 'data': result}, 200

        except Exception as e:
            db.session.rollback()
            print(f"Error al actualizar comentario: {e}")
            return {'message': f'Error al actualizar comentario: {e}'}, 500

    @jwt_required()
    def delete(self, comment_id):
        """Elimina (oculta) un comentario."""
        try:
            comentario = Comentario.query.get_or_404(comment_id)
            current_user_id = int(get_jwt_identity())
            current_user = Usuario.query.get(current_user_id)

            # Permiso: propietario o admin/moderator
            if comentario.usuario_id != current_user_id and current_user.role not in ['admin', 'moderator']:
                return {'message': 'Permiso denegado: No tienes autorización para eliminar este recurso.'}, 403

            comentario.is_visible = False
            db.session.add(comentario)
            db.session.commit()
            return {'status': 'success', 'message': 'Comentario ocultado (eliminado lógicamente)'}, 204

        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar comentario: {e}")
            return {'message': f'Error al eliminar comentario: {e}'}, 500
