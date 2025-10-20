import os
from flask import Flask
from gerador.services.service_clean_old_files import limpar_arquivos_antigos
from gerador import create_app


if __name__ == '__main__':
    # Criar diretório de templates se não existir
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
        static_folder=os.path.join(os.path.dirname(__file__), 'static')
    )
    
    app = create_app()

    # Limpar arquivos antigos ao iniciar
    limpar_arquivos_antigos()
    
    app.run(debug=True, host='0.0.0.0', port=5000)