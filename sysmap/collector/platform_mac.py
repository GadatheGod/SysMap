"""macOS-specific system data collectors."""

import os
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

    # system_profiler SPHardwareDataType
    hw = run_cmd(['system_profiler', 'SPHardwareDataType'])
    if hw:
        for line in hw.split('\n'):
            if 'Hardware Overview' in line:
                pass
            if 'Model Name:' in line: info.model = line.split(': ')[1].strip()
            if 'Model Identifier:' in line: info.model += ' - ' + line.split(': ')[1].strip()
            if 'Processor Name:' in line: info.manufacturer = line.split(': ')[1].strip()
            if 'Chip:' in line: info.manufacturer = line.split(': ')[1].strip()
            if 'Memory:' in line: pass  # handled by psutil
            if 'Serial Number:' in line: info.serial = line.split(': ')[1].strip()
            if 'UUID:' in line: info.uuid = line.split(': ')[1].strip()

    # SWDPInfo SPPlatformDataType
    platform = run_cmd(['system_profiler', 'SPPlatformDataType'])
    if platform:
        for line in platform.split('\n'):
            if 'Board Number:' in line: info.motherboard_model = line.split(': ')[1].strip()
            if 'ROM Version:' in line: info.bios_version = line.split(': ')[1].strip()

    # system_profiler SPSoftwareDataType
    sw = run_cmd(['system_profiler', 'SPSoftwareDataType'])
    if sw:
        for line in sw.split('\n'):
            if 'System Version:' in line: pass

    info.uefi_mode = True  # Macs are always UEFI
    return info


def get_gpus() -> List[GpuInfo]:
    gpus = []
    gpu_info = run_cmd(['system_profiler', 'SPDisplaysDataType'])
    if gpu_info:
        gpu = GpuInfo()
        gpu.name = ""
        gpu.architecture = "Apple" if 'Apple' in gpu_info else ""
        for line in gpu_info.split('\n'):
            if 'Chipset Model:' in line: gpu.name = line.split(': ')[1].strip()
            if 'GPU Type:' in line: gpu.architecture = line.split(': ')[1].strip()
            if 'VRAM:' in line:
                vram_str = line.split(': ')[1].strip()
                gpu.vram_bytes = parse_bytes(vram_str)
            if 'Display Type:' in line: gpu.hardware_acceleration = True
        if gpu.name:
            gpus.append(gpu)
    return gpus


def get_monitors() -> List[MonitorInfo]:
    monitors = []
    displays = run_cmd(['system_profiler', 'SPDisplaysDataType'])
    if displays:
        monitor = MonitorInfo()
        for line in displays.split('\n'):
            if 'Resolution:' in line:
                res = line.split(': ')[1].strip()
                match = __import__('re').search(r'(\d+) x (\d+)', res)
                if match:
                    monitor.resolution_width = int(match.group(1))
                    monitor.resolution_height = int(match.group(2))
            if 'Monitor Serial Number:' in line:
                monitor.serial = line.split(': ')[1].strip()
            if 'Display Type:' in line:
                monitor.panel_type = line.split(': ')[1].strip()
            if 'Rotation:' in line:
                monitor.rotation = line.split(': ')[1].strip()
        if monitor.resolution_width:
            monitors.append(monitor)
    return monitors


def get_disks() -> List[DiskInfo]:
    disks = []
    smart = run_cmd(['diskutil', 'info', 'disk0'])
    if smart:
        disk = DiskInfo()
        for line in smart.split('\n'):
            if 'Device Name:' in line: disk.name = line.split(': ')[1].strip()
            if 'Model:' in line: disk.model = line.split(': ')[1].strip()
            if 'Device Identifier:' in line: disk.name = line.split(': ')[1].strip()
            if 'SMART Status:' in line: disk.health_status = line.split(': ')[1].strip()
            if 'Total Size:' in line: disk.capacity_bytes = parse_bytes(line.split(': ')[1].strip())
            if 'Transfer Rate:' in line: disk.interface = line.split(': ')[1].strip()
        if disk.name:
            disks.append(disk)
    return disks


def get_partitions() -> List[PartitionInfo]:
    partitions = []
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
            adapter.adapter_type = "WiFi" if 'en0' in name or 'en1' in name else "Ethernet"
            adapter.speed_mbps = int(stats.speed * 1000000) if stats.speed else 0
            adapter.connection_state = "UP" if stats.isup else "DOWN"
        adapters.append(adapter)
    return adapters


