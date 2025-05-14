#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para criar um pacote de deploy do TechCare para o PythonAnywhere

Este script cria um arquivo ZIP contendo todos os arquivos necessários para
o deploy do TechCare no PythonAnywhere, excluindo arquivos desnecessários.
Também verifica se os arquivos essenciais estão presentes.
"""

import os
import sys
import zipfile
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import glob

# Cores para saída no terminal
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def print_colored(text, color):
    """Imprimir texto colorido no terminal."""
    colors = {
        'red': '\033[91m',
        'green': '\033[92m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'magenta': '\033[95m',
        'cyan': '\033[96m',
        'reset': '\033[0m'
    }
    print(f"{colors.get(color, '')}{text}{colors['reset']}")

# Arquivos essenciais para o deploy
ESSENTIAL_FILES = [
    'app/__init__.py',
    'config.py',
    'wsgi.py',
    'wsgi_pythonanywhere.py',
    'requirements_pythonanywhere.txt',
    'README_PYTHONANYWHERE.md',
]

def verify_essential_files():
    """Verifica se os arquivos essenciais para o deploy existem"""
    missing_files = []
    for file_path in ESSENTIAL_FILES:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print_colored("✗ Arquivos essenciais faltando:", "red")
        for file in missing_files:
            print(f"  - {file}")
        
        # Cria o arquivo wsgi_pythonanywhere.py se estiver faltando
        if 'wsgi_pythonanywhere.py' in missing_files:
            print_colored("Criando arquivo wsgi_pythonanywhere.py...", "yellow")
            with open('wsgi_pythonanywhere.py', 'w') as f:
                f.write("""import sys
import os

# Adiciona o diretório da aplicação ao PATH
# ATENÇÃO: Atualize este caminho para o diretório correto no PythonAnywhere
path = '/home/Zewell10/TechCare'
if path not in sys.path:
    sys.path.append(path)

# Define variáveis de ambiente
os.environ['FLASK_ENV'] = 'production'
os.environ['FLASK_CONFIG'] = 'production'

# Importa e cria a aplicação
from app import create_app

# Cria a aplicação usando as configurações de produção
application = create_app('production')
""")
            missing_files.remove('wsgi_pythonanywhere.py')
        
        if 'README_PYTHONANYWHERE.md' in missing_files:
            print_colored("Criando arquivo README_PYTHONANYWHERE.md...", "yellow")
            try:
                with open('README_PYTHONANYWHERE.md', 'w', encoding='utf-8') as f:
                    f.write("""# Instruções de Deploy no PythonAnywhere

## 1. Preparação no PythonAnywhere

1. Faça login na sua conta PythonAnywhere (zewell10)
2. Abra um console Bash (clique em "Consoles" → "Bash")

## 2. Limpar ambiente atual (opcional)

Se quiser começar totalmente do zero:

```bash
# Remova instalações anteriores
rm -rf ~/mysite ~/TechCare
```

## 3. Criar diretório e extrair arquivos

```bash
# Crie um diretório limpo
mkdir -p ~/TechCare

# Extraia os arquivos (ajuste o nome do arquivo ZIP se necessário)
cd ~
unzip techcare_deploy_*.zip -d TechCare
cd TechCare

# Verifique se os arquivos foram extraídos corretamente
ls -la
```

## 4. Configurar ambiente virtual e instalar dependências

```bash
# Criar ambiente virtual
python3 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências
pip install --upgrade pip setuptools wheel
pip install -r requirements_pythonanywhere.txt
```

## 5. Configurar o arquivo WSGI

1. Vá para a aba "Web" no dashboard do PythonAnywhere
2. Localize a seção "Code" e clique no link do seu arquivo WSGI
3. Substitua todo o conteúdo pelo conteúdo do arquivo `wsgi_pythonanywhere.py`
4. **IMPORTANTE**: Verifique se o caminho no arquivo está correto:
   - `path = '/home/Zewell10/TechCare'` (ajuste para o seu diretório)
5. Clique em "Save" para salvar as alterações

## 6. Configurar diretório da aplicação

1. Na aba "Web", localize a seção "Code"
2. Atualize "Source code" para: `/home/Zewell10/TechCare`
3. Atualize "Working directory" para: `/home/Zewell10/TechCare`
4. Verifique "WSGI configuration file"

## 7. Configurar ambiente virtual

1. Na aba "Web", localize a seção "Virtualenv"
2. Digite o caminho para seu ambiente virtual: `/home/Zewell10/TechCare/venv`
3. Clique no botão vermelho para criar/atualizar o ambiente virtual

## 8. Reiniciar a aplicação

