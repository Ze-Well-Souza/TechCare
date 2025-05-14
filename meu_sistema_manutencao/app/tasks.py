from celery import Celery
from celery.schedules import crontab
from app.services.notification_service import NotificationService
from app.services.audit_log_retention_service import AuditLogRetentionService
from app.models.system_metric import SystemMetric
from app.extensions import create_app, db

def make_celery(app):
    """
    Configurar Celery com contexto da aplicação Flask
    """
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery

# Criar aplicação Flask
flask_app = create_app()
celery_app = make_celery(flask_app)

@celery_app.task(name='tasks.collect_system_metrics')
def collect_system_metrics():
    """
    Tarefa para coletar métricas do sistema periodicamente
    """
    with flask_app.app_context():
        try:
            metric = SystemMetric.collect_metrics()
            return f"Métricas coletadas: {metric.id}"
        except Exception as e:
            print(f"Erro ao coletar métricas: {e}")
            return None

@celery_app.task(name='tasks.generate_system_alerts')
def generate_system_alerts():
    """
    Tarefa para gerar alertas do sistema
    """
    with flask_app.app_context():
        try:
            alerts = NotificationService.generate_system_alerts()
            return f"{len(alerts)} alertas gerados"
        except Exception as e:
            print(f"Erro ao gerar alertas: {e}")
            return None

@celery_app.task(name='tasks.cleanup_old_metrics')
def cleanup_old_metrics():
    """
    Tarefa para limpar métricas antigas
    """
    with flask_app.app_context():
        try:
            # Excluir métricas com mais de 30 dias
            from datetime import datetime, timedelta
            from sqlalchemy import delete

            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Excluir métricas antigas
            delete_query = delete(SystemMetric).where(
                SystemMetric.timestamp < cutoff_date
            )
            
            result = db.session.execute(delete_query)
            db.session.commit()
            
            return f"{result.rowcount} métricas antigas removidas"
        except Exception as e:
            print(f"Erro ao limpar métricas antigas: {e}")
            return None

@celery_app.task(name='tasks.cleanup_audit_logs')
def cleanup_audit_logs():
    """
    Tarefa para limpar logs de auditoria
    """
    with flask_app.app_context():
        try:
            AuditLogRetentionService.cleanup_audit_logs()
            return "Logs de auditoria limpos"
        except Exception as e:
            print(f"Erro ao limpar logs de auditoria: {e}")
            return None

# Configuração de agendamento de tarefas
celery_app.conf.beat_schedule = {
    'collect-system-metrics': {
        'task': 'tasks.collect_system_metrics',
        'schedule': crontab(minute='*/15')  # A cada 15 minutos
    },
    'generate-system-alerts': {
        'task': 'tasks.generate_system_alerts',
        'schedule': crontab(hour='*/2')  # A cada 2 horas
    },
    'cleanup-old-metrics': {
        'task': 'tasks.cleanup_old_metrics',
        'schedule': crontab(day_of_month='1')  # Primeiro dia de cada mês
    }
}

# Configurações adicionais
celery_app.conf.timezone = 'UTC'
