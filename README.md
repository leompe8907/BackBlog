# Blog en Flask

Este proyecto es una aplicación web de blog desarrollada con Flask, SQLAlchemy y MySQL. La aplicación permite a los usuarios registrarse, iniciar sesión, crear publicaciones, comentar en publicaciones, editar y eliminar sus propias publicaciones.

## Requisitos

- Python 3.x
- MySQL
- Virtualenv (opcional pero recomendado)

## Instalación

1. Clonar el repositorio:
    ```bash
    git clone https://github.com/leompe8907/BackBlog.git
    cd tu-repo
    ```

2. Crear y activar un entorno virtual (opcional pero recomendado):
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows usa `venv\Scripts\activate`
    ```

3. Instalar las dependencias:
    ```bash
    pip install -r requirements.txt
    ```

4. Configurar la base de datos MySQL:
    - Crear una base de datos llamada `blogdb`.
    - Actualizar la URI de la base de datos en el archivo `config.py` si es necesario.

    ```python
    class Config:
        SQLALCHEMY_DATABASE_URI = 'mysql://root:password@localhost/blogdb'
        SQLALCHEMY_TRACK_MODIFICATIONS = False
        SECRET_KEY = os.urandom(24)
    ```

5. Crear las tablas en la base de datos:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

## Ejecución

1. Ejecutar la aplicación:
    ```bash
    python app.py
    ```

2. Abrir el navegador web y acceder a `http://localhost:5000`.

## Endpoints

- `POST /register`: Registro de nuevos usuarios.
- `POST /login`: Inicio de sesión de usuarios.
- `GET /logout`: Cierre de sesión de usuarios.
- `GET /publicaciones`: Obtiene todas las publicaciones.
- `POST /publicaciones`: Crea una nueva publicación.
- `POST /comentar/<int:publicacion_id>`: Comenta en una publicación.
- `DELETE /eliminar/<int:id>`: Elimina una publicación.
- `PUT /editar/<int:id>`: Edita una publicación.
- `GET /publicaciones/<int:id>`: Obtiene una publicación específica.

Uso:
La página principal (/) muestra todas las publicaciones y sus respuestas, los usuarios pueden registrarse y loguearse a través de la barra superior. Los usuarios registrados pueden crear, editar y eliminar sus publicaciones, todos los usuarios pueden ver las publicaciones y comentarios, pero solo los usuarios registrados pueden comentar o responder.

Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un issue o un pull request para discutir cualquier cambio que te gustaría hacer.

