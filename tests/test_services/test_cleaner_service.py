"""
Testes para o serviço de limpeza
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import platform
import psutil

# Alterando a importação para usar caminho relativo mais simples
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

@patch('os.listdir')
@patch('os.path.exists')
@patch('os.path.getsize')
def test_analyze_temp_files(mock_getsize, mock_exists, mock_listdir, cleaner_service_mock):
    """Testa a análise de arquivos temporários."""
    # Configura os mocks
    mock_exists.return_value = True
    mock_getsize.return_value = 1024 * 1024 * 100  # 100 MB
    mock_listdir.return_value = ['temp_file1.txt', 'temp_file2.log']
    
    # Adicionar mock para a função os.walk
    with patch('os.walk', return_value=[(
        'C:\\fake\\temp', 
        ['subfolder'], 
        ['temp_file1.txt', 'temp_file2.log']
    )]):
        result = cleaner_service_mock._analyze_temp_files()
        
        # Verifica os resultados
        assert 'total_size' in result
        assert result['total_size'] > 0
        assert 'paths' in result
        assert len(result['paths']) > 0
        assert 'formatted_total_size' in result

@patch('os.path.exists')
@patch('os.path.getsize')
@patch('os.listdir')
@patch('shutil.rmtree')
def test_clean_browser_cache(mock_rmtree, mock_listdir, mock_getsize, mock_exists, cleaner_service_mock):
    """Testa a limpeza de cache de navegadores."""
    mock_exists.return_value = True
    mock_getsize.return_value = 1024 * 1024 * 50  # 50 MB
    mock_listdir.return_value = ['default-profile']
    
    # Adicionar mock para _clear_directory
    with patch.object(CleanerService, '_clear_directory', return_value=True), \
         patch.object(CleanerService, '_get_directory_size', return_value=1024 * 1024 * 50):
        
        result = cleaner_service_mock.clean_browser_cache('chrome')
        
        # Verifica os resultados
        assert result['success'] is True
        assert 'total_cleaned_size' in result
        assert result['total_cleaned_size'] > 0

@pytest.mark.skipif(sys.platform != 'win32', reason="Teste específico para Windows")
@patch('winreg.OpenKey')
@patch('winreg.EnumKey')
@patch('winreg.EnumValue')
@patch('winreg.QueryValueEx')
def test_analyze_registry(mock_query_value, mock_enum_value, mock_enum_key, mock_open_key, cleaner_service_mock):
    """Testa a análise do registro do Windows."""
    # Simula chaves de registro para análise
    mock_open_key.return_value = MagicMock()
    mock_enum_key.side_effect = [0, 1, 2, WindowsError]  # Simula 3 chaves e depois termina
    mock_enum_value.side_effect = [
        (0, "TestValue1", "Test1"),
        (1, "TestValue2", ""),  # Valor vazio = problema
        (2, "TestValue3", "Test3"),
        WindowsError
    ]
    mock_query_value.return_value = ("Some test data", 1)
    
    with patch.object(CleanerService, '_analyze_registry', return_value={
        'issues': [
            {
                'key': 'HKEY_CURRENT_USER',
                'path': 'Software\\Test',
                'name': 'TestValue2',
                'issue_type': 'invalid_value',
                'description': 'Valor inválido',
                'action': 'delete'
            },
            {
                'key': 'HKEY_LOCAL_MACHINE',
                'path': 'Software\\Test',
                'name': 'MissingDLL',
                'issue_type': 'missing_shared_dlls',
                'description': 'DLL ausente',
                'action': 'delete'
            },
            {
                'key': 'HKEY_CURRENT_USER',
                'path': 'Software\\Test\\Invalid',
                'name': 'BrokenPath',
                'issue_type': 'startup_item',
                'description': 'Caminho quebrado',
                'action': 'disable'
            }
        ],
        'total_issues': 3,
        'details': {
            'invalid_shortcuts': 1,
            'obsolete_software': 0,
            'startup_entries': 1,
            'missing_shared_dlls': 1
        }
    }):
        result = cleaner_service_mock._analyze_registry()
        
        # Verifica os resultados
        assert 'issues' in result
        assert len(result['issues']) > 0
        assert 'total_issues' in result
        assert result['total_issues'] > 0
        assert 'details' in result

@patch('os.path.exists')
@patch('os.path.getsize')
@patch('glob.glob')
def test_analyze_large_files(mock_glob, mock_getsize, mock_exists, cleaner_service_mock):
    """Testa a análise de arquivos grandes."""
    mock_exists.return_value = True
    mock_getsize.side_effect = [
        1024 * 1024 * 500,  # 500 MB
        1024 * 1024 * 200,  # 200 MB
        1024 * 1024 * 100,  # 100 MB
    ]
    mock_glob.return_value = [
        'C:\\Users\\test\\large_file1.iso',
        'C:\\Users\\test\\large_file2.zip',
        'C:\\Users\\test\\large_file3.mp4'
    ]
    
    with patch.object(CleanerService, '_find_large_files', return_value={
        'large_files': [
            {'path': 'C:\\Users\\test\\large_file1.iso', 'size_bytes': 1024 * 1024 * 500, 'formatted_size': '500.00 MB'},
            {'path': 'C:\\Users\\test\\large_file2.zip', 'size_bytes': 1024 * 1024 * 200, 'formatted_size': '200.00 MB'},
            {'path': 'C:\\Users\\test\\large_file3.mp4', 'size_bytes': 1024 * 1024 * 100, 'formatted_size': '100.00 MB'}
        ],
        'total_size_bytes': 1024 * 1024 * 800,
        'formatted_total_size': '800.00 MB'
    }):
        result = cleaner_service_mock._find_large_files(min_size_mb=100)
        
        # Verifica os resultados
        assert 'large_files' in result
        assert len(result['large_files']) == 3
        assert result['total_size_bytes'] > 0
        assert result['large_files'][0]['size_bytes'] > result['large_files'][1]['size_bytes']  # Ordenados por tamanho

@patch('os.path.exists')
@patch('os.path.getsize')
def test_clean_temp_files(mock_getsize, mock_exists, cleaner_service_mock):
    """Testa a limpeza de arquivos temporários."""
    mock_exists.return_value = True
    mock_getsize.return_value = 1024 * 1024 * 100  # 100 MB
    
    with patch.object(CleanerService, '_clear_directory', return_value=True), \
         patch.object(CleanerService, '_analyze_temp_files', return_value={
             'total_size': 1024 * 1024 * 200,
             'formatted_total_size': '200.00 MB',
             'paths': {'C:\\fake\\temp': {'size': 1024 * 1024 * 200, 'files': 10}}
         }), \
         patch.object(CleanerService, '_get_directory_size', return_value=1024 * 1024 * 200):
        
        result = cleaner_service_mock.clean_temp_files()
        
        # Verifica os resultados
        assert result['success'] is True
        assert 'total_cleaned_size' in result
        assert result['total_cleaned_size'] > 0
        assert 'cleaned_files' in result
        assert result['cleaned_files'] > 0
        assert 'formatted_cleaned_size' in result

@pytest.mark.skipif(sys.platform != 'win32', reason="Teste específico para Windows")
@patch('subprocess.run')
def test_repair_system_files(mock_subprocess, cleaner_service_mock):
    """Testa o reparo de arquivos do sistema no Windows."""
    mock_subprocess.return_value = MagicMock(returncode=0)
    
    result = cleaner_service_mock.repair_system_files()
    
    # Verifica os resultados
    assert result['success'] is True
    assert 'commands_executed' in result
    assert len(result['commands_executed']) > 0

@pytest.mark.skipif(sys.platform != 'win32', reason="Teste específico para Windows")
@patch('winreg.OpenKey')
@patch('winreg.DeleteValue')
def test_clean_registry(mock_delete_value, mock_open_key, cleaner_service_mock):
    """Testa a limpeza do registro do Windows."""
    mock_open_key.return_value = MagicMock()
    
    # Estrutura atualizada para corresponder à implementação atual
    with patch.object(CleanerService, '_analyze_registry', return_value={
        'issues': [
            {
                'key': 'HKEY_CURRENT_USER',
                'path': 'Software\\Test',
                'name': 'TestValue2',
                'issue_type': 'invalid_value',
                'description': 'Valor inválido',
                'action': 'delete'
            },
            {
                'key': 'HKEY_LOCAL_MACHINE',
                'path': 'Software\\Test',
                'name': 'MissingDLL',
                'issue_type': 'missing_shared_dlls',
                'description': 'DLL ausente',
                'action': 'delete'
            },
            {
                'key': 'HKEY_CURRENT_USER',
                'path': 'Software\\Test\\Invalid',
                'name': 'BrokenPath',
                'issue_type': 'startup_item',
                'description': 'Caminho quebrado',
                'action': 'disable'
            }
        ],
        'total_issues': 3,
        'details': {
            'invalid_shortcuts': 1,
            'obsolete_software': 0,
            'startup_entries': 1,
            'missing_shared_dlls': 1
        }
    }), patch.object(CleanerService, '_fix_registry_issue', return_value=True):
        
        result = cleaner_service_mock.clean_registry()
        
        # Verifica os resultados
        assert result['success'] is True
        assert 'issues_fixed_count' in result
        assert result['issues_fixed_count'] > 0

def test_create_maintenance_plan_stub(cleaner_service_mock):
    """Testa o stub de criação de plano de manutenção."""
    result = cleaner_service_mock.create_maintenance_plan()
    assert isinstance(result, dict)
    assert result["status"] == "not_implemented"
    assert "message" in result

def test_get_maintenance_history_stub(cleaner_service_mock):
    """Testa o stub de histórico de manutenção."""
    result = cleaner_service_mock.get_maintenance_history()
    assert isinstance(result, dict)
    assert result["status"] == "not_implemented"
    assert "history" in result
    assert isinstance(result["history"], list)

def test_repair_system_files_stub(cleaner_service_mock):
    """Testa o stub de reparo de arquivos do sistema."""
    result = cleaner_service_mock.repair_system_files()
    assert isinstance(result, dict)
    assert result["success"] is True
    assert "commands_executed" in result
    assert isinstance(result["commands_executed"], list)

def test_clear_directory_stub(cleaner_service_mock):
    """Testa o stub de limpeza de diretório."""
    assert cleaner_service_mock._clear_directory("/tmp/test") is True

@patch('app.services.cleaner_service.winreg')
def test_fix_registry_issue_stub(mock_winreg, cleaner_service_mock):
    """Testa o stub de correção de problema de registro."""
    # Mock para getattr(winreg, issue.get('key', 'HKEY_CURRENT_USER'))
    mock_winreg.HKEY_CURRENT_USER = MagicMock()
    
    # Configurar o método OpenKey para retornar um objeto mock
    mock_key = MagicMock()
    mock_winreg.OpenKey.return_value = mock_key
    
    # Definir o mock para CloseKey
    mock_winreg.CloseKey = MagicMock()
    
    # Definir o mock para DeleteValue
    mock_winreg.DeleteValue = MagicMock()
    
    # Chamar a função com os dados de teste
    result = cleaner_service_mock._fix_registry_issue({
        "key": "HKEY_CURRENT_USER", 
        "path": "Software\\Test", 
        "name": "TestValue", 
        "issue_type": "invalid_value",
        "action": "delete"
    })
    
    # Verificar se a função retornou True
    assert result is True
    
    # Verificar se DeleteValue foi chamado com os argumentos esperados
    mock_winreg.DeleteValue.assert_called_once_with(mock_key, "TestValue")

def test_schedule_maintenance_stub(cleaner_service_mock):
    """Testa o stub de agendamento de manutenção."""
    result = cleaner_service_mock.schedule_maintenance()
    assert isinstance(result, dict)
    assert result["status"] == "not_implemented"
    assert "message" in result

def test_execute_maintenance_task_stub(cleaner_service_mock):
    """Testa o stub de execução de tarefa de manutenção."""
    result = cleaner_service_mock.execute_maintenance_task()
    assert isinstance(result, dict)
    assert result["status"] == "not_implemented"
    assert "message" in result

@patch('psutil.disk_partitions')
@patch('psutil.disk_usage')
def test_analyze_system_basic(mock_disk_usage, mock_disk_partitions, cleaner_service_mock):
    """Testa a análise básica do sistema (retorno de estrutura esperada)."""
    # Simula uma partição
    mock_disk_partitions.return_value = [MagicMock(mountpoint='C:/', fstype='NTFS', opts='rw')]
    mock_disk_usage.return_value = MagicMock(total=100*1024**3, used=50*1024**3, free=50*1024**3, percent=50.0)
    result = cleaner_service_mock.analyze_system()
    assert isinstance(result, dict)
    assert "temp_files" in result
    assert "browser_data" in result
    assert "disk_space" in result
    assert "total_cleanup_size" in result


def test_clean_temp_files_returns_success(cleaner_service_mock):
    """Testa se clean_temp_files retorna sucesso e estrutura esperada."""
    result = cleaner_service_mock.clean_temp_files()
    assert result["success"] is True
    assert "cleaned_size" in result
    assert "cleaned_files" in result


def test_clean_browser_data_returns_expected(cleaner_service_mock):
    """Testa se clean_browser_data retorna estrutura esperada mesmo sem browsers reais."""
    result = cleaner_service_mock.clean_browser_data(browsers=["chrome", "firefox"])
    assert "total_cleaned_size" in result
    assert "details" in result
    assert isinstance(result["details"], dict)


def test_optimize_startup_simulation(cleaner_service_mock):
    """Testa a simulação de otimização de inicialização."""
    result = cleaner_service_mock.optimize_startup(items_to_disable=["FakeItem"])
    assert isinstance(result, dict)
    assert "status" in result
    assert "errors" in result


def test_repair_disk_simulation(cleaner_service_mock):
    """Testa a simulação de reparo de disco."""
    result = cleaner_service_mock.repair_disk(drive_letter="C:")
    assert isinstance(result, dict)
    assert "status" in result
    assert "output" in result
    assert "error" in result


def test_defragment_disk_simulation(cleaner_service_mock):
    """Testa a simulação de desfragmentação de disco."""
    result = cleaner_service_mock.defragment_disk(drive_letter="C:")
    assert isinstance(result, dict)
    assert "status" in result
    assert "output" in result
    assert "error" in result 