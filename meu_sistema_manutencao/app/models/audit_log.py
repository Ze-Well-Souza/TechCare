from app.extensions import db
from datetime import datetime
import enum
import json
import ipaddress
import socket

class AuditLogAction(enum.Enum):
    """
    Enum para categorizar tipos de ações de auditoria
    """
    LOGIN = 'login'
    LOGOUT = 'logout'
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    ACCESS = 'access'
    PERMISSION_CHANGE = 'permission_change'
    SYSTEM_CONFIG = 'system_config'

class AuditLog(db.Model):
    """
    Modelo para registrar logs de auditoria
    """
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    
    # Informações do usuário
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    username = db.Column(db.String(100), nullable=False)
    
    # Detalhes da ação
    action = db.Column(db.Enum(AuditLogAction), nullable=False)
    resource_type = db.Column(db.String(100), nullable=False)
    resource_id = db.Column(db.Integer, nullable=True)
    
    # Detalhes da requisição
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.String(500), nullable=True)
    
    # Dados adicionais
    old_data = db.Column(db.JSON, nullable=True)
    new_data = db.Column(db.JSON, nullable=True)
    
    # Timestamps
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relacionamentos
    user = db.relationship('User', backref='audit_logs')

    @classmethod
    def log_action(cls, 
                   user, 
                   action, 
                   resource_type, 
                   resource_id=None, 
                   old_data=None, 
                   new_data=None, 
                   request=None):
        """
        Método de fábrica para criar logs de auditoria
        
        :param user: Usuário que realizou a ação
        :param action: Ação realizada (enum AuditLogAction)
        :param resource_type: Tipo de recurso afetado
        :param resource_id: ID do recurso afetado
        :param old_data: Estado anterior do recurso
        :param new_data: Novo estado do recurso
        :param request: Objeto de requisição Flask
        """
        # Obter endereço IP
        if request:
            ip_address = request.remote_addr
            user_agent = request.user_agent.string
        else:
            # Fallback para IP local se não houver request
            ip_address = socket.gethostbyname(socket.gethostname())
            user_agent = None

        # Validar endereço IP
        try:
            ipaddress.ip_address(ip_address)
        except ValueError:
            ip_address = '127.0.0.1'

        # Converter dados para JSON se necessário
        def _safe_json(data):
            try:
                return json.dumps(data) if data is not None else None
            except (TypeError, ValueError):
                return str(data)

        # Criar log de auditoria
        audit_log = cls(
            user_id=user.id,
            username=user.username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            user_agent=user_agent,
            old_data=_safe_json(old_data),
            new_data=_safe_json(new_data)
        )

        # Salvar log
        db.session.add(audit_log)
        db.session.commit()

        return audit_log

    def to_dict(self):
        """
        Converter log de auditoria para dicionário
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.username,
            'action': self.action.value,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'old_data': json.loads(self.old_data) if self.old_data else None,
            'new_data': json.loads(self.new_data) if self.new_data else None,
            'timestamp': self.timestamp.isoformat()
        }

    @classmethod
    def get_user_activity(cls, user_id=None, days=30, action=None):
        """
        Obter atividades de auditoria
        
        :param user_id: ID do usuário (opcional)
        :param days: Número de dias para buscar logs
        :param action: Filtrar por tipo de ação
        """
        from datetime import datetime, timedelta

        # Calcular data de início
        start_date = datetime.utcnow() - timedelta(days=days)

        # Construir query base
        query = cls.query.filter(cls.timestamp >= start_date)

        # Filtros opcionais
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if action:
            query = query.filter_by(action=action)

        # Ordenar por timestamp mais recente
        query = query.order_by(cls.timestamp.desc())

        return query.all()
