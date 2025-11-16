# EFI Segunda Etapa - Miniblog API REST

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/LucilaGiordano/EfiPythonFinal.git
cd EfiPythonFinal


Crear y activar entorno virtual:
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows


Instalar dependencias:
pip install -r requirements.txt


Configurar variables de entorno:
export FLASK_APP=run.py
export FLASK_ENV=development
export JWT_SECRET_KEY="tu_clave_secreta"


Inicializar base de datos:
flask db upgrade


Ejecución
flask run

Luego abrir: http://127.0.0.1:5000

| Rol       | Email                                   | Password |
| --------- | --------------------------------------- | -------- |
| Admin     | [L@gmail.com]                           | 12345678 |
| Moderator | [eliana@gmail.com]                      | 12345678 |
| Usuario   | [T@gmail.com]                           | 12345678 |


                      Endpoints principales (informal)
Autenticación

POST /api/register → Crear usuario

POST /api/login → Login y obtener JWT

Posts

GET /api/posts

GET /api/posts/<id>

POST /api/posts (autenticado)

PUT /api/posts/<id> (autor o admin)

DELETE /api/posts/<id> (autor o admin)

Comentarios

GET /api/posts/<id>/comments

POST /api/posts/<id>/comments

DELETE /api/comments/<id> (autor, moderator o admin)

Categorías

GET /api/categories

POST /api/categories (moderator/admin)

PUT /api/categories/<id> (moderator/admin)

DELETE /api/categories/<id> (admin)

Usuarios (admin)

GET /api/users

GET /api/users/<id>

PATCH /api/users/<id>/role

DELETE /api/users/<id>

Estadísticas

GET /api/stats (moderator/admin)


## Inicializar Base de Datos

1. Abrir el archivo `db/init_db.sql`.
2. Ejecutarlo en tu motor de base de datos (SQLite/MySQL/PostgreSQL) preferido:
   ```bash
   sqlite3 app.db < db/init_db.sql








