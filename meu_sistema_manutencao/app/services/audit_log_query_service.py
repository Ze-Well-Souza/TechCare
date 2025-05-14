from datetime import datetime, timedelta
from sqlalchemy import and_, or_
from app.models.audit_log import AuditLog, AuditLogAction
from app.extensions import db

class AuditLogQueryService:
    """
    Serviço para consultas avançadas de logs de auditoria
    """
    
    @classmethod
    def advanced_search(cls, 
                        start_date=None, 
                        end_date=None, 
                        user_ids=None, 
                        actions=None, 
                        resource_types=None, 
                        ip_addresses=None,
                        page=1, 
                        per_page=50):
        """
        Realizar busca avançada de logs de auditoria
        
        :param start_date: Data de início para filtro
        :param end_date: Data de término para filtro
        :param user_ids: Lista de IDs de usuários
        :param actions: Lista de tipos de ações
        :param resource_types: Lista de tipos de recursos
        :param ip_addresses: Lista de endereços IP
        :param page: Número da página
        :param per_page: Logs por página
        :return: Tupla (logs, total_logs)
        """
        # Construir query base
        query = AuditLog.query

        # Filtros de data
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)

        # Filtro de usuários
        if user_ids:
            query = query.filter(AuditLog.user_id.in_(user_ids))

        # Filtro de ações
        if actions:
            query = query.filter(AuditLog.action.in_(actions))

        # Filtro de tipos de recursos
        if resource_types:
            query = query.filter(AuditLog.resource_type.in_(resource_types))

        # Filtro de endereços IP
        if ip_addresses:
            query = query.filter(AuditLog.ip_address.in_(ip_addresses))

        # Ordenar por timestamp decrescente
        query = query.order_by(AuditLog.timestamp.desc())

        # Paginação
        total_logs = query.count()
        logs = query.paginate(page=page, per_page=per_page, error_out=False).items

        return logs, total_logs

    @classmethod
    def generate_anomaly_report(cls, days=30):
        """
        Gerar relatório de anomalias em logs de auditoria
        
        :param days: Número de dias para análise
        :return: Dicionário com anomalias detectadas
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Anomalias de login
        login_anomalies = cls._detect_login_anomalies(start_date, end_date)

        # Anomalias de recursos críticos
        resource_anomalies = cls._detect_resource_anomalies(start_date, end_date)

        # Anomalias de IP
        ip_anomalies = cls._detect_ip_anomalies(start_date, end_date)

        return {
            'login_anomalies': login_anomalies,
            'resource_anomalies': resource_anomalies,
            'ip_anomalies': ip_anomalies
        }

    @classmethod
    def _detect_login_anomalies(cls, start_date, end_date):
        """
        Detectar anomalias em logs de login
        """
        # Número máximo de tentativas de login em um curto período
        max_login_attempts = 5
        max_login_window = timedelta(minutes=10)

        # Buscar logs de login com múltiplas tentativas
        login_attempts = db.session.query(
            AuditLog.user_id, 
            AuditLog.username,
            db.func.count(AuditLog.id).label('attempt_count')
        ).filter(
            AuditLog.action == AuditLogAction.LOGIN,
            AuditLog.timestamp.between(start_date, end_date)
        ).group_by(
            AuditLog.user_id, 
            AuditLog.username
        ).having(
            db.func.count(AuditLog.id) > max_login_attempts
        ).all()

        return [
            {
                'user_id': attempt.user_id,
                'username': attempt.username,
                'login_attempts': attempt.attempt_count
            } for attempt in login_attempts
        ]

    @classmethod
    def _detect_resource_anomalies(cls, start_date, end_date):
        """
        Detectar anomalias em logs de recursos críticos
        """
        # Recursos críticos para monitoramento
        critical_resources = ['user', 'permission', 'system_config']

        # Contar ações em recursos críticos
        resource_actions = db.session.query(
            AuditLog.resource_type,
            AuditLog.action,
            db.func.count(AuditLog.id).label('action_count')
        ).filter(
            AuditLog.resource_type.in_(critical_resources),
            AuditLog.timestamp.between(start_date, end_date)
        ).group_by(
            AuditLog.resource_type, 
            AuditLog.action
        ).all()

        return [
            {
                'resource_type': action.resource_type,
                'action': action.action,
                'action_count': action.action_count
            } for action in resource_actions
        ]

    @classmethod
    def _detect_ip_anomalies(cls, start_date, end_date):
        """
        Detectar anomalias de endereços IP
        """
        # Número máximo de usuários de um mesmo IP
        max_users_per_ip = 2

        # Encontrar IPs com múltiplos usuários
        ip_users = db.session.query(
            AuditLog.ip_address,
            db.func.count(db.func.distinct(AuditLog.user_id)).label('unique_users')
        ).filter(
            AuditLog.timestamp.between(start_date, end_date)
        ).group_by(
            AuditLog.ip_address
        ).having(
            db.func.count(db.func.distinct(AuditLog.user_id)) > max_users_per_ip
        ).all()

        return [
            {
                'ip_address': ip_log.ip_address,
                'unique_users': ip_log.unique_users
            } for ip_log in ip_users
        ]
