"""
Módulo principal para diagnóstico de sistema.
Este módulo expõe a API principal de diagnóstico de forma compatível com a versão anterior,
porém utilizando uma arquitetura mais modular e eficiente em termos de memória.
"""

from app.services.diagnostic.diagnostic_service import DiagnosticService

# Expõe apenas a classe principal para manter compatibilidade de APIs
__all__ = ['DiagnosticService'] 