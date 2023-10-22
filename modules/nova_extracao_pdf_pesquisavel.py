
import os
import csv
import json
import shutil
from io import StringIO
from pathlib import Path
from PIL import Image
from pdf2image import convert_from_path
import matplotlib.pyplot as plt

import fitz  # Módulo PyMuPDF
import re
from fuzzywuzzy import fuzz
from unidecode import unidecode
from unicodedata import normalize
import PyPDF2
import logging


from datetime import datetime, timezone, timedelta

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar



nf_data_servico = {}
# 0. Pesquisa PDF
def is_pdf_searchable(pdf_path):
    try:
        pdf_document = fitz.open(pdf_path)
        is_searchable = all(page.get_text("text") != "" for page in pdf_document)
        pdf_document.close()
        return is_searchable
    except Exception as e:
        print(f"Erro ao verificar o PDF: {e}")
        return False

# 1. CABECALHO
def extract_fields_cabecalho(idx, row, row_info, text, original_file_name, debug): 
       
    lista_erros = []
    nf_data_cabecalho = {}
    section = "1. CABECALHO"
    nf_data_cabecalho['secao'] = section
    # nf_data_cabecalho['status_documento'] = 'PREPROCESS_EXTRACT'
    # nf_data_cabecalho['informations'] = " "
    batch_name = row['batch']
    #print(f'\n\n3. dentro da funçao cabecalho: batch_name: {batch_name} text:\n{text}\n\n')
    # try:
    #     # Extrair Nome da Prefeitura
    #     nome_prefeitura_match = re.search(r'PREFEITURA (.+)', text)
    #     if nome_prefeitura_match:
    #         nome_prefeitura = "PREFEITURA " + nome_prefeitura_match.group(1)
    #         nf_data_cabecalho['nome_prefeitura'] = nome_prefeitura
    #     print(f'nome_prefeitura: {nome_prefeitura} - doc: {original_file_name}')        
    # except Exception as e:
    #     msg = (f"doc: {original_file_name} | {e}")
    #     logging.error(f" {batch_name} |  doc: {original_file_name:>25} | setion:{section:20}| erro na extracaçao | {msg }")
    #     nf_data_cabecalho['informations'] = msg
    
    # # Extrair Nome da Prefeitura
    # nome_prefeitura_match = re.search(r'PREFEITURA (.+)', text)
    # if nome_prefeitura_match:
    #     nome_prefeitura = "PREFEITURA " + nome_prefeitura_match.group(1)
    #     nf_data_cabecalho['nome_prefeitura'] = nome_prefeitura

    # try:
    #     # Extrair Tipo de NF
    #     tipo_nf_match = re.search(r'NOTA FISCAL (.+)', text)
    #     if tipo_nf_match:
    #         tipo_nf = "NOTA FISCAL " + tipo_nf_match.group(1)
    #         nf_data_cabecalho['tipo_nota_fiscal'] = tipo_nf
    # except Exception as e:
    #     msg = (f"doc: {original_file_name} | {e}")
    #     logging.error(f" {batch_name} |  doc: {original_file_name:>25} | setion:{section:20} | erro na extracaçao | {msg }")
        
        


    # # Extrair Tipo de NF
    # tipo_nf_match = re.search(r'NOTA FISCAL (.+)', text)
    # if tipo_nf_match:
    #     tipo_nf = "NOTA FISCAL " + tipo_nf_match.group(1)
    #     nf_data_cabecalho['tipo_nota_fiscal'] = tipo_nf
    
    # Extrair Número da Nota
    try:
        numero_nota_match = re.search(r'Número da Nota:\s+(\d+)', text)
        if numero_nota_match:
            nr_nro_nf = numero_nota_match.group(1)
            nf_data_cabecalho['numero_nota_fiscal'] = numero_nota_match.group(1)
            print(f'nr_nro_nf: {nr_nro_nf} - doc: {original_file_name}')
    except Exception as e:
        msg = (f"doc: {original_file_name} | {e}")
        lista_erros.append(msg)
        nf_data_cabecalho['numero_nota_fiscal'] = None
        # nf_data_cabecalho['status_documento'] = 'NO_PROCESS'
        # nf_data_cabecalho['informations'] = msg
              

    # Extrair Competência
    competencia_match = re.search(r'Competência:\s+(.+)', text)
    if competencia_match:
        nf_data_cabecalho['competencia'] = competencia_match.group(1)

    # Extrair Data e Hora de Emissão
    data_emissao_match = re.search(r'Data e Hora da Emissão:\s+(.+)', text)
    if data_emissao_match:
        nf_data_cabecalho['dt_hr_emissao'] = data_emissao_match.group(1)
        
    # Extrair Data e Hora de Emissão
    codigo_verificacao_match = re.search(r'Código Verificação:\s+(.+)', text)
    if codigo_verificacao_match:
        nf_data_cabecalho['codigo_verificacao'] = codigo_verificacao_match.group(1) 
    
    print(f'5. dentro da funcao: \n\n{nf_data_cabecalho}\n\n')    
        
    return nf_data_cabecalho





