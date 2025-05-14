#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para configuração inicial da aplicação TechCare
"""

import os
import sys
import subprocess
import platform

def setup_app():
    """
    Configura a aplicação TechCare inicialmente, criando diretórios,
    configurando o ambiente virtual e inicializando o banco de dados
    """
    print("=== Configuração inicial do TechCare ===")
    
    # Detecta o sistema operacional
    os_name = platform.system()
    print(f"Sistema operacional detectado: {os_name}")
    
    # Cria diretórios necessários
    directories = [
        "data",
        "data/diagnostics",
        "data/repair_logs",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(os.path.join(os.path.dirname(__file__), directory), exist_ok=True)
        print(f"Diretório criado: {directory}")
    
    # Verifica se o ambiente virtual já existe
    venv_dir = os.path.join(os.path.dirname(__file__), "venv")
    if not os.path.exists(venv_dir):
        print("\nCriando ambiente virtual...")
        
        # Comando para criar ambiente virtual
        if os_name == "Windows":
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        else:
            subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
    else:
        print("\nAmbiente virtual já existe.")
    
    # Instala as dependências
    print("\nInstalando dependências...")
    
    # Comando para instalar dependências
    if os_name == "Windows":
        pip_cmd = os.path.join(venv_dir, "Scripts", "pip")
    else:
        pip_cmd = os.path.join(venv_dir, "bin", "pip")
    
    subprocess.run([pip_cmd, "install", "-r", "requirements.txt"], check=True)
    
    # Inicializa o banco de dados
    print("\nInicializando o banco de dados...")
    
    # Comando para executar o script de inicialização do banco de dados
    if os_name == "Windows":
        python_cmd = os.path.join(venv_dir, "Scripts", "python")
    else:
        python_cmd = os.path.join(venv_dir, "bin", "python")
    
    subprocess.run([python_cmd, "scripts/init_db.py"], check=True)
    
    print("\n=== Configuração concluída com sucesso! ===")
    print("\nPara iniciar a aplicação, execute:")
    if os_name == "Windows":
        print("venv\\Scripts\\python run.py")
    else:
        print("venv/bin/python run.py")

if __name__ == "__main__":
    setup_app() 