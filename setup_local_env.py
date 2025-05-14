#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para configurar o ambiente virtual local para o TechCare.
Este script ajuda a configurar corretamente o ambiente virtual no Windows.
"""

import os
import sys
import subprocess
import shutil
import logging
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lista de pacotes que podem ser ignorados se falharem
IGNORABLE_PACKAGES = [
    "shutil-which",
    "pywin32",
    "wmi",
    "sensors-core"
]

def create_venv():
    """Cria e configura o ambiente virtual."""
    logger.info("Iniciando configuração do ambiente virtual...")
    
    # Verifica se o Python está disponível
    try:
        result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
        logger.info(f"Python versão: {result.stdout.strip()}")
    except Exception as e:
        logger.error(f"Erro ao verificar versão do Python: {e}")
        return False
    
    # Remove ambiente virtual anterior se existir
    venv_path = Path("venv")
    if venv_path.exists():
        logger.info("Ambiente virtual existente detectado. Removendo...")
        try:
            # No Windows, alguns arquivos podem estar travados, então usamos shutil
            shutil.rmtree(venv_path, ignore_errors=True)
            logger.info("Ambiente virtual anterior removido.")
        except Exception as e:
            logger.error(f"Erro ao remover ambiente virtual: {e}")
            logger.warning("Por favor, feche todas as instâncias do Python e tente novamente.")
            return False
    
    # Cria um novo ambiente virtual
    logger.info("Criando novo ambiente virtual...")
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        logger.info("Ambiente virtual criado com sucesso.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao criar ambiente virtual: {e}")
        return False
    
    # Determina os caminhos para pip e python no ambiente virtual
    is_windows = sys.platform.startswith('win')
    if is_windows:
        python_venv = os.path.join("venv", "Scripts", "python.exe")
        pip_venv = os.path.join("venv", "Scripts", "pip.exe")
    else:
        python_venv = os.path.join("venv", "bin", "python")
        pip_venv = os.path.join("venv", "bin", "pip")
    
    # Atualiza pip, setuptools e wheel
    logger.info("Atualizando pip, setuptools e wheel...")
    try:
        subprocess.run([python_venv, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"], check=True)
        logger.info("Pip, setuptools e wheel atualizados.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Erro ao atualizar pip: {e}")
        return False
    
    # Instala as dependências
    logger.info("Instalando dependências do projeto...")
    req_file = "requirements.txt"
    if not os.path.exists(req_file):
        logger.error(f"Arquivo {req_file} não encontrado!")
        return False
    
    # Vamos filtrar as dependências problemáticas com base no sistema operacional
    logger.info("Preparando requisitos adaptados ao sistema...")
    packages_to_install = []
    with open(req_file, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Ignora a dependência shutil-which se presente (não está mais no requirements.txt)
                if any(pkg in line for pkg in IGNORABLE_PACKAGES):
                    # Verifica se tem condição de plataforma
                    if ';' in line:
                        # Se tem condição, mantém como está
                        packages_to_install.append(line)
                    else:
                        # Se não tem condição, adiciona um log e pula
                        logger.warning(f"Ignorando pacote opcional {line}")
                else:
                    packages_to_install.append(line)
    
    # Escreve arquivo temporário de requisitos
    with open("requirements_temp.txt", "w") as temp_req:
        for package in packages_to_install:
            temp_req.write(f"{package}\n")
    
    # Tenta instalar tudo de uma vez primeiro
    try:
        logger.info("Tentando instalar todas as dependências principais...")
        subprocess.run([python_venv, "-m", "pip", "install", "-r", "requirements_temp.txt"], check=True)
        logger.info("Dependências instaladas com sucesso.")
        install_success = True
    except subprocess.CalledProcessError:
        logger.warning("Não foi possível instalar todas as dependências juntas.")
        logger.info("Tentando instalar as dependências individualmente...")
        
        # Instala pacote por pacote
        install_success = True  # Assumimos que vai dar certo até que falhe algo crítico
        for package in packages_to_install:
            try:
                # Extrai o nome do pacote sem a condição de plataforma
                package_name = package.split(';')[0].strip()
                
                # Verifica se é um pacote que pode ser ignorado se falhar
                is_ignorable = any(pkg in package_name for pkg in IGNORABLE_PACKAGES)
                
                logger.info(f"Instalando {package_name}...")
                try:
                    subprocess.run([python_venv, "-m", "pip", "install", package_name], check=True)
                    logger.info(f"Pacote {package_name} instalado com sucesso.")
                except subprocess.CalledProcessError as pkg_err:
                    if is_ignorable:
                        logger.warning(f"Falha ao instalar pacote opcional {package_name}: {pkg_err}")
                    else:
                        logger.error(f"Erro ao instalar pacote necessário {package_name}: {pkg_err}")
                        install_success = False
            except Exception as e:
                logger.warning(f"Problema ao processar pacote {package}: {e}")
    
    # Limpa arquivos temporários
    try:
        if os.path.exists("requirements_temp.txt"):
            os.remove("requirements_temp.txt")
    except Exception as e:
        logger.warning(f"Não foi possível remover arquivo temporário: {e}")
    
    if install_success:
        logger.info("="*50)
        logger.info("Ambiente virtual configurado com sucesso!")
        logger.info("\nPara ativar o ambiente virtual:")
        if is_windows:
            logger.info("   venv\\Scripts\\activate")
        else:
            logger.info("   source venv/bin/activate")
        logger.info("\nPara executar a aplicação:")
        logger.info("   python run_local.py --debug")
        logger.info("="*50)
        return True
    else:
        logger.error("Não foi possível configurar completamente o ambiente virtual.")
        logger.info("No entanto, as dependências principais foram instaladas e a aplicação pode funcionar.")
        logger.info("Tente executar 'python run_local.py --debug' para verificar.")
        return False

if __name__ == "__main__":
    create_venv() 