from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, jwt_required

# --- Decorador de Verificación de Roles ---
def roles_required(*roles):
    """
    Verifica que el usuario tenga uno de los roles permitidos.
    Usar después de @jwt_required().
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):
            try:
                claims = get_jwt()
                user_role = claims.get('role')
            except Exception as e:
                return jsonify({"msg": "Error al obtener roles del token.", "details": str(e)}), 500
            
            if user_role not in roles:
                return jsonify(
                    msg="Acceso denegado. Rol insuficiente.", 
                    required_roles=roles,
                    user_role=user_role
                ), 403
            
            return fn(*args, **kwargs)
        return decorator
    return wrapper

# --- Función de Verificación de Propiedad ---
def check_ownership(resource_owner_id):
    """
    Verifica si el usuario actual es el dueño del recurso.
    Admin y moderator siempre tienen acceso.
    """
    try:
        current_user_id = get_jwt_identity()
        if current_user_id is None:
            return False
        current_user_id = int(current_user_id)
        
        claims = get_jwt()
        user_role = claims.get('role', '')

        # Admin o moderator siempre pueden
        if user_role in ['admin', 'moderator']:
            return True

        # Comparar con el owner_id
        if resource_owner_id is None:
            return False

        return current_user_id == int(resource_owner_id)
    except Exception as e:
        print(f"[check_ownership] Error: {e}")
        return False

# --- Decorador auxiliar para endpoints de post ---
def post_owner_required():
    """
    Verifica que el usuario sea el dueño del post o admin/moderator.
    Debe aplicarse después de @jwt_required().
    """
    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorated(*args, **kwargs):
            from ..models import Post  # Import local para evitar circularidad
            post_id = kwargs.get('post_id')
            if post_id is None:
                return jsonify({"msg": "Falta el ID del post."}), 400

            post = Post.query.get(post_id)
            if not post:
                return jsonify({"msg": "Post no encontrado."}), 404

            if not check_ownership(post.usuario_id):
                return jsonify({"msg": "Acceso denegado. No eres el autor ni admin/moderator."}), 403

            # Pasamos el post a la función para evitar consulta extra
            kwargs['post'] = post
            return fn(*args, **kwargs)
        return decorated
    return wrapper
