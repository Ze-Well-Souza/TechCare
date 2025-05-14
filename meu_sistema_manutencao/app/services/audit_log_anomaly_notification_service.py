from datetime import datetime, timedelta
from app.services.audit_log_query_service import AuditLogQueryService
from app.models.notification import Notification, NotificationLevel
from app.extensions import db
import logging

class AuditLogAnomalyNotificationService:
    """
    Serviço para detecção e notificação de anomalias em logs de auditoria
    """
    
    @classmethod
    def check_and_notify_anomalies(cls, days=1):
        """
        Verificar e notificar anomalias nos logs de auditoria
        
        :param days: Número de dias para análise
        :return: Dicionário com anomalias detectadas
        """
        try:
            # Obter relatório de anomalias
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            anomalies = AuditLogQueryService.generate_anomaly_report(days)
            
            # Processar anomalias e gerar notificações
            notifications = []
            
            # Anomalias de login
            login_anomalies = anomalies.get('login_anomalies', [])
            for anomaly in login_anomalies:
                if anomaly['login_attempts'] > 5:
                    notification = cls._create_login_anomaly_notification(anomaly)
                    notifications.append(notification)
            
            # Anomalias de recursos críticos
            resource_anomalies = anomalies.get('resource_anomalies', [])
            for anomaly in resource_anomalies:
                if anomaly['action_count'] > 10:
                    notification = cls._create_resource_anomaly_notification(anomaly)
                    notifications.append(notification)
            
            # Anomalias de IP
            ip_anomalies = anomalies.get('ip_anomalies', [])
            for anomaly in ip_anomalies:
                if anomaly['unique_users'] > 2:
                    notification = cls._create_ip_anomaly_notification(anomaly)
                    notifications.append(notification)
            
            # Salvar notificações
            if notifications:
                db.session.add_all(notifications)
                db.session.commit()
            
            # Log de execução
            logging.info(f"Verificação de anomalias concluída. {len(notifications)} notificações geradas.")
            
            return {
                'total_anomalies': len(notifications),
                'login_anomalies': len([n for n in notifications if 'login' in n.title.lower()]),
                'resource_anomalies': len([n for n in notifications if 'recurso' in n.title.lower()]),
                'ip_anomalies': len([n for n in notifications if 'ip' in n.title.lower()])
            }
        
        except Exception as e:
            # Registrar erro
            logging.error(f"Erro na verificação de anomalias: {e}")
            db.session.rollback()
            
            return {
                'error': str(e),
                'total_anomalies': 0
            }
    
    @classmethod
    def _create_login_anomaly_notification(cls, anomaly):
        """
        Criar notificação para anomalias de login
        """
        return Notification(
            title=f"Anomalia de Login: {anomaly['username']}",
            message=(
                f"Múltiplas tentativas de login detectadas para o usuário {anomaly['username']}. "
                f"Total de tentativas: {anomaly['login_attempts']}. "
                "Verifique possíveis tentativas de acesso não autorizado."
            ),
            level=NotificationLevel.HIGH,
            category='security',
            user_id=None  # Notificação para todos os administradores
        )
    
    @classmethod
    def _create_resource_anomaly_notification(cls, anomaly):
        """
        Criar notificação para anomalias de recursos críticos
        """
        return Notification(
            title=f"Anomalia em Recurso Crítico: {anomaly['resource_type']}",
            message=(
                f"Número incomum de ações detectadas no recurso {anomaly['resource_type']}. "
                f"Total de ações: {anomaly['action_count']}. "
                "Recomenda-se investigação imediata."
            ),
            level=NotificationLevel.HIGH,
            category='security',
            user_id=None  # Notificação para todos os administradores
        )
    
    @classmethod
    def _create_ip_anomaly_notification(cls, anomaly):
        """
        Criar notificação para anomalias de endereço IP
        """
        return Notification(
            title=f"Anomalia de IP: {anomaly['ip_address']}",
            message=(
                f"Endereço IP {anomaly['ip_address']} associado a múltiplos usuários. "
                f"Total de usuários únicos: {anomaly['unique_users']}. "
                "Possível atividade suspeita detectada."
            ),
            level=NotificationLevel.HIGH,
            category='security',
            user_id=None  # Notificação para todos os administradores
        )
    
    @classmethod
    def get_recent_anomaly_notifications(cls, days=7):
        """
        Obter notificações de anomalias recentes
        
        :param days: Número de dias para buscar notificações
        :return: Lista de notificações de anomalias
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        return Notification.query.filter(
            Notification.category == 'security',
            Notification.timestamp.between(start_date, end_date)
        ).order_by(
            Notification.timestamp.desc()
        ).all()
