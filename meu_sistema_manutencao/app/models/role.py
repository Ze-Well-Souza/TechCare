from app.extensions import db
from sqlalchemy.orm import relationship
from enum import Enum, auto

class PermissionType(Enum):
    """
    Tipos de permissões no sistema
    """
    # Permissões de usuário
    USER_CREATE = auto()
    USER_READ = auto()
    USER_UPDATE = auto()
    USER_DELETE = auto()

    # Permissões de serviço
    SERVICE_CREATE = auto()
    SERVICE_READ = auto()
    SERVICE_UPDATE = auto()
    SERVICE_DELETE = auto()

    # Permissões de log
    LOG_VIEW = auto()
    LOG_EXPORT = auto()
    LOG_MANAGE = auto()

    # Permissões de sistema
    SYSTEM_CONFIG = auto()
    SYSTEM_METRICS = auto()
    SYSTEM_ALERTS = auto()

class Role(db.Model):
    """
    Modelo de Role para controle de acesso
    """
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Relacionamento com permissões
    permissions = db.Column(db.JSON, nullable=False, default=[])
    
    # Relacionamento com usuários
    users = relationship('User', back_populates='role')

    @classmethod
    def create_default_roles(cls):
        """
        Criar roles padrão do sistema
        """
        default_roles = [
            {
                'name': 'Admin Master',
                'description': 'Acesso total ao sistema',
                'permissions': [p.name for p in PermissionType]
            },
            {
                'name': 'Admin Técnico',
                'description': 'Acesso a funcionalidades técnicas',
                'permissions': [
                    'SERVICE_CREATE', 'SERVICE_READ', 'SERVICE_UPDATE',
                    'LOG_VIEW', 'LOG_EXPORT',
                    'SYSTEM_METRICS', 'SYSTEM_ALERTS'
                ]
            },
            {
                'name': 'Visualizador',
                'description': 'Acesso apenas para visualização',
                'permissions': [
                    'USER_READ', 
                    'SERVICE_READ', 
                    'LOG_VIEW', 
                    'SYSTEM_METRICS'
                ]
            }
        ]

        for role_data in default_roles:
            existing_role = cls.query.filter_by(name=role_data['name']).first()
            if not existing_role:
                role = cls(
                    name=role_data['name'], 
                    description=role_data['description'],
                    permissions=role_data['permissions']
                )
                db.session.add(role)
        
        db.session.commit()

    def has_permission(self, permission):
        """
        Verificar se a role possui uma permissão específica
        """
        return (isinstance(permission, PermissionType) and 
                permission.name in self.permissions)

    def add_permission(self, permission):
        """
        Adicionar permissão à role
        """
        if isinstance(permission, PermissionType):
            if permission.name not in self.permissions:
                self.permissions.append(permission.name)

    def remove_permission(self, permission):
        """
        Remover permissão da role
        """
        if isinstance(permission, PermissionType):
            if permission.name in self.permissions:
                self.permissions.remove(permission.name)

    def __repr__(self):
        return f'<Role {self.name}>'
