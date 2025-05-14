from app.models.system_config import SystemConfig
from app.models.user_activity_log import UserActivityLog, UserActivityType
from app.extensions import db
import logging
import json

class SystemConfigService:
    """
    Serviço para gerenciamento de configurações do sistema
    """
    
    @classmethod
    def update_config(
        cls, 
        config_key, 
        config_value, 
        description=None, 
        is_sensitive=False, 
        user_id=None
    ):
        """
        Atualizar configuração do sistema
        
        :param config_key: Chave de configuração
        :param config_value: Valor da configuração
        :param description: Descrição opcional
        :param is_sensitive: Se a configuração é sensível
        :param user_id: ID do usuário que fez a alteração
        :return: Resultado da operação
        """
        try:
            # Validar valor da configuração
            if not SystemConfig.validate_config(config_key, config_value):
                return {
                    'success': False,
                    'message': f'Valor inválido para a configuração {config_key}'
                }
            
            # Atualizar configuração
            config = SystemConfig.set_config(
                config_key=config_key,
                config_value=config_value,
                description=description,
                is_sensitive=is_sensitive,
                user_id=user_id
            )
            
            # Registrar atividade
            if user_id:
                UserActivityLog.log_activity(
                    user_id=user_id,
                    activity_type=UserActivityType.SYSTEM_CONFIG,
                    description=f'Configuração atualizada: {config_key}',
                    old_value={'config_key': config_key},
                    new_value={'config_value': config_value}
                )
            
            return {
                'success': True,
                'message': f'Configuração {config_key} atualizada com sucesso',
                'config': config.to_dict(include_sensitive=False)
            }
        
        except Exception as e:
            logging.error(f"Erro ao atualizar configuração {config_key}: {e}")
            return {
                'success': False,
                'message': f'Erro ao atualizar configuração {config_key}',
                'error': str(e)
            }
    
    @classmethod
    def get_config(cls, config_key, default=None):
        """
        Obter valor de configuração
        
        :param config_key: Chave de configuração
        :param default: Valor padrão se não encontrado
        :return: Valor da configuração
        """
        try:
            return SystemConfig.get_config(config_key, default)
        except Exception as e:
            logging.error(f"Erro ao obter configuração {config_key}: {e}")
            return default
    
    @classmethod
    def delete_config(cls, config_key, user_id=None):
        """
        Excluir configuração
        
        :param config_key: Chave de configuração
        :param user_id: ID do usuário que fez a exclusão
        :return: Resultado da operação
        """
        try:
            # Verificar se a configuração existe
            existing_config = SystemConfig.query.filter_by(config_key=config_key).first()
            
            if not existing_config:
                return {
                    'success': False,
                    'message': f'Configuração {config_key} não encontrada'
                }
            
            # Excluir configuração
            SystemConfig.delete_config(config_key)
            
            # Registrar atividade
            if user_id:
                UserActivityLog.log_activity(
                    user_id=user_id,
                    activity_type=UserActivityType.SYSTEM_CONFIG,
                    description=f'Configuração excluída: {config_key}',
                    old_value={'config_key': config_key}
                )
            
            return {
                'success': True,
                'message': f'Configuração {config_key} excluída com sucesso'
            }
        
        except Exception as e:
            logging.error(f"Erro ao excluir configuração {config_key}: {e}")
            return {
                'success': False,
                'message': f'Erro ao excluir configuração {config_key}',
                'error': str(e)
            }
    
    @classmethod
    def get_all_configs(cls, include_sensitive=False):
        """
        Obter todas as configurações
        
        :param include_sensitive: Se configurações sensíveis devem ser incluídas
        :return: Lista de configurações
        """
        try:
            configs = SystemConfig.get_all_configs(include_sensitive)
            return [
                config.to_dict(include_sensitive=include_sensitive) 
                for config in configs
            ]
        except Exception as e:
            logging.error(f"Erro ao obter todas as configurações: {e}")
            return []
    
    @classmethod
    def load_default_configs(cls):
        """
        Carregar configurações padrão do sistema
        """
        default_configs = [
            {
                'config_key': 'debug_mode',
                'config_value': False,
                'description': 'Modo de depuração do sistema',
                'is_sensitive': False
            },
            {
                'config_key': 'max_login_attempts',
                'config_value': 5,
                'description': 'Máximo de tentativas de login',
                'is_sensitive': False
            },
            {
                'config_key': 'session_timeout',
                'config_value': 3600,  # 1 hora
                'description': 'Tempo de expiração da sessão em segundos',
                'is_sensitive': False
            },
            {
                'config_key': 'log_retention_days',
                'config_value': 90,
                'description': 'Dias para retenção de logs',
                'is_sensitive': False
            },
            {
                'config_key': 'maintenance_mode',
                'config_value': False,
                'description': 'Modo de manutenção do sistema',
                'is_sensitive': False
            }
        ]
        
        for config in default_configs:
            # Verificar se a configuração já existe
            existing_config = SystemConfig.query.filter_by(
                config_key=config['config_key']
            ).first()
            
            if not existing_config:
                SystemConfig.set_config(**config)
        
        db.session.commit()