# 2. PRESTADOR DE SERVIÇO
def extract_fields_prestador(text): # Função para extrair campos e valores dentro de um retângulo
    nf_data_prestador = {}
    
    nf_data_prestador['secao'] = "2. PRESTADOR DE SERVIÇO"
    
    
    # Extrair CPF/CNPJ com máscara 1
    if "CPF/CNPJ:" in text:
        cpf_cnpj_formatado_match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', text)
        if cpf_cnpj_formatado_match:
                        nf_data_prestador['p_cpf_cnpj_com_mascara'] = cpf_cnpj_formatado_match.group(1)
                        nf_data_prestador['p_cpf_cnpj_sem_mascara'] = re.sub(r'\D', '', cpf_cnpj_formatado_match.group(1))

    # Extrair Inscrição Municipal
    inscricao_municipal_match = re.search(r'Inscrição Municipal:\s+(.+)', text)
    if inscricao_municipal_match:
        nf_data_prestador['p_inscricao_municipal'] = inscricao_municipal_match.group(1)
        
               
    # Extrair Inscrição Estadual
    #if "Inscrição Estadual:" in text:
    
    # Extrair Inscrição Estadual
    inscricao_estadual_match = re.search(r'Inscrição Estadual:\s+(.+)', text)
    if inscricao_estadual_match:
        inscricao_estadual_str = inscricao_estadual_match.group(1)
        if inscricao_estadual_str == 'Nome/Razão Social:':
            nf_data_prestador['p_inscricao_estadual'] = "NONE"
        else:    
            nf_data_prestador['p_inscricao_estadual'] = inscricao_estadual_match.group(1)       
        
                
    

    # Extrair Telefone
    #telefone_match = re.search(r'Telefone:\s+([0-9.\s-])', text)
    telefone_match = re.search(r'Telefone:\s+([0-9.\s-]+)', text)
    if telefone_match: 
        telefone_str = telefone_match.group(1)
        # Remover quebras de linha
        telefone_str = telefone_str.replace('.', '')
        telefone_str = telefone_str.replace('\n', '')
                
        nf_data_prestador['p_telefone'] = telefone_str
    else:
        nf_data_prestador['p_telefone'] = "NONE"

         
                
    # Nome/Razão Social:
    razao_social_match = re.search(r'Nome/Razão Social:\s+(.+)', text)
    if razao_social_match:
        nf_data_prestador['p_razao_social'] = razao_social_match.group(1)  
                
    # Nome de Fantasia:
    nome_fantasia_match = re.search(r'Nome de Fantasia:\s+(.+)', text)
    if nome_fantasia_match:
        nf_data_prestador['p_nome_fantasia'] = nome_fantasia_match.group(1)                                    
                
            
    # Endereço:
    endereco_match = re.search(r'Endereço:\s+(.+)', text)
    if endereco_match:
        nf_data_prestador['p_endereco'] = endereco_match.group(1) 
    
    # E-mail:
    email_match = re.search(r'E-mail:\s+(.+)', text)
    if email_match:
        nf_data_prestador['p_email'] = email_match.group(1)  
    else:
        nf_data_prestador['p_email'] = "NONE"  # Valor padrão quando não há correspondência
   
        

    return nf_data_prestador

