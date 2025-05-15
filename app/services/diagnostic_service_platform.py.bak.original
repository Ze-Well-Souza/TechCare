"""
Módulo de adaptação para compatibilidade com diferentes plataformas (Windows/Linux)
Usado para garantir que o sistema funcione tanto em ambiente de desenvolvimento Windows
quanto em ambientes de produção Linux (como PythonAnywhere)
"""

import platform
import os
import logging
import sys
import psutil

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Detecta o sistema operacional atual
CURRENT_OS = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)

# Inicializa o COM no Windows (necessário para WMI)
if CURRENT_OS == 'Windows':
    try:
        import pythoncom
        logger.info("Inicializando COM para suporte ao WMI no Windows")
        pythoncom.CoInitialize()
    except ImportError:
        logger.warning("Módulo pythoncom não encontrado, operações WMI podem falhar")
    except Exception as e:
        logger.warning(f"Erro ao inicializar COM: {str(e)}")

def is_windows():
    """Verifica se o sistema operacional é Windows"""
    return CURRENT_OS == 'Windows'

def is_linux():
    """Verifica se o sistema operacional é Linux"""
    return CURRENT_OS == 'Linux'

def is_macos():
    """Verifica se o sistema operacional é macOS"""
    return CURRENT_OS == 'Darwin'

def initialize_com():
    """
    Inicializa COM para operações WMI - deve ser chamado no início de cada função
    que utiliza WMI para garantir que está inicializado na thread atual
    """
    if is_windows():
        try:
            import pythoncom
            pythoncom.CoInitialize()
            return True
        except Exception as e:
            logger.warning(f"Erro ao inicializar COM: {str(e)}")
            return False
    return True

