"""
Testes para o serviço de reparo
"""
import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import json

# Adicionando o diretório raiz ao sys.path para permitir importações corretas
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from app.services.repair_service import RepairService

def test_repair_service_initialization():
    """Testa a inicialização do serviço de reparo."""
    service = RepairService()
    assert service is not None
    assert hasattr(service, 'generate_repair_plan')
    assert hasattr(service, 'repair_guides')

def test_get_repair_plan_empty():
    """Testa a geração de um plano de reparo quando não há problemas."""
    service = RepairService()
    problems = []
    
    plan = service.generate_repair_plan(problems)
    
    assert plan is not None
    assert 'problems_count' in plan
    assert plan['problems_count'] == 0
    assert 'repair_steps' in plan
    assert len(plan['repair_steps']) == 0

def test_get_repair_plan_with_problems():
    """Testa a geração de um plano de reparo com problemas detectados."""
    service = RepairService()
    problems = [
        {
            'id': 'cpu-001',
            'category': 'cpu',
            'title': 'Alto uso de CPU',
            'description': 'O processador está com uso muito elevado',
            'severity': 'medium'
        },
        {
            'id': 'memory-001',
            'category': 'memory',
            'title': 'Pouca memória disponível',
            'description': 'O sistema está com pouca memória RAM disponível',
            'severity': 'high'
        }
    ]
    
    plan = service.generate_repair_plan(problems)
    
    assert plan is not None
    assert 'problems_count' in plan
    assert plan['problems_count'] == 2
    assert 'repair_steps' in plan
    assert len(plan['repair_steps']) > 0
    
    # Verifica se os passos têm a estrutura correta
    for step in plan['repair_steps']:
        assert 'problem' in step
        assert 'guide' in step

def test_find_repair_guide():
    """Testa a busca de um guia de reparo específico."""
    service = RepairService()
    
    # Verifica um guia para um problema de CPU
    guide = service._find_repair_guide('cpu', 'Alto uso de CPU')
    assert guide is not None
    assert 'title' in guide
    assert 'steps' in guide
    
    # Verifica um guia para um problema desconhecido
    guide = service._find_repair_guide('unknown', 'Problema desconhecido')
    assert guide is None

def test_cpu_repair_guides():
    """Testa os guias de reparo para CPU."""
    service = RepairService()
    guides = service._get_cpu_repair_guides()
    
    assert isinstance(guides, list)
    assert len(guides) > 0
    
    # Verifica a estrutura de cada guia
    for guide_info in guides:
        assert 'problem_pattern' in guide_info
        assert 'title' in guide_info
        assert 'steps' in guide_info
        assert isinstance(guide_info['steps'], list) 