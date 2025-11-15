from flask.views import MethodView
from flask import request, jsonify
from app.extensions import db, ma, bcrypt, jwt
from ..models import Categoria
from ..schemas.category_schemas import CategoriaSchema
from ..decorators.auth_decorators import roles_required 
from flask_jwt_extended import jwt_required
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError

# Instanciamos los schemas
category_schema = CategoriaSchema()
categories_schema = CategoriaSchema(many=True)

class CategoryListAPI(MethodView):
    """
    Maneja GET (lista de categorías) y POST (crear nueva categoría).
    """

    # Endpoint público: Obtener todas las categorías
    def get(self):
        categorias = Categoria.query.all()
        return jsonify(categories_schema.dump(categorias)), 200

    # Endpoint privado: Crear una nueva categoría (Solo Admin)
    @jwt_required()
    @roles_required('admin', 'moderator')
    def post(self):
        # 1. Validar los datos de entrada
        data = request.json
        if data is None:
            return jsonify({"msg": "Error al procesar el JSON: Cuerpo de solicitud vacío o Content-Type incorrecto."}), 400
        
        try:
            validated_data = category_schema.load(data)
        except Exception as e:
            return jsonify({"errors": str(e)}), 400
        
        if Categoria.query.filter_by(nombre=validated_data['nombre']).first():
            return jsonify({"msg": f"La categoría '{validated_data['nombre']}' ya existe."}), 409
        
        new_category = Categoria(nombre=validated_data['nombre'])
        db.session.add(new_category)
        try:
            db.session.commit()
            return jsonify({
                "msg": "Categoría creada exitosamente.",
                "category": category_schema.dump(new_category)
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Error de integridad: La categoría ya existe.", 
                            "details": "Verifique que el nombre sea único."}), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al guardar la categoría.", "details": str(e)}), 500


class CategoryDetailAPI(MethodView):
    """
    Maneja GET, PUT, DELETE de una categoría específica.
    """

    # Endpoint público: Obtener detalle de una categoría
    def get(self, category_id):
        try:
            category = Categoria.query.filter_by(id=category_id).one()
            return jsonify(category_schema.dump(category)), 200
        except NoResultFound:
            return jsonify({"msg": "Categoría no encontrada."}), 404
    
    # Endpoint privado: Editar una categoría (Admin o Moderator)
    @jwt_required()
    @roles_required('admin', 'moderator')  # ✅ Moderadores pueden editar
    def put(self, category_id):
        category = Categoria.query.get_or_404(category_id)
        
        # 1. Validar los datos de entrada (permitimos actualización parcial)
        data = request.json
        try:
            validated_data = category_schema.load(data, partial=True)
        except Exception as e:
            return jsonify({"errors": str(e)}), 400

        if 'nombre' in validated_data:
            category.nombre = validated_data['nombre']

        try:
            db.session.commit()
            return jsonify({
                "msg": "Categoría actualizada exitosamente.",
                "category": category_schema.dump(category)
            }), 200
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Error: El nombre de la categoría ya está en uso."}), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al actualizar la categoría.", "details": str(e)}), 500

    # Endpoint privado: Eliminar una categoría (Solo Admin)
    @jwt_required()
    @roles_required('admin')  # Eliminación solo para admins
    def delete(self, category_id):
        category = Categoria.query.get_or_404(category_id)
        
        # Eliminación directa
        db.session.delete(category)
        try:
            db.session.commit()
            return jsonify({"msg": f"Categoría ID {category_id} eliminada exitosamente."}), 204
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al eliminar la categoría.", "details": str(e)}), 500
