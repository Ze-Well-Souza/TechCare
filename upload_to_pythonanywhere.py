#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para automatizar o upload do TechCare para o PythonAnywhere

Este script facilita o processo de deploy do TechCare para o PythonAnywhere,
realizando o upload dos arquivos necessários e configurando o ambiente.

Requisitos:
- Uma conta PythonAnywhere
- Token de API do PythonAnywhere (obtido em Account > API Token)
- O módulo 'requests' instalado

Uso:
    python upload_to_pythonanywhere.py --username SEU_USUARIO --token SEU_TOKEN_API [--host HOSTNAME]
    
Onde HOSTNAME pode ser www.pythonanywhere.com (padrão) ou eu.pythonanywhere.com
"""

import os
import sys
import argparse
import requests
import json
import time
from pathlib import Path
import zipfile
import io

# Cores para saída no terminal
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def parse_arguments():
    """Parse os argumentos da linha de comando"""
    parser = argparse.ArgumentParser(description='Upload do TechCare para o PythonAnywhere')
    parser.add_argument('--username', required=True, help='Seu nome de usuário do PythonAnywhere')
    parser.add_argument('--token', required=True, help='Seu token de API do PythonAnywhere')
    parser.add_argument('--path', default='TechCare', help='Caminho no PythonAnywhere onde o código será instalado')
    parser.add_argument('--files', action='store_true', help='Fazer upload apenas dos arquivos (sem configurar)')
    parser.add_argument('--host', default='www.pythonanywhere.com', help='Host do PythonAnywhere (www.pythonanywhere.com ou eu.pythonanywhere.com)')
    return parser.parse_args()

def create_zipfile():
    """Cria um arquivo ZIP com os arquivos do projeto"""
    print(f"{BOLD}Criando arquivo ZIP para upload...{RESET}")
    
    # Cria um arquivo ZIP em memória
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Lista de arquivos e diretórios a serem ignorados
        ignore_patterns = [
            '.git', '__pycache__', '.pytest_cache', 'venv', '*.pyc', 
            '*.pyo', '.coverage', '*.webp', '*.png', '*.zip', 'node_modules'
        ]
        
        # Função para verificar se um item deve ser ignorado
        def should_ignore(path):
            for pattern in ignore_patterns:
                if pattern.startswith('*'):
                    if path.endswith(pattern[1:]):
                        return True
                elif pattern in path:
                    return True
            return False
        
        # Adiciona todos os arquivos ao ZIP, exceto os ignorados
        for root, dirs, files in os.walk('.'):
            # Remove diretórios ignorados da lista para não percorrê-los
            dirs[:] = [d for d in dirs if not should_ignore(os.path.join(root, d))]
            
            for file in files:
                file_path = os.path.join(root, file)
                if not should_ignore(file_path):
                    # Normaliza o caminho para usar apenas barras
                    archive_path = os.path.join(root, file)[2:]  # Remove './' do início
                    archive_path = archive_path.replace('\\', '/')
                    
                    print(f"Adicionando: {archive_path}")
                    zipf.write(file_path, archive_path)
    
    # Retorna o buffer para a posição inicial
    zip_buffer.seek(0)
    
    print(f"{GREEN}✓ Arquivo ZIP criado com sucesso!{RESET}")
    return zip_buffer

def upload_to_pythonanywhere(args):
    """Faz o upload do projeto para o PythonAnywhere"""
    print(f"{BOLD}Iniciando upload para PythonAnywhere...{RESET}")
    
    # Configurações da API
    api_base_url = f"https://{args.host}/api/v0/user/{args.username}"
    headers = {'Authorization': f'Token {args.token}'}
    
    # Verifica se o usuário existe e o token é válido
    print("Verificando acesso à API do PythonAnywhere...")
    try:
        response = requests.get(f"{api_base_url}/", headers=headers)
        response.raise_for_status()
        print(f"{GREEN}✓ Autenticação bem-sucedida!{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Erro ao acessar a API: {str(e)}{RESET}")
        sys.exit(1)
    
    # Cria o diretório no PythonAnywhere (se não existir)
    print(f"Criando diretório {args.path} no PythonAnywhere...")
    try:
        response = requests.post(
            f"{api_base_url}/files/path/home/{args.username}/{args.path}/",
            headers=headers
        )
        if response.status_code == 201:
            print(f"{GREEN}✓ Diretório criado com sucesso!{RESET}")
        elif response.status_code == 200:
            print(f"{YELLOW}! Diretório já existe.{RESET}")
        else:
            print(f"{YELLOW}! Status: {response.status_code} - {response.text}{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Erro ao criar diretório: {str(e)}{RESET}")
        sys.exit(1)
    
    # Prepara e faz o upload do arquivo ZIP
    print("Preparando arquivo para upload...")
    zip_buffer = create_zipfile()
    
    print("Fazendo upload do arquivo ZIP...")
    try:
        response = requests.post(
            f"{api_base_url}/files/path/home/{args.username}/{args.path}/techcare_upload.zip",
            headers=headers,
            files={'content': ('techcare_upload.zip', zip_buffer, 'application/zip')}
        )
        response.raise_for_status()
        print(f"{GREEN}✓ Upload do arquivo ZIP concluído!{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Erro no upload: {str(e)}{RESET}")
        sys.exit(1)
    
    # Descompacta o arquivo ZIP no servidor
    print("Descompactando o arquivo no servidor...")
    try:
        # Executa o comando para descompactar o arquivo
        response = requests.post(
            f"{api_base_url}/consoles/",
            headers=headers,
            json={'executable': 'bash', 'arguments': '-c "cd /home/' + args.username + '/' + args.path + ' && unzip -o techcare_upload.zip && rm techcare_upload.zip"'}
        )
        response.raise_for_status()
        console_id = response.json()['id']
        
        # Espera até que o comando seja concluído
        print("Aguardando a descompactação... (isso pode levar alguns minutos)")
        while True:
            response = requests.get(
                f"{api_base_url}/consoles/{console_id}/",
                headers=headers
            )
            if not response.json()['alive']:
                break
            print(".", end="", flush=True)
            time.sleep(2)
        
        print(f"\n{GREEN}✓ Descompactação concluída!{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Erro ao descompactar: {str(e)}{RESET}")
    
    # Se a flag --files foi passada, encerra aqui
    if args.files:
        print(f"{BOLD}Upload de arquivos concluído com sucesso!{RESET}")
        return
    
    # Faz upload do arquivo fix_pandas_pythonanywhere.py para resolver problemas com o pandas
    print("Fazendo upload do script fix_pandas_pythonanywhere.py...")
    try:
        with open('fix_pandas_pythonanywhere.py', 'r') as f:
            fix_script_content = f.read()
        
        response = requests.post(
            f"{api_base_url}/files/path/home/{args.username}/{args.path}/fix_pandas_pythonanywhere.py",
            headers=headers,
            files={'content': ('fix_pandas_pythonanywhere.py', fix_script_content, 'text/plain')}
        )
        response.raise_for_status()
        print(f"{GREEN}✓ Upload do script fix_pandas_pythonanywhere.py concluído!{RESET}")
    except FileNotFoundError:
        print(f"{YELLOW}! Script fix_pandas_pythonanywhere.py não encontrado. Pulando etapa.{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Erro no upload do script: {str(e)}{RESET}")
    
    # Configura o ambiente virtual e instala as dependências
    print("Configurando ambiente virtual e instalando dependências...")
    try:
        # Usa o arquivo requirements_pythonanywhere_updated.txt se existir
        req_file = 'requirements_pythonanywhere_updated.txt' if os.path.exists('requirements_pythonanywhere_updated.txt') else 'requirements_pythonanywhere.txt'
        
        response = requests.post(
            f"{api_base_url}/consoles/",
            headers=headers,
            json={'executable': 'bash', 'arguments': '-c "cd /home/' + args.username + '/' + args.path + ' && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip setuptools wheel && python fix_pandas_pythonanywhere.py"'}
        )
        response.raise_for_status()
        console_id = response.json()['id']
        
        print("Instalando dependências... (isso pode levar vários minutos)")
        while True:
            response = requests.get(
                f"{api_base_url}/consoles/{console_id}/",
                headers=headers
            )
            if not response.json()['alive']:
                break
            print(".", end="", flush=True)
            time.sleep(5)
        
        print(f"\n{GREEN}✓ Ambiente configurado e dependências instaladas!{RESET}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Erro ao configurar ambiente: {str(e)}{RESET}")
    
    # Verifica se já existe uma aplicação web configurada
    print("Verificando aplicações web existentes...")
    try:
        response = requests.get(
            f"{api_base_url}/webapps/",
            headers=headers
        )
        response.raise_for_status()
        webapps = response.json()
        
        # Verifica se já existe uma aplicação com o domínio padrão
        domain = f"{args.username}.pythonanywhere.com"
        existing_app = next((app for app in webapps if app['domain'] == domain), None)
        
        if existing_app:
            print(f"{YELLOW}! Aplicação web já existe. Atualizando configuração...{RESET}")
            
            # Atualiza a configuração do WSGI
            print("Atualizando arquivo WSGI...")
            wsgi_path = existing_app['user_wsgi_file_path']
            
            # Escolhe o arquivo WSGI mais específico disponível
            if os.path.exists('wsgi_pythonanywhere.py'):
                wsgi_file = 'wsgi_pythonanywhere.py'
            else:
                wsgi_file = 'wsgi.py'
                
            with open(wsgi_file, 'r') as f:
                wsgi_content = f.read()
            
            # Substitui o caminho pelo correto
            wsgi_content = wsgi_content.replace(
                "path = '/home/SEU_USUARIO/TechCare'", 
                f"path = '/home/{args.username}/{args.path}'"
            ).replace(
                "path = os.path.dirname(os.path.abspath(__file__))", 
                f"path = '/home/{args.username}/{args.path}'"
            )
            
            # Faz upload do WSGI atualizado
            response = requests.post(
                f"{api_base_url}/files/path{wsgi_path}",
                headers=headers,
                files={'content': ('wsgi.py', wsgi_content, 'text/plain')}
            )
            response.raise_for_status()
            
            # Define o caminho do virtualenv
            venv_path = f"/home/{args.username}/{args.path}/venv"
            response = requests.patch(
                f"{api_base_url}/webapps/{domain}/",
                headers=headers,
                json={'virtualenv_path': venv_path}
            )
            response.raise_for_status()
            
            # Define os caminhos de código e trabalho
            response = requests.patch(
                f"{api_base_url}/webapps/{domain}/static_files/",
                headers=headers,
                json=[
                    {'url': '/static/', 'path': f"/home/{args.username}/{args.path}/app/static"}
                ]
            )
            response.raise_for_status()
            
            print(f"{GREEN}✓ Configuração atualizada!{RESET}")
        else:
            print(f"{YELLOW}! Nenhuma aplicação web encontrada. É necessário criar uma manualmente.{RESET}")
            print("Siga os passos no arquivo DEPLOY_PYTHONANYWHERE.md para configurar a aplicação web.")
        
        # Recarrega a aplicação web (se existir)
        if existing_app:
            print("Recarregando aplicação web...")
            response = requests.post(
                f"{api_base_url}/webapps/{domain}/reload/",
                headers=headers
            )
            response.raise_for_status()
            print(f"{GREEN}✓ Aplicação recarregada com sucesso!{RESET}")
            print(f"\nSua aplicação TechCare está disponível em: https://{domain}")
    except requests.exceptions.RequestException as e:
        print(f"{RED}✗ Erro ao configurar aplicação web: {str(e)}{RESET}")
    
    print(f"\n{BOLD}Processo de upload e configuração concluído!{RESET}")
    print(f"Se surgirem problemas, consulte o arquivo DEPLOY_PYTHONANYWHERE.md para instruções detalhadas.")

if __name__ == "__main__":
    args = parse_arguments()
    upload_to_pythonanywhere(args) 