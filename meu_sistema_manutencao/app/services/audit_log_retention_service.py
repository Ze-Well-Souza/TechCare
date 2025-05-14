from datetime import datetime, timedelta
from sqlalchemy import and_
from app.models.audit_log import AuditLog
from app.extensions import db
import logging

class AuditLogRetentionService:
    """
    Serviço para gerenciamento de retenção de logs de auditoria
    """
    
    @classmethod
    def get_retention_policy(cls):
        """
        Definir políticas de retenção de logs
        
        Retorna um dicionário com políticas de retenção por tipo de ação
        """
        return {
            'login': timedelta(days=90),      # Logs de login por 3 meses
            'logout': timedelta(days=90),     # Logs de logout por 3 meses
            'create': timedelta(days=180),    # Logs de criação por 6 meses
            'update': timedelta(days=180),    # Logs de atualização por 6 meses
            'delete': timedelta(days=365),    # Logs de exclusão por 1 ano
            'default': timedelta(days=120)    # Política padrão de 4 meses
        }
    
    @classmethod
    def clean_expired_logs(cls, dry_run=False):
        """
        Limpar logs de auditoria expirados
        
        :param dry_run: Se True, simula a limpeza sem remover logs
        :return: Dicionário com estatísticas de logs expirados
        """
        retention_policies = cls.get_retention_policy()
        current_time = datetime.utcnow()
        
        # Estatísticas de limpeza
        cleanup_stats = {
            'total_logs_checked': 0,
            'logs_to_delete': {},
            'total_logs_to_delete': 0
        }
        
        try:
            # Verificar logs para cada tipo de ação
            for action_type, retention_period in retention_policies.items():
                # Calcular data limite para logs deste tipo
                expiration_date = current_time - retention_period
                
                # Encontrar logs expirados
                expired_logs = AuditLog.query.filter(
                    and_(
                        AuditLog.action == action_type,
                        AuditLog.timestamp < expiration_date
                    )
                ).all()
                
                # Registrar estatísticas
                cleanup_stats['logs_to_delete'][action_type] = len(expired_logs)
                cleanup_stats['total_logs_checked'] += len(expired_logs)
                cleanup_stats['total_logs_to_delete'] += len(expired_logs)
                
                # Remover logs, se não for dry run
                if not dry_run and expired_logs:
                    for log in expired_logs:
                        db.session.delete(log)
                    
                    db.session.commit()
            
            # Log de execução
            logging.info(f"Limpeza de logs de auditoria: {cleanup_stats}")
            
            return cleanup_stats
        
        except Exception as e:
            # Registrar erro de limpeza
            logging.error(f"Erro na limpeza de logs de auditoria: {e}")
            
            # Reverter transação em caso de erro
            db.session.rollback()
            
            return {
                'error': str(e),
                'total_logs_checked': 0,
                'logs_to_delete': {},
                'total_logs_to_delete': 0
            }
    
    @classmethod
    def get_log_retention_summary(cls):
        """
        Gerar resumo de retenção de logs
        
        :return: Dicionário com resumo de logs por tipo de ação
        """
        retention_policies = cls.get_retention_policy()
        current_time = datetime.utcnow()
        
        retention_summary = {}
        
        for action_type, retention_period in retention_policies.items():
            # Data limite para logs deste tipo
            expiration_date = current_time - retention_period
            
            # Contar logs ativos e expirados
            total_logs = AuditLog.query.filter(AuditLog.action == action_type).count()
            expired_logs = AuditLog.query.filter(
                and_(
                    AuditLog.action == action_type,
                    AuditLog.timestamp < expiration_date
                )
            ).count()
            
            retention_summary[action_type] = {
                'total_logs': total_logs,
                'expired_logs': expired_logs,
                'retention_period_days': retention_period.days
            }
        
        return retention_summary
