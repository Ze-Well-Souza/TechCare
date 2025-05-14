from app.models.user_activity_log import UserActivityLog, UserActivityType
from app.extensions import db
from datetime import datetime, timedelta
import logging

class UserActivityService:
    """
    Serviço para gerenciamento de logs de atividade de usuário
    """
    
    @classmethod
    def log_login(cls, user, ip_address=None, user_agent=None):
        """
        Registrar log de login
        
        :param user: Usuário que fez login
        :param ip_address: Endereço IP do login
        :param user_agent: User agent do cliente
        """
        try:
            UserActivityLog.log_activity(
                user_id=user.id,
                activity_type=UserActivityType.LOGIN,
                description=f"Login de usuário: {user.username}",
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as e:
            logging.error(f"Erro ao registrar log de login: {e}")
    
    @classmethod
    def log_logout(cls, user, ip_address=None, user_agent=None):
        """
        Registrar log de logout
        
        :param user: Usuário que fez logout
        :param ip_address: Endereço IP do logout
        :param user_agent: User agent do cliente
        """
        try:
            UserActivityLog.log_activity(
                user_id=user.id,
                activity_type=UserActivityType.LOGOUT,
                description=f"Logout de usuário: {user.username}",
                ip_address=ip_address,
                user_agent=user_agent
            )
        except Exception as e:
            logging.error(f"Erro ao registrar log de logout: {e}")
    
    @classmethod
    def log_role_change(cls, user, old_role, new_role):
        """
        Registrar mudança de role
        
        :param user: Usuário que teve a role alterada
        :param old_role: Role anterior
        :param new_role: Nova role
        """
        try:
            UserActivityLog.log_activity(
                user_id=user.id,
                activity_type=UserActivityType.ROLE_CHANGE,
                description=f"Alteração de role: {old_role.name} -> {new_role.name}",
                old_value={'role_id': old_role.id, 'role_name': old_role.name},
                new_value={'role_id': new_role.id, 'role_name': new_role.name}
            )
        except Exception as e:
            logging.error(f"Erro ao registrar mudança de role: {e}")
    
    @classmethod
    def log_permission_change(cls, role, added_permissions=None, removed_permissions=None):
        """
        Registrar mudança de permissões
        
        :param role: Role com permissões alteradas
        :param added_permissions: Permissões adicionadas
        :param removed_permissions: Permissões removidas
        """
        try:
            UserActivityLog.log_activity(
                user_id=None,  # Log de sistema
                activity_type=UserActivityType.PERMISSION_CHANGE,
                description=f"Alteração de permissões da role: {role.name}",
                old_value={'removed_permissions': [p.name for p in removed_permissions]} if removed_permissions else None,
                new_value={'added_permissions': [p.name for p in added_permissions]} if added_permissions else None
            )
        except Exception as e:
            logging.error(f"Erro ao registrar mudança de permissões: {e}")
    
    @classmethod
    def get_user_activity_summary(cls, user_id, days=30):
        """
        Obter resumo de atividades do usuário
        
        :param user_id: ID do usuário
        :param days: Número de dias para análise
        :return: Dicionário com resumo de atividades
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        try:
            activities, total = UserActivityLog.get_user_activities(
                user_id=user_id,
                start_date=start_date,
                end_date=end_date
            )
            
            # Resumo por tipo de atividade
            activity_summary = {}
            for activity in activities:
                activity_type = activity.activity_type.name
                activity_summary[activity_type] = activity_summary.get(activity_type, 0) + 1
            
            return {
                'total_activities': total,
                'activity_summary': activity_summary,
                'start_date': start_date,
                'end_date': end_date
            }
        
        except Exception as e:
            logging.error(f"Erro ao obter resumo de atividades: {e}")
            return {
                'total_activities': 0,
                'activity_summary': {},
                'start_date': start_date,
                'end_date': end_date
            }
    
    @classmethod
    def cleanup_old_activity_logs(cls, retention_days=90):
        """
        Limpar logs de atividade antigos
        
        :param retention_days: Número de dias para manter logs
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            # Deletar logs antigos
            deleted_count = UserActivityLog.query.filter(
                UserActivityLog.timestamp < cutoff_date
            ).delete()
            
            db.session.commit()
            
            logging.info(f"Limpeza de logs de atividade: {deleted_count} logs removidos")
            return deleted_count
        
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao limpar logs de atividade: {e}")
            return 0
