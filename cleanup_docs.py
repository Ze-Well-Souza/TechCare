#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para limpar arquivos de documentação redundantes após consolidação 
do guia de deploy do TechCare para PythonAnywhere.
"""

import os
import shutil
from datetime import datetime

# Diretório para backups
BACKUP_DIR = "backup_docs"

# Arquivos consolidados no DEPLOY_PYTHONANYWHERE.md
files_to_archive = [
    "README_PYTHONANYWHERE.md",
    "README_DEPLOY_PYTHONANYWHERE.md",
    "README_HOSPEDAGEM_PYTHONANYWHERE.md",
    "techcare_pythonanywhere_guide.md",
    "guia_visual_deploy.md",
    "steps_to_deploy.md",
    "fix_pandas_pythonanywhere.md",
    "setup_virtualenv.md",
    "static_files_config.md",
    "deploy_zewell10_simplificado.md",
    "GUIA_PYTHONANYWHERE.md",
    "pythonanywhere_deploy_guide.md",
    ".pythonanywhere.txt"
]

def main():
    """Função principal que executa o processo de backup e limpeza."""
    print("Iniciando processo de limpeza de documentação redundante...")
    
    # Criar diretório de backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{BACKUP_DIR}_{timestamp}"
    
    if not os.path.exists(backup_path):
        os.makedirs(backup_path)
        print(f"Diretório de backup criado: {backup_path}")
    
    # Fazer backup e remover os arquivos
    for filename in files_to_archive:
        if os.path.exists(filename):
            # Backup
            shutil.copy2(filename, os.path.join(backup_path, filename))
            print(f"Backup do arquivo: {filename}")
            
            # Não removemos agora, apenas mostramos quais arquivos seriam removidos
            print(f"Arquivo a ser removido: {filename}")
    
    print("\nResumo:")
    print(f"Total de arquivos para backup: {len(files_to_archive)}")
    print(f"Diretório de backup: {backup_path}")
    print("\nIMPORTANTE: Este script não removeu nenhum arquivo automaticamente.")
    print("Para concluir a limpeza, execute um dos seguintes comandos:")
    print("\nOpção 1 - Remover individualmente depois de verificar (recomendado):")
    
    for filename in files_to_archive:
        if os.path.exists(filename):
            print(f"rm {filename}")
    
    print("\nOpção 2 - Remover todos de uma vez (cuidado):")
    cmd = "rm " + " ".join(f'"{f}"' for f in files_to_archive if os.path.exists(f))
    print(cmd)
    
    print("\nTodos os arquivos foram copiados para o diretório de backup.")
    print("Certifique-se de que o arquivo DEPLOY_PYTHONANYWHERE.md está atualizado antes de remover os arquivos.")

if __name__ == "__main__":
    main() 