"""
Testes específicos para a funcionalidade de limpeza de disco
"""
import pytest
from unittest.mock import patch, MagicMock
import platform
from app.services.cleaner_service import CleanerService

@pytest.fixture
def cleaner_service_mock():
    """Fixture que retorna um serviço de limpeza configurado para testes"""
    with patch.object(CleanerService, '_get_temp_paths', return_value=['C:\\fake\\temp']), \
         patch.object(CleanerService, '_get_browser_paths', return_value={
            'chrome': {
                'cache': 'C:\\fake\\path\\chrome\\cache',
                'cookies': 'C:\\fake\\path\\chrome\\cookies',
                'history': 'C:\\fake\\path\\chrome\\history'
            },
            'firefox': {
                'cache': 'C:\\fake\\path\\firefox\\cache',
                'cookies': 'C:\\fake\\path\\firefox\\cookies',
                'history': 'C:\\fake\\path\\firefox\\history'
            }
         }):
        service = CleanerService()
        service.is_windows = True
        return service

def test_get_cleaning_options(cleaner_service_mock):
    """Testa se as opções de limpeza são retornadas corretamente"""
    options = cleaner_service_mock.get_cleaning_options()
    
    # Verifica se retorna uma lista
    assert isinstance(options, list)
    
    # Verifica se contém as opções básicas
    option_ids = [option['id'] for option in options]
    assert 'temp_files' in option_ids
    assert 'browser_cache' in option_ids
    
    # Como configuramos como Windows, deve ter opções específicas do Windows
    assert 'registry' in option_ids
    assert 'system_logs' in option_ids

def test_clean_system(cleaner_service_mock):
    """Testa a funcionalidade de limpeza do sistema"""
    # Mock para clean_temp_files
    with patch.object(CleanerService, 'clean_temp_files', return_value={
            'success': True,
            'total_cleaned_size': 1024 * 1024 * 100,  # 100 MB
            'cleaned_files': 50,
            'formatted_cleaned_size': '100.00 MB'
        }), \
        patch.object(CleanerService, 'clean_browser_data', return_value={
            'total_cleaned_size': 1024 * 1024 * 200,  # 200 MB
            'formatted_total_cleaned_size': '200.00 MB',
            'details': {'chrome': {'status': 'ok'}}
        }), \
        patch.object(CleanerService, 'clean_registry', return_value={
            'success': True,
            'fixed_issues': [],
            'errors': [],
            'issues_fixed_count': 5
        }):
        
        # Testa limpeza com todas as opções
        result = cleaner_service_mock.clean_system(['temp_files', 'browser_cache', 'registry'])
        
        # Verifica o resultado
        assert result['success'] is True
        assert 'total_cleaned' in result
        assert result['total_cleaned'] == 1024 * 1024 * 300  # 100 MB + 200 MB
        assert 'details' in result
        assert 'temp_files' in result['details']
        assert 'browser_cache' in result['details']
        assert 'registry' in result['details']
        
        # Testa limpeza com opções específicas
        result = cleaner_service_mock.clean_system(['temp_files'])
        assert 'temp_files' in result['details']
        assert 'browser_cache' not in result['details']
        assert 'registry' not in result['details']

def test_clean_disk(cleaner_service_mock):
    """Testa a funcionalidade de limpeza de disco"""
    # Mock para clean_system
    with patch.object(CleanerService, 'clean_system', return_value={
            'success': True,
            'total_cleaned': 1024 * 1024 * 300,  # 300 MB
            'formatted_total_cleaned': '300.00 MB',
            'details': {
                'temp_files': {'success': True},
                'browser_cache': {'total_cleaned_size': 1024 * 1024 * 200}
            }
        }):
        
        # Testa limpeza de disco com opções padrão
        result = cleaner_service_mock.clean_disk()
        
        # Verifica o resultado
        assert result['success'] is True
        assert result['formatted_total_cleaned'] == '300.00 MB'
        
        # Testa limpeza com opções específicas
        result = cleaner_service_mock.clean_disk({
            'temp_files': True,
            'browser_cache': False,
            'registry': True
        })
        
        # Verificações adicionais seriam feitas no objeto mock
        assert result['success'] is True 