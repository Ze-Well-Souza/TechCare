from app.extensions import db
from datetime import datetime, UTC
from enum import Enum, auto
import uuid

class ServiceStatusType(Enum):
    """
    Tipos de status de serviço
    """
    RUNNING = auto()
    STOPPED = auto()
    ERROR = auto()
    DEGRADED = auto()
    MAINTENANCE = auto()

class ServiceStatus(db.Model):
    """
    Modelo para monitoramento de status de serviços
    """
    __tablename__ = 'service_statuses'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    service_name = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.Enum(ServiceStatusType), nullable=False)
    
    # Detalhes adicionais do status
    description = db.Column(db.Text)
    health_check_timestamp = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    
    # Métricas de performance
    cpu_usage = db.Column(db.Float)
    memory_usage = db.Column(db.Float)
    response_time = db.Column(db.Float)  # em milissegundos
    
    # Informações de erro
    error_details = db.Column(db.JSON)

    @classmethod
    def update_service_status(
        cls, 
        service_name, 
        status, 
        description=None, 
        cpu_usage=None, 
        memory_usage=None, 
        response_time=None, 
        error_details=None
    ):
        """
        Atualizar status de um serviço
        
        :param service_name: Nome do serviço
        :param status: Status do serviço
        :param description: Descrição adicional
        :param cpu_usage: Uso de CPU
        :param memory_usage: Uso de memória
        :param response_time: Tempo de resposta
        :param error_details: Detalhes de erro
        :return: Instância de status de serviço
        """
        # Buscar status existente ou criar novo
        service_status = cls.query.filter_by(service_name=service_name).first()
        
        if not service_status:
            service_status = cls(service_name=service_name)
        
        service_status.status = status
        service_status.description = description
        service_status.health_check_timestamp = datetime.now(UTC)
        
        # Atualizar métricas, se fornecidas
        if cpu_usage is not None:
            service_status.cpu_usage = cpu_usage
        
        if memory_usage is not None:
            service_status.memory_usage = memory_usage
        
        if response_time is not None:
            service_status.response_time = response_time
        
        if error_details is not None:
            service_status.error_details = error_details
        
        db.session.add(service_status)
        db.session.commit()
        
        return service_status

    @classmethod
    def get_service_status(cls, service_name=None):
        """
        Obter status de serviços
        
        :param service_name: Nome do serviço (opcional)
        :return: Lista de status de serviços
        """
        if service_name:
            return cls.query.filter_by(service_name=service_name).all()
        
        return cls.query.all()

    @classmethod
    def get_system_health_summary(cls):
        """
        Obter resumo de saúde do sistema
        
        :return: Dicionário com resumo de status
        """
        services = cls.query.all()
        
        summary = {
            'total_services': len(services),
            'status_breakdown': {},
            'performance_metrics': {
                'avg_cpu_usage': 0,
                'avg_memory_usage': 0,
                'avg_response_time': 0
            }
        }
        
        # Contagem de status
        for service in services:
            status_name = service.status.name
            summary['status_breakdown'][status_name] = summary['status_breakdown'].get(status_name, 0) + 1
        
        # Métricas de performance médias
        if services:
            summary['performance_metrics'] = {
                'avg_cpu_usage': sum(s.cpu_usage or 0 for s in services) / len(services),
                'avg_memory_usage': sum(s.memory_usage or 0 for s in services) / len(services),
                'avg_response_time': sum(s.response_time or 0 for s in services) / len(services)
            }
        
        return summary
