from flask import Blueprint, request, jsonify
from services.auth_service import AuthService

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    
    # Validación de entrada
    email = data.get('email')
    password = data.get('password')
    nombre = data.get('nombre')
    
    if not email or not password or not nombre:
        return jsonify({'error': 'Faltan datos necesarios (email, password, nombre)'}), 400
    
    # Intentar registrar al usuario
    user, error = AuthService.register_user(email=email, password=password, nombre=nombre)
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'success': 'Registro exitoso'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    
    # Validación de entrada
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Faltan datos necesarios (email, password)'}), 400

    # Intentar autenticar al usuario
    user, error = AuthService.login_user(email=email, password=password)
    if error:
        return jsonify({'error': 'Credenciales incorrectas'}), 400
    
    # Generar token
    token = AuthService.generate_token(user)
    
    return jsonify({'token': token}), 200
