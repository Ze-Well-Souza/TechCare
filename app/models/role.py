import enum
from app import db
from sqlalchemy.orm import relationship

class PermissionType(enum.Enum):
    """Enumeração de tipos de permissões no sistema"""
    VIEW_DASHBOARD = 1
    RUN_DIAGNOSTICS = 2
    RUN_REPAIRS = 3
    MANAGE_USERS = 4
    VIEW_LOGS = 5
    ADMIN_ACCESS = 6


class Role(db.Model):
    """Modelo de papel/função para controle de acesso"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    description = db.Column(db.String(255))
    permissions = db.Column(db.Integer, default=0)
    users = relationship('User', back_populates='role')
    
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        # Garante que permissions nunca seja None
        if self.permissions is None:
            self.permissions = 0
    
    def has_permission(self, permission):
        """Verifica se o papel tem uma permissão específica"""
        if isinstance(permission, PermissionType):
            # Garante que permissions nunca seja None durante a verificação
            perms = self.permissions or 0
            return bool(perms & (1 << permission.value))
        return False
    
    def add_permission(self, permission):
        """Adiciona uma permissão específica"""
        # Garante que permissions nunca seja None durante a adição
        if self.permissions is None:
            self.permissions = 0
        
        if not self.has_permission(permission):
            self.permissions += 1 << permission.value
    
    def remove_permission(self, permission):
        """Remove uma permissão específica"""
        # Garante que permissions nunca seja None durante a remoção
        if self.permissions is None:
            self.permissions = 0
            return
            
        if self.has_permission(permission):
            self.permissions -= 1 << permission.value
    
    def reset_permissions(self):
        """Remove todas as permissões"""
        self.permissions = 0
    
    def __repr__(self):
        return f'<Role {self.name}>' 