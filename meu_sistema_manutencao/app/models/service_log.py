from app.extensions import db
from datetime import datetime
import json

class ServiceLog(db.Model):
    """
    Modelo para registrar logs de execução de serviços
    """
    __tablename__ = 'service_logs'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    log_level = db.Column(db.String(20), nullable=False)  # INFO, WARNING, ERROR
    message = db.Column(db.Text, nullable=False)
    metadata = db.Column(db.JSON, nullable=True)

    service = db.relationship('Service', backref=db.backref('logs', lazy='dynamic'))

    @classmethod
    def log_service_event(cls, service, log_level, message, metadata=None):
        """
        Registrar um evento de log para um serviço
        """
        log_entry = cls(
            service_id=service.id,
            log_level=log_level,
            message=message,
            metadata=json.dumps(metadata) if metadata else None
        )
        db.session.add(log_entry)
        db.session.commit()
        return log_entry

    def to_dict(self):
        """
        Converter log para dicionário
        """
        return {
            'id': self.id,
            'service_id': self.service_id,
            'timestamp': self.timestamp.isoformat(),
            'log_level': self.log_level,
            'message': self.message,
            'metadata': json.loads(self.metadata) if self.metadata else None
        }

    @classmethod
    def get_service_logs(cls, service_id, limit=50, log_level=None):
        """
        Obter logs de um serviço específico
        """
        query = cls.query.filter_by(service_id=service_id)
        
        if log_level:
            query = query.filter_by(log_level=log_level)
        
        return query.order_by(cls.timestamp.desc()).limit(limit).all()
