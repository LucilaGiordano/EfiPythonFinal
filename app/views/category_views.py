from flask.views import MethodView
from flask import request, jsonify
from app import db 
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
    @roles_required('admin')
    def post(self):
        # 1. Validar los datos de entrada
        data = request.json
        if data is None:
             # Este es un buen punto de control si se sigue viendo el 422
             return jsonify({"msg": "Error al procesar el JSON: Cuerpo de solicitud vacío o Content-Type incorrecto."}), 400
        
        try:
            # load() también verifica campos requeridos como 'nombre'
            validated_data = category_schema.load(data)
        except Exception as e:
            return jsonify({"errors": str(e)}), 400
        
        # 2. Verificar si la categoría ya existe (IntegrityError lo maneja, pero es mejor dar un mensaje claro)
        if Categoria.query.filter_by(nombre=validated_data['nombre']).first():
             return jsonify({"msg": f"La categoría '{validated_data['nombre']}' ya existe."}), 409
        
        # 3. Crear la Categoría
        new_category = Categoria(
            nombre=validated_data['nombre']
        )

        db.session.add(new_category)
        try:
            db.session.commit()
            return jsonify({
                "msg": "Categoría creada exitosamente.",
                "category": category_schema.dump(new_category)
            }), 201
        except IntegrityError:
            db.session.rollback()
            return jsonify({"error": "Error de integridad: La categoría ya existe (posiblemente).", 
                            "details": "Verifique que el nombre sea único."}), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al guardar la categoría.", "details": str(e)}), 500


class CategoryDetailAPI(MethodView):
    """
    Maneja GET (detalle), PUT (editar), DELETE (eliminar) de una categoría específica.
    """

    # Endpoint público: Obtener detalle de una categoría
    def get(self, category_id):
        try:
            category = Categoria.query.filter_by(id=category_id).one()
            return jsonify(category_schema.dump(category)), 200
        except NoResultFound:
            return jsonify({"msg": "Categoría no encontrada."}), 404
    
    # Endpoint privado: Editar una categoría (Solo Admin)
    @jwt_required()
    @roles_required('admin')
    def put(self, category_id):
        category = Categoria.query.get_or_404(category_id)
        
        # 1. Validar los datos de entrada (permitimos actualización parcial)
        data = request.json
        try:
            # Usamos partial=True porque solo queremos actualizar el nombre
            validated_data = category_schema.load(data, partial=True)
        except Exception as e:
            return jsonify({"errors": str(e)}), 400

        # 2. Actualizar campo (solo nombre)
        if 'nombre' in validated_data:
            category.nombre = validated_data['nombre']

        # 3. Guardar cambios en la DB
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
    @roles_required('admin')
    def delete(self, category_id):
        category = Categoria.query.get_or_404(category_id)
        
        # Opcional: Podrías querer desvincular los posts antes de eliminar la categoría
        # Pero por ahora, la eliminación está directa.
        
        db.session.delete(category)
        try:
            db.session.commit()
            return jsonify({"msg": f"Categoría ID {category_id} eliminada exitosamente."}), 204
        except Exception as e:
            db.session.rollback()
            # Posiblemente Foreign Key error si está vinculada
            return jsonify({"error": "Error al eliminar la categoría.", "details": str(e)}), 500