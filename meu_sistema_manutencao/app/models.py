from . import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    plano = db.Column(db.String(20), default='free')
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime)
    
    logs = db.relationship('Log', backref='user', lazy='dynamic')
    machines = db.relationship('Machine', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)
    
    def __repr__(self):
        return f'<User {self.nome}>'

class Log(db.Model):
    __tablename__ = 'logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    acao = db.Column(db.String(100))
    detalhes = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Log {self.acao} by User {self.user_id}>'

class Machine(db.Model):
    __tablename__ = 'machines'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    nome = db.Column(db.String(100))
    specs = db.Column(db.JSON)
    last_diagnostic = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Machine {self.nome} of User {self.user_id}>'

# Constantes de Planos
PLANOS = {
    "free": {
        "nome": "Gratuito",
        "preco": 0,
        "max_machines": 1,
        "features": {
            "diagnostico": True,
            "limpeza": False,
            "instalacao": False,
            "pos_formatacao": False,
            "relatorios": False
        }
    },
    "intermediario": {
        "nome": "Intermediário",
        "preco": 29.90,
        "max_machines": 3,
        "features": {
            "diagnostico": True,
            "limpeza": True,
            "instalacao": True,
            "pos_formatacao": False,
            "relatorios": True
        }
    },
    "profissional": {
        "nome": "Profissional",
        "preco": 59.90,
        "max_machines": 10,
        "features": {
            "diagnostico": True,
            "limpeza": True,
            "instalacao": True,
            "pos_formatacao": True,
            "relatorios": True,
            "suporte_prioritario": True
        }
    }
}
