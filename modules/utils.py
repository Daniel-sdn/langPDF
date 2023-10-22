# ------------------------------------------------------------------------------
# Copyright 2023, Daniel Silva do Nascimento, mailto:danielsdn0725@gmail.com
#
# Relacao deferramentas utilizadas na aplicacao
#
# Part of "extractNF" project, a Python solution for extracting data from NFS-e
# for Modernizaçao Informatica
# -------------------------------------------------------------------------------

import re
import io
import os
import csv
import json
import uuid
import hashlib
import shutil
import pandas as pd
from pathlib import Path
from urllib import response
from unicodedata import normalize
from icecream import ic




def generate_file_hash(file_path):
    """ Criar hash SHA-256 para um arquivo
        se o arquivo for renomeado, seu hash se mantera
        entretanto qualquer muudança no conteúdo do arquivo
        modificara seu hash
    """
    
    with open(file_path, "rb") as f:
        file_data = f.read()
        file_hash = hashlib.sha256(file_data).hexdigest()
    return file_hash


def generate_unique_id():
    return str(uuid.uuid4())



def busca_proximo_batch(conf_export_plan_path):
    # Abre o arquivo Excel e lê a coluna 'batch'
    df = pd.read_excel(conf_export_plan_path, usecols=["batch"])
    # Pega o último valor da coluna 'batch'
    last_value = df.iloc[-1, 0]
    
    # Extraí o número do último batch e adiciona 1 para o próximo
    last_number = int(last_value.split("_")[1])
    next_number = last_number + 1
    
    # Forma o nome do próximo batch
    next_batch = f"Batch_{next_number}"
    
    return next_batch    

# 4. Função para verificar e criar a pasta se não existir
def check_and_create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)



def apagar_zone(documentos_extracao_path):
    # Para apagar arquivos PDF:Zone
    for root, dirs, files in os.walk(documentos_extracao_path):
        folder_name = os.path.basename(root)
        for file in files:
            file_path = os.path.join(root, file)
            #print(file)
            if ":Zone" in file:
                file_to_delete = file_path
                os.remove(file_to_delete)
                #print(file, "termina, pode eliminar")
                
                
             


# 7. funçao que MOVE documentos e gera add_log_transaction_entry para df_log_transctions
def move_doc_processed_file(batch_name, src_path, tgt_path):
    
    function = "move_doc_processed_file"
    source_path = src_path
    file = os.path.basename(source_path)
    sub_dir = os.path.join(tgt_path, batch_name)
    destination_path = os.path.join(sub_dir, file)
    document_action = "move_processed_file"
    transaction_detail = (f'document {file} moved by: {function}')
    df_move = pd.DataFrame()
    try:
        document_unique_id = get_document_id_by_file(batch_name, file)
        check_and_create_folder(destination_path)
        shutil.move(source_path, destination_path)
        sucess = True
        move_log = add_log_transaction_entry(document_unique_id, batch_name, file, document_action, src_path, tgt_path, transaction_detail, sucess)
    except Exception as e:
        print(f"Erro ao mover documento: {e}")
        sucess = False
    
    return move_log   


# XXX Usando na criacao da imagem 
def conv_filename_no_ext(title):
    
    # Divida o título em nome e extensão (mas ignore a extensão)
    name = title.rsplit('.', 1)[0] if '.' in title else title

    # Remova acentos e caracteres especiais do nome
    name = normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    
    # Substitua espaços e hífens por sublinhados
    filename = name.replace(' ', '_').replace('-', '_')

    # Remova quaisquer outros caracteres não alfanuméricos, exceto sublinhados
    filename = re.sub(r'[^\w_]', '', filename)

    # Converter para minúsculas
    filename = filename.lower()

    return filename 








def filtrar_df(df, **kwargs):
    query = " & ".join(f"{key} == @kwargs['{key}']" for key in kwargs)
    ic(query)
    result = df.query(query)
    ic(result)
    return result


# 11. Pesquiso Unique_ID por file
def get_document_id_by_file(batch, file):
    
    result = filtrar_df(df_id_relations, Batch=batch, File=file)
    document_unique_id = result['Unique_ID'].values[0]
    
    return document_unique_id


def get_children(batch, file_path):
    
    file = os.path.basename(file_path)
    result = filtrar_df(df_id_relations, Batch=batch, File=file)
    document_unique_id = result['Unique_ID'].values[0]
    # Buscando todos dos filhos de um documento
    return filtrar_df(df_id_relations, Batch=batch, Parent_Unique_ID=document_unique_id)

# 13. Busca pai -simples
def get_father(batch, file_path):
    
    file = os.path.basename(file_path)
    result = filtrar_df(df_id_relations, Batch=batch, File=file)
    parent_unique_id = result['Parent_Unique_ID'].values[0]
    # Buscando todos dos filhos de um documento
    return filtrar_df(df_id_relations, Batch=batch, Unique_ID=parent_unique_id)

