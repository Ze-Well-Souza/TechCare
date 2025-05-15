#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para testar o sistema de atualização de drivers diretamente,
sem depender da interface web.
"""

import os
import sys
import json
import datetime as dt
from pathlib import Path

# Adiciona o diretório atual ao path para importar os módulos da aplicação
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa o serviço de drivers
from app.services.driver_update_service import DriverUpdateService

def main():
    print("=== Teste do Sistema de Atualização de Drivers ===")
    
    # Cria uma instância do serviço de drivers
    driver_service = DriverUpdateService()
    
    # Verifica se o sistema é Windows
    if not driver_service.is_windows:
        print("AVISO: Este sistema não é Windows. Serão usados dados simulados.")
    
    # Escaneia os drivers do sistema
    print("\nEscaneando drivers do sistema...")
    drivers_info = driver_service.scan_drivers()
    
    # Exibe um resumo dos drivers encontrados
    print(f"\nResumo dos Drivers:")
    print(f"Total de drivers: {drivers_info['total_count']}")
    print(f"Drivers atualizados: {drivers_info['updated_count']}")
    print(f"Drivers desatualizados: {drivers_info['outdated_count']}")
    print(f"Drivers com problemas: {drivers_info['issue_count']}")
    
    # Exibe a lista de drivers
    print("\nLista de Drivers:")
    for i, driver in enumerate(drivers_info['drivers']):
        status = driver['status']
        status_color = ""
        if status == "Updated":
            status_text = "Atualizado"
        elif status == "Outdated":
            status_text = "Desatualizado"
        else:
            status_text = "Com Problemas"
            
        print(f"{i+1}. {driver['name']} ({driver['manufacturer']})")
        print(f"   Versão: {driver['version']}, Status: {status_text}")
        print(f"   Tipo: {driver['type']}, Data: {driver['date']}")
        print(f"   Atualização disponível: {'Sim' if driver.get('update_available', False) else 'Não'}")
        print()
    
    # Exibe as recomendações
    if 'recommendations' in drivers_info and drivers_info['recommendations']:
        print("\nRecomendações:")
        for i, rec in enumerate(drivers_info['recommendations']):
            print(f"{i+1}. {rec['title']} - {rec['description']}")
            print(f"   Prioridade: {rec['priority']}")
    
    # Salva os resultados em um arquivo JSON para análise posterior
    output_dir = Path("data/drivers")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / "last_scan_results.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(drivers_info, f, indent=4, ensure_ascii=False)
    
    print(f"\nResultados salvos em: {output_file}")

if __name__ == "__main__":
    main()
