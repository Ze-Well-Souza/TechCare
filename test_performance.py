#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar o desempenho e consumo de memória do serviço de diagnóstico refatorado.
Compara a implementação original com a nova implementação.
"""

import os
import sys
import time
import platform
import psutil
import gc
import tracemalloc
from typing import Dict, Any, List, Tuple

# Configuração de paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

def print_separator():
    """Imprime uma linha separadora para melhorar a legibilidade"""
    print('-' * 80)

def measure_memory_usage(func, *args, **kwargs) -> Tuple[Dict[str, Any], float, float, List[Tuple[int, int]]]:
    """
    Mede o uso de memória de uma função.
    
    Args:
        func: Função a ser medida
        *args, **kwargs: Argumentos para a função
        
    Returns:
        Tuple com: 
        - resultado da função
        - uso máximo de memória em MB
        - tempo de execução em segundos
        - snapshots de memória durante a execução
    """
    # Força coleta de lixo antes de iniciar
    gc.collect()
    
    # Inicia rastreamento de memória
    tracemalloc.start()
    
    # Captura estado inicial
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss / (1024 * 1024)  # MB
    
    # Lista para armazenar snapshots de memória
    memory_snapshots = []
    
    # Medição de tempo
    start_time = time.time()
    
    # Executa função
    result = func(*args, **kwargs)
    
    # Captura estado final
    peak_memory = tracemalloc.get_traced_memory()[1] / (1024 * 1024)  # MB
    current_memory = process.memory_info().rss / (1024 * 1024)  # MB
    memory_snapshots.append((time.time() - start_time, current_memory))
    
    # Finaliza medição
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Para rastreamento
    tracemalloc.stop()
    
    # Força coleta de lixo após execução
    gc.collect()
    
    return result, peak_memory, execution_time, memory_snapshots

def test_original_diagnostic():
    """
    Testa o serviço de diagnóstico original.
    
    Returns:
        O resultado do diagnóstico e métricas de desempenho
    """
    try:
        from app.services.diagnostic_service import DiagnosticService as OriginalDiagnosticService
        
        service = OriginalDiagnosticService()
        return measure_memory_usage(service.run_diagnostics)
    except ImportError:
        print("AVISO: Serviço de diagnóstico original não encontrado. Pulando...")
        return None, 0, 0, []

def test_new_diagnostic():
    """
    Testa o serviço de diagnóstico refatorado.
    
    Returns:
        O resultado do diagnóstico e métricas de desempenho
    """
    from app.services.diagnostic.diagnostic_service import DiagnosticService
    
    service = DiagnosticService()
    return measure_memory_usage(service.run_diagnostic)

def format_memory(value_mb: float) -> str:
    """Formata um valor de memória em MB com duas casas decimais"""
    return f"{value_mb:.2f} MB"

def format_time(value_seconds: float) -> str:
    """Formata um valor de tempo em segundos com duas casas decimais"""
    return f"{value_seconds:.2f} segundos"

def print_result_summary(result: Dict[str, Any], is_new: bool = False):
    """
    Imprime um resumo do resultado do diagnóstico
    
    Args:
        result: Resultado do diagnóstico
        is_new: Se True, considera o formato da nova API
    """
    print(f"Pontuação de saúde: {result.get('health_score', 'N/A')}")
    
    if is_new:
        components = result.get('components', {})
        problems = result.get('problems', [])
        recommendations = result.get('recommendations', [])
    else:
        components = result.get('components', {})
        problems = []
        for component_result in components.values():
            if 'issues' in component_result:
                for issue in component_result.get('issues', []):
                    problems.append({
                        'description': issue.get('description'),
                        'severity': issue.get('severity')
                    })
        recommendations = result.get('recommendations', [])
    
    print(f"Componentes analisados: {len(components)}")
    print(f"Problemas encontrados: {len(problems)}")
    print(f"Recomendações geradas: {len(recommendations)}")

def compare_results(original_results, new_results):
    """
    Compara os resultados e métricas das duas implementações
    
    Args:
        original_results: Resultado e métricas da implementação original
        new_results: Resultado e métricas da nova implementação
    """
    original_result, original_peak_memory, original_execution_time, original_snapshots = original_results
    new_result, new_peak_memory, new_execution_time, new_snapshots = new_results
    
    print_separator()
    print("COMPARAÇÃO DE RESULTADOS")
    print_separator()
    
    if original_result is None:
        print("Implementação original não disponível para comparação.")
        print_separator()
        
        print("RESULTADO DA NOVA IMPLEMENTAÇÃO")
        print_separator()
        print_result_summary(new_result, True)
        print(f"Pico de memória: {format_memory(new_peak_memory)}")
        print(f"Tempo de execução: {format_time(new_execution_time)}")
        return
    
    # Comparação de métricas
    memory_diff = original_peak_memory - new_peak_memory
    memory_percent = (memory_diff / original_peak_memory) * 100 if original_peak_memory > 0 else 0
    
    time_diff = original_execution_time - new_execution_time
    time_percent = (time_diff / original_execution_time) * 100 if original_execution_time > 0 else 0
    
    print("MÉTRICAS DE DESEMPENHO")
    print_separator()
    print(f"Pico de memória (Original): {format_memory(original_peak_memory)}")
    print(f"Pico de memória (Nova): {format_memory(new_peak_memory)}")
    print(f"Diferença de memória: {format_memory(memory_diff)} ({memory_percent:.2f}%)")
    print()
    print(f"Tempo de execução (Original): {format_time(original_execution_time)}")
    print(f"Tempo de execução (Nova): {format_time(new_execution_time)}")
    print(f"Diferença de tempo: {format_time(time_diff)} ({time_percent:.2f}%)")
    print_separator()
    
    print("RESUMO DOS RESULTADOS")
    print_separator()
    print("Implementação Original:")
    print_result_summary(original_result)
    print()
    print("Nova Implementação:")
    print_result_summary(new_result, True)

def main():
    """Função principal"""
    print_separator()
    print("TESTE DE DESEMPENHO E CONSUMO DE MEMÓRIA - SERVIÇO DE DIAGNÓSTICO")
    print_separator()
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Versão Python: {platform.python_version()}")
    print(f"Memória total: {format_memory(psutil.virtual_memory().total / (1024 * 1024))}")
    print(f"Processador: {platform.processor()}")
    print_separator()
    
    print("Testando implementação original...")
    original_results = test_original_diagnostic()
    
    print("Testando nova implementação...")
    new_results = test_new_diagnostic()
    
    compare_results(original_results, new_results)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 