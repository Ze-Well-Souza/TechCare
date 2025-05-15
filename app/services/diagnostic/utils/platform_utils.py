"""
Utilitários para detecção de plataforma e sistema operacional.
Fornece funções para identificar o sistema operacional atual e suas características.
"""

import platform
import sys
import os
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_platform_info() -> Dict[str, Any]:
    """
    Obtém informações detalhadas sobre a plataforma.
    
    Returns:
        Dict[str, Any]: Dicionário com informações da plataforma
    """
    info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version(),
        'python_implementation': platform.python_implementation(),
        'python_compiler': platform.python_compiler(),
        'is_64bit': sys.maxsize > 2**32
    }
    
    # Adiciona informações específicas baseadas no sistema
    if is_windows():
        import winreg
        try:
            # Tenta obter a edição do Windows
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
                info['edition'] = winreg.QueryValueEx(key, "EditionID")[0]
                info['product_name'] = winreg.QueryValueEx(key, "ProductName")[0]
        except Exception as e:
            logger.debug(f"Erro ao obter detalhes específicos do Windows: {str(e)}")
    
    elif is_linux():
        try:
            # Tenta obter informações de distribuição Linux
            if hasattr(platform, 'freedesktop_os_release'):
                # Python 3.10+
                os_release = platform.freedesktop_os_release()
                info['distro'] = os_release.get('NAME', 'Unknown')
                info['distro_version'] = os_release.get('VERSION_ID', 'Unknown')
            else:
                # Versões anteriores do Python
                import distro
                info['distro'] = distro.name()
                info['distro_version'] = distro.version()
        except ImportError:
            # Fallback se o módulo distro não estiver disponível
            import subprocess
            try:
                # Tenta ler /etc/os-release
                with open('/etc/os-release', 'r') as f:
                    os_release = {}
                    for line in f:
                        if '=' in line:
                            key, value = line.rstrip().split('=', 1)
                            os_release[key] = value.strip('"\'')
                
                info['distro'] = os_release.get('NAME', 'Unknown')
                info['distro_version'] = os_release.get('VERSION_ID', 'Unknown')
            except Exception as e:
                logger.debug(f"Erro ao obter detalhes de distribuição Linux: {str(e)}")
                
    elif is_macos():
        try:
            # Tenta obter informações específicas do macOS
            from subprocess import Popen, PIPE
            process = Popen(['sw_vers'], stdout=PIPE)
            output = process.communicate()[0].decode('utf-8')
            
            for line in output.splitlines():
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower().replace(' ', '_')
                    value = value.strip()
                    
                    if key == 'productversion':
                        info['macos_version'] = value
                    elif key == 'buildversion':
                        info['macos_build'] = value
        except Exception as e:
            logger.debug(f"Erro ao obter detalhes específicos do macOS: {str(e)}")
    
    return info

def is_windows() -> bool:
    """
    Verifica se o sistema operacional é Windows.
    
    Returns:
        bool: True se for Windows, False caso contrário
    """
    return platform.system().lower() == 'windows'

def is_linux() -> bool:
    """
    Verifica se o sistema operacional é Linux.
    
    Returns:
        bool: True se for Linux, False caso contrário
    """
    return platform.system().lower() == 'linux'

def is_macos() -> bool:
    """
    Verifica se o sistema operacional é macOS.
    
    Returns:
        bool: True se for macOS, False caso contrário
    """
    return platform.system().lower() == 'darwin'

def is_test_environment() -> bool:
    """
    Verifica se está sendo executado em um ambiente de teste.
    
    Returns:
        bool: True se estiver em ambiente de teste, False caso contrário
    """
    # Verifica se está sendo executado em pytest ou unittest
    return (
        'pytest' in sys.modules or 
        'unittest' in sys.modules or
        'PYTEST_CURRENT_TEST' in os.environ or
        hasattr(sys, '_called_from_test')
    )

def is_development_environment() -> bool:
    """
    Verifica se está sendo executado em ambiente de desenvolvimento.
    
    Returns:
        bool: True se estiver em ambiente de desenvolvimento, False caso contrário
    """
    from app.config import Config
    return getattr(Config, 'ENVIRONMENT', 'production').lower() == 'development'

