import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from models.user import Usuario
from dotenv import load_dotenv
import os

class SecurityUtils:
    
    load_dotenv()

    @staticmethod
    def generate_password_hash(password):
        """Genera un hash seguro de la contraseña"""
        return generate_password_hash(password)

    @staticmethod
    def check_password_hash(pw_hash, password):
        """Verifica si la contraseña coincide con el hash"""
        return check_password_hash(pw_hash, password)

    @staticmethod
    def generate_token(user_id):
        """Genera un JWT token para el usuario"""
        try:
            payload = {
                'exp': datetime.now() + timedelta(hours=current_app.config['JWT_ACCESS_TOKEN_EXPIRES']),
                'iat': datetime.now(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                os.getenv('SECRET_KEY'),  # Usamos una variable de entorno para la clave secreta
                algorithm='HS256'
            )
        except Exception as e:
            return SecurityUtils.handle_error(str(e))

    @staticmethod
    def verify_token(token):
        """Verifica y decodifica un JWT token"""
        try:
            payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
            return payload['sub']  # Retorna el user_id
        except jwt.ExpiredSignatureError:
            return SecurityUtils.handle_error('Token expirado. Por favor inicie sesión nuevamente.')
        except jwt.InvalidTokenError:
            return SecurityUtils.handle_error('Token inválido. Por favor inicie sesión nuevamente.')

    @staticmethod
    def handle_error(message):
        """Función para manejar los errores y generar respuestas consistentes"""
        return jsonify({'message': message}), 401

    @staticmethod
    def token_required(f):
        """Decorator para verificar el token en los endpoints protegidos"""

        @wraps(f)
        def decorated(*args, **kwargs):
            token = None

            # Verificar si el token está en los headers
            if 'Authorization' in request.headers:
                token = request.headers['Authorization'].split(" ")[1]

            if not token:
                return SecurityUtils.handle_error('Token no proporcionado')

            try:
                # Verificar el token
                data = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=['HS256'])
                current_user = Usuario.query.get(data['sub'])

                if not current_user:
                    return SecurityUtils.handle_error('Usuario no encontrado')

            except Exception as e:
                return SecurityUtils.handle_error(f'Token inválido: {str(e)}')

            return f(current_user, *args, **kwargs)

        return decorated

    @staticmethod
    def role_required(role):
        """Decorator para verificar si el usuario tiene un rol específico"""

        @wraps(role)
        def decorated(f, current_user, *args, **kwargs):
            # Verificar si el rol está presente en el usuario
            if not hasattr(current_user, role) or not getattr(current_user, role):
                return jsonify({'message': f'Se requieren privilegios de {role}'}), 403
            return f(current_user, *args, **kwargs)

        return decorated

    @staticmethod
    def admin_required(f):
        """Decorator para verificar si el usuario es admin"""

        return SecurityUtils.role_required('is_admin')(f)
