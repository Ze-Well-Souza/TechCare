"""
Script para inicialização do TechCare no PythonAnywhere

Este script deve ser executado após o upload do código para o PythonAnywhere
para criar os diretórios necessários e inicializar o banco de dados.
"""

import os
import sys
from pathlib import Path

def setup_pythonanywhere():
    """
    Configura o ambiente do TechCare no PythonAnywhere
    """
    print("=== Configuração do TechCare no PythonAnywhere ===")
    
    # Diretório base do projeto
    base_dir = Path(__file__).resolve().parent
    
    # Cria diretórios necessários
    directories = [
        "data",
        "data/diagnostics",
        "data/repair_logs",
        "data/diagnostics_storage",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(os.path.join(base_dir, directory), exist_ok=True)
        print(f"Diretório criado: {directory}")
    
    # Inicializa o banco de dados
    print("\nInicializando o banco de dados...")
    
    try:
        from app import create_app, db
        app = create_app('production')
        with app.app_context():
            db.create_all()
            print("Banco de dados inicializado com sucesso!")
    except Exception as e:
        print(f"Erro ao inicializar o banco de dados: {e}")
        print("Você pode precisar inicializar o banco manualmente.")
    
    print("\n=== Configuração concluída! ===")
    print("\nAgora você pode:")
    print("1. Configurar a aplicação web na interface do PythonAnywhere")
    print("2. Configurar o arquivo WSGI conforme o guia")
    print("3. Configurar os arquivos estáticos")
    print("4. Clicar em 'Reload' para iniciar a aplicação")

if __name__ == "__main__":
    setup_pythonanywhere() 