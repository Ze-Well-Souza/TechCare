"""
Analisador de CPU para o diagnóstico de sistema.
Responsável por coletar e analisar informações sobre a CPU.
"""

import platform
import psutil
import logging
import time
import re
from typing import Dict, Any, List, Optional
import gc

from app.utils.cache import cache_result
from app.services.diagnostic.utils.platform_utils import is_windows, is_linux, is_macos
from app.services.diagnostic.utils.wmi_utils import wmi_connection, get_wmi_class

logger = logging.getLogger(__name__)

class CPUAnalyzer:
    """
    Classe responsável por analisar o desempenho e características da CPU.
    """
    
    def __init__(self):
        """Inicializa o analisador de CPU"""
        self.problems = []
        self.score = 100
        self.has_wmi = False
        
        if is_windows():
            try:
                import wmi
                import pythoncom
                self.has_wmi = True
            except ImportError:
                logger.warning("Módulos WMI não disponíveis para análise detalhada da CPU no Windows")
    
    @cache_result(expire_seconds=300)
    def analyze(self) -> Dict[str, Any]:
        """
        Executa a análise completa da CPU.
        
        Returns:
            Dict[str, Any]: Resultados da análise da CPU
        """
        logger.info("Analisando CPU...")
        
        try:
            # Inicia com os dados básicos disponíveis em todas as plataformas
            result = self._get_basic_cpu_info()
            
            # Adiciona informações de desempenho
            performance_data = self._get_performance_data()
            result.update(performance_data)
            
            # Adiciona informações específicas da plataforma
            if is_windows():
                self._add_windows_specific_data(result)
            elif is_linux():
                self._add_linux_specific_data(result)
            elif is_macos():
                self._add_macos_specific_data(result)
            
            # Analisa problemas
            issues = self._analyze_issues(result)
            result['issues'] = issues
            
            # Calcula pontuação de saúde
            result['health_score'] = self._calculate_health_score(result)
            
            # Adiciona problemas encontrados
            result['problems'] = self.problems
            
            return result
        except Exception as e:
            logger.error(f"Erro ao analisar CPU: {str(e)}", exc_info=True)
            return {
                'error': f"Erro ao analisar CPU: {str(e)}",
                'vendor': 'Desconhecido',
                'model': 'Desconhecido',
                'cores': 0,
                'threads': 0,
                'usage': 0,
                'health_score': 0,
                'issues': [{
                    'description': f'Erro crítico na análise de CPU: {str(e)}',
                    'recommendation': 'Verifique os logs para mais detalhes.',
                    'severity': 'high'
                }],
                'problems': [{
                    'category': 'cpu',
                    'title': 'Erro na análise de CPU',
                    'description': f'Erro crítico ao analisar CPU: {str(e)}',
                    'solution': 'Verifique os logs para mais detalhes.',
                    'impact': 'high',
                    'severity': 'high'
                }]
            }
        finally:
            # Libera memória
            gc.collect()
    
    def _get_basic_cpu_info(self) -> Dict[str, Any]:
        """
        Obtém informações básicas sobre a CPU usando psutil.
        
        Returns:
            Dict[str, Any]: Informações básicas da CPU
        """
        # Dados básicos disponíveis em todas as plataformas
        info = {
            'vendor': 'Desconhecido',
            'model': platform.processor() or 'Desconhecido',
            'cores': psutil.cpu_count(logical=False) or 0,
            'threads': psutil.cpu_count(logical=True) or 0,
            'architecture': platform.architecture()[0],
            'temperature': None
        }
        
        # Tenta obter informações adicionais usando cpuinfo se disponível
        try:
            import cpuinfo
            cpu_info = cpuinfo.get_cpu_info()
            
            info['vendor'] = cpu_info.get('vendor_id', info['vendor'])
            info['model'] = cpu_info.get('brand_raw', info['model'])
            info['frequency'] = cpu_info.get('hz_actual_friendly', 'Desconhecido')
            info['bits'] = cpu_info.get('bits', 64 if '64' in platform.architecture()[0] else 32)
        except ImportError:
            logger.debug("Módulo cpuinfo não disponível, usando informações básicas")
        except Exception as e:
            logger.warning(f"Erro ao obter informações detalhadas da CPU: {str(e)}")
        
        return info
    
    def _get_performance_data(self) -> Dict[str, Any]:
        """
        Obtém dados de desempenho da CPU.
        
        Returns:
            Dict[str, Any]: Dados de desempenho da CPU
        """
        # Coleta utilização da CPU
        try:
            # Amostragem para estabilizar a leitura
            cpu_usage_samples = []
            for _ in range(3):
                cpu_usage_samples.append(psutil.cpu_percent(interval=0.5))
            
            # Média das amostras
            cpu_usage = sum(cpu_usage_samples) / len(cpu_usage_samples)
            
            # Coleta informações por núcleo
            per_core_usage = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # Verifica se há núcleos sobrecarregados (acima de 90%)
            overloaded_cores = [i for i, usage in enumerate(per_core_usage) if usage > 90]
            
            # Frequência atual, se disponível
            freq = psutil.cpu_freq()
            current_freq = freq.current if freq else None
            
            # Dados de carga
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            
            result = {
                'usage': round(cpu_usage, 1),
                'per_core_usage': per_core_usage,
                'overloaded_cores': overloaded_cores,
                'current_frequency': current_freq,
                'load_average': load_avg
            }
            
            return result
        except Exception as e:
            logger.warning(f"Erro ao obter dados de desempenho da CPU: {str(e)}")
            return {
                'usage': 0,
                'per_core_usage': [],
                'overloaded_cores': [],
                'current_frequency': None,
                'load_average': None
            }
    
    def _add_windows_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas de CPU para Windows.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        if not self.has_wmi:
            return
            
        try:
            # Obtém temperatura e informações detalhadas via WMI
            with wmi_connection("root\\wmi") as wmi_conn:
                if wmi_conn:
                    # Tenta obter temperatura
                    try:
                        temperature_info = wmi_conn.MSAcpi_ThermalZoneTemperature()[0]
                        # Converte decikelvin para Celsius
                        temperature = (temperature_info.CurrentTemperature / 10.0) - 273.15
                        result['temperature'] = round(temperature, 1)
                    except Exception:
                        pass
                        
            # Obtém informações de processador via WMI
            with wmi_connection() as wmi_conn:
                if wmi_conn:
                    # Informações detalhadas do processador
                    try:
                        processors = wmi_conn.Win32_Processor()
                        if processors:
                            processor = processors[0]
                            result['model'] = processor.Name
                            result['vendor'] = processor.Manufacturer
                            result['socket'] = processor.SocketDesignation
                            result['max_clock_speed'] = processor.MaxClockSpeed
                            result['virtualization'] = processor.VirtualizationFirmwareEnabled
                            result['l2_cache_size'] = processor.L2CacheSize
                            result['l3_cache_size'] = processor.L3CacheSize
                    except Exception as e:
                        logger.debug(f"Erro ao obter informações detalhadas do processador: {str(e)}")
        except Exception as e:
            logger.warning(f"Erro ao obter dados específicos de CPU para Windows: {str(e)}")
    
    def _add_linux_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas de CPU para Linux.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        try:
            # Temperatura da CPU no Linux
            from app.services.diagnostic.utils.linux_utils import get_cpu_temperature
            result['temperature'] = get_cpu_temperature()
            
            # Tenta ler informações adicionais do /proc/cpuinfo
            if not result.get('model') or result['model'] == 'Desconhecido':
                try:
                    with open('/proc/cpuinfo', 'r') as f:
                        cpuinfo = f.read()
                        
                    # Modelo
                    model_matches = re.findall(r'model name\s+:\s+(.*)', cpuinfo)
                    if model_matches:
                        result['model'] = model_matches[0]
                        
                    # Vendor
                    vendor_matches = re.findall(r'vendor_id\s+:\s+(.*)', cpuinfo)
                    if vendor_matches:
                        result['vendor'] = vendor_matches[0]
                        
                    # Cache
                    cache_matches = re.findall(r'cache size\s+:\s+(.*)', cpuinfo)
                    if cache_matches:
                        result['cache_size'] = cache_matches[0]
                except Exception:
                    pass
        except Exception as e:
            logger.warning(f"Erro ao obter dados específicos de CPU para Linux: {str(e)}")
    
    def _add_macos_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas de CPU para macOS.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        try:
            # No macOS, podemos obter algumas informações via sysctl
            import subprocess
            
            # Modelo
            try:
                model = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.brand_string']).decode().strip()
                if model:
                    result['model'] = model
            except Exception:
                pass
                
            # Vendor
            try:
                vendor = subprocess.check_output(['sysctl', '-n', 'machdep.cpu.vendor']).decode().strip()
                if vendor:
                    result['vendor'] = vendor
            except Exception:
                pass
                
            # Frequência
            try:
                freq = subprocess.check_output(['sysctl', '-n', 'hw.cpufrequency']).decode().strip()
                if freq:
                    result['frequency'] = f"{int(freq) / 1000000000:.2f} GHz"
            except Exception:
                pass
                
            # Cache
            try:
                l2_cache = subprocess.check_output(['sysctl', '-n', 'hw.l2cachesize']).decode().strip()
                if l2_cache:
                    result['l2_cache_size'] = int(l2_cache) // 1024  # KB
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Erro ao obter dados específicos de CPU para macOS: {str(e)}")
    
    def _analyze_issues(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analisa os dados de CPU para identificar possíveis problemas.
        
        Args:
            data: Dados da CPU coletados
            
        Returns:
            List[Dict[str, Any]]: Lista de problemas encontrados
        """
        issues = []
        
        # Verifica alta utilização da CPU
        if data.get('usage', 0) > 85:
            issue = {
                'description': f"Alta utilização da CPU ({data['usage']}%)",
                'recommendation': "Verifique quais processos estão consumindo mais recursos e considere encerrá-los.",
                'severity': 'high'
            }
            issues.append(issue)
            
            # Adiciona à lista de problemas gerais
            self.problems.append({
                'category': 'cpu',
                'title': 'Alta utilização da CPU',
                'description': f"A CPU está operando com utilização muito alta ({data['usage']}%).",
                'solution': "Encerre processos desnecessários ou aplicativos em segundo plano que possam estar consumindo muitos recursos.",
                'impact': 'performance',
                'severity': 'high'
            })
            
            # Reduz a pontuação
            self.score -= 20
        elif data.get('usage', 0) > 70:
            issue = {
                'description': f"Utilização moderadamente alta da CPU ({data['usage']}%)",
                'recommendation': "Monitore quais processos estão consumindo mais recursos.",
                'severity': 'medium'
            }
            issues.append(issue)
            
            # Adiciona à lista de problemas gerais
            self.problems.append({
                'category': 'cpu',
                'title': 'Utilização moderadamente alta da CPU',
                'description': f"A CPU está operando com utilização elevada ({data['usage']}%).",
                'solution': "Considere encerrar processos não essenciais para liberar recursos.",
                'impact': 'performance',
                'severity': 'medium'
            })
            
            # Reduz a pontuação
            self.score -= 10
        
        # Verifica núcleos sobrecarregados
        if data.get('overloaded_cores', []):
            core_list = ', '.join([str(core) for core in data.get('overloaded_cores', [])])
            issue = {
                'description': f"Núcleos sobrecarregados: {core_list}",
                'recommendation': "Verifique se algum aplicativo está utilizando excessivamente núcleos específicos.",
                'severity': 'medium'
            }
            issues.append(issue)
            
            # Reduz a pontuação
            self.score -= 5
        
        # Verifica temperatura (se disponível)
        if data.get('temperature') is not None:
            temp = data.get('temperature')
            if temp > 85:
                issue = {
                    'description': f"Temperatura crítica da CPU: {temp}°C",
                    'recommendation': "Verifique o sistema de refrigeração do computador imediatamente. A CPU pode estar em risco de danos por superaquecimento.",
                    'severity': 'critical'
                }
                issues.append(issue)
                
                # Adiciona à lista de problemas gerais
                self.problems.append({
                    'category': 'cpu',
                    'title': 'Temperatura crítica da CPU',
                    'description': f"A CPU está operando em temperatura perigosamente alta ({temp}°C).",
                    'solution': "Verifique se o sistema de refrigeração está funcionando corretamente. Limpe os ventiladores e dissipadores de calor se necessário.",
                    'impact': 'hardware',
                    'severity': 'critical'
                })
                
                # Reduz a pontuação drasticamente
                self.score -= 40
            elif temp > 75:
                issue = {
                    'description': f"Temperatura alta da CPU: {temp}°C",
                    'recommendation': "Verifique o sistema de refrigeração do computador. A CPU está operando em temperatura elevada.",
                    'severity': 'high'
                }
                issues.append(issue)
                
                # Adiciona à lista de problemas gerais
                self.problems.append({
                    'category': 'cpu',
                    'title': 'Temperatura alta da CPU',
                    'description': f"A CPU está operando em temperatura elevada ({temp}°C).",
                    'solution': "Verifique se o sistema de refrigeração está funcionando corretamente e se há poeira acumulada.",
                    'impact': 'hardware',
                    'severity': 'high'
                })
                
                # Reduz a pontuação
                self.score -= 15
            elif temp > 65:
                issue = {
                    'description': f"Temperatura moderadamente alta da CPU: {temp}°C",
                    'recommendation': "Monitore a temperatura da CPU. Considere limpar o sistema de refrigeração se persistir.",
                    'severity': 'medium'
                }
                issues.append(issue)
                
                # Reduz a pontuação
                self.score -= 5
        
        return issues
    
    def _calculate_health_score(self, data: Dict[str, Any]) -> int:
        """
        Calcula a pontuação de saúde da CPU com base nos dados coletados.
        
        Args:
            data: Dados da CPU coletados
            
        Returns:
            int: Pontuação de saúde (0-100)
        """
        # Parte da pontuação inicial de 100 e vai deduzindo conforme problemas
        score = self.score
        
        # Garante que o score esteja entre 0 e 100
        return max(0, min(100, score)) 