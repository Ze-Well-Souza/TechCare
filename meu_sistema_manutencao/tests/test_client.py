import pytest
from app.models import Machine, Log

def test_client_dashboard(test_app, test_client, test_user, test_db):
    """Testar dashboard do cliente."""
    # Adicionar máquina de teste
    machine = Machine(
        user_id=test_user.id, 
        nome='PC Teste', 
        specs={'cpu': 'Intel', 'ram': '8GB'}
    )
    test_db.session.add(machine)
    test_db.session.commit()
    
    # Login como usuário
    test_client.post('/auth/login', data={
        'email': 'teste@exemplo.com',
        'password': 'senha_teste'
    })
    
    # Acessar dashboard
    response = test_client.get('/dashboard')
    assert response.status_code == 200
    
    # Verificar presença de máquina
    assert b'PC Teste' in response.data

def test_machine_diagnostic_free_plan(test_app, test_client, test_user, test_db):
    """Testar diagnóstico com plano free."""
    # Adicionar máquina de teste
    machine = Machine(
        user_id=test_user.id, 
        nome='PC Teste', 
        specs={'cpu': 'Intel', 'ram': '8GB'}
    )
    test_db.session.add(machine)
    test_db.session.commit()
    
    # Login como usuário
    test_client.post('/auth/login', data={
        'email': 'teste@exemplo.com',
        'password': 'senha_teste'
    })
    
    # Tentar diagnosticar máquina
    response = test_client.get(f'/machine/diagnostic/{machine.id}', follow_redirects=True)
    
    # Verificar restrição de plano
    assert b'Seu plano n\xc3\xa3o permite' in response.data

def test_machine_diagnostic_paid_plan(test_app, test_client, test_db, test_admin):
    """Testar diagnóstico com plano pago."""
    # Alterar plano do usuário
    test_admin.plano = 'intermediario'
    test_db.session.commit()
    
    # Adicionar máquina de teste
    machine = Machine(
        user_id=test_admin.id, 
        nome='PC Admin', 
        specs={'cpu': 'Intel', 'ram': '16GB'}
    )
    test_db.session.add(machine)
    test_db.session.commit()
    
    # Login como admin (plano intermediário)
    test_client.post('/auth/login', data={
        'email': 'admin@exemplo.com',
        'password': 'admin_teste'
    })
    
    # Realizar diagnóstico
    response = test_client.post(f'/machine/diagnostic/{machine.id}', data={
        'check_cpu': True,
        'check_memory': True,
        'check_disk': True,
        'check_network': True
    }, follow_redirects=True)
    
    # Verificar sucesso do diagnóstico
    assert b'Diagn\xc3\xb3stico realizado com sucesso' in response.data
    
    # Verificar log de diagnóstico
    log = Log.query.filter_by(acao='diagnostico_maquina').first()
    assert log is not None
    assert log.user_id == test_admin.id
