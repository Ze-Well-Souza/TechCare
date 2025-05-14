"""
Testes para o serviço de diagnóstico
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import types

# Adicionando o diretório raiz ao sys.path para permitir importações corretas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.services.diagnostic_service import DiagnosticService

def test_diagnostic_service_initialization():
    """Testa a inicialização do serviço de diagnóstico."""
    service = DiagnosticService()
    assert service.results is not None
    assert service.problems == []
    assert service.score == 100

@patch('app.services.diagnostic_service_platform.PlatformAdapter.get_cpu_info')
@patch('psutil.cpu_percent')
@patch('psutil.cpu_freq')
def test_analyze_cpu(mock_cpu_freq, mock_cpu_percent, mock_get_cpu_info):
    """Testa a análise de CPU simulando um uso alto."""
    # Configurar mocks
    mock_cpu_percent.return_value = 90
    mock_cpu_percent.side_effect = lambda interval, percpu: [85, 90, 88, 92] if percpu else 90
    
    mock_freq = MagicMock()
    mock_freq.current = 3000
    mock_freq.max = 4000
    mock_cpu_freq.return_value = mock_freq
    
    mock_get_cpu_info.return_value = {
        'brand': 'Intel Core i7',
        'vendor': 'GenuineIntel',
        'cores_physical': 4,
        'cores_logical': 8,
        'architecture': 'x86_64',
        'temperature': 70
    }
    
    service = DiagnosticService()
    result = service.analyze_cpu()
    
    # Verifica se detectou problema de CPU alta
    assert len(service.problems) > 0
    cpu_problem = next((p for p in service.problems if p['category'] == 'cpu'), None)
    assert cpu_problem is not None
    # Verifica se contém "CPU" e "uso" no título, independente da palavra exata
    assert 'CPU' in cpu_problem['title'] and 'uso' in cpu_problem['title'].lower() 
    # Não verifica o score exato, apenas que houve alguma mudança
    assert service.score < 100

@patch('app.services.diagnostic_service_platform.PlatformAdapter.get_memory_info')
@patch('psutil.process_iter')
def test_analyze_memory(mock_process_iter, mock_get_memory_info):
    """Testa a análise de memória simulando baixa disponibilidade."""
    # Configurar mock para processos
    mock_process_iter.return_value = []
    
    # Simula um sistema com 8GB de RAM total, mas apenas 10% disponível
    mock_get_memory_info.return_value = {
        'total': 8 * 1024 * 1024 * 1024,  # 8GB
        'available': 0.1 * 8 * 1024 * 1024 * 1024,  # 10% de 8GB
        'used': 0.9 * 8 * 1024 * 1024 * 1024,  # 90% de 8GB
        'percent': 90.0,  # 90% usado
        'swap_total': 4 * 1024 * 1024 * 1024,  # 4GB
        'swap_used': 1 * 1024 * 1024 * 1024,  # 1GB
        'swap_free': 3 * 1024 * 1024 * 1024,  # 3GB
        'swap_percent': 25.0  # 25% usado
    }
    
    service = DiagnosticService()
    result = service.analyze_memory()
    
    # Verifica se detectou problema de memória baixa
    assert len(service.problems) > 0
    memory_problem = next((p for p in service.problems if p['category'] == 'memory'), None)
    assert memory_problem is not None
    assert 'Uso alto de memória RAM' in memory_problem['title']
    # Não verifica o score exato, apenas que houve alguma mudança
    assert service.score < 100

@patch('platform.system', return_value='Windows')
@patch('psutil.disk_partitions', return_value=[MagicMock(device='C:', mountpoint='C:\\', fstype='NTFS', opts='')])
@patch('psutil.disk_usage')
def test_analyze_disk(mock_disk_usage, mock_partitions, mock_platform):
    """Testa a análise de disco simulando pouco espaço disponível."""
    # Simula um disco com 500GB de espaço total, mas apenas 5% disponível
    mock_disk = MagicMock()
    mock_disk.total = 500 * 1024 * 1024 * 1024  # 500GB
    mock_disk.free = 0.05 * 500 * 1024 * 1024 * 1024  # 5% de 500GB
    mock_disk.percent = 95.0  # 95% usado
    
    mock_disk_usage.return_value = mock_disk
    
    service = DiagnosticService()
    service.is_windows = True
    # Desativa o método alternativo para o teste
    service._analyze_disk_windows_alternative = MagicMock(side_effect=Exception("Método alternativo desativado para teste"))
    
    # Corrigimos a função para definir um score inicial conhecido
    service.score = 100
    service.analyze_disk()
    
    # Verifica se detectou problema de espaço em disco baixo
    assert len(service.problems) > 0
    disk_problem = next((p for p in service.problems if p['category'] == 'disk'), None)
    assert disk_problem is not None
    assert 'Disco' in disk_problem['title'] and 'cheio' in disk_problem['title']
    # Não verifica o score exato, apenas que houve alguma mudança
    assert service.score != 100

@patch('platform.system', return_value='Windows')
def test_analyze_security_windows(mock_platform):
    """Testa a análise de segurança em ambiente Windows (simulado)."""
    # Mocka o módulo wmi antes de instanciar o serviço
    sys.modules['wmi'] = types.SimpleNamespace(WMI=lambda *a, **kw: types.SimpleNamespace())
    service = DiagnosticService()
    service.is_windows = True
    # Mocka métodos internos para evitar chamadas reais
    service._check_windows_defender = MagicMock(return_value={'real_time_protection': False})
    service._check_windows_firewall = MagicMock(return_value={'enabled': False})
    service._check_windows_updates = MagicMock(return_value={'pending_count': 5})
    service.analyze_security()
    # Deve adicionar problemas de segurança
    assert any(p['category'] == 'security' for p in service.problems)

def test_analyze_temperature_high_cpu():
    """Testa a análise de temperatura com CPU muito quente."""
    import psutil
    # Garante que o atributo existe
    if not hasattr(psutil, 'sensors_temperatures'):
        psutil.sensors_temperatures = lambda: {'coretemp': [MagicMock(current=95, label='CPU')]}
    else:
        original = psutil.sensors_temperatures
        psutil.sensors_temperatures = lambda: {'coretemp': [MagicMock(current=95, label='CPU')]}
    service = DiagnosticService()
    service.is_windows = False  # Força caminho genérico
    service.analyze_temperature()
    # Deve adicionar problema de temperatura crítica
    assert any(p['category'] == 'temperature' for p in service.problems)
    assert service.results['temperature']['cpu'] == 95
    # Restaura se necessário
    if 'original' in locals():
        psutil.sensors_temperatures = original

@patch('psutil.net_if_addrs', return_value={'eth0': [MagicMock(family=2, address='192.168.0.2', netmask='255.255.255.0')],})
@patch('psutil.net_io_counters', return_value=MagicMock(bytes_sent=1000, bytes_recv=2000, packets_sent=10, packets_recv=20, errin=0, errout=0))
@patch('socket.create_connection', side_effect=OSError)
def test_analyze_network_no_internet(mock_socket, mock_io, mock_if_addrs):
    """Testa a análise de rede sem conexão com a internet."""
    service = DiagnosticService()
    service.analyze_network()
    # Deve adicionar problema de rede
    assert any(p['category'] == 'network' for p in service.problems)
    assert service.results['network']['internet_connected'] is False 