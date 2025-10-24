import os
import pandas as pd
import numpy as np
from gerador.constants import CODIGOS_COMPLEMENTO, PROGRESS_LOCK, MESSAGE_QUEUE

def formatar_coordenada(coord):
    """Converte coordenada de formato brasileiro para internacional"""
    if pd.isna(coord):
        return None
    try:
        return float(str(coord).replace(',', '.'))
    except ValueError:
        return None

def update_progress(message, progress=None, current=None, total=None, status=None):
    """Atualiza os dados de progresso e envia para a fila"""
    global progress_data
    with PROGRESS_LOCK:
        if message:
            progress_data['message'] = message
        if progress is not None:
            progress_data['progress'] = progress
        if current is not None:
            progress_data['current'] = current
        if total is not None:
            progress_data['total'] = total
        if status:
            progress_data['status'] = status
        
        # Envia cópia dos dados para a fila
        MESSAGE_QUEUE.put(progress_data.copy())

# REMOVIDA: função validar_colunas_csv - agora está no CSVValidator

def obter_codigo_complemento(texto):
    """
    Obtém o código do complemento baseado nas duas primeiras letras do texto
    """
    if pd.isna(texto) or texto == '':
        return '60'  # Default para LT (LOTE)
    
    texto_str = str(texto).strip().upper()
    
    # Pegar as duas primeiras letras
    if len(texto_str) >= 2:
        codigo = texto_str[:2]
        return str(CODIGOS_COMPLEMENTO.get(codigo, 60))  # Default 60 se não encontrar
    else:
        return '60'  # Default para LT (LOTE)

def extrair_numero_argumento(texto):
    """
    Extrai TODO o conteúdo depois das duas primeiras letras
    """
    if pd.isna(texto) or texto == '':
        return '1'
    
    texto_str = str(texto).strip()
    
    if len(texto_str) < 2:
        return '1'
    
    argumento = texto_str[2:].strip()
    
    if argumento == '':
        return '1'
    
    return argumento

def determinar_destinacao(ucs_residenciais, ucs_comerciais):
    """Determina a destinação baseado nas UCs residenciais e comerciais"""
    if ucs_residenciais > 0 and ucs_comerciais == 0:
        return 'RESIDENCIA'
    elif ucs_comerciais > 0 and ucs_residenciais == 0:
        return 'COMERCIO'
    else:
        return 'MISTA'

def validador_xml(xml_content, complemento_vazio):
    # Esta função pode ser movida para XMLValidator depois
    pass

def carregar_roteiros():
    """Carrega os arquivos de roteiro necessários para a conversão"""
    try:
        # Caminho absoluto para a pasta de roteiros
        base_dir = os.path.dirname(os.path.abspath(__file__))
        roteiros_dir = os.path.join(base_dir, 'roteiros')
        
        caminho_aparecida = os.path.join(roteiros_dir, 'roteiro_aparecida.xlsx')
        caminho_goiania = os.path.join(roteiros_dir, 'roteiro_goiania.xlsx')
        
        print(f"📂 Tentando carregar roteiros de:")
        print(f"   - {caminho_aparecida}")
        print(f"   - {caminho_goiania}")
        
        # Verificar se os arquivos existem
        if not os.path.exists(caminho_aparecida):
            print(f"❌ Arquivo não encontrado: {caminho_aparecida}")
            return None, None
        if not os.path.exists(caminho_goiania):
            print(f"❌ Arquivo não encontrado: {caminho_goiania}")
            return None, None
            
        df_roteiro_aparecida = pd.read_excel(caminho_aparecida)
        df_roteiro_goiania = pd.read_excel(caminho_goiania)
        
        print("✅ Roteiros carregados com sucesso")
        print(f"   - Aparecida: {len(df_roteiro_aparecida)} registros")
        print(f"   - Goiania: {len(df_roteiro_goiania)} registros")
        
        return df_roteiro_aparecida, df_roteiro_goiania
        
    except Exception as e:
        print(f"❌ Erro ao carregar roteiros: {e}")
        return None, None

# ... (o restante da função processar_enderecos_otimizado permanece igual)
def processar_enderecos_otimizado(df_enderecos, df_roteiro_aparecida, df_roteiro_goiania):
    """
    Processa os dados de endereços de forma otimizada mantendo TODOS os dados originais
    """
    # ... (código completo da função permanece igual)
    # ... (mantenha todo o código existente desta função)