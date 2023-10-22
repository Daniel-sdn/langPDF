import os
import re
import json
import pytz
import time, copy
import datetime

from pytz import timezone
from urllib import response
from datetime import datetime

#calculatempo
def calculaTempo(since, fase):
    elapsed = (time.time() - since) * 1000
    minutes, seconds = divmod(elapsed / 1000, 60)
    milliseconds = elapsed % 1000
    return elapsed, minutes, seconds, milliseconds


# Funçao para trabalhar datas
def timestamp_to_portuguese_time(timestamp):
    # Convert the timestamp to a datetime object
    dt = datetime.fromtimestamp(timestamp)

    # Format the datetime object to a Portuguese time format
    portuguese_time_format = dt.strftime("%d/%m/%Y %H:%M:%S")

    # Get the date and time values in separate formats
    date = dt.strftime("%d/%m/%Y")
    time_24h = dt.strftime("%H:%M:%S")
    time_am_pm = dt.strftime("%I:%M:%S %p")

    # Return a dictionary with all the values
    return {
        "full_date_time": portuguese_time_format,
        "date": date,
        "time_24h": time_24h,
        "time_am_pm": time_am_pm,
        "redis_date_time_format": dt.strftime("%Y-%m-%d %H:%M:%S")
    }

def timenow_pt_BR():
    
    # Nosso timezone
    local_tz = pytz.timezone('America/Sao_Paulo')
    
    # Obtenha a hora UTC atual e converta-a para a hora local
    utc_now = datetime.now(pytz.utc)
    local_now = utc_now.astimezone(local_tz)
    
    # Converta a hora local em um carimbo de data/hora Unix
    local_timestamp = local_now.timestamp()
    
    dt = datetime.fromtimestamp(local_timestamp)
    
    pt_BR_time_format = dt.strftime("%d/%m/%Y %H:%M:%S")
    
    return pt_BR_time_format


def convert_email_date(email_date):
    
    # Utiliza expressão regular para extrair os componentes
    match = re.search(r'(\d{2}) (\w{3}) (\d{4}) (\d{2}):(\d{2}):(\d{2}) ([+-]\d{4})', email_date)
    if match:
        day, month_str, year, hour, minute, second, tz_offset = match.groups()
        
        month_map_en = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        month_map_pt = {'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6, 'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}

        # Detectar idioma do campo de data (um exemplo simples, você pode fazer algo mais robusto)
        if 'Jan' in email_date or 'Feb' in email_date or 'Mar' in email_date:
            month_map = month_map_en
        else:
            month_map = month_map_pt
            
        month = month_map.get(month_str, 0) 
        
        
        # Cria um objeto datetime
        dt = datetime(year=int(year), month=month, day=int(day),
                hour=int(hour), minute=int(minute), second=int(second)) 
        
        formatted_date_str = dt.strftime("%d/%m/%Y %H:%M:%S")  
        
    return formatted_date_str
    