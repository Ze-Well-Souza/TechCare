"""
Utilitários para operações específicas de sistemas Linux.
Fornece funções para acessar informações de hardware e software em sistemas Linux.
"""

import os
import logging
import subprocess
from typing import Optional, Dict, List, Any
import re

from app.services.diagnostic.utils.platform_utils import is_linux

# Configuração de logging
logger = logging.getLogger(__name__)

def run_command(command):
    """
    Executa um comando no shell e retorna a saída.
    
    Args:
        command (str): Comando a ser executado
        
    Returns:
        str: Saída do comando ou string vazia em caso de erro
    """
    if not is_linux():
        logger.warning("Tentativa de executar comando específico do Linux em sistema não-Linux")
        return ""
        
    try:
        output = subprocess.check_output(command, shell=True, universal_newlines=True)
        return output.strip()
    except Exception as e:
        logger.warning(f"Erro ao executar comando '{command}': {str(e)}")
        return ""

def get_cpu_temperature():
    """
    Obtém a temperatura da CPU em sistemas Linux.
    
    Returns:
        float: Temperatura da CPU em graus Celsius, ou None se não disponível
    """
    if not is_linux():
        return None
        
    try:
        # Tenta diferentes arquivos de temperatura no Linux
        paths = [
            "/sys/class/thermal/thermal_zone0/temp",
            "/sys/devices/platform/coretemp.0/temp1_input",
            "/sys/bus/acpi/devices/LNXTHERM:00/thermal_zone/temp"
        ]
        
        for path in paths:
            if os.path.exists(path):
                with open(path, 'r') as f:
                    temp = int(f.read().strip()) / 1000
                    return round(temp, 1)
        
        # Tenta usando o comando sensors
        try:
            output = run_command("sensors")
            if output:
                # Procura por padrões como "Core 0: +45.0°C"
                temp_matches = re.findall(r'Core \d+:\s+\+(\d+\.\d+)°C', output)
                if temp_matches:
                    # Calcula a média das temperaturas dos núcleos
                    temps = [float(t) for t in temp_matches]
                    return round(sum(temps) / len(temps), 1)
        except Exception:
            pass
            
        return None
    except Exception as e:
        logger.warning(f"Erro ao obter temperatura da CPU no Linux: {str(e)}")
        return None

def get_memory_info():
    """
    Obtém informações detalhadas sobre a memória em sistemas Linux.
    
    Returns:
        Dict: Informações sobre a memória
    """
    if not is_linux():
        return {}
        
    try:
        # Utiliza arquivo /proc/meminfo
        mem_info = {}
        if os.path.exists('/proc/meminfo'):
            with open('/proc/meminfo', 'r') as f:
                for line in f:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        value = value.strip()
                        # Remove unidade (geralmente kB) e converte para inteiro
                        if 'kB' in value:
                            value = int(value.replace('kB', '').strip()) * 1024
                        mem_info[key.strip()] = value
        
        # Converte para um formato mais amigável
        result = {
            'total': int(mem_info.get('MemTotal', 0)),
            'free': int(mem_info.get('MemFree', 0)),
            'available': int(mem_info.get('MemAvailable', 0)),
            'used': int(mem_info.get('MemTotal', 0)) - int(mem_info.get('MemAvailable', 0)),
            'swap_total': int(mem_info.get('SwapTotal', 0)),
            'swap_free': int(mem_info.get('SwapFree', 0))
        }
        
        # Calcula percentuais
        if result['total'] > 0:
            result['percent_used'] = round((result['used'] / result['total']) * 100, 1)
        else:
            result['percent_used'] = 0
            
        if result['swap_total'] > 0:
            result['swap_percent_used'] = round(
                ((result['swap_total'] - result['swap_free']) / result['swap_total']) * 100, 1
            )
        else:
            result['swap_percent_used'] = 0
            
        return result
    except Exception as e:
        logger.warning(f"Erro ao obter informações de memória no Linux: {str(e)}")
        return {} 