# 3. TOMADOR DE SERVIÇO
def extract_fields_tomador(text):
    nf_data_tomador = {}
    
    
    nf_data_tomador['secao'] = "3. TOMADOR DE SERVIÇO"
    
    try:
        # Extrair CPF/CNPJ com máscara 1
        if "CPF/CNPJ:" in text:
            cpf_cnpj_formatado_match = re.search(r'(\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2})', text)
            if cpf_cnpj_formatado_match:
                nf_data_tomador['t_cpf_cnpj_com_mascara'] = cpf_cnpj_formatado_match.group(1)
                nf_data_tomador['t_cpf_cnpj_sem_mascara'] = re.sub(r'\D', '', cpf_cnpj_formatado_match.group(1))
    except Exception as e:
        print(f"Erro ao verificar o PDF: {e}")
        
    # Extrair RG    
    rg_match = re.search(r'RG:\s+(.+)', text)   
    if rg_match:
        rg_str = rg_match.group(1)
        if rg_str == 'Telefone:':
            nf_data_tomador['t_rg'] = "NONE"  # Valor padrão quando não há correspondência
        else:    
            nf_data_tomador['t_rg'] = rg_match.group(1)  
 
        
    # Extrair Telefone
    telefone_match = re.search(r'Telefone:\s+(.+)', text)
    if telefone_match:
        telefone_str = telefone_match.group(1)
        if telefone_str == 'Inscrição Estadual:':
            nf_data_tomador['t_telefone'] = "NONE"  # Valor padrão quando não há correspondência
        else:    
            nf_data_tomador['t_telefone'] = telefone_match.group(1)
     

    # Extrair Inscrição Municipal
    inscricao_municipal_match = re.search(r'Inscrição Municipal:\s+(.+)', text)
    if inscricao_municipal_match:
        nf_data_tomador['t_inscricao_municipal'] = inscricao_municipal_match.group(1)
    else:
        nf_data_tomador['t_inscricao_municipal'] = None
                
                
                
    # Extrair Inscrição Estadual
    inscricao_estadual_match = re.search(r'Inscrição Estadual:\s+(.+)', text)
    if inscricao_estadual_match:
        inscricao_estadual_str = inscricao_estadual_match.group(1)
        if inscricao_estadual_str == 'Nome/Razão Social:':
            nf_data_tomador['t_inscricao_estadual'] = None
        else:    
            nf_data_tomador['t_inscricao_estadual'] = inscricao_estadual_match.group(1)   
                
    
    # Nome/Razão Social:
    razao_social_match = re.search(r'Nome/Razão Social:\s+(.+)', text)
    if razao_social_match:
        nf_data_tomador['t_razao_social'] = razao_social_match.group(1)                                                
                
    # Endereço:
    endereco_match = re.search(r'Endereço:\s+(.+)', text)
    if endereco_match:
        nf_data_tomador['t_endereco'] = endereco_match.group(1)
    else:
        nf_data_tomador['t_endereco'] = None
             
    
    # E-mail:
    email_match = re.search(r'E-mail:\s+(.+)', text)
    if email_match:
        nf_data_tomador['t_email'] = email_match.group(1) 
    else:
        nf_data_tomador['t_email'] = "NONE"  # Valor padrão quando não há correspondência    

    return nf_data_tomador

