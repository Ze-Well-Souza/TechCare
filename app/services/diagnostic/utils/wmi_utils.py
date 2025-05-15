"""
Utilitários para acesso ao WMI (Windows Management Instrumentation).
Fornece funções para obter informações detalhadas do sistema no Windows.
"""

import logging
import gc
import os
import sys
from contextlib import contextmanager
from typing import Any, Optional, List, Dict, Generator

# Configuração de logging
logger = logging.getLogger(__name__)

def is_wmi_available() -> bool:
    """
    Verifica se o WMI está disponível no sistema.
    
    Returns:
        bool: True se WMI estiver disponível, False caso contrário
    """
    try:
        import wmi
        import pythoncom
        return True
    except ImportError:
        return False

@contextmanager
def wmi_connection(namespace: str = "root\\cimv2") -> Generator[Any, None, None]:
    """
    Estabelece uma conexão WMI com o namespace especificado.
    Usa um context manager para garantir a limpeza adequada da conexão.
    
    Args:
        namespace: Namespace WMI a ser usado
        
    Yields:
        Objeto de conexão WMI ou None em caso de erro
    """
    if not sys.platform.startswith('win'):
        yield None
        return
        
    try:
        import wmi
        import pythoncom
        
        # Inicializa COM para a thread atual
        pythoncom.CoInitialize()
        
        # Cria conexão WMI
        connection = wmi.WMI(namespace=namespace)
        yield connection
        
    except ImportError as e:
        logger.warning(f"Módulos WMI não disponíveis: {str(e)}")
        yield None
        
    except Exception as e:
        logger.error(f"Erro ao criar conexão WMI: {str(e)}")
        yield None
        
    finally:
        # Cleanup
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass
        
        # Força coleta de lixo para liberar recursos COM
        gc.collect()

def get_wmi_class(class_name: str, namespace: str = "root\\cimv2") -> List[Any]:
    """
    Obtém instâncias de uma classe WMI específica.
    
    Args:
        class_name: Nome da classe WMI a ser consultada
        namespace: Namespace WMI a ser usado
        
    Returns:
        Lista de objetos da classe ou lista vazia em caso de erro
    """
    if not sys.platform.startswith('win'):
        return []
        
    try:
        with wmi_connection(namespace) as wmi_conn:
            if wmi_conn:
                return getattr(wmi_conn, class_name)()
            return []
    except Exception as e:
        logger.error(f"Erro ao obter classe WMI {class_name}: {str(e)}")
        return []

def get_processor_info() -> Dict[str, Any]:
    """
    Obtém informações detalhadas sobre o processador via WMI.
    
    Returns:
        Dict[str, Any]: Informações do processador
    """
    result = {
        'name': 'Desconhecido',
        'manufacturer': 'Desconhecido',
        'cores': 0,
        'threads': 0,
        'max_clock_speed': 0,
        'socket': 'Desconhecido',
        'architecture': 'Desconhecido',
        'virtualization': False
    }
    
    processors = get_wmi_class('Win32_Processor')
    if processors:
        proc = processors[0]
        result['name'] = proc.Name
        result['manufacturer'] = proc.Manufacturer
        result['cores'] = proc.NumberOfCores
        result['threads'] = proc.NumberOfLogicalProcessors
        result['max_clock_speed'] = proc.MaxClockSpeed
        result['socket'] = proc.SocketDesignation
        result['architecture'] = 'x64' if proc.AddressWidth == 64 else 'x86'
        result['virtualization'] = proc.VirtualizationFirmwareEnabled if hasattr(proc, 'VirtualizationFirmwareEnabled') else None
        
    return result

def get_memory_info() -> Dict[str, Any]:
    """
    Obtém informações detalhadas sobre a memória RAM via WMI.
    
    Returns:
        Dict[str, Any]: Informações da memória
    """
    result = {
        'total': 0,
        'modules': [],
        'slots_total': 0,
        'slots_used': 0
    }
    
    # Obtém informação total de memória
    computer_system = get_wmi_class('Win32_ComputerSystem')
    if computer_system:
        # Converte de KB para bytes
        total_memory_kb = int(computer_system[0].TotalPhysicalMemory) // 1024
        result['total'] = total_memory_kb
    
    # Obtém detalhes dos módulos de memória
    memory_modules = get_wmi_class('Win32_PhysicalMemory')
    if memory_modules:
        result['slots_used'] = len(memory_modules)
        
        for module in memory_modules:
            module_info = {
                'capacity': int(module.Capacity) // (1024*1024) if hasattr(module, 'Capacity') else 0,  # Converte para MB
                'type': get_memory_type(module.MemoryType) if hasattr(module, 'MemoryType') else 'Desconhecido',
                'speed': module.Speed if hasattr(module, 'Speed') else 0,
                'manufacturer': module.Manufacturer if hasattr(module, 'Manufacturer') else 'Desconhecido',
                'location': module.DeviceLocator if hasattr(module, 'DeviceLocator') else 'Desconhecido'
            }
            result['modules'].append(module_info)
    
    # Obtém informações sobre slots de memória
    memory_slots = get_wmi_class('Win32_PhysicalMemoryArray')
    if memory_slots and memory_slots[0].MemoryDevices:
        result['slots_total'] = memory_slots[0].MemoryDevices
    
    return result

