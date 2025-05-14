import pytest
from flask_login import current_user
from app.models import User, Log

def test_login_logout(test_app, test_client, test_db, test_user):
    """Testar fluxo de login e logout."""
    # Login
    response = test_client.post('/auth/login', data={
        'email': 'teste@exemplo.com',
        'password': 'senha_teste'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert current_user.is_authenticated
    assert current_user.email == 'teste@exemplo.com'
    
    # Verificar log de login
    login_log = Log.query.filter_by(user_id=test_user.id, acao='login').first()
    assert login_log is not None
    
    # Logout
    response = test_client.get('/auth/logout', follow_redirects=True)
    assert response.status_code == 200
    assert not current_user.is_authenticated
    
    # Verificar log de logout
    logout_log = Log.query.filter_by(user_id=test_user.id, acao='logout').first()
    assert logout_log is not None

def test_invalid_login(test_app, test_client):
    """Testar login com credenciais inválidas."""
    response = test_client.post('/auth/login', data={
        'email': 'invalido@exemplo.com',
        'password': 'senha_errada'
    }, follow_redirects=True)
    
    assert b'Email ou senha inválidos' in response.data
    assert not current_user.is_authenticated

def test_registration_admin(test_app, test_client, test_db, test_admin):
    """Testar registro de usuário por admin."""
    # Login como admin
    test_client.post('/auth/login', data={
        'email': 'admin@exemplo.com',
        'password': 'admin_teste'
    })
    
    # Registrar novo usuário
    response = test_client.post('/auth/register', data={
        'nome': 'Novo Usuário',
        'email': 'novo@exemplo.com',
        'password': 'senha_novo',
        'confirm_password': 'senha_novo',
        'plano': 'intermediario',
        'is_admin': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verificar usuário criado
    novo_usuario = User.query.filter_by(email='novo@exemplo.com').first()
    assert novo_usuario is not None
    assert novo_usuario.nome == 'Novo Usuário'
    assert novo_usuario.plano == 'intermediario'
    assert not novo_usuario.is_admin
    
    # Verificar log de registro
    registro_log = Log.query.filter_by(acao='registro_usuario').first()
    assert registro_log is not None

def test_registration_unauthorized(test_app, test_client, test_user):
    """Testar registro sem autorização."""
    # Login como usuário comum
    test_client.post('/auth/login', data={
        'email': 'teste@exemplo.com',
        'password': 'senha_teste'
    })
    
    # Tentar registrar usuário
    response = test_client.post('/auth/register', data={
        'nome': 'Usuário Não Autorizado',
        'email': 'nao_autorizado@exemplo.com',
        'password': 'senha_teste',
        'confirm_password': 'senha_teste',
        'plano': 'free'
    }, follow_redirects=True)
    
    assert b'Voc\xc3\xaa n\xc3\xa3o tem permiss\xc3\xa3o' in response.data
    
    # Verificar que usuário não foi criado
    usuario_nao_autorizado = User.query.filter_by(email='nao_autorizado@exemplo.com').first()
    assert usuario_nao_autorizado is None
