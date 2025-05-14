import pytest
from src.config import Config

def test_password_validation():
    # Senhas válidas
    valid_passwords = [
        'StrongPass123!',
        'Secure@2023',
        'Complex#Password9'
    ]

    # Senhas inválidas
    invalid_passwords = [
        'short',  # muito curta
        'onlylowercase',  # sem maiúsculas, números ou caracteres especiais
        'ONLYUPPERCASE',  # sem minúsculas, números ou caracteres especiais
        'NoSpecialChars123',  # sem caracteres especiais
        'a' * 100  # muito longa
    ]

    # Testa senhas válidas
    for password in valid_passwords:
        assert Config.validate_password(password) is True, f"Senha {password} deveria ser válida"

    # Testa senhas inválidas
    for password in invalid_passwords:
        assert Config.validate_password(password) is False, f"Senha {password} deveria ser inválida"

def test_config_environment():
    # Testa métodos de configuração
    assert hasattr(Config, 'is_production')
    assert hasattr(Config, 'get_cors_config')

def test_security_policies():
    # Verifica se as políticas de segurança estão definidas
    policies = Config.SECURITY_POLICIES
    assert 'require_uppercase' in policies
    assert 'require_lowercase' in policies
    assert 'require_numbers' in policies
    assert 'require_special_chars' in policies
    assert 'max_login_attempts' in policies
    assert 'lockout_duration' in policies

def test_cors_config():
    # Testa a configuração de CORS
    cors_config = Config.get_cors_config()
    assert 'origins' in cors_config
    assert 'supports_credentials' in cors_config
    assert cors_config['supports_credentials'] is True

def test_token_expiration():
    # Verifica as configurações de expiração de token
    assert Config.JWT_ACCESS_TOKEN_EXPIRES.total_seconds() > 0
    assert Config.JWT_REFRESH_TOKEN_EXPIRES.total_seconds() > Config.JWT_ACCESS_TOKEN_EXPIRES.total_seconds()