def is_pythonanywhere() -> bool:
    """
    Verifica se está sendo executado no PythonAnywhere.
    
    Returns:
        bool: True se estiver no PythonAnywhere, False caso contrário
    """
    # Verifica por características específicas do PythonAnywhere
    return (
        'PYTHONANYWHERE_DOMAIN' in os.environ or
        'PYTHONANYWHERE_SITE' in os.environ or
        os.path.exists('/home/pythonanywhere') or
        os.path.exists('/var/www/.pythonanywhere')
    )

def get_windows_version() -> Optional[Dict[str, Any]]:
    """
    Obtém informações detalhadas sobre a versão do Windows.
    
    Returns:
        Optional[Dict[str, Any]]: Informações da versão do Windows ou None se não for Windows
    """
    if not is_windows():
        return None
        
    try:
        import winreg
        version_info = {}
        
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion") as key:
            for name in [
                "ProductName", "EditionID", "InstallationType", "CurrentBuild", 
                "ReleaseId", "CurrentMajorVersionNumber", "CurrentMinorVersionNumber"
            ]:
                try:
                    value, _ = winreg.QueryValueEx(key, name)
                    version_info[name] = value
                except FileNotFoundError:
                    pass
        
        # Detecta Windows 11 vs Windows 10
        if 'CurrentMajorVersionNumber' in version_info:
            major = version_info['CurrentMajorVersionNumber']
            if major >= 10:
                build = int(version_info.get('CurrentBuild', 0))
                # Windows 11 usa build 22000 ou superior
                version_info['is_windows_11'] = build >= 22000
            else:
                version_info['is_windows_11'] = False
        
        return version_info
    except Exception as e:
        logger.warning(f"Erro ao obter versão detalhada do Windows: {str(e)}")
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version()
        }

def get_os_architecture() -> str:
    """
    Obtém a arquitetura do sistema operacional.
    
    Returns:
        str: Arquitetura do sistema operacional (32-bit, 64-bit, etc.)
    """
    return '64-bit' if sys.maxsize > 2**32 else '32-bit'

def get_kernel_version() -> str:
    """
    Obtém a versão do kernel.
    
    Returns:
        str: Versão do kernel
    """
    if is_linux():
        try:
            import subprocess
            output = subprocess.check_output(['uname', '-r']).decode('utf-8').strip()
            return output
        except Exception:
            pass
    
    return platform.release()

def initialize_com():
    """
    Inicializa COM para operações WMI - deve ser chamado no início de cada função
    que utiliza WMI para garantir que está inicializado na thread atual
    
    Returns:
        bool: True se inicializado com sucesso ou não for necessário, False caso contrário
    """
    if is_windows():
        try:
            # Importação tardia para evitar carga desnecessária em sistemas não-Windows
            import pythoncom
            pythoncom.CoInitialize()
            return True
        except ImportError:
            logger.warning("Módulo pythoncom não encontrado, operações WMI podem falhar")
            return False
        except Exception as e:
            logger.warning(f"Erro ao inicializar COM: {str(e)}")
            return False
    return True

def get_wmi_connection():
    """
    Obtém uma conexão WMI para consultas no Windows
    
    Returns:
        object: Objeto de conexão WMI ou None se não disponível
    """
    if not is_windows():
        return None
        
    # Inicializa COM para esta thread
    if not initialize_com():
        return None
        
    try:
        # Importação tardia para evitar carga desnecessária em sistemas não-Windows
        import wmi
        return wmi.WMI()
    except ImportError:
        logger.warning("Módulo WMI não encontrado")
        return None
    except Exception as e:
        logger.warning(f"Erro ao obter conexão WMI: {str(e)}")
        return None

def run_powershell_command(command):
    """
    Executa um comando PowerShell e retorna a saída
    
    Args:
        command (str): Comando PowerShell a ser executado
        
    Returns:
        str: Saída do comando PowerShell ou string vazia em caso de erro
    """
    if not is_windows():
        logger.warning("Tentativa de executar PowerShell em sistema não-Windows")
        return ""
        
    try:
        import subprocess
        completed_process = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        return completed_process.stdout.strip()
    except Exception as e:
        logger.warning(f"Erro ao executar comando PowerShell: {str(e)}")
        return "" 