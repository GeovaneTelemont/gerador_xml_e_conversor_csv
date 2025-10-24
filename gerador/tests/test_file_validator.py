import pytest
import os
import tempfile
from unittest.mock import Mock
from gerador.validators.file_validator import FileValidator

class TestFileValidator:
    
    def setup_method(self):
        self.validator = FileValidator()
    
    def test_validate_upload_no_file(self):
        # Testa quando nenhum arquivo é enviado
        result = self.validator.validate_upload(None)
        
        assert result['is_valid'] == False
        assert "Nenhum arquivo selecionado" in result['errors'][0]
    
    def test_validate_upload_empty_filename(self):
        # Testa quando o filename está vazio
        mock_file = Mock()
        mock_file.filename = ''
        
        result = self.validator.validate_upload(mock_file)
        
        assert result['is_valid'] == False
        assert "Nenhum arquivo selecionado" in result['errors'][0]
    
    def test_validate_upload_invalid_extension(self):
        # Testa extensão inválida
        mock_file = Mock()
        mock_file.filename = 'arquivo.txt'
        
        result = self.validator.validate_upload(mock_file)
        
        assert result['is_valid'] == False
        assert "Tipo de arquivo não permitido" in result['errors'][0]
    
    def test_validate_upload_valid_csv(self):
        # Testa arquivo CSV válido
        mock_file = Mock()
        mock_file.filename = 'teste.csv'
        mock_file.read.return_value = b'coluna1;coluna2\nvalor1;valor2'
        mock_file.seek = Mock()
        
        result = self.validator.validate_upload(mock_file)
        
        assert result['is_valid'] == True
        assert len(result['errors']) == 0
    
    def test_validate_file_exists(self):
        # Testa validação de arquivo existente
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            result = self.validator.validate_file_exists(temp_path)
            assert result['is_valid'] == True
        finally:
            os.unlink(temp_path)
    
    def test_validate_file_not_exists(self):
        # Testa validação de arquivo não existente
        result = self.validator.validate_file_exists('/caminho/inexistente/arquivo.csv')
        
        assert result['is_valid'] == False
        assert "Arquivo não encontrado" in result['errors'][0]