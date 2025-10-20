import os
import tempfile
from flask import Flask
from gerador.routes import  routes_bP # import do Blueprint

def create_app():
    app = Flask(__name__)
    
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(__file__), 'static'),
        template_folder=os.path.join(os.path.dirname(__file__), 'templates')
    )
    # Configurações básicas
    app.secret_key = 'sua_chave_secreta_aqui'  # coloque uma segura
    app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp()
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
    app.config['DOWNLOAD_FOLDER'] = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'downloads'
    )
    os.makedirs(app.config['DOWNLOAD_FOLDER'], exist_ok=True)

    # Registrar Blueprints
    app.register_blueprint(routes_bP)

    return app
