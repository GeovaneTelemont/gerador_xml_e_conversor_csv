# validators.py
import pandas as pd
import chardet
from typing import Dict, List, Tuple, Any
from gerador.constants import COLUNAS_OBRIGATORIAS  # Importar do constants
from flask import flash


class CSVValidator:
    def __init__(self):
        pass
    
    def validar(self, filepath):
        """
        Valida apenas os valores das colunas COMPLEMENTO, COMPLEMENTO2 e COMPLEMENTO3
        Retorna (sucesso, mensagem)
        """
        # Tentar diferentes codificações
        codificacoes = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'windows-1252']
        
        for encoding in codificacoes:
            try:
                # Ler o arquivo CSV
                with open(filepath, 'r', encoding=encoding) as f:
                    primeira_linha = f.readline()
                
                delimiter = ';' if ';' in primeira_linha else ','
                df = pd.read_csv(filepath, delimiter=delimiter, encoding=encoding)
                
                # Validar complementos
                resultado, info_complementos = self._validar_valores_complementos(df)
                
                if resultado:
                    return True, f'✅ {info_complementos}'
                else:
                    return False, f'❌ {info_complementos}'
                
            except UnicodeDecodeError:
                continue
            except Exception as e:
                continue
        
        return False, '❌ Não foi possível ler o arquivo.'
    
    def _validar_valores_complementos(self, df):
        """
        Valida os valores das colunas COMPLEMENTO, COMPLEMENTO2 e COMPLEMENTO3
        Retorna (resultado, mensagem)
        """
        # Normalizar nomes das colunas
        colunas_csv = {col.upper().strip(): col for col in df.columns}
        
        # Verificar se colunas existem
        for coluna in ['COMPLEMENTO', 'COMPLEMENTO2', 'COMPLEMENTO3']:
            if coluna not in colunas_csv:
                return False, f'Coluna {coluna} não encontrada'
        
        complemento_col = colunas_csv['COMPLEMENTO']
        complemento2_col = colunas_csv['COMPLEMENTO2'] 
        complemento3_col = colunas_csv['COMPLEMENTO3']
        
        erros_complementos = []
        registros_1_comp = 0
        registros_2_comp = 0
        registros_3_comp = 0
        
        for idx, row in df.iterrows():
            linha_num = idx + 2  # +2 porque idx começa em 0 e o CSV tem cabeçalho
            
            # Obter valores (tratar NaN como string vazia)
            comp1 = str(row[complemento_col]).strip() if pd.notna(row[complemento_col]) else ""
            comp2 = str(row[complemento2_col]).strip() if pd.notna(row[complemento2_col]) else ""
            comp3 = str(row[complemento3_col]).strip() if pd.notna(row[complemento3_col]) else ""
            
            # REGRA 1: COMPLEMENTO deve estar preenchido (obrigatório)
            if not comp1:
                erros_complementos.append("COMPLEMENTO deve estar preenchido")
                continue
            
            # Verificar combinações válidas
            if comp1 and not comp2 and not comp3:
                # 1 complemento: apenas COMPLEMENTO preenchido
                registros_1_comp += 1
                
            elif comp1 and comp2 and not comp3:
                # 2 complementos: COMPLEMENTO e COMPLEMENTO2 preenchidos
                registros_2_comp += 1
                
            elif comp1 and comp2 and comp3:
                # 3 complementos: todos preenchidos
                registros_3_comp += 1
                
            else:
                # Combinações inválidas
                if comp1 and not comp2 and comp3:
                    erros_complementos.append("Para gerar XML com três complementos a coluna COMPLEMENTO2 deve ser preenchida")
                elif comp1 and comp3 and not comp2:
                    erros_complementos.append("Para gerar XML com três complementos a coluna COMPLEMENTO2 deve ser preenchida")
                elif not comp1 and comp2:
                    erros_complementos.append("COMPLEMENTO deve estar preenchido")
                elif not comp1 and comp3:
                    erros_complementos.append("COMPLEMENTO deve estar preenchido")
        
        if erros_complementos:
            # Mostrar apenas o primeiro erro
            primeiro_erro = erros_complementos[0]
            return False, f'{primeiro_erro}'
        
        # Mensagem de sucesso
        total_registros = len(df)
        if registros_1_comp > 0 and registros_2_comp > 0 and registros_3_comp > 0:
            info = f'{registros_1_comp} registros com 1 complemento, {registros_2_comp} com 2 complementos e {registros_3_comp} com 3 complementos'
        elif registros_1_comp > 0 and registros_2_comp > 0:
            info = f'{registros_1_comp} registros com 1 complemento e {registros_2_comp} com 2 complementos'
        elif registros_1_comp > 0 and registros_3_comp > 0:
            info = f'{registros_1_comp} registros com 1 complemento e {registros_3_comp} com 3 complementos'
        elif registros_2_comp > 0 and registros_3_comp > 0:
            info = f'{registros_2_comp} registros com 2 complementos e {registros_3_comp} com 3 complementos'
        elif registros_1_comp > 0:
            info = f'{registros_1_comp} registros com 1 complemento'
        elif registros_2_comp > 0:
            info = f'{registros_2_comp} registros com 2 complementos'
        elif registros_3_comp > 0:
            info = f'{registros_3_comp} registros com 3 complementos'
        else:
            info = 'Nenhum registro válido encontrado'
        
        return True, info