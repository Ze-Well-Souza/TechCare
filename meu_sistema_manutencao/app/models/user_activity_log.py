from app.extensions import db
from datetime import datetime, UTC
from enum import Enum, auto

class UserActivityType(Enum):
    """
    Tipos de atividades de usuário
    """
    LOGIN = auto()
    LOGOUT = auto()
    PROFILE_UPDATE = auto()
    ROLE_CHANGE = auto()
    PERMISSION_CHANGE = auto()
    RESOURCE_ACCESS = auto()
    SYSTEM_CONFIG = auto()

class UserActivityLog(db.Model):
    """
    Modelo para registro de atividades de usuário
    """
    __tablename__ = 'user_activity_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='activity_logs')
    
    activity_type = db.Column(db.Enum(UserActivityType), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    
    # Detalhes adicionais da atividade
    ip_address = db.Column(db.String(45))  # Suporta IPv4 e IPv6
    user_agent = db.Column(db.String(255))
    
    # Dados de contexto para mudanças
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    
    timestamp = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(UTC),
        nullable=False
    )

    @classmethod
    def log_activity(
        cls, 
        user_id, 
        activity_type, 
        description, 
        ip_address=None, 
        user_agent=None, 
        old_value=None, 
        new_value=None
    ):
        """
        Registrar uma nova atividade de usuário
        
        :param user_id: ID do usuário
        :param activity_type: Tipo de atividade
        :param description: Descrição da atividade
        :param ip_address: Endereço IP da atividade
        :param user_agent: User agent do cliente
        :param old_value: Valor anterior (para mudanças)
        :param new_value: Novo valor (para mudanças)
        :return: Instância de log de atividade
        """
        activity_log = cls(
            user_id=user_id,
            activity_type=activity_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            old_value=old_value,
            new_value=new_value
        )
        
        db.session.add(activity_log)
        db.session.commit()
        
        return activity_log

    @classmethod
    def get_user_activities(
        cls, 
        user_id=None, 
        start_date=None, 
        end_date=None, 
        activity_types=None, 
        page=1, 
        per_page=50
    ):
        """
        Buscar logs de atividade com filtros
        
        :param user_id: Filtrar por ID de usuário
        :param start_date: Data de início
        :param end_date: Data de término
        :param activity_types: Tipos de atividade
        :param page: Página de resultados
        :param per_page: Resultados por página
        :return: Tupla (logs, total)
        """
        query = cls.query

        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if start_date:
            query = query.filter(cls.timestamp >= start_date)
        
        if end_date:
            query = query.filter(cls.timestamp <= end_date)
        
        if activity_types:
            query = query.filter(cls.activity_type.in_(activity_types))
        
        query = query.order_by(cls.timestamp.desc())
        
        # Paginação
        paginated_logs = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return paginated_logs.items, paginated_logs.total
