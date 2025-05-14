import subprocess
import signal
import psutil
import logging
import os
import platform
from app.models.service_status import ServiceStatus, ServiceStatusType
from app.models.user_activity_log import UserActivityLog, UserActivityType
from app.extensions import db

class ServiceManagementService:
    """
    Serviço para gerenciamento de serviços do sistema
    """
    
    @classmethod
    def _get_service_pid(cls, service_name):
        """
        Obter PID de um serviço
        
        :param service_name: Nome do serviço
        :return: PID do serviço ou None
        """
        service_map = {
            'web_server': cls._find_web_server_pid,
            'database': cls._find_database_pid,
            'task_queue': cls._find_task_queue_pid,
            'cache_service': cls._find_cache_service_pid
        }
        
        pid_finder = service_map.get(service_name)
        return pid_finder() if pid_finder else None
    
    @classmethod
    def _find_web_server_pid(cls):
        """
        Encontrar PID do servidor web
        """
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if 'gunicorn' in proc.info['name'] or 'flask' in proc.info['name']:
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return None
    
    @classmethod
    def _find_database_pid(cls):
        """
        Encontrar PID do banco de dados
        """
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if 'postgres' in proc.info['name'] or 'mysql' in proc.info['name']:
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return None
    
    @classmethod
    def _find_task_queue_pid(cls):
        """
        Encontrar PID da fila de tarefas
        """
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if 'celery' in proc.info['name']:
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return None
    
    @classmethod
    def _find_cache_service_pid(cls):
        """
        Encontrar PID do serviço de cache
        """
        for proc in psutil.process_iter(['name', 'cmdline']):
            try:
                if 'redis' in proc.info['name']:
                    return proc.pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return None
    
    @classmethod
    def stop_service(cls, service_name, user_id=None):
        """
        Parar um serviço
        
        :param service_name: Nome do serviço
        :param user_id: ID do usuário que solicitou a parada
        :return: Resultado da operação
        """
        try:
            pid = cls._get_service_pid(service_name)
            
            if not pid:
                return {
                    'success': False,
                    'message': f'Serviço {service_name} não encontrado'
                }
            
            # Tentar parar o processo
            os.kill(pid, signal.SIGTERM)
            
            # Atualizar status do serviço
            ServiceStatus.update_service_status(
                service_name=service_name,
                status=ServiceStatusType.STOPPED,
                description=f'Serviço {service_name} parado manualmente'
            )
            
            # Registrar atividade
            if user_id:
                UserActivityLog.log_activity(
                    user_id=user_id,
                    activity_type=UserActivityType.SYSTEM_CONFIG,
                    description=f'Serviço {service_name} parado'
                )
            
            return {
                'success': True,
                'message': f'Serviço {service_name} parado com sucesso'
            }
        
        except Exception as e:
            logging.error(f"Erro ao parar serviço {service_name}: {e}")
            return {
                'success': False,
                'message': f'Erro ao parar serviço {service_name}',
                'error': str(e)
            }
    
    @classmethod
    def start_service(cls, service_name, user_id=None):
        """
        Iniciar um serviço
        
        :param service_name: Nome do serviço
        :param user_id: ID do usuário que solicitou a inicialização
        :return: Resultado da operação
        """
        service_start_commands = {
            'web_server': ['gunicorn', 'app:create_app()'],
            'database': cls._get_database_start_command(),
            'task_queue': ['celery', '-A', 'app.celery_app', 'worker'],
            'cache_service': ['redis-server']
        }
        
        try:
            # Verificar se o serviço já está em execução
            if cls._get_service_pid(service_name):
                return {
                    'success': False,
                    'message': f'Serviço {service_name} já está em execução'
                }
            
            # Obter comando de inicialização
            start_cmd = service_start_commands.get(service_name)
            
            if not start_cmd:
                return {
                    'success': False,
                    'message': f'Comando de inicialização não definido para {service_name}'
                }
            
            # Iniciar serviço
            subprocess.Popen(start_cmd, start_new_session=True)
            
            # Atualizar status do serviço
            ServiceStatus.update_service_status(
                service_name=service_name,
                status=ServiceStatusType.RUNNING,
                description=f'Serviço {service_name} iniciado manualmente'
            )
            
            # Registrar atividade
            if user_id:
                UserActivityLog.log_activity(
                    user_id=user_id,
                    activity_type=UserActivityType.SYSTEM_CONFIG,
                    description=f'Serviço {service_name} iniciado'
                )
            
            return {
                'success': True,
                'message': f'Serviço {service_name} iniciado com sucesso'
            }
        
        except Exception as e:
            logging.error(f"Erro ao iniciar serviço {service_name}: {e}")
            return {
                'success': False,
                'message': f'Erro ao iniciar serviço {service_name}',
                'error': str(e)
            }
    
    @classmethod
    def _get_database_start_command(cls):
        """
        Obter comando de inicialização do banco de dados
        
        :return: Comando de inicialização
        """
        system = platform.system().lower()
        
        database_start_commands = {
            'linux': {
                'postgres': ['systemctl', 'start', 'postgresql'],
                'mysql': ['systemctl', 'start', 'mysqld']
            },
            'darwin': {  # macOS
                'postgres': ['brew', 'services', 'start', 'postgresql'],
                'mysql': ['brew', 'services', 'start', 'mysql']
            },
            'windows': {
                'postgres': ['net', 'start', 'postgresql'],
                'mysql': ['net', 'start', 'mysql']
            }
        }
        
        # Detectar banco de dados instalado
        for db_type in ['postgres', 'mysql']:
            if cls._check_database_installed(db_type):
                return database_start_commands.get(system, {}).get(db_type)
        
        return None
    
    @classmethod
    def _check_database_installed(cls, db_type):
        """
        Verificar se um banco de dados está instalado
        
        :param db_type: Tipo de banco de dados
        :return: Booleano indicando se está instalado
        """
        try:
            result = subprocess.run(
                [db_type, '--version'], 
                capture_output=True, 
                text=True
            )
            return result.returncode == 0
        except Exception:
            return False
    
    @classmethod
    def restart_service(cls, service_name, user_id=None):
        """
        Reiniciar um serviço
        
        :param service_name: Nome do serviço
        :param user_id: ID do usuário que solicitou o reinício
        :return: Resultado da operação
        """
        try:
            # Parar serviço
            stop_result = cls.stop_service(service_name)
            
            if not stop_result['success']:
                return stop_result
            
            # Iniciar serviço
            start_result = cls.start_service(service_name, user_id)
            
            # Registrar atividade
            if user_id:
                UserActivityLog.log_activity(
                    user_id=user_id,
                    activity_type=UserActivityType.SYSTEM_CONFIG,
                    description=f'Serviço {service_name} reiniciado'
                )
            
            return start_result
        
        except Exception as e:
            logging.error(f"Erro ao reiniciar serviço {service_name}: {e}")
            return {
                'success': False,
                'message': f'Erro ao reiniciar serviço {service_name}',
                'error': str(e)
            }
