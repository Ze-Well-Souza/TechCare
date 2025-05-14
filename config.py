import os
import secrets
import sys
from pathlib import Path

# Detecção de ambiente
IS_PYTHONANYWHERE = "PYTHONANYWHERE_DOMAIN" in os.environ
IS_WINDOWS = sys.platform.startswith('win')

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent

# Configurações do ambiente
class Config:
    """Configuração base para todos os ambientes"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Configurações de diagnóstico
    # O PythonAnywhere geralmente precisa de caminhos específicos
    if IS_PYTHONANYWHERE:
        # No PythonAnywhere, usamos o diretório home do usuário
        PA_USERNAME = os.environ.get('USERNAME', 'defaultuser')
        DIAGNOSTIC_SAVE_PATH = os.path.join('/home', PA_USERNAME, 'data', 'diagnostics')
        REPAIR_LOGS_PATH = os.path.join('/home', PA_USERNAME, 'data', 'repair_logs')
        DIAGNOSTICS_STORAGE_PATH = os.path.join('/home', PA_USERNAME, 'data', 'diagnostics_storage')
    else:
        # Em desenvolvimento local, usamos diretórios relativos à instância
        DIAGNOSTIC_SAVE_PATH = os.path.join(BASE_DIR, 'instance', 'diagnostics')
        REPAIR_LOGS_PATH = os.path.join(BASE_DIR, 'instance', 'repair_logs')
        DIAGNOSTICS_STORAGE_PATH = os.path.join(BASE_DIR, 'instance', 'diagnostics_storage')
    
    # Configurações do sistema
    APP_NAME = "TechCare"
    APP_VERSION = "1.0.0"
    ADMIN_EMAIL = "admin@techcare.com.br"
    
    # Configurações de cache
    CACHE_ENABLED = True
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos
    
    # Garante que os diretórios de dados existam
    @staticmethod
    def init_app(app):
        os.makedirs(Config.DIAGNOSTIC_SAVE_PATH, exist_ok=True)
        os.makedirs(Config.REPAIR_LOGS_PATH, exist_ok=True)
        os.makedirs(Config.DIAGNOSTICS_STORAGE_PATH, exist_ok=True)
        # Configuração adicional baseada no ambiente
        if IS_PYTHONANYWHERE:
            app.config['PREFERRED_URL_SCHEME'] = 'https'


class DevelopmentConfig(Config):
    """Configuração para ambiente de desenvolvimento"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'techcare-dev.db')


class TestingConfig(Config):
    """Configuração para ambiente de testes"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'techcare-test.db')
    CACHE_ENABLED = False  # Desativa cache em testes


class ProductionConfig(Config):
    """Configuração para ambiente de produção"""
    if IS_PYTHONANYWHERE:
        # Em PythonAnywhere, armazene o banco de dados no diretório do usuário
        PA_USERNAME = os.environ.get('USERNAME', 'defaultuser')
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join('/home', PA_USERNAME, 'techcare.db')
    else:
        # Em outras instalações de produção
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'sqlite:///' + os.path.join(BASE_DIR, 'instance', 'techcare.db')
    
    # Em produção, recomenda-se usar uma string secreta forte salva em variável de ambiente
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)
    
    # Configurações de cache para produção
    CACHE_DEFAULT_TIMEOUT = 600  # 10 minutos


# Dicionário com os ambientes disponíveis
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
} 