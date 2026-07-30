"""Linux-specific system data collectors."""

import os
import re
import glob
import subprocess
import psutil
from typing import List, Dict, Any, Optional

from .shared import run_cmd, run_cmd_combined, parse_bytes, get_platform
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

    # DMI/SMBIOS info
    def read_dmi(name: str) -> str:
        path = f"/sys/class/dmi/id/{name}"
        try:
            with open(path, 'r') as f:
                return f.read().strip()
        except (FileNotFoundError, PermissionError):
            return ""

    info.manufacturer = read_dmi('sys_vendor')
    info.model = read_dmi('product_name')
    info.serial = read_dmi('product_serial')
    info.sku = read_dmi('product_sku')
    info.uuid = read_dmi('board_serial')
    info.family = read_dmi('product_family')
    info.motherboard_manufacturer = read_dmi('board_vendor')
    info.motherboard_model = read_dmi('board_name')
    info.motherboard_version = read_dmi('board_version')
    info.motherboard_serial = read_dmi('board_serial')
    info.chassis_manufacturer = read_dmi('chassis_vendor')
    info.chassis_type = read_dmi('chassis_type')
    info.chassis_serial = read_dmi('chassis_serial')
    info.bios_vendor = read_dmi('bios_vendor')
    info.bios_version = read_dmi('bios_version')
    info.bios_date = read_dmi('bios_date')

    try:
        with open('/sys/class/dmi/id/bios_rom_size', 'r') as f:
            info.bios_rom_size_bytes = int(f.read().strip()[:-1]) * 1024 if f.read().strip().endswith('KB') else 0
    except Exception:
        pass

    info.uefi_mode = os.path.exists('/sys/firmware/efi')
    info.wake_on_lan = False

    # SMBIOS version
    smbios = run_cmd(['sudo', 'dmidecode', '-s', 'smbios-version'])
    if smbios:
        info.smbios_version = smbios

    return info


