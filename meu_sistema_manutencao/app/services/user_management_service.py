from app.models.user import User
from app.models.role import Role
from app.models.audit_log import AuditLog, AuditLogType
from app.extensions import db
from sqlalchemy import or_
from werkzeug.security import generate_password_hash
import logging
from datetime import datetime, UTC

class UserManagementService:
    """
    Serviço para gerenciamento de usuários
    """
    
    @classmethod
    def create_user(
        cls, 
        username, 
        email, 
        password, 
        role_name=None, 
        admin_user_id=None
    ):
        """
        Criar novo usuário
        
        :param username: Nome de usuário
        :param email: E-mail do usuário
        :param password: Senha do usuário
        :param role_name: Nome da role (opcional)
        :param admin_user_id: ID do usuário admin que está criando
        :return: Usuário criado ou None
        """
        try:
            # Verificar se usuário já existe
            existing_user = User.query.filter(
                or_(User.username == username, User.email == email)
            ).first()
            
            if existing_user:
                return {
                    'success': False,
                    'message': 'Usuário ou e-mail já cadastrado'
                }
            
            # Obter role
            role = None
            if role_name:
                role = Role.query.filter_by(name=role_name).first()
                if not role:
                    return {
                        'success': False,
                        'message': f'Role {role_name} não encontrada'
                    }
            
            # Criar novo usuário
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash(password),
                role=role
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            # Registrar log de auditoria
            if admin_user_id:
                AuditLog.log_activity(
                    user_id=admin_user_id,
                    action_type=AuditLogType.USER_CREATED,
                    description=f'Usuário {username} criado',
                    target_user_id=new_user.id
                )
            
            return {
                'success': True,
                'message': 'Usuário criado com sucesso',
                'user': new_user
            }
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao criar usuário: {e}")
            return {
                'success': False,
                'message': 'Erro ao criar usuário',
                'error': str(e)
            }
    
    @classmethod
    def update_user(
        cls, 
        user_id, 
        username=None, 
        email=None, 
        role_name=None, 
        admin_user_id=None
    ):
        """
        Atualizar usuário
        
        :param user_id: ID do usuário a ser atualizado
        :param username: Novo nome de usuário (opcional)
        :param email: Novo e-mail (opcional)
        :param role_name: Novo nome da role (opcional)
        :param admin_user_id: ID do usuário admin que está atualizando
        :return: Resultado da atualização
        """
        try:
            # Buscar usuário
            user = User.query.get(user_id)
            
            if not user:
                return {
                    'success': False,
                    'message': 'Usuário não encontrado'
                }
            
            # Armazenar valores antigos para log de auditoria
            old_username = user.username
            old_email = user.email
            old_role = user.role.name if user.role else None
            
            # Atualizar nome de usuário
            if username and username != user.username:
                user.username = username
            
            # Atualizar e-mail
            if email and email != user.email:
                user.email = email
            
            # Atualizar role
            if role_name:
                role = Role.query.filter_by(name=role_name).first()
                if not role:
                    return {
                        'success': False,
                        'message': f'Role {role_name} não encontrada'
                    }
                user.role = role
            
            db.session.commit()
            
            # Registrar log de auditoria
            if admin_user_id:
                AuditLog.log_activity(
                    user_id=admin_user_id,
                    action_type=AuditLogType.USER_UPDATED,
                    description='Usuário atualizado',
                    details={
                        'old_username': old_username,
                        'new_username': user.username,
                        'old_email': old_email,
                        'new_email': user.email,
                        'old_role': old_role,
                        'new_role': user.role.name if user.role else None
                    },
                    target_user_id=user_id
                )
            
            return {
                'success': True,
                'message': 'Usuário atualizado com sucesso',
                'user': user
            }
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao atualizar usuário: {e}")
            return {
                'success': False,
                'message': 'Erro ao atualizar usuário',
                'error': str(e)
            }
    
    @classmethod
    def delete_user(cls, user_id, admin_user_id=None):
        """
        Excluir usuário
        
        :param user_id: ID do usuário a ser excluído
        :param admin_user_id: ID do usuário admin que está excluindo
        :return: Resultado da exclusão
        """
        try:
            # Buscar usuário
            user = User.query.get(user_id)
            
            if not user:
                return {
                    'success': False,
                    'message': 'Usuário não encontrado'
                }
            
            # Armazenar informações para log de auditoria
            username = user.username
            
            # Excluir usuário
            db.session.delete(user)
            db.session.commit()
            
            # Registrar log de auditoria
            if admin_user_id:
                AuditLog.log_activity(
                    user_id=admin_user_id,
                    action_type=AuditLogType.USER_DELETED,
                    description=f'Usuário {username} excluído',
                    target_user_id=user_id
                )
            
            return {
                'success': True,
                'message': 'Usuário excluído com sucesso'
            }
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao excluir usuário: {e}")
            return {
                'success': False,
                'message': 'Erro ao excluir usuário',
                'error': str(e)
            }
    
    @classmethod
    def get_users_by_role(cls, role_name=None, page=1, per_page=10):
        """
        Listar usuários por role
        
        :param role_name: Nome da role (opcional)
        :param page: Número da página
        :param per_page: Usuários por página
        :return: Lista de usuários
        """
        try:
            # Construir query base
            query = User.query
            
            # Filtrar por role se especificado
            if role_name:
                query = query.join(User.role).filter(Role.name == role_name)
            
            # Paginar resultados
            paginated_users = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            return {
                'users': [
                    {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'role': user.role.name if user.role else None,
                        'last_login': user.last_login_at.isoformat() if user.last_login_at else None
                    } for user in paginated_users.items
                ],
                'total': paginated_users.total,
                'pages': paginated_users.pages,
                'current_page': page
            }
        
        except Exception as e:
            logging.error(f"Erro ao listar usuários por role: {e}")
            return {
                'users': [],
                'total': 0,
                'pages': 0,
                'current_page': page
            }
    
    @classmethod
    def reset_user_password(
        cls, 
        user_id, 
        new_password, 
        admin_user_id=None
    ):
        """
        Redefinir senha do usuário
        
        :param user_id: ID do usuário
        :param new_password: Nova senha
        :param admin_user_id: ID do usuário admin que está redefinindo
        :return: Resultado da redefinição
        """
        try:
            # Buscar usuário
            user = User.query.get(user_id)
            
            if not user:
                return {
                    'success': False,
                    'message': 'Usuário não encontrado'
                }
            
            # Atualizar senha
            user.password = generate_password_hash(new_password)
            db.session.commit()
            
            # Registrar log de auditoria
            if admin_user_id:
                AuditLog.log_activity(
                    user_id=admin_user_id,
                    action_type=AuditLogType.USER_PASSWORD_RESET,
                    description='Senha do usuário redefinida',
                    target_user_id=user_id
                )
            
            return {
                'success': True,
                'message': 'Senha redefinida com sucesso'
            }
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao redefinir senha do usuário: {e}")
            return {
                'success': False,
                'message': 'Erro ao redefinir senha',
                'error': str(e)
            }
