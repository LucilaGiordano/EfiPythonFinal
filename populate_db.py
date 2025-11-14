from app import create_app, db
from app.models import Usuario, Post, Comentario, Categoria
from datetime import datetime

app = create_app()

with app.app_context():
    # Limpiar base de datos (opcional, solo para pruebas)
    db.drop_all()
    db.create_all()

    # Crear categorías
    cat_tech = Categoria(nombre='Tecnología')
    cat_sports = Categoria(nombre='Deportes')
    cat_food = Categoria(nombre='Comida')
    db.session.add_all([cat_tech, cat_sports, cat_food])
    db.session.commit()

    # Crear usuarios
    user1 = Usuario(username='Lucila', email='lucila@example.com')
    user1.set_password('123456')
    user2 = Usuario(username='Matias', email='matias@example.com')
    user2.set_password('123456')
    db.session.add_all([user1, user2])
    db.session.commit()

    # Crear posts
    post1 = Post(
        titulo='Mi primer post',
        contenido='Este es el contenido de mi primer post sobre tecnología.',
        autor=user1,
        categorias=[cat_tech]
    )

    post2 = Post(
        titulo='Deporte y salud',
        contenido='Hablar sobre cómo los deportes mejoran nuestra salud.',
        autor=user2,
        categorias=[cat_sports]
    )

    post3 = Post(
        titulo='Receta rápida',
        contenido='Una receta de comida rápida y deliciosa para probar este fin de semana.',
        autor=user1,
        categorias=[cat_food]
    )

    db.session.add_all([post1, post2, post3])
    db.session.commit()

    # Crear comentarios
    comentario1 = Comentario(
        texto='¡Excelente post!',
        autor=user2,
        post=post1
    )

    comentario2 = Comentario(
        texto='Muy útil, gracias por compartir.',
        autor=user1,
        post=post2
    )

    db.session.add_all([comentario1, comentario2])
    db.session.commit()

    print("Base de datos poblada con éxito.")