def get_gpus() -> List[GpuInfo]:
    gpus = []

    # Try NVIDIA via NVML
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        for i in range(device_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            gpu = GpuInfo()
            gpu.name = pynvml.nvmlDeviceGetName(handle)
            gpu.architecture = "NVIDIA"
            gpu.driver_version = pynvml.nvmlSystemGetDriverVersion()
            gpu.vram_bytes = pynvml.nvmlDeviceGetMemoryInfo(handle).total
            gpu.vram_type = "GDDR"  # Simplified
            gpu.temperature_c = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            gpu.power_draw_w = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0
            gpu.power_limit_w = pynvml.nvmlDeviceGetEnforcedPowerLimit(handle) / 1000.0
            gpu.fan_speed_pct = pynvml.nvmlDeviceGetFanSpeed(handle)
            gpu.cuda_cores = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[0] if pynvml.nvmlDeviceGetCudaComputeCapability(handle) else 0
            gpu.pci_vendor_id = hex(pynvml.nvmlDeviceGetDeviceId(handle))
            gpu.opencl_version = "OpenCL 3.0"
            gpu.hardware_acceleration = True
            gpus.append(gpu)
        pynvml.nvmlShutdown()
    except ImportError:
        pass
    except Exception:
        pass

    # Fallback: parse lspci for all GPUs
    lspci_output = run_cmd(['lspci'])
    if lspci_output:
        for line in lspci_output.split('\n'):
            if 'VGA' in line or '3D' in line or 'Display' in line or 'GPU' in line:
                gpu = GpuInfo()
                gpu.name = line.split(':')[-1].strip() if ':' in line else "Unknown GPU"
                gpu.pci_interface = "PCIe"
                gpu.hardware_acceleration = True
                # Check if already added via NVML
                if not any(g.name == gpu.name for g in gpus):
                    gpus.append(gpu)

    # Try to get AMD GPU info
    amd_output = run_cmd(['amdgpu', '--querygpu', 'name,driver,memory_total,vram_used,temp,clock_now'] if run_cmd(['which', 'amdgpu']) else ['rocm-smi', '--showallinfo'])
    if amd_output:
        for line in amd_output.split('\n'):
            if 'gpu' in line.lower() and 'name' in line.lower():
                gpu = GpuInfo()
                gpu.name = line.split(':')[-1].strip() if ':' in line else "AMD GPU"
                gpu.architecture = "AMD"
                gpu.hardware_acceleration = True
                if not any(g.name == gpu.name for g in gpus):
                    gpus.append(gpu)

    return gpus


def get_monitors() -> List[MonitorInfo]:
    monitors = []

    # Try xrandr
    xrandr = run_cmd(['xrandr'])
    if xrandr:
        current_output = None
        for line in xrandr.split('\n'):
            if ' connected' in line:
                parts = line.split(' connected')
                name = parts[0].strip()
                monitor = MonitorInfo()
                monitor.name = name

                # Parse resolution
                res_match = re.search(r'\((\d+x\d+)', line)
                if res_match:
                    res = res_match.group(1)
                    monitor.resolution_width = int(res.split('x')[0])
                    monitor.resolution_height = int(res.split('x')[1])
                    monitor.current_refresh_hz = 60  # Default
                    current_output = name

                # Parse refresh rate
                refresh_match = re.search(r'\d+x\d+\s+(\d+\.?\d*)', line)
                if refresh_match:
                    monitor.current_refresh_hz = int(float(refresh_match.group(1)))

                if 'primary' in line:
                    monitor.is_primary = True

                monitors.append(monitor)

            # Try to get EDID info
            if 'connected' in line and not monitors:
                pass

    # Fallback: use screeninfo
    if not monitors:
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

    # Get disk names from lsblk
    lsblk = run_cmd(['lsblk', '-d', '-b', '-o', 'NAME,SIZE,MODEL,SERIAL,FIRMWARE,TRAN,ROTA,TYPE', '-J'])
    if lsblk:
        try:
            data = __import__('json').loads(lsblk)
            for disk in data.get('blockdevices', []):
                if disk.get('type') == 'disk':
                    disk_info = DiskInfo()
                    disk_info.name = f"/dev/{disk['name']}"
                    disk_info.model = disk.get('model', '').strip()
                    disk_info.manufacturer = ""
                    disk_info.serial = disk.get('serial', '').strip()
                    disk_info.firmware = disk.get('firmware', '').strip()
                    disk_info.interface = disk.get('tran', '').upper() or "SATA"
                    disk_info.capacity_bytes = disk.get('size', 0) or 0
                    disk_info.form_factor = "2.5\"" if '2.5' in disk.get('model', '').lower() else "3.5\"" if '3.5' in disk.get('model', '').lower() else "M.2" if 'NVMe' in disk.get('model', '') else "Unknown"
                    disk_info.rpm = 0 if disk.get('rota', True) else 0  # SSD
                    disk_info.rpm = 5400 if disk.get('rota', True) else 0  # HDD default
                    disks.append(disk_info)
        except (json.JSONDecodeError, KeyError):
            pass

    # Get SMART data for each disk
    for disk in disks:
        smart_output = run_cmd(['sudo', 'smartctl', '-i', disk.name])
        if smart_output:
            for line in smart_output.split('\n'):
                if 'Inquiry:' in line:
                    parts = line.split(':')
                    if len(parts) > 1:
                        disk.manufacturer = parts[1].strip().split()[0] if parts[1].strip() else disk.manufacturer
                if 'Temperature_Celsius' in line or 'Temperature' in line:
                    temp_match = re.search(r'(\d+)', line)
                    if temp_match:
                        disk.temperature_c = float(temp_match.group(1))
                if 'Power_On_Hours' in line:
                    hours_match = re.search(r'(\d+)', line)
                    if hours_match:
                        disk.power_on_hours = int(hours_match.group(1))

        # Get SMART health
        health = run_cmd(['sudo', 'smartctl', '-H', disk.name])
        if health and 'PASSED' in health:
            disk.health_status = "PASSED"
        elif health:
            disk.health_status = "UNKNOWN"

        # Get NVMe specific attributes
        if 'NVMe' in disk.name or 'nvme' in disk.name:
            nvme_output = run_cmd(['sudo', 'nvme', 'smart-log', disk.name.replace('/dev/', '')])
            if nvme_output:
                for line in nvme_output.split('\n'):
                    if 'temperature' in line.lower():
                        temp_match = re.search(r'(\d+)', line)
                        if temp_match:
                            disk.temperature_c = float(temp_match.group(1)) - 273.15  # Kelvin to Celsius
                    if 'data_units' in line.lower():
                        units_match = re.search(r'(\d+)', line)
                        if units_match:
                            disk.power_on_hours = int(units_match.group(1)) * 30 // 3600  # Rough estimate

    return disks


def get_partitions() -> List[PartitionInfo]:
    partitions = []

    try:
        for mount in psutil.disk_partitions(all=False):
            try:
                usage = psutil.disk_usage(mount.mountpoint)
                partition = PartitionInfo(
                    name=mount.device,
                    type="",
                    filesystem=mount.fstype,
                    size_bytes=usage.total,
                    used_bytes=usage.used,
                    free_bytes=usage.free,
                    mount_point=mount.mountpoint,
                    label="",
                    block_size=4096,
                    read_only=mount.opts and 'ro' in mount.opts,
                    usage_percent=usage.percent,
                )
                partitions.append(partition)
            except (PermissionError, FileNotFoundError):
                continue
    except Exception:
        pass

    # Try lsblk for more detail
    lsblk = run_cmd(['lsblk', '-b', '-o', 'NAME,SIZE,FSTYPE,MOUNTPOINT,LABEL,UUID,TYPE,RO,FSUSE%', '-J'])
    if lsblk:
        try:
            data = __import__('json').loads(lsblk)
            for part in data.get('blockdevices', []):
                if part.get('type') == 'part':
                    partition = PartitionInfo()
                    partition.name = f"/dev/{part['name']}"
                    partition.size_bytes = part.get('size', 0) or 0
                    partition.filesystem = part.get('fstype', '') or ''
                    partition.mount_point = part.get('mountpoint', '') or ''
                    partition.label = part.get('label', '') or ''
                    partition.uuid = part.get('uuid', '') or ''
                    partition.usage_percent = float(part.get('fsuse%', '0') or '0')
                    if partition not in partitions:
                        partitions.append(partition)
        except (json.JSONDecodeError, KeyError):
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
            'rx_bytes': io.bytes_recv,
            'tx_bytes': io.bytes_sent,
            'rx_packets': io.packets_recv,
            'tx_packets': io.packets_sent,
            'rx_errors': io.errin,
            'tx_errors': io.errout,
            'rx_dropped': io.dropin,
            'tx_dropped': io.dropout,
        }

        # Get addresses
        addrs = net_addr.get(name, [])
        for addr in addrs:
            if addr.family == psutil.AF_LINK:
                adapter.mac_address = addr.address
            elif addr.family == 2:  # AF_INET
                adapter.ipv4_address = addr.address
            elif addr.family == 10:  # AF_INET6
                adapter.ipv6_address = addr.address

        # Get stats
        stats = net_stats.get(name)
        if stats:
            adapter.adapter_type = "Ethernet" if not stats.isup or 'eth' in name else "WiFi"
            adapter.speed_mbps = int(stats.speed * 1000000) if stats.speed else 0
            adapter.duplex = "FULL" if stats.duplex else "UNKNOWN"
            adapter.mtu = stats.mtu or 1500
            adapter.connection_state = "UP" if stats.isup else "DOWN"

        adapters.append(adapter)

    return adapters


