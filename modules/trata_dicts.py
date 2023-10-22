
import os
import sys
import shutil
import platform
from io import StringIO
from pathlib import Path
from urllib import response

from outlook_msg import Message
import extract_msg
import zipfile
from pyunpack import Archive
import py7zr


import csv
import json
import pandas as pd


import locale
import time, copy
from pytz import timezone
from datetime import datetime, timezone, timedelta

import cv2
import fitz  # Módulo PyMuPDF
from PIL import Image
from PIL import ImageFont
from PIL import Image, ImageDraw
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import matplotlib.pyplot as plt
from pdf2image import convert_from_path

import pytesseract

import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle





# # Mapeando prefeitura e CNAE para a descrição do CNAE
# cnae_dict = dict(zip(zip(cnae_x_item_servico_df['PREFE'], cnae_x_item_servico_df['CNA_NUMERO']), cnae_x_item_servico_df['CNA_NOME']))

# # Mapeando prefeitura e item de serviço para a descrição do item de serviço e o CNAE associado
# item_servico_dict = dict(zip(zip(cnae_x_item_servico_df['PREFE'], cnae_x_item_servico_df['ATV_CODIGO']), zip(cnae_x_item_servico_df['ATV_DESCRICAO'], cnae_x_item_servico_df['CNA_NUMERO'])))


# 2. XXX  Tratando o CNAE com dict criado
def processa_cnae_dict(Texto_extraido, de_para_pm, debug):

    text_splited = Texto_extraido.split('\n')
    # Processando CNAE
    cnae_lines = [line for line in text_splited if 'CNAE' in line]

    if cnae_lines:
        cnae_line = cnae_lines[0]
        #print(f'cnae_line: {cnae_line}')
        
        cnae_number = int(extract_number(cnae_line))
        
        cnae_value = cnae_dict.get((de_para_pm, cnae_number),("Valor não encontrado"))
        if cnae_value != "Valor não encontrado":
            cnae_value = cnae_value.upper()
            cnae_value = str(cnae_number) + " - " + cnae_value
            return cnae_value
        else:
            return None
    else:
        cnae_value = processa_cnae_outros(Texto_extraido)
        cnae_number = int(extract_number(cnae_value))

        cnae_value = cnae_dict.get((de_para_pm, cnae_number),("Valor não encontrado"))
        if cnae_value != "Valor não encontrado":
            cnae_value = cnae_value.upper()
            cnae_value = str(cnae_number) + " - " + cnae_value
            return cnae_value
        else:
            return None

     

# 3. XXX  Tratando Item de Servico com dict criado
def processa_itens_servico_dict(Texto_extraido, de_para_pm, debug):
    
    text_splited = Texto_extraido.split('\n')
    # Encontrando a linha que contém o texto desejado
    item_servico_lines = [line for line in text_splited if 'Item da Lista de Serviços' in line]
    #print(f'item_servico_lines (fora do if): {item_servico_lines}')
    # Verificando se encontramos uma linha válida
    if item_servico_lines:
        #print(f'item_servico_lines: {item_servico_lines}')
        item_servico_line = item_servico_lines[0]
        item_servico_cod = float(extract_number(item_servico_line))
        item_servico, cnae_associado = item_servico_dict.get((de_para_pm, item_servico_cod), ("Valor não encontrado", None))
        item_servico = item_servico.upper()
        item_servico_value = str(item_servico_cod) + " - " + item_servico
        return item_servico_value
    
    else:
        #print("Linha com 'Item da Lista de Serviços' não encontrada")
        item_servico_line = processa_item_sevico_outros(Texto_extraido)
        if item_servico_line:
            item_servico_cod = float(extract_number(item_servico_line))
            item_servico, cnae_associado = item_servico_dict.get((de_para_pm, item_servico_cod), ("Valor não encontrado", None))
            item_servico = item_servico.upper()
            item_servico_value = str(item_servico_cod) + " - " + item_servico
            return item_servico_value
        
        else:
            return None
        #return None


def define_rotulo_acao(nome_arquivo, debug):
    
    for palavra_chave, rotulo in mapeamento_palavras_chave.items():
        if palavra_chave.lower() in nome_arquivo.lower():
            break
    else:
        rotulo = 'prov_nota_fiscal' #"sem_rotulo"
        palavra_chave = 'default'
        acao_sugerida = sugestoes_acao.get(rotulo, 'None')
        return palavra_chave, rotulo, acao_sugerida
        # palavra_chave = 'None' #"sem_palavra_chave"
        # acao_sugerida = 'None' #"sem_acao_sugerida"
        
        return palavra_chave, rotulo, acao_sugerida
        #print(f'nome_arquivo: {nome_arquivo} | rotulo: {rotulo}')
    if rotulo != 'None': #"sem_rotulo"
        acao_sugerida = sugestoes_acao.get(rotulo, 'None') # "Ação não definida"
        return palavra_chave, rotulo, acao_sugerida
