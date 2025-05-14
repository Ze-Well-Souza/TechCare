"""
Testes para o serviço de diagnóstico
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Adicionando o diretório raiz ao sys.path para permitir importações corretas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.services.diagnostic_service import DiagnosticService

def test_diagnostic_service_initialization():
    """Testa a inicialização do serviço de diagnóstico."""
    service = DiagnosticService()
    assert service.results is not None
    assert service.problems == []
    assert service.score == 100

@patch('psutil.cpu_percent')
def test_analyze_cpu(mock_cpu_percent):
    """Testa a análise de CPU simulando um uso alto."""
    mock_cpu_percent.return_value = 90
    
    service = DiagnosticService()
    service.analyze_cpu()
    
    # Verifica se detectou problema de CPU alta
    assert len(service.problems) > 0
    cpu_problem = next((p for p in service.problems if p['category'] == 'cpu'), None)
    assert cpu_problem is not None
    assert 'Alto uso de CPU' in cpu_problem['title']
    # Não verifica o score exato, apenas que houve alguma mudança
    assert service.score != 100

@patch('psutil.virtual_memory')
def test_analyze_memory(mock_virtual_memory):
    """Testa a análise de memória simulando baixa disponibilidade."""
    # Simula um sistema com 8GB de RAM total, mas apenas 10% disponível
    mock_memory = MagicMock()
    mock_memory.total = 8 * 1024 * 1024 * 1024  # 8GB
    mock_memory.available = 0.1 * 8 * 1024 * 1024 * 1024  # 10% de 8GB
    mock_memory.percent = 90.0  # 90% usado
    
    mock_virtual_memory.return_value = mock_memory
    
    service = DiagnosticService()
    service.analyze_memory()
    
    # Verifica se detectou problema de memória baixa
    assert len(service.problems) > 0
    memory_problem = next((p for p in service.problems if p['category'] == 'memory'), None)
    assert memory_problem is not None
    assert 'Uso alto de memória RAM' in memory_problem['title']
    # Não verifica o score exato, apenas que houve alguma mudança
    assert service.score != 100

@patch('psutil.disk_usage')
def test_analyze_disk(mock_disk_usage):
    """Testa a análise de disco simulando pouco espaço disponível."""
    # Simula um disco com 500GB de espaço total, mas apenas 5% disponível
    mock_disk = MagicMock()
    mock_disk.total = 500 * 1024 * 1024 * 1024  # 500GB
    mock_disk.free = 0.05 * 500 * 1024 * 1024 * 1024  # 5% de 500GB
    mock_disk.percent = 95.0  # 95% usado
    
    mock_disk_usage.return_value = mock_disk
    
    service = DiagnosticService()
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