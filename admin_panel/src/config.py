import os
from datetime import timedelta

class Config:
    # Configurações de Segurança
    SECRET_KEY = os.getenv('SECRET_KEY', 'fallback_development_secret_key')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 15)))
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES', 30)))

    # Configurações de Banco de Dados
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///admin_panel.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Configurações de CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

    # Configurações de Segurança Adicional
    PASSWORD_MIN_LENGTH = 8
    PASSWORD_MAX_LENGTH = 64
    USERNAME_MIN_LENGTH = 3
    USERNAME_MAX_LENGTH = 50

    # Políticas de Segurança
    SECURITY_POLICIES = {
        'require_uppercase': True,
        'require_lowercase': True,
        'require_numbers': True,
        'require_special_chars': True,
        'max_login_attempts': 5,
        'lockout_duration': timedelta(minutes=15)
    }

    # Configurações de Logging
    LOGGING_CONFIG = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'level': 'INFO',
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
            'file': {
                'level': 'WARNING',
                'formatter': 'standard',
                'class': 'logging.FileHandler',
                'filename': 'admin_panel.log'
            }
        },
        'loggers': {
            '': {  # root logger
                'handlers': ['default', 'file'],
                'level': 'INFO',
                'propagate': True
            }
        }
    }

    @classmethod
    def is_production(cls):
        return os.getenv('FLASK_ENV', 'development') == 'production'

    @classmethod
    def validate_password(cls, password):
        """Valida a força da senha"""
        if not (cls.PASSWORD_MIN_LENGTH <= len(password) <= cls.PASSWORD_MAX_LENGTH):
            return False

        policies = cls.SECURITY_POLICIES
        checks = [
            (policies['require_uppercase'], lambda p: any(c.isupper() for c in p)),
            (policies['require_lowercase'], lambda p: any(c.islower() for c in p)),
            (policies['require_numbers'], lambda p: any(c.isdigit() for c in p)),
            (policies['require_special_chars'], lambda p: any(not c.isalnum() for c in p))
        ]

        return all(check(password) for required, check in checks if required)

    @classmethod
    def get_cors_config(cls):
        """Retorna configurações de CORS"""
        return {
            'origins': cls.CORS_ORIGINS,
            'supports_credentials': True
        }
