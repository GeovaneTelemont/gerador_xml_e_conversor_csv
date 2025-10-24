import os
from pathlib import Path
from typing import Dict, Any
from .base_validator import BaseValidator

class FileValidator(BaseValidator):
    """Validador para arquivos"""
    
    ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
    
    def validate(self, file, allowed_extensions: set = None) -> Dict[str, Any]:
        """
        Método abstrato implementado - valida um arquivo
        
        Args:
            file: Objeto de arquivo do Flask
            allowed_extensions: Extensões permitidas (opcional)
        
        Returns:
            Dict com resultado da validação
        """
        return self.validate_upload(file, allowed_extensions)
    
    def validate_upload(self, file, allowed_extensions: set = None) -> Dict[str, Any]:
        """
        Valida um arquivo enviado via upload
        
        Args:
            file: Objeto de arquivo do Flask
            allowed_extensions: Extensões permitidas (opcional)
        
        Returns:
            Dict com resultado da validação
        """
        self.clear_errors()
        self.clear_warnings()
        
        if allowed_extensions is None:
            allowed_extensions = self.ALLOWED_EXTENSIONS
        
        # Verifica se o arquivo foi enviado
        if not file or file.filename == '':
            self.add_error("Nenhum arquivo selecionado")
            return self.get_validation_result()
        
        # Verifica extensão
        if not self._is_allowed_file(file.filename, allowed_extensions):
            self.add_error(f"Tipo de arquivo não permitido. Use: {', '.join(allowed_extensions)}")
            return self.get_validation_result()
        
        # Verifica tamanho
        if not self._is_valid_size(file):
            self.add_error(f"Arquivo muito grande. Máximo: {self._format_size(self.MAX_FILE_SIZE)}")
            return self.get_validation_result()
        
        # Verifica se é um arquivo CSV válido (para CSV)
        if file.filename.lower().endswith('.csv'):
            if not self._is_valid_csv_file(file):
                self.add_error("Arquivo CSV inválido ou corrompido")
                return self.get_validation_result()
        
        return self.get_validation_result()
    
    def validate_file_exists(self, file_path: str) -> Dict[str, Any]:
        """Valida se um arquivo existe no sistema de arquivos"""
        self.clear_errors()
        self.clear_warnings()
        
        if not os.path.exists(file_path):
            self.add_error(f"Arquivo não encontrado: {file_path}")
        
        return self.get_validation_result()
    
    def _is_allowed_file(self, filename: str, allowed_extensions: set) -> bool:
        """Verifica se a extensão do arquivo é permitida"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    def _is_valid_size(self, file) -> bool:
        """Verifica se o tamanho do arquivo é válido"""
        # Volta para o início do arquivo para leitura
        if hasattr(file, 'seek'):
            file.seek(0, 2)  # Vai para o final
            file_size = file.tell()
            file.seek(0)  # Volta para o início
        else:
            file_size = len(file.read())
            if hasattr(file, 'seek'):
                file.seek(0)
        
        return file_size <= self.MAX_FILE_SIZE
    
    def _is_valid_csv_file(self, file) -> bool:
        """Verifica se é um arquivo CSV válido"""
        try:
            # Lê as primeiras linhas para verificar se é CSV válido
            if hasattr(file, 'read'):
                content = file.read(1024)  # Lê 1KB
                if hasattr(file, 'seek'):
                    file.seek(0)  # Volta para o início
                
                # Verifica se tem conteúdo e se parece com CSV
                if content and (b',' in content or b';' in content or b'|' in content):
                    return True
            return False
        except Exception:
            return False
    
    def _format_size(self, size_bytes: int) -> str:
        """Formata o tamanho em bytes para string legível"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"