def get_bluetooth() -> Optional[BluetoothDeviceInfo]:
    info = BluetoothDeviceInfo()
    bt = run_cmd(['system_profiler', 'SPBluetoothDataType'])
    if bt and 'None' not in bt:
        info.adapter_name = "Bluetooth"
        for line in bt.split('\n'):
            if 'Product Name:' in line: info.adapter_name = line.split(': ')[1].strip()
            if 'Manufacturer:' in line: info.adapter_manufacturer = line.split(': ')[1].strip()
            if 'Version:' in line: info.adapter_version = line.split(': ')[1].strip()
    return info if info.adapter_name else None


def get_battery() -> Optional[BatteryInfo]:
    info = BatteryInfo()
    bcl = run_cmd(['pmset', '-g', 'batt'])
    if bcl:
        for line in bcl.split(';'):
            if 'charging' in line or 'discharging' in line or 'full' in line:
                info.state = 'charging' if 'charging' in line else 'discharging' if 'discharging' in line else 'full'
            if '%' in line:
                match = __import__('re').search(r'(\d+)%', line)
                if match:
                    info.charge_percent = float(match.group(1))

    powerinfo = run_cmd(['system_profiler', 'SPPowerDataType'])
    if powerinfo:
        for line in powerinfo.split('\n'):
            if 'Cycle Count:' in line:
                match = __import__('re').search(r'(\d+)', line.split(': ')[1].strip())
                if match: info.cycle_count = int(match.group(1))
            if 'Condition:' in line:
                info.health_percent = 100.0 if 'Normal' in line else 50.0
            if 'Amperage:' in line:
                match = __import__('re').search(r'(\d+)', line.split(': ')[1].strip())
                if match: info.voltage = float(match.group(1)) / 1000.0 if match.group(1) else 0.0

    info.name = "Built-in Battery"
    return info if info.charge_percent > 0 or info.state else None


def get_security() -> SecurityInfo:
    info = SecurityInfo()
    csr = run_cmd(['csrutil', 'status'])
    if csr:
        info.vbs_running = 'enabled' in csr.lower()
    sip = run_cmd(['system_profiler', 'SPSecurityDataType'])
    if sip:
        for line in sip.split('\n'):
            if 'Secure Boot:' in line:
                info.secure_boot = "Enabled" if 'Allow' in line else "Disabled"
            if 'FileVault:' in line:
                info.bitlocker_status = "On" if 'On' in line else "Off"
    return info


def get_virtualization() -> VirtualizationInfo:
    info = VirtualizationInfo()
    try:
        out = run_cmd(['docker', '--version'])
        if out:
            info.docker_installed = True
            info.docker_version = out.split()[-1] if out else ""
    except Exception:
        pass
    return info


def get_wireless() -> List[WirelessInfo]:
    wireless = []
    wifi = run_cmd(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-I'])
    if wifi:
        info = WirelessInfo()
        for line in wifi.split('\n'):
            if 'ssid:' in line: info.current_ssid = line.split(': ')[1].strip()
            if 'bssid:' in line: info.current_bssid = line.split(': ')[1].strip()
            if 'rate:' in line:
                match = __import__('re').search(r'(\d+)', line.split(': ')[1].strip())
                if match: info.tx_rate_mbps = float(match.group(1))
            if 'signal:' in line:
                match = __import__('re').search(r'(-?\d+)', line.split(': ')[1].strip())
                if match: info.rssi_dbm = int(match.group(1))
            if 'channel:' in line:
                match = __import__('re').search(r'(\d+)', line.split(': ')[1].strip())
                if match: info.channel = int(match.group(1))
            if 'auth:' in line: info.security_type = line.split(': ')[1].strip()
        info.adapter_name = "Wi-Fi"
        wireless.append(info)
    return wireless


def get_installed_software() -> List[InstalledSoftware]:
    software = []
    brew_list = run_cmd(['brew', 'list', '--versions'])
    if brew_list:
        for line in brew_list.split('\n'):
            parts = line.split()
            if len(parts) >= 2:
                software.append(InstalledSoftware(
                    name=parts[0],
                    version=parts[1],
                    publisher="Homebrew",
                    architecture="arm64" if 'arm' in os.uname().machine else "x86_64"
                ))
    return software[:100]
