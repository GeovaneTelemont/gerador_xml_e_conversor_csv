import os
import tempfile

# Configurações principais do Flask
class Config:
    SECRET_KEY = 'sua_chave_secreta_aqui'  # Altere para uma chave segura
    UPLOAD_FOLDER = tempfile.mkdtemp()
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Pasta de downloads
    DOWNLOAD_FOLDER = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'downloads'
    )

    # Cria a pasta se não existir
    os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)
