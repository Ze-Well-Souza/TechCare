import os
import shutil
import zipfile
import logging
from datetime import datetime, UTC
import subprocess
import json
from sqlalchemy import inspect
from app.extensions import db
from app.models.system_config import SystemConfig
from app.models.audit_log import AuditLog, AuditLogType

class BackupService:
    """
    Serviço para gerenciamento de backups
    """
    
    BACKUP_BASE_DIR = os.path.join(os.getcwd(), 'backups')
    
    @classmethod
    def initialize_backup_directory(cls):
        """
        Inicializar diretório de backups
        """
        os.makedirs(cls.BACKUP_BASE_DIR, exist_ok=True)
    
    @classmethod
    def create_database_backup(cls, description=None):
        """
        Criar backup do banco de dados
        
        :param description: Descrição opcional do backup
        :return: Dicionário com resultado do backup
        """
        try:
            # Configurações de backup do banco de dados
            db_config = SystemConfig.get_config('database_backup_config', {
                'type': 'sqlite',
                'max_backups': 10
            })
            
            # Gerar nome do arquivo de backup
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            backup_filename = f'db_backup_{timestamp}.sqlite'
            backup_path = os.path.join(cls.BACKUP_BASE_DIR, backup_filename)
            
            # Backup de banco de dados SQLite
            if db_config['type'] == 'sqlite':
                # Obter caminho do banco de dados atual
                engine = db.engine
                inspector = inspect(engine)
                current_db_path = engine.url.database
                
                # Copiar arquivo de banco de dados
                shutil.copy2(current_db_path, backup_path)
            
            # Registrar log de auditoria
            backup_log = AuditLog.log_activity(
                user_id=None,  # Sistema
                action_type=AuditLogType.SYSTEM_BACKUP,
                description=description or 'Backup de banco de dados',
                details={
                    'backup_file': backup_filename,
                    'backup_path': backup_path
                }
            )
            
            # Gerenciar número máximo de backups
            cls._manage_backup_retention(db_config.get('max_backups', 10))
            
            return {
                'success': True,
                'message': 'Backup de banco de dados criado com sucesso',
                'backup_file': backup_filename,
                'backup_path': backup_path
            }
        
        except Exception as e:
            logging.error(f"Erro ao criar backup de banco de dados: {e}")
            return {
                'success': False,
                'message': 'Erro ao criar backup de banco de dados',
                'error': str(e)
            }
    
    @classmethod
    def create_file_backup(cls, directories=None, description=None):
        """
        Criar backup de arquivos e diretórios
        
        :param directories: Lista de diretórios para backup
        :param description: Descrição opcional do backup
        :return: Dicionário com resultado do backup
        """
        try:
            # Configurações de backup de arquivos
            file_backup_config = SystemConfig.get_config('file_backup_config', {
                'default_dirs': ['app', 'config', 'migrations'],
                'max_backups': 5
            })
            
            # Usar diretórios padrão se não especificados
            if not directories:
                directories = file_backup_config.get('default_dirs', [])
            
            # Gerar nome do arquivo de backup
            timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
            backup_filename = f'files_backup_{timestamp}.zip'
            backup_path = os.path.join(cls.BACKUP_BASE_DIR, backup_filename)
            
            # Criar arquivo zip
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for directory in directories:
                    # Verificar se diretório existe
                    if not os.path.exists(directory):
                        logging.warning(f"Diretório {directory} não encontrado")
                        continue
                    
                    # Adicionar diretório ao zip
                    for root, _, files in os.walk(directory):
                        for file in files:
                            file_path = os.path.join(root, file)
                            zipf.write(file_path, 
                                       arcname=os.path.relpath(file_path, 
                                                               start=os.getcwd()))
            
            # Registrar log de auditoria
            backup_log = AuditLog.log_activity(
                user_id=None,  # Sistema
                action_type=AuditLogType.SYSTEM_BACKUP,
                description=description or 'Backup de arquivos',
                details={
                    'backup_file': backup_filename,
                    'backup_path': backup_path,
                    'directories': directories
                }
            )
            
            # Gerenciar número máximo de backups
            cls._manage_backup_retention(
                file_backup_config.get('max_backups', 5), 
                backup_type='files'
            )
            
            return {
                'success': True,
                'message': 'Backup de arquivos criado com sucesso',
                'backup_file': backup_filename,
                'backup_path': backup_path,
                'directories': directories
            }
        
        except Exception as e:
            logging.error(f"Erro ao criar backup de arquivos: {e}")
            return {
                'success': False,
                'message': 'Erro ao criar backup de arquivos',
                'error': str(e)
            }
    
    @classmethod
    def _manage_backup_retention(cls, max_backups, backup_type='database'):
        """
        Gerenciar número máximo de backups
        
        :param max_backups: Número máximo de backups a manter
        :param backup_type: Tipo de backup (database ou files)
        """
        try:
            # Padrão de nome de arquivo baseado no tipo
            pattern = 'db_backup_' if backup_type == 'database' else 'files_backup_'
            
            # Listar backups existentes
            backups = [
                f for f in os.listdir(cls.BACKUP_BASE_DIR) 
                if f.startswith(pattern)
            ]
            
            # Ordenar backups por data (do mais antigo para o mais recente)
            backups.sort()
            
            # Excluir backups excedentes
            while len(backups) > max_backups:
                oldest_backup = backups.pop(0)
                os.remove(os.path.join(cls.BACKUP_BASE_DIR, oldest_backup))
        
        except Exception as e:
            logging.error(f"Erro ao gerenciar retenção de backups: {e}")
    
    @classmethod
    def restore_database_backup(cls, backup_filename, user_id=None):
        """
        Restaurar backup de banco de dados
        
        :param backup_filename: Nome do arquivo de backup
        :param user_id: ID do usuário que está restaurando
        :return: Dicionário com resultado da restauração
        """
        try:
            # Caminho completo do backup
            backup_path = os.path.join(cls.BACKUP_BASE_DIR, backup_filename)
            
            # Verificar se backup existe
            if not os.path.exists(backup_path):
                return {
                    'success': False,
                    'message': 'Arquivo de backup não encontrado'
                }
            
            # Obter caminho do banco de dados atual
            engine = db.engine
            current_db_path = engine.url.database
            
            # Fechar conexões existentes
            db.session.close()
            engine.dispose()
            
            # Copiar backup para o banco de dados atual
            shutil.copy2(backup_path, current_db_path)
            
            # Registrar log de auditoria
            AuditLog.log_activity(
                user_id=user_id,
                action_type=AuditLogType.SYSTEM_RESTORE,
                description='Restauração de backup de banco de dados',
                details={
                    'backup_file': backup_filename,
                    'backup_path': backup_path
                }
            )
            
            return {
                'success': True,
                'message': 'Backup de banco de dados restaurado com sucesso'
            }
        
        except Exception as e:
            logging.error(f"Erro ao restaurar backup de banco de dados: {e}")
            return {
                'success': False,
                'message': 'Erro ao restaurar backup de banco de dados',
                'error': str(e)
            }
    
    @classmethod
    def restore_file_backup(cls, backup_filename, user_id=None):
        """
        Restaurar backup de arquivos
        
        :param backup_filename: Nome do arquivo de backup
        :param user_id: ID do usuário que está restaurando
        :return: Dicionário com resultado da restauração
        """
        try:
            # Caminho completo do backup
            backup_path = os.path.join(cls.BACKUP_BASE_DIR, backup_filename)
            
            # Verificar se backup existe
            if not os.path.exists(backup_path):
                return {
                    'success': False,
                    'message': 'Arquivo de backup não encontrado'
                }
            
            # Extrair backup
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                zipf.extractall(os.getcwd())
            
            # Registrar log de auditoria
            AuditLog.log_activity(
                user_id=user_id,
                action_type=AuditLogType.SYSTEM_RESTORE,
                description='Restauração de backup de arquivos',
                details={
                    'backup_file': backup_filename,
                    'backup_path': backup_path
                }
            )
            
            return {
                'success': True,
                'message': 'Backup de arquivos restaurado com sucesso'
            }
        
        except Exception as e:
            logging.error(f"Erro ao restaurar backup de arquivos: {e}")
            return {
                'success': False,
                'message': 'Erro ao restaurar backup de arquivos',
                'error': str(e)
            }
    
    @classmethod
    def list_backups(cls, backup_type=None):
        """
        Listar backups disponíveis
        
        :param backup_type: Tipo de backup (database ou files)
        :return: Lista de backups
        """
        try:
            # Listar todos os backups
            all_backups = os.listdir(cls.BACKUP_BASE_DIR)
            
            # Filtrar por tipo, se especificado
            if backup_type == 'database':
                backups = [b for b in all_backups if b.startswith('db_backup_')]
            elif backup_type == 'files':
                backups = [b for b in all_backups if b.startswith('files_backup_')]
            else:
                backups = all_backups
            
            # Ordenar backups por data (do mais recente para o mais antigo)
            backups.sort(reverse=True)
            
            return {
                'backups': backups,
                'backup_dir': cls.BACKUP_BASE_DIR
            }
        
        except Exception as e:
            logging.error(f"Erro ao listar backups: {e}")
            return {
                'backups': [],
                'backup_dir': cls.BACKUP_BASE_DIR
            }
    
    @classmethod
    def schedule_backup(cls):
        """
        Agendar backups automáticos
        """
        try:
            # Configurações de backup agendado
            backup_schedule = SystemConfig.get_config('backup_schedule', {
                'database_interval': 'daily',
                'files_interval': 'weekly'
            })
            
            # Implementação de agendamento de backup
            # Nota: Em produção, usar Celery, APScheduler ou similar
            logging.info("Backup agendado configurado")
            
            return {
                'success': True,
                'schedule': backup_schedule
            }
        
        except Exception as e:
            logging.error(f"Erro ao agendar backups: {e}")
            return {
                'success': False,
                'error': str(e)
            }
