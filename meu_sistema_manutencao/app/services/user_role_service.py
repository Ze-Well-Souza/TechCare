from app.models.user import User
from app.models.role import Role, PermissionType
from app.extensions import db
import logging

class UserRoleService:
    """
    Serviço para gerenciamento de usuários e roles
    """
    
    @classmethod
    def create_user(cls, username, email, password, role_name='Visualizador'):
        """
        Criar usuário com role específica
        
        :param username: Nome de usuário
        :param email: Email do usuário
        :param password: Senha do usuário
        :param role_name: Nome da role (padrão: Visualizador)
        :return: Usuário criado
        """
        try:
            # Buscar role
            role = Role.query.filter_by(name=role_name).first()
            
            # Criar role se não existir
            if not role:
                role = Role(name=role_name)
                db.session.add(role)
            
            # Criar usuário
            user = User(
                username=username, 
                email=email, 
                role=role
            )
            user.password = password
            
            db.session.add(user)
            db.session.commit()
            
            logging.info(f"Usuário {username} criado com role {role_name}")
            return user
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao criar usuário: {e}")
            raise
    
    @classmethod
    def update_user_role(cls, user_id, new_role_name):
        """
        Atualizar role de um usuário
        
        :param user_id: ID do usuário
        :param new_role_name: Nome da nova role
        :return: Usuário atualizado
        """
        try:
            # Buscar usuário
            user = User.query.get(user_id)
            if not user:
                raise ValueError("Usuário não encontrado")
            
            # Buscar nova role
            new_role = Role.query.filter_by(name=new_role_name).first()
            if not new_role:
                raise ValueError(f"Role {new_role_name} não encontrada")
            
            # Atualizar role
            user.role = new_role
            db.session.commit()
            
            logging.info(f"Role do usuário {user.username} atualizada para {new_role_name}")
            return user
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao atualizar role do usuário: {e}")
            raise
    
    @classmethod
    def get_users_by_role(cls, role_name):
        """
        Obter todos os usuários de uma role específica
        
        :param role_name: Nome da role
        :return: Lista de usuários
        """
        try:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                return []
            
            return role.users
        
        except Exception as e:
            logging.error(f"Erro ao buscar usuários por role: {e}")
            return []
    
    @classmethod
    def add_permission_to_role(cls, role_name, permission):
        """
        Adicionar permissão a uma role
        
        :param role_name: Nome da role
        :param permission: Permissão a ser adicionada
        """
        try:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                raise ValueError(f"Role {role_name} não encontrada")
            
            role.add_permission(permission)
            db.session.commit()
            
            logging.info(f"Permissão {permission.name} adicionada à role {role_name}")
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao adicionar permissão à role: {e}")
            raise
    
    @classmethod
    def remove_permission_from_role(cls, role_name, permission):
        """
        Remover permissão de uma role
        
        :param role_name: Nome da role
        :param permission: Permissão a ser removida
        """
        try:
            role = Role.query.filter_by(name=role_name).first()
            if not role:
                raise ValueError(f"Role {role_name} não encontrada")
            
            role.remove_permission(permission)
            db.session.commit()
            
            logging.info(f"Permissão {permission.name} removida da role {role_name}")
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao remover permissão da role: {e}")
            raise
