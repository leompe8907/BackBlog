import os
import jwt
from flask import Flask, Blueprint, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, current_user, login_required, UserMixin
from flask_cors import CORS, cross_origin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuración de la aplicación
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/blogdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

CORS(app, origins=["http://localhost:5000", "http://127.0.0.1:5500", "https://tifblog.vercel.app", "https://leonard27.pythonanywhere.com"],
     supports_credentials=True,
     methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization"])

main = Blueprint('main', __name__)

db = SQLAlchemy(app)
login = LoginManager(app)
login.login_view = 'main.login'

class Usuarios(UserMixin, db.Model):
    __tablename__ = "usuarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    nombre = db.Column(db.String(50), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

@login.user_loader
def load_user(user_id):
    return Usuarios.query.get(int(user_id))

class Publicaciones(db.Model):
    __tablename__ = "publicaciones_comentarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    autor = db.relationship('Usuarios', backref='publicaciones_comentarios')
    tipo = db.Column(db.String(50), nullable=False)  # 'publicacion' o 'comentario'
    contenido = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    publicacion_id = db.Column(db.Integer, db.ForeignKey('publicaciones_comentarios.id'), nullable=True)  # Solo para comentarios
    comentarios = db.relationship('Publicaciones', backref=db.backref('publicacion', remote_side=[id]), cascade="all, delete-orphan")

def generate_token(user):
    token = jwt.encode({
        'user_id': user.id,
        'exp': datetime.now() + timedelta(hours=1)  # Token expira en 1 hora
    }, app.config['SECRET_KEY'], algorithm='HS256')
    return token

def verify_token(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return Usuarios.query.get(data['user_id'])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

@main.route('/register', methods=['POST'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500","https://tifblog.vercel.app"], supports_credentials=True)
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    nombre = data.get('nombre')
    if Usuarios.query.filter_by(email=email).first():
        return jsonify({'error': 'Correo Existente'}), 400
    user = Usuarios(email=email, nombre=nombre)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'success': 'Felicidades, te has registrado'}), 201

@main.route('/login', methods=['POST'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500","https://tifblog.vercel.app"], supports_credentials=True)
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = Usuarios.query.filter_by(email=email).first()
    if user is None or not user.check_password(password):
        return jsonify({'error': 'Email o Contraseña incorrecta'}), 400
    token = generate_token(user)
    return jsonify({'success': 'Inicio de Sesión Exitosa','token': token}), 200

@main.route('/logout', methods=['GET'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500","https://tifblog.vercel.app"], supports_credentials=True)
def logout():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    else:
        return jsonify({'error': 'Token no proporcionado'}), 401

    user = verify_token(token)
    if not user:
        return jsonify({'error': 'Token inválido o expirado'}), 401

    logout_user()
    return jsonify({'success': 'Te has deslogueado exitosamente.'}), 200

@main.route('/publicaciones', methods=['GET'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500","https://tifblog.vercel.app"], supports_credentials=True)
def obtener_publicaciones():
    publicaciones = Publicaciones.query.filter_by(tipo='publicacion').order_by(Publicaciones.date.desc()).all()
    publicaciones_list = []
    for pub in publicaciones:
        comentarios = [{'id': com.id, 'contenido': com.contenido, 'autor': com.autor.nombre, 'date': com.date} for com in pub.comentarios]
        publicaciones_list.append({'id': pub.id, 'contenido': pub.contenido, 'autor': pub.autor.nombre, 'date': pub.date, 'comentarios': comentarios})
    return jsonify(publicaciones_list), 200

@main.route('/publicaciones', methods=['GET'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500", "https://tifblog.vercel.app"], supports_credentials=True)
def obtener_publicaciones():
    publicaciones = Publicaciones.query.filter_by(tipo='publicacion').order_by(Publicaciones.date.desc()).all()
    publicaciones_list = []
    for pub in publicaciones:
        comentarios = [{'id': com.id, 'contenido': com.contenido, 'autor': com.autor.nombre, 'date': com.date} for com in pub.comentarios]
        publicaciones_list.append({'id': pub.id, 'contenido': pub.contenido, 'autor': pub.autor.nombre, 'date': pub.date, 'comentarios': comentarios})
    return jsonify(publicaciones_list), 200

@main.route('/publicaciones', methods=['POST'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500", "https://tifblog.vercel.app"], supports_credentials=True)
def crear_publicacion():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    else:
        return jsonify({'error': 'Token no proporcionado'}), 401

    user = verify_token(token)
    if not user:
        return jsonify({'error': 'Token inválido o expirado'}), 401

    data = request.json
    contenido = data.get('contenido')
    publicacion = Publicaciones(contenido=contenido, autor=user, tipo='publicacion')
    db.session.add(publicacion)
    db.session.commit()
    return jsonify({'success': 'Tu publicación ha sido creada!'}), 201

@main.route('/comentar/<int:publicacion_id>', methods=['POST'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500","https://tifblog.vercel.app"], supports_credentials=True)
def comentar(publicacion_id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    else:
        return jsonify({'error': 'Token no proporcionado'}), 401

    user = verify_token(token)
    if not user:
        return jsonify({'error': 'Token inválido o expirado'}), 401

    data = request.json
    contenido = data.get('contenido')
    comentario = Publicaciones(contenido=contenido, autor=user, tipo='comentario', publicacion_id=publicacion_id)
    db.session.add(comentario)
    db.session.commit()
    return jsonify({"success": "Tu comentario ha sido publicado"}), 201

@main.route('/eliminar/<int:id>', methods=['DELETE'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500","https://tifblog.vercel.app"], supports_credentials=True)
def eliminar_publicacion(id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    else:
        return jsonify({'error': 'Token no proporcionado'}), 401

    user = verify_token(token)
    if not user:
        return jsonify({'error': 'Token inválido o expirado'}), 401

    publicacion = Publicaciones.query.get_or_404(id)
    if user.id != publicacion.autor_id:
        return jsonify({'error': 'No tienes permiso para eliminar esta publicación.'}), 403
    try:
        with db.session.no_autoflush:
            if publicacion.tipo == 'publicacion':
                for comentario in publicacion.comentarios:
                    db.session.delete(comentario)
            db.session.delete(publicacion)
            db.session.commit()
            return jsonify({'success': 'Tu publicación ha sido eliminada!'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error al eliminar la publicación: {}'.format(str(e))}), 500

@main.route('/editar/<int:id>', methods=['PUT'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500","https://tifblog.vercel.app"], supports_credentials=True)
def editar_publicacion(id):
    auth_header = request.headers.get('Authorization')
    if auth_header:
        try:
            token = auth_header.split(" ")[1]
        except IndexError:
            return jsonify({'error': 'Token inválido'}), 401
    else:
        return jsonify({'error': 'Token no proporcionado'}), 401

    user = verify_token(token)
    if not user:
        return jsonify({'error': 'Token inválido o expirado'}), 401

    publicacion = Publicaciones.query.get_or_404(id)
    if user.id != publicacion.autor_id:
        return jsonify({'error': 'No tienes permiso para editar esta publicación.'}), 403
    data = request.json
    contenido = data.get('contenido')
    publicacion.contenido = contenido
    db.session.commit()
    return jsonify({'success': 'Tu publicación ha sido actualizada!'}), 200

@main.route('/publicaciones/<int:id>', methods=['GET'])
@cross_origin(origins=["http://localhost:5000", "http://127.0.0.1:5500","https://tifblog.vercel.app"], supports_credentials=True)
def obtener_publicacion(id):
    publicacion = Publicaciones.query.get_or_404(id)
    return jsonify({'contenido': publicacion.contenido}), 200


if __name__ == '__main__':
    app.register_blueprint(main)
    with app.app_context():
        db.create_all()
    app.run()
