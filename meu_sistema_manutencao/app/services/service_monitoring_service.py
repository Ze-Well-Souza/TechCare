import psutil
import logging
import subprocess
import platform
from app.models.service_status import ServiceStatus, ServiceStatusType
from app.extensions import db
import time

class ServiceMonitoringService:
    """
    Serviço para monitoramento de serviços do sistema
    """
    
    @classmethod
    def check_system_services(cls):
        """
        Verificar status dos principais serviços do sistema
        """
        services_to_check = [
            'database',  # Serviço de banco de dados
            'web_server',  # Servidor web
            'task_queue',  # Fila de tarefas (Celery)
            'cache_service',  # Serviço de cache
            'logging_service'  # Serviço de logging
        ]
        
        for service_name in services_to_check:
            try:
                status = cls._check_service_status(service_name)
                ServiceStatus.update_service_status(
                    service_name=service_name,
                    status=status['status'],
                    description=status.get('description'),
                    cpu_usage=status.get('cpu_usage'),
                    memory_usage=status.get('memory_usage'),
                    response_time=status.get('response_time')
                )
            except Exception as e:
                logging.error(f"Erro ao verificar status do serviço {service_name}: {e}")
    
    @classmethod
    def _check_service_status(cls, service_name):
        """
        Verificar status de um serviço específico
        
        :param service_name: Nome do serviço
        :return: Dicionário com status do serviço
        """
        # Mapeamento de verificações de status por serviço
        status_checkers = {
            'database': cls._check_database_status,
            'web_server': cls._check_web_server_status,
            'task_queue': cls._check_task_queue_status,
            'cache_service': cls._check_cache_service_status,
            'logging_service': cls._check_logging_service_status
        }
        
        # Usar verificador específico ou genérico
        checker = status_checkers.get(service_name, cls._generic_service_check)
        return checker(service_name)
    
    @classmethod
    def _check_database_status(cls, service_name):
        """
        Verificar status do banco de dados
        """
        try:
            # Exemplo com SQLAlchemy - adapte conforme seu banco
            db.session.execute('SELECT 1')
            return {
                'status': ServiceStatusType.RUNNING,
                'description': 'Conexão com banco de dados OK',
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'response_time': 50  # ms
            }
        except Exception as e:
            return {
                'status': ServiceStatusType.ERROR,
                'description': f'Erro de conexão com banco de dados: {e}',
                'error_details': str(e)
            }
    
    @classmethod
    def _check_web_server_status(cls, service_name):
        """
        Verificar status do servidor web
        """
        try:
            # Exemplo de verificação - adapte para seu ambiente
            start_time = time.time()
            response = subprocess.run(
                ['curl', '-s', 'http://localhost:5000/health'],
                capture_output=True, 
                text=True, 
                timeout=5
            )
            response_time = (time.time() - start_time) * 1000  # ms
            
            if response.returncode == 0:
                return {
                    'status': ServiceStatusType.RUNNING,
                    'description': 'Servidor web respondendo normalmente',
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'response_time': response_time
                }
            else:
                return {
                    'status': ServiceStatusType.ERROR,
                    'description': 'Falha na verificação do servidor web',
                    'error_details': response.stderr
                }
        except Exception as e:
            return {
                'status': ServiceStatusType.ERROR,
                'description': f'Erro ao verificar servidor web: {e}',
                'error_details': str(e)
            }
    
    @classmethod
    def _check_task_queue_status(cls, service_name):
        """
        Verificar status da fila de tarefas
        """
        try:
            # Exemplo com Celery - adapte conforme sua configuração
            from celery.task.control import inspect
            
            insp = inspect()
            stats = insp.stats()
            
            if stats:
                return {
                    'status': ServiceStatusType.RUNNING,
                    'description': 'Fila de tarefas operacional',
                    'cpu_usage': psutil.cpu_percent(),
                    'memory_usage': psutil.virtual_memory().percent,
                    'response_time': 100  # ms
                }
            else:
                return {
                    'status': ServiceStatusType.STOPPED,
                    'description': 'Fila de tarefas não detectada'
                }
        except Exception as e:
            return {
                'status': ServiceStatusType.ERROR,
                'description': f'Erro ao verificar fila de tarefas: {e}',
                'error_details': str(e)
            }
    
    @classmethod
    def _check_cache_service_status(cls, service_name):
        """
        Verificar status do serviço de cache
        """
        try:
            # Exemplo com Redis - adapte conforme sua configuração
            import redis
            
            redis_client = redis.Redis(host='localhost', port=6379, db=0)
            redis_client.ping()
            
            return {
                'status': ServiceStatusType.RUNNING,
                'description': 'Serviço de cache operacional',
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'response_time': 20  # ms
            }
        except Exception as e:
            return {
                'status': ServiceStatusType.ERROR,
                'description': f'Erro no serviço de cache: {e}',
                'error_details': str(e)
            }
    
    @classmethod
    def _check_logging_service_status(cls, service_name):
        """
        Verificar status do serviço de logging
        """
        try:
            # Tentar escrever um log de teste
            logging.info('Teste de serviço de logging')
            
            return {
                'status': ServiceStatusType.RUNNING,
                'description': 'Serviço de logging funcional',
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'response_time': 10  # ms
            }
        except Exception as e:
            return {
                'status': ServiceStatusType.ERROR,
                'description': f'Erro no serviço de logging: {e}',
                'error_details': str(e)
            }
    
    @classmethod
    def _generic_service_check(cls, service_name):
        """
        Verificação genérica de status de serviço
        """
        try:
            # Verificação básica de sistema
            return {
                'status': ServiceStatusType.RUNNING,
                'description': f'Serviço {service_name} verificado',
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent
            }
        except Exception as e:
            return {
                'status': ServiceStatusType.ERROR,
                'description': f'Erro ao verificar serviço {service_name}: {e}',
                'error_details': str(e)
            }
    
    @classmethod
    def get_system_resource_usage(cls):
        """
        Obter uso de recursos do sistema
        
        :return: Dicionário com métricas de recursos
        """
        try:
            return {
                'cpu_usage': psutil.cpu_percent(interval=1),
                'memory_usage': {
                    'total': psutil.virtual_memory().total,
                    'available': psutil.virtual_memory().available,
                    'percent': psutil.virtual_memory().percent
                },
                'disk_usage': {
                    'total': psutil.disk_usage('/').total,
                    'used': psutil.disk_usage('/').used,
                    'percent': psutil.disk_usage('/').percent
                },
                'platform': {
                    'system': platform.system(),
                    'release': platform.release(),
                    'version': platform.version()
                }
            }
        except Exception as e:
            logging.error(f"Erro ao obter uso de recursos do sistema: {e}")
            return None
