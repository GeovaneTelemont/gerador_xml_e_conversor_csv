import os
import pandas as pd
import numpy as np
from gerador.constants import CODIGOS_COMPLEMENTO, COLUNAS_OBRIGATORIAS, PROGRESS_LOCK, MESSAGE_QUEUE


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

def _normalize_cols(cols):
    # Remove BOM, espaços externos e normaliza para uppercase
    return [str(c).replace('\ufeff','').strip().upper() for c in cols]

def validar_colunas_csv(arquivo_path, verbose=True):
    """
        Validador robusto que tenta vários encodings e separadores,
        mostra o cabeçalho lido e quais colunas estão faltando/extras.
        Retorna um dict com o melhor resultado e um log de todas as tentativas.
    """
    
    encodings = ['utf-8-sig', 'utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    separadores = ['|', ';', '\t', ',']
    obrigatorias = [c.upper() for c in COLUNAS_OBRIGATORIAS]

    attempts = []

    # Ler a primeira linha bruta (para inspecionar)
    try:
        with open(arquivo_path, 'rb') as f:
            raw_head_bytes = f.readline()
        # tenta decodificar com algumas codificações para ver a primeira linha
        head_samples = {}
        for enc in encodings:
            try:
                head_samples[enc] = raw_head_bytes.decode(enc, errors='replace').strip()
            except Exception:
                head_samples[enc] = None
    except Exception as e:
        return {
            'valido': False,
            'erro': f'Erro ao abrir arquivo: {e}',
            'attempts': []
        }

    # Tenta combinações de encoding x separador
    for enc in encodings:
        for sep in separadores:
            try:
                df_header = pd.read_csv(arquivo_path, encoding=enc, sep=sep, nrows=0)
                cols = _normalize_cols(df_header.columns.tolist())
                cols_set = set(cols)
                faltantes = sorted(list(set(obrigatorias) - cols_set))
                extras = sorted(list(cols_set - set(obrigatorias)))
                ok = (len(faltantes) == 0)

                attempts.append({
                    'encoding': enc,
                    'separador': repr(sep),
                    'header_preview': head_samples.get(enc),
                    'num_cols': len(cols),
                    'cols_sample': cols[:20],
                    'colunas_encontradas': cols,
                    'colunas_faltantes': faltantes,
                    'colunas_extras': extras,
                    'valido': ok
                })

                # Se válido, devolve imediatamente (mas ainda loga)
                if ok:
                    if verbose:
                        print("✅ Validação OK com encoding:", enc, "separador:", repr(sep))
                        print("Colunas encontradas (exemplo):", cols[:20])
                        if faltantes:
                            print("Colunas faltantes:", faltantes)
                    return {
                        'valido': True,
                        'encoding': enc,
                        'separador': sep,
                        'colunas_encontradas': cols,
                        'colunas_faltantes': faltantes,
                        'colunas_extras': extras,
                        'attempts': attempts
                    }

            except Exception as e:
                # registra falha dessa tentativa
                attempts.append({
                    'encoding': enc,
                    'separador': repr(sep),
                    'erro': str(e),
                    'valido': False
                })
                continue

    # Nenhuma tentativa foi totalmente válida — retorna relatório detalhado
    if verbose:
        print("❌ Nenhuma combinação encontrou todas as colunas obrigatórias.")
        for at in attempts:
            print("----")
            print("encoding:", at.get('encoding'), "sep:", at.get('separador'), "valido:", at.get('valido'))
            if 'cols_sample' in at:
                print("cols_sample:", at.get('cols_sample')[:20])
            if 'colunas_faltantes' in at and at.get('colunas_faltantes'):
                print("faltantes:", at.get('colunas_faltantes'))
            if 'erro' in at:
                print("erro:", at.get('erro'))

    # escolher tentativa "melhor" (a que tem menos faltantes) para retorno
    best = min(
        (a for a in attempts if 'colunas_faltantes' in a),
        key=lambda x: len(x.get('colunas_faltantes', [])),
        default=None
    )

    return {
        'valido': False,
        'erro': 'Nenhuma combinação de encoding/separador satisfez as colunas obrigatórias.',
        'best_attempt': best,
        'attempts': attempts
    }

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
    
def processar_enderecos_otimizado(df_enderecos, df_roteiro_aparecida, df_roteiro_goiania):
    """
    Processa os dados de endereços de forma otimizada mantendo TODOS os dados originais
    """
    
    # Fazer uma cópia do dataframe
    df = df_enderecos.copy()
    
    print(f"🔍 Colunas iniciais: {list(df.columns)}")
    print(f"📊 Total de linhas inicial: {len(df)}")
    
    # ========== CORREÇÕES DE FORMATAÇÃO OTIMIZADAS ==========
    
    print("🔧 Aplicando correções de formatação...")
    
    # 1. Corrigir CEP - operações vetorizadas
    if 'CEP' in df.columns:
        df['CEP'] = (df['CEP'].astype(str)
                      .str.strip()
                      .str.replace(r'\D', '', regex=True)
                      .str[:8]
                      .apply(lambda x: x.zfill(8) if x != '' else ''))
        print("✅ CEP formatado")
    
    # 2. Corrigir COD_LOGRADOURO - operações vetorizadas
    if 'COD_LOGRADOURO' in df.columns:
        df['COD_LOGRADOURO'] = (df['COD_LOGRADOURO'].astype(str)
                                 .str.strip()
                                 .str.replace(r'\D', '', regex=True)
                                 .str[:10])
        print("✅ COD_LOGRADOURO formatado")
    
    # ========== CRIAÇÃO DE COLUNAS OTIMIZADAS ==========
    
    print("Criando CHAVE LOG...")
    # CHAVE LOG otimizada - evita apply
    colunas_chave = ['ESTACAO_ABASTECEDORA', 'LOCALIDADE', 'LOGRADOURO', 'COMPLEMENTO', 'COMPLEMENTO2']
    for coluna in colunas_chave:
        if coluna in df.columns:
            df[coluna] = df[coluna].fillna('').astype(str).str.strip()
    
    # Cria CHAVE LOG de forma vetorizada
    df['CHAVE LOG'] = (df['ESTACAO_ABASTECEDORA'] + "-" + 
                      df['LOCALIDADE'] + "-" + 
                      df['LOGRADOURO'] + "-" + 
                      df['COMPLEMENTO'] + "-" + 
                      df['COMPLEMENTO2'])
    
    # Remove hífens extras
    df['CHAVE LOG'] = df['CHAVE LOG'].str.replace(r'-+', '-', regex=True).str.strip('-')
    
    print("Processando COMPLEMENTO3...")
    # COMPLEMENTO3 otimizado - MANTÉM OS DADOS ORIGINAIS
    if 'COMPLEMENTO3' in df.columns:
        # Salva o original
        df['COMPLEMENTO3_ORIGINAL'] = df['COMPLEMENTO3']
        # Cria versão tratada para processamento
        df['COMPLEMENTO3_TRATADO'] = df['COMPLEMENTO3'].fillna('').astype(str).str.strip().str.upper()
    else:
        df['COMPLEMENTO3_ORIGINAL'] = ''
        df['COMPLEMENTO3_TRATADO'] = ''
    
    # Extrai prefixo de forma vetorizada (usa o tratado)
    df['Prefixo'] = df['COMPLEMENTO3_TRATADO'].str[:2]
    
    print("Agrupando e numerando...")
    # Filtra e agrupa de forma mais eficiente - MAS MANTÉM TODAS AS LINHAS
    mask_prefixo_valido = (df['Prefixo'].notna()) & (df['Prefixo'] != "")
    df_com_prefixo = df[mask_prefixo_valido].copy()
    df_sem_prefixo = df[~mask_prefixo_valido].copy()
    
    # Aplica agrupamento apenas se houver dados
    if len(df_com_prefixo) > 0:
        df_com_prefixo['ORDEM'] = df_com_prefixo.groupby(['CHAVE LOG', 'Prefixo']).cumcount() + 1
        df_com_prefixo['Resultado'] = df_com_prefixo['Prefixo'] + " " + df_com_prefixo['ORDEM'].astype(str)
        df_com_prefixo = df_com_prefixo.drop('Prefixo', axis=1)
    else:
        df_com_prefixo['ORDEM'] = 0
        df_com_prefixo['Resultado'] = ""
    
    # Prepara dados sem prefixo - MANTÉM TODOS OS DADOS ORIGINAIS
    df_sem_prefixo['ORDEM'] = 0
    df_sem_prefixo['Resultado'] = ""
    if 'Prefixo' in df_sem_prefixo.columns:
        df_sem_prefixo = df_sem_prefixo.drop('Prefixo', axis=1)
    
    # Combina os dataframes - AGORA COM TODAS AS LINHAS
    df = pd.concat([df_com_prefixo, df_sem_prefixo], ignore_index=True)
    
    print(f"📊 Linhas com prefixo válido: {len(df_com_prefixo)}")
    print(f"📊 Linhas sem prefixo válido: {len(df_sem_prefixo)}")
    print(f"📊 Total após concatenação: {len(df)}")
    
    # ========== TRANSFORMAÇÕES RÁPIDAS ==========
    
    print("Aplicando transformações rápidas...")
    
    # COD_ZONA otimizado
    if 'CELULA' in df.columns:
        df['Nº CELULA'] = df['CELULA'].str.split(' ').str[0].fillna('')
    else:
        df['Nº CELULA'] = ''
    
    df['COD_ZONA'] = (df['UF'] + "-" + df['LOCALIDADE_ABREV'] + "-" + 
                     df['ESTACAO_ABASTECEDORA'] + "-CEOS-" + df['Nº CELULA'])
    
    # RESULTADO e COMPARATIVO otimizados
    df['RESULTADO'] = df['Resultado'].str.replace(' ', '')
    
    # COMPARATIVO usa o COMPLEMENTO3 original
    df['COMPARATIVO'] = np.where(df['RESULTADO'] == df['COMPLEMENTO3_TRATADO'], "VERDADEIRO", "FALSO")
    
    # Remove coluna temporária
    if 'Nº CELULA' in df.columns:
        df = df.drop('Nº CELULA', axis=1)
    
    # ========== MERGE OTIMIZADO E CORRIGIDO ==========
    
    print("Fazendo merge com roteiros...")
    df_roteiros = pd.concat([df_roteiro_aparecida, df_roteiro_goiania], ignore_index=True)
    
    # Prepara colunas para merge - CORREÇÃO DO ERRO
    if 'id' in df_roteiros.columns:
        df_roteiros['id'] = df_roteiros['id'].astype(str).str.replace(r'\.0$', '', regex=True)
    if 'id_localidade' in df_roteiros.columns:
        df_roteiros['id_localidade'] = df_roteiros['id_localidade'].astype(str).str.replace(r'\.0$', '', regex=True)
    
    # CORREÇÃO: Converter cod_lograd para string para compatibilidade com COD_LOGRADOURO
    if 'cod_lograd' in df_roteiros.columns:
        df_roteiros['cod_lograd'] = df_roteiros['cod_lograd'].astype(str).str.strip()
        df_roteiros['cod_lograd'] = df_roteiros['cod_lograd'].str.replace(r'\D', '', regex=True)
        df_roteiros['cod_lograd'] = df_roteiros['cod_lograd'].str[:10]  # Garante 10 dígitos
    
    # Faz merge apenas se as colunas existem
    if 'COD_LOGRADOURO' in df.columns and 'cod_lograd' in df_roteiros.columns:
        # Garantir que ambas as colunas são strings
        df['COD_LOGRADOURO'] = df['COD_LOGRADOURO'].astype(str)
        df_roteiros['cod_lograd'] = df_roteiros['cod_lograd'].astype(str)
        
        df = df.merge(
            df_roteiros[['cod_lograd', 'id', 'id_localidade']],
            left_on='COD_LOGRADOURO',
            right_on='cod_lograd',
            how='left'
        )
        df = df.rename(columns={'id': 'ID_ROTEIRO', 'id_localidade': 'ID_LOCALIDADE'})
        if 'cod_lograd' in df.columns:
            df = df.drop('cod_lograd', axis=1)
        print("✅ Merge com roteiros concluído")
    else:
        df['ID_ROTEIRO'] = ''
        df['ID_LOCALIDADE'] = ''
        print("⚠️  Merge não realizado - colunas de junção não encontradas")
    
    # ========== REMOVE DUPLICATAS ==========
    
    if 'COD_SURVEY' in df.columns:
        antes = len(df)
        df = df.drop_duplicates(subset=['COD_SURVEY'])
        depois = len(df)
        print(f"📊 Duplicatas removidas: {antes - depois}")
    
    # ========== COLUNAS NUMÉRICAS ==========
    
    print("Processando colunas numéricas...")
    # Extrai números do COMPLEMENTO3 tratado
    df['Nº ARGUMENTO3 COMPLEMENTO3'] = (df['COMPLEMENTO3_TRATADO']
                                       .str.extract(r'(\d+)')[0]
                                       .fillna(0)
                                       .astype(int))
    
    df['ORDEM'] = df['ORDEM'].astype(int)
    
    # ========== VALIDAÇÃO SIMPLIFICADA ==========
    
    print("Criando validação...")
    conditions = [
        df['ORDEM'] == 0,
        df['Nº ARGUMENTO3 COMPLEMENTO3'] == 0,
        df['Nº ARGUMENTO3 COMPLEMENTO3'] > 10,
        df['ORDEM'] > 10
    ]
    
    choices = [
        "SEM PREFIXO VÁLIDO",
        "VERIFICAR COMPLEMENTO3-VAZIO",
        "VERIFICAR COMPLEMENTO3 >10", 
        "VERIFICAR RESULTADO >10"
    ]
    
    df['VALIDAÇÃO'] = np.select(conditions, choices, default="OK")
    
    # ========== GARANTIR ESTRUTURA FINAL ==========
    
    print("Finalizando estrutura...")
    
    # RESTAURA O COMPLEMENTO3 ORIGINAL
    df['COMPLEMENTO3'] = df['COMPLEMENTO3_ORIGINAL']
    
    colunas_finais = [
        'CHAVE LOG', 'CELULA', 'ESTACAO_ABASTECEDORA', 'UF', 'MUNICIPIO', 'LOCALIDADE', 
        'COD_LOCALIDADE', 'LOCALIDADE_ABREV', 'LOGRADOURO', 'COD_LOGRADOURO', 'NUM_FACHADA', 
        'COMPLEMENTO', 'COMPLEMENTO2', 'COMPLEMENTO3', 'CEP', 'BAIRRO', 'COD_SURVEY', 
        'QUANTIDADE_UMS', 'COD_VIABILIDADE', 'TIPO_VIABILIDADE', 'TIPO_REDE', 'UCS_RESIDENCIAIS', 
        'UCS_COMERCIAIS', 'NOME_CDO', 'ID_ENDERECO', 'LATITUDE', 'LONGITUDE', 'TIPO_SURVEY', 
        'REDE_INTERNA', 'UMS_CERTIFICADAS', 'REDE_EDIF_CERT', 'DISP_COMERCIAL', 'ESTADO_CONTROLE', 
        'DATA_ESTADO_CONTROLE', 'ID_CELULA', 'QUANTIDADE_HCS', 'ID_ROTEIRO', 'ID_LOCALIDADE', 
        'COD_ZONA', 'ORDEM', 'RESULTADO', 'COMPARATIVO', 'Nº ARGUMENTO3 COMPLEMENTO3', 'VALIDAÇÃO'
    ]
    
    # Adiciona colunas faltantes
    for coluna in colunas_finais:
        if coluna not in df.columns:
            df[coluna] = ''
    
    # Reordena colunas
    df = df[colunas_finais]
    
    # Remove colunas auxiliares
    colunas_para_remover = ['COMPLEMENTO3_ORIGINAL', 'COMPLEMENTO3_TRATADO', 'Resultado']
    for coluna in colunas_para_remover:
        if coluna in df.columns:
            df = df.drop(coluna, axis=1)
    
    # ========== PREPARAÇÃO PARA POWER QUERY (RÁPIDA) ==========
    
    print("Preparando para Power Query...")
    
    # Apenas as correções essenciais para Power Query
    df = df.replace({
        'NaN': '',
        'nan': '',
        'None': '',
        'null': '',
        'True': 'VERDADEIRO',
        'False': 'FALSO'
    })
    
    # Remove valores nulos
    df = df.fillna('')
    
    print(f"✅ Processamento concluído. Linhas: {len(df):,}")
    
    # Verificar estatísticas dos dados
    print(f"\n📈 ESTATÍSTICAS DOS DADOS:")
    print(f"   - Total de linhas: {len(df):,}")
    print(f"   - COMPLEMENTO3 vazios: {(df['COMPLEMENTO3'] == '').sum():,}")
    print(f"   - COMPLEMENTO2 vazios: {(df['COMPLEMENTO2'] == '').sum():,}")
    print(f"   - Linhas com validação OK: {(df['VALIDAÇÃO'] == 'OK').sum():,}")
    print(f"   - Linhas sem prefixo válido: {(df['VALIDAÇÃO'] == 'SEM PREFIXO VÁLIDO').sum():,}")
    
    return df



