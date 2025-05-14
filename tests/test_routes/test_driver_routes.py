"""
Testes para as rotas de gerenciamento de drivers
"""
import pytest
import json
from unittest.mock import patch, MagicMock

def test_drivers_page_requires_login(client):
    """Testa se a página de drivers requer login"""
    response = client.get('/drivers', follow_redirects=True)
    assert response.status_code == 200
    assert b'Login' in response.data

def test_drivers_page_access(auth_client):
    """Testa se um usuário logado pode acessar a página de drivers"""
    response = auth_client.get('/drivers/')
    assert response.status_code == 200
    assert b'Drivers' in response.data

def test_scan_drivers_api(auth_client):
    """Testa a API para escanear drivers"""
    with patch('app.services.driver_update_service.DriverUpdateService.scan_drivers') as mock_scan:
        mock_scan.return_value = {
            'total_drivers': 3,
            'outdated_drivers': [
                {
                    'device_id': 'PCI\\VEN_8086&DEV_0046',
                    'name': 'Intel HD Graphics',
                    'version': '10.18.10.3960',
                    'update_available': True,
                    'update_info': {
                        'latest_version': '27.20.100.9030',
                        'download_url': 'https://example.com/driver.exe'
                    }
                }
            ],
            'problematic_drivers': [],
            'up_to_date_drivers': [
                {'device_id': 'DEVICE2', 'name': 'Device 2', 'version': '2.0.0', 'update_available': False},
                {'device_id': 'DEVICE3', 'name': 'Device 3', 'version': '3.0.0', 'update_available': False}
            ]
        }
        
        response = auth_client.get('/drivers/api/drivers/scan')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'results' in data
        assert data['results']['total_drivers'] == 3
        assert len(data['results']['outdated_drivers']) == 1
        assert len(data['results']['up_to_date_drivers']) == 2

def test_download_driver_api(auth_client):
    """Testa a API para download de drivers"""
    driver_id = 'PCI\\VEN_8086&DEV_0046'
    
    with patch('app.services.driver_update_service.DriverUpdateService.download_driver') as mock_download:
        mock_download.return_value = {
            'success': True,
            'file_path': 'C:\\data\\drivers\\intel_graphics_27.20.100.9030.exe',
            'driver_id': driver_id
        }
        
        response = auth_client.post(f'/drivers/api/drivers/download/{driver_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['result']['driver_id'] == driver_id
        assert 'file_path' in data['result']

def test_install_driver_api(auth_client):
    """Testa a API para instalação de drivers"""
    driver_id = 'PCI\\VEN_8086&DEV_0046'
    file_path = 'C:\\data\\drivers\\intel_graphics_27.20.100.9030.exe'
    
    with patch('app.services.driver_update_service.DriverUpdateService.install_driver') as mock_install:
        mock_install.return_value = {
            'success': True,
            'driver_id': driver_id,
            'version': '27.20.100.9030',
            'message': 'Driver instalado com sucesso.'
        }
        
        response = auth_client.post(
            f'/drivers/api/drivers/install/{driver_id}',
            json={'file_path': file_path}
        )
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['result']['driver_id'] == driver_id
        assert data['result']['version'] == '27.20.100.9030'

def test_get_driver_details_api(auth_client):
    """Testa a API para obter detalhes de um driver"""
    driver_id = 'PCI\\VEN_8086&DEV_0046'
    
    with patch('app.services.driver_update_service.DriverUpdateService.get_driver_details') as mock_details:
        mock_details.return_value = {
            'device_id': driver_id,
            'name': 'Intel HD Graphics',
            'manufacturer': 'Intel Corporation',
            'version': '10.18.10.3960',
            'date': '2022-05-15',
            'update_available': True,
            'update_info': {
                'latest_version': '27.20.100.9030',
                'release_date': '2023-08-20',
                'download_url': 'https://example.com/driver.exe',
                'release_notes': 'Melhoria de desempenho e correções de bugs'
            }
        }
        
        response = auth_client.get(f'/drivers/api/drivers/details/{driver_id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['driver']['device_id'] == driver_id
        assert data['driver']['name'] == 'Intel HD Graphics'
        assert data['driver']['update_available'] is True

def test_driver_update_history_api(auth_client):
    """Testa a API para obter o histórico de atualizações de drivers"""
    with patch('app.services.driver_update_service.DriverUpdateService.get_update_history') as mock_history:
        mock_history.return_value = [
            {
                'driver_id': 'PCI\\VEN_8086&DEV_0046',
                'name': 'Intel HD Graphics',
                'old_version': '10.18.10.3960',
                'new_version': '27.20.100.9030',
                'date': '2023-10-15T14:30:00',
                'status': 'success'
            },
            {
                'driver_id': 'USB\\VID_046D&PID_C52B',
                'name': 'Logitech Webcam',
                'old_version': '12.5.0',
                'new_version': '12.7.0',
                'date': '2023-09-22T10:15:00',
                'status': 'success'
            }
        ]
        
        response = auth_client.get('/drivers/api/drivers/history')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['success'] is True
        assert len(data['history']) == 2
        assert data['history'][0]['driver_id'] == 'PCI\\VEN_8086&DEV_0046'
        assert data['history'][1]['driver_id'] == 'USB\\VID_046D&PID_C52B' 