"""
Analisador de memória para o diagnóstico de sistema.
Responsável por coletar e analisar informações sobre a memória RAM.
"""

import platform
import psutil
import logging
import gc
from typing import Dict, Any, List, Optional

from app.utils.cache import cache_result
from app.services.diagnostic.utils.platform_utils import is_windows, is_linux, is_macos
from app.services.diagnostic.utils.wmi_utils import wmi_connection, get_wmi_class

logger = logging.getLogger(__name__)

class MemoryAnalyzer:
    """
    Classe responsável por analisar o desempenho e características da memória RAM.
    """
    
    def __init__(self):
        """Inicializa o analisador de memória"""
        self.problems = []
        self.score = 100
        self.has_wmi = False
        
        if is_windows():
            try:
                import wmi
                import pythoncom
                self.has_wmi = True
            except ImportError:
                logger.warning("Módulos WMI não disponíveis para análise detalhada da memória no Windows")
    
    @cache_result(expire_seconds=60)  # Cache por 1 minuto (memória é mais volátil)
    def analyze(self) -> Dict[str, Any]:
        """
        Executa a análise completa da memória.
        
        Returns:
            Dict[str, Any]: Resultados da análise da memória
        """
        logger.info("Analisando memória...")
        
        try:
            # Informações básicas disponíveis em todas as plataformas
            result = self._get_basic_memory_info()
            
            # Adiciona informações específicas da plataforma
            if is_windows():
                self._add_windows_specific_data(result)
            elif is_linux():
                self._add_linux_specific_data(result)
            elif is_macos():
                self._add_macos_specific_data(result)
            
            # Análise de processos que mais consomem memória
            result['top_processes'] = self._get_memory_consuming_processes(5)
            
            # Analisa problemas
            issues = self._analyze_issues(result)
            result['issues'] = issues
            
            # Calcula pontuação de saúde
            result['health_score'] = self._calculate_health_score(result)
            
            # Adiciona problemas encontrados
            result['problems'] = self.problems
            
            return result
        except Exception as e:
            logger.error(f"Erro ao analisar memória: {str(e)}", exc_info=True)
            return {
                'error': f"Erro ao analisar memória: {str(e)}",
                'total': 0,
                'available': 0,
                'percent': 0,
                'health_score': 0,
                'issues': [{
                    'description': f'Erro crítico na análise de memória: {str(e)}',
                    'recommendation': 'Verifique os logs para mais detalhes.',
                    'severity': 'high'
                }],
                'problems': [{
                    'category': 'memory',
                    'title': 'Erro na análise de memória',
                    'description': f'Erro crítico ao analisar memória: {str(e)}',
                    'solution': 'Verifique os logs para mais detalhes.',
                    'impact': 'high',
                    'severity': 'high'
                }]
            }
        finally:
            # Libera memória
            gc.collect()
    
    def _get_basic_memory_info(self) -> Dict[str, Any]:
        """
        Obtém informações básicas sobre a memória usando psutil.
        
        Returns:
            Dict[str, Any]: Informações básicas da memória
        """
        try:
            # Obtém informações de memória virtual
            memory = psutil.virtual_memory()
            
            # Conversão para bytes e megabytes para facilitar exibição
            total_mb = memory.total / (1024 * 1024)
            available_mb = memory.available / (1024 * 1024)
            used_mb = memory.used / (1024 * 1024)
            
            # Obtém informações de swap
            swap = psutil.swap_memory()
            swap_total_mb = swap.total / (1024 * 1024)
            swap_used_mb = swap.used / (1024 * 1024)
            
            # Resultados básicos disponíveis em todas as plataformas
            result = {
                'total': memory.total,
                'total_mb': round(total_mb, 2),
                'available': memory.available,
                'available_mb': round(available_mb, 2),
                'used': memory.used,
                'used_mb': round(used_mb, 2),
                'percent': memory.percent,
                'swap_total': swap.total,
                'swap_total_mb': round(swap_total_mb, 2),
                'swap_used': swap.used,
                'swap_used_mb': round(swap_used_mb, 2),
                'swap_percent': swap.percent
            }
            
            return result
        except Exception as e:
            logger.warning(f"Erro ao obter informações básicas de memória: {str(e)}")
            return {
                'total': 0,
                'total_mb': 0,
                'available': 0,
                'available_mb': 0,
                'used': 0,
                'used_mb': 0,
                'percent': 0,
                'swap_total': 0,
                'swap_total_mb': 0,
                'swap_used': 0,
                'swap_used_mb': 0,
                'swap_percent': 0
            }
    
    def _get_memory_consuming_processes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Obtém os processos que mais consomem memória.
        
        Args:
            limit: Número máximo de processos a retornar
            
        Returns:
            List[Dict[str, Any]]: Lista dos processos que mais consomem memória
        """
        try:
            # Lista todos os processos
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'memory_percent']):
                try:
                    # Obtém informações de memória
                    pinfo = proc.info
                    if pinfo['memory_info'] and pinfo['memory_info'].rss > 0:
                        processes.append({
                            'pid': pinfo['pid'],
                            'name': pinfo['name'],
                            'memory_mb': pinfo['memory_info'].rss / (1024 * 1024),
                            'memory_percent': pinfo['memory_percent']
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Ordena por uso de memória (do maior para o menor)
            processes.sort(key=lambda x: x['memory_mb'], reverse=True)
            
            # Retorna apenas os top N processos
            return processes[:limit]
        except Exception as e:
            logger.warning(f"Erro ao obter processos que consomem memória: {str(e)}")
            return []
    
    def _add_windows_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas de memória para Windows.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        if not self.has_wmi:
            return
            
        try:
            # Obtém informações sobre a memória física via WMI
            with wmi_connection() as wmi_conn:
                if wmi_conn:
                    try:
                        # Coleta informações detalhadas de memória física
                        physical_memories = wmi_conn.Win32_PhysicalMemory()
                        memory_devices = []
                        
                        total_capacity = 0
                        for mem in physical_memories:
                            capacity_mb = int(mem.Capacity) / (1024 * 1024) if hasattr(mem, 'Capacity') else 0
                            memory_devices.append({
                                'bank_label': mem.BankLabel if hasattr(mem, 'BankLabel') else 'Unknown',
                                'capacity_mb': capacity_mb,
                                'speed': mem.Speed if hasattr(mem, 'Speed') else None,
                                'manufacturer': mem.Manufacturer if hasattr(mem, 'Manufacturer') else 'Unknown',
                                'part_number': mem.PartNumber.strip() if hasattr(mem, 'PartNumber') else 'Unknown',
                                'device_locator': mem.DeviceLocator if hasattr(mem, 'DeviceLocator') else 'Unknown'
                            })
                            total_capacity += capacity_mb
                            
                        result['memory_devices'] = memory_devices
                        result['memory_device_count'] = len(memory_devices)
                        
                        # Verifica se há discrepância no total reportado
                        # Isso pode indicar módulos não detectados ou problemas de hardware
                        reported_total_mb = result.get('total_mb', 0)
                        if reported_total_mb > 0 and abs(total_capacity - reported_total_mb) > 1024:  # Se diferença > 1GB
                            discrepancy_pct = abs(total_capacity - reported_total_mb) / reported_total_mb * 100
                            result['memory_discrepancy'] = {
                                'reported_mb': reported_total_mb,
                                'detected_mb': total_capacity,
                                'difference_mb': abs(total_capacity - reported_total_mb),
                                'difference_percent': round(discrepancy_pct, 2)
                            }
                    except Exception as e:
                        logger.debug(f"Erro ao obter detalhes da memória física: {str(e)}")
                        
                    # Obtém informações adicionais sobre a memória virtual/paginação
                    try:
                        os_info = wmi_conn.Win32_OperatingSystem()[0]
                        result['total_virtual_mb'] = int(os_info.TotalVirtualMemorySize) / 1024 if hasattr(os_info, 'TotalVirtualMemorySize') else 0
                        result['free_virtual_mb'] = int(os_info.FreeVirtualMemory) / 1024 if hasattr(os_info, 'FreeVirtualMemory') else 0
                        result['total_visible_mb'] = int(os_info.TotalVisibleMemorySize) / 1024 if hasattr(os_info, 'TotalVisibleMemorySize') else 0
                        result['free_physical_mb'] = int(os_info.FreePhysicalMemory) / 1024 if hasattr(os_info, 'FreePhysicalMemory') else 0
                    except Exception as e:
                        logger.debug(f"Erro ao obter informações de memória virtual/paginação: {str(e)}")
                        
                    # Obtém configurações de arquivo de paginação
                    try:
                        page_files = wmi_conn.Win32_PageFileSetting()
                        if page_files:
                            page_file_data = []
                            for pf in page_files:
                                page_file_data.append({
                                    'name': pf.Name if hasattr(pf, 'Name') else 'Unknown',
                                    'initial_size_mb': pf.InitialSize if hasattr(pf, 'InitialSize') else 0,
                                    'max_size_mb': pf.MaximumSize if hasattr(pf, 'MaximumSize') else 0
                                })
                            result['page_files'] = page_file_data
                    except Exception as e:
                        logger.debug(f"Erro ao obter configurações de arquivo de paginação: {str(e)}")
        except Exception as e:
            logger.warning(f"Erro ao obter dados específicos de memória para Windows: {str(e)}")
    
    def _add_linux_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas de memória para Linux.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        try:
            # Importação tardia para evitar dependências desnecessárias
            from app.services.diagnostic.utils.linux_utils import get_memory_info
            
            # Obtém informações específicas do Linux
            linux_memory_info = get_memory_info()
            
            # Adiciona informações (se disponíveis) ao resultado
            if linux_memory_info:
                for key, value in linux_memory_info.items():
                    if key not in result:
                        result[key] = value
                        
            # Tenta obter informações detalhadas sobre os módulos de memória
            try:
                import subprocess
                # Tenta usar o comando dmidecode para obter informações (requer root)
                dmidecode_output = subprocess.check_output(
                    "command -v dmidecode >/dev/null 2>&1 && sudo dmidecode -t memory 2>/dev/null || echo ''",
                    shell=True, universal_newlines=True
                )
                
                if dmidecode_output and "Memory Device" in dmidecode_output:
                    memory_devices = []
                    current_device = {}
                    
                    for line in dmidecode_output.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                            
                        if "Memory Device" in line and line.startswith("Memory"):
                            if current_device:  # Salva dispositivo anterior
                                memory_devices.append(current_device)
                                current_device = {}
                        elif ":" in line:
                            key, value = line.split(":", 1)
                            key = key.strip()
                            value = value.strip()
                            
                            if key == "Size" and value != "No Module Installed":
                                if "MB" in value:
                                    capacity = float(value.replace("MB", "").strip())
                                elif "GB" in value:
                                    capacity = float(value.replace("GB", "").strip()) * 1024
                                else:
                                    capacity = 0
                                current_device['capacity_mb'] = capacity
                            elif key == "Manufacturer":
                                current_device['manufacturer'] = value
                            elif key == "Speed":
                                current_device['speed'] = value
                            elif key == "Part Number":
                                current_device['part_number'] = value
                            elif key == "Locator":
                                current_device['device_locator'] = value
                                
                    if current_device:  # Adiciona o último dispositivo
                        memory_devices.append(current_device)
                        
                    # Adiciona apenas se encontrou módulos válidos
                    if memory_devices:
                        result['memory_devices'] = memory_devices
                        result['memory_device_count'] = len(memory_devices)
            except Exception as e:
                logger.debug(f"Erro ao obter detalhes dos módulos de memória no Linux: {str(e)}")
        except Exception as e:
            logger.warning(f"Erro ao obter dados específicos de memória para Linux: {str(e)}")
    
    def _add_macos_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas de memória para macOS.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        try:
            # No macOS, podemos obter algumas informações via sysctl
            import subprocess
            
            # Informações de pressão de memória
            try:
                vm_stat_output = subprocess.check_output(['vm_stat'], universal_newlines=True)
                
                # Analisa saída do vm_stat
                memory_pressure = {}
                page_size = 4096  # Valor padrão
                
                for line in vm_stat_output.split('\n'):
                    if 'page size of' in line:
                        try:
                            page_size = int(line.split('page size of ')[1].split(' ')[0])
                        except:
                            pass
                    if 'Pages free:' in line:
                        try:
                            free_pages = int(line.split(':')[1].strip().rstrip('.'))
                            memory_pressure['free_mb'] = (free_pages * page_size) / (1024 * 1024)
                        except:
                            pass
                    if 'Pages active:' in line:
                        try:
                            active_pages = int(line.split(':')[1].strip().rstrip('.'))
                            memory_pressure['active_mb'] = (active_pages * page_size) / (1024 * 1024)
                        except:
                            pass
                    if 'Pages inactive:' in line:
                        try:
                            inactive_pages = int(line.split(':')[1].strip().rstrip('.'))
                            memory_pressure['inactive_mb'] = (inactive_pages * page_size) / (1024 * 1024)
                        except:
                            pass
                    if 'Pages speculative:' in line:
                        try:
                            speculative_pages = int(line.split(':')[1].strip().rstrip('.'))
                            memory_pressure['speculative_mb'] = (speculative_pages * page_size) / (1024 * 1024)
                        except:
                            pass
                    if 'Pages wired down:' in line:
                        try:
                            wired_pages = int(line.split(':')[1].strip().rstrip('.'))
                            memory_pressure['wired_mb'] = (wired_pages * page_size) / (1024 * 1024)
                        except:
                            pass
                            
                # Adiciona métricas de pressão de memória ao resultado
                if memory_pressure:
                    result['memory_pressure'] = memory_pressure
            except Exception as e:
                logger.debug(f"Erro ao obter pressão de memória no macOS: {str(e)}")
                
            # Tenta obter informações de hardware no macOS
            try:
                system_profiler_output = subprocess.check_output(
                    ['system_profiler', 'SPMemoryDataType'], 
                    universal_newlines=True
                )
                
                # Parse da saída do system_profiler
                memory_devices = []
                current_device = {}
                
                for line in system_profiler_output.split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                        
                    if "BANK" in line:
                        if current_device:
                            memory_devices.append(current_device)
                        current_device = {'bank_label': line}
                    elif ":" in line:
                        key, value = line.split(":", 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == "Size":
                            if "GB" in value:
                                capacity = float(value.replace("GB", "").strip()) * 1024
                            elif "MB" in value:
                                capacity = float(value.replace("MB", "").strip())
                            else:
                                capacity = 0
                            current_device['capacity_mb'] = capacity
                        elif key == "Type":
                            current_device['type'] = value
                        elif key == "Speed":
                            current_device['speed'] = value
                        elif key == "Manufacturer":
                            current_device['manufacturer'] = value
                        elif key == "Part Number":
                            current_device['part_number'] = value
                            
                if current_device:
                    memory_devices.append(current_device)
                    
                # Adiciona apenas se encontrou módulos válidos
                if memory_devices:
                    result['memory_devices'] = memory_devices
                    result['memory_device_count'] = len(memory_devices)
            except Exception as e:
                logger.debug(f"Erro ao obter detalhes dos módulos de memória no macOS: {str(e)}")
        except Exception as e:
            logger.warning(f"Erro ao obter dados específicos de memória para macOS: {str(e)}")
    
    def _analyze_issues(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analisa os dados de memória para identificar possíveis problemas.
        
        Args:
            data: Dados da memória coletados
            
        Returns:
            List[Dict[str, Any]]: Lista de problemas encontrados
        """
        issues = []
        
        # Verifica uso alto de memória RAM
        if data.get('percent', 0) > 90:
            issue = {
                'description': f"Uso crítico de memória RAM ({data['percent']}%)",
                'recommendation': "Feche aplicativos desnecessários ou aumente a memória física do sistema.",
                'severity': 'critical'
            }
            issues.append(issue)
            
            # Adiciona à lista de problemas gerais
            self.problems.append({
                'category': 'memory',
                'title': 'Uso crítico de memória RAM',
                'description': f"O sistema está utilizando {data['percent']}% da memória RAM disponível.",
                'solution': "Feche aplicativos desnecessários, reinicie o sistema, ou considere aumentar a memória RAM.",
                'impact': 'performance',
                'severity': 'critical'
            })
            
            # Reduz a pontuação drasticamente
            self.score -= 40
        elif data.get('percent', 0) > 80:
            issue = {
                'description': f"Uso alto de memória RAM ({data['percent']}%)",
                'recommendation': "Considere fechar aplicativos não utilizados para liberar memória.",
                'severity': 'high'
            }
            issues.append(issue)
            
            # Adiciona à lista de problemas gerais
            self.problems.append({
                'category': 'memory',
                'title': 'Uso alto de memória RAM',
                'description': f"O sistema está utilizando {data['percent']}% da memória RAM disponível.",
                'solution': "Feche aplicativos desnecessários ou em segundo plano para liberar recursos.",
                'impact': 'performance',
                'severity': 'high'
            })
            
            # Reduz a pontuação
            self.score -= 20
        elif data.get('percent', 0) > 70:
            issue = {
                'description': f"Uso moderadamente alto de memória RAM ({data['percent']}%)",
                'recommendation': "Monitore o uso de memória para evitar degradação de desempenho.",
                'severity': 'medium'
            }
            issues.append(issue)
            
            # Reduz a pontuação levemente
            self.score -= 10
        
        # Verifica uso alto de swap
        if data.get('swap_percent', 0) > 70:
            issue = {
                'description': f"Uso alto do arquivo de paginação/swap ({data['swap_percent']}%)",
                'recommendation': "O sistema está usando muito a memória virtual, o que pode degradar o desempenho.",
                'severity': 'high'
            }
            issues.append(issue)
            
            # Adiciona à lista de problemas gerais
            self.problems.append({
                'category': 'memory',
                'title': 'Uso elevado de memória virtual',
                'description': f"O sistema está usando {data['swap_percent']}% do arquivo de paginação/swap.",
                'solution': "Feche aplicativos para reduzir o uso de memória ou considere adicionar mais RAM física.",
                'impact': 'performance',
                'severity': 'high'
            })
            
            # Reduz a pontuação
            self.score -= 15
        
        # Verifica pouca RAM disponível
        available_mb = data.get('available_mb', 0)
        if available_mb < 500:  # Menos de 500 MB disponível
            issue = {
                'description': f"Memória RAM disponível muito baixa ({available_mb:.0f} MB)",
                'recommendation': "O sistema está com pouca memória livre, o que pode causar instabilidade.",
                'severity': 'critical'
            }
            issues.append(issue)
            
            # Adiciona à lista de problemas gerais
            self.problems.append({
                'category': 'memory',
                'title': 'Memória RAM disponível crítica',
                'description': f"O sistema está com apenas {available_mb:.0f} MB de memória livre.",
                'solution': "Reinicie o sistema ou feche aplicativos para liberar memória imediatamente.",
                'impact': 'stability',
                'severity': 'critical'
            })
            
            # Reduz a pontuação drasticamente
            self.score -= 30
        elif available_mb < 1000:  # Menos de 1 GB disponível
            issue = {
                'description': f"Memória RAM disponível baixa ({available_mb:.0f} MB)",
                'recommendation': "O sistema está com pouca memória livre para executar novos aplicativos.",
                'severity': 'high'
            }
            issues.append(issue)
            
            # Reduz a pontuação
            self.score -= 15
        
        # Verifica discrepância entre memória detectada e reportada (apenas Windows)
        if 'memory_discrepancy' in data:
            discrepancy = data['memory_discrepancy']
            if discrepancy['difference_percent'] > 10:  # Mais de 10% de diferença
                issue = {
                    'description': f"Discrepância na detecção de memória RAM ({discrepancy['difference_percent']}%)",
                    'recommendation': "Há uma diferença significativa entre a memória detectada e a reportada. Verifique se todos os módulos estão funcionando corretamente.",
                    'severity': 'medium'
                }
                issues.append(issue)
                
                # Adiciona à lista de problemas gerais
                self.problems.append({
                    'category': 'memory',
                    'title': 'Possível problema em módulo de memória',
                    'description': f"Foi detectada uma discrepância de {discrepancy['difference_mb']:.0f} MB entre a memória instalada e a memória disponível para o sistema.",
                    'solution': "Verifique se todos os módulos de memória estão corretamente instalados e funcionando. Considere executar um teste de memória.",
                    'impact': 'hardware',
                    'severity': 'medium'
                })
                
                # Reduz a pontuação
                self.score -= 10
        
        # Identifica processos problemáticos
        top_processes = data.get('top_processes', [])
        if top_processes and len(top_processes) > 0:
            # Verifica se algum processo está utilizando mais de 25% da memória
            for process in top_processes:
                if process.get('memory_percent', 0) > 25:
                    issue = {
                        'description': f"Processo {process['name']} (PID {process['pid']}) utilizando {process['memory_percent']:.1f}% da memória total",
                        'recommendation': f"Verifique se este processo está funcionando corretamente ou apresenta vazamento de memória.",
                        'severity': 'high'
                    }
                    issues.append(issue)
                    
                    # Adiciona à lista de problemas gerais
                    self.problems.append({
                        'category': 'memory',
                        'title': 'Processo com uso excessivo de memória',
                        'description': f"O processo {process['name']} (PID {process['pid']}) está utilizando {process['memory_mb']:.0f} MB ({process['memory_percent']:.1f}%) da memória.",
                        'solution': f"Considere reiniciar ou finalizar o processo {process['name']} se não for essencial.",
                        'impact': 'performance',
                        'severity': 'high'
                    })
                    
                    # Reduz a pontuação
                    self.score -= 15
                    
                    # Só reporta o pior processo para não sobrecarregar
                    break
        
        return issues
    
    def _calculate_health_score(self, data: Dict[str, Any]) -> int:
        """
        Calcula a pontuação de saúde da memória com base nos dados coletados.
        
        Args:
            data: Dados da memória coletados
            
        Returns:
            int: Pontuação de saúde (0-100)
        """
        # Parte da pontuação inicial de 100 e vai deduzindo conforme problemas
        score = self.score
        
        # Garante que o score esteja entre 0 e 100
        return max(0, min(100, score)) 