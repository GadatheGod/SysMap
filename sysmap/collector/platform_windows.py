"""Windows-specific system data collectors."""

import os
import re
import subprocess
import psutil
from typing import List, Dict, Any, Optional

from .shared import run_cmd, parse_bytes
from .models import (
    SystemInfo, GpuInfo, MonitorInfo, DiskInfo, PartitionInfo,
    NetworkAdapterInfo, UsbDeviceInfo, UsbControllerInfo, AudioDeviceInfo,
    PciDeviceInfo, BluetoothDeviceInfo, BatteryInfo, SecurityInfo,
    InstalledSoftware, InstalledDriver, ServiceInfo, PowerPlanInfo,
    VirtualizationInfo, InputDeviceInfo, WirelessInfo, CoolingInfo,
    SensorReading
)


def get_system_info() -> SystemInfo:
    info = SystemInfo()
    try:
        out = run_cmd(['wmic', 'computersystem', 'get', 'Manufacturer,Model,SerialNumber,SKUNumber,UUID,SystemFamily', '/format:list'])
        if out:
            for line in out.split('\n'):
                if 'Manufacturer=' in line: info.manufacturer = line.split('=')[1].strip()
                if 'Model=' in line: info.model = line.split('=')[1].strip()
                if 'SerialNumber=' in line: info.serial = line.split('=')[1].strip()
                if 'SKUNumber=' in line: info.sku = line.split('=')[1].strip()
                if 'UUID=' in line: info.uuid = line.split('=')[1].strip()
                if 'SystemFamily=' in line: info.family = line.split('=')[1].strip()
    except Exception:
        pass

    try:
        out = run_cmd(['wmic', 'bios', 'get', 'Manufacturer,Version,ReleaseDate,RomSize', '/format:list'])
        if out:
            for line in out.split('\n'):
                if 'Manufacturer=' in line: info.bios_vendor = line.split('=')[1].strip()
                if 'Version=' in line: info.bios_version = line.split('=')[1].strip()
                if 'ReleaseDate=' in line: info.bios_date = line.split('=')[1].strip()
                if 'RomSize=' in line: info.bios_rom_size_bytes = int(line.split('=')[1].strip()) * 1024 * 1024 if line.split('=')[1].strip().isdigit() else 0
    except Exception:
        pass

    try:
        out = run_cmd(['wmic', 'baseboard', 'get', 'Manufacturer,Product,Version,SerialNumber', '/format:list'])
        if out:
            for line in out.split('\n'):
                if 'Manufacturer=' in line: info.motherboard_manufacturer = line.split('=')[1].strip()
                if 'Product=' in line: info.motherboard_model = line.split('=')[1].strip()
                if 'Version=' in line: info.motherboard_version = line.split('=')[1].strip()
                if 'SerialNumber=' in line: info.motherboard_serial = line.split('=')[1].strip()
    except Exception:
        pass

    try:
        out = run_cmd(['wmic', 'chassis', 'get', 'ChassisTypes,Manufacturer,SerialNumber', '/format:list'])
        if out:
            for line in out.split('\n'):
                if 'Manufacturer=' in line: info.chassis_manufacturer = line.split('=')[1].strip()
                if 'SerialNumber=' in line: info.chassis_serial = line.split('=')[1].strip()
    except Exception:
        pass

    info.uefi_mode = os.path.exists('C:\\Windows\\System32\\efi')
    return info


def get_gpus() -> List[GpuInfo]:
    gpus = []
    try:
        out = run_cmd(['wmic', 'desktopgpu', 'get', 'Name,DriverVersion,AdapterRAM,DisplayMemory,VRAM', '/format:list'])
        if out:
            gpu = GpuInfo()
            gpu.name = ""
            for line in out.split('\n'):
                if 'Name=' in line: gpu.name = line.split('=')[1].strip()
                if 'DriverVersion=' in line: gpu.driver_version = line.split('=')[1].strip()
                if 'AdapterRAM=' in line: gpu.vram_bytes = int(line.split('=')[1].strip())
                if 'VRAM=' in line: gpu.vram_bytes = int(line.split('=')[1].strip())
            if gpu.name:
                gpus.append(gpu)
    except Exception:
        pass

    # Try PowerShell for more details
    try:
        out = run_cmd(['powershell', '-Command', 'Get-CimInstance', 'Win32_VideoController'])
        if out:
            for line in out.split('\n'):
                if 'Name=' in line:
                    gpu = GpuInfo()
                    gpu.name = line.split('=')[1].strip()
                    gpu.hardware_acceleration = True
                    if not any(g.name == gpu.name for g in gpus):
                        gpus.append(gpu)
    except Exception:
        pass

    return gpus


def get_monitors() -> List[MonitorInfo]:
    monitors = []
    try:
        out = run_cmd(['powershell', '-Command', 'Get-CimInstance', 'Win32_DesktopMonitor'])
        if out:
            for line in out.split('\n'):
                if 'MonitorManufacturer=' in line:
                    m = MonitorInfo()
                    m.manufacturer = line.split('=')[1].strip() or "Unknown"
                    monitors.append(m)
    except Exception:
        pass

    # Screen resolution
    try:
        from screeninfo import get_monitors
        for m in get_monitors():
            monitor = MonitorInfo()
            monitor.resolution_width = m.width
            monitor.resolution_height = m.height
            monitor.current_refresh_hz = m.refresh_rate or 60
            monitor.is_primary = m.is_primary
            monitors.append(monitor)
    except ImportError:
        pass

    return monitors


