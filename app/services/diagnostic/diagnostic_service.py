#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serviço de diagnóstico do sistema refatorado.
Este serviço é responsável por coordenar a execução dos diversos analisadores
e agregar seus resultados.
"""

import time
import json
import logging
import gc
import datetime
from typing import Dict, Any, List, Optional, Union, Type, Tuple
import importlib
import traceback

# Evitar o conflito de importação
# from datetime import datetime

# Importações sob demanda (lazy imports)
# Estas classes serão carregadas apenas quando necessárias
_cpu_analyzer = None
_memory_analyzer = None
_disk_analyzer = None
_network_analyzer = None
_startup_analyzer = None
_security_analyzer = None
_driver_analyzer = None

# Importações de utilitários
from app.utils.cache import cache_result
from app.services.diagnostic.utils.platform_utils import is_windows, is_linux, is_macos

# Inicialização do logger
logger = logging.getLogger(__name__)

class DiagnosticService:
    """
    Serviço principal de diagnóstico que orquestra os diferentes analisadores.
    Implementa Lazy Loading para economizar memória.
    """
    
    def __init__(self, repository=None):
        """
        Inicializa o serviço de diagnóstico.
        
        Args:
            repository: Repositório de diagnóstico para persistência (carregado sob demanda)
        """
        self._repository = repository
        self._repository_module = None
        self._recommendation_generator = None
        self._analyzers = {}
        
    def _get_repository(self):
        """
        Obtém o repositório de diagnóstico (lazy loading).
        
        Returns:
            Instância do repositório de diagnóstico
        """
        if self._repository is None:
            try:
                if self._repository_module is None:
                    from app.services.diagnostic.repositories.diagnostic_repository import DiagnosticRepository
                    self._repository_module = DiagnosticRepository
                self._repository = self._repository_module()
                logger.debug("Repositório de diagnóstico carregado com sucesso")
            except Exception as e:
                logger.error(f"Erro ao carregar repositório de diagnóstico: {str(e)}")
                # Fallback para repositório original se o novo falhar
                try:
                    from app.services.diagnostic_repository import DiagnosticRepository as OriginalRepository
                    self._repository = OriginalRepository()
                    logger.warning("Usando repositório de diagnóstico legado como fallback")
                except Exception:
                    logger.error("Não foi possível carregar nenhum repositório de diagnóstico", exc_info=True)
        
        return self._repository
    
    def _get_analyzer(self, analyzer_type: str) -> Any:
        """
        Obtém um analisador pelo tipo usando lazy loading.
        
        Args:
            analyzer_type: Tipo de analisador (cpu, memory, disk, network, startup, etc.)
            
        Returns:
            Instância do analisador ou None se não encontrado
        """
        if analyzer_type not in self._analyzers:
            try:
                if analyzer_type == 'cpu':
                    from app.services.diagnostic.analyzers import CPUAnalyzer
                    self._analyzers[analyzer_type] = CPUAnalyzer()
                elif analyzer_type == 'memory':
                    from app.services.diagnostic.analyzers import MemoryAnalyzer
                    self._analyzers[analyzer_type] = MemoryAnalyzer()
                elif analyzer_type == 'disk':
                    from app.services.diagnostic.analyzers import DiskAnalyzer
                    self._analyzers[analyzer_type] = DiskAnalyzer()
                elif analyzer_type == 'network':
                    from app.services.diagnostic.analyzers import NetworkAnalyzer
                    self._analyzers[analyzer_type] = NetworkAnalyzer()
                elif analyzer_type == 'startup':
                    from app.services.diagnostic.analyzers import StartupAnalyzer
                    self._analyzers[analyzer_type] = StartupAnalyzer()
                elif analyzer_type == 'security':
                    from app.services.diagnostic.analyzers import SecurityAnalyzer
                    self._analyzers[analyzer_type] = SecurityAnalyzer()
                elif analyzer_type == 'driver':
                    from app.services.diagnostic.analyzers import DriverAnalyzer
                    self._analyzers[analyzer_type] = DriverAnalyzer()
                else:
                    logger.warning(f"Analisador desconhecido: {analyzer_type}")
                    return None
            except Exception as e:
                logger.error(f"Erro ao carregar analisador {analyzer_type}: {str(e)}", exc_info=True)
                return None
                
        return self._analyzers.get(analyzer_type)
    
    def run_diagnostic(self) -> Dict[str, Any]:
        """
        Executa o diagnóstico completo do sistema.
        
        Returns:
            Dict[str, Any]: Resultado do diagnóstico
        """
        logger.info("Iniciando diagnóstico completo do sistema")
        
        try:
            start_time = time.time()
            
            # Inicializa componentes básicos do diagnóstico
            result = {
                'timestamp': datetime.datetime.now().isoformat(),
                'system_info': self._get_system_info(),
                'components': {},
                'problems': [],
                'recommendations': [],
                'health_score': 0
            }
            
            # Lista de análises a serem executadas
            analyzers = ['cpu', 'memory', 'disk', 'network', 'startup', 'security', 'driver']
            
            # Executa cada análise
            for analyzer_type in analyzers:
                try:
                    analyzer_start = time.time()
                    analyzer_result = self._run_analyzer(analyzer_type)
                    analyzer_end = time.time()
                    
                    if analyzer_result:
                        logger.info(f"Análise de {analyzer_type} concluída em {analyzer_end - analyzer_start:.2f}s")
                        result['components'][analyzer_type] = analyzer_result
                        
                        # Adiciona problemas do analisador à lista principal
                        if 'problems' in analyzer_result:
                            result['problems'].extend(analyzer_result['problems'])
                except Exception as e:
                    logger.error(f"Erro durante análise de {analyzer_type}: {str(e)}", exc_info=True)
            
            # Calcula pontuação geral
            result['health_score'] = self._calculate_health_score(result['problems'])
            
            # Gera recomendações baseadas nos problemas
            result['recommendations'] = self.generate_recommendations(result['problems'])
            
            # Registra duração
            duration = time.time() - start_time
            result['duration'] = round(duration, 2)
            
            logger.info(f"Diagnóstico concluído em {duration:.2f}s com pontuação {result['health_score']}")
            
            # Salva resultado no banco de dados
            try:
                repository = self._get_repository()
                if repository:
                    diagnostic_id = repository.save_diagnostic(result)
                    result['diagnostic_id'] = diagnostic_id
                    logger.info(f"Diagnóstico salvo com ID: {diagnostic_id}")
            except Exception as e:
                logger.error(f"Erro ao salvar diagnóstico: {str(e)}", exc_info=True)
            
            return result
            
        except Exception as e:
            logger.error(f"Erro durante execução do diagnóstico: {str(e)}", exc_info=True)
            return {
                'error': f"Erro durante execução do diagnóstico: {str(e)}",
                'timestamp': datetime.datetime.now(),
                'duration': time.time() - start_time,
                'health_score': 0,
                'components': {},
                'problems': [{
                    'description': f'Erro crítico no diagnóstico: {str(e)}',
                    'recommendation': 'Verifique os logs para mais detalhes',
                    'severity': 'high'
                }],
                'recommendations': ['Verificar logs do sistema para identificar a causa do erro']
            }
    
    def get_latest_diagnostic(self) -> Optional[Dict[str, Any]]:
        """
        Obtém o diagnóstico mais recente.
        
        Returns:
            Dict[str, Any] ou None: O diagnóstico mais recente ou None se não houver diagnósticos.
        """
        try:
            repository = self._get_repository()
            if repository:
                return repository.get_latest_diagnostic()
            return None
        except Exception as e:
            logger.error(f"Erro ao obter diagnóstico mais recente: {str(e)}", exc_info=True)
            return None
    
    def get_diagnostic_by_id(self, diagnostic_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtém um diagnóstico pelo ID.
        
        Args:
            diagnostic_id: ID do diagnóstico
            
        Returns:
            Dict[str, Any] ou None: O diagnóstico ou None se não for encontrado.
        """
        try:
            repository = self._get_repository()
            if repository:
                return repository.get_diagnostic_by_id(diagnostic_id)
            return None
        except Exception as e:
            logger.error(f"Erro ao obter diagnóstico por ID {diagnostic_id}: {str(e)}", exc_info=True)
            return None
    
    def get_all_diagnostics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Obtém todos os diagnósticos, limitados pelo parâmetro.
        
        Args:
            limit: Número máximo de diagnósticos a retornar
            
        Returns:
            List[Dict[str, Any]]: Lista de diagnósticos
        """
        try:
            repository = self._get_repository()
            if repository:
                return repository.get_all_diagnostics(limit)
            return []
        except Exception as e:
            logger.error(f"Erro ao obter todos os diagnósticos: {str(e)}", exc_info=True)
            return []
    
    def generate_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Gera recomendações baseadas nos problemas encontrados.
        
        Args:
            issues: Lista de problemas encontrados no diagnóstico
            
        Returns:
            List[str]: Lista de recomendações
        """
        try:
            # Carrega gerador de recomendações sob demanda
            if self._recommendation_generator is None:
                try:
                    from app.services.diagnostic.reporters.recommendations import RecommendationGenerator
                    self._recommendation_generator = RecommendationGenerator()
                except ImportError:
                    logger.warning("Módulo de recomendações não disponível, usando gerador simples")
                    self._recommendation_generator = SimpleRecommendationGenerator()
            
            return self._recommendation_generator.generate(issues)
        except Exception as e:
            logger.error(f"Erro ao gerar recomendações: {str(e)}", exc_info=True)
            # Fallback para implementação simples em caso de erro
            return self._generate_simple_recommendations(issues)
    
    def _generate_simple_recommendations(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Implementação simplificada de geração de recomendações (fallback).
        
        Args:
            issues: Lista de problemas encontrados
            
        Returns:
            List[str]: Lista de recomendações
        """
        recommendations = []
        
        for issue in issues:
            if 'recommendation' in issue:
                recommendations.append(issue['recommendation'])
        
        return list(set(recommendations))  # Remove duplicatas

    def _run_analyzer(self, analyzer_type: str) -> Dict[str, Any]:
        """
        Executa um analisador específico.
        
        Args:
            analyzer_type: Tipo de analisador a ser executado
            
        Returns:
            Dict[str, Any]: Resultado da análise ou None se falhar
        """
        logger.info(f"Executando analisador: {analyzer_type}")
        
        try:
            analyzer = self._get_analyzer(analyzer_type)
            if analyzer:
                return analyzer.analyze()
            else:
                logger.warning(f"Analisador não disponível: {analyzer_type}")
                return None
        except Exception as e:
            logger.error(f"Erro ao executar analisador {analyzer_type}: {str(e)}", exc_info=True)
            return None
            
    def _calculate_health_score(self, problems: List[Dict[str, Any]]) -> int:
        """
        Calcula pontuação de saúde com base nos problemas encontrados.
        
        Args:
            problems: Lista de problemas encontrados
            
        Returns:
            int: Pontuação de saúde (0-100)
        """
        # Base: pontuação perfeita
        score = 100
        
        # Reduz pontuação com base na severidade dos problemas
        for problem in problems:
            severity = problem.get('severity', 'low').lower()
            
            if severity == 'critical':
                score -= 15
            elif severity == 'high':
                score -= 10
            elif severity == 'medium':
                score -= 5
            elif severity == 'low':
                score -= 2
        
        # Garante que a pontuação fique no intervalo 0-100
        return max(0, min(100, score))
        
    def _get_system_info(self) -> Dict[str, Any]:
        """
        Obtém informações básicas do sistema.
        
        Returns:
            Dict[str, Any]: Informações do sistema
        """
        try:
            import platform
            import psutil
            import socket
            import os
            
            # Informações básicas
            system_info = {
                'hostname': socket.gethostname(),
                'platform': platform.system(),
                'platform_release': platform.release(),
                'platform_version': platform.version(),
                'architecture': platform.machine(),
                'processor': platform.processor(),
                'cpu_cores': psutil.cpu_count(logical=False),
                'cpu_threads': psutil.cpu_count(logical=True),
                'memory_total': round(psutil.virtual_memory().total / (1024**3), 2),  # GB
                'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()).isoformat()
            }
            
            # Adiciona nome do usuário se disponível
            try:
                system_info['username'] = os.getlogin()
            except:
                pass
            
            return system_info
        except Exception as e:
            logger.error(f"Erro ao obter informações do sistema: {str(e)}", exc_info=True)
            return {
                'error': f"Erro ao obter informações do sistema: {str(e)}"
            }


class SimpleRecommendationGenerator:
    """
    Implementação simples de gerador de recomendações para fallback.
    """
    
    def generate(self, issues: List[Dict[str, Any]]) -> List[str]:
        """
        Gera recomendações baseadas nos problemas encontrados.
        
        Args:
            issues: Lista de problemas encontrados
            
        Returns:
            List[str]: Lista de recomendações
        """
        recommendations = []
        
        for issue in issues:
            if 'recommendation' in issue:
                recommendations.append(issue['recommendation'])
        
        return list(set(recommendations))  # Remove duplicatas 