def get_disk_info() -> List[Dict[str, Any]]:
    """
    Obtém informações detalhadas sobre os discos via WMI.
    
    Returns:
        List[Dict[str, Any]]: Lista de informações dos discos
    """
    disks = []
    
    # Obtém discos físicos
    physical_disks = get_wmi_class('Win32_DiskDrive')
    for disk in physical_disks:
        # Determina se é SSD ou HDD
        disk_type = 'Desconhecido'
        try:
            # MSFT_PhysicalDisk tem campo MediaType mais preciso
            with wmi_connection("root\\Microsoft\\Windows\\Storage") as wmi_storage:
                if wmi_storage:
                    for pd in wmi_storage.MSFT_PhysicalDisk():
                        # Compara pelo número de disco
                        if pd.DeviceID == disk.Index:
                            # 3: HDD, 4: SSD, 5: SCM
                            if pd.MediaType == 3:
                                disk_type = 'HDD'
                            elif pd.MediaType == 4:
                                disk_type = 'SSD'
                            elif pd.MediaType == 5:
                                disk_type = 'SCM'
                            break
        except Exception:
            # Fallback: tenta determinar por modelo conhecido
            model = disk.Model.lower() if hasattr(disk, 'Model') else ''
            if any(keyword in model for keyword in ['ssd', 'solid', 'nvme', 'pcie']):
                disk_type = 'SSD'
            elif any(keyword in model for keyword in ['hdd', 'hard disk']):
                disk_type = 'HDD'
        
        # Obtém partições associadas ao disco
        partitions = []
        for partition in get_wmi_class('Win32_DiskPartition'):
            if partition.DiskIndex == disk.Index:
                # Obtém volumes lógicos associados à partição
                logical_disks = []
                for association in get_wmi_class('Win32_LogicalDiskToPartition'):
                    if association.Antecedent.split('=')[1].strip('"\'') == partition.DeviceID:
                        logical_disk_id = association.Dependent.split('=')[1].strip('"\'')
                        
                        # Busca o volume correspondente
                        for logical_disk in get_wmi_class('Win32_LogicalDisk'):
                            if logical_disk.DeviceID == logical_disk_id:
                                logical_disks.append({
                                    'device_id': logical_disk.DeviceID,
                                    'volume_name': logical_disk.VolumeName or '',
                                    'file_system': logical_disk.FileSystem or '',
                                    'size': int(logical_disk.Size) if logical_disk.Size else 0,
                                    'free_space': int(logical_disk.FreeSpace) if logical_disk.FreeSpace else 0
                                })
                
                partitions.append({
                    'name': partition.Name,
                    'size': int(partition.Size) if partition.Size else 0,
                    'logical_disks': logical_disks
                })
        
        disk_info = {
            'model': disk.Model if hasattr(disk, 'Model') else 'Desconhecido',
            'type': disk_type,
            'serial': disk.SerialNumber if hasattr(disk, 'SerialNumber') else 'Desconhecido',
            'size': int(disk.Size) if hasattr(disk, 'Size') else 0,
            'interface': disk.InterfaceType if hasattr(disk, 'InterfaceType') else 'Desconhecido',
            'partitions': partitions
        }
        
        disks.append(disk_info)
    
    return disks

