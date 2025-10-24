import xml.etree.ElementTree as ET
from typing import Dict, Any
from .base_validator import BaseValidator

class XMLValidator(BaseValidator):
    """Validador para arquivos XML"""
    
    def validate(self, xml_content: str) -> Dict[str, Any]:
        """
        Método abstrato implementado - valida estrutura XML
        
        Args:
            xml_content: Conteúdo XML como string
        
        Returns:
            Dict com resultado da validação
        """
        return self.validate_structure(xml_content)
    
    def validate_structure(self, xml_content: str) -> Dict[str, Any]:
        """
        Valida a estrutura básica do XML
        
        Args:
            xml_content: Conteúdo XML como string
        
        Returns:
            Dict com resultado da validação
        """
        self.clear_errors()
        self.clear_warnings()
        
        try:
            # Tenta parsear o XML
            root = ET.fromstring(xml_content)
            
            # Validações básicas
            if not root:
                self.add_error("XML inválido - raiz não encontrada")
            
            # Valida elementos obrigatórios para seu schema
            required_elements = ['edificio', 'enderecoEdificio', 'tecnico', 'empresa']
            for elem in required_elements:
                if root.find(elem) is None:
                    self.add_error(f"Elemento obrigatório '{elem}' não encontrado no XML")
            
            # Valida atributos obrigatórios
            required_attrs = ['tipo', 'versao']
            for attr in required_attrs:
                if attr not in root.attrib:
                    self.add_warning(f"Atributo '{attr}' não encontrado no elemento raiz")
            
        except ET.ParseError as e:
            self.add_error(f"Erro de parsing XML: {str(e)}")
        except Exception as e:
            self.add_error(f"Erro ao validar XML: {str(e)}")
        
        return self.get_validation_result()
    
    def validate_complementos(self, xml_content: str) -> Dict[str, Any]:
        """
        Valida específicamente os complementos no XML
        """
        self.clear_errors()
        self.clear_warnings()
        
        try:
            root = ET.fromstring(xml_content)
            endereco = root.find('enderecoEdificio')
            
            if endereco is not None:
                # Valida complemento1
                comp1 = endereco.find('id_complemento1')
                if comp1 is None or comp1.text is None or comp1.text.strip() == '':
                    self.add_warning("Complemento1 não encontrado ou vazio")
                
                # Valida complemento2  
                comp2 = endereco.find('id_complemento2')
                if comp2 is None or comp2.text is None or comp2.text.strip() == '':
                    self.add_warning("Complemento2 não encontrado ou vazio")
                
                # Complemento3 é opcional
                comp3 = endereco.find('id_complemento3')
                if comp3 is not None and (comp3.text is None or comp3.text.strip() == ''):
                    self.add_warning("Complemento3 definido mas vazio")
                    
        except Exception as e:
            self.add_error(f"Erro ao validar complementos: {str(e)}")
        
        return self.get_validation_result()