def get_disks() -> List[DiskInfo]:
    disks = []
    try:
        out = run_cmd(['wmic', 'diskdrive', 'get', 'Model,Size,SerialNumber,FirmwareVersion,InterfaceType,MediaLoaded', '/format:list'])
        if out:
            disk = DiskInfo()
            for line in out.split('\n'):
                if 'Model=' in line: disk.model = line.split('=')[1].strip()
                if 'Size=' in line: disk.capacity_bytes = int(line.split('=')[1].strip())
                if 'SerialNumber=' in line: disk.serial = line.split('=')[1].strip()
                if 'FirmwareVersion=' in line: disk.firmware = line.split('=')[1].strip()
                if 'InterfaceType=' in line: disk.interface = line.split('=')[1].strip()
            if disk.model:
                disks.append(disk)
    except Exception:
        pass
    return disks


def get_partitions() -> List[PartitionInfo]:
    partitions = []
    try:
        for mount in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(mount.mountpoint)
                partition = PartitionInfo(
                    name=mount.device,
                    filesystem=mount.fstype,
                    size_bytes=usage.total,
                    used_bytes=usage.used,
                    free_bytes=usage.free,
                    mount_point=mount.mountpoint,
                    usage_percent=usage.percent,
                )
                partitions.append(partition)
            except (PermissionError, FileNotFoundError):
                continue
    except Exception:
        pass
    return partitions


def get_network_adapters() -> List[NetworkAdapterInfo]:
    adapters = []
    net_io = psutil.net_io_counters(pernic=True)
    net_addr = psutil.net_if_addrs()
    net_stats = psutil.net_if_stats()

    for name, io in net_io.items():
        adapter = NetworkAdapterInfo()
        adapter.name = name
        adapter.io_stats = {
            'rx_bytes': io.bytes_recv, 'tx_bytes': io.bytes_sent,
            'rx_packets': io.packets_recv, 'tx_packets': io.packets_sent,
        }
        addrs = net_addr.get(name, [])
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                adapter.mac_address = addr.address
            elif addr.family == 2:
                adapter.ipv4_address = addr.address
        stats = net_stats.get(name)
        if stats:
            adapter.adapter_type = "WiFi" if 'wi' in name.lower() or 'wireless' in name.lower() else "Ethernet"
            adapter.speed_mbps = int(stats.speed * 1000000) if stats.speed else 0
            adapter.connection_state = "UP" if stats.isup else "DOWN"
        adapters.append(adapter)
    return adapters


def get_installed_software() -> List[InstalledSoftware]:
    software = []
    try:
        out = run_cmd(['powershell', '-Command', 'Get-ItemProperty', 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*', '-ErrorAction', 'SilentlyContinue', '|', 'Select-Object', 'DisplayName,DisplayVersion,Publisher,InstallDate', '|', 'Format-List'])
        if out:
            pkg = InstalledSoftware()
            for line in out.split('\n'):
                if 'DisplayName=' in line: pkg.name = line.split('=')[1].strip()
                if 'DisplayVersion=' in line: pkg.version = line.split('=')[1].strip()
                if 'Publisher=' in line: pkg.publisher = line.split('=')[1].strip()
                if 'InstallDate=' in line: pkg.install_date = line.split('=')[1].strip()
                if pkg.name:
                    software.append(pkg)
                    pkg = InstalledSoftware()
    except Exception:
        pass
    return software[:100]


def get_security() -> SecurityInfo:
    info = SecurityInfo()
    try:
        out = run_cmd(['powershell', '-Command', 'Get-CimInstance', 'Win32_Tpm'])
        if out:
            info.tpm_present = True
            info.tpm_enabled = True
            info.tpm_activated = True
            info.tpm_version = "2.0"
        out2 = run_cmd(['powershell', '-Command', 'Get-SecureBootUEFI'])
        if out2:
            info.secure_boot = "Enabled"
    except Exception:
        pass
    try:
        out = run_cmd(['powershell', '-Command', 'Get-MpComputerStatus'])
        if out:
            info.antivirus_name = "Windows Defender"
            info.antivirus_status = "Running"
    except Exception:
        pass
    try:
        out = run_cmd(['powershell', '-Command', 'Get-NetFirewallProfile'])
        if out:
            info.firewall_enabled = True
            info.firewall_profiles = ["Domain", "Private", "Public"]
    except Exception:
        pass
    return info


def get_virtualization() -> VirtualizationInfo:
    info = VirtualizationInfo()
    try:
        out = run_cmd(['powershell', '-Command', 'Get-WindowsOptionalFeature', '-Online', '-FeatureName', 'Microsoft-Hyper-V'])
        if out and 'Enabled' in out:
            info.hyper_v_enabled = True
        out2 = run_cmd(['docker', '--version'])
        if out2:
            info.docker_installed = True
            info.docker_version = out2.split()[-1] if out2 else ""
    except Exception:
        pass
    return info


def get_wireless() -> List[WirelessInfo]:
    wireless = []
    try:
        out = run_cmd(['powershell', '-Command', 'Get-NetAdapter | Where-Object {$_.InterfaceDescription -like \'*Wireless*\' or $_.InterfaceDescription -like \'*WiFi*\'}'])
        if out:
            info = WirelessInfo()
            info.adapter_name = "WiFi Adapter"
            wireless.append(info)
    except Exception:
        pass
    return wireless


def get_cooling() -> List[CoolingInfo]:
    cooling = []
    try:
        out = run_cmd(['powershell', '-Command', 'Get-CimInstance', 'Win32_Fan'])
        if out:
            info = CoolingInfo()
            info.fan_name = "System Fan"
            cooling.append(info)
    except Exception:
        pass
    return cooling
