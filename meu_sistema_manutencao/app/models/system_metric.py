from app.extensions import db
from datetime import datetime
import psutil
import platform
import json

class SystemMetric(db.Model):
    """
    Modelo para armazenar métricas de desempenho do sistema
    """
    __tablename__ = 'system_metrics'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Métricas de CPU
    cpu_usage = db.Column(db.Float, nullable=False)
    cpu_cores = db.Column(db.Integer, nullable=False)
    
    # Métricas de Memória
    memory_total = db.Column(db.BigInteger, nullable=False)
    memory_used = db.Column(db.BigInteger, nullable=False)
    memory_percent = db.Column(db.Float, nullable=False)
    
    # Métricas de Disco
    disk_total = db.Column(db.BigInteger, nullable=False)
    disk_used = db.Column(db.BigInteger, nullable=False)
    disk_percent = db.Column(db.Float, nullable=False)
    
    # Métricas de Rede
    network_bytes_sent = db.Column(db.BigInteger, nullable=False)
    network_bytes_recv = db.Column(db.BigInteger, nullable=False)
    
    # Informações do Sistema
    system_info = db.Column(db.JSON, nullable=False)

    @classmethod
    def collect_metrics(cls):
        """
        Coletar métricas atuais do sistema
        """
        # Métricas de CPU
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_cores = psutil.cpu_count()
        
        # Métricas de Memória
        memory = psutil.virtual_memory()
        
        # Métricas de Disco
        disk = psutil.disk_usage('/')
        
        # Métricas de Rede
        network = psutil.net_io_counters()
        
        # Informações do Sistema
        system_info = {
            'platform': platform.platform(),
            'python_version': platform.python_version(),
            'processor': platform.processor(),
            'architecture': platform.machine()
        }

        # Criar nova entrada de métrica
        metric = cls(
            cpu_usage=cpu_usage,
            cpu_cores=cpu_cores,
            memory_total=memory.total,
            memory_used=memory.used,
            memory_percent=memory.percent,
            disk_total=disk.total,
            disk_used=disk.used,
            disk_percent=disk.percent,
            network_bytes_sent=network.bytes_sent,
            network_bytes_recv=network.bytes_recv,
            system_info=json.dumps(system_info)
        )
        
        db.session.add(metric)
        db.session.commit()
        
        return metric

    def to_dict(self):
        """
        Converter métrica para dicionário
        """
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'cpu_usage': self.cpu_usage,
            'cpu_cores': self.cpu_cores,
            'memory': {
                'total': self.memory_total,
                'used': self.memory_used,
                'percent': self.memory_percent
            },
            'disk': {
                'total': self.disk_total,
                'used': self.disk_used,
                'percent': self.disk_percent
            },
            'network': {
                'bytes_sent': self.network_bytes_sent,
                'bytes_recv': self.network_bytes_recv
            },
            'system_info': json.loads(self.system_info)
        }

    @classmethod
    def get_performance_summary(cls, hours=24):
        """
        Obter resumo de performance para um período
        """
        from sqlalchemy import func
        from datetime import timedelta

        # Calcular métricas agregadas
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        # Métricas agregadas
        aggregated_metrics = db.session.query(
            func.avg(cls.cpu_usage).label('avg_cpu_usage'),
            func.avg(cls.memory_percent).label('avg_memory_usage'),
            func.avg(cls.disk_percent).label('avg_disk_usage'),
            func.max(cls.network_bytes_sent).label('total_network_sent'),
            func.max(cls.network_bytes_recv).label('total_network_recv')
        ).filter(
            cls.timestamp.between(start_time, end_time)
        ).first()

        return {
            'period_hours': hours,
            'avg_cpu_usage': aggregated_metrics.avg_cpu_usage,
            'avg_memory_usage': aggregated_metrics.avg_memory_usage,
            'avg_disk_usage': aggregated_metrics.avg_disk_usage,
            'total_network_sent': aggregated_metrics.total_network_sent,
            'total_network_recv': aggregated_metrics.total_network_recv
        }
