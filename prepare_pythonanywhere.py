#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar compatibilidade com PythonAnywhere e preparar implantação
"""

import os
import sys
import platform
import pkg_resources
import subprocess
import shutil
from pathlib import Path

GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

print(f"{BOLD}Verificação de Compatibilidade para PythonAnywhere{RESET}\n")

# 1. Verificar versão do Python
py_version = platform.python_version()
print(f"1. Versão do Python: {py_version}")
py_version_parts = [int(x) for x in py_version.split('.')]
if py_version_parts[0] >= 3 and py_version_parts[1] >= 8:
    print(f"   {GREEN}✓ Versão do Python compatível com PythonAnywhere{RESET}")
else:
    print(f"   {RED}✗ Versão do Python abaixo do mínimo recomendado (3.8+){RESET}")
    print(f"   PythonAnywhere suporta Python 3.8, 3.9, 3.10 e 3.11")

# 2. Verificar dependências específicas do Windows
print("\n2. Verificando dependências específicas para Windows")
windows_libs = ['pywin32', 'wmi', 'shutil-which']
windows_alternatives = {
    'pywin32': 'O módulo não será necessário no Linux',
    'wmi': 'Substitua por psutil para obter informações do sistema',
    'shutil-which': 'O módulo which do shutil está disponível no Python 3.8+'
}

with open('requirements.txt', 'r') as f:
    requirements = f.readlines()

windows_deps_found = []
for req in requirements:
    req = req.strip()
    for lib in windows_libs:
        if lib in req:
            windows_deps_found.append(lib)

if windows_deps_found:
    print(f"   {YELLOW}! Dependências específicas do Windows encontradas:{RESET}")
    for dep in windows_deps_found:
        print(f"     - {dep}: {windows_alternatives.get(dep, 'Sem alternativa conhecida')}")
    
    # Criar requirements_pythonanywhere.txt
    print("\n   Criando requirements_pythonanywhere.txt sem dependências Windows...")
    with open('requirements_pythonanywhere.txt', 'w') as f:
        for req in requirements:
            req = req.strip()
            skip = False
            for lib in windows_libs:
                if lib in req and '; sys_platform == ' not in req:
                    skip = True
                    break
            if not skip:
                f.write(req + '\n')
    print(f"   {GREEN}✓ requirements_pythonanywhere.txt criado{RESET}")
else:
    print(f"   {GREEN}✓ Nenhuma dependência específica do Windows encontrada{RESET}")
    shutil.copy('requirements.txt', 'requirements_pythonanywhere.txt')

# 3. Verificar configurações do banco de dados
print("\n3. Verificando configurações do banco de dados")
if os.path.exists('app/config.py'):
    with open('app/config.py', 'r') as f:
        config_content = f.read()
    
    if 'SQLALCHEMY_DATABASE_URI' in config_content and 'sqlite' in config_content:
        print(f"   {GREEN}✓ Usando SQLite - compatível com o PythonAnywhere{RESET}")
    else:
        print(f"   {YELLOW}! Verifique se a configuração do banco de dados é compatível com PythonAnywhere{RESET}")
        print(f"     - Conta gratuita: apenas MySQL e SQLite")
        print(f"     - Contas pagas: MySQL, PostgreSQL, SQLite")
else:
    print(f"   {YELLOW}! Arquivo de configuração não encontrado, verifique manualmente{RESET}")

# 4. Verificar presença de arquivos críticos
print("\n4. Verificando arquivos críticos para o deploy")
critical_files = ['wsgi.py', 'run.py', 'app/__init__.py']
for file in critical_files:
    if os.path.exists(file):
        print(f"   {GREEN}✓ {file} encontrado{RESET}")
    else:
        print(f"   {RED}✗ {file} não encontrado{RESET}")

# 5. Criar arquivo .pyhonanywhere.py com informações úteis
print("\n5. Criando arquivo com instruções para PythonAnywhere")
with open('.pythonanywhere.txt', 'w') as f:
    f.write("# Instruções para deploy no PythonAnywhere\n\n")
    f.write("## Configuração do aplicativo web\n")
    f.write("- Source code: /home/SEU_USERNAME/TechCare\n")
    f.write("- Working directory: /home/SEU_USERNAME/TechCare\n")
    f.write("- WSGI configuration file: /var/www/SEU_USERNAME_pythonanywhere_com_wsgi.py\n\n")
    f.write("## Conteúdo do arquivo WSGI:\n")
    f.write("```python\n")
    f.write("import sys\n")
    f.write("import os\n\n")
    f.write("# Adiciona o diretório da aplicação ao PATH\n")
    f.write("path = '/home/SEU_USERNAME/TechCare'\n")
    f.write("if path not in sys.path:\n")
    f.write("    sys.path.append(path)\n\n")
    f.write("# Importa e cria a aplicação\n")
    f.write("from app import create_app\n\n")
    f.write("# Cria a aplicação usando as configurações de produção\n")
    f.write("application = create_app('production')\n")
    f.write("```\n\n")
    f.write("## Comandos para instalar dependências\n")
    f.write("```bash\n")
    f.write("pip install -r requirements_pythonanywhere.txt\n")
    f.write("```\n\n")
    f.write("## Reiniciar aplicação web\n")
    f.write("Após fazer upload dos arquivos ou fazer alterações, use o botão 'Reload' no dashboard.\n")

print(f"   {GREEN}✓ Arquivo .pythonanywhere.txt criado com instruções{RESET}")

# 6. Exibir instruções finais
print(f"\n{BOLD}Resumo da Verificação:{RESET}")
print(f"1. Preparação do ambiente: {GREEN}Concluída{RESET}")
print(f"2. Arquivos críticos: {'Verificados' if all(os.path.exists(f) for f in critical_files) else f'{RED}Alguns não encontrados{RESET}'}")
print(f"3. Dependências compatíveis: {GREEN}requirements_pythonanywhere.txt criado{RESET}")

print(f"\n{BOLD}Próximos Passos:{RESET}")
print(f"1. Faça login no PythonAnywhere (www.pythonanywhere.com)")
print(f"2. Crie um web app (Ubuntu, Python 3.8+, Flask)")
print(f"3. Faça upload dos arquivos do projeto")
print(f"4. Configure o arquivo WSGI conforme as instruções em .pythonanywhere.txt")
print(f"5. Instale as dependências: pip install -r requirements_pythonanywhere.txt")
print(f"6. Clique em 'Reload' para iniciar a aplicação")

print(f"\n{BOLD}Boa sorte com o deploy!{RESET}") 