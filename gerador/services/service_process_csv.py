import os, shutil, zipfile
import pandas as pd
from datetime import datetime
from .service_create_xml import criar_xml_edificio_ccomplementos
from gerador.utils import obter_codigo_complemento, extrair_numero_argumento
from gerador.config import Config

def processar_csv(arquivo_path):
    global LOG_COMPLEMENTOS
    global ERRO_COMPLEMENTO2
    global ERRO_COMPLEMENTO3
    ERRO_COMPLEMENTO2 = False
    ERRO_COMPLEMENTO3 = False


    try:
        encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
        for encoding in encodings:
            try:
                df = pd.read_csv(arquivo_path, sep=';', encoding=encoding)
                # print(f"Arquivo lido com encoding: {encoding}")
                break 
            except UnicodeDecodeError:
                continue
        else:
            df = pd.read_csv(arquivo_path, sep=';')
    except Exception as e:
        raise Exception(f"Erro ao ler o arquivo CSV: {e}")

    if len(df) == 0:
        raise Exception("O arquivo CSV está vazio")

    estacao = df['ESTACAO_ABASTECEDORA'].iloc[0] if 'ESTACAO_ABASTECEDORA' in df.columns else 'DESCONHECIDA'
    diretorio_principal = f'moradias_xml_{estacao}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
    os.makedirs(diretorio_principal, exist_ok=True)

    pastas_criadas = []
    log_processamento = []

    for i, (index, linha) in enumerate(df.iterrows(), 1):
         # Verifica se a coluna COMPLEMENTO3 e COMPLEMENTO2 estão totalmente vazias
        coluna_complemento_2_vazia = df['COMPLEMENTO3'].isna().all() or (df['COMPLEMENTO3'].astype(str).str.strip() == '').all()
        
        nome_pasta = f'moradia{i}'
        caminho_pasta = os.path.join(diretorio_principal, nome_pasta)
        os.makedirs(caminho_pasta, exist_ok=True)
        pastas_criadas.append(caminho_pasta)

        comp1 = linha['COMPLEMENTO'] if 'COMPLEMENTO' in linha else ''
        comp2 = linha['COMPLEMENTO2'] if 'COMPLEMENTO2' in linha else ''
        resultado = linha['RESULTADO'] if 'RESULTADO' in linha else ''

        xml_content = criar_xml_edificio_ccomplementos(linha, i, coluna_complemento_2_vazia)

        # validação dos complementos
        if comp1 == '' or pd.isna(comp1):
            ERRO_COMPLEMENTO2 = True
            LOG_COMPLEMENTOS = "⚠️(ERRO) no CSV na coluna do [COMPLEMENTO1], existem células que estão vazias. Todas as celulas da coluna COMPLEMENTO2 teve ser preenchidas para gerar o xml com 2 complementos."
        
        elif comp2 == '' or pd.isna(comp2):
            ERRO_COMPLEMENTO2 = True
            LOG_COMPLEMENTOS = "⚠️(ERRO) no CSV na coluna do [COMPLEMENTO2], existem células que estão vazias. Todas as celulas da coluna COMPLEMENTO2 teve ser preenchidas para gerar o xml com 2 complementos."

        elif resultado == '' or pd.isna(resultado):
            ERRO_COMPLEMENTO3 = True
            LOG_COMPLEMENTOS = "⚠️(ERRO) no CSV na coluna do [COMPLEMENTO3], existem células que estão vazias. Todas as celulas da coluna COMPLEMENTO3 teve ser preenchidas para gerar o xml com 3 complementos."
        
        elif coluna_complemento_2_vazia:
            ERRO_COMPLEMENTO3 = False
            ERRO_COMPLEMENTO2 = False
            LOG_COMPLEMENTOS = "✅(XML) com dois complementos gerado com sucesso! Agora é só fazer o download do zip!"
        else:
            ERRO_COMPLEMENTO3 = False
            ERRO_COMPLEMENTO2 = False
            LOG_COMPLEMENTOS = "✅(XML) com três complementos gerado com sucesso! Agora é só fazer o download do zip!"


        caminho_xml = os.path.join(caminho_pasta, f'{nome_pasta}.xml')
        with open(caminho_xml, 'wb') as f:
            f.write(xml_content)

        if i % 10 == 0 or i == 1:
            codigo1 = obter_codigo_complemento(comp1)
            codigo2 = obter_codigo_complemento(comp2)
            arg1 = extrair_numero_argumento(comp1)
            arg2 = extrair_numero_argumento(comp2)
            log_processamento.append(f'Registro {i}:')

            if coluna_complemento_2_vazia:
                log_processamento.append(f'  COMP1("{comp1}" → código:{codigo1} argumento:"{arg1}")')
                log_processamento.append(f'  COMP2("{comp2}" → código:{codigo2} argumento:"{arg2}")')
                log_processamento.append('-' * 50)
                
            else:
                codigo3 = obter_codigo_complemento(resultado)
                arg3 = extrair_numero_argumento(resultado)
                log_processamento.append(f'  COMP1("{comp1}" → código:{codigo1} argumento:"{arg1}")')
                log_processamento.append(f'  COMP2("{comp2}" → código:{codigo2} argumento:"{arg2}")')
                log_processamento.append(f'  COMP3("{resultado}" → código:{codigo3} argumento:"{arg3}")')
                log_processamento.append('-' * 50)
          

    zip_filename = os.path.join(Config.DOWNLOAD_FOLDER, f'{diretorio_principal}.zip')
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for pasta in pastas_criadas:
            for root, dirs, files in os.walk(pasta):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, diretorio_principal)
                    zipf.write(file_path, arcname)

    shutil.rmtree(diretorio_principal)
    return os.path.basename(zip_filename), len(df), '\n'.join(log_processamento) 