def get_usb_devices() -> List[UsbDeviceInfo]:
    devices = []

    lsusb = run_cmd(['lsusb'])
    if lsusb:
        for line in lsusb.split('\n'):
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                device = UsbDeviceInfo()
                device.vendor_id = parts[1] if len(parts) > 1 else ""
                device.product_id = parts[2] if len(parts) > 2 else ""
                device.name = ' '.join(parts[3:]) if len(parts) > 3 else ""
                device.speed = "USB 2.0" if '2.0' in line else "USB 3.0" if '3.0' in line or '3.1' in line else "Unknown"
                try:
                    bus_str = parts[0].replace('Bus', '')
                    device.bus_number = int(bus_str) if bus_str else 0
                except (ValueError, IndexError):
                    device.bus_number = 0
                try:
                    dev_str = parts[2].replace('Device', '')
                    device.device_address = int(dev_str) if dev_str else 0
                except (ValueError, IndexError):
                    device.device_address = 0
                devices.append(device)

    return devices


def get_usb_controllers() -> List[UsbControllerInfo]:
    controllers = []

    lspci = run_cmd(['lspci'])
    if lspci:
        for line in lspci.split('\n'):
            if 'USB' in line or 'XHCI' in line or 'EHCI' in line or 'OHCI' in line:
                controller = UsbControllerInfo()
                controller.name = line.split(':')[-1].strip() if ':' in line else "USB Controller"
                controller.speed = "USB 3.0" if 'XHCI' in line or '3.0' in line or '3.1' in line else "USB 2.0"
                controller.controller_type = "XHCI" if 'XHCI' in line else "EHCI" if 'EHCI' in line else "OHCI"
                controllers.append(controller)

    return controllers


