#!/usr/bin/env python
"""
Script para realizar backup automático do banco de dados SQLite.
- Cria cópias de segurança com data e hora no nome do arquivo
- Mantém um número configurável de backups
- Pode ser executado manualmente ou agendado como tarefa
- Suporta tanto ambientes Windows quanto Linux
"""

import os
import sys
import shutil
import sqlite3
import logging
import argparse
import datetime
import configparser
import zipfile
from pathlib import Path

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/database_backup.log', 'a')
    ]
)

logger = logging.getLogger('backup_database')

# Criar diretório de logs se não existir
os.makedirs('logs', exist_ok=True)

def get_database_path():
    """
    Determina o caminho do banco de dados com base no ambiente.
    
    Returns:
        str: Caminho para o arquivo de banco de dados SQLite
    """
    # Verifica se existe um arquivo config.py
    if os.path.exists('config.py'):
        import importlib.util
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        # Verifica se há um caminho de banco de dados definido na configuração
        if hasattr(config, 'SQLALCHEMY_DATABASE_URI'):
            db_uri = config.SQLALCHEMY_DATABASE_URI
            # Extrai o caminho do arquivo do URI SQLite
            if db_uri.startswith('sqlite:///'):
                return db_uri.replace('sqlite:///', '')
    
    # Caminhos padrão para procurar o banco de dados
    default_paths = [
        'instance/techcare.db',  # Caminho padrão do Flask
        'app/techcare.db',
        'techcare.db'
    ]
    
    for path in default_paths:
        if os.path.exists(path):
            return path
    
    logger.warning("Banco de dados não encontrado nos caminhos padrão!")
    return None

def create_backup(db_path, backup_dir='backups', compress=True, max_backups=10):
    """
    Cria um backup do banco de dados SQLite.
    
    Args:
        db_path (str): Caminho para o banco de dados
        backup_dir (str): Diretório onde os backups serão armazenados
        compress (bool): Se True, compacta o backup em um arquivo zip
        max_backups (int): Número máximo de backups a manter
        
    Returns:
        bool: True se o backup foi bem-sucedido, False caso contrário
    """
    try:
        # Criar diretório de backup se não existir
        os.makedirs(backup_dir, exist_ok=True)
        
        # Gerar nome do arquivo de backup com timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        db_filename = os.path.basename(db_path)
        backup_filename = f"{os.path.splitext(db_filename)[0]}_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Verificar se o banco está íntegro
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            integrity_result = cursor.fetchone()[0]
            if integrity_result != "ok":
                logger.error(f"Verificação de integridade do banco de dados falhou: {integrity_result}")
                conn.close()
                return False
            conn.close()
        except Exception as e:
            logger.error(f"Erro ao verificar integridade do banco de dados: {str(e)}")
            return False
        
        # Criar backup usando cópia direta do arquivo
        logger.info(f"Criando backup do banco de dados {db_path} para {backup_path}")
        shutil.copy2(db_path, backup_path)
        
        # Comprimir backup em arquivo zip se solicitado
        if compress:
            zip_path = f"{backup_path}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(backup_path, os.path.basename(backup_path))
            
            # Remover o arquivo .db original após comprimí-lo
            os.remove(backup_path)
            backup_path = zip_path
            logger.info(f"Backup comprimido para {zip_path}")
        
        # Limitar o número de backups mantidos
        if max_backups > 0:
            cleanup_old_backups(backup_dir, max_backups, compress)
        
        logger.info("Backup concluído com sucesso")
        return True
    
    except Exception as e:
        logger.error(f"Erro ao criar backup: {str(e)}")
        return False

def cleanup_old_backups(backup_dir, max_backups, compressed=True):
    """
    Remove backups antigos mantendo apenas o número especificado.
    
    Args:
        backup_dir (str): Diretório onde os backups estão armazenados
        max_backups (int): Número máximo de backups a manter
        compressed (bool): Se True, procura por arquivos .zip, caso contrário .db
    """
    try:
        extension = ".zip" if compressed else ".db"
        backup_files = list(Path(backup_dir).glob(f"*{extension}"))
        
        # Ordenar arquivos por data de modificação (mais recente primeiro)
        backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        
        # Remover arquivos excedentes
        if len(backup_files) > max_backups:
            for old_file in backup_files[max_backups:]:
                logger.info(f"Removendo backup antigo: {old_file}")
                os.remove(old_file)
    
    except Exception as e:
        logger.error(f"Erro ao limpar backups antigos: {str(e)}")

