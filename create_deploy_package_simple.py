#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Versão simplificada do script para criar um pacote de deploy do TechCare

Este script cria rapidamente um arquivo ZIP com os arquivos essenciais 
para o deploy no PythonAnywhere, sem realizar verificações extensivas.
"""

import os
import zipfile
from datetime import datetime

# Arquivos e diretórios a incluir (apenas os essenciais)
INCLUDE_FILES = [
    'app/',
    'migrations/',
    'run.py',
    'wsgi.py',
    'requirements_pythonanywhere.txt',
    'README_DEPLOY_PYTHONANYWHERE.md',
    'check_deploy_readiness.py',
    'create_admin_pythonanywhere.py',
    'techcare_pythonanywhere_guide.md'
]

# Arquivos e diretórios a ignorar
IGNORE_PATTERNS = [
    '__pycache__',
    '.pytest_cache',
    '*.pyc',
    '*.pyo',
    '.coverage',
    '*.log',
    '.git/',
    'venv/',
    'node_modules/',
    '*.zip'
]

def should_ignore(path):
    """Verifica se um caminho deve ser ignorado"""
    for pattern in IGNORE_PATTERNS:
        if pattern.startswith('*') and path.endswith(pattern[1:]):
            return True
        elif pattern in path:
            return True
    return False

def create_deploy_package():
    """Cria um pacote de deploy para o PythonAnywhere"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"techcare_deploy_{timestamp}.zip"
    
    print(f"Criando pacote de deploy: {zip_filename}")
    
    # Cria o arquivo ZIP
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Adiciona os arquivos essenciais
        for include_path in INCLUDE_FILES:
            # Verifica se é um diretório ou arquivo
            if include_path.endswith('/'):
                # É um diretório, adiciona todos os arquivos dentro dele
                dir_path = include_path[:-1]  # Remove a barra final
                if not os.path.exists(dir_path):
                    print(f"Aviso: Diretório '{dir_path}' não encontrado, ignorando...")
                    continue
                
                for root, dirs, files in os.walk(dir_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        if not should_ignore(file_path):
                            # Define o caminho dentro do ZIP
                            archive_path = file_path.replace('\\', '/')
                            print(f"Adicionando: {archive_path}")
                            zipf.write(file_path, archive_path)
            else:
                # É um arquivo, adiciona diretamente
                if os.path.exists(include_path):
                    archive_path = include_path.replace('\\', '/')
                    print(f"Adicionando: {archive_path}")
                    zipf.write(include_path, archive_path)
                else:
                    print(f"Aviso: Arquivo '{include_path}' não encontrado, ignorando...")
    
    print(f"\nPacote de deploy criado com sucesso: {zip_filename}")
    print(f"Tamanho: {os.path.getsize(zip_filename) / (1024*1024):.2f} MB")
    print("\nAgora você pode fazer upload deste arquivo para o PythonAnywhere manualmente.")
    print("Instruções:")
    print("1. Faça login no PythonAnywhere (www.pythonanywhere.com)")
    print("2. Vá para a seção 'Files'")
    print("3. Navegue até a pasta onde deseja extrair o TechCare")
    print("4. Clique em 'Upload a file' e selecione o arquivo ZIP gerado")
    print("5. Após o upload, use o console bash para extrair o arquivo:")
    print(f"   unzip -o {zip_filename} && rm {zip_filename}")
    print("6. Siga as instruções no README_DEPLOY_PYTHONANYWHERE.md para finalizar a configuração")

if __name__ == "__main__":
    create_deploy_package() 