"""
Analisador de programas de inicialização do sistema.
Responsável por coletar e analisar informações sobre programas que iniciam automaticamente com o sistema.
"""

import os
import logging
import time
from typing import Dict, Any, List, Optional
import gc

from app.utils.cache import cache_result
from app.services.diagnostic.utils.platform_utils import is_windows, is_linux, is_macos

logger = logging.getLogger(__name__)

class StartupAnalyzer:
    """
    Classe responsável por analisar os programas de inicialização do sistema.
    Identifica programas que iniciam automaticamente com o sistema e avalia seu impacto.
    """
    
    def __init__(self):
        """Inicializa o analisador de inicialização"""
        self.problems = []
        self.score = 100
    
    @cache_result(expire_seconds=300)
    def analyze(self) -> Dict[str, Any]:
        """
        Executa a análise completa dos programas de inicialização.
        
        Returns:
            Dict[str, Any]: Resultados da análise de inicialização
        """
        logger.info("Analisando programas de inicialização")
        
        try:
            # Inicializa o resultado base
            result = {
                'items': [],
                'count': 0,
                'health_score': 100,
                'issues': []
            }
            
            # Análise específica por sistema operacional
            if is_windows():
                self._analyze_windows_startup(result)
            elif is_linux():
                self._analyze_linux_startup(result)
            elif is_macos():
                self._analyze_macos_startup(result)
            else:
                logger.info("Sistema operacional não suportado para análise de inicialização")
                return {
                    'items': [],
                    'count': 0,
                    'error': 'Sistema operacional não suportado',
                    'health_score': 0,
                    'issues': []
                }
            
            # Atualiza a contagem de itens
            result['count'] = len(result['items'])
            
            # Avalia os problemas e calcula pontuação de saúde
            self._evaluate_startup_items(result)
            
            # Adiciona problemas encontrados
            result['issues'] = self.problems
            result['health_score'] = self.score
            
            logger.info(f"Análise de programas de inicialização concluída. Encontrados {result['count']} itens.")
            return result
            
        except Exception as e:
            logger.error(f"Erro ao analisar programas de inicialização: {str(e)}", exc_info=True)
            return {
                'items': [],
                'count': 0,
                'error': f"Erro ao analisar inicialização: {str(e)}",
                'health_score': 0,
                'issues': [{
                    'description': f'Erro na análise de inicialização: {str(e)}',
                    'recommendation': 'Verifique os logs para mais detalhes.',
                    'severity': 'high'
                }]
            }
        finally:
            # Libera memória
            gc.collect()
    
    def _analyze_windows_startup(self, result: Dict[str, Any]) -> None:
        """
        Analisa programas de inicialização no Windows.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        try:
            import winreg
            
            startup_locations = [
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce",
                r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run",
                r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunOnce"
            ]
            
            startup_items = []
            
            # Verifica no registro do Windows (HKLM)
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
                                'location': f"HKLM\\{location}",
                                'type': 'registry'
                            })
                            i += 1
                        except WindowsError:
                            break
                    
                    winreg.CloseKey(reg)
                except WindowsError:
                    continue
            
            # Verifica no registro do Windows (HKCU)
            for location in startup_locations:
                try:
                    reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, location)
                    
                    i = 0
                    while True:
                        try:
                            name, value, _ = winreg.EnumValue(reg, i)
                            startup_items.append({
                                'name': name,
                                'command': value,
                                'location': f"HKCU\\{location}",
                                'type': 'registry'
                            })
                            i += 1
                        except WindowsError:
                            break
                    
                    winreg.CloseKey(reg)
                except WindowsError:
                    continue
            
            # Verifica nas pastas de inicialização
            startup_folders = [
                os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup"),
                os.path.join(os.environ.get("ALLUSERSPROFILE", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
            ]
            
            for folder in startup_folders:
                if os.path.exists(folder):
                    for file in os.listdir(folder):
                        file_path = os.path.join(folder, file)
                        if os.path.isfile(file_path) and (file.endswith('.lnk') or file.endswith('.url')):
                            startup_items.append({
                                'name': file,
                                'command': file_path,
                                'location': folder,
                                'type': 'folder'
                            })
            
            # Adiciona informação sobre serviços de inicialização
            try:
                import subprocess
                import json
                
                # Executa o comando PowerShell para obter serviços de inicialização
                powershell_cmd = "Get-Service | Where-Object {$_.StartType -eq 'Automatic'} | Select-Object Name, DisplayName, Status | ConvertTo-Json"
                process = subprocess.Popen(['powershell', '-Command', powershell_cmd], 
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0 and stdout.strip():
                    try:
                        services = json.loads(stdout)
                        # Garante que o resultado seja uma lista, mesmo para um único serviço
                        if not isinstance(services, list):
                            services = [services]
                            
                        for service in services:
                            startup_items.append({
                                'name': service.get('DisplayName', service.get('Name', 'Serviço Desconhecido')),
                                'command': f"Service: {service.get('Name', 'Unknown')}",
                                'location': 'Windows Services',
                                'type': 'service',
                                'status': service.get('Status', 'Unknown')
                            })
                    except json.JSONDecodeError:
                        logger.warning("Erro ao decodificar JSON dos serviços Windows.")
            except Exception as e:
                logger.warning(f"Erro ao obter serviços de inicialização: {str(e)}")
            
            # Atualiza o resultado
            result['items'] = startup_items
            
            # Verifica se há itens de inicialização de alto impacto
            high_impact_items = self._identify_high_impact_startup_items(startup_items)
            if high_impact_items:
                result['high_impact_items'] = high_impact_items
            
        except Exception as e:
            logger.error(f"Erro ao analisar inicialização do Windows: {str(e)}", exc_info=True)
            raise
    
    def _analyze_linux_startup(self, result: Dict[str, Any]) -> None:
        """
        Analisa programas de inicialização no Linux.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        startup_items = []
        
        try:
            # Verifica os serviços systemd
            import subprocess
            
            try:
                # Lista serviços habilitados
                process = subprocess.Popen(['systemctl', 'list-unit-files', '--state=enabled', '--type=service', '--no-legend'],
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0:
                    for line in stdout.strip().split('\n'):
                        if line:
                            parts = line.split()
                            if parts:
                                service_name = parts[0]
                                if service_name.endswith('.service'):
                                    service_name = service_name[:-8]  # Remove o sufixo .service
                                
                                startup_items.append({
                                    'name': service_name,
                                    'command': f"systemd service: {service_name}",
                                    'location': '/etc/systemd/system',
                                    'type': 'systemd'
                                })
            except Exception as e:
                logger.warning(f"Erro ao obter serviços systemd: {str(e)}")
            
            # Verifica arquivos .desktop em autostart
            autostart_dirs = [
                os.path.expanduser('~/.config/autostart'),
                '/etc/xdg/autostart'
            ]
            
            for directory in autostart_dirs:
                if os.path.exists(directory):
                    for file in os.listdir(directory):
                        if file.endswith('.desktop'):
                            file_path = os.path.join(directory, file)
                            
                            # Lê o arquivo .desktop para extrair informações
                            name = file[:-8]  # Remove .desktop
                            command = ''
                            
                            try:
                                with open(file_path, 'r') as f:
                                    for line in f:
                                        if line.startswith('Name='):
                                            name = line[5:].strip()
                                        elif line.startswith('Exec='):
                                            command = line[5:].strip()
                            except Exception:
                                pass
                            
                            startup_items.append({
                                'name': name,
                                'command': command or file_path,
                                'location': directory,
                                'type': 'desktop'
                            })
            
            # Verifica entradas em rc.local
            rc_local_path = '/etc/rc.local'
            if os.path.exists(rc_local_path) and os.access(rc_local_path, os.X_OK):
                try:
                    with open(rc_local_path, 'r') as f:
                        content = f.read()
                    
                    # Adiciona o arquivo inteiro como uma entrada
                    startup_items.append({
                        'name': 'rc.local',
                        'command': content,
                        'location': rc_local_path,
                        'type': 'script'
                    })
                except Exception as e:
                    logger.warning(f"Erro ao ler rc.local: {str(e)}")
            
            # Atualiza o resultado
            result['items'] = startup_items
            
        except Exception as e:
            logger.error(f"Erro ao analisar inicialização do Linux: {str(e)}", exc_info=True)
            raise
    
    def _analyze_macos_startup(self, result: Dict[str, Any]) -> None:
        """
        Analisa programas de inicialização no macOS.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        startup_items = []
        
        try:
            # Verifica os itens de login
            login_items_dir = os.path.expanduser('~/Library/LaunchAgents')
            system_items_dirs = [
                '/Library/LaunchAgents',
                '/Library/LaunchDaemons',
                '/System/Library/LaunchAgents',
                '/System/Library/LaunchDaemons'
            ]
            
            # Função auxiliar para processar arquivos plist
            def process_plist_dir(directory, item_type):
                if os.path.exists(directory):
                    for file in os.listdir(directory):
                        if file.endswith('.plist'):
                            file_path = os.path.join(directory, file)
                            name = file[:-6]  # Remove .plist
                            
                            startup_items.append({
                                'name': name,
                                'command': file_path,
                                'location': directory,
                                'type': item_type
                            })
            
            # Processa diretórios de itens de inicialização
            process_plist_dir(login_items_dir, 'user_agent')
            for directory in system_items_dirs:
                process_plist_dir(directory, 'system_agent' if 'Agent' in directory else 'daemon')
            
            # Verifica itens de login via API do macOS
            try:
                import subprocess
                
                # Executa o comando para obter itens de login
                osascript_cmd = 'osascript -e \'tell application "System Events" to get the name of every login item\''
                process = subprocess.Popen(osascript_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                stdout, stderr = process.communicate()
                
                if process.returncode == 0 and stdout.strip():
                    for item in stdout.strip().split(', '):
                        startup_items.append({
                            'name': item,
                            'command': f"Login Item: {item}",
                            'location': 'System Login Items',
                            'type': 'login_item'
                        })
            except Exception as e:
                logger.warning(f"Erro ao obter itens de login do macOS: {str(e)}")
            
            # Atualiza o resultado
            result['items'] = startup_items
            
        except Exception as e:
            logger.error(f"Erro ao analisar inicialização do macOS: {str(e)}", exc_info=True)
            raise
    
    def _evaluate_startup_items(self, result: Dict[str, Any]) -> None:
        """
        Avalia o impacto dos programas de inicialização e identifica problemas.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        items = result.get('items', [])
        
        # Avalia com base na quantidade
        if len(items) > 15:
            self.problems.append({
                'description': f'Excesso de programas na inicialização ({len(items)} itens)',
                'recommendation': 'Desative programas desnecessários na inicialização para melhorar o tempo de boot.',
                'severity': 'high'
            })
            self.score -= 15
        elif len(items) > 8:
            self.problems.append({
                'description': f'Muitos programas na inicialização ({len(items)} itens)',
                'recommendation': 'Considere desativar programas não essenciais na inicialização.',
                'severity': 'medium'
            })
            self.score -= 8
        
        # Avalia serviços duplicados ou redundantes
        if is_windows():
            duplicate_items = self._find_duplicate_startup_items(items)
            if duplicate_items:
                self.problems.append({
                    'description': f'Itens de inicialização duplicados ou redundantes ({len(duplicate_items)} itens)',
                    'recommendation': 'Remova itens redundantes para otimizar a inicialização.',
                    'severity': 'medium'
                })
                self.score -= 5
                result['duplicate_items'] = duplicate_items
        
        # Avalia itens de alto impacto
        high_impact_items = result.get('high_impact_items', [])
        if high_impact_items and len(high_impact_items) > 3:
            self.problems.append({
                'description': f'Vários programas de alto impacto na inicialização ({len(high_impact_items)} itens)',
                'recommendation': 'Avalie a necessidade de iniciar automaticamente programas que consomem muitos recursos.',
                'severity': 'high'
            })
            self.score -= 10
    
    def _find_duplicate_startup_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Encontra itens de inicialização duplicados ou redundantes.
        
        Args:
            items: Lista de itens de inicialização
            
        Returns:
            List[Dict[str, Any]]: Lista de itens duplicados
        """
        # Mapeia comandos para identificar duplicatas
        command_map = {}
        duplicates = []
        
        for item in items:
            cmd = item.get('command', '').lower()
            # Remove parâmetros para comparação mais precisa
            base_cmd = cmd.split(' ')[0] if ' ' in cmd else cmd
            
            if base_cmd in command_map:
                # Marca o item atual como duplicata
                duplicates.append(item)
                # Adiciona o item original se ainda não estiver na lista de duplicatas
                if command_map[base_cmd] not in duplicates:
                    duplicates.append(command_map[base_cmd])
            else:
                command_map[base_cmd] = item
        
        return duplicates
    
    def _identify_high_impact_startup_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Identifica itens de inicialização com alto impacto no desempenho.
        
        Args:
            items: Lista de itens de inicialização
            
        Returns:
            List[Dict[str, Any]]: Lista de itens de alto impacto
        """
        high_impact_keywords = [
            'update', 'sync', 'cloud', 'adobe', 'teams', 'skype', 'steam',
            'epic', 'nvidia', 'amd catalyst', 'antivirus', 'scanner',
            'helper', 'assistant', 'daemon', 'torrent', 'download'
        ]
        
        high_impact_items = []
        
        for item in items:
            name = item.get('name', '').lower()
            cmd = item.get('command', '').lower()
            
            # Verifica se o nome ou comando contém palavras-chave de alto impacto
            if any(keyword in name or keyword in cmd for keyword in high_impact_keywords):
                high_impact_items.append(item)
        
        return high_impact_items 