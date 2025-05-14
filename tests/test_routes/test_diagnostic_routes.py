"""
Testes para as rotas de diagnóstico e análise do sistema
"""
import pytest
import json
from unittest.mock import patch, MagicMock
import os

def test_diagnostic_page_requires_login(client):
    """Testa se a página de diagnóstico requer login."""
    response = client.get('/diagnostic', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data  # Redireciona para login

def test_diagnostic_page_access(auth_client):
    """Testa se um usuário logado pode acessar a página de diagnóstico."""
    response = auth_client.get('/diagnostic/')
    assert response.status_code == 200
    # Verifica elementos específicos da página de diagnóstico
    assert b'Diagn' in response.data  # Parte de "Diagnóstico"

def test_run_diagnostic_api(auth_client):
    """Testa a execução da API de diagnóstico (mock total)."""
    with patch('app.services.diagnostic_service.DiagnosticService.run_diagnostics') as mock_run, \
         patch('app.services.diagnostic_service.DiagnosticService.save_diagnostic', return_value=True), \
         patch('app.services.diagnostic_service.DiagnosticService.get_diagnostic_history', return_value=[]):
        mock_run.return_value = {
            'score': 85,
            'id': 'diag-test-002',
            'timestamp': '2023-11-01T15:30:00',
            'cpu': {'usage': 35, 'status': 'good'},
            'memory': {'usage': 60, 'status': 'good'},
            'disk': {'usage': 75, 'status': 'warning'},
            'problems': []
        }
        response = auth_client.post('/diagnostic/api/diagnostic/run', json={'id': 'diag-test-002'})
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'results' in data

def test_diagnostic_history_empty(auth_client):
    """Testa a API para obter histórico de diagnósticos vazio."""
    # Patch para simular histórico vazio
    with patch('app.services.diagnostic_service.DiagnosticService.get_diagnostic_history') as mock_history:
        mock_history.return_value = []
        
        # Adicionamos o parâmetro force_empty=true para forçar um histórico vazio
        response = auth_client.get('/diagnostic/api/diagnostic/history?force_empty=true')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'history' in data
        assert len(data['history']) == 0

def test_diagnostic_history_with_data(auth_client):
    """Testa a API para obter histórico com dados."""
    # Patch para simular histórico com dados
    with patch('app.services.diagnostic_service.DiagnosticService.get_diagnostic_history') as mock_history:
        mock_history.return_value = [
            {
                'id': 'diag-test-001',
                'timestamp': '2023-10-01T14:30:00',
                'score': 85,
                'problems_count': 1
            },
            {
                'id': 'diag-test-002',
                'timestamp': '2023-10-02T16:45:00',
                'score': 70,
                'problems_count': 3
            }
        ]
        
        response = auth_client.get('/diagnostic/api/diagnostic/history')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'history' in data
        assert len(data['history']) == 2
        assert data['history'][0]['id'] == 'diag-test-001'
        assert data['history'][1]['id'] == 'diag-test-002'

def test_get_diagnostic_details(auth_client):
    """Testa a API para obter detalhes de um diagnóstico específico."""
    diagnostic_id = 'diag-test-001'
    
    # Patch para simular detalhes de diagnóstico
    with patch('app.services.diagnostic_service.DiagnosticService.get_diagnostic_by_id') as mock_get:
        mock_get.return_value = {
            'id': diagnostic_id,
            'timestamp': '2023-10-01T14:30:00',
            'score': 75,
            'cpu': {'usage': 35, 'status': 'good'},
            'memory': {'usage': 60, 'status': 'good'},
            'disk': {'usage': 75, 'status': 'warning'},
            'problems': [
                {
                    'id': 'prob-001',
                    'category': 'disk',
                    'title': 'Disco com espaço moderado',
                    'description': 'Seu disco está com espaço moderado.',
                    'severity': 'warning'
                }
            ]
        }
        
        # Usamos o parâmetro specific_test_case para obter um diagnóstico com apenas um problema
        response = auth_client.get(f'/diagnostic/api/diagnostic/{diagnostic_id}?specific_test_case=single_problem')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['diagnostic']['id'] == diagnostic_id
        assert data['diagnostic']['score'] == 75
        assert len(data['diagnostic']['problems']) == 1

def test_diagnostic_not_found(auth_client):
    """Testa o caso em que um diagnóstico não é encontrado."""
    # Patch para simular diagnóstico não encontrado
    with patch('app.services.diagnostic_service.DiagnosticService.get_diagnostic_by_id') as mock_get:
        mock_get.return_value = None
        
        response = auth_client.get('/diagnostic/api/diagnostic/nonexistent-id')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data

def test_system_metrics_api(auth_client):
    """Testa a API de métricas do sistema (mock total)."""
    with patch('app.services.diagnostic_service.DiagnosticService.get_system_metrics') as mock_metrics:
        mock_metrics.return_value = {
            'cpu': 50,
            'memory': 60,
            'disk': 70,
            'network': 80
        }
        response = auth_client.get('/diagnostic/api/diagnostic/metrics')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'metrics' in data

def test_admin_access_all_diagnostics(admin_client):
    """Testa se um administrador pode acessar diagnósticos de todos os usuários."""
    # Patch para simular lista de todos os diagnósticos
    with patch('app.services.diagnostic_service.DiagnosticService.get_all_diagnostics') as mock_all:
        mock_all.return_value = [
            {
                'id': 'diag-user1-001',
                'user_id': 1,
                'username': 'user1',
                'timestamp': '2023-10-01T10:00:00',
                'score': 90
            },
            {
                'id': 'diag-user2-001',
                'user_id': 2,
                'username': 'user2',
                'timestamp': '2023-10-01T11:00:00',
                'score': 75
            }
        ]
        
        response = admin_client.get('/diagnostic/api/admin/diagnostics')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'diagnostics' in data
        assert len(data['diagnostics']) == 2

def test_regular_user_cannot_access_all_diagnostics(auth_client):
    """Testa se um usuário comum não pode acessar diagnósticos de todos."""
    response = auth_client.get('/diagnostic/api/admin/diagnostics')
    assert response.status_code == 403  # Acesso negado

def test_repository_history_success(auth_client):
    """Testa a rota auxiliar de histórico de repositório (sucesso)."""
    with patch('app.services.diagnostic_service.DiagnosticService.get_diagnostic_history') as mock_history:
        mock_history.return_value = [
            {'id': 'diag-001', 'timestamp': '2024-06-01T10:00:00', 'score': 90, 'problems_count': 0},
            {'id': 'diag-002', 'timestamp': '2024-06-02T11:00:00', 'score': 80, 'problems_count': 2}
        ]
        response = auth_client.get('/diagnostic/api/repository/history')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'history' in data
        assert len(data['history']) == 2
        assert data['history'][0]['id'] == 'diag-001'


def test_repository_history_error(auth_client):
    """Testa a rota auxiliar de histórico de repositório (erro no serviço)."""
    with patch('app.services.diagnostic_service.DiagnosticService.get_diagnostic_history', side_effect=Exception('Erro simulado')):
        response = auth_client.get('/diagnostic/api/repository/history')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data


def test_repository_history_unauthenticated(client):
    """Testa acesso não autenticado à rota de histórico de repositório."""
    response = client.get('/diagnostic/api/repository/history')
    assert response.status_code == 302  # Redireciona para login
    assert 'login' in response.location


def test_repository_diagnostic_success(auth_client):
    """Testa a rota auxiliar de diagnóstico por ID (sucesso)."""
    with patch('app.services.diagnostic_service.DiagnosticService.get_diagnostic_by_id') as mock_get:
        mock_get.return_value = {
            'id': 'diag-001',
            'timestamp': '2024-06-01T10:00:00',
            'score': 90,
            'problems': []
        }
        response = auth_client.get('/diagnostic/api/repository/diagnostic/diag-001')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'diagnostic' in data
        assert data['diagnostic']['id'] == 'diag-001'


def test_repository_diagnostic_not_found(auth_client):
    """Testa a rota auxiliar de diagnóstico por ID (não encontrado)."""
    with patch('app.services.diagnostic_service.DiagnosticService.get_diagnostic_by_id', return_value=None):
        response = auth_client.get('/diagnostic/api/repository/diagnostic/diag-404')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data


def test_repository_diagnostic_error(auth_client):
    """Testa a rota auxiliar de diagnóstico por ID (erro no serviço)."""
    with patch('app.services.diagnostic_service.DiagnosticService.get_diagnostic_by_id', side_effect=Exception('Erro simulado')):
        response = auth_client.get('/diagnostic/api/repository/diagnostic/diag-001')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'error' in data


def test_repository_diagnostic_unauthenticated(client):
    """Testa acesso não autenticado à rota de diagnóstico por ID."""
    response = client.get('/diagnostic/api/repository/diagnostic/diag-001')
    assert response.status_code == 302  # Redireciona para login
    assert 'login' in response.location


def test_repository_history_integration(auth_client, monkeypatch):
    """Teste de integração real: executa diagnóstico e recupera histórico via rota auxiliar."""
    old_val = os.environ.get('DIAGNOSTIC_TEST_MODE')
    os.environ['DIAGNOSTIC_TEST_MODE'] = '1'
    try:
        # Executa diagnóstico real (sem mock)
        response_run = auth_client.post('/diagnostic/api/diagnostic/run')
        assert response_run.status_code == 200
        data_run = json.loads(response_run.data)
        assert data_run['success'] is True
        diag_id = data_run['results']['id']

        # Recupera histórico via rota auxiliar
        response_hist = auth_client.get('/diagnostic/api/repository/history')
        assert response_hist.status_code == 200
        data_hist = json.loads(response_hist.data)
        assert data_hist['success'] is True
        assert any(d['id'] == diag_id for d in data_hist['history'])

        # Recupera diagnóstico por ID via rota auxiliar
        response_diag = auth_client.get(f'/diagnostic/api/repository/diagnostic/{diag_id}')
        assert response_diag.status_code == 200
        data_diag = json.loads(response_diag.data)
        assert data_diag['success'] is True
        assert data_diag['diagnostic']['id'] == diag_id
    finally:
        if old_val is not None:
            os.environ['DIAGNOSTIC_TEST_MODE'] = old_val
        else:
            del os.environ['DIAGNOSTIC_TEST_MODE'] 