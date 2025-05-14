import pytest
from app.models import User, Log, PLANOS

def test_admin_dashboard_access(test_app, test_client, test_admin):
    """Testar acesso ao painel admin."""
    # Login como admin
    test_client.post('/auth/login', data={
        'email': 'admin@exemplo.com',
        'password': 'admin_teste'
    })
    
    # Acessar dashboard admin
    response = test_client.get('/admin/')
    assert response.status_code == 200
    
    # Verificar métricas
    assert b'Total de Usuários' in response.data
    assert b'Logs do Sistema' in response.data

def test_admin_users_list(test_app, test_client, test_admin, test_db):
    """Testar listagem de usuários."""
    # Login como admin
    test_client.post('/auth/login', data={
        'email': 'admin@exemplo.com',
        'password': 'admin_teste'
    })
    
    # Acessar lista de usuários
    response = test_client.get('/admin/users')
    assert response.status_code == 200
    
    # Verificar presença de usuários
    assert b'admin@exemplo.com' in response.data

def test_user_management(test_app, test_client, test_admin, test_db):
    """Testar gerenciamento de usuário."""
    # Criar usuário para teste
    test_user = User(
        nome='Usuário Teste Gestão',
        email='gestao@exemplo.com',
        plano='free'
    )
    test_user.set_password('senha_teste')
    test_db.session.add(test_user)
    test_db.session.commit()
    
    # Login como admin
    test_client.post('/auth/login', data={
        'email': 'admin@exemplo.com',
        'password': 'admin_teste'
    })
    
    # Atualizar usuário
    response = test_client.post(f'/admin/user/{test_user.id}', data={
        'plano': 'intermediario',
        'is_active': False
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verificar alterações
    updated_user = User.query.get(test_user.id)
    assert updated_user.plano == 'intermediario'
    assert updated_user.is_active == False
    
    # Verificar log de alteração
    log = Log.query.filter_by(acao='editar_usuario').first()
    assert log is not None
    assert 'Plano alterado' in log.detalhes

def test_system_logs(test_app, test_client, test_admin):
    """Testar visualização de logs do sistema."""
    # Login como admin
    test_client.post('/auth/login', data={
        'email': 'admin@exemplo.com',
        'password': 'admin_teste'
    })
    
    # Acessar logs
    response = test_client.get('/admin/logs')
    assert response.status_code == 200
    
    # Verificar elementos de log
    assert b'Logs do Sistema' in response.data

def test_non_admin_access_denied(test_app, test_client, test_user):
    """Testar negação de acesso para usuários não admin."""
    # Login como usuário comum
    test_client.post('/auth/login', data={
        'email': 'teste@exemplo.com',
        'password': 'senha_teste'
    })
    
    # Tentar acessar rotas admin
    routes = ['/admin/', '/admin/users', '/admin/logs']
    
    for route in routes:
        response = test_client.get(route, follow_redirects=True)
        assert b'Acesso negado' in response.data
        assert response.status_code == 200
