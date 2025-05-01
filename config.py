import os
from datetime import timedelta


class Config:
    # Configuración común a todos los entornos
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24)
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL') or 'mysql://root:@localhost:3306/blogdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # Configuración de CORS
    CORS_ORIGINS = [
        "http://localhost:5000",
        "http://127.0.0.1:5500",
        "https://tifblog.vercel.app",
    ]
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_METHODS = ["GET", "POST", "OPTIONS", "PUT", "DELETE"]
    CORS_ALLOW_HEADERS = ["Content-Type", "Authorization"]

    # Configuración de cookies de sesión
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    @staticmethod
    def init_app(app):
        """Método para inicializar configuraciones adicionales si es necesario"""
        pass

class DevelopmentConfig(Config):
    """Configuraciones específicas para el entorno de desarrollo"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL') or 'mysql://root:@localhost:3306/blogdb'
    SQLALCHEMY_ECHO = True  # Muestra las consultas SQL en la consola

class TestingConfig(Config):
    """Configuraciones específicas para el entorno de pruebas"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DATABASE_URL') or 'sqlite:///:memory:'  # Base de datos en memoria para pruebas
    WTF_CSRF_ENABLED = False  # Desactiva CSRF en pruebas

class ProductionConfig(Config):
    """Configuraciones específicas para el entorno de producción"""
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or 'mysql://root:@localhost:3306/blogdb'

    @classmethod
    def init_app(cls, app):
        """Método para inicializar configuraciones adicionales para producción"""
        Config.init_app(app)
        app.config['SESSION_COOKIE_SECURE'] = True
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SQLALCHEMY_POOL_SIZE'] = 10
        app.config['SQLALCHEMY_POOL_RECYCLE'] = 299
        app.config['LOGGING_LEVEL'] = 'ERROR'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}