#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para instalar corretamente o pandas e dependências no PythonAnywhere.

Este script ajuda a contornar as limitações do PythonAnywhere com o pandas,
instalando uma versão compatível (1.5.3) em vez da versão mais recente.

O PythonAnywhere tem limitações de memória que impedem a instalação de 
versões mais recentes do pandas (>=2.0) que dependem do numpy mais recente.
"""

import os
import sys
import subprocess
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def install_package(package, version=None):
    """Instala um pacote Python"""
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade"]
    if version:
        cmd.append(f"{package}=={version}")
    else:
        cmd.append(package)
    
    logger.info(f"Instalando {package}" + (f" versão {version}" if version else ""))
    try:
        subprocess.check_call(cmd)
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao instalar {package}: {e}")
        return False

def install_pandas_pythonanywhere():
    """Instala pandas e dependências compatíveis com o PythonAnywhere"""
    logger.info("Iniciando instalação do pandas no PythonAnywhere...")
    
    # Verifica se está rodando no PythonAnywhere
    is_pythonanywhere = "PYTHONANYWHERE_DOMAIN" in os.environ
    if is_pythonanywhere:
        logger.info("Ambiente PythonAnywhere detectado.")
    else:
        logger.info("Ambiente local detectado. Este script é otimizado para PythonAnywhere.")
    
    # Instala dependências básicas
    logger.info("Instalando dependências básicas...")
    install_package("pip")
    install_package("wheel")
    install_package("setuptools")
    
    # Instala os requisitos do projeto
    req_file = "requirements_pythonanywhere_updated.txt"
    if os.path.exists(req_file):
        logger.info(f"Instalando dependências do arquivo {req_file}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_file])
            logger.info("Dependências instaladas com sucesso!")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Erro ao instalar dependências: {e}")
    else:
        logger.info("Arquivo requirements_pythonanywhere_updated.txt não encontrado. Instalando pacotes individualmente...")
        
        # Instala numpy primeiro
        install_package("numpy", "1.24.0")
        
        # Instala pandas versão 1.5.3 (compatível com PythonAnywhere)
        if not install_package("pandas", "1.5.3"):
            logger.warning("Tentando versão alternativa do pandas...")
            if not install_package("pandas", "1.3.5"):
                logger.error("Falha ao instalar o pandas. Tente fazer a instalação manualmente.")
                return False
        
        # Instala outras dependências
        packages = [
            ("flask", "3.1.0"),
            ("sqlalchemy", "2.0.32"),
            ("flask-login", "0.6.3"),
            ("flask-wtf", "1.2.1"),
            ("requests", "2.31.0"),
            ("pathlib", "1.0.1"),
            ("plotly", "5.18.0"),
            ("psutil", "7.0.0"),
            ("py-cpuinfo", "9.0.0")
        ]
        
        for package, version in packages:
            install_package(package, version)
    
    logger.info("Instalação do pandas e dependências concluída!")
    return True

if __name__ == "__main__":
    install_pandas_pythonanywhere() 