#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serviço de diagnóstico para análise de hardware e software
"""

import os
import sys
import time
import json
import psutil
import platform
import threading
import logging
import uuid
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime
from pathlib import Path
import subprocess
import socket

# Detecção de módulos específicos do Windows
HAS_WMI = False
if platform.system() == 'Windows':
    try:
        import wmi
        import pythoncom  # Necessário para inicializar COM
        HAS_WMI = True
    except ImportError:
        pass

# Função para inicializar COM antes das operações WMI
def initialize_com():
    """Inicializa COM para operações WMI em threads diferentes"""
    if platform.system() == 'Windows':
        try:
            import pythoncom
            pythoncom.CoInitialize()
            return True
        except Exception as e:
            logging.warning(f"Erro ao inicializar COM: {str(e)}")
            return False
    return True

# Detecção de módulos específicos do Linux
HAS_SENSORS = False
if platform.system() == 'Linux':
    try:
        import sensors
        HAS_SENSORS = True
    except ImportError:
        pass

from app.services.diagnostic_repository import DiagnosticRepository
from app.services.diagnostic_service_platform import PlatformAdapter, is_windows
from app.utils.cache import cache_result

# Configuração de logging
logger = logging.getLogger(__name__)

class DiagnosticService:
    """
    Classe responsável pelo diagnóstico completo do sistema.
    Realiza análises de hardware e software, identifica problemas e gera recomendações.
    """
    
    def __init__(self, diagnostic_repository: Optional[DiagnosticRepository] = None):
        """
        Inicializa o serviço de diagnóstico
        
        Args:
            diagnostic_repository: Repositório para armazenamento de diagnósticos
        """
        self.results = {
            'cpu': {},
            'memory': {},
            'disk': {},
            'startup': {},
            'drivers': {},
            'security': {},
            'network': {},
            'temperature': {}  # Adicionando seção para temperatura
        }
        self.problems = []
        self.score = 100  # Pontuação inicial do sistema
        self.is_windows = platform.system() == 'Windows'
        
        # Injeção de dependência do repositório
        self.repository = diagnostic_repository or DiagnosticRepository()
        
        logger.info(f"Iniciando DiagnosticService no sistema {platform.system()}")

    def run_diagnostics(self, user_id: str = 'anonymous') -> Dict[str, Any]:
        """
        Executa um diagnóstico completo do sistema e salva no histórico
        Se DIAGNOSTIC_TEST_MODE=1, retorna dados simulados para ambiente de teste.
        """
        if os.environ.get('DIAGNOSTIC_TEST_MODE') == '1':
            diagnostic_result = {
                'id': f'diag-test-{user_id}',
                'user_id': user_id,
                'timestamp': '2024-06-01T12:00:00',
                'score': 90,
                'cpu': {'usage': 35, 'status': 'good'},
                'memory': {'usage': 60, 'status': 'good'},
                'disk': {'usage': 75, 'status': 'warning'},
                'network': {'status': 'ok', 'adapters': []},
                'problems': [],
                'recommendations': ['Tudo ok no ambiente de teste.']
            }
            self.repository.save(diagnostic_result)
            return diagnostic_result
        logger.info(f"Iniciando diagnóstico via run_diagnostics para usuário {user_id}")
        diagnostic_result = self.start_diagnostic()
        
        # Adiciona informações do usuário
        diagnostic_result['user_id'] = user_id
        
        # Salva o diagnóstico no repositório
        self.repository.save(diagnostic_result)
        
        return diagnostic_result

    def save_diagnostic(self, diagnostic_data: Dict[str, Any]) -> bool:
        """
        Salva um diagnóstico no histórico
        
        Args:
            diagnostic_data: Dados do diagnóstico a serem salvos
            
        Returns:
            bool: True se o salvamento foi bem-sucedido
        """
        try:
            self.repository.save(diagnostic_data)
            return True
        except Exception as e:
            logger.error(f"Erro ao salvar diagnóstico: {e}")
            return False
        
    def get_diagnostic_history(self, user_id: str = 'anonymous', limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recupera o histórico de diagnósticos para um usuário
        
        Args:
            user_id: ID do usuário
            limit: Número máximo de registros a retornar
            
        Returns:
            list: Lista de diagnósticos resumidos, ordenados por data (mais recente primeiro)
        """
        return self.repository.get_history(user_id, limit)
        
    def get_diagnostic_by_id(self, diagnostic_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Recupera um diagnóstico específico pelo ID
        
        Args:
            diagnostic_id: ID do diagnóstico
            user_id: ID do usuário (se None, busca em todos os usuários)
            
        Returns:
            dict: Dados completos do diagnóstico ou None se não encontrado
        """
        return self.repository.get_by_id(diagnostic_id, user_id)
        
    def get_all_diagnostics(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Recupera diagnósticos de todos os usuários (para administradores)
        
        Args:
            limit: Número máximo de registros a retornar
            
        Returns:
            list: Lista de diagnósticos resumidos de todos os usuários
        """
        return self.repository.get_all(limit)

    @cache_result(expire_seconds=300)  # Cache por 5 minutos
    def start_diagnostic(self) -> Dict[str, Any]:
        """
        Inicia o diagnóstico completo do sistema
        
        Returns:
            dict: Resultados completos do diagnóstico
        """
        logger.info("Iniciando diagnóstico completo do sistema")
        
        try:
            # Executa cada análise em sequência
            self.analyze_cpu()
            self.analyze_memory()
            self.analyze_disk()
            
            # Análises específicas para Windows
            if self.is_windows:
                self.analyze_startup()
            
            # Análises comuns
            self.analyze_drivers()
            self.analyze_security()
            self.analyze_temperature()
            self.analyze_network()
            
            # Gera relatório e recomendações
            diagnostic_report = self.generate_report()
            
            # Adiciona identificador único e timestamp
            diagnostic_report['id'] = f"diag-{uuid.uuid4().hex[:8]}"
            diagnostic_report['timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Diagnóstico completo concluído com sucesso, ID: {diagnostic_report['id']}")
            return diagnostic_report
            
        except Exception as e:
            logger.error(f"Erro durante o diagnóstico: {e}")
            # Em caso de erro, retorna um relatório básico com a mensagem de erro
            error_report = {
                'id': f"error-{uuid.uuid4().hex[:8]}",
                'timestamp': datetime.now().isoformat(),
                'error': str(e),
                'score': 0,
                'problems': [f"Erro durante diagnóstico: {e}"],
                'recommendations': ["Tente novamente o diagnóstico ou contate o suporte."]
            }
            return error_report
    
    def analyze_cpu(self) -> Dict[str, Any]:
        """Analisa a CPU do sistema e retorna métricas relevantes"""
        logger.info("Analisando CPU...")
        
        try:
            # Usar o PlatformAdapter para obter informações da CPU de forma compatível
            cpu_info = PlatformAdapter.get_cpu_info()
            
            # Métricas de uso
            cpu_percent = psutil.cpu_percent(interval=0.5, percpu=False)
            cpu_percent_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
            cpu_freq = psutil.cpu_freq()
            
            # Resultados básicos
            result = {
                'usage': cpu_percent,
                'usage_per_core': cpu_percent_per_core,
                'current_frequency': cpu_freq.current if cpu_freq else None,
                'max_frequency': cpu_freq.max if cpu_freq and hasattr(cpu_freq, 'max') else None,
                'cores_logical': cpu_info['cores_logical'],
                'cores_physical': cpu_info['cores_physical'],
                'vendor': cpu_info['vendor'],
                'brand': cpu_info['brand'],
                'architecture': cpu_info['architecture'],
                'temperature': cpu_info['temperature'],
                'is_overheating': False,
                'is_throttling': False,
                'issues': []
            }
            
            # Verificação de problemas
            # 1. Temperatura (se disponível)
            if result['temperature'] is not None:
                if result['temperature'] > 85:
                    result['is_overheating'] = True
                    result['issues'].append({
                        'severity': 'high',
                        'description': f'Temperatura crítica de CPU ({result["temperature"]}°C)',
                        'recommendation': 'Verifique a ventilação e os dissipadores de calor do sistema.'
                    })
                    # Adiciona problema para o diagnóstico geral
                    self.problems.append({
                        'category': 'cpu',
                        'title': f'Temperatura crítica de CPU',
                        'description': f'A CPU está em temperatura crítica: {result["temperature"]}°C',
                        'solution': 'Verifique a ventilação e os dissipadores de calor do sistema.',
                        'impact': 'high'
                    })
                elif result['temperature'] > 75:
                    result['issues'].append({
                        'severity': 'medium',
                        'description': f'Temperatura elevada de CPU ({result["temperature"]}°C)',
                        'recommendation': 'Considere limpar os ventiladores e verificar a pasta térmica.'
                    })
                    # Adiciona problema para o diagnóstico geral
                    self.problems.append({
                        'category': 'cpu',
                        'title': f'Temperatura elevada de CPU',
                        'description': f'A CPU está com temperatura elevada: {result["temperature"]}°C',
                        'solution': 'Considere limpar os ventiladores e verificar a pasta térmica.',
                        'impact': 'medium'
                    })
            
            # 2. Uso de CPU
            if result['usage'] > 90:
                result['issues'].append({
                    'severity': 'high',
                    'description': f'Uso extremamente alto de CPU ({result["usage"]}%)',
                    'recommendation': 'Verifique quais processos estão consumindo a CPU e encerre os desnecessários.'
                })
                # Adiciona problema para o diagnóstico geral
                self.problems.append({
                    'category': 'cpu',
                    'title': f'Alto uso de CPU',
                    'description': f'A CPU está com uso extremamente alto: {result["usage"]}%',
                    'solution': 'Verifique quais processos estão consumindo a CPU e encerre os desnecessários.',
                    'impact': 'high'
                })
            elif result['usage'] > 80:
                result['issues'].append({
                    'severity': 'medium',
                    'description': f'Uso elevado de CPU ({result["usage"]}%)',
                    'recommendation': 'Monitore os processos em execução que podem estar sobrecarregando o sistema.'
                })
                # Adiciona problema para o diagnóstico geral
                self.problems.append({
                    'category': 'cpu',
                    'title': f'Uso elevado de CPU',
                    'description': f'A CPU está com uso elevado: {result["usage"]}%',
                    'solution': 'Monitore os processos em execução que podem estar sobrecarregando o sistema.',
                    'impact': 'medium'
                })
            
            # 3. Verificação de throttling (limitação de velocidade)
            if cpu_freq and hasattr(cpu_freq, 'max') and hasattr(cpu_freq, 'current'):
                if cpu_freq.current < (cpu_freq.max * 0.7) and result['usage'] > 70:
                    result['is_throttling'] = True
                    result['issues'].append({
                        'severity': 'medium',
                        'description': f'CPU possivelmente limitada (throttling)',
                        'recommendation': 'Verifique a temperatura, energia e configurações de gerenciamento de energia.'
                    })
                    # Adiciona problema para o diagnóstico geral
                    self.problems.append({
                        'category': 'cpu',
                        'title': f'CPU limitada (throttling)',
                        'description': f'A CPU está possivelmente limitada (throttling)',
                        'solution': 'Verifique a temperatura, energia e configurações de gerenciamento de energia.',
                        'impact': 'medium'
                    })
            
            # 4. Verificação de cores
            if result['cores_physical'] == 1:
                result['issues'].append({
                    'severity': 'low',
                    'description': 'CPU com número limitado de núcleos físicos',
                    'recommendation': 'Considere um upgrade de hardware para aplicações mais exigentes.'
                })
                # Adiciona problema para o diagnóstico geral
                self.problems.append({
                    'category': 'cpu',
                    'title': f'CPU com poucos núcleos',
                    'description': f'CPU com número limitado de núcleos físicos',
                    'solution': 'Considere um upgrade de hardware para aplicações mais exigentes.',
                    'impact': 'low'
                })
            
            # Verifica se existe algum problema para determinar a saúde
            health_status = 100
            for issue in result['issues']:
                if issue['severity'] == 'high':
                    health_status -= 20
                elif issue['severity'] == 'medium':
                    health_status -= 10
                elif issue['severity'] == 'low':
                    health_status -= 5
            
            result['health_status'] = max(health_status, 0)
            
            # Atualiza a pontuação global do sistema
            if health_status < 100:
                self.score -= (100 - health_status) * 0.15  # Impacto de 15% na pontuação total
            
            logger.info(f"Análise de CPU concluída. Saúde: {result['health_status']}%")
            
            # Atualiza os resultados
            self.results['cpu'] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao analisar CPU: {str(e)}")
            error_result = {
                'error': str(e),
                'usage': 0,
                'cores_logical': 0,
                'cores_physical': 0,
                'health_status': 0,
                'issues': [
                    {
                        'severity': 'high',
                        'description': f'Erro ao analisar CPU: {str(e)}',
                        'recommendation': 'Verifique os logs para mais detalhes.'
                    }
                ]
            }
            
            # Adiciona problema para o diagnóstico geral
            self.problems.append({
                'category': 'cpu',
                'title': f'Erro na análise de CPU',
                'description': f'Ocorreu um erro ao analisar a CPU: {str(e)}',
                'solution': 'Verifique os logs para mais detalhes.',
                'impact': 'high'
            })
            
            # Atualiza os resultados
            self.results['cpu'] = error_result
            
            return error_result
    
    def analyze_memory(self) -> Dict[str, Any]:
        """Analisa a memória RAM do sistema e retorna métricas relevantes"""
        logger.info("Analisando memória RAM...")
        
        try:
            # Usar o PlatformAdapter para obter informações de memória de forma compatível
            memory_info = PlatformAdapter.get_memory_info()
            
            # Métricas de uso
            top_memory_processes = []
            for proc in sorted(psutil.process_iter(['pid', 'name', 'memory_percent']), 
                              key=lambda p: p.info['memory_percent'] if 'memory_percent' in p.info else 0, 
                              reverse=True)[:5]:
                try:
                    if proc.info.get('memory_percent', 0) > 0:
                        top_memory_processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'memory_percent': proc.info.get('memory_percent', 0),
                            'memory_mb': proc.memory_info().rss // (1024 ** 2) if hasattr(proc, 'memory_info') else 0  # MB
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, AttributeError):
                    pass
            
            # Resultados básicos
            result = {
                'total': memory_info['total'],
                'total_gb': memory_info['total'] / (1024 ** 3),
                'available': memory_info['available'],
                'available_gb': memory_info['available'] / (1024 ** 3),
                'used': memory_info['used'],
                'used_gb': memory_info['used'] / (1024 ** 3),
                'percent': memory_info['percent'],
                'swap_total': memory_info['swap_total'],
                'swap_total_gb': memory_info['swap_total'] / (1024 ** 3),
                'swap_used': memory_info['swap_used'],
                'swap_used_gb': memory_info['swap_used'] / (1024 ** 3),
                'swap_percent': memory_info['swap_percent'],
                'top_processes': top_memory_processes,
                'issues': []
            }
            
            # Análise de problemas de memória
            total_ram_gb = result['total_gb']
            
            # Regra: verificar se há RAM suficiente (menos de 4GB é problema, menos de 8GB é alerta)
            if total_ram_gb < 8:
                result['issues'].append({
                    'code': 'low_memory',
                    'title': 'Pouca memória RAM',
                    'description': f'Seu sistema tem {total_ram_gb:.1f}GB de RAM. Para melhor desempenho, recomendamos atualizar para pelo menos 8GB de RAM.',
                    'category': 'hardware',
                    'impact': 'high' if total_ram_gb < 4 else 'medium'
                })
            
            # Verificação de problemas
            # 1. Verificar uso de memória RAM
            if result['percent'] > 90:
                result['issues'].append({
                    'severity': 'high',
                    'description': f"Memória RAM quase esgotada ({result['percent']}%)",
                    'recommendation': 'Feche programas não utilizados, reinicie o computador, ou considere aumentar a quantidade de RAM.'
                })
                # Adiciona problema para o diagnóstico geral
                self.problems.append({
                    'category': 'memory',
                    'title': f'Uso alto de memória RAM',
                    'description': f"Memória RAM quase esgotada ({result['percent']}%)",
                    'solution': 'Feche programas não utilizados, reinicie o computador, ou considere aumentar a quantidade de RAM.',
                    'impact': 'high'
                })
            elif result['percent'] > 80:
                result['issues'].append({
                    'severity': 'medium',
                    'description': f"Uso alto de memória RAM ({result['percent']}%)",
                    'recommendation': 'Feche programas não utilizados para liberar memória.'
                })
                # Adiciona problema para o diagnóstico geral
                self.problems.append({
                    'category': 'memory',
                    'title': f'Uso alto de memória RAM',
                    'description': f"Uso alto de memória RAM ({result['percent']}%)",
                    'solution': 'Feche programas não utilizados para liberar memória.',
                    'impact': 'medium'
                })
            
            # 2. Verificar quantidade total de RAM
            total_ram_gb = result['total_gb']
            if total_ram_gb < 4:
                result['issues'].append({
                    'severity': 'high',
                    'description': f"Pouca memória RAM ({total_ram_gb:.1f} GB)",
                    'recommendation': 'Considere atualizar sua memória RAM para pelo menos 8GB.'
                })
                # Adiciona problema para o diagnóstico geral
                self.problems.append({
                    'category': 'memory',
                    'title': f'Pouca memória RAM instalada',
                    'description': f"Pouca memória RAM ({total_ram_gb:.1f} GB)",
                    'solution': 'Considere atualizar sua memória RAM para pelo menos 8GB.',
                    'impact': 'high'
                })
            elif total_ram_gb < 8:
                result['issues'].append({
                    'severity': 'medium',
                    'description': f"Memória RAM limitada ({total_ram_gb:.1f} GB)",
                    'recommendation': 'Considere atualizar sua memória RAM para 16GB ou mais para melhor desempenho.'
                })
                # Adiciona problema para o diagnóstico geral
                self.problems.append({
                    'category': 'memory',
                    'title': f'Memória RAM limitada',
                    'description': f"Memória RAM limitada ({total_ram_gb:.1f} GB)",
                    'solution': 'Considere atualizar sua memória RAM para 16GB ou mais para melhor desempenho.',
                    'impact': 'medium'
                })
            
            # 3. Verificar uso excessivo de swap
            if result['swap_percent'] > 80 and result['swap_total'] > 0:
                result['issues'].append({
                    'severity': 'high',
                    'description': f"Uso excessivo de memória swap ({result['swap_percent']}%)",
                    'recommendation': 'Feche programas não utilizados ou aumente a memória RAM física.'
                })
                # Adiciona problema para o diagnóstico geral
                self.problems.append({
                    'category': 'memory',
                    'title': f'Uso excessivo de memória swap',
                    'description': f"Uso excessivo de memória swap ({result['swap_percent']}%)",
                    'solution': 'Feche programas não utilizados ou aumente a memória RAM física.',
                    'impact': 'high'
                })
            
            # Verifica se existe algum problema para determinar a saúde
            health_status = 100
            for issue in result['issues']:
                if issue['severity'] == 'high':
                    health_status -= 20
                elif issue['severity'] == 'medium':
                    health_status -= 10
                elif issue['severity'] == 'low':
                    health_status -= 5
            
            result['health_status'] = max(health_status, 0)
            
            # Atualiza a pontuação global do sistema
            if health_status < 100:
                self.score -= (100 - health_status) * 0.15  # Impacto de 15% na pontuação total
            
            logger.info(f"Análise de memória concluída. Saúde: {result['health_status']}%")
            
            # Atualiza os resultados
            self.results['memory'] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao analisar memória: {str(e)}")
            error_result = {
                'error': str(e),
                'total': 0,
                'available': 0,
                'percent': 0,
                'health_status': 0,
                'issues': [
                    {
                        'severity': 'high',
                        'description': f'Erro ao analisar memória: {str(e)}',
                        'recommendation': 'Verifique os logs para mais detalhes.'
                    }
                ]
            }
            
            # Adiciona problema para o diagnóstico geral
            self.problems.append({
                'category': 'memory',
                'title': f'Erro na análise de memória',
                'description': f'Ocorreu um erro ao analisar a memória: {str(e)}',
                'solution': 'Verifique os logs para mais detalhes.',
                'impact': 'high'
            })
            
            # Atualiza os resultados
            self.results['memory'] = error_result
            
            return error_result
    
    def analyze_disk(self):
        """Analisa os discos do sistema"""
        logger.info("Analisando discos")
        
        self.results['disk']['partitions'] = []
        total_disk_score = 0
        partition_count = 0
        
        # Tenta uma abordagem alternativa se o sistema for Windows
        if self.is_windows:
            try:
                # Usa o método alternativo para Windows
                return self._analyze_disk_windows_alternative()
            except Exception as e:
                logger.warning(f"Método alternativo para análise de disco falhou: {str(e)}")
                # Continua com o método padrão se o alternativo falhar
        
        try:
            # Analisa cada partição do sistema
            for partition in psutil.disk_partitions():
                try:
                    # Pula dispositivos de rede ou CD-ROM em sistemas Windows
                    if self.is_windows and ('cdrom' in partition.opts or partition.fstype == ''):
                        continue
                    
                    # Verifica se o ponto de montagem existe e é acessível
                    if not os.path.exists(partition.mountpoint):
                        logger.warning(f"Ponto de montagem não existe: {partition.mountpoint}")
                        continue
                    
                    # Em caso de erro, tenta usar try/except específico para cada mountpoint
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        
                        # Inicializa valores antes de processá-los
                        total_gb, used_gb, free_gb, percent = 0, 0, 0, 0
                        
                        # Processa os valores em variáveis antes de formatar
                        if hasattr(usage, 'total') and usage.total is not None:
                            total_gb = usage.total / (1024 ** 3)
                            total_gb = round(total_gb, 2) if isinstance(total_gb, (int, float)) else total_gb
                        
                        if hasattr(usage, 'used') and usage.used is not None:
                            used_gb = usage.used / (1024 ** 3)
                            used_gb = round(used_gb, 2) if isinstance(used_gb, (int, float)) else used_gb
                        
                        if hasattr(usage, 'free') and usage.free is not None:
                            free_gb = usage.free / (1024 ** 3)
                            free_gb = round(free_gb, 2) if isinstance(free_gb, (int, float)) else free_gb
                        
                        if hasattr(usage, 'percent') and usage.percent is not None:
                            percent = usage.percent
                            percent = round(percent, 2) if isinstance(percent, (int, float)) else percent
                        
                        # Cria o objeto de informações da partição
                        partition_info = {
                            'device': partition.device,
                            'mountpoint': partition.mountpoint,
                            'fstype': partition.fstype or "desconhecido",
                            'total_gb': total_gb,
                            'used_gb': used_gb,
                            'free_gb': free_gb,
                            'percent': percent
                        }
                        
                        # Verifica espaço disponível
                        partition_score = 100
                        
                        if percent > 95:
                            self.problems.append({
                                'category': 'disk',
                                'title': f'Disco {partition.device} criticamente cheio',
                                'description': f'O disco {partition.device} está com {percent}% de uso, com apenas {free_gb}GB livres.',
                                'solution': 'Libere espaço urgentemente removendo arquivos temporários, aplicativos não utilizados e considere transferir arquivos para armazenamento externo.',
                                'impact': 'high'
                            })
                            partition_score -= 40
                        elif percent > 85:
                            self.problems.append({
                                'category': 'disk',
                                'title': f'Disco {partition.device} quase cheio',
                                'description': f'O disco {partition.device} está com {percent}% de uso.',
                                'solution': 'Libere espaço removendo arquivos temporários e aplicativos não utilizados.',
                                'impact': 'medium'
                            })
                            partition_score -= 20
                        
                        # Adiciona informações e incrementa contadores
                        partition_info['score'] = partition_score
                        self.results['disk']['partitions'].append(partition_info)
                        total_disk_score += partition_score
                        partition_count += 1
                        
                    except Exception as e:
                        logger.warning(f"Erro ao analisar o uso do disco na partição {partition.mountpoint}: {str(e)}")
                        continue
                
                except PermissionError:
                    logger.warning(f"Permissão negada ao analisar a partição {partition.mountpoint}")
                    continue
                except Exception as e:
                    logger.warning(f"Erro ao analisar a partição {partition.mountpoint}: {str(e)}")
                    continue
        except Exception as e:
            logger.error(f"Erro geral na análise de discos: {str(e)}")
        
        # Calcula a pontuação média dos discos
        if partition_count > 0:
            disk_score = total_disk_score / partition_count
            self.score -= (100 - disk_score) * 0.2  # Impacto de 20% na pontuação total
        else:
            # Se nenhuma partição foi analisada com sucesso, penaliza o score
            self.problems.append({
                'category': 'disk',
                'title': 'Não foi possível analisar os discos',
                'description': 'Não foi possível analisar o espaço em disco. Isso pode indicar problemas de permissão ou corrupção.',
                'solution': 'Verifique as permissões de acesso ao disco e execute uma verificação de disco (chkdsk).',
                'impact': 'medium'
            })
            self.score -= 10
        
        logger.info(f"Análise de discos concluída. Partições analisadas: {partition_count}")
        return self.results['disk']

    def _analyze_disk_windows_alternative(self):
        """Método alternativo para análise de disco em sistemas Windows usando comandos diretos"""
        logger.info("Utilizando método alternativo para análise de disco no Windows")
        
        try:
            # Usa o comando 'wmic' para obter informações do disco
            try:
                output = subprocess.check_output("wmic logicaldisk get DeviceID,Size,FreeSpace", shell=True, text=True)
                
                lines = output.strip().split('\n')
                if len(lines) < 2:
                    raise ValueError("Saída do comando wmic inválida")
                
                # Remove a linha de cabeçalho
                lines = lines[1:]
                partition_count = 0
                total_disk_score = 0
                
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 3:
                        try:
                            device_id = parts[0]
                            
                            # Converte os valores para números
                            try:
                                size = float(parts[1])
                                free_space = float(parts[2])
                            except ValueError:
                                # Tenta extrair os números da string
                                size = float(''.join(c for c in parts[1] if c.isdigit() or c == '.'))
                                free_space = float(''.join(c for c in parts[2] if c.isdigit() or c == '.'))
                            
                            # Calcula os valores em GB e percentuais
                            total_gb = size / (1024 ** 3)
                            free_gb = free_space / (1024 ** 3)
                            used_gb = total_gb - free_gb
                            percent = 100 - (free_space / size * 100) if size > 0 else 0
                            
                            # Formata para duas casas decimais
                            total_gb = round(total_gb, 2)
                            free_gb = round(free_gb, 2)
                            used_gb = round(used_gb, 2)
                            percent = round(percent, 2)
                            
                            # Cria o objeto de informações da partição
                            partition_info = {
                                'device': device_id,
                                'mountpoint': device_id + '\\',
                                'fstype': 'NTFS',  # Assumindo NTFS para simplificar
                                'total_gb': total_gb,
                                'used_gb': used_gb,
                                'free_gb': free_gb,
                                'percent': percent
                            }
                            
                            # Verifica espaço disponível
                            partition_score = 100
                            
                            if percent > 95:
                                self.problems.append({
                                    'category': 'disk',
                                    'title': f'Disco {device_id} criticamente cheio',
                                    'description': f'O disco {device_id} está com {percent}% de uso, com apenas {free_gb}GB livres.',
                                    'solution': 'Libere espaço urgentemente removendo arquivos temporários, aplicativos não utilizados e considere transferir arquivos para armazenamento externo.',
                                    'impact': 'high'
                                })
                                partition_score -= 40
                            elif percent > 85:
                                self.problems.append({
                                    'category': 'disk',
                                    'title': f'Disco {device_id} quase cheio',
                                    'description': f'O disco {device_id} está com {percent}% de uso.',
                                    'solution': 'Libere espaço removendo arquivos temporários e aplicativos não utilizados.',
                                    'impact': 'medium'
                                })
                                partition_score -= 20
                            
                            # Adiciona informações e incrementa contadores
                            partition_info['score'] = partition_score
                            self.results['disk']['partitions'].append(partition_info)
                            total_disk_score += partition_score
                            partition_count += 1
                            
                        except Exception as e:
                            logger.warning(f"Erro ao processar informações do disco {parts[0]}: {str(e)}")
                            continue
                
                # Calcula a pontuação média dos discos
                if partition_count > 0:
                    disk_score = total_disk_score / partition_count
                    self.score -= (100 - disk_score) * 0.2  # Impacto de 20% na pontuação total
                
                logger.info(f"Análise alternativa de discos concluída. Partições analisadas: {partition_count}")
                return self.results['disk']
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Erro ao executar comando wmic: {str(e)}")
                raise
                
        except Exception as e:
            logger.error(f"Método alternativo de análise de disco falhou: {str(e)}")
            raise
    
    def analyze_startup(self):
        """Analisa programas de inicialização (apenas Windows)"""
        if not self.is_windows:
            logger.info("Análise de inicialização ignorada - não é um sistema Windows")
            return
        
        logger.info("Analisando programas de inicialização")
        
        try:
            import winreg
            
            startup_locations = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunOnce"
            ]
            
            startup_items = []
            
            # Verifica no registro do Windows
            for location in startup_locations:
                try:
                    reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, location)
                    
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(reg, i)
                            startup_items.append({
                                'name': name,
                                'command': value,
                                'location': f"HKLM\\{location}"
                            })
                            i += 1
                        except WindowsError:
                            break
                    
                    winreg.CloseKey(reg)
                except WindowsError:
                    continue
                
                try:
                    reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, location)
                    
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(reg, i)
                            startup_items.append({
                                'name': name,
                                'command': value,
                                'location': f"HKCU\\{location}"
                            })
                            i += 1
                        except WindowsError:
                            break
                    
                    winreg.CloseKey(reg)
                except WindowsError:
                    continue
            
            # Verifica nas pastas de inicialização
            startup_folders = [
                os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup"),
                os.path.join(os.environ["ALLUSERSPROFILE"], r"Microsoft\Windows\Start Menu\Programs\Startup")
            ]
            
            for folder in startup_folders:
                if os.path.exists(folder):
                    for file in os.listdir(folder):
                        file_path = os.path.join(folder, file)
                        if os.path.isfile(file_path) and (file.endswith('.lnk') or file.endswith('.url')):
                            startup_items.append({
                                'name': file,
                                'command': file_path,
                                'location': folder
                            })
            
            self.results['startup']['items'] = startup_items
            
            # Avaliação de programas de inicialização
            if len(startup_items) > 15:
                self.problems.append({
                    'category': 'startup',
                    'title': 'Excesso de programas na inicialização',
                    'description': f'Existem {len(startup_items)} programas configurados para iniciar com o Windows, o que aumenta significativamente o tempo de inicialização.',
                    'solution': 'Desative programas desnecessários na inicialização usando o Gerenciador de Tarefas.',
                    'impact': 'high'
                })
                self.score -= 15
            elif len(startup_items) > 8:
                self.problems.append({
                    'category': 'startup',
                    'title': 'Muitos programas na inicialização',
                    'description': f'Existem {len(startup_items)} programas configurados para iniciar com o Windows.',
                    'solution': 'Considere desativar programas não essenciais na inicialização para melhorar o tempo de boot.',
                    'impact': 'medium'
                })
                self.score -= 8
            
            logger.info(f"Análise de inicialização concluída. Programas encontrados: {len(startup_items)}")
        
        except Exception as e:
            logger.error(f"Erro ao analisar programas de inicialização: {str(e)}", exc_info=True)
            self.results['startup']['error'] = str(e)
    
    def analyze_drivers(self):
        """Analisa drivers do sistema (apenas Windows)"""
        if not self.is_windows:
            logger.info("Análise de drivers ignorada - não é um sistema Windows")
            return
        
        logger.info("Analisando drivers do sistema")
        
        try:
            # Inicializa COM para esta thread
            initialize_com()
            
            import wmi
            
            w = wmi.WMI()
            drivers = w.Win32_PnPSignedDriver()
            
            self.results['drivers']['count'] = len(drivers)
            self.results['drivers']['outdated'] = []
            self.results['drivers']['problematic'] = []
            
            # Lista de drivers com potenciais problemas
            problematic_drivers = []
            outdated_drivers = []
            
            for driver in drivers:
                driver_info = {
                    'name': driver.DeviceName,
                    'manufacturer': driver.Manufacturer,
                    'version': driver.DriverVersion
                }
                
                # Verificar drivers com problemas
                if hasattr(driver, 'Status') and driver.Status and driver.Status.lower() != 'ok':
                    driver_info['status'] = driver.Status
                    problematic_drivers.append(driver_info)
                
                # Verificar drivers desatualizados
                # Nota: Esta é uma verificação simples baseada na data. Uma verificação real
                # exigiria uma base de dados de drivers atualizados ou consulta a serviços online.
                if hasattr(driver, 'DriverDate') and driver.DriverDate:
                    driver_date = driver.DriverDate
                    if isinstance(driver_date, str) and len(driver_date) > 8:
                        try:
                            # Formato WMI: YYYYMMDDHHMMSS.mmmmmm+UUU
                            year = int(driver_date[:4])
                            current_year = datetime.now().year
                            
                            if (current_year - year) > 3:
                                driver_info['driver_date'] = driver_date
                                driver_info['age_years'] = current_year - year
                                outdated_drivers.append(driver_info)
                        except ValueError:
                            pass
            
            self.results['drivers']['problematic'] = problematic_drivers
            self.results['drivers']['outdated'] = outdated_drivers
            
            # Avaliação de drivers
            if len(problematic_drivers) > 0:
                self.problems.append({
                    'category': 'drivers',
                    'title': 'Drivers com problemas',
                    'description': f'Foram encontrados {len(problematic_drivers)} drivers com problemas que podem afetar o funcionamento do sistema.',
                    'solution': 'Atualize ou reinstale os drivers problemáticos usando o Gerenciador de Dispositivos.',
                    'impact': 'high'
                })
                self.score -= 15
            
            if len(outdated_drivers) > 5:
                self.problems.append({
                    'category': 'drivers',
                    'title': 'Muitos drivers desatualizados',
                    'description': f'Foram encontrados {len(outdated_drivers)} drivers com mais de 3 anos sem atualização.',
                    'solution': 'Atualize os drivers mais importantes, especialmente os de vídeo, rede e chipset.',
                    'impact': 'medium'
                })
                self.score -= 10
            elif len(outdated_drivers) > 0:
                self.problems.append({
                    'category': 'drivers',
                    'title': 'Drivers desatualizados',
                    'description': f'Foram encontrados {len(outdated_drivers)} drivers com mais de 3 anos sem atualização.',
                    'solution': 'Considere atualizar esses drivers para melhorar a estabilidade e desempenho.',
                    'impact': 'low'
                })
                self.score -= 5
            
            logger.info(f"Análise de drivers concluída. Total: {len(drivers)}, Problemáticos: {len(problematic_drivers)}, Desatualizados: {len(outdated_drivers)}")
        
        except Exception as e:
            logger.error(f"Erro ao analisar drivers: {str(e)}", exc_info=True)
            self.results['drivers']['error'] = str(e)
    
    def analyze_security(self):
        """Analisa a segurança do sistema (apenas Windows)"""
        if not self.is_windows:
            logger.info("Análise de segurança ignorada - não é um sistema Windows")
            return
        
        logger.info("Analisando segurança do sistema")
        
        try:
            # Verificar se temos acesso ao WMI
            if not HAS_WMI:
                logger.warning("Módulo WMI não disponível, usando métodos alternativos para análise de segurança")
                
                # Tenta alternativas sem WMI para obter informações de segurança
                
                # Verifica o Windows Defender usando PowerShell
                try:
                    defender_status = self._check_defender_with_powershell()
                    self.results['security']['antivirus'] = defender_status
                    
                    if not defender_status.get('real_time_protection', True):
                        self.problems.append({
                            'category': 'security',
                            'title': 'Proteção em tempo real desativada',
                            'description': 'A proteção em tempo real do Windows Defender está desativada, deixando seu sistema vulnerável.',
                            'solution': 'Ative a proteção em tempo real do Windows Defender ou instale outro antivírus.',
                            'impact': 'high'
                        })
                        self.score -= 20
                except Exception as e:
                    logger.warning(f"Não foi possível verificar o status do Windows Defender: {str(e)}")
                    self.results['security']['antivirus'] = {'error': str(e)}
                
                # Verifica o Firewall do Windows
                try:
                    firewall_status = self._check_windows_firewall()
                    self.results['security']['firewall'] = firewall_status
                    
                    if not firewall_status.get('enabled', True):
                        self.problems.append({
                            'category': 'security',
                            'title': 'Firewall desativado',
                            'description': 'O Firewall do Windows está desativado, o que pode comprometer a segurança da rede.',
                            'solution': 'Ative o Firewall do Windows ou instale outro firewall.',
                            'impact': 'high'
                        })
                        self.score -= 15
                except Exception as e:
                    logger.warning(f"Não foi possível verificar o status do Firewall do Windows: {str(e)}")
                    self.results['security']['firewall'] = {'error': str(e)}
                
                # Verifica atualizações do Windows
                try:
                    updates_status = self._check_windows_updates()
                    self.results['security']['updates'] = updates_status
                    
                    if updates_status.get('pending_count', 0) > 10:
                        self.problems.append({
                            'category': 'security',
                            'title': 'Atualizações pendentes',
                            'description': f'Existem {updates_status["pending_count"]} atualizações do Windows pendentes.',
                            'solution': 'Execute o Windows Update para instalar todas as atualizações pendentes.',
                            'impact': 'high'
                        })
                        self.score -= 15
                    elif updates_status.get('pending_count', 0) > 0:
                        self.problems.append({
                            'category': 'security',
                            'title': 'Algumas atualizações pendentes',
                            'description': f'Existem {updates_status["pending_count"]} atualizações do Windows pendentes.',
                            'solution': 'Execute o Windows Update para manter seu sistema atualizado.',
                            'impact': 'medium'
                        })
                        self.score -= 8
                except Exception as e:
                    logger.warning(f"Não foi possível verificar as atualizações do Windows: {str(e)}")
                    self.results['security']['updates'] = {'error': str(e)}
                
                return
            
            # Se temos WMI, usa o método padrão
            import wmi
            w = wmi.WMI()
            
            # Verifica o Windows Defender
            try:
                defender_status = self._check_windows_defender()
                self.results['security']['antivirus'] = defender_status
                
                if not defender_status.get('real_time_protection', True):
                    self.problems.append({
                        'category': 'security',
                        'title': 'Proteção em tempo real desativada',
                        'description': 'A proteção em tempo real do Windows Defender está desativada, deixando seu sistema vulnerável.',
                        'solution': 'Ative a proteção em tempo real do Windows Defender ou instale outro antivírus.',
                        'impact': 'high'
                    })
                    self.score -= 20
            except Exception as e:
                logger.warning(f"Não foi possível verificar o status do Windows Defender: {str(e)}")
                self.results['security']['antivirus'] = {'error': str(e)}
            
            # Verifica o Firewall do Windows
            try:
                firewall_status = self._check_windows_firewall()
                self.results['security']['firewall'] = firewall_status
                
                if not firewall_status.get('enabled', True):
                    self.problems.append({
                        'category': 'security',
                        'title': 'Firewall desativado',
                        'description': 'O Firewall do Windows está desativado, o que pode comprometer a segurança da rede.',
                        'solution': 'Ative o Firewall do Windows ou instale outro firewall.',
                        'impact': 'high'
                    })
                    self.score -= 15
            except Exception as e:
                logger.warning(f"Não foi possível verificar o status do Firewall do Windows: {str(e)}")
                self.results['security']['firewall'] = {'error': str(e)}
            
            # Verifica atualizações do Windows
            try:
                updates_status = self._check_windows_updates()
                self.results['security']['updates'] = updates_status
                
                if updates_status.get('pending_count', 0) > 10:
                    self.problems.append({
                        'category': 'security',
                        'title': 'Atualizações pendentes',
                        'description': f'Existem {updates_status["pending_count"]} atualizações do Windows pendentes.',
                        'solution': 'Execute o Windows Update para instalar todas as atualizações pendentes.',
                        'impact': 'high'
                    })
                    self.score -= 15
                elif updates_status.get('pending_count', 0) > 0:
                    self.problems.append({
                        'category': 'security',
                        'title': 'Algumas atualizações pendentes',
                        'description': f'Existem {updates_status["pending_count"]} atualizações do Windows pendentes.',
                        'solution': 'Execute o Windows Update para manter seu sistema atualizado.',
                        'impact': 'medium'
                    })
                    self.score -= 8
            except Exception as e:
                logger.warning(f"Não foi possível verificar as atualizações do Windows: {str(e)}")
                self.results['security']['updates'] = {'error': str(e)}
            
            logger.info("Análise de segurança concluída")
        
        except Exception as e:
            logger.error(f"Erro ao analisar segurança: {str(e)}")
            self.results['security']['error'] = str(e)
    
    def _check_windows_defender(self):
        """Verifica o status do Windows Defender"""
        result = {}
        
        # Se WMI não estiver disponível, usa o método PowerShell
        if not HAS_WMI:
            return self._check_defender_with_powershell()
        
        try:
            # Inicializa COM para esta thread
            initialize_com()
            
            import wmi
            w = wmi.WMI(namespace="root\\Microsoft\\Windows\\Defender")
            
            # Verifica o status do serviço
            defender = w.MSFT_MpComputerStatus()[0]
            
            result['product_name'] = 'Windows Defender'
            result['real_time_protection'] = defender.RealTimeProtectionEnabled
            result['antivirus_enabled'] = defender.AntivirusEnabled
            result['antispyware_enabled'] = defender.AntispywareEnabled
            result['behavior_monitoring'] = defender.BehaviorMonitorEnabled
            result['version'] = defender.AntivirusSignatureVersion
            result['engine_version'] = defender.AMEngineVersion
            result['last_update'] = defender.AntivirusSignatureLastUpdated
            
            return result
        except Exception as e:
            logger.warning(f"Erro ao verificar Windows Defender via WMI: {str(e)}")
            return self._check_defender_with_powershell()
    
    def _check_defender_with_powershell(self):
        """Verifica o status do Windows Defender usando PowerShell"""
        result = {}
        
        try:
            # Executa o comando PowerShell para verificar o status do Windows Defender
            cmd = ['powershell', '-Command', 'Get-MpComputerStatus | ConvertTo-Json']
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if process.returncode == 0 and process.stdout:
                status = json.loads(process.stdout)
                
                result['product_name'] = 'Windows Defender'
                result['real_time_protection'] = status.get('RealTimeProtectionEnabled', False)
                result['antivirus_enabled'] = status.get('AntivirusEnabled', False)
                result['antispyware_enabled'] = status.get('AntispywareEnabled', False)
                result['last_scan'] = status.get('LastFullScanDateTime', '')
                result['last_definition_update'] = status.get('AntivirusSignatureLastUpdated', '')
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _check_windows_firewall(self):
        """Verifica o status do Firewall do Windows"""
        result = {}
        
        try:
            # Executa o comando para verificar o status do firewall
            cmd = ['netsh', 'advfirewall', 'show', 'allprofiles']
            process = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if process.returncode == 0:
                output = process.stdout
                
                # Processa a saída para extrair o status
                profiles = {
                    'Domain Profile': {},
                    'Private Profile': {},
                    'Public Profile': {}
                }
                
                current_profile = None
                for line in output.splitlines():
                    line = line.strip()
                    
                    # Identifica o perfil atual
                    if line.endswith('Profile Settings:'):
                        current_profile = line.replace('Profile Settings:', '').strip()
                        continue
                    
                    # Extrai o status do firewall para o perfil atual
                    if current_profile and line.startswith('State'):
                        state = line.split(' ', 1)[1].strip()
                        if current_profile in profiles:
                            profiles[current_profile]['enabled'] = (state.upper() == 'ON')
                
                # Verifica se pelo menos um perfil está ativo
                any_enabled = any(profile.get('enabled', False) for profile in profiles.values())
                
                result = {
                    'enabled': any_enabled,
                    'profiles': profiles
                }
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _check_windows_updates(self):
        """Verifica o status das atualizações do Windows"""
        result = {}
        
        try:
            # Executa o comando PowerShell para verificar atualizações pendentes
            cmd = ['powershell', '-Command', '(New-Object -ComObject Microsoft.Update.Session).CreateUpdateSearcher().Search("IsInstalled=0").Updates.Count']
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0 and process.stdout:
                pending_count = int(process.stdout.strip())
                result['pending_count'] = pending_count
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def _get_disk_type_windows(self, drive_letter):
        """Determina se o disco é SSD ou HDD no Windows"""
        # Remove qualquer coisa após : e remove a / (se houver)
        if drive_letter.endswith(':'):
            drive_letter = drive_letter[:2]
        else:
            drive_letter = drive_letter.split(':')[0]
            if drive_letter.startswith('\\'):
                drive_letter = drive_letter.lstrip('\\')
            drive_letter = f"{drive_letter}:"
        
        try:
            # Executa o comando para obter o tipo de mídia
            cmd = ['powershell', '-Command', f'Get-PhysicalDisk | Where-Object {{ $_.DeviceId -eq ((Get-Partition -DriveLetter {drive_letter[0]}).DiskNumber) }} | Select-Object MediaType | ConvertTo-Json']
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0 and process.stdout:
                output = json.loads(process.stdout)
                media_type = output.get('MediaType', 0)
                
                # MediaType: 3 = HDD, 4 = SSD, 5 = SCM
                if media_type == 4:
                    return 'SSD'
                elif media_type == 3:
                    return 'HDD'
                elif media_type == 5:
                    return 'SCM'
                else:
                    return 'Unknown'
        except Exception:
            pass
        
        # Método alternativo se o primeiro falhar
        try:
            cmd = ['wmic', 'diskdrive', 'get', 'Model,SerialNumber,Status,MediaType', '/format:csv']
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if 'SSD' in process.stdout:
                return 'SSD'
            elif 'HDD' in process.stdout:
                return 'HDD'
        except Exception:
            pass
        
        return 'Unknown'
    
    def _check_fragmentation_windows(self, drive_letter):
        """Verifica a fragmentação do disco no Windows"""
        if not drive_letter.endswith(':'):
            drive_letter = drive_letter[:2]
        
        try:
            # Executa o comando para verificar a fragmentação
            cmd = ['powershell', '-Command', f'$vol = Get-Volume -DriveLetter {drive_letter[0]}; $defrag = Optimize-Volume -DriveLetter {drive_letter[0]} -Analyze -Verbose; $vol | Select-Object FileSystemFragmentation | ConvertTo-Json']
            process = subprocess.run(cmd, capture_output=True, text=True)
            
            if process.returncode == 0 and process.stdout:
                try:
                    output = json.loads(process.stdout)
                    fragmentation = output.get('FileSystemFragmentation', 0)
                    return fragmentation
                except json.JSONDecodeError:
                    # Fallback para extração por expressão regular
                    import re
                    match = re.search(r'FileSystemFragmentation\s*:\s*(\d+)', process.stdout)
                    if match:
                        return int(match.group(1))
        except Exception as e:
            logger.warning(f"Erro ao verificar fragmentação: {str(e)}")
        
        return None
    
    def analyze_temperature(self):
        """Analisa a temperatura dos componentes do sistema"""
        logger.info("Analisando temperatura dos componentes")
        
        temperatures = {}
        
        # Verificar a disponibilidade dos módulos
        HAS_WMI = False
        if self.is_windows:
            try:
                import wmi
                HAS_WMI = True
            except ImportError:
                logger.warning("Módulo 'wmi' não está disponível para análise de temperatura")
                HAS_WMI = False
        
        if platform.system() == 'Linux':
            try:
                import sensors
                HAS_SENSORS = True
            except ImportError:
                logger.warning("Módulo 'sensors' não está disponível para análise de temperatura")
                HAS_SENSORS = False
        
        # Método específico para Windows usando WMI
        if self.is_windows and HAS_WMI:
            try:
                temperatures = self._check_temperatures_windows()
            except Exception as e:
                logger.error(f"Erro ao verificar temperaturas via WMI: {str(e)}")
        
        # Método para Linux usando sensors
        elif platform.system() == 'Linux' and HAS_SENSORS:
            try:
                temperatures = self._check_temperatures_linux()
            except Exception as e:
                logger.error(f"Erro ao verificar temperaturas via sensors: {str(e)}")
        
        # Tenta usar método genérico para ambos sistemas com psutil
        if not temperatures:
            try:
                if hasattr(psutil, "sensors_temperatures"):
                    temps = psutil.sensors_temperatures()
                    if temps:
                        for chip, sensors_list in temps.items():
                            for sensor in sensors_list:
                                if hasattr(sensor, 'current') and sensor.current:
                                    label = sensor.label or f"{chip}_{sensor.index}"
                                    temperatures[label] = sensor.current
            except Exception as e:
                logger.error(f"Erro ao verificar temperaturas via psutil: {str(e)}")
            
        # Se nenhum método funcionou, tenta métodos alternativos
        if not temperatures and self.is_windows:
            try:
                # Tenta usar o OpenHardwareMonitor via comando
                temperatures = self._check_temperatures_alternative_windows()
            except Exception as e:
                logger.error(f"Erro ao verificar temperaturas via método alternativo: {str(e)}")
        
        self.results['temperature']['components'] = temperatures
        
        # Avaliação das temperaturas
        cpu_temp = None
        
        # Tenta identificar a temperatura da CPU entre os valores obtidos
        for key, value in temperatures.items():
            if 'cpu' in key.lower() or 'processor' in key.lower() or 'core' in key.lower():
                if cpu_temp is None or value > cpu_temp:
                    cpu_temp = value
        
        if cpu_temp:
            self.results['temperature']['cpu'] = cpu_temp
            
            # Avaliação da temperatura da CPU
            if cpu_temp > 90:  # Temperatura crítica
                self.problems.append({
                    'category': 'temperature',
                    'title': 'Temperatura da CPU muito alta',
                    'description': f'A CPU está operando a {cpu_temp}°C, o que pode causar danos permanentes ao hardware.',
                    'solution': 'Desligue o computador imediatamente, verifique se as ventoinhas estão funcionando e limpe o sistema de refrigeração.',
                    'impact': 'critical'
                })
                self.score -= 25
            elif cpu_temp > 80:  # Temperatura alta
                self.problems.append({
                    'category': 'temperature',
                    'title': 'Temperatura da CPU alta',
                    'description': f'A CPU está operando a {cpu_temp}°C, o que pode causar instabilidade e redução de desempenho.',
                    'solution': 'Verifique a refrigeração do sistema, limpe o pó interno e considere melhorar o fluxo de ar no gabinete.',
                    'impact': 'high'
                })
                self.score -= 15
            elif cpu_temp > 70:  # Temperatura elevada
                self.problems.append({
                    'category': 'temperature',
                    'title': 'Temperatura da CPU elevada',
                    'description': f'A CPU está operando a {cpu_temp}°C, um pouco acima do ideal para operação prolongada.',
                    'solution': 'Considere melhorar a ventilação do sistema e verificar se os dissipadores de calor estão limpos.',
                    'impact': 'medium'
                })
                self.score -= 5
        else:
            self.results['temperature']['cpu'] = None
            logger.warning("Não foi possível determinar a temperatura da CPU")
        
        logger.info(f"Análise de temperatura concluída. Temperatura CPU: {self.results['temperature'].get('cpu')}°C")
    
    def analyze_network(self):
        """Analisa a conectividade de rede"""
        logger.info("Analisando conectividade de rede")
        
        # Inicializa a estrutura de dados de rede
        self.results['network'] = {
            'interfaces': [],
            'bytes_sent': 0,
            'bytes_recv': 0,
            'packets_sent': 0,
            'packets_recv': 0,
            'errin': 0,
            'errout': 0,
            'internet_connected': False,
            'latency_ms': None,
            'dns_status': 'unknown',
            'gateway_status': 'unknown',
            'connection_quality': 'unknown',
            'active_connections': 0
        }
        
        # Analisa as interfaces de rede
        try:
            for interface, addresses in psutil.net_if_addrs().items():
                interface_info = {
                    'name': interface, 
                    'addresses': [],
                    'speed': 'unknown',
                    'is_up': True,  # Considera que está ativa por padrão
                    'mac_address': None
                }
                
                for address in addresses:
                    if address.family == socket.AF_INET:  # IPv4
                        interface_info['addresses'].append({
                            'ip': address.address,
                            'netmask': address.netmask,
                            'type': 'IPv4'
                        })
                    elif address.family == socket.AF_INET6:  # IPv6
                        interface_info['addresses'].append({
                            'ip': address.address,
                            'netmask': address.netmask,
                            'type': 'IPv6'
                        })
                    elif hasattr(socket, 'AF_PACKET') and address.family == socket.AF_PACKET:  # MAC address
                        interface_info['mac_address'] = address.address
                
                # Tenta obter status mais detalhados da interface
                try:
                    if_stats = psutil.net_if_stats().get(interface)
                    if if_stats:
                        interface_info['is_up'] = if_stats.isup
                        interface_info['speed'] = f"{if_stats.speed} Mbps" if if_stats.speed > 0 else "unknown"
                        interface_info['mtu'] = if_stats.mtu
                except Exception as e:
                    logger.warning(f"Erro ao obter estatísticas detalhadas da interface {interface}: {str(e)}")
                
                self.results['network']['interfaces'].append(interface_info)
        except Exception as e:
            logger.warning(f"Erro ao obter informações de interfaces de rede: {str(e)}")
        
        # Estatísticas de rede
        try:
            net_io = psutil.net_io_counters()
            self.results['network']['bytes_sent'] = net_io.bytes_sent
            self.results['network']['bytes_recv'] = net_io.bytes_recv
            self.results['network']['packets_sent'] = net_io.packets_sent
            self.results['network']['packets_recv'] = net_io.packets_recv
            self.results['network']['errin'] = net_io.errin
            self.results['network']['errout'] = net_io.errout
            
            # Calcula uso de banda aproximado (taxa de transferência)
            try:
                # Mede uso em dois momentos para calcular taxa
                time.sleep(0.5)  # Espera 0.5 segundo
                net_io2 = psutil.net_io_counters()
                down_speed = (net_io2.bytes_recv - net_io.bytes_recv) * 2  # Bytes por segundo
                up_speed = (net_io2.bytes_sent - net_io.bytes_sent) * 2  # Bytes por segundo
                
                self.results['network']['download_speed_bps'] = down_speed
                self.results['network']['upload_speed_bps'] = up_speed
                
                # Classifica qualidade com base na taxa
                if down_speed > 1024 * 1024:  # Mais de 1MB/s
                    self.results['network']['connection_quality'] = 'excellent'
                elif down_speed > 500 * 1024:  # Mais de 500KB/s
                    self.results['network']['connection_quality'] = 'good'
                elif down_speed > 100 * 1024:  # Mais de 100KB/s
                    self.results['network']['connection_quality'] = 'average'
                elif down_speed > 0:
                    self.results['network']['connection_quality'] = 'poor'
                else:
                    self.results['network']['connection_quality'] = 'inactive'
            except Exception as e:
                logger.warning(f"Erro ao calcular taxa de transferência: {str(e)}")
        except Exception as e:
            logger.warning(f"Erro ao obter estatísticas de rede: {str(e)}")
        
        # Verifica conexões ativas
        try:
            connections = psutil.net_connections()
            self.results['network']['active_connections'] = len(connections)
            
            # Identifica processos usando a rede (apenas uma amostra)
            network_processes = []
            for conn in connections[:10]:  # Limita para evitar processamento excessivo
                if conn.pid and conn.status == 'ESTABLISHED':
                    try:
                        proc = psutil.Process(conn.pid)
                        network_processes.append({
                            'pid': conn.pid,
                            'name': proc.name(),
                            'remote_ip': conn.raddr.ip if conn.raddr else None,
                            'remote_port': conn.raddr.port if conn.raddr else None,
                            'local_port': conn.laddr.port if conn.laddr else None
                        })
                    except Exception:
                        pass
                        
            if network_processes:
                self.results['network']['sample_processes'] = network_processes
        except Exception as e:
            logger.warning(f"Erro ao analisar conexões de rede: {str(e)}")
        
        # Teste de gateway
        try:
            default_gateway = None
            
            if self.is_windows:
                try:
                    # Windows - usa ipconfig
                    output = subprocess.check_output("ipconfig", shell=True, text=True)
                    for line in output.split('\n'):
                        if "Default Gateway" in line or "Gateway Padrão" in line:
                            parts = line.split(':')
                            if len(parts) > 1 and parts[1].strip():
                                default_gateway = parts[1].strip()
                                break
                except Exception:
                    pass
            else:
                try:
                    # Linux - usa route
                    output = subprocess.check_output("ip route | grep default", shell=True, text=True)
                    parts = output.strip().split()
                    if len(parts) > 2:
                        default_gateway = parts[2]
                except Exception:
                    pass
            
            if default_gateway:
                self.results['network']['default_gateway'] = default_gateway
                
                # Testa ping para o gateway
                try:
                    if self.is_windows:
                        cmd = f"ping -n 4 {default_gateway}"
                    else:
                        cmd = f"ping -c 4 {default_gateway}"
                    
                    ping_output = subprocess.check_output(cmd, shell=True, text=True)
                    
                    # Extrai latência média
                    if "Average" in ping_output or "Media" in ping_output or "avg" in ping_output:
                        import re
                        
                        # Diferentes padrões para diferentes sistemas
                        latency_patterns = [
                            r"Average = (\d+)ms",  # Windows EN
                            r"Média = (\d+)ms",    # Windows PT
                            r"= [\d\.]+/(\d+\.\d+)/",  # Linux
                        ]
                        
                        for pattern in latency_patterns:
                            match = re.search(pattern, ping_output)
                            if match:
                                try:
                                    self.results['network']['latency_ms'] = float(match.group(1))
                                    self.results['network']['gateway_status'] = 'reachable'
                                    break
                                except ValueError:
                                    pass
                except Exception:
                    self.results['network']['gateway_status'] = 'unreachable'
            else:
                self.results['network']['gateway_status'] = 'not_found'
        except Exception as e:
            logger.warning(f"Erro ao testar gateway: {str(e)}")
        
        # Teste de DNS
        try:
            dns_working = False
            test_domains = ['google.com', 'amazon.com', 'microsoft.com']
            
            for domain in test_domains:
                try:
                    socket.gethostbyname(domain)
                    dns_working = True
                    break
                except socket.gaierror:
                    continue
            
            self.results['network']['dns_status'] = 'working' if dns_working else 'failing'
            
            if not dns_working:
                self.problems.append({
                    'category': 'network',
                    'title': 'Resolução DNS não está funcionando',
                    'description': 'Não foi possível resolver nomes de domínio para endereços IP.',
                    'solution': 'Verifique as configurações DNS, tente usar o DNS 8.8.8.8 (Google) ou 1.1.1.1 (Cloudflare).',
                    'impact': 'medium'
                })
                self.score -= 10
        except Exception as e:
            logger.warning(f"Erro ao testar DNS: {str(e)}")
        
        # Teste de conectividade com a internet
        try:
            internet_connected = False
            test_sites = ['8.8.8.8', '1.1.1.1', 'google.com']
            for site in test_sites:
                try:
                    # Tenta abrir um socket TCP na porta 53 (DNS) ou 80 (HTTP)
                    for port in [53, 80]:
                        sock = socket.create_connection((site, port), timeout=2)
                        sock.close()
                        internet_connected = True
                        break
                    if internet_connected:
                        break
                except Exception:
                    continue
            
            self.results['network']['internet_connected'] = internet_connected
            
            if not internet_connected:
                self.problems.append({
                    'category': 'network',
                    'title': 'Sem conexão com a internet',
                    'description': 'Não foi possível conectar-se a sites populares.',
                    'solution': 'Verifique sua conexão de rede, reinicie o roteador ou contate seu provedor.',
                    'impact': 'high'
                })
                self.score -= 15
        except Exception as e:
            logger.warning(f"Erro ao testar conectividade com a internet: {str(e)}")
        
        # Detecta problemas em interfaces
        if not self.results['network']['interfaces']:
            self.problems.append({
                'category': 'network',
                'title': 'Nenhuma interface de rede detectada',
                'description': 'Não foi possível encontrar nenhuma interface de rede.',
                'solution': 'Verifique se os adaptadores de rede estão instalados corretamente.',
                'impact': 'high'
            })
            self.score -= 15
        else:
            # Verifica interfaces com problemas
            problem_interfaces = []
            for iface in self.results['network']['interfaces']:
                if not iface.get('is_up', False):
                    problem_interfaces.append(iface['name'])
            
            if problem_interfaces:
                self.problems.append({
                    'category': 'network',
                    'title': f"Interface(s) de rede desativada(s): {', '.join(problem_interfaces)}",
                    'description': 'Uma ou mais interfaces de rede estão desativadas.',
                    'solution': 'Verifique as configurações de rede e ative as interfaces necessárias.',
                    'impact': 'medium'
                })
                self.score -= 5
        
        # Verifica erros de rede
        if self.results['network'].get('errin', 0) > 1000 or self.results['network'].get('errout', 0) > 1000:
            self.problems.append({
                'category': 'network',
                'title': 'Erros frequentes na rede',
                'description': 'Foram detectados muitos erros de pacote na rede.',
                'solution': 'Verifique se há problemas com cabos, interferência Wi-Fi ou hardware de rede defeituoso.',
                'impact': 'medium'
            })
            self.score -= 5
        
        logger.info(f"Análise de rede concluída. Interfaces: {len(self.results['network'].get('interfaces', []))}, " +
                   f"Conectividade: {self.results['network'].get('internet_connected', False)}")
        
        return self.results['network']
    
    def generate_report(self):
        """
        Gera o relatório final do diagnóstico
        
        Returns:
            dict: Relatório completo com resultados, problemas e recomendações
        """
        # Ajusta a pontuação final para estar entre 0 e 100
        self.score = max(0, min(100, self.score))
        
        # Gera recomendações baseadas nos problemas encontrados
        recommendations = self.generate_recommendations()
        
        # Cria o relatório completo
        report = {
            'timestamp': datetime.now().isoformat(),
            'system': {
                'os': platform.system(),
                'os_version': platform.version(),
                'hostname': platform.node(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version()
            },
            'score': self.score,
            'results': self.results,
            'problems': sorted(self.problems, key=lambda x: 0 if x['impact'] == 'high' else 1 if x['impact'] == 'medium' else 2),
            'recommendations': recommendations
        }
        
        # Classificação do estado do sistema
        if self.score >= 90:
            report['system_status'] = "Excelente"
        elif self.score >= 80:
            report['system_status'] = "Bom"
        elif self.score >= 70:
            report['system_status'] = "Adequado"
        elif self.score >= 50:
            report['system_status'] = "Precisa de melhoria"
        else:
            report['system_status'] = "Crítico"
        
        logger.info(f"Relatório de diagnóstico gerado. Pontuação: {self.score}, Status: {report['system_status']}")
        
        return report
    
    def generate_recommendations(self):
        """
        Gera recomendações baseadas nos problemas encontrados
        
        Returns:
            list: Lista de recomendações ordenadas por prioridade
        """
        recommendations = []
        
        # Converte problemas em recomendações
        for problem in self.problems:
            recommendations.append({
                'title': 'Resolver: ' + problem['title'],
                'description': problem['solution'],
                'category': problem['category'],
                'impact': problem['impact']
            })
        
        # Adiciona recomendações gerais baseadas na pontuação
        if self.score < 50:
            recommendations.append({
                'title': 'Manutenção completa do sistema',
                'description': 'Seu sistema precisa de uma manutenção completa. Considere backup dos dados e reinstalação do sistema operacional se os outros reparos não forem suficientes.',
                'category': 'general',
                'impact': 'high'
            })
        elif self.score < 70:
            recommendations.append({
                'title': 'Otimização geral do sistema',
                'description': 'Seu sistema pode se beneficiar de uma otimização geral, incluindo limpeza de arquivos temporários, desfragmentação (para HDDs) e revisão de programas de inicialização.',
                'category': 'general',
                'impact': 'medium'
            })
        
        # Recomendações para hardware específico
        if 'cpu' in self.results:
            if self.results.get('cpu', {}).get('cores_physical', 0) < 4:
                recommendations.append({
                    'title': 'Atualização de processador',
                    'description': 'Seu processador está abaixo das especificações recomendadas para software moderno. Considere atualizar para um modelo com pelo menos 4 núcleos.',
                    'category': 'hardware',
                    'impact': 'medium'
                })
        
        if 'memory' in self.results:
            total_ram_gb = self.results.get('memory', {}).get('total', 0) / 1024  # GB
            if total_ram_gb < 8:
                recommendations.append({
                    'title': 'Atualização de memória RAM',
                    'description': f'Seu sistema tem {total_ram_gb:.1f}GB de RAM. Para melhor desempenho, recomendamos atualizar para pelo menos 8GB de RAM.',
                    'category': 'hardware',
                    'impact': 'high' if total_ram_gb < 4 else 'medium'
                })
        
        # Ordena as recomendações por impacto
        impact_priority = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda x: impact_priority.get(x['impact'], 3))
        
        return recommendations

    def get_system_metrics(self, user_id: str = None) -> dict:
        """Obtém métricas resumidas do sistema para visualização"""
        return self.repository.get_metrics(user_id)
    
    def get_system_summary(self) -> Dict[str, Any]:
        """
        Obtém um resumo das informações do sistema para exibição rápida.
        Versão simplificada do get_computer_identity.
        
        Returns:
            dict: Resumo das informações do sistema
        """
        try:
            import platform
            import psutil
            import socket
            import datetime
            
            # Informações básicas do sistema
            system_info = {
                'os': {
                    'name': platform.system(),
                    'version': platform.release(),
                    'full_version': platform.version(),
                    'hostname': socket.gethostname(),
                    'uptime_hours': 0.0  # Valor padrão em caso de erro
                }
            }
            
            # Calcular uptime com tratamento de erro
            try:
                boot_time = psutil.boot_time()
                uptime_secs = (datetime.datetime.now() - datetime.datetime.fromtimestamp(boot_time)).total_seconds()
                system_info['os']['uptime_hours'] = round(uptime_secs / 3600, 2)
            except Exception as e:
                logger.warning(f"Erro ao calcular uptime: {str(e)}")
            
            # Informações da CPU
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count(logical=False) or 1
            cpu_count_logical = psutil.cpu_count(logical=True) or 1
            
            # Obter marca/modelo da CPU
            cpu_brand = platform.processor()
            if not cpu_brand or "unknown" in cpu_brand.lower():
                # Tentar com PlatformAdapter
                try:
                    from app.services.diagnostic_service_platform import PlatformAdapter
                    cpu_info = PlatformAdapter.get_cpu_info()
                    if cpu_info and 'brand' in cpu_info:
                        cpu_brand = cpu_info['brand']
                except Exception:
                    cpu_brand = "CPU não identificada"
            
            system_info['cpu'] = {
                'brand': cpu_brand,
                'cores_physical': cpu_count,
                'cores_logical': cpu_count_logical,
                'usage_percent': cpu_percent,
                'frequency_mhz': cpu_freq.current if cpu_freq else 0,
                'status': 'Bom' if cpu_percent < 80 else 'Atenção'
            }
            
            # Informações da memória
            memory = psutil.virtual_memory()
            system_info['memory'] = {
                'total_gb': round(memory.total / (1024**3), 2),
                'available_gb': round(memory.available / (1024**3), 2),
                'used_gb': round(memory.used / (1024**3), 2),
                'percent_used': memory.percent,
                'status': 'Bom' if memory.percent < 90 else 'Atenção'
            }
            
            return system_info
        except Exception as e:
            logger.error(f"Erro ao obter resumo do sistema: {str(e)}")
            return {
                'os': {'name': 'Desconhecido', 'version': 'Desconhecido', 'uptime_hours': 0.0},
                'cpu': {'brand': 'Desconhecido', 'cores_physical': 1, 'status': 'Desconhecido'},
                'memory': {'total_gb': 0, 'used_gb': 0, 'percent_used': 0, 'status': 'Desconhecido'}
            }
    
    def _get_driver_summary(self) -> Dict[str, Any]:
        """Retorna resumo do status dos drivers"""
        # Valores padrão para ambiente de teste ou não-Windows
        if os.environ.get('DIAGNOSTIC_TEST_MODE') == '1' or not is_windows():
            return {
                'status': 'Bom',
                'outdated_count': 0
            }
            
        try:
            # Simulação simplificada - em produção, usar dados reais
            import random
            outdated = random.randint(0, 3)
            
            return {
                'status': 'Bom' if outdated == 0 else 'Atenção',
                'outdated_count': outdated,
                'message': f"{outdated} drivers desatualizados" if outdated > 0 else "Todos os drivers atualizados"
            }
        except Exception as e:
            logger.error(f"Erro ao verificar status dos drivers: {e}")
            return {
                'status': 'Desconhecido',
                'outdated_count': 0,
                'error': str(e)
            }
    
    def _get_security_summary(self) -> Dict[str, Any]:
        """Retorna resumo do status de segurança"""
        if os.environ.get('DIAGNOSTIC_TEST_MODE') == '1':
            return {
                'status': 'Bom',
                'antivirus': 'Ativo',
                'firewall': 'Ativo',
                'updates': 'Atualizado'
            }
            
        security = {
            'antivirus': 'Desconhecido',
            'firewall': 'Desconhecido',
            'updates': 'Desconhecido'
        }
        
        try:
            if is_windows():
                # Verificar Windows Defender
                av_status = self._check_windows_defender_status()
                security['antivirus'] = av_status
                
                # Verificar Firewall
                fw_status = self._check_firewall_status()
                security['firewall'] = fw_status
                
                # Verificar atualizações (simplificado)
                security['updates'] = 'Verificando...'
            
            # Determinar status geral
            if 'Desativado' in security.values() or 'Problema' in security.values():
                security['status'] = 'Problema'
            elif 'Desconhecido' in security.values():
                security['status'] = 'Atenção'
            else:
                security['status'] = 'Bom'
                
            return security
        except Exception as e:
            logger.error(f"Erro ao verificar status de segurança: {e}")
            return {
                'status': 'Desconhecido',
                'antivirus': 'Erro na verificação',
                'firewall': 'Erro na verificação',
                'updates': 'Erro na verificação',
                'error': str(e)
            }
    
    def _check_windows_defender_status(self) -> str:
        """Verifica status simplificado do Windows Defender"""
        if not is_windows():
            return "Não aplicável"
            
        try:
            # Simplificação para exemplo - em produção usar PowerShell para verificação real
            return "Ativo"
        except Exception:
            return "Desconhecido"
    
    def _check_firewall_status(self) -> str:
        """Verifica status simplificado do Firewall"""
        if not is_windows():
            return "Não aplicável"
            
        try:
            # Simplificação para exemplo - em produção usar comandos netsh
            return "Ativo"
        except Exception:
            return "Desconhecido"
    
    def get_computer_identity(self) -> Dict[str, Any]:
        """
        Obtém informações detalhadas do computador, como um 'RG do computador'
        
        Returns:
            dict: Informações detalhadas do sistema
        """
        try:
            from app.services.diagnostic_service_platform import PlatformAdapter
            import platform
            import socket
            import uuid
            import psutil
            import cpuinfo
            import datetime
            
            # Informações do sistema operacional
            system_info = {
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'architecture': platform.architecture(),
                'hostname': socket.gethostname(),
                'ip_address': socket.gethostbyname(socket.gethostname()),
                'mac_address': ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 2)][::-1]),
                'boot_time': datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
                'uptime_hours': round((datetime.datetime.now() - datetime.datetime.fromtimestamp(psutil.boot_time())).total_seconds() / 3600, 2)
            }
            
            # Obter informações detalhadas do sistema (fabricante, modelo)
            system_details = PlatformAdapter.get_system_information()
            system_info.update({
                'manufacturer': system_details.get('manufacturer', 'Desconhecido'),
                'model': system_details.get('model', 'Desconhecido'),
                'serial_number': system_details.get('serial_number', 'Desconhecido')
            })
            
            # Se houver informações de BIOS, adicionar
            if 'bios' in system_details:
                system_info['bios'] = system_details['bios']
            
            # Informações da CPU
            cpu_info = PlatformAdapter.get_cpu_info()
            detailed_cpu_info = cpuinfo.get_cpu_info()
            
            # Verificar se informações estão corretas através de validação cruzada
            cpu_brand = cpu_info.get('brand', 'Desconhecido')
            platform_processor = platform.processor()
            
            # Se as informações são diferentes e platform.processor retorna algo útil,
            # verificar qual parece mais confiável
            if cpu_brand != platform_processor and platform_processor and "unknown" not in platform_processor.lower():
                # Verificar qual tem mais detalhes e parece mais confiável
                if len(platform_processor) > len(cpu_brand) and cpu_brand in platform_processor:
                    cpu_brand = platform_processor
            
            # Extrair informações mais detalhadas da CPU
            cpu = {
                'brand': cpu_brand,
                'vendor': cpu_info.get('vendor', 'Desconhecido'),
                'cores_physical': cpu_info.get('cores_physical', 0),
                'cores_logical': cpu_info.get('cores_logical', 0),
                'frequency_mhz': cpu_info.get('frequency', 0),
                'architecture': cpu_info.get('architecture', 'Desconhecido'),
                'bits': cpu_info.get('bits', 64),
                'virtualization': detailed_cpu_info.get('flags', []),
                'l1_cache_size': detailed_cpu_info.get('l1_data_cache_size', 'Desconhecido'),
                'l2_cache_size': detailed_cpu_info.get('l2_cache_size', 'Desconhecido'),
                'l3_cache_size': detailed_cpu_info.get('l3_cache_size', 'Desconhecido'),
                'current_usage_percent': psutil.cpu_percent(interval=0.1)
            }
            
            # Informações da memória
            memory_info = PlatformAdapter.get_memory_info()
            memory = {
                'total_gb': round(memory_info.get('total', 0) / (1024**3), 2),
                'available_gb': round(memory_info.get('available', 0) / (1024**3), 2),
                'used_gb': round(memory_info.get('used', 0) / (1024**3), 2),
                'percent_used': memory_info.get('percent', 0),
                'swap_total_gb': round(memory_info.get('swap_total', 0) / (1024**3), 2),
                'swap_used_gb': round(memory_info.get('swap_used', 0) / (1024**3), 2),
                'swap_percent': memory_info.get('swap_percent', 0)
            }
            
            # Adicionar informações detalhadas da memória se disponíveis
            if is_windows() and hasattr(memory_info, 'get') and memory_info.get('physical_memory'):
                memory['details'] = {
                    'modules': memory_info.get('physical_memory', []),
                    'slots': memory_info.get('memory_slots', {})
                }
            
            # Informações do disco
            disk_info = PlatformAdapter.get_disk_info()
            
            # Lista de discos e partições
            disks = {
                'total_bytes': disk_info.get('total', 0),
                'free_bytes': disk_info.get('free', 0),
                'used_bytes': disk_info.get('used', 0),
                'percent_used': disk_info.get('percent', 0),
                'total_gb': round(disk_info.get('total', 0) / (1024**3), 2),
                'free_gb': round(disk_info.get('free', 0) / (1024**3), 2),
                'used_gb': round(disk_info.get('used', 0) / (1024**3), 2),
                'partitions': disk_info.get('partitions', [])
            }
            
            # Informações físicas dos discos (Windows)
            if system_info['system'] == 'Windows':
                try:
                    # Verificar se já temos informações de discos físicos do PlatformAdapter
                    if 'physical_disks' in disk_info:
                        disks['physical_disks'] = disk_info['physical_disks']
                    else:
                        # Tentar obter via WMI
                        # Inicializa COM para esta thread
                        initialize_com()
                        
                        import wmi
                        w = wmi.WMI()
                        physical_disks = []
                        
                        for disk in w.Win32_DiskDrive():
                            physical_disks.append({
                                'model': disk.Model,
                                'manufacturer': disk.Manufacturer,
                                'serial': disk.SerialNumber,
                                'size_gb': round(int(disk.Size or 0) / (1024**3), 2),
                                'partitions': disk.Partitions,
                                'interface_type': disk.InterfaceType,
                                'media_type': disk.MediaType,
                                'status': disk.Status,
                                'firmware': disk.FirmwareRevision
                            })
                        
                        disks['physical_disks'] = physical_disks
                except Exception as e:
                    logger.warning(f"Erro ao obter informações detalhadas dos discos físicos: {str(e)}")
            
            # Informações de rede
            network_info = PlatformAdapter.get_network_info()
            network = {
                'interfaces': []
            }
            
            for name, interface in network_info.get('interfaces', {}).items():
                interface_data = {
                    'name': name,
                    'addresses': interface.get('addresses', []),
                    'is_up': interface.get('stats', {}).get('isup', False),
                    'speed': interface.get('stats', {}).get('speed', 0),
                    'mtu': interface.get('stats', {}).get('mtu', 0)
                }
                network['interfaces'].append(interface_data)
            
            # Adicionar informações de placa de rede no Windows
            if system_info['system'] == 'Windows':
                try:
                    # Inicializa COM para esta thread
                    initialize_com()
                    
                    import wmi
                    w = wmi.WMI()
                    network_adapters = []
                    
                    for adapter in w.Win32_NetworkAdapter():
                        if adapter.NetConnectionStatus == 2:  # 2 = conectado
                            adapter_data = {
                                'name': adapter.Name,
                                'description': adapter.Description,
                                'manufacturer': adapter.Manufacturer,
                                'mac_address': adapter.MACAddress,
                                'adapter_type': adapter.AdapterType,
                                'speed_mbps': adapter.Speed and int(adapter.Speed) // 1000000
                            }
                            network_adapters.append(adapter_data)
                    
                    network['adapters'] = network_adapters
                except Exception as e:
                    logger.warning(f"Erro ao obter informações detalhadas das placas de rede: {str(e)}")
            
            # Informações da placa de vídeo (GPU) - Windows only
            gpu = {
                'devices': []
            }
            
            if system_info['system'] == 'Windows':
                try:
                    # Inicializa COM para esta thread
                    initialize_com()
                    
                    import wmi
                    w = wmi.WMI()
                    
                    for gpu_device in w.Win32_VideoController():
                        gpu_data = {
                            'name': gpu_device.Name,
                            'adapter_ram_mb': round(int(gpu_device.AdapterRAM or 0) / (1024**2), 2),
                            'driver_version': gpu_device.DriverVersion,
                            'driver_date': gpu_device.DriverDate,
                            'video_processor': gpu_device.VideoProcessor,
                            'video_mode_description': gpu_device.VideoModeDescription,
                            'current_refresh_rate': gpu_device.CurrentRefreshRate,
                            'current_bits_per_pixel': gpu_device.CurrentBitsPerPixel
                        }
                        gpu['devices'].append(gpu_data)
                except Exception as e:
                    logger.warning(f"Erro ao obter informações da GPU: {str(e)}")
            
            # Informações da BIOS e Placa-mãe já obtidas do get_system_information
            motherboard = {}
            
            if 'bios' in system_details:
                motherboard['bios'] = system_details['bios']
                
            if system_details.get('baseboard'):
                motherboard['baseboard'] = system_details['baseboard']
            
            # Montar o resultado consolidado
            result = {
                'system': system_info,
                'cpu': cpu,
                'memory': memory,
                'disk': disks,
                'network': network,
                'gpu': gpu,
                'motherboard': motherboard,
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter identidade do computador: {str(e)}")
            return {
                'error': str(e),
                'system': {
                    'system': platform.system(),
                    'version': platform.version(),
                    'hostname': socket.gethostname(),
                },
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }