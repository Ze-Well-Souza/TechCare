import logging
import sys
import os
import json
import shutil
import tempfile
import platform
import subprocess
import re
import psutil
from pathlib import Path
import datetime
# import winreg # Comentado para importação condicional
import uuid

# Importação condicional do winreg
if platform.system() == 'Windows':
    import winreg
else:
    winreg = None # Define winreg como None em sistemas não-Windows

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class CleanerService:
    """
    Serviço responsável por limpar, otimizar e reparar o sistema.
    Funcionalidade similar ao CCleaner Pro.
    """
    
    def __init__(self):
        """Inicializa o serviço de limpeza e otimização"""
        logger.info("Iniciando CleanerService")
        self.is_windows = platform.system() == 'Windows'
        self.temp_paths = self._get_temp_paths()
        self.browser_paths = self._get_browser_paths()
        
        # Define o diretório de dados
        self.data_dir = Path("data/maintenance")
        
        # Cria o diretório de dados se não existir
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def _get_temp_paths(self):
        """Retorna caminhos para diretórios temporários do sistema"""
        temp_paths = []
        
        if self.is_windows:
            # Diretórios temporários padrão do Windows
            temp_paths.extend([
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Temp'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp')
            ])
            
            # Adiciona diretório de arquivos temporários da lixeira
            recycle_bin = os.path.join(os.environ.get('SYSTEMDRIVE', 'C:'), '$Recycle.Bin')
            if os.path.exists(recycle_bin):
                temp_paths.append(recycle_bin)
        else:
            # Diretórios temporários padrão do Linux/macOS
            temp_paths.extend([
                '/tmp',
                '/var/tmp',
                os.path.expanduser('~/.cache')
            ])
        
        return [path for path in temp_paths if path and os.path.exists(path)]
    
    def _get_browser_paths(self):
        """Retorna caminhos para caches de navegadores"""
        browser_paths = {}
        
        if self.is_windows:
            appdata = os.environ.get('LOCALAPPDATA', '')
            
            # Chrome
            chrome_path = os.path.join(appdata, 'Google', 'Chrome', 'User Data', 'Default', 'Cache')
            if os.path.exists(chrome_path):
                browser_paths['chrome'] = {
                    'cache': chrome_path,
                    'cookies': os.path.join(appdata, 'Google', 'Chrome', 'User Data', 'Default', 'Cookies'),
                    'history': os.path.join(appdata, 'Google', 'Chrome', 'User Data', 'Default', 'History')
                }
            
            # Firefox
            firefox_path = os.path.join(os.environ.get('APPDATA', ''), 'Mozilla', 'Firefox', 'Profiles')
            if os.path.exists(firefox_path):
                for profile in os.listdir(firefox_path):
                    if profile.endswith('.default'):
                        profile_path = os.path.join(firefox_path, profile)
                        browser_paths['firefox'] = {
                            'cache': os.path.join(profile_path, 'cache2'),
                            'cookies': os.path.join(profile_path, 'cookies.sqlite'),
                            'history': os.path.join(profile_path, 'places.sqlite')
                        }
                        break
            
            # Edge
            edge_path = os.path.join(appdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache')
            if os.path.exists(edge_path):
                browser_paths['edge'] = {
                    'cache': edge_path,
                    'cookies': os.path.join(appdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'Cookies'),
                    'history': os.path.join(appdata, 'Microsoft', 'Edge', 'User Data', 'Default', 'History')
                }
        
        return browser_paths
    
    def analyze_system(self):
        """
        Analisa o sistema para identificar oportunidades de limpeza e otimização
        
        Returns:
            dict: Resultado da análise do sistema
        """
        logger.info("Analisando sistema para limpeza e otimização")
        
        result = {
            "temp_files": self._analyze_temp_files(),
            "browser_data": self._analyze_browser_data(),
            "startup_items": self._analyze_startup_items() if self.is_windows else {},
            "registry_issues": self._analyze_registry() if self.is_windows else {},
            "disk_space": self._analyze_disk_space(),
            "large_files": self._find_large_files(),
            "duplicates": [],  # Será preenchido posteriormente
            "corrupted_files": self._check_corrupted_files() if self.is_windows else {}
        }
        
        # Calcula espaço total que pode ser liberado
        total_cleanup_size = 0
        total_cleanup_size += result["temp_files"].get("total_size", 0)
        
        for browser, data in result["browser_data"].items():
            total_cleanup_size += data.get("cache_size", 0)
        
        result["total_cleanup_size"] = total_cleanup_size
        result["total_cleanup_formatted"] = self._format_size(total_cleanup_size)
        
        logger.info(f"Análise concluída. Potencial de limpeza: {result['total_cleanup_formatted']}")
        return result
    
    def _analyze_temp_files(self):
        """Analisa arquivos temporários no sistema"""
        logger.info("Analisando arquivos temporários")
        
        temp_files = {
            "paths": {},
            "total_size": 0,
            "total_files": 0
        }
        
        for temp_path in self.temp_paths:
            path_info = {
                "path": temp_path,
                "size": 0,
                "files": 0
            }
            
            try:
                for root, dirs, files in os.walk(temp_path):
                    for file in files:
                        try:
                            file_path = os.path.join(root, file)
                            file_size = os.path.getsize(file_path)
                            path_info["size"] += file_size
                            path_info["files"] += 1
                            temp_files["total_size"] += file_size
                            temp_files["total_files"] += 1
                        except (PermissionError, FileNotFoundError):
                            # Ignora arquivos que não podem ser acessados
                            pass
            except (PermissionError, OSError):
                # Ignora diretórios que não podem ser acessados
                pass
            
            path_info["formatted_size"] = self._format_size(path_info["size"])
            temp_files["paths"][temp_path] = path_info
        
        temp_files["formatted_total_size"] = self._format_size(temp_files["total_size"])
        return temp_files
    
    def _analyze_browser_data(self):
        """Analisa dados de navegadores (cache, cookies, histórico)"""
        logger.info("Analisando dados de navegadores")
        
        browser_data = {}
        
        for browser_name, paths in self.browser_paths.items():
            browser_info = {
                "cache_size": 0,
                "cookies_size": 0,
                "history_size": 0,
                "total_size": 0
            }
            
            # Analisa cache do navegador
            if "cache" in paths and os.path.exists(paths["cache"]):
                cache_size = self._get_directory_size(paths["cache"])
                browser_info["cache_size"] = cache_size
                browser_info["total_size"] += cache_size
            
            # Analisa arquivo de cookies
            if "cookies" in paths and os.path.exists(paths["cookies"]):
                cookies_size = os.path.getsize(paths["cookies"])
                browser_info["cookies_size"] = cookies_size
                browser_info["total_size"] += cookies_size
            
            # Analisa arquivo de histórico
            if "history" in paths and os.path.exists(paths["history"]):
                history_size = os.path.getsize(paths["history"])
                browser_info["history_size"] = history_size
                browser_info["total_size"] += history_size
            
            browser_info["formatted_cache_size"] = self._format_size(browser_info["cache_size"])
            browser_info["formatted_cookies_size"] = self._format_size(browser_info["cookies_size"])
            browser_info["formatted_history_size"] = self._format_size(browser_info["history_size"])
            browser_info["formatted_total_size"] = self._format_size(browser_info["total_size"])
            
            browser_data[browser_name] = browser_info
        
        return browser_data
    
    def _analyze_startup_items(self):
        """Analisa itens de inicialização do Windows"""
        logger.info("Analisando itens de inicialização")
        
        startup_items = {
            "registry": [],
            "startup_folder": [],
            "total_items": 0
        }
        
        if not self.is_windows:
            return startup_items
        
        try:
            # Verifica itens de inicialização no registro
            registry_keys = [
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
                (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\RunOnce"),
                (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\RunOnce")
            ]
            
            for hkey, key_path in registry_keys:
                try:
                    with winreg.OpenKey(hkey, key_path) as key:
                        i = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, i)
                                startup_items["registry"].append({
                                    "name": name,
                                    "command": value,
                                    "location": f"{hkey}\\{key_path}",
                                    "type": "registry"
                                })
                                startup_items["total_items"] += 1
                                i += 1
                            except WindowsError:
                                break
                except WindowsError:
                    pass
            
            # Verifica itens de inicialização na pasta Startup
            startup_folders = [
                os.path.join(os.environ.get('APPDATA', ''), r"Microsoft\Windows\Start Menu\Programs\Startup"),
                os.path.join(os.environ.get('ALLUSERSPROFILE', ''), r"Microsoft\Windows\Start Menu\Programs\Startup")
            ]
            
            for folder in startup_folders:
                if os.path.exists(folder):
                    for item in os.listdir(folder):
                        item_path = os.path.join(folder, item)
                        startup_items["startup_folder"].append({
                            "name": item,
                            "path": item_path,
                            "location": folder,
                            "type": "file" if os.path.isfile(item_path) else "folder"
                        })
                        startup_items["total_items"] += 1
        
        except Exception as e:
            logger.error(f"Erro ao analisar itens de inicialização: {str(e)}", exc_info=True)
        
        return startup_items
    
    def _analyze_registry(self):
        """Analisa problemas no registro do Windows"""
        logger.info("Analisando registro do Windows")
        
        registry_issues = {
            "invalid_shortcuts": 0,
            "obsolete_software": 0,
            "startup_entries": 0,
            "missing_shared_dlls": 0,
            "total_issues": 0
        }
        
        if not self.is_windows:
            return registry_issues
        
        # Em uma implementação real, faríamos varreduras detalhadas do registro
        # Por ora, simulamos alguns resultados típicos
        registry_issues["invalid_shortcuts"] = 12
        registry_issues["obsolete_software"] = 8
        registry_issues["startup_entries"] = 5
        registry_issues["missing_shared_dlls"] = 15
        registry_issues["total_issues"] = sum([
            registry_issues["invalid_shortcuts"],
            registry_issues["obsolete_software"],
            registry_issues["startup_entries"],
            registry_issues["missing_shared_dlls"]
        ])
        
        return registry_issues
    
    def _analyze_disk_space(self):
        """Analisa o espaço em disco disponível"""
        logger.info("Analisando espaço em disco")
        
        disk_space = {}
        
        for partition in psutil.disk_partitions():
            if not partition.mountpoint or "cdrom" in partition.opts or partition.fstype == "":
                continue
            
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disk_space[partition.device] = {
                    "mountpoint": partition.mountpoint,
                    "fstype": partition.fstype,
                    "total": usage.total,
                    "used": usage.used,
                    "free": usage.free,
                    "percent": usage.percent,
                    "formatted_total": self._format_size(usage.total),
                    "formatted_used": self._format_size(usage.used),
                    "formatted_free": self._format_size(usage.free)
                }
            except (PermissionError, FileNotFoundError):
                pass
        
        return disk_space
    
    def _find_large_files(self, min_size_mb=100, max_files=50):
        """Encontra arquivos grandes no sistema"""
        logger.info(f"Buscando arquivos maiores que {min_size_mb}MB")
        
        large_files = []
        search_paths = []
        
        # Determina caminhos para busca
        if self.is_windows:
            # Procura nas unidades disponíveis
            for partition in psutil.disk_partitions():
                if partition.mountpoint and "cdrom" not in partition.opts and partition.fstype != "":
                    search_paths.append(partition.mountpoint)
        else:
            # No Linux/macOS, procura no diretório home
            search_paths.append(os.path.expanduser("~"))
        
        min_size = min_size_mb * 1024 * 1024  # Converte MB para bytes
        
        # Por questão de eficiência, limitamos a busca a alguns diretórios
        safe_paths = [
            os.path.join(path, "Users" if self.is_windows else "home") for path in search_paths
        ]
        
        # Para cada caminho, busca arquivos grandes
        for path in safe_paths:
            if not os.path.exists(path):
                continue
                
            try:
                for root, dirs, files in os.walk(path):
                    # Pula diretórios do sistema
                    if any(skip_dir in root for skip_dir in [
                        "Windows", "Program Files", "Program Files (x86)", "$Recycle.Bin", "System Volume Information"
                    ]):
                        continue
                    
                    for file in files:
         
(Content truncated due to size limit. Use line ranges to read in chunks)