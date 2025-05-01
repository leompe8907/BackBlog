from flask import Blueprint, request, jsonify
from services.post_service import PostService
from services.auth_service import AuthService

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('/posts', methods=['GET'])
def get_posts():
    try:
        posts = PostService.get_all_posts()
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@posts_bp.route('/posts', methods=['POST'])
def create_post():
    token = request.headers.get('Authorization', '').split(' ')[-1]
    user = AuthService.verify_token(token)
    
    if not user:
        return jsonify({'error': 'No autorizado'}), 401

    # Validación de entrada
    contenido = request.json.get('contenido')
    if not contenido:
        return jsonify({'error': 'El contenido de la publicación no puede estar vacío'}), 400
    
    # Intentar crear la publicación
    post, error = PostService.create_post(user_id=user.id, contenido=contenido)
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify({'success': 'Publicación creada'}), 201
