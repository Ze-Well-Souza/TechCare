#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Analisador de drivers para o diagnóstico de sistema.
Responsável por verificar a saúde e atualização dos drivers do sistema.
"""

import logging
import platform
import gc
import os
import re
from typing import Dict, Any, List, Optional
import datetime

from app.utils.cache import cache_result
from app.services.diagnostic.utils.platform_utils import is_windows, is_linux, is_macos, run_powershell_command
from app.services.diagnostic.utils.wmi_utils import wmi_connection, is_wmi_available

logger = logging.getLogger(__name__)

class DriverAnalyzer:
    """
    Classe responsável por analisar os drivers do sistema.
    Verifica se há drivers desatualizados, problemáticos ou ausentes.
    """
    
    def __init__(self):
        """Inicializa o analisador de drivers"""
        self.problems = []
        self.score = 100
    
    @cache_result(expire_seconds=600)  # Cache por 10 minutos
    def analyze(self) -> Dict[str, Any]:
        """
        Executa a análise completa dos drivers do sistema.
        
        Returns:
            Dict[str, Any]: Resultados da análise de drivers
        """
        logger.info("Analisando drivers do sistema...")
        
        try:
            result = {
                'drivers': [],
                'outdated_count': 0,
                'problem_count': 0,
                'total_count': 0,
                'issues': []
            }
            
            # A análise de drivers é principalmente relevante para Windows
            if is_windows():
                self._analyze_windows_drivers(result)
            elif is_linux():
                self._analyze_linux_drivers(result)
            elif is_macos():
                self._analyze_macos_drivers(result)
            
            # Analisa problemas e calcula pontuação
            result['issues'] = self._analyze_issues(result)
            result['health_score'] = self._calculate_health_score(result)
            result['problems'] = self.problems
            
            return result
        except Exception as e:
            logger.error(f"Erro na análise de drivers: {str(e)}", exc_info=True)
            return {
                'error': f"Erro ao analisar drivers: {str(e)}",
                'drivers': [],
                'outdated_count': 0,
                'problem_count': 0,
                'total_count': 0,
                'health_score': 0,
                'issues': [{
                    'description': f'Erro crítico na análise de drivers: {str(e)}',
                    'recommendation': 'Verifique os logs para mais detalhes.',
                    'severity': 'high'
                }],
                'problems': [{
                    'category': 'drivers',
                    'title': 'Erro na análise de drivers',
                    'description': f'Erro crítico ao analisar drivers: {str(e)}',
                    'solution': 'Verifique os logs para mais detalhes.',
                    'impact': 'medium',
                    'severity': 'medium'
                }]
            }
        finally:
            gc.collect()
    
    def _analyze_windows_drivers(self, result: Dict[str, Any]) -> None:
        """
        Analisa os drivers no Windows usando WMI e PowerShell.
        
        Args:
            result: Dicionário para armazenar os resultados
        """
        try:
            drivers = []
            problem_count = 0
            outdated_count = 0
            
            # Verifica se o WMI está disponível
            if is_wmi_available():
                try:
                    with wmi_connection() as wmi_conn:
                        # Obtém informações de driver pelo WMI
                        win32_drivers = wmi_conn.Win32_PnPSignedDriver()
                        
                        for driver in win32_drivers:
                            if not driver.DeviceID:
                                continue
                                
                            driver_info = {
                                'name': driver.FriendlyName or driver.Description or driver.DeviceName or 'Desconhecido',
                                'device_id': driver.DeviceID,
                                'device_class': driver.DeviceClass or 'Desconhecido',
                                'manufacturer': driver.Manufacturer or 'Desconhecido',
                                'version': driver.DriverVersion or 'Desconhecido',
                                'date': self._format_driver_date(driver.DriverDate),
                                'status': 'OK'
                            }
                            
                            # Verifica se o driver está com problema (não está rodando)
                            if driver.Status and driver.Status.lower() != 'ok':
                                driver_info['status'] = 'Problem'
                                problem_count += 1
                                
                                self.problems.append({
                                    'category': 'drivers',
                                    'title': f'Problema com driver: {driver_info["name"]}',
                                    'description': f'O driver {driver_info["name"]} está com status {driver.Status}',
                                    'solution': 'Verifique o Gerenciador de Dispositivos para mais detalhes e considere reinstalar o driver.',
                                    'impact': 'medium',
                                    'severity': 'medium'
                                })
                                self.score -= 5
                            
                            # Verifica idade do driver (mais de 2 anos = desatualizado)
                            if 'date' in driver_info and driver_info['date']:
                                try:
                                    driver_date = datetime.datetime.strptime(driver_info['date'], '%Y-%m-%d')
                                    age_days = (datetime.datetime.now() - driver_date).days
                                    driver_info['age_days'] = age_days
                                    
                                    if age_days > 730:  # Mais de 2 anos
                                        driver_info['outdated'] = True
                                        outdated_count += 1
                                        
                                        # Adiciona problema apenas para drivers importantes
                                        important_classes = ['Display', 'Net', 'DiskDrive', 'Processor', 'SCSIAdapter', 'HDC']
                                        if driver_info['device_class'] in important_classes:
                                            self.problems.append({
                                                'category': 'drivers',
                                                'title': f'Driver desatualizado: {driver_info["name"]}',
                                                'description': f'O driver {driver_info["name"]} está desatualizado (mais de 2 anos).',
                                                'solution': 'Considere atualizar este driver através do site do fabricante ou do Gerenciador de Dispositivos.',
                                                'impact': 'low',
                                                'severity': 'low'
                                            })
                                            self.score -= 2
                                except Exception as e:
                                    logger.debug(f"Erro ao processar data do driver: {str(e)}")
                            
                            drivers.append(driver_info)
                except Exception as e:
                    logger.warning(f"Erro ao obter drivers via WMI: {str(e)}")
            
            # Se não conseguirmos obter drivers via WMI, tentamos via PowerShell
            if not drivers:
                try:
                    # Comando PowerShell para obter informações de drivers
                    ps_command = "Get-WmiObject Win32_PnPSignedDriver | Select-Object DeviceName, DeviceClass, Manufacturer, DriverVersion, DriverDate | ConvertTo-Json"
                    driver_output = run_powershell_command(ps_command)
                    
                    if driver_output:
                        import json
                        try:
                            ps_drivers = json.loads(driver_output)
                            
                            # Certifica-se de que temos uma lista
                            if not isinstance(ps_drivers, list):
                                ps_drivers = [ps_drivers]
                            
                            for driver in ps_drivers:
                                if not driver.get('DeviceName'):
                                    continue
                                    
                                driver_info = {
                                    'name': driver.get('DeviceName', 'Desconhecido'),
                                    'device_class': driver.get('DeviceClass', 'Desconhecido'),
                                    'manufacturer': driver.get('Manufacturer', 'Desconhecido'),
                                    'version': driver.get('DriverVersion', 'Desconhecido'),
                                    'date': self._format_driver_date(driver.get('DriverDate')),
                                    'status': 'OK'
                                }
                                
                                # Verifica idade do driver como acima
                                if 'date' in driver_info and driver_info['date']:
                                    try:
                                        driver_date = datetime.datetime.strptime(driver_info['date'], '%Y-%m-%d')
                                        age_days = (datetime.datetime.now() - driver_date).days
                                        driver_info['age_days'] = age_days
                                        
                                        if age_days > 730:  # Mais de 2 anos
                                            driver_info['outdated'] = True
                                            outdated_count += 1
                                    except Exception as e:
                                        logger.debug(f"Erro ao processar data do driver: {str(e)}")
                                
                                drivers.append(driver_info)
                        except Exception as e:
                            logger.warning(f"Erro ao processar JSON dos drivers: {str(e)}")
                except Exception as e:
                    logger.warning(f"Erro ao obter drivers via PowerShell: {str(e)}")
            
            # Tenta obter problemas no gerenciador de dispositivos
            if not problem_count:
                try:
                    # Comando PowerShell para verificar dispositivos com problemas
                    ps_command = "Get-WmiObject Win32_PnPEntity | Where-Object {$_.ConfigManagerErrorCode -ne 0} | Select-Object Name, ConfigManagerErrorCode | ConvertTo-Json"
                    problem_output = run_powershell_command(ps_command)
                    
                    if problem_output and problem_output.strip() not in ['[]', 'null']:
                        import json
                        try:
                            problem_devices = json.loads(problem_output)
                            
                            # Certifica-se de que temos uma lista
                            if not isinstance(problem_devices, list):
                                problem_devices = [problem_devices]
                            
                            for device in problem_devices:
                                device_name = device.get('Name', 'Dispositivo desconhecido')
                                error_code = device.get('ConfigManagerErrorCode', 0)
                                
                                # Adiciona ou atualiza o driver na lista
                                found = False
                                for driver in drivers:
                                    if driver['name'] == device_name:
                                        driver['status'] = 'Problem'
                                        driver['error_code'] = error_code
                                        found = True
                                        break
                                
                                if not found:
                                    drivers.append({
                                        'name': device_name,
                                        'status': 'Problem',
                                        'error_code': error_code,
                                        'device_class': 'Desconhecido',
                                        'manufacturer': 'Desconhecido',
                                        'version': 'Desconhecido'
                                    })
                                
                                problem_count += 1
                                
                                # Adiciona problema
                                self.problems.append({
                                    'category': 'drivers',
                                    'title': f'Problema com dispositivo: {device_name}',
                                    'description': f'O dispositivo "{device_name}" está com erro (código {error_code}).',
                                    'solution': 'Verifique o Gerenciador de Dispositivos para mais detalhes e considere reinstalar o driver.',
                                    'impact': 'medium',
                                    'severity': 'medium'
                                })
                                self.score -= 5
                        except Exception as e:
                            logger.warning(f"Erro ao processar JSON de dispositivos com problema: {str(e)}")
                except Exception as e:
                    logger.warning(f"Erro ao verificar dispositivos com problema: {str(e)}")
            
            # Atualiza o resultado
            result['drivers'] = drivers
            result['total_count'] = len(drivers)
            result['problem_count'] = problem_count
            result['outdated_count'] = outdated_count
            
        except Exception as e:
            logger.error(f"Erro ao analisar drivers do Windows: {str(e)}", exc_info=True)
    
    def _format_driver_date(self, date_str: Optional[str]) -> Optional[str]:
        """
        Formata a data do driver para o formato YYYY-MM-DD.
        
        Args:
            date_str: String de data no formato WMI
            
        Returns:
            String de data formatada ou None
        """
        if not date_str:
            return None
            
        try:
            # O formato WMI é algo como '20200515000000.000000+000'
            # Extraímos apenas a parte relevante
            if isinstance(date_str, str) and len(date_str) >= 8:
                # Tenta extrair usando expressão regular
                match = re.search(r'(\d{4})(\d{2})(\d{2})', date_str)
                if match:
                    year, month, day = match.groups()
                    return f"{year}-{month}-{day}"
            return None
        except Exception as e:
            logger.debug(f"Erro ao formatar data do driver: {str(e)}")
            return None
    
    def _analyze_linux_drivers(self, result: Dict[str, Any]) -> None:
        """
        Analisa módulos do kernel no Linux (equivalente a drivers).
        
        Args:
            result: Dicionário para armazenar os resultados
        """
        try:
            drivers = []
            
            # No Linux, os "drivers" são módulos do kernel
            try:
                # Lista todos os módulos do kernel carregados
                lsmod_output = os.popen('lsmod').read()
                
                # Parseia a saída
                lines = lsmod_output.strip().split('\n')[1:]  # Pula a primeira linha (cabeçalho)
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 1:
                        module_name = parts[0]
                        
                        # Tenta obter mais informações sobre o módulo
                        modinfo_output = os.popen(f'modinfo {module_name} 2>/dev/null').read()
                        
                        module_info = {
                            'name': module_name,
                            'status': 'OK',
                            'device_class': 'Kernel Module'
                        }
                        
                        # Extrai informações adicionais
                        for info_line in modinfo_output.strip().split('\n'):
                            if ':' in info_line:
                                key, value = info_line.split(':', 1)
                                key, value = key.strip(), value.strip()
                                
                                if key == 'description':
                                    module_info['description'] = value
                                elif key == 'author':
                                    module_info['manufacturer'] = value
                                elif key == 'version':
                                    module_info['version'] = value
                                elif key == 'license':
                                    module_info['license'] = value
                        
                        drivers.append(module_info)
            except Exception as e:
                logger.warning(f"Erro ao analisar módulos do kernel: {str(e)}")
            
            # Verifica problemas com dispositivos
            try:
                dmesg_output = os.popen('dmesg | grep -i "fail\\|error\\|warn" | grep -i "driver\\|module" | tail -20').read()
                
                if dmesg_output:
                    for line in dmesg_output.split('\n'):
                        if line.strip():
                            # Busca nomes de módulos/drivers na linha
                            module_match = re.search(r'module\s+([a-zA-Z0-9_]+)', line, re.IGNORECASE)
                            driver_match = re.search(r'driver\s+([a-zA-Z0-9_]+)', line, re.IGNORECASE)
                            
                            module_name = None
                            if module_match:
                                module_name = module_match.group(1)
                            elif driver_match:
                                module_name = driver_match.group(1)
                            
                            if module_name:
                                # Verifica se já existe na lista
                                found = False
                                for driver in drivers:
                                    if driver['name'] == module_name:
                                        driver['status'] = 'Problem'
                                        driver['error'] = line.strip()
                                        found = True
                                        break
                                
                                if not found:
                                    drivers.append({
                                        'name': module_name,
                                        'status': 'Problem',
                                        'error': line.strip(),
                                        'device_class': 'Kernel Module'
                                    })
                                
                                # Adiciona problema
                                self.problems.append({
                                    'category': 'drivers',
                                    'title': f'Problema com módulo do kernel: {module_name}',
                                    'description': f'O módulo {module_name} apresenta erros: {line.strip()}',
                                    'solution': 'Verifique os logs do sistema (dmesg) para mais detalhes.',
                                    'impact': 'medium',
                                    'severity': 'medium'
                                })
                                self.score -= 5
            except Exception as e:
                logger.warning(f"Erro ao verificar problemas com módulos do kernel: {str(e)}")
            
            # Atualiza o resultado
            result['drivers'] = drivers
            result['total_count'] = len(drivers)
            result['problem_count'] = sum(1 for driver in drivers if driver.get('status') == 'Problem')
            
        except Exception as e:
            logger.error(f"Erro ao analisar drivers do Linux: {str(e)}", exc_info=True)
    
    def _analyze_macos_drivers(self, result: Dict[str, Any]) -> None:
        """
        Analisa kexts (kernel extensions) no macOS.
        
        Args:
            result: Dicionário para armazenar os resultados
        """
        try:
            drivers = []
            
            # No macOS, os "drivers" são kernel extensions (kexts)
            try:
                # Lista todas as kexts carregadas
                kextstat_output = os.popen('kextstat').read()
                
                # Parseia a saída
                lines = kextstat_output.strip().split('\n')[1:]  # Pula a primeira linha (cabeçalho)
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 6:
                        kext_name = parts[5]
                        
                        # Extrai a versão
                        version_match = re.search(r'\((.+)\)', line)
                        version = version_match.group(1) if version_match else 'Desconhecido'
                        
                        kext_info = {
                            'name': kext_name,
                            'version': version,
                            'status': 'OK',
                            'device_class': 'Kernel Extension'
                        }
                        
                        drivers.append(kext_info)
            except Exception as e:
                logger.warning(f"Erro ao analisar extensões do kernel: {str(e)}")
            
            # Verifica problemas com kexts
            try:
                log_output = os.popen('log show --predicate "subsystem == \\"com.apple.kext\\"" --style compact --last 1h | grep -i "fail\\|error\\|warn"').read()
                
                if log_output:
                    for line in log_output.split('\n'):
                        if line.strip():
                            # Busca nomes de kexts na linha
                            kext_match = re.search(r'com\.([a-zA-Z0-9.]+)', line)
                            
                            if kext_match:
                                kext_name = kext_match.group(0)
                                
                                # Verifica se já existe na lista
                                found = False
                                for driver in drivers:
                                    if kext_name in driver['name']:
                                        driver['status'] = 'Problem'
                                        driver['error'] = line.strip()
                                        found = True
                                        break
                                
                                if not found:
                                    drivers.append({
                                        'name': kext_name,
                                        'status': 'Problem',
                                        'error': line.strip(),
                                        'device_class': 'Kernel Extension'
                                    })
                                
                                # Adiciona problema
                                self.problems.append({
                                    'category': 'drivers',
                                    'title': f'Problema com extensão do kernel: {kext_name}',
                                    'description': f'A extensão {kext_name} apresenta erros.',
                                    'solution': 'Verifique os logs do sistema para mais detalhes.',
                                    'impact': 'medium',
                                    'severity': 'medium'
                                })
                                self.score -= 5
            except Exception as e:
                logger.warning(f"Erro ao verificar problemas com extensões do kernel: {str(e)}")
            
            # Atualiza o resultado
            result['drivers'] = drivers
            result['total_count'] = len(drivers)
            result['problem_count'] = sum(1 for driver in drivers if driver.get('status') == 'Problem')
            
        except Exception as e:
            logger.error(f"Erro ao analisar drivers do macOS: {str(e)}", exc_info=True)
    
    def _analyze_issues(self, result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analisa problemas nos drivers.
        
        Args:
            result: Dicionário com os resultados da análise
            
        Returns:
            List[Dict[str, Any]]: Lista de problemas encontrados
        """
        issues = []
        
        # Verifica se há drivers com problemas
        if result.get('problem_count', 0) > 0:
            issues.append({
                'description': f'Encontrados {result["problem_count"]} drivers com problemas',
                'recommendation': 'Verifique o Gerenciador de Dispositivos e considere reinstalar os drivers problemáticos.',
                'severity': 'high'
            })
        
        # Verifica se há drivers desatualizados
        if result.get('outdated_count', 0) > 0:
            issues.append({
                'description': f'Encontrados {result["outdated_count"]} drivers potencialmente desatualizados',
                'recommendation': 'Considere atualizar os drivers através do site do fabricante ou do Gerenciador de Dispositivos.',
                'severity': 'medium'
            })
        
        return issues
    
    def _calculate_health_score(self, result: Dict[str, Any]) -> float:
        """
        Calcula a pontuação de saúde dos drivers.
        
        Args:
            result: Dicionário com os resultados da análise
            
        Returns:
            float: Pontuação de saúde dos drivers
        """
        # Usa o score calculado durante a análise
        return max(0, min(100, self.score)) 