import os
import sys
import shutil
import platform
from io import StringIO
from pathlib import Path
from urllib import response

#import cv2
import fitz  # Módulo PyMuPDF
from PIL import Image
from PIL import ImageFont
from PIL import Image, ImageDraw
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar
import matplotlib.pyplot as plt
from pdf2image import convert_from_path

import PyPDF2


# 2. XXX Analisa nro de paginas
def analisa_nro_pages(file_path):
    
    pdf_document = fitz.open(file_path)
    pages = pdf_document.pages() # generator object

    page_nro = []
    for page in pages:
        page_nro.append(page)
        
    nro_paginas = len(page_nro)    
    if nro_paginas > 1:
        doc_1_page = False
        return doc_1_page, nro_paginas    
    else:
        doc_1_page = True
        return doc_1_page, nro_paginas  
    pdf_document.close()
    
    
    # XXX FUNCAO DE SPLIT
def split_documentos(qualquer_df, fase, atividade, status):
    
    documentos_splitados = []
    doc_info = {}
    rows_list = []
    documentos = []
    #output_dir = os.path.join(documentos_scan_path, batch_name)
    num_linhas_df = qualquer_df.shape[0]

    i = num_linhas_df + 1
    for idx, row in qualquer_df.iterrows():
        message_erro = []
        nun_pages = row['pages']
        batch_name = row['batch']
        original_file_name = row['original_file_name']
        folder_name = row['directory']
        file_path = row['file_path']
        level = row['level']
        document_type = row['document_type']
        doc_action = row['doc_action']
        document_unique_id = idx
        new_level = level + 1
        
        if (doc_action == 'splitar') and (status == 'root_analise'):
            if nun_pages > 1:
                try:
                    pdf = fitz.open(file_path)
                    # Número total de páginas no PDF
                    total_pages = len(pdf)
                except Exception as e:
                    print(f"Nao congui abrir o PDF: {e}")    

                # Nome base para os arquivos de saída
                base_name = file_path.split('.')[0]  # Remove a extensão do arquivo
                file_to_delete = file_path
                # Loop para criar um novo PDF para cada página
                for page_num in range(total_pages):
                    # Cria um novo objeto PDF
                    new_pdf = fitz.open()
                    # Adiciona a página atual ao novo PDF
                    new_pdf.insert_pdf(pdf, from_page=page_num, to_page=page_num)
                    # Nome do novo arquivo PDF
                    new_pdf_name = f"{base_name}_page_{page_num + 1}.pdf"
                    # Salva o novo PDF
                    new_pdf.save(new_pdf_name)
                    # Fecha o novo PDF
                    new_pdf.close()
                    rotulo = "prov_nota_fiscal"
                    acao_sugerida = sugestoes_acao.get(rotulo, "no_defined_action")
                    acao_executada = "novo_doc_criado"
                    informations = (f'documento criado a partir do split do documento: {original_file_name}')  
                    name_pdf_splited = os.path.basename(new_pdf_name)

                    new_row = {
                        "seq": i,
                        "date_time": cron.timenow_pt_BR(),
                        "batch": batch_name,
                        "fase_processo": fase,
                        "nome_atividade": atividade,
                        "status_documento": status,
                        "acao_executada": acao_executada,
                        "original_file_name": new_pdf_name,
                        "directory": folder_name,
                        "one_page": True,
                        "pages": 1,
                        "document_type": rotulo,
                        "doc_action": acao_sugerida,
                        "level": level,
                        "document_unique_id": generate_unique_id(),
                        "parent_document_unique_id": document_unique_id,
                        "file_hash": generate_file_hash(file_path),
                        "file_path": file_path,
                        "informations": informations,
                    }
                    rows_list.append(new_row)
                    i += 1
                qualquer_df.loc[idx, 'status_documento'] = "NAO_PROCESSAR" 
                qualquer_df.loc[idx, 'informations'] = "Paginas splitada em multiplos documentos" 
                qualquer_df.loc[idx, 'date_time'] = cron.timenow_pt_BR() 
    
    total_split = i - 1        
    df_split = pd.DataFrame(rows_list)
    
    
    return df_split, rows_list




def confirma_pdf_pesquisavel(file_path):
    
    pdf_document = fitz.open(file_path)
    # Página do PDF  ATENCAO  (UNICA PAGINA)
    page_number = 0  # Defina o número da página que deseja analisar
    page = pdf_document[page_number]
    # Definir retângulo de interesse
    try:
        x0 = 0
        y0 = 4
        x1 = 600
        y1 = 200  # Ajuste este valor para delimitar a região vertical
        # Extrair texto dentro do retângulo
        text = page.get_text("text", clip=(x0, y0, x1, y1))
        if text:
            page_number = 0
            pdf_pequisavel = True
        #print(page_number)
        else:
            page_number = 1
            pdf_pequisavel = False
        #print(page_number)
    except Exception as e:
        msg_error = (f"Erro ao abrir pagina do PDF: {e}")
        pdf_pequisavel = False
        pdf_document.close()   
         
        return pdf_pequisavel