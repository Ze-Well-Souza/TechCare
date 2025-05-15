#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analisador de segurança para o diagnóstico de sistema.
Responsável por verificar configurações de segurança e potenciais vulnerabilidades.
"""

import logging
import platform
import gc
from typing import Dict, Any, List, Optional
import psutil
import os
import re
import datetime

from app.utils.cache import cache_result
from app.services.diagnostic.utils.platform_utils import is_windows, is_linux, is_macos, run_powershell_command
from app.services.diagnostic.utils.wmi_utils import wmi_connection, is_wmi_available

logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    """
    Classe responsável por analisar a segurança do sistema.
    Verifica configurações de firewall, antivírus, atualizações de segurança, etc.
    """
    
    def __init__(self):
        """Inicializa o analisador de segurança"""
        self.problems = []
        self.score = 100
    
    @cache_result(expire_seconds=300)
    def analyze(self) -> Dict[str, Any]:
        """
        Executa a análise completa de segurança do sistema.
        
        Returns:
            Dict[str, Any]: Resultados da análise de segurança
        """
        logger.info("Analisando segurança do sistema...")
        
        try:
            result = {
                'security_products': [],
                'firewall_status': {},
                'updates_status': {},
                'issues': []
            }
            
            # Executa análises específicas para cada plataforma
            if is_windows():
                self._analyze_windows_security(result)
            elif is_linux():
                self._analyze_linux_security(result)
            elif is_macos():
                self._analyze_macos_security(result)
            
            # Analisa problemas e calcula pontuação
            result['issues'] = self._analyze_issues(result)
            result['health_score'] = self._calculate_health_score(result)
            result['problems'] = self.problems
            
            return result
        except Exception as e:
            logger.error(f"Erro na análise de segurança: {str(e)}", exc_info=True)
            return {
                'error': f"Erro ao analisar segurança: {str(e)}",
                'security_products': [],
                'firewall_status': {'enabled': False},
                'updates_status': {'up_to_date': False},
                'health_score': 0,
                'issues': [{
                    'description': f'Erro crítico na análise de segurança: {str(e)}',
                    'recommendation': 'Verifique os logs para mais detalhes.',
                    'severity': 'high'
                }],
                'problems': [{
                    'category': 'security',
                    'title': 'Erro na análise de segurança',
                    'description': f'Erro crítico ao analisar segurança: {str(e)}',
                    'solution': 'Verifique os logs para mais detalhes.',
                    'impact': 'high',
                    'severity': 'high'
                }]
            }
        finally:
            gc.collect()
    
    def _analyze_windows_security(self, result: Dict[str, Any]) -> None:
        """
        Analisa configurações de segurança do Windows.
        
        Args:
            result: Dicionário para armazenar os resultados
        """
        try:
            # Verifica status do Windows Defender
            ps_command = "Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, IoavProtectionEnabled, AntispywareEnabled | ConvertTo-Json"
            defender_status = run_powershell_command(ps_command)
            
            if defender_status:
                try:
                    import json
                    defender_json = json.loads(defender_status)
                    result['security_products'].append({
                        'name': 'Windows Defender',
                        'type': 'antivirus',
                        'enabled': defender_json.get('AntivirusEnabled', False),
                        'real_time_protection': defender_json.get('RealTimeProtectionEnabled', False)
                    })
                    
                    if not defender_json.get('AntivirusEnabled', False):
                        self.problems.append({
                            'category': 'security',
                            'title': 'Windows Defender desativado',
                            'description': 'O Windows Defender está desativado, o que pode deixar seu sistema vulnerável.',
                            'solution': 'Ative o Windows Defender nas configurações de segurança.',
                            'impact': 'high',
                            'severity': 'high'
                        })
                        self.score -= 30
                    
                    if not defender_json.get('RealTimeProtectionEnabled', False):
                        self.problems.append({
                            'category': 'security',
                            'title': 'Proteção em tempo real desativada',
                            'description': 'A proteção em tempo real do Windows Defender está desativada.',
                            'solution': 'Ative a proteção em tempo real nas configurações do Windows Defender.',
                            'impact': 'medium',
                            'severity': 'medium'
                        })
                        self.score -= 15
                except Exception as e:
                    logger.warning(f"Erro ao analisar status do Windows Defender: {str(e)}")
            
            # Verifica status do firewall
            ps_command = "Get-NetFirewallProfile | Select-Object Name, Enabled | ConvertTo-Json"
            firewall_status = run_powershell_command(ps_command)
            
            if firewall_status:
                try:
                    import json
                    firewall_profiles = json.loads(firewall_status)
                    
                    # Certifica-se de que temos uma lista
                    if not isinstance(firewall_profiles, list):
                        firewall_profiles = [firewall_profiles]
                    
                    result['firewall_status'] = {
                        'enabled': any(profile.get('Enabled', False) for profile in firewall_profiles),
                        'profiles': {}
                    }
                    
                    for profile in firewall_profiles:
                        profile_name = profile.get('Name', 'Unknown')
                        profile_enabled = profile.get('Enabled', False)
                        result['firewall_status']['profiles'][profile_name] = profile_enabled
                    
                    if not result['firewall_status']['enabled']:
                        self.problems.append({
                            'category': 'security',
                            'title': 'Firewall do Windows desativado',
                            'description': 'O Firewall do Windows está desativado em todos os perfis.',
                            'solution': 'Ative o Firewall do Windows nas configurações de segurança.',
                            'impact': 'high',
                            'severity': 'high'
                        })
                        self.score -= 25
                except Exception as e:
                    logger.warning(f"Erro ao analisar status do Firewall: {str(e)}")
            
            # Verifica status das atualizações do Windows
            ps_command = "Get-HotFix | Sort-Object -Property InstalledOn -Descending | Select-Object -First 1 HotFixID, InstalledOn | ConvertTo-Json"
            update_status = run_powershell_command(ps_command)
            
            if update_status:
                try:
                    import json
                    update_json = json.loads(update_status)
                    
                    # Verifica se a última atualização foi instalada recentemente (nos últimos 30 dias)
                    if 'InstalledOn' in update_json:
                        installed_date_str = update_json['InstalledOn']
                        try:
                            # Verifica se é um dicionário e extrai a informação relevante, ou usa como string
                            if isinstance(installed_date_str, dict):
                                # Se for um dicionário, precisamos extrair a informação relevante
                                # Vamos tentar obter o valor da data ou uma representação em string
                                installed_date_str = str(installed_date_str.get('value', installed_date_str))
                            elif not isinstance(installed_date_str, str):
                                # Se não for string nem dicionário, converte para string
                                installed_date_str = str(installed_date_str)
                            
                            # Trata o formato especial de data do WMI/JSON: /Date(timestamp)/
                            if isinstance(installed_date_str, str) and '/Date(' in installed_date_str:
                                # Extrai o timestamp em milissegundos
                                match = re.search(r'/Date\((\d+)\)/', installed_date_str)
                                if match:
                                    timestamp_ms = int(match.group(1))
                                    installed_date = datetime.datetime.fromtimestamp(timestamp_ms / 1000)  # Converter ms para s
                                else:
                                    raise ValueError(f"Formato de data inválido: {installed_date_str}")
                            else:
                                # Converte a string de data para objeto datetime no formato padrão
                                installed_date = datetime.datetime.strptime(installed_date_str, '%d/%m/%Y') if '/' in installed_date_str else datetime.datetime.strptime(installed_date_str, '%m/%d/%Y')
                            
                            days_since_update = (datetime.datetime.now() - installed_date).days
                            
                            result['updates_status'] = {
                                'up_to_date': days_since_update <= 30,
                                'last_update': installed_date_str,
                                'days_since_update': days_since_update
                            }
                            
                            if days_since_update > 30:
                                self.problems.append({
                                    'category': 'security',
                                    'title': 'Sistema desatualizado',
                                    'description': f'O sistema não recebe atualizações há {days_since_update} dias.',
                                    'solution': 'Execute o Windows Update para instalar as atualizações mais recentes.',
                                    'impact': 'medium',
                                    'severity': 'medium'
                                })
                                self.score -= 15
                        except Exception as e:
                            logger.warning(f"Erro ao analisar data da última atualização: {str(e)}")
                except Exception as e:
                    logger.warning(f"Erro ao analisar status das atualizações: {str(e)}")
            
            # Verifica software antivírus de terceiros usando WMI
            if is_wmi_available():
                try:
                    with wmi_connection() as wmi_conn:
                        if wmi_conn:
                            try:
                                # Usamos uma abordagem mais segura para iterar
                                try:
                                    antivirus_products = list(wmi_conn.InstancesOf('AntiVirusProduct'))
                                    for product in antivirus_products:
                                        try:
                                            result['security_products'].append({
                                                'name': getattr(product, 'displayName', 'Unknown Antivirus'),
                                                'type': 'antivirus',
                                                'provider': getattr(product, 'pathToSignedProductExe', 'Unknown')
                                            })
                                        except Exception as e:
                                            logger.debug(f"Erro ao processar produto antivírus: {str(e)}")
                                except Exception as e:
                                    # Captura erro específico de "Classe inválida" - comum em muitos sistemas Windows
                                    # Tratamos isso silenciosamente, pois já detectamos o Windows Defender via PowerShell
                                    if "Classe inválida" in str(e) or "Invalid class" in str(e):
                                        logger.debug(f"Classe WMI 'AntiVirusProduct' não disponível neste sistema: {str(e)}")
                                    else:
                                        logger.debug(f"Erro ao listar produtos antivírus via WMI: {str(e)}")
                            except Exception as e:
                                logger.debug(f"Erro ao verificar produtos antivírus via WMI: {str(e)}")
                except Exception as e:
                    logger.debug(f"Erro ao verificar produtos antivírus via WMI: {str(e)}")
            
            # Se não encontramos antivírus via WMI, tentamos outros métodos
            if not any(product.get('type') == 'antivirus' for product in result['security_products']):
                try:
                    # Verificação alternativa usando o registro do Windows para software de segurança comum
                    ps_command = """
                    $avProducts = @(
                        @{Name="Avast"; Path="HKLM:\\SOFTWARE\\AVAST Software\\Avast"},
                        @{Name="AVG"; Path="HKLM:\\SOFTWARE\\AVG"},
                        @{Name="Avira"; Path="HKLM:\\SOFTWARE\\Avira"},
                        @{Name="Bitdefender"; Path="HKLM:\\SOFTWARE\\Bitdefender"},
                        @{Name="ESET"; Path="HKLM:\\SOFTWARE\\ESET"},
                        @{Name="F-Secure"; Path="HKLM:\\SOFTWARE\\F-Secure"},
                        @{Name="Kaspersky"; Path="HKLM:\\SOFTWARE\\KasperskyLab"},
                        @{Name="Malwarebytes"; Path="HKLM:\\SOFTWARE\\Malwarebytes"},
                        @{Name="McAfee"; Path="HKLM:\\SOFTWARE\\McAfee"},
                        @{Name="Norton"; Path="HKLM:\\SOFTWARE\\Norton"},
                        @{Name="Panda"; Path="HKLM:\\SOFTWARE\\Panda Security"},
                        @{Name="Trend Micro"; Path="HKLM:\\SOFTWARE\\TrendMicro"}
                    )
                    
                    $results = @()
                    foreach ($av in $avProducts) {
                        if (Test-Path $av.Path) {
                            $results += @{Name=$av.Name; Installed=$true}
                        }
                    }
                    
                    $results | ConvertTo-Json
                    """
                    av_check_result = run_powershell_command(ps_command)
                    
                    if av_check_result:
                        try:
                            import json
                            av_list = json.loads(av_check_result)
                            
                            # Certifica-se de que temos uma lista
                            if not isinstance(av_list, list):
                                av_list = [av_list]
                            
                            for av in av_list:
                                result['security_products'].append({
                                    'name': av.get('Name', 'Unknown Antivirus'),
                                    'type': 'antivirus',
                                    'installed': True
                                })
                        except Exception as e:
                            logger.debug(f"Erro ao processar resultados de verificação alternativa de antivírus: {str(e)}")
                except Exception as e:
                    logger.debug(f"Erro na verificação alternativa de antivírus: {str(e)}")
        
        except Exception as e:
            logger.error(f"Erro ao analisar segurança do Windows: {str(e)}", exc_info=True)
    
    def _analyze_linux_security(self, result: Dict[str, Any]) -> None:
        """
        Analisa configurações de segurança do Linux.
        
        Args:
            result: Dicionário para armazenar os resultados
        """
        # Implementação básica para Linux - pode ser expandida no futuro
        try:
            # Verifica se UFW está instalado e ativo (Firewall padrão do Ubuntu)
            result['firewall_status'] = {'enabled': False, 'name': 'Unknown'}
            
            try:
                ufw_status = os.popen('ufw status').read()
                if 'Status: active' in ufw_status:
                    result['firewall_status'] = {'enabled': True, 'name': 'UFW'}
                elif 'command not found' not in ufw_status:
                    result['firewall_status'] = {'enabled': False, 'name': 'UFW'}
            except:
                pass
                
            # Tenta verificar iptables
            if not result['firewall_status']['enabled']:
                try:
                    iptables_status = os.popen('iptables -L').read()
                    if iptables_status and 'command not found' not in iptables_status:
                        # Verifica se há regras definidas
                        if 'Chain INPUT (policy ACCEPT)' in iptables_status and 'ACCEPT' in iptables_status:
                            result['firewall_status'] = {'enabled': True, 'name': 'iptables'}
                except:
                    pass
            
            # Verifica se há antivírus instalados
            antivirus_check = {
                'ClamAV': 'clamscan --version',
                'Sophos': 'sophos',
                'ESET': 'esets'
            }
            
            for av_name, av_cmd in antivirus_check.items():
                try:
                    av_result = os.popen(av_cmd).read()
                    if av_result and 'command not found' not in av_result:
                        result['security_products'].append({
                            'name': av_name,
                            'type': 'antivirus',
                            'installed': True
                        })
                except:
                    pass
            
            # Verifica atualizações pendentes (método básico para distribuições baseadas em Debian)
            try:
                updates_available = os.popen('apt list --upgradable 2>/dev/null | wc -l').read().strip()
                if updates_available and updates_available.isdigit():
                    # Subtrai 1 para compensar a linha de cabeçalho
                    updates_count = max(0, int(updates_available) - 1)
                    result['updates_status'] = {
                        'up_to_date': updates_count == 0,
                        'pending_updates': updates_count
                    }
                    
                    if updates_count > 0:
                        self.problems.append({
                            'category': 'security',
                            'title': 'Sistema desatualizado',
                            'description': f'Existem {updates_count} atualizações pendentes.',
                            'solution': 'Execute "sudo apt update && sudo apt upgrade" para atualizar o sistema.',
                            'impact': 'medium',
                            'severity': 'medium'
                        })
                        self.score -= 15
                else:
                    result['updates_status'] = {'up_to_date': True, 'pending_updates': 0}
            except:
                result['updates_status'] = {'up_to_date': False, 'error': 'Não foi possível verificar atualizações'}
                
        except Exception as e:
            logger.error(f"Erro ao analisar segurança do Linux: {str(e)}", exc_info=True)
    
    def _analyze_macos_security(self, result: Dict[str, Any]) -> None:
        """
        Analisa configurações de segurança do macOS.
        
        Args:
            result: Dicionário para armazenar os resultados
        """
        # Implementação básica para macOS - pode ser expandida no futuro
        try:
            # Verifica firewall
            try:
                firewall_status = os.popen('defaults read /Library/Preferences/com.apple.alf globalstate').read().strip()
                result['firewall_status'] = {
                    'enabled': firewall_status in ['1', '2'],
                    'name': 'macOS Firewall'
                }
                
                if firewall_status == '0':
                    self.problems.append({
                        'category': 'security',
                        'title': 'Firewall do macOS desativado',
                        'description': 'O firewall do macOS está desativado.',
                        'solution': 'Ative o firewall nas preferências de segurança.',
                        'impact': 'medium',
                        'severity': 'medium'
                    })
                    self.score -= 20
            except:
                result['firewall_status'] = {'enabled': False, 'error': 'Não foi possível verificar status'}
            
            # Verifica atualizações de software
            try:
                updates_check = os.popen('softwareupdate -l').read()
                if 'No new software available' in updates_check:
                    result['updates_status'] = {'up_to_date': True}
                else:
                    pending_updates = []
                    for line in updates_check.splitlines():
                        if line.strip().startswith('*'):
                            update_name = line.strip()[1:].strip()
                            pending_updates.append(update_name)
                    
                    result['updates_status'] = {
                        'up_to_date': False,
                        'pending_updates': pending_updates
                    }
                    
                    if pending_updates:
                        self.problems.append({
                            'category': 'security',
                            'title': 'Atualizações do macOS pendentes',
                            'description': f'Existem {len(pending_updates)} atualizações pendentes.',
                            'solution': 'Abra a App Store ou Preferências do Sistema para instalar as atualizações.',
                            'impact': 'medium',
                            'severity': 'medium'
                        })
                        self.score -= 15
            except:
                result['updates_status'] = {'up_to_date': False, 'error': 'Não foi possível verificar atualizações'}
                
            # Verifica Gatekeeper (proteção contra apps não assinados)
            try:
                gatekeeper_status = os.popen('spctl --status').read().strip()
                result['gatekeeper'] = {'enabled': 'assessments enabled' in gatekeeper_status}
                
                if 'assessments disabled' in gatekeeper_status:
                    self.problems.append({
                        'category': 'security',
                        'title': 'Gatekeeper desativado',
                        'description': 'O Gatekeeper, que protege contra aplicativos não verificados, está desativado.',
                        'solution': 'Ative o Gatekeeper com o comando "sudo spctl --master-enable"',
                        'impact': 'high',
                        'severity': 'high'
                    })
                    self.score -= 25
            except:
                pass
                
        except Exception as e:
            logger.error(f"Erro ao analisar segurança do macOS: {str(e)}", exc_info=True)
    
    def _analyze_issues(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analisa problemas de segurança encontrados.
        
        Args:
            result: Dicionário com os resultados da análise
            
        Returns:
            List[Dict[str, Any]]: Lista de problemas encontrados
        """
        issues = []
        
        # Verifica se há algum antivírus
        if not result.get('security_products'):
            issues.append({
                'description': 'Nenhum software de segurança detectado',
                'recommendation': 'Instale um software antivírus ou certifique-se de que o Windows Defender está ativado.',
                'severity': 'high'
            })
        
        # Verifica firewall
        if not result.get('firewall_status', {}).get('enabled', False):
            issues.append({
                'description': 'Firewall desativado',
                'recommendation': 'Ative o firewall para proteger seu sistema contra acessos não autorizados.',
                'severity': 'high'
            })
        
        # Verifica atualizações
        if not result.get('updates_status', {}).get('up_to_date', False):
            issues.append({
                'description': 'Sistema operacional desatualizado',
                'recommendation': 'Instale as atualizações de segurança mais recentes.',
                'severity': 'medium'
            })
        
        return issues
    
    def _calculate_health_score(self, result: Dict[str, Any]) -> float:
        """
        Calcula a pontuação de saúde de segurança.
        
        Args:
            result: Dicionário com os resultados da análise
            
        Returns:
            float: Pontuação de saúde de segurança
        """
        # Usa o score calculado durante a análise
        return max(0, min(100, self.score)) 