def get_network_info() -> List[Dict[str, Any]]:
    """
    Obtém informações detalhadas sobre os adaptadores de rede via WMI.
    
    Returns:
        List[Dict[str, Any]]: Lista de informações dos adaptadores de rede
    """
    adapters = []
    
    # Obtém adaptadores de rede configurados
    network_configs = get_wmi_class('Win32_NetworkAdapterConfiguration')
    network_adapters = get_wmi_class('Win32_NetworkAdapter')
    
    # Cria mapeamento de adaptadores por índice
    adapter_map = {adapter.Index: adapter for adapter in network_adapters}
    
    for config in network_configs:
        if config.IPEnabled:
            adapter = adapter_map.get(config.Index)
            
            if adapter:
                adapter_info = {
                    'name': adapter.Name,
                    'description': adapter.Description,
                    'mac_address': config.MACAddress,
                    'ip_addresses': config.IPAddress,
                    'subnet_masks': config.IPSubnet,
                    'default_gateway': config.DefaultIPGateway[0] if config.DefaultIPGateway else None,
                    'dns_servers': config.DNSServerSearchOrder,
                    'connection_speed': adapter.Speed if hasattr(adapter, 'Speed') else None,
                    'adapter_type': adapter.AdapterType if hasattr(adapter, 'AdapterType') else 'Desconhecido',
                    'connection_status': adapter.NetConnectionStatus if hasattr(adapter, 'NetConnectionStatus') else None
                }
                
                adapters.append(adapter_info)
    
    return adapters

def get_computer_system_info() -> Dict[str, Any]:
    """
    Obtém informações sobre o sistema do computador via WMI.
    
    Returns:
        Dict[str, Any]: Informações do sistema
    """
    result = {
        'manufacturer': 'Desconhecido',
        'model': 'Desconhecido',
        'system_type': 'Desconhecido',
        'bios_version': 'Desconhecido',
        'bios_manufacturer': 'Desconhecido',
        'bios_date': 'Desconhecido'
    }
    
    # Obtém informações do sistema
    computer_systems = get_wmi_class('Win32_ComputerSystem')
    if computer_systems:
        system = computer_systems[0]
        result['manufacturer'] = system.Manufacturer
        result['model'] = system.Model
        result['system_type'] = system.SystemType
    
    # Obtém informações da BIOS
    bios_list = get_wmi_class('Win32_BIOS')
    if bios_list:
        bios = bios_list[0]
        result['bios_version'] = bios.Version
        result['bios_manufacturer'] = bios.Manufacturer
        result['bios_date'] = bios.ReleaseDate
    
    return result

def get_graphics_info() -> List[Dict[str, Any]]:
    """
    Obtém informações sobre as placas gráficas via WMI.
    
    Returns:
        List[Dict[str, Any]]: Lista de informações das placas gráficas
    """
    graphics_cards = []
    
    # Obtém informações das placas de vídeo
    video_controllers = get_wmi_class('Win32_VideoController')
    for controller in video_controllers:
        card_info = {
            'name': controller.Name,
            'adapter_ram': int(controller.AdapterRAM) if hasattr(controller, 'AdapterRAM') else 0,
            'driver_version': controller.DriverVersion if hasattr(controller, 'DriverVersion') else 'Desconhecido',
            'current_resolution': f"{controller.CurrentHorizontalResolution}x{controller.CurrentVerticalResolution}" if hasattr(controller, 'CurrentHorizontalResolution') else 'Desconhecido',
            'refresh_rate': controller.CurrentRefreshRate if hasattr(controller, 'CurrentRefreshRate') else 0,
            'driver_date': controller.DriverDate if hasattr(controller, 'DriverDate') else 'Desconhecido'
        }
        
        graphics_cards.append(card_info)
    
    return graphics_cards

def get_memory_type(type_code: int) -> str:
    """
    Converte o código de tipo de memória para uma descrição legível.
    
    Args:
        type_code: Código numérico do tipo de memória
        
    Returns:
        str: Descrição do tipo de memória
    """
    memory_types = {
        0: 'Desconhecido',
        1: 'Outro',
        2: 'DRAM',
        3: 'Sincronizada',
        4: 'Cache',
        5: 'EDO',
        6: 'EDRAM',
        7: 'VRAM',
        8: 'SRAM',
        9: 'RAM',
        10: 'ROM',
        11: 'Flash',
        12: 'EEPROM',
        13: 'FEPROM',
        14: 'EPROM',
        15: 'CDRAM',
        16: '3DRAM',
        17: 'SDRAM',
        18: 'SGRAM',
        19: 'RDRAM',
        20: 'DDR',
        21: 'DDR2',
        22: 'DDR2 FB-DIMM',
        24: 'DDR3',
        25: 'FBD2',
        26: 'DDR4',
        27: 'LPDDR',
        28: 'LPDDR2',
        29: 'LPDDR3',
        30: 'LPDDR4'
    }
    
    return memory_types.get(type_code, 'Desconhecido') 