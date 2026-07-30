"""System data collector engine."""

import platform
from typing import Dict, Any

from .models import SystemSnapshot
from .shared import get_platform, get_timestamp, get_cpu_info, get_memory_info, get_os_info, get_sensors, get_processes, get_total_processes
from .platform_linux import (
    get_system_info as get_system_info_linux, get_gpus as get_gpus_linux,
    get_monitors as get_monitors_linux, get_disks as get_disks_linux,
    get_partitions as get_partitions_linux, get_network_adapters as get_network_adapters_linux,
    get_usb_devices as get_usb_devices_linux, get_usb_controllers as get_usb_controllers_linux,
    get_audio_devices as get_audio_devices_linux, get_pci_devices as get_pci_devices_linux,
    get_bluetooth as get_bluetooth_linux, get_battery as get_battery_linux,
    get_security as get_security_linux, get_installed_software as get_installed_software_linux,
    get_services as get_services_linux, get_virtualization as get_virtualization_linux,
    get_wireless as get_wireless_linux, get_cooling as get_cooling_linux
)
from .platform_windows import (
    get_system_info as get_system_info_windows, get_gpus as get_gpus_windows,
    get_monitors as get_monitors_windows, get_disks as get_disks_windows,
    get_partitions as get_partitions_windows, get_network_adapters as get_network_adapters_windows,
    get_installed_software as get_installed_software_windows, get_security as get_security_windows,
    get_virtualization as get_virtualization_windows, get_wireless as get_wireless_windows,
    get_cooling as get_cooling_windows
)
from .platform_mac import (
    get_system_info as get_system_info_mac, get_gpus as get_gpus_mac,
    get_monitors as get_monitors_mac, get_disks as get_disks_mac,
    get_partitions as get_partitions_mac, get_network_adapters as get_network_adapters_mac,
    get_bluetooth as get_bluetooth_mac, get_battery as get_battery_mac,
    get_security as get_security_mac, get_virtualization as get_virtualization_mac,
    get_wireless as get_wireless_mac, get_installed_software as get_installed_software_mac
)


def collect_all() -> SystemSnapshot:
    """Collect all system data and return a complete snapshot."""
    plat = get_platform()

    # Platform-specific collectors
    if plat == 'linux':
        get_system = get_system_info_linux
        get_gpus = get_gpus_linux
        get_monitors = get_monitors_linux
        get_disks = get_disks_linux
        get_partitions = get_partitions_linux
        get_network = get_network_adapters_linux
        get_usb_dev = get_usb_devices_linux
        get_usb_ctrl = get_usb_controllers_linux
        get_audio = get_audio_devices_linux
        get_pci = get_pci_devices_linux
        get_bluetooth = get_bluetooth_linux
        get_battery = get_battery_linux
        get_security = get_security_linux
        get_software = get_installed_software_linux
        get_services = get_services_linux
        get_virtual = get_virtualization_linux
        get_wireless = get_wireless_linux
        get_cooling = get_cooling_linux
    elif plat == 'windows':
        get_system = get_system_info_windows
        get_gpus = get_gpus_windows
        get_monitors = get_monitors_windows
        get_disks = get_disks_windows
        get_partitions = get_partitions_windows
        get_network = get_network_adapters_windows
        get_usb_dev = lambda: []
        get_usb_ctrl = lambda: []
        get_audio = lambda: []
        get_pci = lambda: []
        get_bluetooth = lambda: None
        get_battery = lambda: None
        get_security = get_security_windows
        get_software = get_installed_software_windows
        get_services = lambda: []
        get_virtual = get_virtualization_windows
        get_wireless = get_wireless_windows
        get_cooling = get_cooling_linux
    elif plat == 'darwin':
        get_system = get_system_info_mac
        get_gpus = get_gpus_mac
        get_monitors = get_monitors_mac
        get_disks = get_disks_mac
        get_partitions = get_partitions_mac
        get_network = get_network_adapters_mac
        get_usb_dev = lambda: []
        get_usb_ctrl = lambda: []
        get_audio = lambda: []
        get_pci = lambda: []
        get_bluetooth = get_bluetooth_mac
        get_battery = get_battery_mac
        get_security = get_security_mac
        get_software = get_installed_software_mac
        get_services = lambda: []
        get_virtual = get_virtualization_mac
        get_wireless = get_wireless_mac
        get_cooling = lambda: []
    else:
        raise ValueError(f"Unsupported platform: {plat}")

    # Collect all data
    system = get_system()
    cpu = get_cpu_info()
    memory = get_memory_info()
    os_info = get_os_info()
    sensors = get_sensors()
    processes = get_processes()
    total_procs, total_threads = get_total_processes()
    gpus = get_gpus()
    monitors = get_monitors()
    disks = get_disks()
    partitions = get_partitions()
    network = get_network()
    usb_dev = get_usb_dev()
    usb_ctrl = get_usb_ctrl()
    audio = get_audio()
    pci = get_pci()
    bluetooth = get_bluetooth()
    battery = get_battery()
    security = get_security()
    software = get_software()
    services = get_services()
    virtual = get_virtual()
    wireless = get_wireless()
    cooling = get_cooling()

    return SystemSnapshot(
        timestamp=get_timestamp(),
        platform=plat,
        system=system,
        cpu=cpu,
        memory=memory,
        gpus=gpus,
        monitors=monitors,
        disks=disks,
        partitions=partitions,
        network_adapters=network,
        usb_devices=usb_dev,
        usb_controllers=usb_ctrl,
        audio_devices=audio,
        pci_devices=pci,
        bluetooth=bluetooth,
        battery=battery,
        sensors=sensors,
        os_info=os_info,
        security=security,
        installed_software=software,
        processes=processes,
        services=services,
        virtualization=virtual,
        wireless=wireless,
        cooling=cooling,
        total_processes=total_procs,
        total_threads=total_threads,
    )


def collect_summary() -> Dict[str, Any]:
    """Collect a quick summary of system info."""
    snapshot = collect_all()

    return {
        "platform": snapshot.platform,
        "hostname": snapshot.os_info.hostname,
        "cpu": snapshot.cpu.name,
        "ram_gb": round(snapshot.memory.total_physical_bytes / (1024**3), 1),
        "gpu": snapshot.gpus[0].name if snapshot.gpus else "N/A",
        "storage_gb": sum(d.capacity_bytes for d in snapshot.disks) / (1024**3),
        "os": f"{snapshot.os_info.platform} {snapshot.os_info.platform_version}",
        "uptime_seconds": 0,
        "processes": snapshot.total_processes,
    }
