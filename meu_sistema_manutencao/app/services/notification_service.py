from app.models.system_metric import SystemMetric
from app.models.service import Service
from app.models.notification import Notification, NotificationLevel
from app.extensions import db

class NotificationService:
    """
    Serviço para gerenciar notificações automáticas do sistema
    """

    @classmethod
    def check_system_performance(cls):
        """
        Verificar métricas de sistema e gerar notificações
        """
        # Obter métricas das últimas 24 horas
        summary = SystemMetric.get_performance_summary(hours=24)

        # Regras de notificação
        notifications = []

        # Alerta de alto uso de CPU
        if summary['avg_cpu_usage'] > 80:
            notifications.append(
                Notification.create_notification(
                    title='Alto Uso de CPU',
                    message=f'Uso médio de CPU nos últimos 24h: {summary["avg_cpu_usage"]:.2f}%',
                    level=NotificationLevel.WARNING
                )
            )

        # Alerta de alta utilização de memória
        if summary['avg_memory_usage'] > 85:
            notifications.append(
                Notification.create_notification(
                    title='Alto Uso de Memória',
                    message=f'Uso médio de memória nos últimos 24h: {summary["avg_memory_usage"]:.2f}%',
                    level=NotificationLevel.CRITICAL
                )
            )

        # Alerta de espaço em disco
        if summary['avg_disk_usage'] > 90:
            notifications.append(
                Notification.create_notification(
                    title='Espaço em Disco Crítico',
                    message=f'Uso médio de disco nos últimos 24h: {summary["avg_disk_usage"]:.2f}%',
                    level=NotificationLevel.CRITICAL
                )
            )

        return notifications

    @classmethod
    def check_service_status(cls):
        """
        Verificar status de serviços e gerar notificações
        """
        notifications = []

        # Buscar todos os serviços
        services = Service.query.all()

        for service in services:
            # Verificar status do serviço
            if not service.is_running():
                notifications.append(
                    Notification.create_notification(
                        title=f'Serviço Parado: {service.name}',
                        message=f'O serviço {service.name} não está em execução.',
                        level=NotificationLevel.WARNING,
                        service_id=service.id
                    )
                )

        return notifications

    @classmethod
    def generate_system_alerts(cls):
        """
        Método principal para geração de alertas do sistema
        """
        performance_alerts = cls.check_system_performance()
        service_alerts = cls.check_service_status()

        return performance_alerts + service_alerts
