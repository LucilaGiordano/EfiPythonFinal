from flask.views import MethodView
from flask import request, jsonify
from app.extensions import db, ma, bcrypt, jwt
from ..models import Usuario
from ..schemas.user_schemas import UsuarioSchema, RegisterSchema, LoginSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError 
import datetime

# 🚨 Decorador para verificar roles
from ..decorators.auth_decorators import roles_required 

# Schemas
usuario_dump_schema = UsuarioSchema()
usuarios_dump_schema = UsuarioSchema(many=True)
register_load_schema = RegisterSchema()
login_load_schema = LoginSchema()


class RegisterAPI(MethodView):
    def post(self):
        data = request.json
        
        try:
            validated_data = register_load_schema.load(data)
            
            # Verificar email único
            if Usuario.query.filter_by(email=validated_data['email']).first():
                return jsonify({"msg": "El email ya está registrado."}), 409

            role_to_assign = validated_data.get('role', 'user')

            new_user = Usuario(
                username=validated_data['username'],
                email=validated_data['email'],
                role=role_to_assign
            )
            new_user.set_password(validated_data['password'])

            db.session.add(new_user)

            try:
                db.session.commit()
                return jsonify({"msg": f"Usuario {new_user.username} registrado exitosamente."}), 201

            except IntegrityError as e:
                db.session.rollback()
                print("\n--- ERROR EN COMMIT ---")
                print(str(e.orig))
                return jsonify({"error": "Fallo al guardar en BD."}), 500
            
            except Exception as e:
                db.session.rollback()
                print("\n--- ERROR INESPERADO ---")
                print(str(e))
                return jsonify({"error": "Error inesperado."}), 500

        except Exception as e:
            error_message = str(e) if not hasattr(e, 'messages') else e.messages
            return jsonify({"error": "Error de validación.", "details": error_message}), 400



class LoginAPI(MethodView):
    def post(self):
        data = request.json
        
        try:
            validated_data = login_load_schema.load(data)
            email = validated_data['email']
            password = validated_data['password']

            usuario = Usuario.query.filter_by(email=email).one()
            
            if usuario.check_password(password):
                expires = datetime.timedelta(hours=24)

                # ✅ TOKEN CORREGIDO: ahora incluye el rol en el JWT
                access_token = create_access_token(
                    identity=str(usuario.id),
                    additional_claims={"role": usuario.role},
                    expires_delta=expires
                )

                user_info = usuario_dump_schema.dump(usuario)
                
                return jsonify({
                    "access_token": access_token,
                    "msg": "Inicio de sesión exitoso.",
                    "user": user_info
                }), 200
            
            else:
                return jsonify({"msg": "Contraseña incorrecta."}), 401

        except NoResultFound:
            return jsonify({"msg": "Usuario no encontrado."}), 404

        except Exception as e:
            error_message = str(e) if not hasattr(e, 'messages') else e.messages
            return jsonify({"error": "Error al iniciar sesión.", "details": error_message}), 400



class UserListAPI(MethodView):
    @jwt_required()
    @roles_required('admin')
    def get(self):
        usuarios = Usuario.query.all()
        return jsonify(usuarios_dump_schema.dump(usuarios)), 200



class UserDetailAPI(MethodView):

    @jwt_required()
    def get(self, user_id):
        current_user_id = get_jwt_identity()
        
        current_user = Usuario.query.get(current_user_id)

        if current_user_id != user_id and current_user.role not in ['admin', 'moderator']:
            return jsonify({"msg": "No tienes permiso para ver este perfil."}), 403

        usuario = Usuario.query.get_or_404(user_id)
        return jsonify(usuario_dump_schema.dump(usuario)), 200


    @jwt_required()
    def put(self, user_id):
        current_user_id = get_jwt_identity()
        current_user = Usuario.query.get(current_user_id)

        if current_user.id != user_id and current_user.role not in ['admin', 'moderator']:
            return jsonify({"msg": "No tienes permiso para editar este perfil."}), 403

        data = request.json

        try:
            usuario = Usuario.query.get_or_404(user_id)

            if 'role' in data and current_user.role != 'admin':
                del data['role']

            validated_data = usuario_dump_schema.load(data, partial=True)

            if 'username' in validated_data:
                usuario.username = validated_data['username']
            if 'email' in validated_data:
                usuario.email = validated_data['email']
            if 'role' in validated_data:
                usuario.role = validated_data['role']

            db.session.commit()
            return jsonify({"msg": "Usuario actualizado", "user": usuario_dump_schema.dump(usuario)}), 200

        except Exception as e:
            db.session.rollback()
            error_message = str(e) if not hasattr(e, 'messages') else e.messages
            return jsonify({"error": "Error al actualizar.", "details": error_message}), 400



    @jwt_required()
    @roles_required('admin')
    def delete(self, user_id):
        try:
            usuario = Usuario.query.get_or_404(user_id)
            db.session.delete(usuario)
            db.session.commit()
            return jsonify({"msg": "Usuario eliminado correctamente."}), 204
        except:
            db.session.rollback()
            return jsonify({"msg": "Error al eliminar usuario."}), 404



class ProtectedAPI(MethodView):
    @jwt_required()
    @roles_required(['admin', 'moderator'])
    def get(self):
        current_user_id = get_jwt_identity()
        user = Usuario.query.get(current_user_id)
        if user:
            return jsonify({
                "msg": f"Acceso concedido a {user.username} (Rol: {user.role}).",
                "user_id": current_user_id
            }), 200
        return jsonify({"msg": "Usuario no encontrado."}), 404
