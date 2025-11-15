from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt # <- 1. Importación: Se añade 'get_jwt'
from marshmallow import ValidationError
from datetime import datetime

# La importación 'db' confirmada para manejar la persistencia
from app import db # Importación ajustada para consistencia
from app.models import Comentario, Post # Importación ajustada para consistencia
from app.schemas.comment_schemas import comentarios_schema, comentario_schema

# 🚨 1. Importación: Se añaden los decoradores de seguridad
from app.decorators.auth_decorators import roles_required, check_ownership 

class CommentListAPI(Resource):
    def get(self, post_id):
        """Retorna la lista de comentarios para un Post específico."""
        try:
            post = Post.query.get_or_404(post_id)
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
            # 1. Obtener la identidad de forma robusta (compatible con ID simple o diccionario)
            identity = get_jwt_identity()
            current_user_id = identity.get('id') if isinstance(identity, dict) else identity
            
            Post.query.get_or_404(post_id)

            json_data = request.get_json()
            if not json_data:
                return {'message': 'No input data provided'}, 400

            try:
                # 1. Cargar y validar la data. 'data' es ahora la instancia de Comentario.
                data = comentario_schema.load(json_data)
                
                # 2. Asignar IDs
                data.usuario_id = current_user_id
                data.post_id = post_id
                
            except ValidationError as err:
                return {'message': 'Error de validación', 'errors': err.messages}, 400
            
            # 3. Guardar en DB (Método correcto con SQLAlchemy)
            db.session.add(data)
            db.session.commit()
            
            # 4. Respuesta
            result = comentario_schema.dump(data)
            return {'status': 'success', 'data': result}, 201

        except Exception as e:
            db.session.rollback() # Rollback si el commit falla
            print(f"Error al crear comentario: {e}")
            return {'message': f'Error al crear comentario: {e}'}, 500

class CommentDetailAPI(Resource):
    
    # Añadido método GET (opcional, pero buena práctica RESTful)
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

            # 🛑 2. CAMBIO CLAVE: Usamos check_ownership (incluye lógica de Admin/Moderador)
            if not check_ownership(comentario.usuario_id):
                return {'message': 'Permiso denegado: No tienes autorización para editar este recurso.'}, 403

            json_data = request.get_json()
            if not json_data:
                return {'message': 'No input data provided'}, 400

            # Carga de datos para actualizar la instancia existente
            data = comentario_schema.load(json_data, instance=comentario, partial=True)
            
            # Persistencia de la actualización (Método correcto con SQLAlchemy)
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
            
            # 🛑 3. CAMBIO CLAVE: Usamos check_ownership (incluye lógica de Admin/Moderador)
            if not check_ownership(comentario.usuario_id):
                return {'message': 'Permiso denegado: No tienes autorización para eliminar este recurso.'}, 403

            # Eliminación lógica
            comentario.is_visible = False
            
            # Persistencia del cambio de estado (Método correcto con SQLAlchemy)
            db.session.add(comentario)
            db.session.commit()
            
            return {'status': 'success', 'message': 'Comentario ocultado (eliminado lógicamente)'}, 204

        except Exception as e:
            db.session.rollback()
            print(f"Error al eliminar comentario: {e}")
            return {'message': f'Error al eliminar comentario: {e}'}, 500