from app.extensions import db
from datetime import datetime, UTC
import json
import uuid

class SystemConfig(db.Model):
    """
    Modelo para armazenar configurações globais do sistema
    """
    __tablename__ = 'system_configs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Chave de configuração única
    config_key = db.Column(db.String(100), nullable=False, unique=True, index=True)
    
    # Valor da configuração (armazenado como JSON para flexibilidade)
    config_value = db.Column(db.JSON, nullable=False)
    
    # Metadados da configuração
    description = db.Column(db.Text)
    is_sensitive = db.Column(db.Boolean, default=False)
    
    # Controle de versão e auditoria
    created_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(UTC),
        nullable=False
    )
    updated_at = db.Column(
        db.DateTime, 
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False
    )
    
    # Relacionamento com usuário que fez a última modificação
    last_modified_by_id = db.Column(
        db.Integer, 
        db.ForeignKey('users.id'), 
        nullable=True
    )
    last_modified_by = db.relationship(
        'User', 
        backref='system_config_changes'
    )

    @classmethod
    def set_config(
        cls, 
        config_key, 
        config_value, 
        description=None, 
        is_sensitive=False, 
        user_id=None
    ):
        """
        Definir ou atualizar uma configuração do sistema
        
        :param config_key: Chave de configuração
        :param config_value: Valor da configuração
        :param description: Descrição opcional
        :param is_sensitive: Se a configuração é sensível
        :param user_id: ID do usuário que fez a alteração
        :return: Instância de configuração
        """
        # Converter valor para JSON se não for
        if not isinstance(config_value, (str, dict, list, int, float, bool)):
            config_value = str(config_value)
        
        # Buscar configuração existente
        config = cls.query.filter_by(config_key=config_key).first()
        
        if not config:
            # Criar nova configuração
            config = cls(
                config_key=config_key,
                config_value=config_value,
                description=description,
                is_sensitive=is_sensitive,
                last_modified_by_id=user_id
            )
        else:
            # Atualizar configuração existente
            config.config_value = config_value
            config.description = description or config.description
            config.is_sensitive = is_sensitive
            config.last_modified_by_id = user_id
        
        db.session.add(config)
        db.session.commit()
        
        return config

    @classmethod
    def get_config(cls, config_key, default=None):
        """
        Obter valor de configuração
        
        :param config_key: Chave de configuração
        :param default: Valor padrão se não encontrado
        :return: Valor da configuração
        """
        config = cls.query.filter_by(config_key=config_key).first()
        return config.config_value if config else default

    @classmethod
    def delete_config(cls, config_key):
        """
        Excluir uma configuração
        
        :param config_key: Chave de configuração
        :return: Booleano indicando sucesso
        """
        config = cls.query.filter_by(config_key=config_key).first()
        
        if config:
            db.session.delete(config)
            db.session.commit()
            return True
        
        return False

    @classmethod
    def get_all_configs(cls, include_sensitive=False):
        """
        Obter todas as configurações
        
        :param include_sensitive: Se configurações sensíveis devem ser incluídas
        :return: Lista de configurações
        """
        if include_sensitive:
            return cls.query.all()
        
        return cls.query.filter_by(is_sensitive=False).all()

    @classmethod
    def validate_config(cls, config_key, config_value):
        """
        Validar valor de configuração baseado em regras predefinidas
        
        :param config_key: Chave de configuração
        :param config_value: Valor a ser validado
        :return: Booleano indicando validade
        """
        validation_rules = {
            'debug_mode': lambda x: isinstance(x, bool),
            'max_login_attempts': lambda x: isinstance(x, int) and 1 <= x <= 10,
            'session_timeout': lambda x: isinstance(x, int) and x > 0,
            'log_retention_days': lambda x: isinstance(x, int) and 1 <= x <= 365,
            'maintenance_mode': lambda x: isinstance(x, bool)
        }
        
        validator = validation_rules.get(config_key)
        return validator(config_value) if validator else True

    def to_dict(self, include_sensitive=False):
        """
        Converter configuração para dicionário
        
        :param include_sensitive: Se valores sensíveis devem ser incluídos
        :return: Dicionário de configuração
        """
        config_dict = {
            'id': self.id,
            'config_key': self.config_key,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        # Incluir valor apenas se não for sensível ou se explicitamente solicitado
        if not self.is_sensitive or include_sensitive:
            config_dict['config_value'] = self.config_value
        
        return config_dict
