from datetime import datetime
from app import db

class Publicacion(db.Model):
    __tablename__ = "publicaciones_comentarios"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    autor_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    autor = db.relationship('Usuario', backref='publicaciones_comentarios')
    tipo = db.Column(db.String(50), nullable=False)  # 'publicacion' o 'comentario'
    contenido = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)
    publicacion_id = db.Column(db.Integer, db.ForeignKey('publicaciones_comentarios.id'), nullable=True)
    comentarios = db.relationship('Publicacion', backref=db.backref('publicacion', remote_side=[id]), cascade="all, delete-orphan")