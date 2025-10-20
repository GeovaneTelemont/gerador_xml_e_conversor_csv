import pandas as pd
import xml.etree.ElementTree as ET
from datetime import datetime
from ..utils import formatar_coordenada, obter_codigo_complemento, extrair_numero_argumento

def criar_xml_edificio_ccomplementos(dados_csv, numero_pasta, complemento_vazio):
    edificio = ET.Element('edificio')
    edificio.set('tipo', 'M')
    edificio.set('versao', '7.9.2')
    ET.SubElement(edificio, 'gravado').text = 'false'
    ET.SubElement(edificio, 'nEdificio').text = dados_csv['COD_SURVEY']
    latitude = formatar_coordenada(dados_csv['LATITUDE'])
    longitude = formatar_coordenada(dados_csv['LONGITUDE'])
    ET.SubElement(edificio, 'coordX').text = str(longitude)
    ET.SubElement(edificio, 'coordY').text = str(latitude)
    codigo_zona = str(dados_csv['COD_ZONA']) if 'COD_ZONA' in dados_csv and not pd.isna(dados_csv['COD_ZONA']) else 'DF-GURX-ETGR-CEOS-68'
    ET.SubElement(edificio, 'codigoZona').text = codigo_zona
    ET.SubElement(edificio, 'nomeZona').text = codigo_zona
    localidade = str(dados_csv['LOCALIDADE']) if 'LOCALIDADE' in dados_csv and not pd.isna(dados_csv['LOCALIDADE']) else 'GUARA'
    ET.SubElement(edificio, 'localidade').text = localidade
    endereco = ET.SubElement(edificio, 'enderecoEdificio')
    ET.SubElement(endereco, 'id').text = str(dados_csv['ID_ENDERECO']) if 'ID_ENDERECO' in dados_csv and not pd.isna(dados_csv['ID_ENDERECO']) else '93128133'
    logradouro = str(dados_csv['LOGRADOURO'] +", "+ dados_csv['BAIRRO']+", "+dados_csv['MUNICIPIO']+", "+dados_csv['LOCALIDADE']+" - "+ dados_csv["UF"]+ f" ({dados_csv['COD_LOGRADOURO']})" )
    ET.SubElement(endereco, 'logradouro').text = logradouro
    num_fachada = str(dados_csv['NUM_FACHADA']) if 'NUM_FACHADA' in dados_csv and not pd.isna(dados_csv['NUM_FACHADA']) else 'SN'
    ET.SubElement(endereco, 'numero_fachada').text = num_fachada
    complemento1 = dados_csv['COMPLEMENTO'] if 'COMPLEMENTO' in dados_csv else ''
    codigo_complemento1 = obter_codigo_complemento(complemento1)
    argumento1 = extrair_numero_argumento(complemento1)
    ET.SubElement(endereco, 'id_complemento1').text = codigo_complemento1
    ET.SubElement(endereco, 'argumento1').text = argumento1
    complemento2 = dados_csv['COMPLEMENTO2'] if 'COMPLEMENTO2' in dados_csv else ''
    codigo_complemento2 = obter_codigo_complemento(complemento2)
    argumento2 = extrair_numero_argumento(complemento2)
    ET.SubElement(endereco, 'id_complemento2').text = codigo_complemento2
    ET.SubElement(endereco, 'argumento2').text = argumento2

    # Só adiciona complemento3 se não estiver vazio
    if complemento_vazio == False:
        complemento3 = dados_csv['RESULTADO'] if 'RESULTADO' in dados_csv else ''
        if not pd.isna(complemento3) and str(complemento3).strip() != '':
            codigo_complemento3 = obter_codigo_complemento(complemento3)
            argumento3 = extrair_numero_argumento(complemento3)
            ET.SubElement(endereco, 'id_complemento3').text = codigo_complemento3
            ET.SubElement(endereco, 'argumento3').text = argumento3

    cep = str(dados_csv['CEP']) if 'CEP' in dados_csv and not pd.isna(dados_csv['CEP']) else '71065071'
    ET.SubElement(endereco, 'cep').text = cep
    bairro = str(dados_csv['BAIRRO']) if 'BAIRRO' in dados_csv and not pd.isna(dados_csv['BAIRRO']) else localidade
    ET.SubElement(endereco, 'bairro').text = bairro
    ET.SubElement(endereco, 'id_roteiro').text = str(dados_csv['ID_ROTEIRO']) if 'ID_ROTEIRO' in dados_csv and not pd.isna(dados_csv['ID_ROTEIRO']) else '57149008'
    ET.SubElement(endereco, 'id_localidade').text = str(dados_csv['ID_LOCALIDADE']) if 'ID_LOCALIDADE' in dados_csv and not pd.isna(dados_csv['ID_LOCALIDADE']) else '1894644'
    cod_lograd = str(dados_csv['COD_LOGRADOURO']) if 'COD_LOGRADOURO' in dados_csv and not pd.isna(dados_csv['COD_LOGRADOURO']) else '2700035341'
    ET.SubElement(endereco, 'cod_lograd').text = cod_lograd
    tecnico = ET.SubElement(edificio, 'tecnico')
    ET.SubElement(tecnico, 'id').text = '1828772688'
    ET.SubElement(tecnico, 'nome').text = 'NADIA CAROLINE'
    empresa = ET.SubElement(edificio, 'empresa')
    ET.SubElement(empresa, 'id').text = '42541126'
    ET.SubElement(empresa, 'nome').text = 'TELEMONT'
    data_atual = datetime.now().strftime('%Y%m%d%H%M%S')
    ET.SubElement(edificio, 'data').text = data_atual
    total_ucs = int(dados_csv['QUANTIDADE_UMS']) if 'QUANTIDADE_UMS' in dados_csv and not pd.isna(dados_csv['QUANTIDADE_UMS']) else 1
    ET.SubElement(edificio, 'totalUCs').text = str(total_ucs)
    ET.SubElement(edificio, 'ocupacao').text = "EDIFICACAOCOMPLETA"
    ET.SubElement(edificio, 'numPisos').text = '1'
    ET.SubElement(edificio, 'destinacao').text = 'COMERCIO'
    xml_str = ET.tostring(edificio, encoding='UTF-8', method='xml')
    xml_completo = b'<?xml version="1.0" encoding="UTF-8"?>' + xml_str
    return xml_completo 
