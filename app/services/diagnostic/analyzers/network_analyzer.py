#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analisador de rede para o diagnóstico de sistema.
Responsável por coletar e analisar informações sobre conectividade e interfaces de rede.
"""

import platform
import psutil
import logging
import socket
import gc
from typing import Dict, Any, List, Optional
import time

from app.utils.cache import cache_result
from app.services.diagnostic.utils.platform_utils import is_windows, is_linux, is_macos, run_powershell_command
from app.services.diagnostic.utils.wmi_utils import wmi_connection, get_wmi_class, is_wmi_available

logger = logging.getLogger(__name__)

class NetworkAnalyzer:
    """
    Classe responsável por analisar o desempenho e características da conectividade de rede.
    """
    
    def __init__(self):
        """Inicializa o analisador de rede"""
        self.problems = []
        self.score = 100
        self.has_wmi = False
        
        if is_windows():
            try:
                import wmi
                import pythoncom
                self.has_wmi = True
            except ImportError:
                logger.warning("Módulos WMI não disponíveis para análise detalhada da rede no Windows")
    
    @cache_result(expire_seconds=180)
    def analyze(self) -> Dict[str, Any]:
        """
        Executa a análise completa da rede.
        
        Returns:
            Dict[str, Any]: Resultados da análise da rede
        """
        logger.info("Analisando rede...")
        
        try:
            # Inicia com os dados básicos disponíveis em todas as plataformas
            result = self._get_basic_network_info()
            
            # Adiciona informações específicas da plataforma
            if is_windows():
                self._add_windows_specific_data(result)
            elif is_linux():
                self._add_linux_specific_data(result)
            elif is_macos():
                self._add_macos_specific_data(result)
            
            # Testa a conectividade com a internet
            result['connectivity'] = self._test_connectivity()
            
            # Analisa problemas
            issues = self._analyze_issues(result)
            result['issues'] = issues
            
            # Calcula pontuação de saúde
            result['health_score'] = self._calculate_health_score(result)
            
            # Adiciona problemas encontrados
            result['problems'] = self.problems
            
            return result
        except Exception as e:
            logger.error(f"Erro ao analisar rede: {str(e)}", exc_info=True)
            return {
                'error': f"Erro ao analisar rede: {str(e)}",
                'interfaces': [],
                'connectivity': {'status': 'unknown'},
                'health_score': 0,
                'issues': [{
                    'description': f'Erro crítico na análise de rede: {str(e)}',
                    'recommendation': 'Verifique os logs para mais detalhes.',
                    'severity': 'high'
                }],
                'problems': [{
                    'category': 'network',
                    'title': 'Erro na análise de rede',
                    'description': f'Erro crítico ao analisar rede: {str(e)}',
                    'solution': 'Verifique os logs para mais detalhes.',
                    'impact': 'high',
                    'severity': 'high'
                }]
            }
        finally:
            # Libera memória
            gc.collect()
    
    def _get_basic_network_info(self) -> Dict[str, Any]:
        """
        Obtém informações básicas sobre a rede usando psutil.
        
        Returns:
            Dict[str, Any]: Informações básicas da rede
        """
        try:
            # Obtém informações sobre as interfaces de rede
            net_if_addrs = psutil.net_if_addrs()
            net_if_stats = psutil.net_if_stats()
            
            interfaces = []
            
            for if_name, addrs in net_if_addrs.items():
                # Ignora interfaces de loopback e virtuais em alguns casos
                if if_name == 'lo' or if_name.startswith('veth') or if_name.startswith('docker'):
                    continue
                    
                # Obtém estatísticas da interface
                if_stats = net_if_stats.get(if_name, None)
                
                # Inicializa informações da interface
                interface_info = {
                    'name': if_name,
                    'addresses': [],
                    'is_up': if_stats.isup if if_stats else False,
                    'speed_mb': if_stats.speed if if_stats else 0,
                    'mtu': if_stats.mtu if if_stats else 0,
                    'duplex': if_stats.duplex if if_stats else '',
                    'is_running': getattr(if_stats, 'isrunning', True) if if_stats else False,
                    'type': self._determine_interface_type(if_name)
                }
                
                # Adiciona endereços IP
                for addr in addrs:
                    addr_info = {
                        'family': addr.family,
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'broadcast': addr.broadcast,
                        'ptp': addr.ptp
                    }
                    
                    # Identifica tipo de endereço (IPv4, IPv6, MAC)
                    try:
                        # Família na forma numérica (2=IPv4, 23/17=IPv6, 1=MAC)
                        if addr.family == socket.AF_INET:  # IPv4
                            addr_info['type'] = 'ipv4'
                        elif addr.family == socket.AF_INET6:  # IPv6
                            addr_info['type'] = 'ipv6'
                            # Remove parte de escopo do endereço IPv6 se presente
                            if '%' in addr.address:
                                addr_info['address'] = addr.address.split('%')[0]
                        elif addr.family in [1, 17]:  # MAC (pode variar entre plataformas)
                            addr_info['type'] = 'mac'
                            interface_info['mac_address'] = addr.address
                    except Exception:
                        addr_info['type'] = 'unknown'
                    
                    interface_info['addresses'].append(addr_info)
                
                # Extrai IPv4 principal para referência rápida
                for addr in interface_info['addresses']:
                    if addr.get('type') == 'ipv4':
                        interface_info['ipv4_address'] = addr.get('address')
                        interface_info['ipv4_netmask'] = addr.get('netmask')
                        break
                
                interfaces.append(interface_info)
            
            # Obtém estatísticas de IO de rede
            try:
                net_io_counters = psutil.net_io_counters(pernic=True)
                for interface in interfaces:
                    if_name = interface['name']
                    if if_name in net_io_counters:
                        io_stats = net_io_counters[if_name]
                        
                        # Converte para MB para facilitar exibição
                        bytes_sent_mb = io_stats.bytes_sent / (1024 * 1024)
                        bytes_recv_mb = io_stats.bytes_recv / (1024 * 1024)
                        
                        interface['io_stats'] = {
                            'bytes_sent': io_stats.bytes_sent,
                            'bytes_sent_mb': round(bytes_sent_mb, 2),
                            'bytes_recv': io_stats.bytes_recv,
                            'bytes_recv_mb': round(bytes_recv_mb, 2),
                            'packets_sent': io_stats.packets_sent,
                            'packets_recv': io_stats.packets_recv,
                            'errin': io_stats.errin,
                            'errout': io_stats.errout,
                            'dropin': io_stats.dropin,
                            'dropout': io_stats.dropout
                        }
            except Exception as e:
                logger.debug(f"Erro ao obter estatísticas de IO de rede: {str(e)}")
            
            # Obtém conexões de rede ativas (limitado a 100 para evitar sobrecarga)
            try:
                connections = []
                for conn in list(psutil.net_connections())[:100]:
                    conn_info = {
                        'fd': conn.fd,
                        'family': conn.family,
                        'type': conn.type,
                        'laddr': {'ip': conn.laddr.ip, 'port': conn.laddr.port} if conn.laddr else None,
                        'raddr': {'ip': conn.raddr.ip, 'port': conn.raddr.port} if conn.raddr else None,
                        'status': conn.status,
                        'pid': conn.pid
                    }
                    connections.append(conn_info)
            except (psutil.AccessDenied, PermissionError):
                logger.warning("Acesso negado ao tentar obter conexões de rede. Execute com privilégios elevados.")
                connections = []
            except Exception as e:
                logger.debug(f"Erro ao obter conexões de rede: {str(e)}")
                connections = []
            
            return {
                'hostname': socket.gethostname(),
                'interfaces': interfaces,
                'connections': connections
            }
            
        except Exception as e:
            logger.warning(f"Erro ao obter informações básicas de rede: {str(e)}")
            return {
                'hostname': socket.gethostname(),
                'interfaces': [],
                'connections': []
            }
    
    def _determine_interface_type(self, if_name: str) -> str:
        """
        Determina o tipo de interface de rede baseado no nome.
        
        Args:
            if_name: Nome da interface
            
        Returns:
            str: Tipo da interface (ethernet, wifi, etc.)
        """
        if_name_lower = if_name.lower()
        
        # Interfaces Ethernet
        if any(prefix in if_name_lower for prefix in ['eth', 'en', 'em', 'eno', 'enp', 'e']):
            return 'ethernet'
        
        # Interfaces Wi-Fi
        if any(prefix in if_name_lower for prefix in ['wlan', 'wifi', 'wl', 'wi', 'w']):
            return 'wifi'
        
        # Interfaces Bluetooth
        if 'bt' in if_name_lower or 'blue' in if_name_lower:
            return 'bluetooth'
        
        # Interfaces virtuais
        if any(prefix in if_name_lower for prefix in ['vir', 'virt', 'tap', 'tun']):
            return 'virtual'
        
        # Interfaces celulares
        if any(prefix in if_name_lower for prefix in ['wwan', 'cell', 'mobile', 'ppp']):
            return 'cellular'
        
        # Windows possui nomes diferentes
        if 'wireless' in if_name_lower or 'wi-fi' in if_name_lower:
            return 'wifi'
        
        if 'ethernet' in if_name_lower or 'local area connection' in if_name_lower:
            return 'ethernet'
        
        # Desconhecido
        return 'unknown'
    
    def _add_windows_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas do Windows à análise de rede.
        
        Args:
            result: Dicionário com os resultados da análise básica
        """
        try:
            # Verifica se o WMI está disponível
            if not is_wmi_available():
                logger.warning("WMI não disponível para análise detalhada de rede no Windows")
                return
                
            # Obtém informações detalhadas pelo WMI
            with wmi_connection() as wmi_conn:
                if not wmi_conn:
                    logger.warning("Não foi possível estabelecer conexão WMI")
                    return
                    
                # Obtém adaptadores de rede
                network_adapters = wmi_conn.Win32_NetworkAdapter()
                network_configs = wmi_conn.Win32_NetworkAdapterConfiguration()
                
                # Cria mapa de configurações por índice
                config_map = {}
                for config in network_configs:
                    config_map[config.Index] = config
                
                # Processa e combina informações
                for adapter in network_adapters:
                    # Ignora adapters desabilitados e virtuais
                    if adapter.NetConnectionStatus != 2:  # 2 = Connected
                        continue
                        
                    # Procura a interface correspondente nos resultados básicos
                    found = False
                    for interface in result.get('interfaces', []):
                        # Tenta encontrar correspondência por nome ou endereço MAC
                        adapter_name = adapter.Name or adapter.NetConnectionID or ''
                        if (interface.get('name') == adapter_name or 
                            ('PhysicalAdapter' in dir(adapter) and adapter.PhysicalAdapter and
                             'mac_address' in interface and 
                             interface['mac_address'].lower() == adapter.MACAddress.lower())):
                            
                            # Adiciona as informações específicas do Windows
                            interface['manufacturer'] = adapter.Manufacturer or 'Desconhecido'
                            interface['description'] = adapter.Description or 'Desconhecido'
                            interface['connection_id'] = adapter.NetConnectionID or ''
                            interface['adapter_type'] = adapter.AdapterType or 'Desconhecido'
                            
                            # Adiciona a configuração do adaptador
                            config = config_map.get(adapter.Index)
                            if config:
                                if config.IPEnabled:
                                    if config.DefaultIPGateway:
                                        interface['gateway'] = config.DefaultIPGateway[0]
                                    
                                    if config.DNSServerSearchOrder:
                                        interface['dns_servers'] = list(config.DNSServerSearchOrder)
                                    
                                    if config.DHCPEnabled:
                                        interface['dhcp_enabled'] = True
                                        if config.DHCPServer:
                                            interface['dhcp_server'] = config.DHCPServer
                            
                            # Ajusta o tipo de interface se temos mais informações
                            if adapter.AdapterType:
                                adapter_type = adapter.AdapterType.lower()
                                if 'wireless' in adapter_type or 'wi-fi' in adapter_type:
                                    interface['type'] = 'wifi'
                                elif 'ethernet' in adapter_type:
                                    interface['type'] = 'ethernet'
                                elif 'bluetooth' in adapter_type:
                                    interface['type'] = 'bluetooth'
                                
                            found = True
                            break
                    
                    # Se não encontrou interface correspondente, adiciona como uma nova
                    if not found and adapter.NetConnectionID:
                        # Obtém a configuração deste adaptador
                        config = config_map.get(adapter.Index)
                        
                        # Cria nova entrada para este adaptador
                        interface_info = {
                            'name': adapter.NetConnectionID,
                            'description': adapter.Description or 'Desconhecido',
                            'manufacturer': adapter.Manufacturer or 'Desconhecido',
                            'mac_address': adapter.MACAddress if 'MACAddress' in dir(adapter) else '',
                            'type': self._determine_interface_type(adapter.NetConnectionID or adapter.Name),
                            'is_up': adapter.NetConnectionStatus == 2,  # 2 = Connected
                            'addresses': []
                        }
                        
                        # Adiciona endereços IP se estiver configurado
                        if config and config.IPEnabled:
                            # Adiciona IPv4
                            if config.IPAddress:
                                for i, addr in enumerate(config.IPAddress):
                                    # Determina se é IPv4 (simplificação)
                                    if '.' in addr:
                                        interface_info['addresses'].append({
                                            'type': 'ipv4',
                                            'address': addr,
                                            'netmask': config.IPSubnet[i] if config.IPSubnet and i < len(config.IPSubnet) else None
                                        })
                                        interface_info['ipv4_address'] = addr
                                        if config.IPSubnet and i < len(config.IPSubnet):
                                            interface_info['ipv4_netmask'] = config.IPSubnet[i]
                                    else:
                                        interface_info['addresses'].append({
                                            'type': 'ipv6',
                                            'address': addr,
                                            'netmask': config.IPSubnet[i] if config.IPSubnet and i < len(config.IPSubnet) else None
                                        })
                            
                            # Adiciona gateway
                            if config.DefaultIPGateway:
                                interface_info['gateway'] = config.DefaultIPGateway[0]
                                
                            # Adiciona servidores DNS
                            if config.DNSServerSearchOrder:
                                interface_info['dns_servers'] = list(config.DNSServerSearchOrder)
                                
                            # Adiciona informações DHCP
                            if config.DHCPEnabled:
                                interface_info['dhcp_enabled'] = True
                                if config.DHCPServer:
                                    interface_info['dhcp_server'] = config.DHCPServer
                        
                        # Adiciona à lista de interfaces
                        result['interfaces'].append(interface_info)
            
            # Adiciona informações de velocidade de conexão usando PowerShell para interfaces WiFi
            try:
                for interface in result.get('interfaces', []):
                    if interface.get('type') == 'wifi' and interface.get('is_up'):
                        # Usa PowerShell para obter informações detalhadas de WiFi
                        ps_command = "(Get-NetAdapter | Where-Object {$_.Name -eq '" + interface['name'] + "'} | Get-NetConnectionProfile).Name"
                        network_name = run_powershell_command(ps_command)
                        
                        if network_name:
                            interface['wifi_network'] = network_name.strip()
                        
                        # Tenta obter força do sinal WiFi
                        ps_command = "(netsh wlan show interfaces) | Select-String -Pattern 'Signal'"
                        signal_output = run_powershell_command(ps_command)
                        
                        if signal_output:
                            # Extrai a porcentagem da força do sinal
                            # Formato esperado: "Signal                : 90%"
                            parts = signal_output.strip().split(':')
                            if len(parts) > 1:
                                try:
                                    signal_str = parts[1].strip().replace('%', '')
                                    interface['wifi_signal'] = int(signal_str)
                                except (ValueError, IndexError):
                                    pass
            except Exception as e:
                logger.debug(f"Erro ao obter informações detalhadas de WiFi: {str(e)}")
                
        except Exception as e:
            logger.warning(f"Erro ao adicionar informações específicas do Windows: {str(e)}")
    
    def _add_linux_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas do Linux à análise de rede.
        
        Args:
            result: Dicionário com os resultados da análise básica
        """
    
    def _add_macos_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas do macOS à análise de rede.
        
        Args:
            result: Dicionário com os resultados da análise básica
        """
    
    def _test_connectivity(self) -> Dict[str, Any]:
        """
        Testa a conectividade com a internet.
        
        Returns:
            Dict[str, Any]: Resultado do teste de conectividade
        """
        try:
            # Usa um timeout mais curto para evitar travamentos
            timeout = 2
            start_time = time.time()
            
            # Testa conectividade com múltiplos destinos para maior confiabilidade
            targets = [
                ('8.8.8.8', 53),  # Google DNS
                ('1.1.1.1', 53),   # Cloudflare DNS
                ('208.67.222.222', 53)  # OpenDNS
            ]
            
            for target_ip, target_port in targets:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    sock.settimeout(timeout)
                    
                    # Tenta conexão
                    sock.connect((target_ip, target_port))
                    connected_ip = sock.getsockname()[0]
                    sock.close()
                    
                    # Calcula latência
                    latency = (time.time() - start_time) * 1000
                    
                    # Conexão bem-sucedida
                    return {
                        'status': 'connected',
                        'latency': round(latency, 2),
                        'target': target_ip,
                        'local_ip': connected_ip
                    }
                except (socket.timeout, socket.error):
                    # Continua para o próximo alvo se este falhar
                    continue
                finally:
                    try:
                        sock.close()
                    except:
                        pass
            
            # Se chegou aqui, nenhum dos alvos respondeu
            return {
                'status': 'disconnected',
                'latency': None,
                'message': 'Nenhum dos servidores DNS respondeu'
            }
        
        except Exception as e:
            logger.error(f"Erro ao testar conectividade: {str(e)}", exc_info=True)
            # Retorna status desconhecido, mas não impede a continuação da análise
            return {
                'status': 'unknown',
                'latency': None,
                'error': str(e)
            }
    
    def _analyze_issues(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analisa problemas na rede.
        
        Args:
            result: Dicionário com os resultados da análise
            
        Returns:
            List[Dict[str, Any]]: Lista de problemas encontrados
        """
        issues = []
        
        # Verifica problemas de conectividade
        if result['connectivity']['status'] == 'disconnected':
            issues.append({
                'description': 'Conexão com a internet perdida',
                'recommendation': 'Verifique a conexão com a internet e tente novamente mais tarde.',
                'severity': 'high'
            })
        
        # Verifica problemas de latência
        if result['connectivity']['latency'] is None:
            issues.append({
                'description': 'Latência elevada ao acessar a internet',
                'recommendation': 'Verifique a qualidade da conexão com a internet.',
                'severity': 'medium'
            })
        
        return issues
    
    def _calculate_health_score(self, result: Dict[str, Any]) -> float:
        """
        Calcula a pontuação de saúde da rede.
        
        Args:
            result: Dicionário com os resultados da análise
            
        Returns:
            float: Pontuação de saúde da rede
        """
        score = 100
        
        # Verifica problemas de conectividade
        if result['connectivity']['status'] == 'disconnected':
            score -= 50
        
        # Verifica problemas de latência
        if result['connectivity']['latency'] is None:
            score -= 25
        
        return score 