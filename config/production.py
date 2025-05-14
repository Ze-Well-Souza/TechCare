"""
Configuração para o ambiente de produção do TechCare

Este arquivo contém as configurações específicas para o ambiente de produção,
com foco em segurança, performance e estabilidade.
"""

import os
from pathlib import Path
import secrets

# Diretório base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações de banco de dados
# Em produção, recomendamos PostgreSQL para maior confiabilidade e performance
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'postgresql://techcare:@localhost/techcare_production'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
}

# Segurança
# Em produção, uma SECRET_KEY aleatória e forte deve ser usada
# Deve ser definida como variável de ambiente ou gerada na primeira inicialização
SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(32)

# Desativa o modo de depuração
DEBUG = False
TESTING = False

# Configurações de servidor web
SERVER_NAME = os.environ.get('SERVER_NAME')  # Ex: 'techcare.exemplo.com.br'

# Cookies seguros apenas para HTTPS
SESSION_COOKIE_SECURE = True
REMEMBER_COOKIE_SECURE = True

# Proteção contra ataques XSS e outros
CSRF_ENABLED = True
WTF_CSRF_ENABLED = True
SESSION_COOKIE_HTTPONLY = True

# Configurações de upload de arquivos
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Limita uploads a 16MB

# Diretórios de armazenamento para dados persistentes
DIAGNOSTIC_SAVE_PATH = os.path.join('/var', 'techcare', 'data', 'diagnostics')
REPAIR_LOGS_PATH = os.path.join('/var', 'techcare', 'data', 'repair_logs')
DRIVERS_PATH = os.path.join('/var', 'techcare', 'data', 'drivers')
TEMP_FILES_PATH = os.path.join('/var', 'techcare', 'data', 'temp')

# Logging
LOG_DIR = os.path.join('/var', 'log', 'techcare')
LOG_LEVEL = 'INFO'

# Outros
PREFERRED_URL_SCHEME = 'https'
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'admin@techcare.exemplo.com.br')

# Criação de diretórios necessários
def init_app(app):
    """Inicializa a aplicação para o ambiente de produção."""
    # Cria os diretórios de dados se não existirem
    for path in [DIAGNOSTIC_SAVE_PATH, REPAIR_LOGS_PATH, DRIVERS_PATH, TEMP_FILES_PATH]:
        os.makedirs(path, exist_ok=True)
    
    # Cria o diretório de logs
    os.makedirs(LOG_DIR, exist_ok=True)
    
    # Configuração de logger
    if not app.debug and not app.testing:
        import logging
        from logging.handlers import RotatingFileHandler
        
        # Formato do log: [timestamp] [level] [module] message
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s'
        )
        
        # Log de erros
        error_log = os.path.join(LOG_DIR, 'error.log')
        error_file_handler = RotatingFileHandler(
            error_log, maxBytes=10485760, backupCount=10
        )
        error_file_handler.setFormatter(formatter)
        error_file_handler.setLevel(logging.ERROR)
        
        # Log geral
        info_log = os.path.join(LOG_DIR, 'info.log')
        info_file_handler = RotatingFileHandler(
            info_log, maxBytes=10485760, backupCount=10
        )
        info_file_handler.setFormatter(formatter)
        info_file_handler.setLevel(logging.INFO)
        
        # Adiciona handlers ao logger da aplicação
        app.logger.addHandler(error_file_handler)
        app.logger.addHandler(info_file_handler)
        app.logger.setLevel(logging.INFO)
        
        app.logger.info('TechCare iniciado no ambiente de produção') 