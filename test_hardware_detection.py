#!/usr/bin/env python
"""
Script para testar a detecção de hardware no TechCare.
Este script utiliza as classes e funções do hardware_detection_fix.py
para verificar se a detecção de hardware está funcionando corretamente.
"""

import os
import sys
import logging
from pathlib import Path

# Adicionar o diretório atual ao PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar a classe HardwareDetector
try:
    from hardware_detection_fix import HardwareDetector
except ImportError:
    print("Erro: Não foi possível importar a classe HardwareDetector.")
    print("Certifique-se de que o arquivo hardware_detection_fix.py está no mesmo diretório.")
    sys.exit(1)

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('test_hardware_detection')

def main():
    """Função principal para testar a detecção de hardware"""
    logger.info("Iniciando teste de detecção de hardware")
    
    # Criar instância do detector
    detector = HardwareDetector()
    
    # Testar detecção de sistema (fabricante/modelo)
    try:
        logger.info("\n=== Informações do Sistema ===")
        system_info = detector.get_system_info()
        logger.info(f"Fabricante: {system_info['manufacturer']}")
        logger.info(f"Modelo: {system_info['model']}")
    except Exception as e:
        logger.error(f"Erro ao detectar informações do sistema: {str(e)}")
    
    # Testar detecção de memória
    try:
        logger.info("\n=== Informações de Memória ===")
        memory_info = detector.get_memory_info()
        logger.info(f"Memória RAM Total: {memory_info['total_gb']} GB")
        
        if 'slots' in memory_info and memory_info['slots']:
            logger.info(f"Módulos de memória instalados: {len(memory_info['slots'])}")
            for i, slot in enumerate(memory_info['slots']):
                logger.info(f"  Módulo {i+1}: {slot['capacity_gb']} GB {slot['type']} ({slot['speed']} MHz)")
        
        if 'empty_slots' in memory_info and memory_info['empty_slots']:
            logger.info(f"Slots vazios para expansão: {', '.join(memory_info['empty_slots'])}")
            logger.info(f"Memória expansível: {'Sim' if memory_info.get('is_upgradable', False) else 'Não'}")
    except Exception as e:
        logger.error(f"Erro ao detectar informações de memória: {str(e)}")
    
    # Testar detecção de discos
    try:
        logger.info("\n=== Informações de Disco ===")
        disk_info = detector.get_disk_info()
        
        if 'physical_disks' in disk_info and disk_info['physical_disks']:
            logger.info(f"Discos físicos encontrados: {len(disk_info['physical_disks'])}")
            for i, disk in enumerate(disk_info['physical_disks']):
                logger.info(f"  Disco {i+1}: {disk['model']}")
                logger.info(f"    Capacidade: {disk['size_gb']} GB")
                logger.info(f"    Tipo: {disk['media_type']}")
                logger.info(f"    Interface: {disk['interface_type']}")
                logger.info(f"    Fabricante: {disk['manufacturer']}")
                logger.info(f"    Status: {disk['status']}")
        
        if 'available_slots' in disk_info and disk_info['available_slots']:
            logger.info(f"Slots disponíveis para discos adicionais: {', '.join(disk_info['available_slots'])}")
    except Exception as e:
        logger.error(f"Erro ao detectar informações de disco: {str(e)}")
    
    logger.info("\n=== Teste de Detecção Concluído ===")
    logger.info("Verifique se as informações acima correspondem ao hardware do seu sistema.")
    logger.info("Se as informações estiverem corretas, as melhorias estão funcionando adequadamente.")

if __name__ == "__main__":
    main() 