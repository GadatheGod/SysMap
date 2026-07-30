"""Cross-platform utilities for system collection."""

import platform
import subprocess
import socket
import os
import json
import psutil
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from .models import (
    SystemSnapshot, SystemInfo, CpuInfo, MemoryInfo, GpuInfo,
    MonitorInfo, DiskInfo, PartitionInfo, NetworkAdapterInfo,
    UsbDeviceInfo, UsbControllerInfo, AudioDeviceInfo, PciDeviceInfo,
    BluetoothDeviceInfo, BatteryInfo, SensorReading, OsInfo,
    SecurityInfo, InstalledSoftware, InstalledDriver, ProcessInfo,
    ServiceInfo, PowerPlanInfo, VirtualizationInfo, InputDeviceInfo,
    WirelessInfo, CoolingInfo
)


def get_platform() -> str:
    return platform.system().lower()


def run_cmd(cmd: List[str], timeout: int = 10) -> Optional[str]:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def run_cmd_combined(cmd: List[str], timeout: int = 10) -> Optional[str]:
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout,
            stderr=subprocess.STDOUT
        )
        return result.stdout.strip() if result.returncode == 0 else None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def parse_bytes(s: str) -> int:
    s = s.strip().upper()
    multipliers = {'B': 1, 'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
    for char, mult in sorted(multipliers.items(), key=lambda x: -len(x[0])):
        if s.endswith(char) and s[:-1].strip().isdigit():
            return int(s[:-1].strip()) * mult
    if s.isdigit():
        return int(s)
    return 0


def get_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_cpu_info() -> CpuInfo:
    info = CpuInfo()
    info.name = platform.processor() or ""
    info.brand = platform.platform()

    try:
        import cpuinfo
        cpu_raw = cpuinfo.get_cpu_info()
        if cpu_raw:
            info.name = cpu_raw.get('brand_raw', '') or info.name
            vendor = cpu_raw.get('vendor_id', '') or ''
            if vendor:
                info.manufacturer = vendor.split()[0]
            info.codename = cpu_raw.get('family_name', '') or cpu_raw.get('stepping', '')
            info.socket = cpu_raw.get('socket', '')
            info.hyperthreading = cpu_raw.get('hypermthreading', False)
            info.tdp_watts = float(cpu_raw.get('stepping', 0))
            info.microcode_version = cpu_raw.get('microcode', '')

            flags = cpu_raw.get('flags', [])
            ext_map = {
                'sse': 'SSE', 'sse2': 'SSE2', 'sse3': 'SSE3',
                'ssse3': 'SSSE3', 'sse4.1': 'SSE4.1', 'sse4.2': 'SSE4.2',
                'avx': 'AVX', 'avx2': 'AVX2', 'avx-512f': 'AVX-512',
                'fma': 'FMA', 'bmi1': 'BMI1', 'bmi2': 'BMI2',
                'aes': 'AES', 'pclmul': 'PCLMUL', 'mmx': 'MMX',
                'popcnt': 'POPCNT', 'rdrand': 'RDRAND', 'rdseed': 'RDSEED',
                'sha': 'SHA', 'nx': 'NX Bit', 'lm': 'Long Mode',
                'vmx': 'VT-x', 'svm': 'AMD-V', 'sve': 'SVE', 'neon': 'NEON',
            }
            for flag in flags:
                if flag.lower() in ext_map:
                    info.extensions.append(ext_map[flag.lower()])

            info.virtualization = 'vmx' in flags or 'svm' in flags

            cpu_id = cpu_raw.get('cpu_id', {})
            if cpu_id:
                info.cpu_id = {
                    'vendor': cpu_id.get('raw_string', ''),
                    'brand': cpu_id.get('brand_string', ''),
                    'family': cpu_id.get('family', ''),
                    'model': cpu_id.get('model', ''),
                    'stepping': cpu_id.get('stepping', ''),
                }
    except ImportError:
        pass

    info.physical_cores = psutil.cpu_count(logical=False) or 0
    info.logical_cores = psutil.cpu_count(logical=True) or 0
    info.threads = info.logical_cores

    try:
        freq = psutil.cpu_freq()
        if freq:
            info.base_clock_mhz = freq.current or freq.min or 0.0
            info.boost_clock_mhz = freq.max or 0.0
    except (AttributeError, psutil.NoSuchProcess):
        pass

    perf = psutil.cpu_stats()
    try:
        caches = psutil.cpu_stats()
    except Exception:
        pass

    info.l1_cache_kb = 0
    info.l2_cache_kb = 0
    info.l3_cache_kb = 0

    try:
        with open('/sys/devices/system/cpu/cpu0/cache/index0/size', 'r') as f:
            val = f.read().strip()
            if val.endswith('K'):
                info.l1_cache_kb = int(val[:-1])
        with open('/sys/devices/system/cpu/cpu0/cache/index1/size', 'r') as f:
            val = f.read().strip()
            if val.endswith('K'):
                info.l2_cache_kb = int(val[:-1])
        with open('/sys/devices/system/cpu/cpu0/cache/index2/size', 'r') as f:
            val = f.read().strip()
            if val.endswith('K'):
                info.l3_cache_kb = int(val[:-1])
    except (FileNotFoundError, PermissionError, IndexError):
        pass

    info.per_core_current_freq = [freq.current for freq in psutil.cpu_freq(percpu=True)] if psutil.cpu_freq(percpu=True) else []
    info.per_core_utilization = [psutil.cpu_percent(percpu=True)[i] for i in range(len(psutil.cpu_percent(percpu=True)))]

    return info


def get_memory_info() -> MemoryInfo:
    info = MemoryInfo()
    vm = psutil.virtual_memory()
    info.total_physical_bytes = vm.total
    info.available_physical_bytes = vm.available
    info.total_virtual_bytes = vm.total  # swap included
    info.available_virtual_bytes = vm.available

    swap = psutil.swap_memory()
    info.total_swap_bytes = swap.total
    info.available_swap_bytes = swap.free

    try:
        freq = psutil.cpu_freq()
        if freq and freq.current > 0:
            info.memory_speed_mts = int(freq.current)
    except (AttributeError, psutil.NoSuchProcess):
        pass

    return info


def get_os_info() -> OsInfo:
    info = OsInfo()
    info.hostname = socket.gethostname() or ""
    info.architecture = platform.machine() or ""
    info.platform = platform.platform() or ""
    info.platform_version = platform.version() or ""
    info.node = platform.node() or ""
    info.processor = platform.processor() or ""
    info.machine = platform.machine() or ""
    info.boot_time = datetime.fromtimestamp(psutil.boot_time()).isoformat() if psutil.boot_time() else ""

    system = platform.uname()
    info.kernel_version = system.version or ""
    info.kernel_name = system.system or ""

    try:
        import getpass
        info.username = getpass.getuser()
    except Exception:
        info.username = ""

    info.timezone = str(datetime.now().astimezone().tzinfo) or ""

    try:
        info.boot_time = datetime.fromtimestamp(psutil.boot_time()).isoformat()
    except Exception:
        pass

    return info


def get_sensors() -> List[SensorReading]:
    sensors = []

    try:
        temps = psutil.sensors_temperatures()
        if temps:
            for label, entries in temps.items():
                for entry in entries:
                    sensors.append(SensorReading(
                        name=f"{label} - {entry.label or entry._label or 'Unknown'}",
                        category="temperature",
                        value=entry.current,
                        unit="°C",
                        critical=entry.high or 0.0
                    ))
    except (AttributeError, Exception):
        pass

    try:
        fans = psutil.sensors_fans()
        if fans:
            for label, entries in fans.items():
                for entry in entries:
                    sensors.append(SensorReading(
                        name=f"{label} Fan",
                        category="fan",
                        value=entry[0] if isinstance(entry, tuple) else entry,
                        unit=" RPM",
                        critical=0.0
                    ))
    except (AttributeError, Exception):
        pass

    try:
        voltages = psutil.sensors_voltage()
        if voltages:
            for label, entries in voltages.items():
                for entry in entries:
                    sensors.append(SensorReading(
                        name=f"{label} Voltage",
                        category="voltage",
                        value=entry,
                        unit="V",
                        critical=0.0
                    ))
    except (AttributeError, Exception):
        pass

    return sensors


def get_processes(top_n: int = 20) -> List[ProcessInfo]:
    procs = []
    try:
        for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent',
                                          'memory_info', 'create_time', 'cmdline', 'num_threads',
                                          'io_counters']):
            try:
                p = proc.info
                io = p.get('io_counters')
                procs.append(ProcessInfo(
                    pid=p['pid'],
                    name=p['name'] or '',
                    path='',
                    user=p.get('username') or '',
                    cpu_percent=p.get('cpu_percent') or 0.0,
                    memory_bytes=p.get('memory_info').rss if p.get('memory_info') else 0,
                    threads=p.get('num_threads') or 0,
                    status=p.get('status') or '',
                    create_time=datetime.fromtimestamp(p.get('create_time') or 0).isoformat() if p.get('create_time') else '',
                    command_line=' '.join(p.get('cmdline') or [])[:500],
                    io_read_bytes=io.read_bytes if io else 0,
                    io_write_bytes=io.write_bytes if io else 0,
                ))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
    except Exception:
        pass

    procs.sort(key=lambda x: x.cpu_percent, reverse=True)
    return procs[:top_n]


def get_total_processes() -> tuple:
    try:
        running = sum(1 for p in psutil.process_iter() if p.is_running())
        threads = sum(p.num_threads() for p in psutil.process_iter() if p.is_running())
        return running, threads
    except Exception:
        return 0, 0
