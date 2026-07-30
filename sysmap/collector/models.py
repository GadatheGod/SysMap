"""Pydantic models for system data."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class CpuInfo(BaseModel):
    name: str = ""
    brand: str = ""
    manufacturer: str = ""
    codename: str = ""
    socket: str = ""
    physical_cores: int = 0
    logical_cores: int = 0
    threads: int = 0
    base_clock_mhz: float = 0.0
    boost_clock_mhz: float = 0.0
    l1_cache_kb: int = 0
    l2_cache_kb: int = 0
    l3_cache_kb: int = 0
    extensions: List[str] = Field(default_factory=list)
    virtualization: bool = False
    tdp_watts: float = 0.0
    hyperthreading: bool = False
    per_core_base_freq: List[float] = Field(default_factory=list)
    per_core_boost_freq: List[float] = Field(default_factory=list)
    per_core_current_freq: List[float] = Field(default_factory=list)
    per_core_utilization: List[float] = Field(default_factory=list)
    per_core_temperature: List[float] = Field(default_factory=list)
    cpu_id: Dict[str, str] = Field(default_factory=dict)
    microcode_version: str = ""
    hybrid_arch: bool = False
    p_core_count: int = 0
    e_core_count: int = 0
    power_limits: Dict[str, float] = Field(default_factory=dict)


class MemoryInfo(BaseModel):
    total_physical_bytes: int = 0
    available_physical_bytes: int = 0
    total_virtual_bytes: int = 0
    available_virtual_bytes: int = 0
    total_swap_bytes: int = 0
    available_swap_bytes: int = 0
    memory_type: str = ""
    memory_speed_mts: int = 0
    memory_voltage: float = 0.0
    form_factor: str = ""
    channel_count: int = 0
    ecc_supported: bool = False
    ecc_active: bool = False
    timings: Dict[str, int] = Field(default_factory=dict)
    slots_total: int = 0
    slots_used: int = 0
    slots: List[Dict[str, Any]] = Field(default_factory=list)
    bandwidth_utilization: Dict[str, float] = Field(default_factory=dict)


class GpuInfo(BaseModel):
    name: str = ""
    codename: str = ""
    architecture: str = ""
    revision: str = ""
    die_size_mm2: float = 0.0
    transistor_count: str = ""
    process_node_nm: int = 0
    vram_bytes: int = 0
    vram_type: str = ""
    vram_speed_mts: int = 0
    vram_bus_width: int = 0
    vram_manufacturer: str = ""
    vram_part_number: str = ""
    pci_interface: str = ""
    pci_generation: str = ""
    pci_link_speed: str = ""
    driver_version: str = ""
    driver_date: str = ""
    uefi_version: str = ""
    uefi_supported: bool = False
    directx_version: str = ""
    opengl_version: str = ""
    vulkan_version: str = ""
    cuda_cores: int = 0
    stream_processors: int = 0
    compute_units: int = 0
    shader_model: str = ""
    temperature_c: float = 0.0
    power_draw_w: float = 0.0
    power_limit_w: float = 0.0
    fan_speed_pct: float = 0.0
    core_clock_mhz: float = 0.0
    boost_clock_mhz: float = 0.0
    memory_clock_mhz: float = 0.0
    vram_used_bytes: int = 0
    vram_available_bytes: int = 0
    pci_vendor_id: str = ""
    pci_device_id: str = ""
    pci_subsystem_id: str = ""
    opencl_version: str = ""
    hardware_acceleration: bool = False


class MonitorInfo(BaseModel):
    name: str = ""
    manufacturer: str = ""
    model: str = ""
    serial: str = ""
    edid_version: str = ""
    physical_width_mm: int = 0
    physical_height_mm: int = 0
    resolution_width: int = 0
    resolution_height: int = 0
    refresh_rate_hz: int = 0
    color_depth: int = 0
    color_space: str = ""
    panel_type: str = ""
    aspect_ratio: str = ""
    ppi: float = 0.0
    hdr_support: bool = False
    hdr_standard: str = ""
    brightness_nits: int = 0
    contrast_ratio: str = ""
    native_refresh_hz: int = 0
    current_refresh_hz: int = 0
    scaling_factor: float = 0.0
    position_x: int = 0
    position_y: int = 0
    is_primary: bool = False
    rotation: str = ""
    edid_vendor: str = ""
    edid_product: str = ""
    backlight_hours: int = 0
    supported_resolutions: List[Dict[str, int]] = Field(default_factory=list)


class DiskInfo(BaseModel):
    name: str = ""
    model: str = ""
    manufacturer: str = ""
    serial: str = ""
    firmware: str = ""
    interface: str = ""
    protocol: str = ""
    capacity_bytes: int = 0
    capacity_formatted_bytes: int = 0
    form_factor: str = ""
    rpm: int = 0
    cache_size_mb: int = 0
    temperature_c: float = 0.0
    power_on_hours: int = 0
    power_count: int = 0
    wear_level_pct: float = 0.0
    health_status: str = ""
    smart_attributes: Dict[str, Any] = Field(default_factory=dict)
    nvme_attributes: Dict[str, Any] = Field(default_factory=dict)


class PartitionInfo(BaseModel):
    name: str = ""
    type: str = ""
    filesystem: str = ""
    size_bytes: int = 0
    used_bytes: int = 0
    free_bytes: int = 0
    mount_point: str = ""
    uuid: str = ""
    boot_flag: bool = False
    label: str = ""
    block_size: int = 0
    read_only: bool = False
    usage_percent: float = 0.0
    mount_options: List[str] = Field(default_factory=list)


class NetworkAdapterInfo(BaseModel):
    name: str = ""
    adapter_type: str = ""
    mac_address: str = ""
    manufacturer: str = ""
    model: str = ""
    driver_version: str = ""
    driver_date: str = ""
    firmware_version: str = ""
    speed_mbps: int = 0
    duplex: str = ""
    mtu: int = 0
    ipv4_address: str = ""
    ipv4_subnet: str = ""
    ipv4_gateway: str = ""
    ipv4_dns: List[str] = Field(default_factory=list)
    ipv6_address: str = ""
    ipv6_prefix: str = ""
    ipv6_gateway: str = ""
    dhcp_enabled: bool = False
    wifi_ssid: str = ""
    wifi_bssid: str = ""
    wifi_signal_dbm: int = 0
    wifi_security: str = ""
    wifi_channel: int = 0
    wifi_frequency_mhz: int = 0
    wifi_standard: str = ""
    connection_state: str = ""
    ipv6_dhcp: bool = False
    dns_suffix: str = ""
    power_management: bool = False
    wake_on_lan: bool = False
    io_stats: Dict[str, int] = Field(default_factory=dict)


class UsbDeviceInfo(BaseModel):
    name: str = ""
    vendor_id: str = ""
    product_id: str = ""
    serial: str = ""
    manufacturer: str = ""
    product_name: str = ""
    speed: str = ""
    class_name: str = ""
    subclass: str = ""
    protocol: str = ""
    max_power_ma: int = 0
    bus_number: int = 0
    device_address: int = 0
    driver: str = ""
    driver_version: str = ""
    hub_port: int = 0
    hub_depth: int = 0


class UsbControllerInfo(BaseModel):
    name: str = ""
    vendor_id: str = ""
    product_id: str = ""
    driver: str = ""
    revision: str = ""
    pci_slot: str = ""
    speed: str = ""
    controller_type: str = ""


class AudioDeviceInfo(BaseModel):
    name: str = ""
    manufacturer: str = ""
    model: str = ""
    driver_version: str = ""
    codec: str = ""
    sample_rates: List[int] = Field(default_factory=list)
    bit_depths: List[int] = Field(default_factory=list)
    channels: int = 0
    default_playback: bool = False
    default_capture: bool = False


class PciDeviceInfo(BaseModel):
    name: str = ""
    vendor_id: str = ""
    device_id: str = ""
    subsystem_vendor_id: str = ""
    subsystem_id: str = ""
    class_name: str = ""
    subclass: str = ""
    programming_interface: str = ""
    revision: str = ""
    pci_generation: str = ""
    link_width: str = ""
    link_speed: str = ""
    driver: str = ""
    driver_version: str = ""
    irq: int = 0
    memory_regions: List[Dict[str, Any]] = Field(default_factory=list)
    vendor_name: str = ""
    device_name: str = ""


class BluetoothDeviceInfo(BaseModel):
    adapter_name: str = ""
    adapter_manufacturer: str = ""
    adapter_version: str = ""
    local_address: str = ""
    paired_devices: List[Dict[str, Any]] = Field(default_factory=list)


class BatteryInfo(BaseModel):
    name: str = ""
    chemistry: str = ""
    design_capacity_wh: float = 0.0
    full_capacity_wh: float = 0.0
    current_capacity_wh: float = 0.0
    state: str = ""
    charge_percent: float = 0.0
    voltage: float = 0.0
    rate_w: float = 0.0
    time_remaining_minutes: int = 0
    cycle_count: int = 0
    temperature_c: float = 0.0
    manufacture_date: str = ""
    serial: str = ""
    manufacturer_name: str = ""
    model_name: str = ""
    design_voltage: float = 0.0
    health_percent: float = 0.0


class SensorReading(BaseModel):
    name: str = ""
    category: str = ""
    value: float = 0.0
    unit: str = ""
    critical: float = 0.0


class OsInfo(BaseModel):
    name: str = ""
    version: str = ""
    build: str = ""
    edition: str = ""
    architecture: str = ""
    kernel_version: str = ""
    kernel_name: str = ""
    hostname: str = ""
    username: str = ""
    language: str = ""
    locale: str = ""
    timezone: str = ""
    uptime_seconds: int = 0
    boot_time: str = ""
    installation_date: str = ""
    activation_status: str = ""
    product_id: str = ""
    system_root: str = ""
    platform: str = ""
    platform_version: str = ""
    node: str = ""
    processor: str = ""
    machine: str = ""
    os_type: str = ""


class SecurityInfo(BaseModel):
    tpm_manufacturer: str = ""
    tpm_version: str = ""
    tpm_spec_version: str = ""
    tpm_firmware_version: str = ""
    tpm_present: bool = False
    tpm_enabled: bool = False
    tpm_activated: bool = False
    tpm_owned: bool = False
    secure_boot: str = ""
    secure_boot_mode: str = ""
    bitlocker_status: str = ""
    bitlocker_drives: List[Dict[str, str]] = Field(default_factory=list)
    firewall_enabled: bool = False
    firewall_profiles: List[str] = Field(default_factory=list)
    antivirus_name: str = ""
    antivirus_status: str = ""
    antivirus_engine_version: str = ""
    antivirus_signature_version: str = ""
    virtualization_based_security: bool = False
    vbs_running: bool = False


class InstalledSoftware(BaseModel):
    name: str = ""
    version: str = ""
    publisher: str = ""
    install_date: str = ""
    install_location: str = ""
    architecture: str = ""
    estimated_size_bytes: int = 0


class InstalledDriver(BaseModel):
    name: str = ""
    version: str = ""
    date: str = ""
    provider: str = ""
    signer: str = ""
    inf_file: str = ""
    device_class: str = ""


class ProcessInfo(BaseModel):
    pid: int = 0
    name: str = ""
    path: str = ""
    user: str = ""
    cpu_percent: float = 0.0
    memory_bytes: int = 0
    threads: int = 0
    status: str = ""
    create_time: str = ""
    command_line: str = ""
    io_read_bytes: int = 0
    io_write_bytes: int = 0


class ServiceInfo(BaseModel):
    name: str = ""
    display_name: str = ""
    status: str = ""
    start_type: str = ""
    description: str = ""
    binary_path: str = ""
    account: str = ""


class PowerPlanInfo(BaseModel):
    name: str = ""
    guid: str = ""
    type: str = ""
    sleep_display_minutes: int = 0
    sleep_system_minutes: int = 0
    hibernate_enabled: bool = False
    fast_startup: bool = False
    disk_spin_down_minutes: int = 0
    usb_selective_suspend: bool = False
    min_processor_state_pct: int = 0
    max_processor_state_pct: int = 0


class VirtualizationInfo(BaseModel):
    hyper_v_enabled: bool = False
    vm_detected: bool = False
    vm_host: str = ""
    vm_guest_os: str = ""
    vm_cpu_cores: int = 0
    vm_ram_bytes: int = 0
    docker_installed: bool = False
    docker_version: str = ""
    kubernetes_installed: bool = False
    kubernetes_version: str = ""
    wsl_installed: bool = False
    wsl_distributions: List[str] = Field(default_factory=list)
    nested_virtualization: bool = False
    vt_x_amd_v_enabled: bool = False


class InputDeviceInfo(BaseModel):
    name: str = ""
    manufacturer: str = ""
    product_id: str = ""
    vendor_id: str = ""
    device_type: str = ""
    dpi: int = 0
    buttons: int = 0
    polling_rate: int = 0
    resolution: str = ""
    frame_rate: int = 0
    field_of_view: float = 0.0


class WirelessInfo(BaseModel):
    adapter_name: str = ""
    mac_address: str = ""
    driver_version: str = ""
    firmware_version: str = ""
    standards: List[str] = Field(default_factory=list)
    bands: List[str] = Field(default_factory=list)
    channel_width: List[str] = Field(default_factory=list)
    current_ssid: str = ""
    current_bssid: str = ""
    rssi_dbm: int = 0
    signal_strength_pct: int = 0
    security_type: str = ""
    encryption_type: str = ""
    channel: int = 0
    frequency_mhz: int = 0
    mimo_config: str = ""
    tx_rate_mbps: float = 0.0
    rx_rate_mbps: float = 0.0
    noise_dbm: int = 0
    snr_db: int = 0


class CoolingInfo(BaseModel):
    fan_name: str = ""
    fan_type: str = ""
    model: str = ""
    manufacturer: str = ""
    rated_rpm: int = 0
    current_rpm: int = 0
    pwm_duty: float = 0.0
    voltage: float = 0.0


class SystemInfo(BaseModel):
    manufacturer: str = ""
    model: str = ""
    serial: str = ""
    sku: str = ""
    uuid: str = ""
    family: str = ""
    motherboard_manufacturer: str = ""
    motherboard_model: str = ""
    motherboard_version: str = ""
    motherboard_serial: str = ""
    chassis_manufacturer: str = ""
    chassis_type: str = ""
    chassis_serial: str = ""
    bios_vendor: str = ""
    bios_version: str = ""
    bios_date: str = ""
    bios_rom_size_bytes: int = 0
    uefi_mode: bool = False
    smbios_version: str = ""
    wake_on_lan: bool = False


class SystemSnapshot(BaseModel):
    timestamp: str = ""
    platform: str = ""
    system: SystemInfo
    cpu: CpuInfo
    memory: MemoryInfo
    gpus: List[GpuInfo] = Field(default_factory=list)
    monitors: List[MonitorInfo] = Field(default_factory=list)
    disks: List[DiskInfo] = Field(default_factory=list)
    partitions: List[PartitionInfo] = Field(default_factory=list)
    network_adapters: List[NetworkAdapterInfo] = Field(default_factory=list)
    usb_devices: List[UsbDeviceInfo] = Field(default_factory=list)
    usb_controllers: List[UsbControllerInfo] = Field(default_factory=list)
    audio_devices: List[AudioDeviceInfo] = Field(default_factory=list)
    pci_devices: List[PciDeviceInfo] = Field(default_factory=list)
    bluetooth: Optional[BluetoothDeviceInfo] = None
    battery: Optional[BatteryInfo] = None
    sensors: List[SensorReading] = Field(default_factory=list)
    os_info: OsInfo
    security: SecurityInfo
    installed_software: List[InstalledSoftware] = Field(default_factory=list)
    installed_drivers: List[InstalledDriver] = Field(default_factory=list)
    processes: List[ProcessInfo] = Field(default_factory=list)
    services: List[ServiceInfo] = Field(default_factory=list)
    power_plan: Optional[PowerPlanInfo] = None
    virtualization: VirtualizationInfo
    input_devices: List[InputDeviceInfo] = Field(default_factory=list)
    wireless: List[WirelessInfo] = Field(default_factory=list)
    cooling: List[CoolingInfo] = Field(default_factory=list)
    total_processes: int = 0
    total_threads: int = 0
    total_swap_bytes: int = 0
