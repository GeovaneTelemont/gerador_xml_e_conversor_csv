import time, os 
from gerador.config import Config


def limpar_arquivos_antigos():
    """Limpa arquivos com mais de 1 hora na pasta de downloads"""
    try:
        agora = time.time()
        for filename in os.listdir(Config.DOWNLOAD_FOLDER):
            file_path = os.path.join(Config.DOWNLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                # Verificar se o arquivo tem mais de 1 hora
                if agora - os.path.getctime(file_path) > 3600:
                    os.remove(file_path)
    except Exception as e:
        print(f"Erro ao limpar arquivos antigos: {e}")