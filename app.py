import os
from flask import Flask
from gerador import create_app
from gerador.services.service_clean_old_files import limpar_arquivos_antigos

if __name__ == '__main__':
    app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
    static_folder=os.path.join(os.path.dirname(__file__), 'static')
    )

    app = create_app()  # ✅ apenas uma vez!
    limpar_arquivos_antigos()
    app.run(debug=True, host='0.0.0.0', port=5000)
