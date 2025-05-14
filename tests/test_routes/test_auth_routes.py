"""
Testes para as rotas de autenticação
"""
import pytest
from flask import url_for, session
from flask_login import current_user

def test_login_page(client):
    """Testa se a página de login é carregada corretamente."""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'Login' in response.data
    assert b'Nome de usu' in response.data  # Parte da string 'Nome de usuário'
    assert b'Senha' in response.data

def test_register_page(client):
    """Testa se a página de registro é carregada corretamente."""
    response = client.get('/auth/register')
    assert response.status_code == 200
    assert b'Cadastre-se' in response.data
    assert b'Nome de usu' in response.data  # Parte da string 'Nome de usuário'
    assert b'Email' in response.data
    assert b'Senha' in response.data
    assert b'Confirme a senha' in response.data

def test_successful_login(client, test_user):
    """Testa um login bem-sucedido."""
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'password123',
        'remember_me': 'on'
    }, follow_redirects=True)
    
    assert response.status_code == 200

def test_failed_login(client):
    """Testa um login malsucedido com credenciais inválidas."""
    response = client.post('/auth/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    assert b'Nome de usu' in response.data or b'invalid' in response.data.lower()

def test_logout(auth_client):
    """Testa o logout de um usuário logado."""
    response = auth_client.get('/auth/logout', follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verifica se foi redirecionado para a página de login ou início
    assert b'Login' in response.data or b'TechCare' in response.data

def test_register_new_user(client):
    """Testa o registro de um novo usuário."""
    response = client.post('/auth/register', data={
        'username': 'newuser',
        'name': 'New User',
        'email': 'new@example.com',
        'password': 'newpass123',
        'password_confirm': 'newpass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Verifica se foi redirecionado para a página de login após o registro
    assert b'Login' in response.data

def test_register_duplicate_username(client, test_user):
    """Testa o registro com nome de usuário duplicado."""
    response = client.post('/auth/register', data={
        'username': 'testuser',  # Nome já existente
        'name': 'Another User',
        'email': 'another@example.com',
        'password': 'pass123',
        'password_confirm': 'pass123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Ainda deve estar na página de registro
    assert b'Cadastre-se' in response.data

def test_register_passwords_dont_match(client):
    """Testa o registro com senhas que não coincidem."""
    response = client.post('/auth/register', data={
        'username': 'newuser2',
        'name': 'New User 2',
        'email': 'new2@example.com',
        'password': 'password123',
        'password_confirm': 'differentpassword'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Ainda deve estar na página de registro
    assert b'Cadastre-se' in response.data

def test_protected_route_redirect(client):
    """Testa redirecionamento para login ao acessar rota protegida."""
    # Tenta acessar uma rota que requer login
    response = client.get('/diagnostic', follow_redirects=True)
    
    assert response.status_code == 200
    # Verifica se foi redirecionado para a página de login
    assert b'Login' in response.data

def test_protected_route_access(auth_client):
    """Testa acesso a rota protegida após login."""
    # Deve configurar uma rota protegida específica para este teste
    response = auth_client.get('/diagnostic', follow_redirects=True)
    
    assert response.status_code == 200
    # O usuário deve ter acesso à área protegida
    assert b'Logout' in response.data or b'Sair' in response.data

def test_auth_middleware_current_user(auth_client):
    """Testa se o middleware de autenticação está configurado corretamente."""
    with auth_client.application.test_request_context():
        with auth_client.session_transaction() as sess:
            # Verifica se há uma sessão de usuário ativa
            assert '_user_id' in sess

def test_register_mismatched_passwords(client):
    """Testa registro com senhas diferentes."""
    response = client.post('/auth/register', data={
        'username': 'mismatched',
        'name': 'Mismatched User',
        'email': 'mismatched@example.com',
        'password': 'password123',
        'password_confirm': 'different'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    # Ainda deve estar na página de registro
    assert b'Cadastre-se' in response.data 