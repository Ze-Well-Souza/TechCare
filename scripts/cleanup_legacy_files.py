#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para limpar arquivos legados da versão JavaScript do projeto TechCare
que foram migrados para a nova versão em Python/Flask.

Este script deve ser executado da raiz do projeto para remover arquivos
que não são mais necessários após a migração.
"""

import os
import shutil
from pathlib import Path
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Arquivos JavaScript que foram migrados para Python
js_files = [
    'interactive.js',
    'agente.js',
    'guia-manutencao.js',
    'conversao.js',
    'correcao.js',
    'database.js',
    'diagnostico.js',
    'main.js',
    'relatorio.js',
    'service-worker.js',
    'js'  # Diretório js
]

# Arquivos HTML que foram migrados para templates Flask
html_files = [
    'index.html',
    'diagnostico.html',
    'suporte.html',
    'historico.html'
]

# Arquivos CSS que foram migrados para arquivos estáticos Flask
css_files = [
    'diagnostico.css',
    'responsive.css',
    'styles.css',
    'css'  # Diretório css
]

# Outros arquivos que não são mais necessários
other_files = [
    'manifest.json',
    'package.json',
    'favicon.ico',
    'icon-192.png',
    'icon-512.png',
    'robots.txt',
    'sitemap.xml'
]

def confirm_removal(files):
    """Solicita confirmação antes de remover os arquivos"""
    print("\nArquivos que serão removidos:")
    for f in files:
        print(f"- {f}")
    
    response = input("\nDeseja continuar com a remoção desses arquivos? (s/n): ")
    return response.lower() == 's'

def backup_files(files, backup_dir):
    """Faz backup dos arquivos antes de removê-los"""
    os.makedirs(backup_dir, exist_ok=True)
    logger.info(f"Realizando backup dos arquivos para {backup_dir}")
    
    for file in files:
        try:
            if os.path.exists(file):
                if os.path.isdir(file):
                    dest = os.path.join(backup_dir, file)
                    shutil.copytree(file, dest, dirs_exist_ok=True)
                    logger.info(f"Backup do diretório {file} para {dest}")
                else:
                    shutil.copy2(file, backup_dir)
                    logger.info(f"Backup do arquivo {file} para {backup_dir}")
        except Exception as e:
            logger.error(f"Erro ao fazer backup de {file}: {str(e)}")

def remove_files(files):
    """Remove os arquivos especificados"""
    for file in files:
        try:
            if os.path.exists(file):
                if os.path.isdir(file):
                    shutil.rmtree(file)
                    logger.info(f"Diretório removido: {file}")
                else:
                    os.remove(file)
                    logger.info(f"Arquivo removido: {file}")
            else:
                logger.warning(f"Arquivo não encontrado: {file}")
        except Exception as e:
            logger.error(f"Erro ao remover {file}: {str(e)}")

def main():
    """Função principal do script"""
    # Garantir que o script está sendo executado do diretório correto
    if not os.path.exists('techcare_python'):
        logger.error("Este script deve ser executado da raiz do projeto TechCare.")
        return
    
    # Juntar todas as listas de arquivos
    all_files = js_files + html_files + css_files + other_files
    
    # Criar diretório de backup
    backup_dir = 'techcare_python/backup_legacy_files'
    
    # Confirmar com o usuário
    if confirm_removal(all_files):
        # Fazer backup antes de remover
        backup_files(all_files, backup_dir)
        
        # Remover os arquivos
        remove_files(all_files)
        
        logger.info(f"Limpeza concluída. Backup disponível em {backup_dir}")
        print(f"\nLimpeza concluída com sucesso!")
        print(f"Um backup dos arquivos removidos foi salvo em {backup_dir}")
    else:
        logger.info("Operação cancelada pelo usuário.")
        print("\nOperação cancelada. Nenhum arquivo foi removido.")

if __name__ == "__main__":
    main() 