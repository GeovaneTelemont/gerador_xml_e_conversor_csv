import pytest
import pandas as pd
import tempfile
import os
from gerador.validators.csv_validator import CSVValidator

class TestCSVValidator:
    
    def setup_method(self):
        self.validator = CSVValidator()
    
    def create_test_csv(self, content: str, separator: str = ';') -> str:
        """Cria um arquivo CSV temporário para testes"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(content)
            return f.name
    
    def test_validate_structure_valid_csv(self):
        # Cria um CSV válido
        csv_content = """COMPLEMENTO;COMPLEMENTO2;RESULTADO;LATITUDE;LONGITUDE
valor1;valor2;valor3;-23.5505;-46.6333"""
        
        csv_path = self.create_test_csv(csv_content)
        
        try:
            result = self.validator.validate_structure(csv_path, separator=';')
            
            assert result['is_valid'] == True
            assert len(result['errors']) == 0
        finally:
            os.unlink(csv_path)
    
    def test_validate_structure_missing_columns(self):
        # Cria um CSV com colunas faltantes
        csv_content = """COMPLEMENTO;LATITUDE
valor1;-23.5505"""
        
        csv_path = self.create_test_csv(csv_content)
        
        try:
            result = self.validator.validate_structure(csv_path, separator=';')
            
            assert result['is_valid'] == False
            assert "Colunas obrigatórias faltando" in result['errors'][0]
        finally:
            os.unlink(csv_path)
    
    def test_validate_structure_empty_file(self):
        # Cria um CSV vazio
        csv_content = ""
        
        csv_path = self.create_test_csv(csv_content)
        
        try:
            result = self.validator.validate_structure(csv_path, separator=';')
            
            assert result['is_valid'] == False
            assert "Arquivo CSV vazio ou inválido" in result['errors'][0]
        finally:
            os.unlink(csv_path)
    
    def test_validate_conversor_structure_valid(self):
        # Cria um CSV válido para o conversor
        csv_content = """CELULA|ESTACAO_ABASTECEDORA|UF|MUNICIPIO
celula1|estacao1|SP|São Paulo"""
        
        csv_path = self.create_test_csv(csv_content, separator='|')
        
        try:
            result = self.validator.validate_conversor_structure(csv_path, separator='|')
            
            # Não deve ter erros críticos (pode ter avisos de colunas faltantes)
            # Mas a estrutura básica é válida
            assert "Erro ao validar CSV do conversor" not in str(result['errors'])
        finally:
            os.unlink(csv_path)