# 7. VALORES E IMPOSTOS
def extract_fields_impostos(text):
    nf_data_valores = {}
    nf_data_valores['secao'] = "7. VALORES E IMPOSTOS"
    
    # Extrair VALOR SERVIÇOS:
    valor_servicos_match = re.search(r'VALOR SERVIÇOS:\s+(.+)', text)
    if valor_servicos_match:
        valor_servicos_str = valor_servicos_match.group(1)
        valor_servicos_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_servicos_str)
        if valor_servicos_sem_formato:
            valor_servicos_sem_formatacao = valor_servicos_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['valor_servicos'] = float(valor_servicos_sem_formatacao)
        else:
            nf_data_valores['valor_servicos'] = 0.0  # Valor não encontrado ou não está no formato esperado
  
  
    # Extrair VALOR DEDUÇÃO:
    valor_deducao_match = re.search(r'DEDUÇÃO:\s+(.+)', text)
    if valor_deducao_match:
        valor_deducao_str = valor_deducao_match.group(1)
        valor_deducao_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_deducao_str)
        if valor_deducao_sem_formato:
            valor_deducao_sem_formato = valor_deducao_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['valor_deducao'] = float(valor_deducao_sem_formato)
        else:
            nf_data_valores['valor_deducao'] = 0.0  # Valor não encontrado ou não está no formato esperado
        
        
    # Extrair DESC. INCOND:
    valor_desc_match = re.search(r'DESC. INCOND:\s+(.+)', text)
    if valor_desc_match:
        valor_desc_str = valor_desc_match.group(1)
        valor_desc_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_desc_str)
        if valor_desc_sem_formato:
            valor_desc_sem_formato = valor_desc_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['desc_incond'] = float(valor_desc_sem_formato)
        else:
            nf_data_valores['desc_incond'] = 0.0  # Valor não encontrado ou não está no formato esperado        
        

    # Extrair BASE DE CÁLCULO:
    valor_calculo_match = re.search(r'CÁLCULO:\s+(.+)', text)
    if valor_calculo_match:
        valor_calculo_str = valor_calculo_match.group(1)
        valor_calculo_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_calculo_str)
        if valor_calculo_sem_formato:
            valor_calculo_sem_formato = valor_calculo_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['base_calculo'] = float(valor_calculo_sem_formato)
        else:
            nf_data_valores['base_calculo'] = 0.0  # Valor não encontrado ou não está no formato esperado    



    # Extrair ALÍQUOTA:
    valor_aliquota_match = re.search(r'ALÍQUOTA:\s+(.+)', text)
    if valor_aliquota_match:
        valor_aliquota_str = valor_aliquota_match.group(1)
        valor_aliquota_sem_formato = re.search(r'([\d.,]+)%', valor_aliquota_str)  # Ajuste aqui
        if valor_aliquota_sem_formato:
            valor_aliquota_sem_formato = valor_aliquota_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['aliquota'] = float(valor_aliquota_sem_formato)
        else:
            nf_data_valores['aliquota'] = 0.0  # Valor não encontrado ou não está no formato esperado


    # Extrair VALOR ISS:
    valor_iss_match = re.search(r'VALOR ISS:\s+(.+)', text)
    if valor_iss_match:
        valor_iss_str = valor_iss_match.group(1)
        valor_iss_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_iss_str)
        if valor_iss_sem_formato:
            valor_iss_sem_formato = valor_iss_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['valor_iss'] = float(valor_iss_sem_formato)
        else:
            nf_data_valores['valor_iss'] = 0.0  # Valor não encontrado ou não está no formato esperado 

    # Extrair VALOR ISS RETIDO:
    valor_iss_retido_match = re.search(r'RETIDO:\s+(.+)', text)
    if valor_iss_match:
        valor_iss_retido_str = valor_iss_retido_match.group(1)
        valor_iss_retido_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_iss_retido_str)
        if valor_iss_retido_sem_formato:
            valor_iss_retido_sem_formato = valor_iss_retido_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['valor_iss_retido'] = float(valor_iss_retido_sem_formato)
        else:
            nf_data_valores['valor_iss_retido'] = 0.0  # Valor não encontrado ou não está no formato esperado 

    # Extrair VALOR DESC. COND:
    valor_desc_cond_match = re.search(r'DESC. COND:\s+(.+)', text)
    if valor_desc_cond_match:
        valor_desc_cond_str = valor_desc_cond_match.group(1)
        valor_desc_cond_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_desc_cond_str)
        if valor_desc_cond_sem_formato:
            valor_desc_cond_sem_formato = valor_desc_cond_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['desc_cond'] = float(valor_desc_cond_sem_formato)
        else:
            nf_data_valores['desc_cond'] = 0.0  # Valor não encontrado ou não está no formato esperado
    
    # Extrair VALOR PIS:
    valor_pis_match = re.search(r'VALOR PIS:\s+(.+)', text)
    if valor_pis_match:
        valor_pis_str = valor_pis_match.group(1)
        valor_pis_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_pis_str)
        if valor_pis_sem_formato:
            valor_pis_sem_formato = valor_pis_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['valor_pis'] = float(valor_pis_sem_formato)
        else:
            nf_data_valores['valor_pis'] = 0.0  # Valor não encontrado ou não está no formato esperado
    
    # Extrair VALOR COFINS:
    valor_cofins_match = re.search(r'VALOR COFINS:\s+(.+)', text)
    if valor_cofins_match:
        valor_cofins_str = valor_cofins_match.group(1)
        valor_cofins_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_cofins_str)
        if valor_cofins_sem_formato:
            valor_cofins_sem_formato = valor_cofins_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['valor_cofins'] = float(valor_cofins_sem_formato)
        else:
            nf_data_valores['valor_cofins'] = 0.0  # Valor não encontrado ou não está no formato esperado
            
    # Extrair VALOR IR:
    valor_ir_match = re.search(r'VALOR IR:\s+(.+)', text)
    if valor_ir_match:
        valor_ir_str = valor_ir_match.group(1)
        valor_ir_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_ir_str)
        if valor_ir_sem_formato:
            valor_ir_sem_formato = valor_ir_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['valor_ir'] = float(valor_ir_sem_formato)
        else:
            nf_data_valores['valor_ir'] = 0.0  # Valor não encontrado ou não está no formato esperado
            
    # Extrair VALOR INSS:
    valor_inss_match = re.search(r'VALOR INSS:\s+(.+)', text)
    if valor_inss_match:
        valor_inss_str = valor_inss_match.group(1)
        valor_inss_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_inss_str)
        if valor_inss_sem_formato:
            valor_inss_sem_formato = valor_inss_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['valor_inss'] = float(valor_inss_sem_formato)
        else:
            nf_data_valores['valor_inss'] = 0.0  # Valor não encontrado ou não está no formato esperado
            
    # Extrair VALOR CSLL:
    valor_csll_match = re.search(r'VALOR CSLL:\s+(.+)', text)
    if valor_csll_match:
        valor_csll_str = valor_csll_match.group(1)
        valor_csll_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_csll_str)
        if valor_csll_sem_formato:
            valor_csll_sem_formato = valor_csll_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['valor_csll'] = float(valor_csll_sem_formato)
        else:
            nf_data_valores['valor_csll'] = 0.0  # Valor não encontrado ou não está no formato esperado
    
    # Extrair OUTRAS RETENÇÕES:
    outras_retencoes_match = re.search(r'OUTRAS RETENÇÕES:\s+(.+)', text)
    if outras_retencoes_match:
        outras_retencoes_str = outras_retencoes_match.group(1)
        outras_retencoes_sem_formato = re.search(r'R\$\s*([\d.,]+)', outras_retencoes_str)
        if outras_retencoes_sem_formato:
            outras_retencoes_sem_formato = outras_retencoes_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['outras_retencoes'] = float(outras_retencoes_sem_formato)
        else:
            nf_data_valores['outras_retencoes'] = 0.0  # Valor não encontrado ou não está no formato esperado
    
    
    # Extrair VALOR LÍQUIDO:
    valor_liquido_match = re.search(r'VALOR LÍQUIDO:\s+(.+)', text)
    if valor_liquido_match:
        valor_liquido_str = valor_liquido_match.group(1)
        valor_liquido_sem_formato = re.search(r'R\$\s*([\d.,]+)', valor_liquido_str)
        if valor_liquido_sem_formato:
            valor_liquido_sem_formato = valor_liquido_sem_formato.group(1).replace('.', '').replace(',', '.').strip()
            nf_data_valores['valor_liquido'] = float(valor_liquido_sem_formato)
        else:
            nf_data_valores['valor_liquido'] = 0.0  # Valor não encontrado ou não está no formato esperado
        

    return nf_data_valores