def get_audio_devices() -> List[AudioDeviceInfo]:
    devices = []

    # Try arecord -l
    arecord = run_cmd(['arecord', '-l'])
    if arecord:
        for line in arecord.split('\n'):
            if 'card' in line.lower():
                device = AudioDeviceInfo()
                device.name = line.strip()
                device.manufacturer = "ALSA"
                devices.append(device)

    # Try lspci for audio
    lspci = run_cmd(['lspci'])
    if lspci:
        for line in lspci.split('\n'):
            if 'Audio' in line or 'Sound' in line or 'HDMI' in line:
                device = AudioDeviceInfo()
                device.name = line.split(':')[-1].strip() if ':' in line else "Audio Device"
                device.manufacturer = "PCI"
                devices.append(device)

    return devices


def get_pci_devices() -> List[PciDeviceInfo]:
    devices = []

    lspci_output = run_cmd(['lspci', '-nnk'])
    if lspci_output:
        current_device = None
        for line in lspci_output.split('\n'):
            if re.match(r'^\d{2}:\d{2}\.', line):
                if current_device:
                    devices.append(current_device)
                current_device = PciDeviceInfo()
                parts = line.split()
                if len(parts) >= 2:
                    current_device.vendor_id = parts[0].split(':')[0] if ':' in parts[0] else ""
                    current_device.device_id = parts[0].split(':')[1] if ':' in parts[0] else ""
                if len(parts) >= 4 and ':' in parts[-2]:
                    current_device.subsystem_vendor_id = parts[-2]
                    current_device.subsystem_id = parts[-1]
                current_device.name = line.split(':')[-1].strip() if ':' in line else ""

                # Check for driver
                for next_line in lspci_output.split('\n')[lspci_output.split('\n').index(line)+1:lspci_output.split('\n').index(line)+3]:
                    if 'Kernel driver' in next_line:
                        current_device.driver = next_line.split(': ')[-1].strip() if ': ' in next_line else ""
                    if 'Kernel modules' in next_line:
                        current_device.driver_version = next_line.split(': ')[-1].strip() if ': ' in next_line else ""
                        break

            elif current_device and line.strip():
                # Parse subsystem info
                if re.match(r'^\s+Subsystem:', line):
                    parts = line.split()
                    if len(parts) >= 4:
                        current_device.subsystem_vendor_id = parts[2]
                        current_device.subsystem_id = parts[3]

        if current_device:
            devices.append(current_device)

    return devices


def get_bluetooth() -> Optional[BluetoothDeviceInfo]:
    info = BluetoothDeviceInfo()

    bluetoothctl = run_cmd(['bluetoothctl', 'list'])
    if bluetoothctl:
        info.adapter_name = bluetoothctl.split(':')[0].strip() if ':' in bluetoothctl else "Bluetooth Adapter"
        info.adapter_manufacturer = "Linux Bluetooth"

    paired = run_cmd(['bluetoothctl', 'paired-devices'])
    if paired:
        for line in paired.split('\n'):
            if 'Device' in line:
                device_info = {}
                device_info['address'] = line.split('Device ')[-1].strip() if 'Device ' in line else ""
                paired.append(device_info)

    return info if info.adapter_name else None


