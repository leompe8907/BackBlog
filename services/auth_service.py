from utils.security import SecurityUtils
from models.user import Usuario
from flask import jsonify
from app import db

class AuthService:
    @staticmethod
    def register_user(email, password, nombre):
        if Usuario.query.filter_by(email=email).first():
            return None, 'Correo existente'

        # Validación del formato del correo
        if not isinstance(email, str) or '@' not in email:
            return None, 'Correo inválido'

        user = Usuario(
            email=email,
            nombre=nombre,
            password=SecurityUtils.generate_password_hash(password)
        )

        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return None, f'Error al registrar usuario: {str(e)}'

        return user, None

    @staticmethod
    def login_user(email, password):
        user = Usuario.query.filter_by(email=email).first()
        if not user or not SecurityUtils.check_password_hash(user.password, password):
            return None, 'Email o contraseña incorrecta'

        token = SecurityUtils.generate_token(user.id)
        return {'user': user, 'token': token}, None
