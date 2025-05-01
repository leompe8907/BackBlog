from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_cors import CORS
from config import config
import os
from dotenv import load_dotenv

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)

    load_dotenv()  # Cargar variables de entorno

    # Cargar configuraciones desde el archivo de entorno o configuración estándar
    app.config.from_object(config[os.getenv('FLASK_ENV', 'default')])

    # Configuración de la clave secreta desde una variable de entorno
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

    # Extensiones
    db.init_app(app)  # Esto es correcto, asegurándote de que 'db' esté registrado con la app
    login_manager.init_app(app)
    CORS(app, supports_credentials=True)

    # Blueprints
    from routes.auth import auth_bp
    from routes.post import posts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(posts_bp)

    # User loader
    from models.user import Usuario
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    return app


if __name__ == '__main__':
    app = create_app()
    try:
        with app.app_context():
            db.create_all()  # Crear las tablas si no existen
    except Exception as e:
        print(f"Error al crear la base de datos: {e}")
    app.run()