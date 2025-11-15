from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm, RegisterForm, PostForm, ComentarioForm
from app.models import Usuario, Post, Comentario, Categoria
from app.extensions import db
from datetime import datetime
from functools import wraps

# --- Decorador de Roles para Rutas Web (Flask-Login) ---
ROLES_HIERARCHY = {'user': 0, 'moderator': 1, 'admin': 2}

def role_required(required_role):
    """Verifica si current_user tiene el rol igual o superior al requerido."""
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('main.login'))
            
            required_level = ROLES_HIERARCHY.get(required_role, 0)
            user_level = ROLES_HIERARCHY.get(current_user.role, -1)
            
            if user_level < required_level:
                flash(f'Acceso denegado. Se requiere el rol: {required_role.upper()}.', 'danger')
                return redirect(url_for('main.index'))
                
            return f(*args, **kwargs)
        return wrapper
    return decorator

bp = Blueprint('main', __name__)

@bp.app_context_processor
def inject_categorias():
    categorias = Categoria.query.all()
    return dict(categorias=categorias)

# ----------------------------
# RUTAS PRINCIPALES
# ----------------------------
@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.filter_by(is_published=True).order_by(Post.timestamp.desc()).paginate(page=page, per_page=5, error_out=False)
    return render_template('index.html', posts=posts)

# ----------------------------
# LOGIN, REGISTER, LOGOUT
# ----------------------------
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Usuario.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash(f'Inicio de sesión exitoso. Rol: {user.role.upper()}', 'success')
            return redirect(next_page or url_for('main.index'))
        else:
            flash('Correo o contraseña incorrectos', 'danger')
    return render_template('login.html', form=form)

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegisterForm()
    if form.validate_on_submit():
        user = Usuario(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Usuario registrado con éxito', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión', 'info')
    return redirect(url_for('main.index'))

# ----------------------------
# CREAR POST
@bp.route('/post/nuevo', methods=['GET', 'POST'])
@login_required
def crear_post():
    form = PostForm()
    form.categorias.choices = [(c.id, c.nombre) for c in Categoria.query.all()]
    if form.validate_on_submit():
        categoria = Categoria.query.get(form.categorias.data)
        post = Post(
            titulo=form.titulo.data,
            contenido=form.contenido.data,
            autor=current_user,
            is_published=True
        )
        if categoria:
            post.categorias.append(categoria)
        db.session.add(post)
        db.session.commit()
        flash('Post creado con éxito', 'success')
        return redirect(url_for('main.index'))
    return render_template('create_post.html', form=form, legend='Crear Nuevo Post')

# ----------------------------
# VER POST + COMENTARIOS
@bp.route('/post/<int:post_id>', methods=['GET', 'POST'])
def ver_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = ComentarioForm()
    
    if current_user.is_authenticated and current_user.role in ['admin', 'moderator']:
        comentarios = Comentario.query.filter_by(post_id=post_id).order_by(Comentario.created_at.asc()).all()
    else:
        comentarios = Comentario.query.filter_by(post_id=post_id, is_visible=True).order_by(Comentario.created_at.asc()).all()
    
    if form.validate_on_submit():
        if current_user.is_authenticated:
            comentario = Comentario(
                contenido=form.contenido.data, 
                autor=current_user,
                post=post,
                created_at=datetime.utcnow()
            )
            db.session.add(comentario)
            db.session.commit()
            flash('Comentario agregado', 'success')
            return redirect(url_for('main.ver_post', post_id=post.id))
        else:
            flash('Debes iniciar sesión para comentar', 'warning')
            return redirect(url_for('main.login', next=request.url))
            
    return render_template('post.html', post=post, form=form, comentarios=comentarios)

# ----------------------------
# EDITAR POST
@bp.route('/post/editar/<int:post_id>', methods=['GET', 'POST'])
@login_required
def editar_post(post_id):
    post = Post.query.get_or_404(post_id)
    
    # Control de propiedad y rol
    if post.autor != current_user and current_user.role not in ['admin', 'moderator']:
        flash('No tienes permiso para editar este post.', 'danger')
        return redirect(url_for('main.ver_post', post_id=post.id))
        
    form = PostForm()
    form.categorias.choices = [(c.id, c.nombre) for c in Categoria.query.all()]
    
    if form.validate_on_submit():
        post.titulo = form.titulo.data
        post.contenido = form.contenido.data
        post.categorias = []
        categoria = Categoria.query.get(form.categorias.data)
        if categoria:
            post.categorias.append(categoria)
        db.session.commit()
        flash('Tu post ha sido actualizado.', 'success')
        return redirect(url_for('main.ver_post', post_id=post.id))
    
    elif request.method == 'GET':
        form.titulo.data = post.titulo
        form.contenido.data = post.contenido
        if post.categorias:
            form.categorias.data = post.categorias[0].id
            
    return render_template('create_post.html', form=form, legend='Editar Post')

# ----------------------------
# ELIMINAR POST
@bp.route('/post/eliminar/<int:post_id>', methods=['POST'])
@login_required
@role_required('admin')  # Solo Admin
def eliminar_post(post_id):
    post = Post.query.get_or_404(post_id)
    db.session.delete(post)
    db.session.commit()
    flash(f'El post "{post.titulo}" ha sido eliminado permanentemente por un Admin.', 'success')
    return redirect(url_for('main.index'))

# ----------------------------
# ELIMINAR COMENTARIO
@bp.route('/comentario/eliminar/<int:comentario_id>', methods=['POST'])
@login_required
def eliminar_comentario(comentario_id):
    comentario = Comentario.query.get_or_404(comentario_id)
    
    if comentario.autor == current_user or current_user.role in ['moderator', 'admin']:
        db.session.delete(comentario)
        db.session.commit()
        flash('Comentario eliminado con éxito.', 'success')
    else:
        flash('No tienes permiso para eliminar este comentario.', 'danger')

    return redirect(url_for('main.ver_post', post_id=comentario.post_id))

# ----------------------------
# POSTS POR CATEGORÍA
@bp.route('/categoria/<nombre>')
def posts_por_categoria(nombre):
    page = request.args.get('page', 1, type=int)
    categoria = Categoria.query.filter_by(nombre=nombre).first_or_404()
    posts = Post.query.join(Post.categorias).filter(
        Categoria.id == categoria.id, Post.is_published == True
    ).order_by(Post.timestamp.desc()).paginate(page=page, per_page=5, error_out=False)
    
    return render_template('index.html', posts=posts, title=f'Posts en {nombre}')

# ----------------------------
# PANEL DE ADMINISTRACIÓN
@bp.route('/admin')
@login_required
@role_required('admin')
def admin_panel():
    usuarios = Usuario.query.all()
    return render_template('admin_panel.html', title='Panel Admin', usuarios=usuarios)

# ----------------------------
# PANEL DE MODERACIÓN
@bp.route('/moderator')
@login_required
@role_required('moderator')
def moderator_panel():
    comentarios = Comentario.query.order_by(Comentario.created_at.desc()).all()
    return render_template('moderator_panel.html', title='Panel de Moderación', comentarios=comentarios)
