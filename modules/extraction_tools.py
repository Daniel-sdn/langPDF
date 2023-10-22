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

import re
from unidecode import unidecode
from unicodedata import normalize
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import PyPDF2

import csv
import json
import pandas as pd

import uuid
import hashlib

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


def corrigir_email(texto):
    # Padrão de regex para identificar e-mails potenciais
    padrao_email = re.compile(r'[a-zA-Z0-9_.+-]+[)!Q@][a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
    
    # Encontrar todos os padrões que se assemelham a um e-mail
    possiveis_emails = padrao_email.findall(texto)
    
    for email in possiveis_emails:
        # Se "@" não estiver presente, tentamos corrigir substituindo ")" ou "!" por "@"
        if "@" not in email:
            email_corrigido = email.replace(")", "@").replace("Q", "@")
            texto = texto.replace(email, email_corrigido)
    
    return texto   