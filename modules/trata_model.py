import os
import sys
import shutil

import pandas as pd
from pathlib import Path

import modules.utils as utils


def get_template_version(model):
    row_frame = utils.filtrar_df(frames_nf_v4_df, model=model)
    if not row_frame.empty:
            # Acessando a primeira linha do DataFrame filtrado e depois acessando as colunas
            version = [((row_frame.iloc[0]['version']))]
            
    return version[0]  

# XXXpara buscar melhor as coordendas dos FRAMES
def get_coordinates_filter(pdf_pesquisavel_map, model, tipo, label, section):
    
    row_frame = utils.filtrar_df(frames_nf_v4_df, model=model, type=tipo, label=label, section_json=section)
    
    # Verificando se row_frame não está vazio
    if not row_frame.empty:
        # Acessando a primeira linha do DataFrame filtrado e depois acessando as colunas
        coodinates = [((row_frame.iloc[0]['x0_p'], row_frame.iloc[0]['y0_p'], row_frame.iloc[0]['x1_p'], row_frame.iloc[0]['y1_p']) if pdf_pesquisavel_map else (row_frame.iloc[0]['x0'], row_frame.iloc[0]['y0'], row_frame.iloc[0]['x1'], row_frame.iloc[0]['y1']))]
    else:
        # Retornando uma tupla de valores NaN se o DataFrame filtrado estiver vazio
        coodinates = [(float('nan'), float('nan'), float('nan'), float('nan'))]
    
    return coodinates