"""
Utilitários para o módulo de diagnóstico.
Este pacote contém utilitários e funções auxiliares para os analisadores de diagnóstico.
"""

# Exporta as funções principais para facilitar o uso
from app.services.diagnostic.utils.platform_utils import (
    is_windows, is_linux, is_macos, is_test_environment,
    is_development_environment, is_pythonanywhere,
    get_platform_info, get_windows_version
)

# Exporta as funções WMI se estiver no Windows
import sys
if sys.platform.startswith('win'):
    try:
        from app.services.diagnostic.utils.wmi_utils import (
            wmi_connection, get_wmi_class, is_wmi_available,
            get_processor_info, get_memory_info, get_disk_info,
            get_network_info, get_computer_system_info
        )
    except ImportError:
        pass 