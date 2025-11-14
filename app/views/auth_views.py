from flask.views import MethodView
from flask import request, jsonify
from app import db # Asume que 'db' es tu instancia de SQLAlchemy
from ..models import Usuario
from ..schemas.user_schemas import UsuarioSchema, RegisterSchema, LoginSchema
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
import datetime

# Instanciamos los schemas de DUMP (mostrar datos)
usuario_dump_schema = UsuarioSchema()
usuarios_dump_schema = UsuarioSchema(many=True)

# Instanciamos los schemas de LOAD (carga de datos)
register_load_schema = RegisterSchema()
login_load_schema = LoginSchema()


class RegisterAPI(MethodView):
    """
    Maneja el registro de nuevos usuarios.
    """
    def post(self):
        data = request.json
        
        # 1. Validar datos de entrada usando RegisterSchema
        try:
            validated_data = register_load_schema.load(data)
        except Exception as e:
            # Aquí se captura el error 400 por campos faltantes o inválidos
            return jsonify({"errors": str(e)}), 400

        # 2. Verificar existencia
        if Usuario.query.filter_by(username=validated_data['username']).first() or \
           Usuario.query.filter_by(email=validated_data['email']).first():
            return jsonify({"msg": "El nombre de usuario o email ya están registrados."}), 409

        # 3. Crear usuario
        new_user = Usuario(
            username=validated_data['username'],
            email=validated_data['email'],
            role=validated_data.get('role', 'user') # Usa el rol validado o 'user' por defecto
        )
        
        # Hashear y asignar contraseña
        new_user.set_password(validated_data['password'])

        db.session.add(new_user)
        try:
            db.session.commit()
            return jsonify({"msg": f"Usuario {new_user.username} registrado exitosamente. Por favor, inicie sesión."}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": "Error al registrar el usuario.", "details": str(e)}), 500


class LoginAPI(MethodView):
    """
    Maneja el inicio de sesión y la generación de JWT.
    """
    def post(self):
        data = request.json
        
        # 1. Validar datos de entrada usando LoginSchema
        try:
            validated_data = login_load_schema.load(data)
        except Exception as e:
            return jsonify({"errors": str(e)}), 400

        email = validated_data['email']
        password = validated_data['password']

        # 2. Buscar usuario
        try:
            user = Usuario.query.filter_by(email=email).one()
        except NoResultFound:
            return jsonify({"msg": "Credenciales inválidas (email no encontrado)."}), 401

        # 3. Verificar la contraseña
        if not user.check_password(password):
            return jsonify({"msg": "Credenciales inválidas (contraseña incorrecta)."}), 401

        # 4. Crear el Token de Acceso
        try:
            # ¡La identidad es el user.id (entero)!
            access_token = create_access_token(
                identity=user.id, 
                additional_claims={'role': user.role},
                expires_delta=datetime.timedelta(hours=24)
            )
        except Exception as e:
            return jsonify({"error": "Fallo al crear el token de acceso.", "details": str(e)}), 500

        # 5. Respuesta exitosa
        return jsonify({
            "access_token": access_token,
            "msg": "Inicio de sesión exitoso.",
            "user": usuario_dump_schema.dump(user) # Serializa el objeto Usuario
        }), 200


class UserDetailAPI(MethodView):
    """
    Maneja GET (detalle de usuario actual).
    """
    @jwt_required()
    def get(self):
        # Obtiene la identity (que es el ID de usuario) del token
        user_id = get_jwt_identity() 
        
        try:
            user = Usuario.query.filter_by(id=int(user_id)).one()
        except NoResultFound:
            return jsonify({"msg": "Usuario no encontrado, ID del token inválido."}), 404
        except ValueError:
            return jsonify({"msg": "Error interno del token: La identidad no es un ID válido."}), 422 
        
        return jsonify(usuario_dump_schema.dump(user)), 200