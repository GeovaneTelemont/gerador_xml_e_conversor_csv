# validators.py
import pandas as pd
import os
from typing import Dict, List, Tuple, Any
from gerador.constants import COLUNAS_OBRIGATORIAS  # Importar do constants

class CSVValidator:
    def __init__(self):
        # Usar as colunas obrigatórias do constants.py
        self.colunas_obrigatorias = COLUNAS_OBRIGATORIAS
        
        # Colunas de complementos específicas do seu sistema
        self.colunas_complementos = ['COMPLEMENTO', 'COMPLEMENTO2', 'COMPLEMENTO3']
    
    def validate_conversor_structure(self, filepath: str, separator: str = '|') -> Dict[str, Any]:
        """
        Valida a estrutura do CSV para o conversor
        Retorna dict com informações sobre validação e tipo de conversão
        """
        try:
            # Ler o CSV
            df = pd.read_csv(filepath, sep=separator, dtype=str, encoding='utf-8')
            df.columns = df.columns.str.strip().str.upper()  # Converter para maiúsculas
            
            # Verificar colunas existentes
            colunas_encontradas = list(df.columns)
            colunas_faltantes = []
            colunas_extras = []
            
            # Validar colunas obrigatórias
            for coluna in self.colunas_obrigatorias:
                if coluna not in colunas_encontradas:
                    colunas_faltantes.append(coluna)
            
            # Identificar colunas extras
            for coluna in colunas_encontradas:
                if (coluna not in self.colunas_obrigatorias and 
                    coluna not in self.colunas_complementos):
                    colunas_extras.append(coluna)
            
            # Determinar tipo de conversão baseado nos complementos
            tipo_conversao = self._determinar_tipo_conversao(df)
            
            # Montar resultado
            resultado = {
                'is_valid': len(colunas_faltantes) == 0,
                'colunas_encontradas': colunas_encontradas,
                'colunas_faltantes': colunas_faltantes,
                'colunas_extras': colunas_extras,
                'total_colunas': len(colunas_encontradas),
                'tipo_conversao': tipo_conversao,
                'total_registros': len(df)
            }
            
            # Adicionar mensagens de erro se necessário
            if not resultado['is_valid']:
                resultado['errors'] = [
                    f'Colunas obrigatórias faltantes: {", ".join(colunas_faltantes)}'
                ]
            else:
                resultado['errors'] = []
                
            # Adicionar informações sobre complementos
            resultado['complementos_info'] = self._analisar_complementos(df)
            
            return resultado
            
        except Exception as e:
            return {
                'is_valid': False,
                'errors': [f'Erro ao validar arquivo CSV: {str(e)}'],
                'colunas_faltantes': [],
                'colunas_extras': [],
                'tipo_conversao': 'indeterminado'
            }
    
    def _determinar_tipo_conversao(self, df: pd.DataFrame) -> str:
        """
        Determina o tipo de conversão baseado nos complementos preenchidos
        Seguindo a lógica especificada:
        - COMPLEMENTO3 preenchido → 3 complementos
        - COMPLEMENTO2 preenchido → 2 complementos  
        - COMPLEMENTO preenchido → 1 complemento
        """
        # Verificar se as colunas existem e estão preenchidas
        complemento_preenchido = 'COMPLEMENTO' in df.columns and not df['COMPLEMENTO'].isna().all()
        complemento2_preenchido = 'COMPLEMENTO2' in df.columns and not df['COMPLEMENTO2'].isna().all()
        complemento3_preenchido = 'COMPLEMENTO3' in df.columns and not df['COMPLEMENTO3'].isna().all()
        
        print(f"🔍 Análise de complementos:")
        print(f"   COMPLEMENTO: {complemento_preenchido}")
        print(f"   COMPLEMENTO2: {complemento2_preenchido}") 
        print(f"   COMPLEMENTO3: {complemento3_preenchido}")
        
        # Aplicar a lógica especificada
        if complemento3_preenchido:
            return '3_complementos'
        elif complemento2_preenchido:
            return '2_complementos'
        elif complemento_preenchido:
            return '1_complemento'
        else:
            return 'sem_complementos'
    
    def _analisar_complementos(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Analisa o preenchimento dos complementos
        """
        info = {}
        
        for complemento in self.colunas_complementos:
            if complemento in df.columns:
                total_linhas = len(df)
                # Contar linhas não vazias (considerando NaN, None e string vazia)
                linhas_preenchidas = df[complemento].apply(
                    lambda x: False if pd.isna(x) or str(x).strip() == '' else True
                ).sum()
                linhas_vazias = total_linhas - linhas_preenchidas
                percentual_preenchido = (linhas_preenchidas / total_linhas) * 100
                
                info[complemento] = {
                    'presente': True,
                    'total_preenchido': int(linhas_preenchidas),
                    'total_vazio': int(linhas_vazias),
                    'percentual_preenchido': round(percentual_preenchido, 2),
                    'completamente_preenchido': linhas_vazias == 0
                }
                
                print(f"   {complemento}: {linhas_preenchidas}/{total_linhas} preenchidos ({percentual_preenchido:.1f}%)")
            else:
                info[complemento] = {
                    'presente': False,
                    'total_preenchido': 0,
                    'total_vazio': len(df),
                    'percentual_preenchido': 0,
                    'completamente_preenchido': False
                }
                print(f"   {complemento}: COLUNA NÃO ENCONTRADA")
        
        return info
    
    def validate_xml_generator_structure(self, filepath: str, separator: str = '|') -> Dict[str, Any]:
        """
        Validação específica para o gerador de XML
        """
        return self.validate_conversor_structure(filepath, separator)