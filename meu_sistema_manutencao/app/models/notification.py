from app.extensions import db
from datetime import datetime
import enum

class NotificationLevel(enum.Enum):
    INFO = 'info'
    WARNING = 'warning'
    CRITICAL = 'critical'
    SUCCESS = 'success'

class Notification(db.Model):
    """
    Modelo para gerenciar notificações do sistema
    """
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.Enum(NotificationLevel), nullable=False, default=NotificationLevel.INFO)
    
    # Relacionamentos
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_at = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    user = db.relationship('User', backref='notifications')
    service = db.relationship('Service', backref='notifications')

    def mark_as_read(self):
        """
        Marcar notificação como lida
        """
        self.read_at = datetime.utcnow()
        db.session.commit()

    def to_dict(self):
        """
        Converter notificação para dicionário
        """
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'level': self.level.value,
            'created_at': self.created_at.isoformat(),
            'read_at': self.read_at.isoformat() if self.read_at else None,
            'user_id': self.user_id,
            'service_id': self.service_id
        }

    @classmethod
    def create_notification(cls, title, message, level=NotificationLevel.INFO, 
                             user_id=None, service_id=None):
        """
        Método de fábrica para criar notificações
        """
        notification = cls(
            title=title,
            message=message,
            level=level,
            user_id=user_id,
            service_id=service_id
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    @classmethod
    def get_unread_notifications(cls, user_id=None, level=None):
        """
        Obter notificações não lidas
        """
        query = cls.query.filter(cls.read_at.is_(None))
        
        if user_id:
            query = query.filter_by(user_id=user_id)
        
        if level:
            query = query.filter_by(level=level)
        
        return query.order_by(cls.created_at.desc()).all()
