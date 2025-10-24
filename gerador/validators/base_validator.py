from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

class BaseValidator(ABC):
    """Classe base para todos os validadores"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def add_error(self, message: str) -> None:
        """Adiciona um erro à lista de erros"""
        self.errors.append(message)
    
    def add_warning(self, message: str) -> None:
        """Adiciona um aviso à lista de avisos"""
        self.warnings.append(message)
    
    def has_errors(self) -> bool:
        """Verifica se existem erros"""
        return len(self.errors) > 0
    
    def has_warnings(self) -> bool:
        """Verifica se existem avisos"""
        return len(self.warnings) > 0
    
    def clear_errors(self) -> None:
        """Limpa a lista de erros"""
        self.errors.clear()
    
    def clear_warnings(self) -> None:
        """Limpa a lista de avisos"""
        self.warnings.clear()
    
    def get_validation_result(self) -> Dict[str, Any]:
        """Retorna o resultado da validação"""
        return {
            'is_valid': not self.has_errors(),
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy()
        }
    
    @abstractmethod
    def validate(self, *args, **kwargs) -> Dict[str, Any]:
        """Método abstrato para validação - deve ser implementado pelas subclasses"""
        pass