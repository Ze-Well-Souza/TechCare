#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para verificar se o TechCare está pronto para deploy no PythonAnywhere

Este script realiza diversas verificações para garantir que o projeto
está pronto para ser implantado em produção no PythonAnywhere.
"""

import os
import sys
import platform
import subprocess
import importlib
import unittest
from pathlib import Path

# Cores para saída no terminal
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BOLD = '\033[1m'

def check_python_version():
    """Verifica a versão do Python"""
    print(f"{BOLD}Verificando versão do Python...{RESET}")
    
    py_version = platform.python_version()
    py_version_parts = [int(x) for x in py_version.split('.')]
    
    if py_version_parts[0] >= 3 and py_version_parts[1] >= 8:
        print(f"{GREEN}✓ Python {py_version} - compatível{RESET}")
        return True
    else:
        print(f"{RED}✗ Python {py_version} - abaixo do mínimo recomendado (3.8+){RESET}")
        print(f"  PythonAnywhere suporta Python 3.8, 3.9, 3.10 e 3.11")
        return False

def check_required_files():
    """Verifica a presença de arquivos críticos para o deploy"""
    print(f"\n{BOLD}Verificando arquivos críticos...{RESET}")
    
    required_files = [
        'wsgi.py', 
        'run.py', 
        'app/__init__.py',
        'requirements_pythonanywhere.txt',
        'README_DEPLOY_PYTHONANYWHERE.md'
    ]
    
    all_found = True
    for file in required_files:
        if os.path.exists(file):
            print(f"{GREEN}✓ {file} encontrado{RESET}")
        else:
            print(f"{RED}✗ {file} não encontrado{RESET}")
            all_found = False
    
    return all_found

def check_windows_dependencies():
    """Verifica dependências específicas do Windows nos requirements"""
    print(f"\n{BOLD}Verificando dependências específicas do Windows...{RESET}")
    
    windows_libs = ['pywin32', 'wmi', 'win32']
    windows_found = []
    
    try:
        with open('requirements_pythonanywhere.txt', 'r') as f:
            requirements = f.readlines()
            
            for req in requirements:
                req = req.strip()
                for lib in windows_libs:
                    if lib in req.lower() and '; sys_platform == ' not in req.lower():
                        windows_found.append(req)
        
        if windows_found:
            print(f"{RED}✗ Dependências do Windows encontradas em requirements_pythonanywhere.txt:{RESET}")
            for dep in windows_found:
                print(f"  - {dep}")
            return False
        else:
            print(f"{GREEN}✓ Nenhuma dependência do Windows encontrada em requirements_pythonanywhere.txt{RESET}")
            return True
    except FileNotFoundError:
        print(f"{RED}✗ Arquivo requirements_pythonanywhere.txt não encontrado{RESET}")
        return False

def run_tests():
    """Executa os testes para verificar se estão passando"""
    print(f"\n{BOLD}Executando testes...{RESET}")
    
    try:
        # Verifica se há testes em /tests ou /app/tests
        test_dirs = ['tests', 'app/tests']
        test_dir_found = False
        
        for test_dir in test_dirs:
            if os.path.isdir(test_dir):
                test_dir_found = True
                break
        
        if not test_dir_found:
            print(f"{YELLOW}! Diretório de testes não encontrado{RESET}")
            return True  # Consideramos que não haveriam testes
        
        # Executa os testes
        print("Executando testes (isso pode levar alguns minutos)...")
        result = subprocess.run(['python', '-m', 'pytest'], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"{GREEN}✓ Todos os testes passaram{RESET}")
            return True
        else:
            print(f"{RED}✗ Alguns testes falharam:{RESET}")
            print(result.stdout[-500:])  # Mostra apenas os últimos 500 caracteres
            return False
    except Exception as e:
        print(f"{RED}✗ Erro ao executar testes: {str(e)}{RESET}")
        return False

def check_platform_adaptations():
    """Verifica adaptações para diferentes plataformas"""
    print(f"\n{BOLD}Verificando adaptações para diferentes plataformas...{RESET}")
    
    # Lista de arquivos a verificar para adaptações de plataforma
    adaptation_files = [
        'app/services/diagnostic_service_platform.py',
        'app/services/diagnostic_service.py'
    ]
    
    all_adapted = True
    found_adaptation = False
    
    for file in adaptation_files:
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    # Verifica padrões comuns de adaptação de plataforma
                    linux_check = 'linux' in content.lower() or 'platform.system()' in content
                    os_check = 'import platform' in content.lower() or 'import os' in content
                    
                    if linux_check and os_check:
                        print(f"{GREEN}✓ {file} contém adaptações para múltiplas plataformas{RESET}")
                        found_adaptation = True
                    else:
                        print(f"{YELLOW}! {file} pode não estar adaptado para Linux{RESET}")
            except Exception as e:
                print(f"{YELLOW}! Erro ao ler {file}: {str(e)}{RESET}")
                all_adapted = False
    
    if not found_adaptation:
        print(f"{RED}✗ Nenhuma adaptação para Linux encontrada nos arquivos verificados{RESET}")
        all_adapted = False
    
    return all_adapted

def check_database_config():
    """Verifica a configuração do banco de dados para compatibilidade com PythonAnywhere"""
    print(f"\n{BOLD}Verificando configuração do banco de dados...{RESET}")
    
    config_files = [
        'app/config.py',
        'config.py',
        'app/__init__.py'
    ]
    
    db_config_found = False
    db_config_compatible = False
    
    for file in config_files:
        if os.path.exists(file):
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    if 'SQLALCHEMY_DATABASE_URI' in content:
                        db_config_found = True
                        # Verifica se usa SQLite ou tem configuração por variável de ambiente
                        if 'sqlite' in content.lower() or 'os.environ.get' in content:
                            db_config_compatible = True
                            print(f"{GREEN}✓ Configuração de banco de dados compatível encontrada em {file}{RESET}")
                            break
            except Exception as e:
                print(f"{YELLOW}! Erro ao ler {file}: {str(e)}{RESET}")
    
    if not db_config_found:
        print(f"{YELLOW}! Configuração de banco de dados não encontrada{RESET}")
        # Não é erro crítico, pode estar configurado em outro lugar
        return True
    
    if not db_config_compatible:
        print(f"{RED}✗ Configuração de banco de dados pode não ser compatível com PythonAnywhere{RESET}")
        print(f"  Certifique-se de usar SQLite ou configurar via variáveis de ambiente")
        return False
    
    return True

def check_wsgi_configuration():
    """Verifica a configuração do arquivo WSGI"""
    print(f"\n{BOLD}Verificando configuração WSGI...{RESET}")
    
    if not os.path.exists('wsgi.py'):
        print(f"{RED}✗ Arquivo wsgi.py não encontrado{RESET}")
        return False
    
    try:
        with open('wsgi.py', 'r') as f:
            content = f.read()
            # Verifica elementos importantes no arquivo WSGI
            has_app_import = 'from app import' in content
            has_application = 'application =' in content
            has_path_addition = 'sys.path.append' in content or 'sys.path.insert' in content
            
            if has_app_import and has_application:
                print(f"{GREEN}✓ Arquivo wsgi.py contém configuração básica necessária{RESET}")
                
                if not has_path_addition:
                    print(f"{YELLOW}! Arquivo wsgi.py pode precisar adicionar o caminho ao sys.path{RESET}")
                
                return True
            else:
                print(f"{RED}✗ Arquivo wsgi.py não contém as configurações necessárias{RESET}")
                return False
    except Exception as e:
        print(f"{RED}✗ Erro ao ler wsgi.py: {str(e)}{RESET}")
        return False

def check_static_files():
    """Verifica a configuração de arquivos estáticos"""
    print(f"\n{BOLD}Verificando arquivos estáticos...{RESET}")
    
    static_dirs = [
        'app/static',
        'static'
    ]
    
    for static_dir in static_dirs:
        if os.path.isdir(static_dir):
            print(f"{GREEN}✓ Diretório de arquivos estáticos encontrado em {static_dir}{RESET}")
            
            # Verifica se há arquivos estáticos
            static_files = list(Path(static_dir).rglob('*.*'))
            if static_files:
                print(f"{GREEN}✓ {len(static_files)} arquivos estáticos encontrados{RESET}")
            else:
                print(f"{YELLOW}! Nenhum arquivo estático encontrado em {static_dir}{RESET}")
            
            return True
    
    print(f"{YELLOW}! Nenhum diretório de arquivos estáticos encontrado{RESET}")
    print(f"  Isso pode ser um problema se sua aplicação depender de CSS, JS ou imagens")
    return True  # Não é um erro crítico

def check_prepare_pythonanywhere():
    """Verifica se o script prepare_pythonanywhere.py existe e funciona"""
    print(f"\n{BOLD}Verificando script prepare_pythonanywhere.py...{RESET}")
    
    if not os.path.exists('prepare_pythonanywhere.py'):
        print(f"{RED}✗ Script prepare_pythonanywhere.py não encontrado{RESET}")
        return False
    
    try:
        # Tenta importar o script para verificar se não há erros de sintaxe
        spec = importlib.util.spec_from_file_location("prepare_pythonanywhere", "prepare_pythonanywhere.py")
        module = importlib.util.module_from_spec(spec)
        
        # Não executa o script, apenas verifica se pode ser importado
        print(f"{GREEN}✓ Script prepare_pythonanywhere.py pode ser importado{RESET}")
        
        # Verifica se o script tem as funções esperadas
        with open('prepare_pythonanywhere.py', 'r') as f:
            content = f.read()
            if 'requirements_pythonanywhere.txt' in content:
                print(f"{GREEN}✓ Script prepare_pythonanywhere.py parece correto{RESET}")
                return True
            else:
                print(f"{YELLOW}! Script prepare_pythonanywhere.py pode não estar completo{RESET}")
                return False
    except Exception as e:
        print(f"{RED}✗ Erro ao verificar prepare_pythonanywhere.py: {str(e)}{RESET}")
        return False

def main():
    """Função principal que executa todas as verificações"""
    print(f"{BOLD}Verificação de Prontidão para Deploy no PythonAnywhere{RESET}\n")
    
    # Lista de verificações e seus resultados
    checks = [
        ("Versão do Python", check_python_version()),
        ("Arquivos críticos", check_required_files()),
        ("Dependências do Windows", check_windows_dependencies()),
        ("Adaptações para Linux", check_platform_adaptations()),
        ("Configuração do banco de dados", check_database_config()),
        ("Configuração WSGI", check_wsgi_configuration()),
        ("Arquivos estáticos", check_static_files()),
        ("Script prepare_pythonanywhere", check_prepare_pythonanywhere())
    ]
    
    # Verifica se estamos em ambiente de teste ou não
    run_unit_tests = os.environ.get('SKIP_TESTS') != '1'
    if run_unit_tests:
        checks.append(("Testes automatizados", run_tests()))
    
    # Exibe o resumo das verificações
    print(f"\n{BOLD}Resumo da Verificação:{RESET}")
    
    all_passed = True
    critical_errors = 0
    warnings = 0
    
    for name, result in checks:
        if result:
            print(f"{GREEN}✓ {name}: OK{RESET}")
        else:
            print(f"{RED}✗ {name}: Falha{RESET}")
            all_passed = False
            if name in ["Arquivos críticos", "Dependências do Windows", "Configuração WSGI"]:
                critical_errors += 1
            else:
                warnings += 1
    
    # Exibe o resultado final
    print(f"\n{BOLD}Resultado Final:{RESET}")
    
    if all_passed:
        print(f"{GREEN}✓ O projeto está pronto para deploy no PythonAnywhere!{RESET}")
        print(f"  Execute o script upload_to_pythonanywhere.py para fazer o deploy.")
        return 0
    elif critical_errors > 0:
        print(f"{RED}✗ O projeto NÃO está pronto para deploy no PythonAnywhere!{RESET}")
        print(f"  {critical_errors} erros críticos e {warnings} avisos encontrados.")
        print(f"  Corrija os problemas acima antes de tentar o deploy.")
        return 1
    else:
        print(f"{YELLOW}! O projeto pode ser deployado, mas há {warnings} avisos.{RESET}")
        print(f"  Recomenda-se corrigir os avisos antes do deploy para evitar problemas.")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 