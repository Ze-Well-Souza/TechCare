"""
Módulos analisadores específicos para diferentes componentes do sistema.
Cada módulo é responsável por analisar um componente específico (CPU, memória, disco, etc.).
"""

# Exporta as classes de analisadores
from app.services.diagnostic.analyzers.cpu_analyzer import CPUAnalyzer
from app.services.diagnostic.analyzers.memory_analyzer import MemoryAnalyzer
from app.services.diagnostic.analyzers.disk_analyzer import DiskAnalyzer
from app.services.diagnostic.analyzers.network_analyzer import NetworkAnalyzer
from app.services.diagnostic.analyzers.startup_analyzer import StartupAnalyzer
from app.services.diagnostic.analyzers.security_analyzer import SecurityAnalyzer
from app.services.diagnostic.analyzers.driver_analyzer import DriverAnalyzer

__all__ = [
    'CPUAnalyzer',
    'MemoryAnalyzer',
    'DiskAnalyzer',
    'NetworkAnalyzer',
    'StartupAnalyzer',
    'SecurityAnalyzer',
    'DriverAnalyzer'
]

# Outras classes serão adicionadas à medida que forem implementadas 