def validate_backup(backup_path):
    """
    Valida se o backup está íntegro.
    
    Args:
        backup_path (str): Caminho para o arquivo de backup
        
    Returns:
        bool: True se o backup é válido, False caso contrário
    """
    try:
        if backup_path.endswith('.zip'):
            # Extrair o arquivo zip para validação
            temp_dir = os.path.join(os.path.dirname(backup_path), 'temp_validation')
            os.makedirs(temp_dir, exist_ok=True)
            
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                db_file = zipf.namelist()[0]  # Pega o primeiro arquivo do zip
                zipf.extract(db_file, temp_dir)
                
                extracted_db = os.path.join(temp_dir, db_file)
                
                # Validar o banco de dados extraído
                conn = sqlite3.connect(extracted_db)
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check;")
                integrity_result = cursor.fetchone()[0]
                conn.close()
                
                # Limpar arquivos temporários
                shutil.rmtree(temp_dir)
                
                return integrity_result == "ok"
        else:
            # Validar banco de dados diretamente
            conn = sqlite3.connect(backup_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA integrity_check;")
            integrity_result = cursor.fetchone()[0]
            conn.close()
            
            return integrity_result == "ok"
    
    except Exception as e:
        logger.error(f"Erro ao validar backup: {str(e)}")
        return False

def configure_scheduled_backup(frequency='daily'):
    """
    Configura o agendamento automático do backup.
    
    Args:
        frequency (str): Frequência de backup ('daily', 'weekly', 'monthly')
        
    Returns:
        bool: True se o agendamento foi configurado com sucesso, False caso contrário
    """
    try:
        is_windows = os.name == 'nt'
        current_dir = os.path.abspath(os.path.dirname(__file__))
        script_path = os.path.join(current_dir, 'backup_database.py')
        
        if is_windows:
            # Configurar tarefa agendada no Windows
            import subprocess
            
            # Definir horário com base na frequência
            if frequency == 'daily':
                schedule_time = "03:00"
                schedule_modifier = "/SC DAILY"
            elif frequency == 'weekly':
                schedule_time = "02:00"
                schedule_modifier = "/SC WEEKLY /D SUN"
            elif frequency == 'monthly':
                schedule_time = "01:00"
                schedule_modifier = "/SC MONTHLY /D 1"
            else:
                logger.error(f"Frequência desconhecida: {frequency}")
                return False
            
            # Criar comando para o agendador de tarefas do Windows
            task_name = "TechCareDBBackup"
            command = f'schtasks /CREATE /TN "{task_name}" {schedule_modifier} /ST {schedule_time} /TR "python {script_path}" /F'
            
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Erro ao configurar tarefa agendada: {result.stderr}")
                return False
            
            logger.info(f"Tarefa agendada configurada com sucesso: {task_name}")
            return True
            
        else:
            # Configurar cron job no Linux
            import subprocess
            
            # Definir expressão cron com base na frequência
            if frequency == 'daily':
                cron_expr = "0 3 * * *"  # 3h da manhã todos os dias
            elif frequency == 'weekly':
                cron_expr = "0 2 * * 0"  # 2h da manhã aos domingos
            elif frequency == 'monthly':
                cron_expr = "0 1 1 * *"  # 1h da manhã no primeiro dia do mês
            else:
                logger.error(f"Frequência desconhecida: {frequency}")
                return False
            
            # Criar cron job temporário
            cron_file = "/tmp/techcare_backup_cron"
            with open(cron_file, 'w') as f:
                f.write(f"{cron_expr} python {script_path}\n")
            
            # Instalar cron job
            result = subprocess.run(f"crontab -l > {cron_file}.existing 2>/dev/null || true", shell=True)
            with open(f"{cron_file}.existing", 'a') as f:
                f.write(f"\n# TechCare backup automático\n{cron_expr} python {script_path}\n")
            
            result = subprocess.run(f"crontab {cron_file}.existing", shell=True, capture_output=True, text=True)
            if result.returncode != 0:
                logger.error(f"Erro ao configurar cron job: {result.stderr}")
                return False
            
            # Limpar arquivos temporários
            os.remove(cron_file)
            os.remove(f"{cron_file}.existing")
            
            logger.info(f"Cron job configurado com sucesso: {cron_expr}")
            return True
            
    except Exception as e:
        logger.error(f"Erro ao configurar backup agendado: {str(e)}")
        return False

def main():
    """Função principal do script de backup"""
    parser = argparse.ArgumentParser(description='Script de backup automático para banco de dados TechCare')
    parser.add_argument('--backup-dir', default='backups', help='Diretório para armazenar os backups')
    parser.add_argument('--compress', action='store_true', default=True, help='Comprimir o backup em um arquivo zip')
    parser.add_argument('--max-backups', type=int, default=10, help='Número máximo de backups a manter')
    parser.add_argument('--db-path', help='Caminho para o banco de dados (opcional)')
    parser.add_argument('--schedule', choices=['daily', 'weekly', 'monthly'], help='Agendar backup automático')
    
    args = parser.parse_args()
    
    # Se solicitado apenas para agendar o backup
    if args.schedule:
        success = configure_scheduled_backup(args.schedule)
        if success:
            logger.info(f"Backup agendado com frequência {args.schedule}")
        else:
            logger.error("Falha ao agendar backup")
        return
    
    # Determinar o caminho do banco de dados
    db_path = args.db_path or get_database_path()
    if not db_path:
        logger.error("Banco de dados não encontrado!")
        return
    
    if not os.path.exists(db_path):
        logger.error(f"Arquivo de banco de dados não encontrado: {db_path}")
        return
    
    # Criar o backup
    success = create_backup(
        db_path, 
        backup_dir=args.backup_dir, 
        compress=args.compress, 
        max_backups=args.max_backups
    )
    
    if success:
        # Validar o backup criado
        backup_files = os.listdir(args.backup_dir)
        if backup_files:
            latest_backup = sorted(
                [os.path.join(args.backup_dir, f) for f in backup_files], 
                key=os.path.getmtime, 
                reverse=True
            )[0]
            
            if validate_backup(latest_backup):
                logger.info(f"Backup validado com sucesso: {latest_backup}")
            else:
                logger.error(f"Validação de backup falhou: {latest_backup}")
    else:
        logger.error("Falha ao criar backup")

if __name__ == "__main__":
    main() 