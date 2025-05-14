#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script para corrigir os problemas de detecção de hardware no TechCare
"""

import os
import sys
import subprocess
import logging
import platform
import traceback

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Verifica e instala as dependências necessárias para detecção de hardware"""
    required_packages = [
        'wmi',
        'pywin32',
        'psutil',
        'py-cpuinfo'
    ]
    
    try:
        import pip
        
        for package in required_packages:
            try:
                __import__(package)
                logger.info(f"Pacote {package} já está instalado.")
            except ImportError:
                logger.info(f"Instalando pacote {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
                logger.info(f"Pacote {package} instalado com sucesso.")
    
    except Exception as e:
        logger.error(f"Erro ao verificar/instalar dependências: {str(e)}")
        traceback.print_exc()

def test_system_detection():
    """Testa as funções de detecção de sistema"""
    try:
        # Importar após instalar dependências
        from app.services.diagnostic_service_platform import PlatformAdapter, is_windows
        
        logger.info("\n===== Testando detecção de sistema =====\n")
        
        # Informações do sistema
        logger.info("Obtendo informações do sistema...")
        system_info = PlatformAdapter.get_system_information()
        logger.info(f"Fabricante: {system_info.get('manufacturer', 'Desconhecido')}")
        logger.info(f"Modelo: {system_info.get('model', 'Desconhecido')}")
        logger.info(f"Tipo de sistema: {system_info.get('system_type', 'Desconhecido')}")
        
        if 'bios' in system_info:
            logger.info(f"BIOS: {system_info['bios'].get('manufacturer', 'Desconhecido')} {system_info['bios'].get('version', 'Desconhecido')}")
        
        # Informações da CPU
        logger.info("\nObtendo informações da CPU...")
        cpu_info = PlatformAdapter.get_cpu_info()
        logger.info(f"CPU: {cpu_info.get('brand', 'Desconhecido')}")
        logger.info(f"Núcleos físicos: {cpu_info.get('cores_physical', 0)}")
        logger.info(f"Núcleos lógicos: {cpu_info.get('cores_logical', 0)}")
        logger.info(f"Frequência: {cpu_info.get('frequency', 0)} MHz")
        
        # Informações da memória
        logger.info("\nObtendo informações da memória...")
        memory_info = PlatformAdapter.get_memory_info()
        logger.info(f"Memória total: {round(memory_info.get('total', 0) / (1024**3), 2)} GB")
        logger.info(f"Memória disponível: {round(memory_info.get('available', 0) / (1024**3), 2)} GB")
        logger.info(f"Memória em uso: {memory_info.get('percent', 0)}%")
        
        # Se está no Windows, testa informações detalhadas da memória
        if is_windows():
            logger.info("\nObtendo informações detalhadas da memória física...")
            memory_details = PlatformAdapter.get_memory_info_windows()
            
            if 'physical_memory' in memory_details:
                logger.info(f"Módulos de memória: {len(memory_details['physical_memory'])}")
                for i, module in enumerate(memory_details['physical_memory'], 1):
                    logger.info(f"  Módulo {i}: {module.get('capacity_gb', 0)} GB - {module.get('speed', 'Desconhecido')} MHz")
            
            if 'memory_slots' in memory_details:
                slots = memory_details['memory_slots']
                logger.info(f"Total de slots: {slots.get('total', 0)}")
                logger.info(f"Slots ocupados: {slots.get('used', 0)}")
                logger.info(f"Slots vazios: {slots.get('empty', 0)}")
            
            logger.info(f"Capacidade total de RAM: {memory_details.get('total_capacity_gb', 0)} GB")
        
        # Informações de disco
        logger.info("\nObtendo informações de disco...")
        disk_info = PlatformAdapter.get_disk_info()
        logger.info(f"Total: {round(disk_info.get('total', 0) / (1024**3), 2)} GB")
        logger.info(f"Livre: {round(disk_info.get('free', 0) / (1024**3), 2)} GB")
        logger.info(f"Uso: {disk_info.get('percent', 0)}%")
        
        # Informações de partições
        logger.info("\nPartições:")
        for partition in disk_info.get('partitions', []):
            logger.info(f"  {partition.get('device', '')} ({partition.get('mountpoint', '')}): "
                      f"{round(partition.get('total', 0) / (1024**3), 2)} GB - "
                      f"Livre: {round(partition.get('free', 0) / (1024**3), 2)} GB "
                      f"({partition.get('percent', 0)}% em uso)")
        
        # Testa o disco físico no Windows
        if is_windows():
            logger.info("\nInformações de discos físicos:")
            if 'physical_disks' in disk_info:
                for disk in disk_info['physical_disks']:
                    logger.info(f"  {disk.get('model', 'Desconhecido')}: {disk.get('size', 0) / (1024**3):.1f} GB")
        
        # Informações de rede
        logger.info("\nObtendo informações de rede...")
        network_info = PlatformAdapter.get_network_info()
        logger.info(f"Bytes enviados: {network_info.get('bytes_sent', 0) / (1024**2):.2f} MB")
        logger.info(f"Bytes recebidos: {network_info.get('bytes_recv', 0) / (1024**2):.2f} MB")
        
        logger.info("\nInterfaces de rede:")
        for name, interface in network_info.get('interfaces', {}).items():
            is_up = interface.get('stats', {}).get('isup', False)
            speed = interface.get('stats', {}).get('speed', 0)
            logger.info(f"  {name}: {'Ativo' if is_up else 'Inativo'} - Velocidade: {speed} Mbps")
            
            for addr in interface.get('addresses', []):
                logger.info(f"    Endereço: {addr.get('address', '')}")
        
        logger.info("\n===== Teste concluído com sucesso =====\n")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao testar detecção de sistema: {str(e)}")
        traceback.print_exc()
        return False
        
def create_test_report():
    """Cria um relatório mais completo como teste do DiagnosticService"""
    try:
        from app.services.diagnostic_service import DiagnosticService
        from app.services.diagnostic_repository import DiagnosticRepository
        
        logger.info("\n===== Criando relatório de diagnóstico completo =====\n")
        
        # Cria uma instância do serviço
        service = DiagnosticService(DiagnosticRepository())
        
        # Executa o diagnóstico
        logger.info("Executando diagnóstico completo...")
        diagnostic = service.start_diagnostic()
        
        # Obtém a identidade do computador
        logger.info("Obtendo identidade do computador...")
        identity = service.get_computer_identity()
        
        # Exibe os resultados mais importantes
        if identity:
            system = identity.get('system', {})
            cpu = identity.get('cpu', {})
            memory = identity.get('memory', {})
            disk = identity.get('disk', {})
            
            logger.info("\n----- Resultados do Diagnóstico -----")
            
            logger.info(f"\nSistema: {system.get('manufacturer', 'Desconhecido')} {system.get('model', 'Desconhecido')}")
            logger.info(f"Sistema Operacional: {system.get('system', 'Desconhecido')} {system.get('version', 'Desconhecido')}")
            
            logger.info(f"\nProcessador: {cpu.get('brand', 'Desconhecido')}")
            logger.info(f"Núcleos: {cpu.get('cores_physical', 0)} físicos / {cpu.get('cores_logical', 0)} lógicos")
            
            logger.info(f"\nMemória RAM: {memory.get('total_gb', 0):.2f} GB")
            logger.info(f"Memória em uso: {memory.get('percent_used', 0)}%")
            
            if 'details' in memory and 'slots' in memory['details']:
                slots = memory['details']['slots']
                logger.info(f"Slots de memória: {slots.get('used', 0)} usados / {slots.get('total', 0)} total")
            
            logger.info(f"\nArmazenamento: {disk.get('total_gb', 0):.2f} GB")
            logger.info(f"Espaço livre: {disk.get('free_gb', 0):.2f} GB ({100 - disk.get('percent_used', 0)}%)")
            
            if 'physical_disks' in disk:
                logger.info("\nDiscos físicos:")
                for pdisk in disk['physical_disks']:
                    logger.info(f"  - {pdisk.get('model', 'Desconhecido')} ({pdisk.get('size_gb', 0):.2f} GB)")
            
            motherboard = identity.get('motherboard', {})
            if 'baseboard' in motherboard:
                logger.info(f"\nPlaca-mãe: {motherboard['baseboard'].get('manufacturer', 'Desconhecido')} {motherboard['baseboard'].get('product', 'Desconhecido')}")
            
            logger.info("\n----- Fim do relatório -----\n")
        
        logger.info("Teste de relatório concluído com sucesso")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao criar relatório de teste: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        logger.info("Iniciando script de correção de detecção de hardware...")
        
        # Verifica sistema operacional
        if platform.system() != 'Windows':
            logger.warning("Este script foi projetado para ser executado em sistemas Windows.")
        
        # Verifica e instala dependências
        check_dependencies()
        
        # Testa a detecção do sistema
        if test_system_detection():
            logger.info("Detecção de sistema funcionando corretamente.")
        else:
            logger.error("Problemas encontrados na detecção de sistema.")
        
        # Cria relatório de teste
        if create_test_report():
            logger.info("Relatório de teste criado com sucesso.")
        else:
            logger.error("Problemas ao criar relatório de teste.")
            
        logger.info("Script de correção de detecção de hardware concluído.")
    
    except Exception as e:
        logger.error(f"Erro ao executar script: {str(e)}")
        traceback.print_exc() 