# 9. OUTRAS INFORMAÇOES / CRITICAS
def extract_fields_outras_info(text):
    nf_data_outras_informacoes = {}
    #nf_data_outras_informacoes['secao'] = "9. OUTRAS INFORMAÇOES / CRITICAS"
    
    # Extrair EXIGIBILIDADE ISS:
    exigibilidade_iss_match = re.search(r'EXIGIBILIDADE ISS\s+(.+)', text)
    if exigibilidade_iss_match:
        exigibilidade_iss_value = exigibilidade_iss_match.group(1).strip()
        nf_data_outras_informacoes['exigibilidade_iss'] = exigibilidade_iss_value
        
    # Extrair REGIME TRIBUTAÇÃO:
    regime_tributacao_match = re.search(r'REGIME TRIBUTAÇÃO\s+(.+)', text)
    if regime_tributacao_match:
        regime_tributacao_value = regime_tributacao_match.group(1).strip()
        nf_data_outras_informacoes['regime_tributacao'] = regime_tributacao_value
    
    # Extrair SIMPLES NACIONAL:
    simples_nacional_match = re.search(r'SIMPLES NACIONAL\s+(.+)', text)
    if simples_nacional_match:
        simples_nacional_value = simples_nacional_match.group(1).strip()
        nf_data_outras_informacoes['simples_nacional'] = simples_nacional_value
        
        
    # Extrair ISSQN RETIDO:
    local_prestacao_servico_match = re.search(r'ISSQN RETIDO\s+(.+)', text)
    if local_prestacao_servico_match:
        local_prestacao_servico_value = local_prestacao_servico_match.group(1).strip()
        nf_data_outras_informacoes['issqn_retido'] = local_prestacao_servico_value        
        
    
    # Extrair LOCAL PRESTAÇÃO SERVIÇO:
    local_prestacao_servico_match = re.search(r'LOCAL\. PRESTAÇÃO\s+SERVIÇO\s+(.+)', text)
    if local_prestacao_servico_match:
        local_prestacao_servico_value = local_prestacao_servico_match.group(1).strip()
        nf_data_outras_informacoes['local_prestacao_servico'] = local_prestacao_servico_value
    
    
    
    # Extrair LOCAL INCIDÊNCIA:
    local_incidencia_match = re.search(r'LOCAL INCIDÊNCIA\s+(.+)', text)
    if local_incidencia_match:
        local_incidencia_value = local_incidencia_match.group(1).strip()
        nf_data_outras_informacoes['local_incidencia'] = local_incidencia_value
   
    
    return nf_data_outras_informacoes