def get_battery() -> Optional[BatteryInfo]:
    info = BatteryInfo()

    # Check for battery
    batteries = list(glob.glob('/sys/class/power_supply/*/'))
    if not batteries:
        return None

    for batt_path in batteries:
        try:
            info.name = open(os.path.join(batt_path, 'type')).read().strip()
            info.manufacturer_name = open(os.path.join(batt_path, 'manufacturer')).read().strip() if os.path.exists(os.path.join(batt_path, 'manufacturer')) else ""
            info.model_name = open(os.path.join(batt_path, 'model_name')).read().strip() if os.path.exists(os.path.join(batt_path, 'model_name')) else ""
            info.serial = open(os.path.join(batt_path, 'serial_number')).read().strip() if os.path.exists(os.path.join(batt_path, 'serial_number')) else ""

            # Capacity
            energy_full = 0.0
            energy_design = 0.0
            if os.path.exists(os.path.join(batt_path, 'energy_full')):
                energy_full = float(open(os.path.join(batt_path, 'energy_full')).read().strip()) / 1000000  # Wh
            if os.path.exists(os.path.join(batt_path, 'energy_full_design')):
                energy_design = float(open(os.path.join(batt_path, 'energy_full_design')).read().strip()) / 1000000  # Wh

            info.design_capacity_wh = energy_design
            info.full_capacity_wh = energy_full
            info.health_percent = (energy_full / energy_design * 100) if energy_design > 0 else 0.0

            # Status
            status = open(os.path.join(batt_path, 'status')).read().strip() if os.path.exists(os.path.join(batt_path, 'status')) else "Unknown"
            info.state = status

            # Charge
            if energy_design > 0:
                info.charge_percent = (energy_full / energy_design) * 100

            # Voltage
            if os.path.exists(os.path.join(batt_path, 'voltage_now')):
                info.voltage = float(open(os.path.join(batt_path, 'voltage_now')).read().strip()) / 1000000  # V

            info.temperature_c = float(open(os.path.join(batt_path, 'temp')).read().strip()) / 10 if os.path.exists(os.path.join(batt_path, 'temp')) else 0.0

        except (ValueError, FileNotFoundError, PermissionError):
            continue

    return info if info.name else None


def get_security() -> SecurityInfo:
    info = SecurityInfo()

    # TPM
    tpm_status = run_cmd(['sudo', 'tpm_version'] if run_cmd(['which', 'tpm_version']) else ['cat', '/sys/class/tpm/tpm0/tpm_version'])
    if tpm_status:
        info.tpm_present = True
        info.tpm_enabled = True
        info.tpm_activated = True
        info.tpm_version = "2.0" if "2.0" in tpm_status else "1.2"

    # Secure Boot
    sb_status = run_cmd(['mokutil', '--sb-state'])
    if sb_status:
        info.secure_boot = "Enabled" if "enabled" in sb_status.lower() else "Disabled"
        info.secure_boot_mode = "Standard" if "standard" in sb_status.lower() else "Custom"

    # Firewall
    ufw_status = run_cmd(['sudo', 'ufw', 'status'])
    if ufw_status:
        info.firewall_enabled = "active" in ufw_status.lower()
        info.firewall_profiles = ["UFW"] if info.firewall_enabled else []

    firewalld = run_cmd(['sudo', 'firewall-cmd', '--state'])
    if firewalld:
        info.firewall_enabled = firewalld.strip() == "running"
        info.firewall_profiles.append("firewalld")

    # Antivirus
    clamav = run_cmd(['sudo', 'clamd', '--version'])
    if clamav:
        info.antivirus_name = "ClamAV"
        info.antivirus_status = "Running"

    return info


def get_installed_software() -> List[InstalledSoftware]:
    software = []

    # Try apt list
    apt_list = run_cmd(['apt', 'list', '--installed'])
    if apt_list:
        for line in apt_list.split('\n'):
            if '/ ' in line and 'now' in line:
                pkg = line.split('/')[0].split(':')[-1] if '/' in line else ""
                version = line.split(' ')[-2] if ' ' in line else ""
                if pkg and version:
                    software.append(InstalledSoftware(
                        name=pkg,
                        version=version,
                        publisher="Debian/Ubuntu",
                        architecture="amd64"
                    ))

    # Try pacman
    pacman_list = run_cmd(['pacman', '-Qe'])
    if pacman_list:
        for line in pacman_list.split('\n'):
            parts = line.split()
            if len(parts) >= 2:
                software.append(InstalledSoftware(
                    name=parts[0],
                    version=parts[1],
                    publisher="Arch Linux",
                    architecture="x86_64"
                ))

    return software[:100]  # Limit to 100


