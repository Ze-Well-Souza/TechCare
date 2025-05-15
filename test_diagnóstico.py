#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar o serviço de diagnóstico refatorado
"""

from app.services.diagnostic.diagnostic_service import DiagnosticService

def main():
    try:
        print("Inicializando serviço de diagnóstico...")
        service = DiagnosticService()
        
        print("Executando diagnóstico...")
        result = service.run_diagnostic()
        
        print(f"Diagnóstico executado com sucesso!")
        print(f"Pontuação de saúde: {result.get('health_score', 'N/A')}")
        
        # Mostrar componentes analisados
        components = result.get('components', {})
        print("\nComponentes analisados:")
        for name, data in components.items():
            health = data.get('health_score', 'N/A')
            print(f"- {name}: {health}")
        
        # Mostrar recomendações
        recommendations = result.get('recommendations', [])
        if recommendations:
            print("\nRecomendações:")
            for rec in recommendations:
                print(f"- {rec}")
        
        return 0
    except Exception as e:
        print(f"Erro ao executar diagnóstico: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main()) 