class PlatformAdapter:
    """
    Classe adaptadora que fornece métodos específicos da plataforma
    para acesso a recursos do sistema
    """
    
    @staticmethod
    def get_cpu_info():
        """
        Retorna informações sobre a CPU, compatível com todas as plataformas
        
        Returns:
            dict: Informações da CPU
        """
        try:
            import cpuinfo
            info = cpuinfo.get_cpu_info()
            
            # Informações básicas disponíveis em todas as plataformas via psutil
            cpu_count = psutil.cpu_count(logical=True)
            cpu_count_physical = psutil.cpu_count(logical=False) or cpu_count
            cpu_freq = psutil.cpu_freq()
            
            result = {
                'vendor': info.get('vendor_id', 'Desconhecido'),
                'brand': info.get('brand_raw', 'Desconhecido'),
                'cores_logical': cpu_count,
                'cores_physical': cpu_count_physical,
                'architecture': info.get('arch', platform.architecture()[0]),
                'bits': info.get('bits', 64 if '64' in platform.architecture()[0] else 32),
                'frequency': cpu_freq.current if cpu_freq else 0,
                'temperature': None  # Será preenchido pelo método específico da plataforma
            }
            
            # Adiciona temperatura se disponível na plataforma atual
            if hasattr(PlatformAdapter, f'get_cpu_temperature_{CURRENT_OS.lower()}'):
                try:
                    temp_method = getattr(PlatformAdapter, f'get_cpu_temperature_{CURRENT_OS.lower()}')
                    result['temperature'] = temp_method()
                except Exception as e:
                    logger.warning(f"Não foi possível obter a temperatura da CPU: {str(e)}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter informações da CPU: {str(e)}")
            # Informações mínimas em caso de erro
            return {
                'vendor': 'Desconhecido',
                'brand': platform.processor() or 'Desconhecido',
                'cores_logical': psutil.cpu_count(logical=True) or 0,
                'cores_physical': psutil.cpu_count(logical=False) or 0,
                'architecture': platform.architecture()[0],
                'bits': 64 if '64' in platform.architecture()[0] else 32,
                'frequency': 0,
                'temperature': None
            }
    
    @staticmethod
    def get_cpu_temperature_windows():
        """
        Obtém a temperatura da CPU no Windows
        
        Returns:
            float: Temperatura da CPU em Celsius, ou None se não disponível
        """
        try:
            if is_windows():
                # Inicializa COM para esta thread
                initialize_com()
                
                import wmi
                w = wmi.WMI(namespace="root\\wmi")
                temperature_info = w.MSAcpi_ThermalZoneTemperature()[0]
                # Converte decikelvin para Celsius
                temperature = (temperature_info.CurrentTemperature / 10.0) - 273.15
                return round(temperature, 1)
            return None
        except Exception as e:
            logger.warning(f"Erro ao obter temperatura CPU no Windows: {str(e)}")
            return None
    
    @staticmethod
    def get_cpu_temperature_linux():
        """
        Obtém a temperatura da CPU no Linux
        
        Returns:
            float: Temperatura da CPU em Celsius, ou None se não disponível
        """
        try:
            if is_linux():
                # Tenta diferentes arquivos de temperatura no Linux
                paths = [
                    "/sys/class/thermal/thermal_zone0/temp",
                    "/sys/devices/platform/coretemp.0/temp1_input",
                    "/sys/bus/acpi/devices/LNXTHERM:00/thermal_zone/temp"
                ]
                
                for path in paths:
                    if os.path.exists(path):
                        with open(path, 'r') as f:
                            temp = int(f.read().strip()) / 1000
                            return round(temp, 1)
                
                # Tenta usando o módulo sensors se disponível
                try:
                    import sensors
                    sensors.init()
                    temp = None
                    for chip in sensors.iter_detected_chips():
                        for feature in chip:
                            if 'temp' in feature.label.lower() or 'core' in feature.label.lower():
                                temp = feature.get_value()
                                break
                        if temp:
                            break
                    sensors.cleanup()
                    if temp:
                        return round(temp, 1)
                except (ImportError, Exception):
                    pass
            return None
        except Exception as e:
            logger.warning(f"Erro ao obter temperatura CPU no Linux: {str(e)}")
            return None
    
    @staticmethod
    def get_disk_info(path=None):
        """
        Obtém informações sobre o disco, compatível com todas as plataformas
        
        Args:
            path: Caminho do disco a ser analisado (opcional)
            
        Returns:
            dict: Informações do disco
        """
        try:
            if path is None:
                path = os.path.abspath(os.sep)  # Raiz do sistema
            
            # Informações básicas disponíveis em todas as plataformas via psutil
            disk_usage = psutil.disk_usage(path)
            disk_io = psutil.disk_io_counters()
            
            # Informações de partições
            partitions = []
            for partition in psutil.disk_partitions(all=False):
                try:
                    partition_usage = psutil.disk_usage(partition.mountpoint)
                    partitions.append({
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'filesystem': partition.fstype,
                        'total': partition_usage.total,
                        'used': partition_usage.used,
                        'free': partition_usage.free,
                        'percent': partition_usage.percent
                    })
                except (PermissionError, OSError) as e:
                    # Alguns pontos de montagem podem não estar acessíveis
                    logger.debug(f"Erro ao acessar partição {partition.mountpoint}: {str(e)}")
            
            result = {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': disk_usage.percent,
                'read_count': disk_io.read_count if hasattr(disk_io, 'read_count') else 0,
                'write_count': disk_io.write_count if hasattr(disk_io, 'write_count') else 0,
                'read_bytes': disk_io.read_bytes if hasattr(disk_io, 'read_bytes') else 0,
                'write_bytes': disk_io.write_bytes if hasattr(disk_io, 'write_bytes') else 0,
                'partitions': partitions
            }
            
            # Adiciona informações específicas da plataforma, se disponíveis
            if hasattr(PlatformAdapter, f'get_disk_info_{CURRENT_OS.lower()}'):
                try:
                    platform_info = getattr(PlatformAdapter, f'get_disk_info_{CURRENT_OS.lower()}')(path)
                    if platform_info:
                        result.update(platform_info)
                except Exception as e:
                    logger.warning(f"Não foi possível obter informações específicas do disco: {str(e)}")
            
            return result
        except Exception as e:
            logger.error(f"Erro ao obter informações do disco: {str(e)}")
            # Informações mínimas em caso de erro
            return {
                'total': 0,
                'used': 0,
                'free': 0,
                'percent': 0,
                'read_count': 0,
                'write_count': 0,
                'read_bytes': 0,
                'write_bytes': 0,
                'partitions': []
            }
    
    @staticmethod
    def get_disk_info_windows(path=None):
        """
        Obtém informações específicas do disco no Windows
        
        Args:
            path: Caminho do disco a ser analisado
            
        Returns:
            dict: Informações adicionais do disco específicas do Windows
        """
        if not is_windows():
            return {}
            
        try:
            # Inicializa COM para esta thread
            initialize_com()
            
            import wmi
            w = wmi.WMI()
            
            # Obtém informações sobre os discos físicos
            physical_disks = []
            for disk in w.Win32_DiskDrive():
                physical_disks.append({
                    'model': disk.Model,
                    'serial': disk.SerialNumber,
                    'size': int(disk.Size) if disk.Size else 0,
                    'status': disk.Status
                })
            
            return {
                'physical_disks': physical_disks
            }
        except Exception as e:
            logger.warning(f"Erro ao obter informações específicas do disco no Windows: {str(e)}")
            return {}
    
    @staticmethod
    def get_memory_info():
        """
        Obtém informações sobre a memória, compatível com todas as plataformas
        
        Returns:
            dict: Informações da memória
        """
        try:
            # Informações básicas disponíveis em todas as plataformas via psutil
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            result = {
                'total': memory.total,
                'available': memory.available,
                'used': memory.used,
                'percent': memory.percent,
                'swap_total': swap.total,
                'swap_used': swap.used,
                'swap_free': swap.free,
                'swap_percent': swap.percent
            }
            
            # Adiciona informações específicas da plataforma, se disponíveis
            if hasattr(PlatformAdapter, f'get_memory_info_{CURRENT_OS.lower()}'):
                try:
                    platform_info = getattr(PlatformAdapter, f'get_memory_info_{CURRENT_OS.lower()}')()
                    if platform_info:
                        result.update(platform_info)
                except Exception as e:
                    logger.warning(f"Não foi possível obter informações específicas da memória: {str(e)}")
            
            return result
        except Exception as e:
            logger.error(f"Erro ao obter informações da memória: {str(e)}")
            # Informações mínimas em caso de erro
            return {
                'total': 0,
                'available': 0,
                'used': 0,
                'percent': 0,
                'swap_total': 0,
                'swap_used': 0,
                'swap_free': 0,
                'swap_percent': 0
            }
    
    @staticmethod
    def get_memory_info_windows():
        """
        Obtém informações específicas da memória no Windows
        
        Returns:
            dict: Informações adicionais da memória específicas do Windows
        """
        if not is_windows():
            return {}
            
        try:
            # Inicializa COM para esta thread
            initialize_com()
            
            import wmi
            w = wmi.WMI()
            
            memory_details = {}
            
            # Obter informações detalhadas da memória física
            physical_memory = []
            total_capacity = 0
            
            for mem in w.Win32_PhysicalMemory():
                try:
                    capacity_gb = round(int(mem.Capacity) / (1024**3), 2) if mem.Capacity else 0
                    total_capacity += capacity_gb
                    
                    memory_module = {
                        'capacity_gb': capacity_gb,
                        'speed': mem.Speed if hasattr(mem, 'Speed') else None,
                        'manufacturer': mem.Manufacturer if hasattr(mem, 'Manufacturer') else 'Desconhecido',
                        'bank_label': mem.BankLabel if hasattr(mem, 'BankLabel') else None,
                        'device_locator': mem.DeviceLocator if hasattr(mem, 'DeviceLocator') else None,
                        'form_factor': mem.FormFactor if hasattr(mem, 'FormFactor') else None,
                        'type': mem.MemoryType if hasattr(mem, 'MemoryType') else None,
                        'type_detail': mem.TypeDetail if hasattr(mem, 'TypeDetail') else None,
                    }
                    
                    physical_memory.append(memory_module)
                except Exception as e:
                    logger.warning(f"Erro ao obter informações de um módulo de memória: {str(e)}")
            
            # Obter informações sobre slots vazios de memória
            try:
                # Primeiro, determinar quantos slots de memória existem no total
                for cs in w.Win32_ComputerSystem():
                    if hasattr(cs, 'MemoryDevices'):
                        total_slots = cs.MemoryDevices
                        break
                
                # Calcular slots vazios pela diferença entre total e ocupados
                empty_slots = total_slots - len(physical_memory) if 'total_slots' in locals() else 0
                
                memory_details['physical_memory'] = physical_memory
                memory_details['total_capacity_gb'] = total_capacity
                memory_details['memory_slots'] = {
                    'total': total_slots if 'total_slots' in locals() else len(physical_memory),
                    'used': len(physical_memory),
                    'empty': empty_slots
                }
                
                # Verificar se o valor calculado pelo WMI corresponde ao obtido pelo psutil
                # para validação cruzada
                memory = psutil.virtual_memory()
                psutil_total_gb = round(memory.total / (1024**3), 2)
                
                if abs(total_capacity - psutil_total_gb) > 1.0:  # diferença maior que 1GB
                    logger.warning(f"Discrepância na detecção de memória: WMI={total_capacity}GB, psutil={psutil_total_gb}GB")
                    # Em caso de discrepância, usar o valor mais confiável (psutil)
                    memory_details['total_capacity_gb'] = psutil_total_gb
                
            except Exception as e:
                logger.warning(f"Erro ao obter informações de slots de memória: {str(e)}")
            
            return memory_details
            
        except Exception as e:
            logger.warning(f"Erro ao obter informações específicas da memória no Windows: {str(e)}")
            return {}
    
    @staticmethod
    def get_network_info():
        """
        Obtém informações sobre a rede, compatível com todas as plataformas
        
        Returns:
            dict: Informações da rede
        """
        try:
            # Informações básicas disponíveis em todas as plataformas via psutil
            net_io = psutil.net_io_counters()
            
            # Informações de interfaces de rede
            interfaces = {}
            for name, addresses in psutil.net_if_addrs().items():
                interfaces[name] = {
                    'addresses': [],
                    'stats': None
                }
                
                for addr in addresses:
                    address_info = {
                        'address': addr.address,
                        'netmask': addr.netmask,
                        'family': str(addr.family)
                    }
                    if hasattr(addr, 'broadcast'):
                        address_info['broadcast'] = addr.broadcast
                    interfaces[name]['addresses'].append(address_info)
            
            # Estatísticas de interfaces
            for name, stats in psutil.net_if_stats().items():
                if name in interfaces:
                    interfaces[name]['stats'] = {
                        'speed': stats.speed,
                        'mtu': stats.mtu,
                        'isup': stats.isup
                    }
            
            result = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errin': net_io.errin,
                'errout': net_io.errout,
                'dropin': net_io.dropin,
                'dropout': net_io.dropout,
                'interfaces': interfaces
            }
            
            # Adiciona informações específicas da plataforma, se disponíveis
            if hasattr(PlatformAdapter, f'get_network_info_{CURRENT_OS.lower()}'):
                try:
                    platform_info = getattr(PlatformAdapter, f'get_network_info_{CURRENT_OS.lower()}')()
                    if platform_info:
                        result.update(platform_info)
                except Exception as e:
                    logger.warning(f"Não foi possível obter informações específicas da rede: {str(e)}")
            
            return result
        except Exception as e:
            logger.error(f"Erro ao obter informações da rede: {str(e)}")
            # Informações mínimas em caso de erro
            return {
                'bytes_sent': 0,
                'bytes_recv': 0,
                'packets_sent': 0,
                'packets_recv': 0,
                'errin': 0,
                'errout': 0,
                'dropin': 0,
                'dropout': 0,
                'interfaces': {}
            }
            
    @staticmethod
    def get_startup_programs():
        """
        Obtém os programas de inicialização, adaptado para diferentes plataformas
        
        Returns:
            list: Lista de programas de inicialização
        """
        if is_windows():
            return PlatformAdapter.get_startup_programs_windows()
        elif is_linux():
            return PlatformAdapter.get_startup_programs_linux()
        else:
            return []
    
    @staticmethod
    def get_startup_programs_windows():
        """
        Obtém os programas de inicialização no Windows usando WMI
        
        Returns:
            list: Lista de programas de inicialização
        """
        try:
            if not is_windows():
                return []
            
            # Inicializa COM para esta thread
            initialize_com()
                
            import wmi
            w = wmi.WMI()
            
            startup_programs = []
            
            # Verificar itens no registro de inicialização do Windows
            for program in w.Win32_StartupCommand():
                startup_programs.append({
                    'name': program.Name,
                    'command': program.Command,
                    'location': program.Location,
                    'user': program.User
                })
            
            return startup_programs
        except Exception as e:
            logger.warning(f"Erro ao obter programas de inicialização no Windows: {str(e)}")
            return []
    
    @staticmethod
    def get_startup_programs_linux():
        """
        Obtém os programas de inicialização no Linux
        
        Returns:
            list: Lista de programas de inicialização
        """
        try:
            if not is_linux():
                return []
                
            startup_programs = []
            
            # Verificar programas de inicialização do systemd
            systemd_paths = [
                "/etc/systemd/system/",
                "/usr/lib/systemd/system/",
                f"/home/{os.getenv('USER')}/.config/systemd/user/"
            ]
            
            for path in systemd_paths:
                if os.path.exists(path):
                    for file in os.listdir(path):
                        if file.endswith(".service"):
                            service_path = os.path.join(path, file)
                            try:
                                with open(service_path, 'r') as f:
                                    content = f.read()
                                    
                                description = ""
                                exec_start = ""
                                
                                for line in content.split('\n'):
                                    if line.startswith("Description="):
                                        description = line.replace("Description=", "").strip()
                                    elif line.startswith("ExecStart="):
                                        exec_start = line.replace("ExecStart=", "").strip()
                                
                                startup_programs.append({
                                    'name': file.replace(".service", ""),
                                    'command': exec_start,
                                    'location': service_path,
                                    'description': description
                                })
                            except Exception as e:
                                logger.debug(f"Erro ao ler arquivo de serviço {service_path}: {str(e)}")
            
            # Verificar programas em /etc/init.d
            init_d_path = "/etc/init.d/"
            if os.path.exists(init_d_path):
                for file in os.listdir(init_d_path):
                    file_path = os.path.join(init_d_path, file)
                    if os.path.isfile(file_path) and os.access(file_path, os.X_OK):
                        startup_programs.append({
                            'name': file,
                            'command': file_path,
                            'location': init_d_path,
                            'description': "Init script"
                        })
            
            # Verificar programas em ~/.config/autostart
            autostart_path = os.path.expanduser("~/.config/autostart")
            if os.path.exists(autostart_path):
                for file in os.listdir(autostart_path):
                    if file.endswith(".desktop"):
                        desktop_path = os.path.join(autostart_path, file)
                        try:
                            with open(desktop_path, 'r') as f:
                                content = f.read()
                                
                            name = ""
                            exec_cmd = ""
                            
                            for line in content.split('\n'):
                                if line.startswith("Name="):
                                    name = line.replace("Name=", "").strip()
                                elif line.startswith("Exec="):
                                    exec_cmd = line.replace("Exec=", "").strip()
                            
                            startup_programs.append({
                                'name': name or file.replace(".desktop", ""),
                                'command': exec_cmd,
                                'location': autostart_path,
                                'description': "User autostart"
                            })
                        except Exception as e:
                            logger.debug(f"Erro ao ler arquivo desktop {desktop_path}: {str(e)}")
            
            return startup_programs
        except Exception as e:
            logger.warning(f"Erro ao obter programas de inicialização no Linux: {str(e)}")
            return []
    
    @staticmethod
    def get_system_information():
        """
        Obtém informações detalhadas sobre o sistema (fabricante, modelo, etc.)
        
        Returns:
            dict: Informações do sistema
        """
        result = {
            'manufacturer': 'Desconhecido',
            'model': 'Desconhecido',
            'system_type': platform.machine(),
            'serial_number': 'Desconhecido',
            'bios_version': 'Desconhecido'
        }
        
        # Tenta obter informações específicas do Windows
        if is_windows():
            try:
                # Inicializa COM para esta thread
                initialize_com()
                
                import wmi
                w = wmi.WMI()
                
                # Sistema
                for system in w.Win32_ComputerSystem():
                    result.update({
                        'manufacturer': system.Manufacturer,
                        'model': system.Model,
                        'system_type': system.SystemType,
                        'total_physical_memory_gb': round(int(system.TotalPhysicalMemory or 0) / (1024**3), 2) if hasattr(system, 'TotalPhysicalMemory') else None
                    })
                
                # BIOS
                for bios in w.Win32_BIOS():
                    result['bios'] = {
                        'manufacturer': bios.Manufacturer,
                        'version': bios.Version,
                        'name': bios.Name,
                        'serial_number': bios.SerialNumber if hasattr(bios, 'SerialNumber') else 'Desconhecido',
                        'release_date': bios.ReleaseDate if hasattr(bios, 'ReleaseDate') else None
                    }
                
                # Método alternativo para obter informações do sistema
                if result['manufacturer'] == 'Desconhecido':
                    try:
                        # Inicializa COM novamente para o namespace alternativo
                        initialize_com()
                        
                        # Tenta com outro namespace do WMI
                        w_alt = wmi.WMI(namespace="root\\cimv2")
                        for system in w_alt.Win32_ComputerSystemProduct():
                            if system.Vendor and system.Vendor != 'Desconhecido':
                                result['manufacturer'] = system.Vendor
                            if system.Name and system.Name != 'Desconhecido':
                                result['model'] = system.Name
                            if hasattr(system, 'IdentifyingNumber') and system.IdentifyingNumber:
                                result['serial_number'] = system.IdentifyingNumber
                    except Exception as e:
                        logger.warning(f"Erro ao obter informações alternativas do sistema: {str(e)}")
                        
                # Método para obter informações via comando powershell
                if result['manufacturer'] == 'Desconhecido' or result['model'] == 'Desconhecido':
                    try:
                        import subprocess
                        cmd = ['powershell', '-Command', 'Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object Manufacturer, Model | ConvertTo-Json']
                        process = subprocess.run(cmd, capture_output=True, text=True)
                        
                        if process.returncode == 0 and process.stdout:
                            import json
                            data = json.loads(process.stdout)
                            if 'Manufacturer' in data and data['Manufacturer']:
                                result['manufacturer'] = data['Manufacturer']
                            if 'Model' in data and data['Model']:
                                result['model'] = data['Model']
                    except Exception as e:
                        logger.warning(f"Erro ao obter informações do sistema via PowerShell: {str(e)}")
                
            except Exception as e:
                logger.warning(f"Erro ao obter informações do sistema no Windows: {str(e)}")
        
        # Para Linux
        elif is_linux():
            try:
                # Tenta obter fabricante/modelo via arquivos do sistema
                for file_path in ['/sys/devices/virtual/dmi/id/sys_vendor', '/sys/devices/virtual/dmi/id/product_name']:
                    try:
                        if os.path.exists(file_path):
                            with open(file_path, 'r') as f:
                                content = f.read().strip()
                                if 'vendor' in file_path and content:
                                    result['manufacturer'] = content
                                elif 'product_name' in file_path and content:
                                    result['model'] = content
                    except Exception:
                        pass
                
                # Tenta via comando lshw para informações mais detalhadas
                try:
                    import subprocess
                    cmd = ['lshw', '-c', 'system', '-json']
                    process = subprocess.run(cmd, capture_output=True, text=True)
                    
                    if process.returncode == 0 and process.stdout:
                        import json
                        data = json.loads(process.stdout)
                        if isinstance(data, list):
                            data = data[0]
                        
                        if 'vendor' in data and data['vendor']:
                            result['manufacturer'] = data['vendor']
                        if 'product' in data and data['product']:
                            result['model'] = data['product']
                        if 'serial' in data and data['serial']:
                            result['serial_number'] = data['serial']
                except Exception:
                    pass
            except Exception as e:
                logger.warning(f"Erro ao obter informações do sistema no Linux: {str(e)}")
        
        return result 