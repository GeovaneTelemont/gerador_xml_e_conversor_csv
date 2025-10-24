import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from gerador.utils import formatar_coordenada, obter_codigo_complemento, extrair_numero_argumento
import xml.etree.ElementTree as ET
from datetime import datetime
import pandas as pd


class GeradorXml:
    """Classe para gerar XML de edificios com complementos"""
    
    def __init__(self, dados_csv, numero_pasta, complemento_vazio):
        self.dados_csv = dados_csv
        self.numero_pasta = numero_pasta
        self.complemento_vazio = complemento_vazio
        self.edificio = None
        
        # Valores padrão
        self.valores_padrao = {
            'codigo_zona': 'DF-GURX-ETGR-CEOS-68',
            'localidade': 'GUARA',
            'id_endereco': '93128133',
            'cep': '71065071',
            'id_roteiro': '57149008',
            'id_localidade': '1894644',
            'cod_lograd': '2700035341',
            'id_tecnico': '1828772688',
            'nome_tecnico': 'NADIA CAROLINE',
            'id_empresa': '42541126',
            'nome_empresa': 'TELEMONT',
            'total_ucs': 1
        }
    
    def _obter_valor(self, campo, campo_padrao=None):
        """Obtém valor do CSV ou usa valor padrão"""
        if campo in self.dados_csv and not pd.isna(self.dados_csv[campo]):
            return str(self.dados_csv[campo])
        return self.valores_padrao.get(campo_padrao, '')
    
    def _criar_elemento_simples(self, pai, tag, valor):
        """Cria elemento XML simples"""
        if valor is not None:
            ET.SubElement(pai, tag).text = str(valor)
    
    def _configurar_cabecalho(self):
        """Configura cabeçalho do XML"""
        self.edificio = ET.Element('edificio')
        self.edificio.set('tipo', 'M')
        self.edificio.set('versao', '7.9.2')
        
        self._criar_elemento_simples(self.edificio, 'gravado', 'false')
        self._criar_elemento_simples(self.edificio, 'nEdificio', 
                                   self._obter_valor('COD_SURVEY'))
    
    def _configurar_coordenadas(self):
        """Configura coordenadas do edificio"""
        latitude = formatar_coordenada(self.dados_csv['LATITUDE'])
        longitude = formatar_coordenada(self.dados_csv['LONGITUDE'])
        
        self._criar_elemento_simples(self.edificio, 'coordX', str(longitude))
        self._criar_elemento_simples(self.edificio, 'coordY', str(latitude))
    
    def _configurar_zona_localidade(self):
        """Configura zona e localidade"""
        codigo_zona = self._obter_valor('COD_ZONA', 'codigo_zona')
        localidade = self._obter_valor('LOCALIDADE', 'localidade')
        
        self._criar_elemento_simples(self.edificio, 'codigoZona', codigo_zona)
        self._criar_elemento_simples(self.edificio, 'nomeZona', codigo_zona)
        self._criar_elemento_simples(self.edificio, 'localidade', localidade)
    
    def _configurar_endereco(self):
        """Configura endereço completo"""
        endereco = ET.SubElement(self.edificio, 'enderecoEdificio')
        
        # Elementos básicos do endereço
        self._criar_elemento_simples(endereco, 'id', 
                                   self._obter_valor('ID_ENDERECO', 'id_endereco'))
        
        logradouro = self._construir_logradouro()
        self._criar_elemento_simples(endereco, 'logradouro', logradouro)
        
        self._criar_elemento_simples(endereco, 'numero_fachada',
                                   self._obter_valor('NUM_FACHADA') or 'SN')
        
        # Complementos
        self._adicionar_complementos(endereco)
        
        # Demais campos do endereço
        self._criar_elemento_simples(endereco, 'cep', 
                                   self._obter_valor('CEP', 'cep'))
        
        bairro = self._obter_valor('BAIRRO') or self._obter_valor('LOCALIDADE', 'localidade')
        self._criar_elemento_simples(endereco, 'bairro', bairro)
        
        self._criar_elemento_simples(endereco, 'id_roteiro',
                                   self._obter_valor('ID_ROTEIRO', 'id_roteiro'))
        
        self._criar_elemento_simples(endereco, 'id_localidade',
                                   self._obter_valor('ID_LOCALIDADE', 'id_localidade'))
        
        self._criar_elemento_simples(endereco, 'cod_lograd',
                                   self._obter_valor('COD_LOGRADOURO', 'cod_lograd'))
    
    def _construir_logradouro(self):
        """Constrói string do logradouro"""
        partes = [
            self._obter_valor('LOGRADOURO'),
            self._obter_valor('BAIRRO'),
            self._obter_valor('MUNICIPIO'),
            f"{self._obter_valor('LOCALIDADE', 'localidade')} - {self._obter_valor('UF')}"
        ]
        
        # Filtra partes vazias e junta
        partes_validas = [p for p in partes if p]
        logradouro = ", ".join(partes_validas)
        
        # Adiciona código do logradouro se disponível
        cod_lograd = self._obter_valor('COD_LOGRADOURO')
        if cod_lograd:
            logradouro += f" ({cod_lograd})"
            
        return logradouro
    
    def _adicionar_complementos(self, endereco):
        """Adiciona complementos ao endereço"""
        complementos = [
            ('COMPLEMENTO', 'id_complemento1', 'argumento1'),
            ('COMPLEMENTO2', 'id_complemento2', 'argumento2')
        ]
        
        for campo_csv, id_tag, arg_tag in complementos:
            complemento = self.dados_csv.get(campo_csv, '')
            codigo_complemento = obter_codigo_complemento(complemento)
            argumento = extrair_numero_argumento(complemento)
            
            self._criar_elemento_simples(endereco, id_tag, codigo_complemento)
            self._criar_elemento_simples(endereco, arg_tag, argumento)
        
        # Complemento 3 - agora usando COMPLEMENTO3 do CSV
        if not self.complemento_vazio:
            complemento3 = self.dados_csv.get('COMPLEMENTO3', '')
            if not pd.isna(complemento3) and str(complemento3).strip():
                codigo_complemento3 = obter_codigo_complemento(complemento3)
                argumento3 = extrair_numero_argumento(complemento3)
                self._criar_elemento_simples(endereco, 'id_complemento3', codigo_complemento3)
                self._criar_elemento_simples(endereco, 'argumento3', argumento3)
    
    def _configurar_tecnico_empresa(self):
        """Configura dados do técnico e empresa"""
        tecnico = ET.SubElement(self.edificio, 'tecnico')
        self._criar_elemento_simples(tecnico, 'id', self.valores_padrao['id_tecnico'])
        self._criar_elemento_simples(tecnico, 'nome', self.valores_padrao['nome_tecnico'])
        
        empresa = ET.SubElement(self.edificio, 'empresa')
        self._criar_elemento_simples(empresa, 'id', self.valores_padrao['id_empresa'])
        self._criar_elemento_simples(empresa, 'nome', self.valores_padrao['nome_empresa'])
    
    def _configurar_dados_adicionais(self):
        """Configura dados adicionais do edificio"""
        data_atual = datetime.now().strftime('%Y%m%d%H%M%S')
        self._criar_elemento_simples(self.edificio, 'data', data_atual)
        
        total_ucs = self._obter_valor('QUANTIDADE_UMS', 'total_ucs')
        self._criar_elemento_simples(self.edificio, 'totalUCs', str(total_ucs))
        
        self._criar_elemento_simples(self.edificio, 'ocupacao', "EDIFICACAOCOMPLETA")
        self._criar_elemento_simples(self.edificio, 'numPisos', '1')
        self._criar_elemento_simples(self.edificio, 'destinacao', 'COMERCIO')
    
    def gerar_xml(self):
        """Gera o XML completo"""
        self._configurar_cabecalho()
        self._configurar_coordenadas()
        self._configurar_zona_localidade()
        self._configurar_endereco()
        self._configurar_tecnico_empresa()
        self._configurar_dados_adicionais()
        
        # Converter para string XML
        xml_str = ET.tostring(self.edificio, encoding='UTF-8', method='xml')
        xml_completo = b'<?xml version="1.0" encoding="UTF-8"?>' + xml_str
        
        return xml_completo
