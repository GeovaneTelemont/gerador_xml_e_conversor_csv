import os
from datetime import datetime
from gerador.utils import carregar_roteiros, processar_enderecos_otimizado
from gerador.config import Config
import pandas as pd

def processar_conversor_csv(arquivo_path):
    """Processa o arquivo CSV para conversão"""
    try:
        print(f"📂 Carregando {arquivo_path}...")
        
        # Carrega o CSV
        df_enderecos = pd.read_csv(
            arquivo_path,
            encoding='latin-1',
            sep='|',
            engine='c',
            low_memory=False
        )
        
        print(f"✅ CSV carregado: {len(df_enderecos):,} linhas")
        
        # Carrega os roteiros
        df_roteiro_aparecida, df_roteiro_goiania = carregar_roteiros()
        if df_roteiro_aparecida is None or df_roteiro_goiania is None:
            raise Exception("Erro ao carregar arquivos de roteiro. Verifique se os arquivos estão na pasta 'roteiros'.")
        
        # Processa os dados
        df_final = processar_enderecos_otimizado(df_enderecos, df_roteiro_aparecida, df_roteiro_goiania)
        
        # Gera nome do arquivo
        nome_arquivo = f"Enderecos_Totais_CO_Convertido_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv"
        caminho_arquivo = os.path.join(Config.DOWNLOAD_FOLDER, nome_arquivo)
        
        # Salva o arquivo
        df_final.to_csv(
            caminho_arquivo,
            index=False,
            encoding='utf-8-sig',
            sep=';',
            quoting=1,
            quotechar='"',
            na_rep=''
        )
        
        print(f"✅ Arquivo convertido salvo: {nome_arquivo}")
        return nome_arquivo, len(df_final)
        
    except Exception as e:
        print(f"❌ Erro no processamento: {e}")
        raise Exception(f"Erro ao processar arquivo: {str(e)}")