1. Clique no botão grande verde "Reload" na parte superior da página Web
2. Verifique a aplicação acessando o URL: `zewell10.pythonanywhere.com`
""")
                print_colored("Arquivo README_PYTHONANYWHERE.md criado com sucesso.", "green")
            except Exception as e:
                print_colored(f"Erro ao criar README_PYTHONANYWHERE.md: {str(e)}", "red")
        
        # Cria o arquivo requirements_pythonanywhere.txt se estiver faltando
        if 'requirements_pythonanywhere.txt' in missing_files:
            print_colored("Criando arquivo requirements_pythonanywhere.txt...", "yellow")
            # Copia o arquivo requirements.txt para requirements_pythonanywhere.txt
            if os.path.exists('requirements.txt'):
                with open('requirements.txt', 'r') as src, open('requirements_pythonanywhere.txt', 'w') as dest:
                    # Filtra as dependências específicas do Windows
                    for line in src:
                        if 'pywin32' not in line and 'wmi' not in line and 'shutil-which' not in line:
                            dest.write(line)
                missing_files.remove('requirements_pythonanywhere.txt')
        
        if missing_files:
            return False
    
    return True

def create_deploy_package():
    """Cria um pacote de deploy para o PythonAnywhere"""
    print_colored("Criando pacote de deploy para PythonAnywhere...", "blue")
    
    # Verifica se os arquivos essenciais estão presentes
    print_colored("Verificando arquivos essenciais...", "blue")
    if not verify_essential_files():
        if not input("Continuar mesmo com arquivos essenciais faltando? (s/n): ").lower().startswith('s'):
            print_colored("Operação cancelada.", "red")
            return
    
    # Verifica se o projeto está pronto para deploy
    if os.path.exists('check_deploy_readiness.py'):
        print_colored("Verificando prontidão para deploy...", "blue")
        result = subprocess.run(['python', 'check_deploy_readiness.py'], capture_output=True, text=True)
        
        if result.returncode != 0:
            print_colored(f"✗ Projeto não está pronto para deploy:", "red")
            print(result.stdout)
            if not input("Deseja continuar mesmo assim? (s/n): ").lower().startswith('s'):
                print_colored("Operação cancelada.", "red")
                return
    
    # Define o nome do arquivo ZIP
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"techcare_deploy_package_{timestamp}.zip"
    
    # Lista de arquivos e diretórios a serem ignorados
    ignore_patterns = [
        '.git', '__pycache__', '.pytest_cache', 'venv', '*.pyc', 
        '*.pyo', '.coverage', 'node_modules', '.vscode', '.idea',
        '*.zip', '*.log', '*.tmp', '*.temp', 'instance', 
        'techcare_deploy_package_*.zip', '*.db', '*.sqlite3',
        '.github', 'tests'
    ]
    
    # Função para verificar se um item deve ser ignorado
    def should_ignore(path):
        path_str = str(path)
        for pattern in ignore_patterns:
            if pattern.startswith('*'):
                if path_str.endswith(pattern[1:]):
                    return True
            elif pattern in path_str:
                return True
        return False
    
    # Cria o arquivo ZIP
    print_colored(f"Criando arquivo ZIP: {zip_filename}", "blue")
    
    try:
        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            total_files = 0
            
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
                        
                        zipf.write(file_path, archive_path)
                        total_files += 1
                        
                        # Exibe progresso a cada 20 arquivos
                        if total_files % 20 == 0:
                            print_colored(f"Adicionados {total_files} arquivos ao pacote...", "blue")
        
        print_colored(f"✓ Pacote de deploy criado com sucesso: {zip_filename}", "green")
        print(f"  Total de arquivos: {total_files}")
        print(f"  Tamanho do arquivo: {os.path.getsize(zip_filename) / (1024*1024):.2f} MB")
        print(f"\nPróximos passos:")
        print(f"1. Faça o upload do pacote para o PythonAnywhere")
        print(f"2. Descompacte o pacote com o comando: unzip {zip_filename}")
        print(f"3. Siga as instruções em README_PYTHONANYWHERE.md")
        
        # Limpar pacotes antigos (opcional)
        if input("Deseja remover pacotes de deploy antigos? (s/n): ").lower().startswith('s'):
            old_packages = [p for p in glob.glob("techcare_deploy_*.zip") if p != zip_filename]
            for package in old_packages:
                os.remove(package)
                print_colored(f"Removido pacote antigo: {package}", "yellow")
        
    except Exception as e:
        print_colored(f"✗ Erro ao criar pacote de deploy: {str(e)}", "red")

if __name__ == "__main__":
    create_deploy_package() 