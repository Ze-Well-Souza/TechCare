"""
Analisador de disco para o diagnóstico de sistema.
Responsável por coletar e analisar informações sobre o armazenamento.
"""

import os
import platform
import psutil
import logging
import gc
import re
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path

from app.utils.cache import cache_result
from app.services.diagnostic.utils.platform_utils import is_windows, is_linux, is_macos
from app.services.diagnostic.utils.wmi_utils import wmi_connection, get_wmi_class
from app.services.diagnostic.utils.platform_utils import run_powershell_command

logger = logging.getLogger(__name__)

class DiskAnalyzer:
    """
    Classe responsável por analisar o desempenho e características do armazenamento.
    """
    
    def __init__(self):
        """Inicializa o analisador de disco"""
        self.problems = []
        self.score = 100
        self.has_wmi = False
        
        if is_windows():
            try:
                import wmi
                import pythoncom
                self.has_wmi = True
            except ImportError:
                logger.warning("Módulos WMI não disponíveis para análise detalhada do disco no Windows")
    
    def _safe_path_for_log(self, path):
        """
        Retorna uma representação segura do caminho para usar em logs.
        
        Args:
            path: O caminho a ser formatado
            
        Returns:
            str: Representação segura do caminho
        """
        if path is None:
            return "None"
        try:
            return repr(path)
        except:
            return "caminho_inválido"
    
    @cache_result(expire_seconds=300)
    def analyze(self) -> Dict[str, Any]:
        """
        Executa a análise completa do armazenamento.
        
        Returns:
            Dict[str, Any]: Resultados da análise do armazenamento
        """
        logger.info("Analisando armazenamento...")
        
        try:
            # Inicia com os dados básicos disponíveis em todas as plataformas
            result = self._get_basic_disk_info()
            
            # Adiciona informações específicas da plataforma
            if is_windows():
                self._add_windows_specific_data(result)
            elif is_linux():
                self._add_linux_specific_data(result)
            elif is_macos():
                self._add_macos_specific_data(result)
            
            # Analisa problemas
            issues = self._analyze_issues(result)
            result['issues'] = issues
            
            # Calcula pontuação de saúde
            result['health_score'] = self._calculate_health_score(result)
            
            # Adiciona problemas encontrados
            result['problems'] = self.problems
            
            return result
        except Exception as e:
            logger.error(f"Erro ao analisar armazenamento: {str(e)}", exc_info=True)
            return {
                'error': f"Erro ao analisar armazenamento: {str(e)}",
                'drives': [],
                'health_score': 0,
                'issues': [{
                    'description': f'Erro crítico na análise de armazenamento: {str(e)}',
                    'recommendation': 'Verifique os logs para mais detalhes.',
                    'severity': 'high'
                }],
                'problems': [{
                    'category': 'disk',
                    'title': 'Erro na análise de armazenamento',
                    'description': f'Erro crítico ao analisar armazenamento: {str(e)}',
                    'solution': 'Verifique os logs para mais detalhes.',
                    'impact': 'high',
                    'severity': 'high'
                }]
            }
        finally:
            # Libera memória
            gc.collect()
    
    def _get_basic_disk_info(self) -> Dict[str, Any]:
        """
        Obtém informações básicas sobre o armazenamento usando psutil.
        
        Returns:
            Dict[str, Any]: Informações básicas do armazenamento
        """
        try:
            drives = []
            
            # Obtém partições de disco
            partitions = psutil.disk_partitions(all=False)
            
            for partition in partitions:
                # Ignora drives virtuais ou de rede em alguns casos
                if partition.fstype == '' and not self._is_valid_mountpoint(partition.mountpoint):
                    continue
                    
                # Obtém uso de disco para esta partição
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Converte para MB para facilitar exibição
                    total_mb = usage.total / (1024 * 1024)
                    used_mb = usage.used / (1024 * 1024)
                    free_mb = usage.free / (1024 * 1024)
                    
                    drive_info = {
                        'device': partition.device,
                        'mountpoint': partition.mountpoint,
                        'fstype': partition.fstype,
                        'opts': partition.opts,
                        'total': usage.total,
                        'total_mb': round(total_mb, 2),
                        'used': usage.used,
                        'used_mb': round(used_mb, 2),
                        'free': usage.free,
                        'free_mb': round(free_mb, 2),
                        'percent': usage.percent,
                        'disk_type': None,  # Será preenchido pelas funções específicas da plataforma
                        'is_ssd': None
                    }
                    
                    drives.append(drive_info)
                except (PermissionError, FileNotFoundError):
                    # Ignora partições que não podem ser acessadas
                    pass
                except Exception:
                    # Ignora erros ao analisar partições para evitar problemas de formatação
                    pass
            
            # Obtém informações de IO do disco
            try:
                disk_io = psutil.disk_io_counters(perdisk=True)
                if disk_io:
                    io_stats = {}
                    for disk_name, stats in disk_io.items():
                        io_stats[disk_name] = {
                            'read_count': stats.read_count,
                            'write_count': stats.write_count,
                            'read_bytes': stats.read_bytes,
                            'read_mb': round(stats.read_bytes / (1024 * 1024), 2),
                            'write_bytes': stats.write_bytes,
                            'write_mb': round(stats.write_bytes / (1024 * 1024), 2),
                            'read_time': getattr(stats, 'read_time', 0),
                            'write_time': getattr(stats, 'write_time', 0)
                        }
            except Exception as e:
                logger.debug(f"Erro ao obter estatísticas de IO do disco: {str(e)}")
                io_stats = {}
                
            result = {
                'drives': drives,
                'io_stats': io_stats
            }
            
            return result
        except Exception as e:
            logger.warning(f"Erro ao obter informações básicas de armazenamento: {str(e)}")
            return {
                'drives': [],
                'io_stats': {}
            }
    
    def _is_valid_mountpoint(self, mountpoint: str) -> bool:
        """
        Verifica se um ponto de montagem é válido.
        
        Args:
            mountpoint: Ponto de montagem a ser verificado
            
        Returns:
            bool: True se for válido, False caso contrário
        """
        if is_windows():
            # No Windows, os pontos de montagem válidos são letras de unidades (C:\, D:\, etc.)
            return re.match(r'^[A-Za-z]:\\$', mountpoint) is not None
        else:
            # No Linux/macOS, os pontos de montagem válidos começam com /
            return mountpoint.startswith('/')
    
    def _add_windows_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas de armazenamento para Windows.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        drives = result.get('drives', [])
        
        if not self.has_wmi:
            return
            
        try:
            # Obtém informações detalhadas sobre discos físicos
            with wmi_connection() as wmi_conn:
                if wmi_conn:
                    try:
                        # Mapeia letras de unidade para discos físicos
                        drive_to_disk_map = {}
                        logical_disks = wmi_conn.Win32_LogicalDisk()
                        
                        for logical_disk in logical_disks:
                            try:
                                for drive in drives:
                                    if drive['mountpoint'].rstrip('\\') == logical_disk.DeviceID:
                                        drive['volume_name'] = logical_disk.VolumeName or ''
                                        drive['volume_serial'] = logical_disk.VolumeSerialNumber or ''
                                        
                                        # Encontra associação com disco físico
                                        for partition in wmi_conn.Win32_DiskDriveToDiskPartition():
                                            for logical_disk_to_partition in wmi_conn.Win32_LogicalDiskToPartition():
                                                if logical_disk_to_partition.Dependent.DeviceID == logical_disk.DeviceID and \
                                                   logical_disk_to_partition.Antecedent == partition.Dependent:
                                                    drive_to_disk_map[drive['mountpoint']] = partition.Antecedent
                            except Exception as e:
                                logger.debug(f"Erro ao processar disco lógico {logical_disk.DeviceID}: {str(e)}")
                        
                        # Adiciona informações sobre discos físicos
                        physical_disks = wmi_conn.Win32_DiskDrive()
                        
                        disk_info_map = {}
                        for disk in physical_disks:
                            try:
                                model = disk.Model or 'Unknown'
                                interface_type = disk.InterfaceType or 'Unknown'
                                size_mb = int(disk.Size or 0) / (1024 * 1024)
                                
                                # Verifica se é SSD através do nome/modelo
                                is_ssd = self._check_if_ssd_by_name(model)
                                
                                disk_info = {
                                    'model': model,
                                    'interface_type': interface_type,
                                    'size_mb': round(size_mb, 2),
                                    'is_ssd': is_ssd,
                                    'firmware': disk.FirmwareRevision or '',
                                    'serial': disk.SerialNumber or ''
                                }
                                
                                disk_info_map[disk.DeviceID] = disk_info
                            except Exception as e:
                                logger.debug(f"Erro ao processar disco físico {disk.DeviceID}: {str(e)}")
                        
                        # Associa informações de discos físicos às unidades lógicas
                        for drive in drives:
                            disk_id = drive_to_disk_map.get(drive['mountpoint'])
                            if disk_id and disk_id in disk_info_map:
                                drive['physical_disk'] = disk_info_map[disk_id]
                                drive['is_ssd'] = disk_info_map[disk_id]['is_ssd']
                                drive['disk_type'] = 'SSD' if disk_info_map[disk_id]['is_ssd'] else 'HDD'
                    
                    except Exception as e:
                        logger.warning(f"Erro ao obter informações detalhadas de discos: {str(e)}")
            
            # Se WMI não obteve sucesso, tenta método alternativo para detectar SSD
            for drive in drives:
                if drive['is_ssd'] is None:
                    drive_letter = drive['mountpoint'].rstrip('\\')
                    drive['is_ssd'] = self._is_ssd_windows_alternative(drive_letter)
                    drive['disk_type'] = 'SSD' if drive['is_ssd'] else 'HDD'
            
            # Adiciona análise de fragmentação
            for drive in drives:
                drive_letter = drive['mountpoint'].rstrip('\\')
                try:
                    fragmentation = self._get_fragmentation_windows(drive_letter)
                    if fragmentation is not None:
                        drive['fragmentation'] = fragmentation
                except Exception as e:
                    logger.debug(f"Erro ao obter fragmentação para {drive_letter}: {str(e)}")
        
        except Exception as e:
            logger.warning(f"Erro ao obter dados específicos de armazenamento para Windows: {str(e)}")
    
    def _check_if_ssd_by_name(self, model: str) -> bool:
        """
        Verifica se um disco é SSD pelo nome/modelo.
        
        Args:
            model: Nome/modelo do disco
            
        Returns:
            bool: True se for SSD, False caso contrário
        """
        model = model.lower()
        ssd_indicators = ['ssd', 'solid state', 'nvme', 'pcie', 'm.2']
        
        for indicator in ssd_indicators:
            if indicator in model:
                return True
                
        return False
    
    def _is_ssd_windows_alternative(self, drive_letter: str) -> bool:
        """
        Método alternativo para detectar SSD no Windows usando PowerShell.
        
        Args:
            drive_letter: Letra da unidade (ex: C:)
            
        Returns:
            bool: True se for SSD, False caso contrário
        """
        try:
            ps_command = f"""
            Get-PhysicalDisk | 
            Where-Object {{ 
                $DriveLetter = "{drive_letter}"
                $partition = Get-Partition | Where-Object {{ $_.DriveLetter -eq $DriveLetter.Trim(':') }}
                $disk = $partition | Get-Disk
                $_.DeviceId -eq $disk.DeviceId
            }} | 
            Select-Object -ExpandProperty MediaType
            """
            
            result = run_powershell_command(ps_command)
            
            if "SSD" in result or "Solid" in result:
                return True
            elif "HDD" in result or "Unspecified" in result:
                return False
                
            # Método alternativo 2: verificar tempo de acesso
            # Discos SSD têm tempo de acesso muito menor que HDDs
            ps_command = f"""
            $driveRoot = "{drive_letter}"
            $testFile = Join-Path -Path $driveRoot -ChildPath "ssd_test.tmp"
            try {{
                if (Test-Path $testFile) {{ Remove-Item $testFile -Force }}
                $sw = [System.Diagnostics.Stopwatch]::StartNew()
                1..10 | ForEach-Object {{
                    [System.IO.File]::WriteAllText($testFile, "SSD Test")
                    [System.IO.File]::ReadAllText($testFile)
                }}
                $sw.Stop()
                if (Test-Path $testFile) {{ Remove-Item $testFile -Force }}
                if ($sw.ElapsedMilliseconds -lt 50) {{ "SSD" }} else {{ "HDD" }}
            }}
            catch {{
                "Unknown"
            }}
            """
            
            result = run_powershell_command(ps_command)
            return "SSD" in result
        
        except Exception as e:
            logger.debug(f"Erro ao detectar tipo de disco para {drive_letter}: {str(e)}")
            return False
    
    def _get_fragmentation_windows(self, drive_letter: str) -> Optional[float]:
        """
        Obtém a fragmentação do disco no Windows.
        
        Args:
            drive_letter: Letra da unidade (ex: C:)
            
        Returns:
            Optional[float]: Percentual de fragmentação ou None se não disponível
        """
        try:
            ps_command = f"""
            $volume = Get-Volume -DriveLetter {drive_letter.replace(':', '')}
            if ($volume.FileSystem -eq 'NTFS') {{
                $defrag = Optimize-Volume -DriveLetter {drive_letter.replace(':', '')} -Analyze -Verbose 4>&1
                $defrag | Select-String -Pattern '([0-9]+)% fragmented'
            }}
            """
            
            result = run_powershell_command(ps_command)
            
            # Extrai o percentual de fragmentação
            match = re.search(r'(\d+)% fragmented', result)
            if match:
                return float(match.group(1))
                
            return None
        except Exception as e:
            logger.debug(f"Erro ao analisar fragmentação para {drive_letter}: {str(e)}")
            return None
    
    def _add_linux_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas de armazenamento para Linux.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        try:
            import subprocess
            drives = result.get('drives', [])
            
            # Mapeia pontos de montagem para dispositivos físicos
            device_map = {}
            try:
                lsblk_output = subprocess.check_output(
                    ["lsblk", "-o", "NAME,MOUNTPOINT,TYPE,FSTYPE,SIZE,MODEL,SERIAL,ROTA", "-J"],
                    universal_newlines=True
                )
                lsblk_data = json.loads(lsblk_output)
                
                # Processa dados do lsblk
                for device in lsblk_data.get('blockdevices', []):
                    self._process_lsblk_device(device, device_map, "")
            except Exception as e:
                logger.debug(f"Erro ao executar lsblk: {str(e)}")
                
            # Associa informações de discos físicos às unidades lógicas
            for drive in drives:
                mountpoint = drive['mountpoint']
                if mountpoint in device_map:
                    device_info = device_map[mountpoint]
                    drive.update(device_info)
                
                # Para dispositivos sem informações completas, tenta outros métodos
                if drive.get('is_ssd') is None:
                    # Tenta detectar SSD pelo nome do dispositivo
                    device_name = os.path.basename(drive['device'])
                    try:
                        rotational = subprocess.check_output(
                            ["cat", f"/sys/block/{device_name}/queue/rotational"],
                            universal_newlines=True
                        ).strip()
                        drive['is_ssd'] = (rotational == '0')
                        drive['disk_type'] = 'SSD' if drive['is_ssd'] else 'HDD'
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Erro ao obter dados específicos de armazenamento para Linux: {str(e)}")
    
    def _process_lsblk_device(self, device, device_map, parent_name):
        """
        Processa recursivamente os dispositivos no output do lsblk.
        
        Args:
            device: Informações do dispositivo
            device_map: Mapa de dispositivos a ser atualizado
            parent_name: Nome do dispositivo pai
        """
        device_name = device.get('name')
        full_name = f"{parent_name}{device_name}" if parent_name else device_name
        mountpoint = device.get('mountpoint')
        
        # Armazena informações do dispositivo
        if mountpoint:
            is_ssd = device.get('rota') == '0'
            model = device.get('model', '').strip()
            
            device_map[mountpoint] = {
                'physical_device': f"/dev/{full_name}",
                'is_ssd': is_ssd,
                'disk_type': 'SSD' if is_ssd else 'HDD',
                'model': model,
                'serial': device.get('serial', '').strip()
            }
        
        # Processa dispositivos filhos
        for child in device.get('children', []):
            self._process_lsblk_device(child, device_map, f"{full_name}")
    
    def _add_macos_specific_data(self, result: Dict[str, Any]) -> None:
        """
        Adiciona informações específicas de armazenamento para macOS.
        
        Args:
            result: Dicionário de resultados a ser atualizado
        """
        try:
            import subprocess
            drives = result.get('drives', [])
            
            # Obtém informações de discos físicos no macOS
            try:
                diskutil_output = subprocess.check_output(
                    ["diskutil", "list", "-plist"],
                    universal_newlines=True
                )
                
                import plistlib
                diskutil_data = plistlib.loads(diskutil_output.encode('utf-8'))
                
                disk_map = {}
                for disk_name in diskutil_data.get('AllDisksAndPartitions', []):
                    disk_id = disk_name.get('DeviceIdentifier')
                    
                    # Obtém informações detalhadas do disco
                    info_output = subprocess.check_output(
                        ["diskutil", "info", "-plist", disk_id],
                        universal_newlines=True
                    )
                    
                    disk_info = plistlib.loads(info_output.encode('utf-8'))
                    
                    is_ssd = disk_info.get('SolidState', False)
                    model = disk_info.get('MediaName', '')
                    
                    disk_map[disk_id] = {
                        'is_ssd': is_ssd,
                        'disk_type': 'SSD' if is_ssd else 'HDD',
                        'model': model,
                        'smart_status': disk_info.get('SMARTStatus', 'Unknown')
                    }
                    
                    # Adiciona informações a todas as partições deste disco
                    for partition in disk_name.get('Partitions', []):
                        partition_id = partition.get('DeviceIdentifier')
                        mount_point = partition.get('MountPoint')
                        
                        if mount_point:
                            for drive in drives:
                                if drive['mountpoint'] == mount_point:
                                    drive.update(disk_map[disk_id])
                                    drive['volume_name'] = partition.get('VolumeName', '')
                                    drive['filesystem'] = partition.get('FilesystemType', '')
            except Exception as e:
                logger.debug(f"Erro ao obter informações de disco no macOS: {str(e)}")
                
        except Exception as e:
            logger.warning(f"Erro ao obter dados específicos de armazenamento para macOS: {str(e)}")
    
    def _analyze_issues(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analisa os dados de armazenamento para identificar possíveis problemas.
        
        Args:
            data: Dados do armazenamento coletados
            
        Returns:
            List[Dict[str, Any]]: Lista de problemas encontrados
        """
        issues = []
        drives = data.get('drives', [])
        
        for drive in drives:
            # Verifica espaço livre
            percent_used = drive.get('percent', 0)
            free_mb = drive.get('free_mb', 0)
            total_mb = drive.get('total_mb', 0)
            mountpoint = drive.get('mountpoint', '')
            
            if percent_used > 95:
                issue = {
                    'description': f"Espaço crítico em {mountpoint}: {percent_used}% utilizado, apenas {free_mb:.0f} MB livres",
                    'recommendation': "Libere espaço urgentemente para evitar falhas no sistema.",
                    'severity': 'critical',
                    'drive': mountpoint
                }
                issues.append(issue)
                
                # Adiciona à lista de problemas gerais
                self.problems.append({
                    'category': 'disk',
                    'title': f'Espaço crítico em {mountpoint}',
                    'description': f"A unidade {mountpoint} está com {percent_used}% do espaço utilizado (apenas {free_mb:.0f} MB livres).",
                    'solution': "Remova arquivos desnecessários, execute a limpeza de disco ou transfira dados para outro dispositivo.",
                    'impact': 'system',
                    'severity': 'critical'
                })
                
                # Reduz a pontuação drasticamente
                self.score -= 30
            elif percent_used > 90:
                issue = {
                    'description': f"Pouco espaço em {mountpoint}: {percent_used}% utilizado, {free_mb:.0f} MB livres",
                    'recommendation': "Libere espaço para melhorar o desempenho e evitar problemas futuros.",
                    'severity': 'high',
                    'drive': mountpoint
                }
                issues.append(issue)
                
                # Adiciona à lista de problemas gerais
                self.problems.append({
                    'category': 'disk',
                    'title': f'Pouco espaço em {mountpoint}',
                    'description': f"A unidade {mountpoint} está com {percent_used}% do espaço utilizado ({free_mb:.0f} MB livres).",
                    'solution': "Remova arquivos temporários e desnecessários ou execute a limpeza de disco.",
                    'impact': 'performance',
                    'severity': 'high'
                })
                
                # Reduz a pontuação
                self.score -= 15
            elif percent_used > 80:
                issue = {
                    'description': f"Espaço moderadamente baixo em {mountpoint}: {percent_used}% utilizado",
                    'recommendation': "Monitore o uso de espaço em disco nesta unidade.",
                    'severity': 'medium',
                    'drive': mountpoint
                }
                issues.append(issue)
                
                # Reduz a pontuação levemente
                self.score -= 5
            
            # Verifica fragmentação (se disponível, apenas para HDDs)
            is_ssd = drive.get('is_ssd', False)
            fragmentation = drive.get('fragmentation')
            
            if not is_ssd and fragmentation is not None and fragmentation > 20:
                issue = {
                    'description': f"Alta fragmentação em {mountpoint}: {fragmentation:.0f}%",
                    'recommendation': "Execute a desfragmentação de disco para melhorar o desempenho.",
                    'severity': 'medium' if fragmentation < 40 else 'high',
                    'drive': mountpoint
                }
                issues.append(issue)
                
                if fragmentation > 40:
                    # Adiciona à lista de problemas gerais
                    self.problems.append({
                        'category': 'disk',
                        'title': f'Alta fragmentação em {mountpoint}',
                        'description': f"A unidade {mountpoint} está com {fragmentation:.0f}% de fragmentação.",
                        'solution': "Execute a desfragmentação de disco para melhorar o desempenho.",
                        'impact': 'performance',
                        'severity': 'high'
                    })
                    
                    # Reduz a pontuação
                    self.score -= 10
                else:
                    # Reduz a pontuação levemente
                    self.score -= 5
            
            # Verifica SMART status (apenas macOS por enquanto)
            smart_status = drive.get('smart_status')
            if smart_status and smart_status != 'Verified':
                issue = {
                    'description': f"Status SMART em {mountpoint}: {smart_status}",
                    'recommendation': "O disco pode estar com problemas de hardware. Faça backup dos dados e considere substituir o disco.",
                    'severity': 'critical',
                    'drive': mountpoint
                }
                issues.append(issue)
                
                # Adiciona à lista de problemas gerais
                self.problems.append({
                    'category': 'disk',
                    'title': f'Possível falha de hardware em {mountpoint}',
                    'description': f"A unidade {mountpoint} reportou problemas no diagnóstico SMART: {smart_status}.",
                    'solution': "Faça backup dos seus dados imediatamente e considere substituir o disco.",
                    'impact': 'data_loss',
                    'severity': 'critical'
                })
                
                # Reduz a pontuação drasticamente
                self.score -= 40
        
        return issues
    
    def _calculate_health_score(self, data: Dict[str, Any]) -> int:
        """
        Calcula a pontuação de saúde do armazenamento com base nos dados coletados.
        
        Args:
            data: Dados do armazenamento coletados
            
        Returns:
            int: Pontuação de saúde (0-100)
        """
        # Parte da pontuação inicial de 100 e vai deduzindo conforme problemas
        score = self.score
        
        # Garante que o score esteja entre 0 e 100
        return max(0, min(100, score)) 