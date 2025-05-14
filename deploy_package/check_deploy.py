"""
Script para verificar a configuração do TechCare no PythonAnywhere

Este script verifica se o ambiente está corretamente configurado,
testando conexões, dependências, diretórios e banco de dados.
"""

import os
import sys
import importlib.util
import platform
from pathlib import Path

def check_environment():
    """Verifica o ambiente Python e o sistema operacional"""
    print("\n=== Verificando Ambiente ===")
    print(f"Python: {sys.version}")
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Arquitetura: {platform.machine()}")

def check_dependencies():
    """Verifica se as dependências principais estão instaladas"""
    print("\n=== Verificando Dependências ===")
    
    required_packages = [
        "flask", "psutil", "sqlalchemy", "flask_login", 
        "flask_wtf", "requests", "gunicorn"
    ]
    
    all_installed = True
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        installed = spec is not None
        status = "✅ Instalado" if installed else "❌ NÃO INSTALADO"
        print(f"{package}: {status}")
        if not installed:
            all_installed = False
    
    if all_installed:
        print("\n✅ Todas as dependências principais estão instaladas.")
    else:
        print("\n❌ Há dependências faltando. Execute:")
        print("   pip install -r requirements_pythonanywhere.txt")

def check_directories():
    """Verifica se os diretórios necessários existem"""
    print("\n=== Verificando Diretórios ===")
    
    base_dir = Path(__file__).resolve().parent
    
    directories = [
        "data",
        "data/diagnostics",
        "data/repair_logs",
        "data/diagnostics_storage",
        "logs"
    ]
    
    all_exist = True
    
    for directory in directories:
        path = os.path.join(base_dir, directory)
        exists = os.path.exists(path)
        status = "✅ Existe" if exists else "❌ NÃO EXISTE"
        print(f"{directory}: {status}")
        if not exists:
            all_exist = False
    
    if all_exist:
        print("\n✅ Todos os diretórios existem.")
    else:
        print("\n❌ Há diretórios faltando. Execute:")
        print("   python setup_pythonanywhere.py")

def check_database():
    """Verifica se o banco de dados existe e é acessível"""
    print("\n=== Verificando Banco de Dados ===")
    
    try:
        base_dir = Path(__file__).resolve().parent
        db_path = os.path.join(base_dir, 'data', 'ulytech.db')
        
        if os.path.exists(db_path):
            print(f"✅ Banco de dados encontrado: {db_path}")
            print(f"   Tamanho: {os.path.getsize(db_path) / 1024:.2f} KB")
            
            # Tenta acessar o banco
            try:
                from app import create_app, db
                app = create_app('production')
                with app.app_context():
                    # Tenta fazer uma consulta simples
                    result = db.session.execute("SELECT 1").fetchone()
                    if result[0] == 1:
                        print("✅ Conexão com o banco de dados validada.")
                    else:
                        print("❌ Conexão com o banco deu um resultado inesperado.")
            except Exception as e:
                print(f"❌ Erro ao acessar o banco de dados: {e}")
        else:
            print(f"❌ Banco de dados não encontrado em: {db_path}")
            print("   Execute: python setup_pythonanywhere.py")
    
    except Exception as e:
        print(f"❌ Erro ao verificar o banco de dados: {e}")

def check_app_config():
    """Verifica se a configuração da aplicação está correta"""
    print("\n=== Verificando Configuração da Aplicação ===")
    
    try:
        from app import create_app
        
        # Verifica ambiente de produção
        os.environ['FLASK_CONFIG'] = 'production'
        app = create_app('production')
        
        print(f"✅ Aplicação criada com sucesso no ambiente: {app.config['ENV']}")
        print(f"✅ Nome da aplicação: {app.config.get('APP_NAME', 'Não definido')}")
        print(f"✅ Versão: {app.config.get('APP_VERSION', 'Não definido')}")
        
        # Verifica configurações críticas
        if app.config.get('SECRET_KEY'):
            print("✅ SECRET_KEY configurada")
        else:
            print("❌ SECRET_KEY não configurada")
        
        if app.config.get('SQLALCHEMY_DATABASE_URI'):
            print(f"✅ Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        else:
            print("❌ SQLALCHEMY_DATABASE_URI não configurada")
        
    except Exception as e:
        print(f"❌ Erro ao verificar configuração da aplicação: {e}")

def run_checks():
    """Executa todas as verificações"""
    print("==================================================")
    print("  VERIFICAÇÃO DO AMBIENTE TECHCARE PYTHONANYWHERE")
    print("==================================================")
    
    try:
        check_environment()
        check_dependencies()
        check_directories()
        check_database()
        check_app_config()
        
        print("\n==================================================")
        print("  RESUMO DA VERIFICAÇÃO")
        print("==================================================")
        print("✅ Verificação de ambiente completa")
        print("Verifique os resultados acima para garantir que tudo está configurado corretamente.")
        print("Se houver problemas, consulte o README_HOSPEDAGEM_PYTHONANYWHERE.md")
    
    except Exception as e:
        print(f"\n❌ Erro durante a verificação: {e}")
        print("Consulte a documentação ou entre em contato com o suporte.")

if __name__ == "__main__":
    run_checks() 