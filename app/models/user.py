from datetime import datetime, UTC
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app import db, login_manager
from sqlalchemy.orm import relationship
from app.models.role import Role, PermissionType

class User(UserMixin, db.Model):
    """Modelo de usuário para autenticação e autorização"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=True)
    role = relationship('Role', back_populates='users')
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(64))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))
    last_login = db.Column(db.DateTime)
    active = db.Column(db.Boolean, default=True)
    
    def __init__(self, **kwargs):
        """Inicializa um novo usuário"""
        super(User, self).__init__(**kwargs)
        # Garante que o usuário começa com status ativo por padrão
        if 'active' not in kwargs:
            self.active = True
    
    @property
    def password(self):
        """Impede acesso direto à senha"""
        raise AttributeError('senha não é um atributo legível')
    
    @password.setter
    def password(self, password):
        """Gera o hash da senha"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        """Verifica se a senha está correta"""
        return check_password_hash(self.password_hash, password)
    
    def check_password(self, password):
        """Alias para verify_password - usado em algumas partes do código"""
        return self.verify_password(password)
    
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.role and 'Admin Master' in self.role.name
    
    def has_permission(self, permission):
        """Verificar se o usuário tem uma permissão específica"""
        return self.role and self.role.has_permission(permission)
    
    def is_technician(self):
        """Verifica se o usuário é técnico"""
        return self.role and 'Technician' in self.role.name
    
    def is_active(self):
        """Implementa o método is_active requerido pelo Flask-Login"""
        return self.active
    
    def __repr__(self):
        return f'<User {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Função para carregar o usuário pelo ID"""
    return db.session.get(User, int(user_id)) 