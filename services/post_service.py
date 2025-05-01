from models.post import Publicacion
from models.user import Usuario
from flask import jsonify
from app import db

class PostService:
    @staticmethod
    def get_all_posts():
        try:
            return Publicacion.query.filter_by(tipo='publicacion').order_by(Publicacion.date.desc()).all()
        except Exception as e:
            return jsonify({'error': f'Error al obtener las publicaciones: {str(e)}'}), 500

    @staticmethod
    def create_post(user_id, contenido):
        # Validación de contenido
        if not contenido or len(contenido) < 5:
            return None, 'El contenido de la publicación debe ser mayor a 5 caracteres'

        user = Usuario.query.get(user_id)
        if not user:
            return None, 'Usuario no encontrado'

        try:
            post = Publicacion(contenido=contenido, autor=user, tipo='publicacion')
            db.session.add(post)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return None, f'Error al crear la publicación: {str(e)}'

        return post, None

    @staticmethod
    def delete_post(post_id, user_id):
        post = Publicacion.query.get_or_404(post_id)
        if post.autor_id != user_id:
            return False, 'No tienes permiso para eliminar esta publicación'

        try:
            db.session.delete(post)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return False, f'Error al eliminar la publicación: {str(e)}'

        return True, None
