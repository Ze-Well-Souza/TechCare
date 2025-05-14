from app.models.service_status import ServiceStatus
from app.models.user import User
from app.models.audit_log import AuditLog
from app.services.service_monitoring_service import ServiceMonitoringService
from sqlalchemy import func
from datetime import datetime, timedelta, UTC
import logging

class DashboardService:
    """
    Serviço para geração de dados do dashboard principal
    """
    
    @classmethod
    def get_system_overview(cls, days=7):
        """
        Obter visão geral do sistema
        
        :param days: Número de dias para análise
        :return: Dicionário com métricas do sistema
        """
        try:
            end_date = datetime.now(UTC)
            start_date = end_date - timedelta(days=days)
            
            # Métricas de serviços
            services_status = ServiceStatus.get_system_health_summary()
            
            # Métricas de usuários
            user_metrics = cls._get_user_metrics(start_date, end_date)
            
            # Métricas de auditoria
            audit_metrics = cls._get_audit_metrics(start_date, end_date)
            
            # Recursos do sistema
            system_resources = ServiceMonitoringService.get_system_resource_usage()
            
            return {
                'services': services_status,
                'users': user_metrics,
                'audit_logs': audit_metrics,
                'system_resources': system_resources,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat()
                }
            }
        
        except Exception as e:
            logging.error(f"Erro ao obter visão geral do sistema: {e}")
            return None
    
    @classmethod
    def _get_user_metrics(cls, start_date, end_date):
        """
        Obter métricas de usuários
        
        :param start_date: Data de início
        :param end_date: Data de término
        :return: Dicionário de métricas de usuários
        """
        try:
            # Total de usuários
            total_users = User.query.count()
            
            # Novos usuários no período
            new_users = User.query.filter(
                User.created_at.between(start_date, end_date)
            ).count()
            
            # Usuários ativos
            active_users = User.query.filter(
                User.last_login_at.between(start_date, end_date)
            ).count()
            
            # Distribuição de roles
            role_distribution = cls._get_role_distribution()
            
            return {
                'total_users': total_users,
                'new_users': new_users,
                'active_users': active_users,
                'role_distribution': role_distribution
            }
        
        except Exception as e:
            logging.error(f"Erro ao obter métricas de usuários: {e}")
            return {}
    
    @classmethod
    def _get_role_distribution(cls):
        """
        Obter distribuição de roles de usuários
        
        :return: Dicionário com contagem de usuários por role
        """
        try:
            # Consulta para contar usuários por role
            role_counts = (
                User.query
                .join(User.role)
                .with_entities(User.role.name, func.count(User.id))
                .group_by(User.role.name)
                .all()
            )
            
            return dict(role_counts)
        
        except Exception as e:
            logging.error(f"Erro ao obter distribuição de roles: {e}")
            return {}
    
    @classmethod
    def _get_audit_metrics(cls, start_date, end_date):
        """
        Obter métricas de logs de auditoria
        
        :param start_date: Data de início
        :param end_date: Data de término
        :return: Dicionário de métricas de auditoria
        """
        try:
            # Total de logs de auditoria
            total_logs = AuditLog.query.filter(
                AuditLog.timestamp.between(start_date, end_date)
            ).count()
            
            # Logs por tipo de ação
            action_type_counts = (
                AuditLog.query
                .filter(AuditLog.timestamp.between(start_date, end_date))
                .with_entities(AuditLog.action_type, func.count(AuditLog.id))
                .group_by(AuditLog.action_type)
                .all()
            )
            
            # Logs por usuário
            user_log_counts = (
                AuditLog.query
                .filter(AuditLog.timestamp.between(start_date, end_date))
                .join(AuditLog.user)
                .with_entities(User.username, func.count(AuditLog.id))
                .group_by(User.username)
                .order_by(func.count(AuditLog.id).desc())
                .limit(10)
                .all()
            )
            
            return {
                'total_logs': total_logs,
                'action_type_counts': dict(action_type_counts),
                'top_users_by_logs': dict(user_log_counts)
            }
        
        except Exception as e:
            logging.error(f"Erro ao obter métricas de auditoria: {e}")
            return {}