def get_services() -> List[ServiceInfo]:
    services = []

    # Try systemctl
    systemctl = run_cmd(['systemctl', 'list-units', '--type=service', '--all', '--no-pager', '--no-legend'])
    if systemctl:
        for line in systemctl.split('\n'):
            parts = line.split()
            if len(parts) >= 3:
                service = ServiceInfo()
                service.name = parts[0].replace('.service', '')
                service.status = parts[-1] if parts[-1] in ['running', 'exited', 'failed'] else "unknown"
                service.start_type = "auto" if service.status == "running" else "manual"
                services.append(service)

    return services[:50]  # Limit


def get_virtualization() -> VirtualizationInfo:
    info = VirtualizationInfo()

    # Check for Docker
    docker_version = run_cmd(['docker', '--version'])
    if docker_version:
        info.docker_installed = True
        info.docker_version = docker_version.split()[-1] if docker_version else ""

    # Check for Kubernetes
    kubectl_version = run_cmd(['kubectl', 'version', '--short'])
    if kubectl_version:
        info.kubernetes_installed = True
        info.kubernetes_version = kubectl_version.split()[-1] if kubectl_version else ""

    # Check for WSL
    if os.path.exists('/run/wsl'):
        info.wsl_installed = True
        info.wsl_distributions = ["WSL2"]

    # Check for nested virtualization
    kvm_loaded = os.path.exists('/dev/kvm')
    info.nested_virtualization = kvm_loaded
    info.vt_x_amd_v_enabled = kvm_loaded

    # Check for VM
    dmidecode = run_cmd(['sudo', 'dmidecode', '-s', 'system-product-name'])
    if dmidecode:
        vm_hyps = ['vmware', 'virtualbox', 'hyper-v', 'kvm', 'qemu']
        for hyp in vm_hyps:
            if hyp in dmidecode.lower():
                info.vm_detected = True
                info.vm_host = hyp.capitalize()
                break

    return info


def get_wireless() -> List[WirelessInfo]:
    wireless = []

    iw = run_cmd(['iw', 'dev'])
    if iw:
        for line in iw.split('\n'):
            if 'SSID' in line:
                info = WirelessInfo()
                info.adapter_name = line.split()[1] if len(line.split()) > 1 else ""
                info.current_ssid = line.split('SSID')[1].strip() if 'SSID' in line else ""
                wireless.append(info)

    # Get more wireless details
    iwconfig = run_cmd(['iwconfig'])
    if iwconfig:
        for line in iwconfig.split('\n'):
            if 'ESSID' in line:
                info = WirelessInfo()
                info.current_ssid = line.split('ESSID:')[1].strip('"') if 'ESSID:' in line else ""
                info.adapter_name = line.split()[0] if line.split() else ""
                if info not in wireless:
                    wireless.append(info)

    return wireless


def get_cooling() -> List[CoolingInfo]:
    cooling = []

    # Read from sysfs
    for fan_path in glob.glob('/sys/class/hwmon/hwmon*/fan*_input'):
        try:
            fan_name = ""
            try:
                fan_name = open(fan_path.replace('_input', '_name')).read().strip()
            except (FileNotFoundError, PermissionError):
                fan_name = os.path.basename(fan_path).replace('_input', '')

            rpm = int(open(fan_path).read().strip())

            info = CoolingInfo()
            info.fan_name = fan_name
            info.current_rpm = rpm
            info.fan_type = "Case" if 'case' in fan_path.lower() or 'chassis' in fan_path.lower() else "CPU" if 'cpu' in fan_path.lower() else "Unknown"
            cooling.append(info)
        except (ValueError, FileNotFoundError, PermissionError):
            continue

    return cooling