# 14. Pesquiso pai pelo Unique_ID e trago um dict
def get_father_data_by_children_file(batch, file):
    
    src_result = filtrar_df(df_id_relations, Batch=batch, File=file)
    src_parent_unique_id = src_result['Parent_Unique_ID'].values[0]
    result = filtrar_df(df_id_relations, Batch=batch, Unique_ID=src_parent_unique_id)
    document_batch = result['Batch'].values[0]
    document_data = result['Data'].values[0]
    document_file = result['File'].values[0]
    document_type = result['Type'].values[0]
    document_level = result['Level'].values[0]
    document_unique_id = result['Unique_ID'].values[0]
    document_parent_unique_id = result['Parent_Unique_ID'].values[0]
    document_hash = result['Hash'].values[0]
    document_file_path = result['File_Path'].values[0]
    
    return {
        'Batch': document_batch, 
        'Data': document_data,
        'File' : document_file,
        'Type': document_type,
        'Level': document_level,
        'Unique_ID': document_unique_id,
        'Parent_Unique_ID': document_parent_unique_id,
        'Hash': document_hash,
        'File_Path': document_file_path,
    }

# 15. Pesquiso pai pelo Unique_ID (document_parent_unique_id) e cria DICT
def get_father_by_unique_id(batch, document_parent_unique_id):
    
    result = filtrar_df(df_id_relations, Batch=batch, Unique_ID=document_parent_unique_id)
    document_batch = result['Batch'].values[0]
    document_data = result['Data'].values[0]
    document_file = result['File'].values[0]
    document_type = result['Type'].values[0]
    document_level = result['Level'].values[0]
    document_unique_id = result['Unique_ID'].values[0]
    document_parent_unique_id = result['Parent_Unique_ID'].values[0]
    document_hash = result['Hash'].values[0]
    document_file_path = result['File_Path'].values[0]
    
    return {
        'Batch': document_batch, 
        'Data': document_data,
        'File' : document_file,
        'Type': document_type,
        'Level': document_level,
        'Unique_ID': document_unique_id,
        'Parent_Unique_ID': document_parent_unique_id,
        'Hash': document_hash,
        'File_Path': document_file_path,
    }
    
# 16. Pesquiso pai pelo file do filho e cria DICT
def get_father_data_by_children_file(batch, file):
    
    src_result = filtrar_df(df_id_relations, Batch=batch, File=file)
    src_parent_unique_id = src_result['Parent_Unique_ID'].values[0]
    result = filtrar_df(df_id_relations, Batch=batch, Unique_ID=src_parent_unique_id)
    document_batch = result['Batch'].values[0]
    document_data = result['Data'].values[0]
    document_file = result['File'].values[0]
    document_type = result['Type'].values[0]
    document_level = result['Level'].values[0]
    document_unique_id = result['Unique_ID'].values[0]
    document_parent_unique_id = result['Parent_Unique_ID'].values[0]
    document_hash = result['Hash'].values[0]
    document_file_path = result['File_Path'].values[0]
    
    return {
        'Batch': document_batch, 
        'Data': document_data,
        'File' : document_file,
        'Type': document_type,
        'Level': document_level,
        'Unique_ID': document_unique_id,
        'Parent_Unique_ID': document_parent_unique_id,
        'Hash': document_hash,
        'File_Path': document_file_path,
    }        
            
        
        

# 17. Busca o 'Unique_ID' para definir o Parent_Unique_ID sem considerar 'Level'
def get_parent_unique_id(df_id_relations, batch_name, file, type):
    try:
        parent_unique_id = df_id_relations[(df_id_relations['Batch'] == batch_name) & (df_id_relations['File'] == file) & (df_id_relations['Type'] == type)]['Unique_ID'].values[0]
    except IndexError:
        parent_unique_id = None
        print(f"Unique_ID para Batch {batch_name} e type: {type} nao encontrado em df_id_relations.")
    return parent_unique_id


# 18. funcao para trazer somente o 'Unique_ID'
def get_document_unique_id(df_id_relations, batch_name, file, type, level):
    try:
        document_unique_id = df_id_relations[(df_id_relations['Batch'] == batch_name) & (df_id_relations['File'] == file) & (df_id_relations['Type'] == type) & (df_id_relations['Level'] == level)]['Unique_ID'].values[0]
    except IndexError:
        document_unique_id = None
        print(f"Unique_ID para Batch {batch_name} e type: {type} nao encontrado em df_id_relations.")
    return document_unique_id


# 19. funcao para trazer somente o 'Parent_Unique_ID'
def get_document_parent_unique_id(df_id_relations, batch_name, file, type, level):
    try:
        document_parent_unique_id = df_id_relations[(df_id_relations['Batch'] == batch_name) & (df_id_relations['File'] == file) & (df_id_relations['Type'] == type) & (df_id_relations['Level'] == level)]['Parent_Unique_ID'].values[0]
    except IndexError:
        document_parent_unique_id = None
        print(f"Unique_ID para Batch {batch_name} e type: {type} nao encontrado em df_id_relations.")
    return document_parent_unique_id


# 20. funçao para trazer toda a row de df_id_relations para o documento
def get_document_id_relations(df_id_relations, batch_name, file, type, level):
    try:
        document_id_relations = df_id_relations[(df_id_relations['Batch'] == batch_name) & (df_id_relations['File'] == file) & (df_id_relations['Type'] == type) & (df_id_relations['Level'] == level)].values[0]
    except IndexError:
        document_id_relations = None
        print(f"Unique_ID para Batch {batch_name} e type: {type} nao encontrado em df_id_relations.")
    return document_id_relations