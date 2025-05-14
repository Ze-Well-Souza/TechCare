import os
from datetime import timedelta

class Config:
    """
    Configurações base da aplicação
    """
    # Configurações gerais
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')
    DEBUG = False
    TESTING = False

    # Configurações de banco de dados
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'sqlite:///techcare.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações de Celery
    CELERY_BROKER_URL = os.environ.get(
        'CELERY_BROKER_URL', 
        'redis://localhost:6379/0'
    )
    CELERY_RESULT_BACKEND = os.environ.get(
        'CELERY_RESULT_BACKEND', 
        'redis://localhost:6379/0'
    )

    # Configurações de JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret_key_change_in_production')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    # Configurações de segurança
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True

class DevelopmentConfig(Config):
    """
    Configurações para ambiente de desenvolvimento
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True

class TestingConfig(Config):
    """
    Configurações para ambiente de testes
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

class ProductionConfig(Config):
    """
    Configurações para ambiente de produção
    """
    DEBUG = False
    
    # Configurações de segurança adicionais
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True

def get_config():
    """
    Selecionar configuração baseada no ambiente
    """
    env = os.environ.get('FLASK_ENV', 'development')
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig
    }
    return config_map.get(env, DevelopmentConfig)
