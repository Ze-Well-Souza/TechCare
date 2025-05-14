from datetime import datetime
from app import db

class MaintenancePlan(db.Model):
    """Modelo para planos de manutenção agendada (limpeza manual e automática)"""
    __tablename__ = 'maintenance_plans'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)
    cleaning_types = db.Column(db.String(128), nullable=False)  # Ex: 'temp,browser,registry'
    frequency = db.Column(db.String(20), nullable=False)  # daily, weekly, monthly, custom
    day_of_week = db.Column(db.String(10))  # Ex: 'monday', 'friday' (para semanal)
    day_of_month = db.Column(db.Integer)    # Ex: 1-31 (para mensal)
    time = db.Column(db.String(10), nullable=False)  # Horário de execução como string (ex: "08:30")
    enabled = db.Column(db.Boolean, default=True)
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    notify_email = db.Column(db.String(120))  # E-mail para notificação
    notify_sms = db.Column(db.String(32))     # Telefone para SMS/WhatsApp
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MaintenancePlan {self.name} for user {self.user_id}>' 