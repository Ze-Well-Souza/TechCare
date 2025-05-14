"""
Testes para as rotas de reparo
"""
import pytest
import json
from unittest.mock import patch, MagicMock

def test_repair_page_requires_login(client):
    """Testa se a página de reparos requer login"""
    response = client.get('/repair', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_repair_page_access(auth_client):
    """Testa se um usuário logado pode acessar a página de reparos"""
    response = auth_client.get('/repair/')
    assert response.status_code == 200
    assert b'Reparos' in response.data

def test_create_repair_plan_api(auth_client):
    """Testa a API para criar um plano de reparo"""
    diagnostic_id = 'diag-test-001'
    
    with patch('app.services.repair_service.RepairService.create_repair_plan') as mock_create:
        mock_create.return_value = {
            'plan_id': 'plan-test-001',
            'diagnostic_id': diagnostic_id,
            'total_steps': 2,
            'steps': [
                {
                    'id': 'step-001',
                    'problem_id': 'prob-001',
                    'title': 'Liberar memória',
                    'description': 'Fechar programas que consomem muita memória.',
                    'status': 'pending'
                },
                {
                    'id': 'step-002',
                    'problem_id': 'prob-002',
                    'title': 'Limpar arquivos temporários',
                    'description': 'Remover arquivos desnecessários para liberar espaço.',
                    'status': 'pending'
                }
            ]
        }
        
        response = auth_client.post(f'/repair/api/repair/plan/{diagnostic_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['plan']['plan_id'] == 'plan-test-001'
        assert data['plan']['diagnostic_id'] == diagnostic_id
        assert len(data['plan']['steps']) == 2

def test_get_repair_plan_api(auth_client):
    """Testa a API para obter um plano de reparo existente"""
    plan_id = 'plan-test-001'
    
    with patch('app.services.repair_service.RepairService.get_repair_plan') as mock_get:
        mock_get.return_value = {
            'plan_id': plan_id,
            'diagnostic_id': 'diag-test-001',
            'total_steps': 2,
            'steps': [
                {
                    'id': 'step-001',
                    'problem_id': 'prob-001',
                    'title': 'Liberar memória',
                    'description': 'Fechar programas que consomem muita memória.',
                    'status': 'completed'
                },
                {
                    'id': 'step-002',
                    'problem_id': 'prob-002',
                    'title': 'Limpar arquivos temporários',
                    'description': 'Remover arquivos desnecessários para liberar espaço.',
                    'status': 'pending'
                }
            ]
        }
        
        response = auth_client.get(f'/repair/api/repair/plan/{plan_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['plan']['plan_id'] == plan_id
        assert data['plan']['total_steps'] == 2
        assert data['plan']['steps'][0]['status'] == 'completed'
        assert data['plan']['steps'][1]['status'] == 'pending'

def test_execute_repair_step_api(auth_client):
    """Testa a API para executar uma etapa de reparo"""
    plan_id = 'plan-test-001'
    step_id = 'step-002'
    
    with patch('app.services.repair_service.RepairService.execute_repair_step') as mock_execute:
        mock_execute.return_value = {
            'success': True,
            'step_id': step_id,
            'new_status': 'completed',
            'message': 'Reparo executado com sucesso.'
        }
        
        response = auth_client.post(f'/repair/api/repair/execute/{plan_id}/{step_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['result']['step_id'] == step_id
        assert data['result']['new_status'] == 'completed'

def test_get_maintenance_history_api(auth_client):
    """Testa a API para obter o histórico de manutenções"""
    with patch('app.services.cleaner_service.CleanerService.get_maintenance_history') as mock_history:
        mock_history.return_value = [
            {
                'id': 'maint-001',
                'date': '2023-10-15T14:30:00',
                'type': 'disk_cleanup',
                'status': 'completed',
                'details': 'Limpeza de disco concluída'
            },
            {
                'id': 'maint-002',
                'date': '2023-10-20T16:45:00',
                'type': 'startup_optimization',
                'status': 'completed',
                'details': 'Otimização de inicialização concluída'
            }
        ]
        
        response = auth_client.get('/repair/api/maintenance/history')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['history']) == 2
        assert data['history'][0]['id'] == 'maint-001'
        assert data['history'][1]['id'] == 'maint-002'

def test_create_maintenance_plan_api(auth_client):
    """Testa a API para criar um plano de manutenção"""
    with patch('app.services.cleaner_service.CleanerService.create_maintenance_plan') as mock_create:
        mock_create.return_value = {
            'plan_id': 'maint-plan-001',
            'name': 'Plano de Manutenção Teste',
            'description': 'Plano para testes',
            'created_at': '2023-11-01T15:30:00',
            'tasks': [
                {
                    'id': 'task-001',
                    'name': 'Limpeza de Arquivos Temporários',
                    'description': 'Remove arquivos temporários do sistema',
                    'status': 'pending'
                },
                {
                    'id': 'task-002',
                    'name': 'Otimização de Inicialização',
                    'description': 'Otimiza os programas de inicialização',
                    'status': 'pending'
                }
            ]
        }
        
        response = auth_client.post('/repair/api/maintenance/plan', json={
            'name': 'Plano de Manutenção Teste',
            'description': 'Plano para testes',
            'tasks': ['temp_files', 'startup']
        })
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['plan']['name'] == 'Plano de Manutenção Teste'
        assert len(data['plan']['tasks']) == 2 