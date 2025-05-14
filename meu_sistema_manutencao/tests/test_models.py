import pytest
from app.models import User, Log, Machine, PLANOS

def test_user_creation(test_user):
    """Testar criação de usuário."""
    assert test_user.nome == 'Usuário Teste'
    assert test_user.email == 'teste@exemplo.com'
    assert test_user.plano == 'free'
    assert not test_user.is_admin

def test_user_password(test_user):
    """Testar métodos de senha."""
    assert test_user.check_password('senha_teste')
    assert not test_user.check_password('senha_errada')

def test_admin_creation(test_admin):
    """Testar criação de usuário administrador."""
    assert test_admin.nome == 'Admin Teste'
    assert test_admin.email == 'admin@exemplo.com'
    assert test_admin.is_admin
    assert test_admin.plano == 'profissional'

def test_log_creation(test_db, test_user):
    """Testar criação de log."""
    log = Log(user_id=test_user.id, acao='diagnostico', detalhes='Teste de log')
    test_db.session.add(log)
    test_db.session.commit()
    
    assert log.user == test_user
    assert log.acao == 'diagnostico'

def test_machine_creation(test_db, test_user):
    """Testar criação de máquina."""
    machine = Machine(
        user_id=test_user.id, 
        nome='PC Teste', 
        specs={'cpu': 'Intel', 'ram': '8GB'}
    )
    test_db.session.add(machine)
    test_db.session.commit()
    
    assert machine.user == test_user
    assert machine.nome == 'PC Teste'
    assert machine.specs == {'cpu': 'Intel', 'ram': '8GB'}

def test_planos_structure():
    """Testar estrutura dos planos."""
    assert 'free' in PLANOS
    assert 'intermediario' in PLANOS
    assert 'profissional' in PLANOS
    
    for plano in ['free', 'intermediario', 'profissional']:
        assert 'nome' in PLANOS[plano]
        assert 'preco' in PLANOS[plano]
        assert 'max_machines' in PLANOS[plano]
        assert 'features' in PLANOS[plano]
        
        features_keys = ['diagnostico', 'limpeza', 'instalacao', 'pos_formatacao', 'relatorios']
        for feature in features_keys:
            assert feature in PLANOS[plano]['features']
