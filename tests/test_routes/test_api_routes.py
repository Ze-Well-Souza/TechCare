"""
Testes para as rotas da API da aplicação
"""
import pytest
import json
from unittest.mock import patch, MagicMock

def test_api_status(client):
    """Testa a rota de status da API"""
    response = client.get('/api/status')
    
    assert response.status_code == 200
    data = json.loads(response.data)
    
    assert data['status'] == 'online'
    assert 'version' in data
    assert 'timestamp' in data

def test_api_system_info(auth_client):
    """Testa a rota de informações do sistema"""
    # Mock para os dados do sistema
    with patch('app.routes.api.get_system_info') as mock_system_info:
        mock_system_info.return_value = {
            'os': 'Windows 10',
            'cpu': 'Intel Core i7',
            'memory': '16GB',
            'disk': '512GB SSD'
        }
        
        response = auth_client.get('/api/system/info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'system_info' in data
        assert data['system_info']['os'] == 'Windows 10'
        assert data['system_info']['cpu'] == 'Intel Core i7'

def test_api_system_info_unauthorized(client):
    """Testa que a rota de informações do sistema requer autenticação"""
    response = client.get('/api/system/info')
    
    # Deve redirecionar para login
    assert response.status_code == 302
    assert 'login' in response.location

def test_api_documentation(client):
    """Testa a rota de documentação da API"""
    response = client.get('/api/docs')
    
    assert response.status_code == 200
    assert b'API Documentation' in response.data
    
    # Verifica se contém informações sobre os endpoints
    assert b'endpoints' in response.data.lower() or b'routes' in response.data.lower() 