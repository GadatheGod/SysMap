"""HTML report generator for sysmap."""

import json
import os
from pathlib import Path
from jinja2 import Template

from sysmap.collector import collect_all
from sysmap.collector.models import SystemSnapshot


def generate_html_report(snapshot: SystemSnapshot, output_path: str = "sysmap_report.html") -> str:
    """Generate a comprehensive HTML report."""
    template = Template(HTML_TEMPLATE)
    html = template.render(
        snapshot=snapshot,
        json_snapshot=json.dumps(snapshot.model_dump(mode='json'), indent=2),
    )
    with open(output_path, 'w') as f:
        f.write(html)
    return output_path


def generate_report(output_path: str = "sysmap_report.html", include_json: bool = False) -> str:
    """Generate report and return path."""
    snapshot = collect_all()
    return generate_html_report(snapshot, output_path)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SysMap - System Report</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            line-height: 1.6;
        }
        .header {
            background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
            border-bottom: 1px solid #334155;
            padding: 2rem;
            text-align: center;
        }
        .header h1 {
            font-size: 2rem;
            font-weight: 700;
            background: linear-gradient(135deg, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
        }
        .header p { color: #94a3b8; font-size: 0.9rem; }
        .container { max-width: 1400px; margin: 0 auto; padding: 1rem; }
        .summary-bar {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        .summary-card {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 1.25rem;
            text-align: center;
        }
        .summary-card .label {
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 0.5rem;
        }
        .summary-card .value {
            font-size: 1.25rem;
            font-weight: 700;
            color: #f1f5f9;
        }
        .section {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            margin-bottom: 1rem;
            overflow: hidden;
        }
        .section-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 1rem 1.5rem;
            background: #1e293b;
            cursor: pointer;
            user-select: none;
            border-bottom: 1px solid #334155;
        }
        .section-header h2 {
            font-size: 1.1rem;
            font-weight: 600;
            color: #f1f5f9;
        }
        .section-header .toggle {
            color: #64748b;
            font-size: 1.2rem;
            transition: transform 0.2s;
        }
        .section-header.collapsed .toggle { transform: rotate(-90deg); }
        .section-content {
            padding: 1.5rem;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 1rem;
        }
        .section-content.collapsed { display: none; }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 0.75rem;
        }
        .info-item {
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 0.75rem 1rem;
        }
        .info-item .label {
            font-size: 0.7rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #64748b;
            margin-bottom: 0.25rem;
        }
        .info-item .value {
            font-size: 0.9rem;
            color: #e2e8f0;
            word-break: break-all;
        }
        .badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 9999px;
            font-size: 0.7rem;
            font-weight: 600;
            text-transform: uppercase;
        }
        .badge-green { background: #064e3b; color: #6ee7b7; }
        .badge-blue { background: #1e3a5f; color: #93c5fd; }
        .badge-purple { background: #4c1d95; color: #c4b5fd; }
        .badge-orange { background: #7c2d12; color: #fdba74; }
        .badge-red { background: #7f1d1d; color: #fca5a5; }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #334155;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 0.5rem;
        }
        .progress-fill {
            height: 100%;
            border-radius: 4px;
            transition: width 0.3s;
        }
        .progress-green { background: linear-gradient(90deg, #059669, #10b981); }
        .progress-blue { background: linear-gradient(90deg, #2563eb, #3b82f6); }
        .progress-orange { background: linear-gradient(90deg, #d97706, #f59e0b); }
        .progress-red { background: linear-gradient(90deg, #dc2626, #ef4444); }
        .table-container { overflow-x: auto; }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }
        th {
            text-align: left;
            padding: 0.75rem 1rem;
            background: #0f172a;
            color: #94a3b8;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.7rem;
            letter-spacing: 0.05em;
            border-bottom: 1px solid #334155;
        }
        td {
            padding: 0.75rem 1rem;
            border-bottom: 1px solid #1e293b;
            color: #cbd5e1;
        }
        tr:hover td { background: #1e293b; }
        .footer {
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-size: 0.8rem;
            border-top: 1px solid #334155;
            margin-top: 2rem;
        }
        @media print {
            body { background: white; color: black; }
            .section { break-inside: avoid; }
            .summary-card { border: 1px solid #ccc; }
        }
        .section-header:hover { background: #253349; }
    </style>
</head>
<body>
    <div class="header">
        <h1>SysMap System Report</h1>
        <p>Generated: {{ snapshot.timestamp }} | Platform: {{ snapshot.platform }} | Hostname: {{ snapshot.os_info.hostname }}</p>
    </div>

    <div class="container">
        <!-- Summary Bar -->
        <div class="summary-bar">
            <div class="summary-card">
                <div class="label">CPU</div>
                <div class="value">{{ snapshot.cpu.name[:50] }}</div>
            </div>
            <div class="summary-card">
                <div class="label">Memory</div>
                <div class="value">{{ "%.1f"|format(snapshot.memory.total_physical_bytes / (1024**3)) }} GB</div>
            </div>
            <div class="summary-card">
                <div class="label">GPU</div>
                <div class="value">{{ snapshot.gpus[0].name[:50] if snapshot.gpus else 'N/A' }}</div>
            </div>
            <div class="summary-card">
                <div class="label">Storage</div>
                <div class="value">{{ "%.0f"|format((snapshot.disks | map(attribute='capacity_bytes') | sum) / (1024**3)) }} GB</div>
            </div>
            <div class="summary-card">
                <div class="label">OS</div>
                <div class="value">{{ snapshot.os_info.platform.split()[0] if snapshot.os_info.platform else 'N/A' }}</div>
            </div>
            <div class="summary-card">
                <div class="label">Processes</div>
                <div class="value">{{ snapshot.total_processes }}</div>
            </div>
        </div>

        <!-- System Info -->
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>System Information</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="label">Manufacturer</div>
                        <div class="value">{{ snapshot.system.manufacturer or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Model</div>
                        <div class="value">{{ snapshot.system.model or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Serial Number</div>
                        <div class="value">{{ snapshot.system.serial or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Motherboard</div>
                        <div class="value">{{ snapshot.system.motherboard_model or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">BIOS Vendor</div>
                        <div class="value">{{ snapshot.system.bios_vendor or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">BIOS Version</div>
                        <div class="value">{{ snapshot.system.bios_version or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">BIOS Date</div>
                        <div class="value">{{ snapshot.system.bios_date or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">UEFI Mode</div>
                        <div class="value">{{ 'Yes' if snapshot.system.uefi_mode else 'No' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Chassis Type</div>
                        <div class="value">{{ snapshot.system.chassis_type or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">SMBIOS Version</div>
                        <div class="value">{{ snapshot.system.smbios_version or 'N/A' }}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- CPU Info -->
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>CPU</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="label">Name</div>
                        <div class="value">{{ snapshot.cpu.name or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Manufacturer</div>
                        <div class="value">{{ snapshot.cpu.manufacturer or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Physical Cores</div>
                        <div class="value">{{ snapshot.cpu.physical_cores }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Logical Cores / Threads</div>
                        <div class="value">{{ snapshot.cpu.logical_cores }} / {{ snapshot.cpu.threads }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Base Clock</div>
                        <div class="value">{{ "%.1f"|format(snapshot.cpu.base_clock_mhz / 1000) }} GHz</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Boost Clock</div>
                        <div class="value">{{ "%.1f"|format(snapshot.cpu.boost_clock_mhz / 1000) }} GHz</div>
                    </div>
                    <div class="info-item">
                        <div class="label">L1 Cache</div>
                        <div class="value">{{ snapshot.cpu.l1_cache_kb }} KB</div>
                    </div>
                    <div class="info-item">
                        <div class="label">L2 Cache</div>
                        <div class="value">{{ snapshot.cpu.l2_cache_kb }} KB</div>
                    </div>
                    <div class="info-item">
                        <div class="label">L3 Cache</div>
                        <div class="value">{{ snapshot.cpu.l3_cache_kb }} KB</div>
                    </div>
                    <div class="info-item">
                        <div class="label">TDP</div>
                        <div class="value">{{ "%.0f"|format(snapshot.cpu.tdp_watts) }} W</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Virtualization</div>
                        <div class="value">{{ 'Yes' if snapshot.cpu.virtualization else 'No' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Hyper-Threading</div>
                        <div class="value">{{ 'Yes' if snapshot.cpu.hyperthreading else 'No' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Instruction Extensions</div>
                        <div class="value">{{ ', '.join(snapshot.cpu.extensions[:10]) or 'N/A' }}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Memory Info -->
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Memory</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="label">Total Physical RAM</div>
                        <div class="value">{{ "%.1f"|format(snapshot.memory.total_physical_bytes / (1024**3)) }} GB</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Available Physical RAM</div>
                        <div class="value">{{ "%.1f"|format(snapshot.memory.available_physical_bytes / (1024**3)) }} GB</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Total Virtual Memory</div>
                        <div class="value">{{ "%.1f"|format(snapshot.memory.total_virtual_bytes / (1024**3)) }} GB</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Total Swap</div>
                        <div class="value">{{ "%.1f"|format(snapshot.memory.total_swap_bytes / (1024**3)) }} GB</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Memory Type</div>
                        <div class="value">{{ snapshot.memory.memory_type or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Memory Speed</div>
                        <div class="value">{{ snapshot.memory.memory_speed_mts }} MT/s</div>
                    </div>
                    <div class="info-item">
                        <div class="label">ECC Supported</div>
                        <div class="value">{{ 'Yes' if snapshot.memory.ecc_supported else 'No' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Memory Slots</div>
                        <div class="value">{{ snapshot.memory.slots_used }} / {{ snapshot.memory.slots_total }}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- GPU Info -->
        {% for gpu in snapshot.gpus %}
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>GPU: {{ gpu.name }}</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="label">Name</div>
                        <div class="value">{{ gpu.name }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Architecture</div>
                        <div class="value">{{ gpu.architecture or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">VRAM</div>
                        <div class="value">{{ "%.1f"|format(gpu.vram_bytes / (1024**3)) }} GB {{ gpu.vram_type }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">VRAM Speed</div>
                        <div class="value">{{ gpu.vram_speed_mts }} MT/s</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Bus Width</div>
                        <div class="value">{{ gpu.vram_bus_width }} bit</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Driver Version</div>
                        <div class="value">{{ gpu.driver_version or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">DirectX</div>
                        <div class="value">{{ gpu.directx_version or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">OpenGL</div>
                        <div class="value">{{ gpu.opengl_version or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Vulkan</div>
                        <div class="value">{{ gpu.vulkan_version or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">CUDA Cores</div>
                        <div class="value">{{ gpu.cuda_cores or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">PCIe Interface</div>
                        <div class="value">{{ gpu.pci_interface }} {{ gpu.pci_generation }}</div>
                    </div>
                    {% if gpu.temperature_c > 0 %}
                    <div class="info-item">
                        <div class="label">Temperature</div>
                        <div class="value">{{ "%.0f"|format(gpu.temperature_c) }} °C</div>
                    </div>
                    {% endif %}
                    {% if gpu.power_draw_w > 0 %}
                    <div class="info-item">
                        <div class="label">Power Draw</div>
                        <div class="value">{{ "%.1f"|format(gpu.power_draw_w) }} W</div>
                    </div>
                    {% endif %}
                </div>
            </div>
        </div>
        {% endfor %}

        <!-- Storage -->
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Storage</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                {% for disk in snapshot.disks %}
                <div class="info-grid" style="grid-template-columns: 1fr;">
                    <div class="info-item">
                        <div class="label">Device: {{ disk.name }}</div>
                        <div class="value">{{ disk.model or 'Unknown' }}</div>
                        <div style="margin-top: 0.5rem;">
                            <div class="label">Capacity</div>
                            <div class="value">{{ "%.0f"|format(disk.capacity_bytes / (1024**3)) }} GB {{ disk.interface }} {{ disk.protocol }}</div>
                        </div>
                        {% if disk.temperature_c > 0 %}
                        <div style="margin-top: 0.5rem;">
                            <div class="label">Temperature</div>
                            <div class="value">{{ "%.0f"|format(disk.temperature_c) }} °C</div>
                        </div>
                        {% endif %}
                        {% if disk.health_status %}
                        <div style="margin-top: 0.5rem;">
                            <div class="label">SMART Health</div>
                            <span class="badge {% if 'PASS' in disk.health_status.upper() %}badge-green{% else %}badge-orange{% endif %}">{{ disk.health_status }}</span>
                        </div>
                        {% endif %}
                        {% if disk.power_on_hours > 0 %}
                        <div style="margin-top: 0.5rem;">
                            <div class="label">Power-On Hours</div>
                            <div class="value">{{ disk.power_on_hours }}</div>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- Partitions -->
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Partitions & Filesystems</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Device</th>
                                <th>Mount Point</th>
                                <th>Filesystem</th>
                                <th>Total</th>
                                <th>Used</th>
                                <th>Free</th>
                                <th>Usage</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for part in snapshot.partitions %}
                            <tr>
                                <td>{{ part.name }}</td>
                                <td>{{ part.mount_point or 'N/A' }}</td>
                                <td>{{ part.filesystem }}</td>
                                <td>{{ "%.1f"|format(part.size_bytes / (1024**3)) }} GB</td>
                                <td>{{ "%.1f"|format(part.used_bytes / (1024**3)) }} GB</td>
                                <td>{{ "%.1f"|format(part.free_bytes / (1024**3)) }} GB</td>
                                <td>
                                    <div class="progress-bar">
                                        <div class="progress-fill {% if part.usage_percent > 90 %}progress-red{% elif part.usage_percent > 70 %}progress-orange{% else %}progress-green{% endif %}" style="width: {{ part.usage_percent }}%"></div>
                                    </div>
                                    {{ "%.0f"|format(part.usage_percent) }}%
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Network -->
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Network Adapters</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                {% for adapter in snapshot.network_adapters %}
                <div class="info-grid" style="grid-template-columns: 1fr;">
                    <div class="info-item">
                        <div class="label">{{ adapter.name }} ({{ adapter.adapter_type }})</div>
                        <div class="value">{{ adapter.mac_address or 'N/A' }}</div>
                        {% if adapter.ipv4_address %}
                        <div style="margin-top: 0.5rem;">
                            <div class="label">IPv4</div>
                            <div class="value">{{ adapter.ipv4_address }}</div>
                        </div>
                        {% endif %}
                        {% if adapter.ipv6_address %}
                        <div style="margin-top: 0.5rem;">
                            <div class="label">IPv6</div>
                            <div class="value">{{ adapter.ipv6_address }}</div>
                        </div>
                        {% endif %}
                        {% if adapter.speed_mbps > 0 %}
                        <div style="margin-top: 0.5rem;">
                            <div class="label">Speed</div>
                            <div class="value">{{ adapter.speed_mbps }} Mbps</div>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>

        <!-- USB Devices -->
        {% if snapshot.usb_devices %}
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>USB Devices</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Device</th>
                                <th>Vendor ID</th>
                                <th>Product ID</th>
                                <th>Speed</th>
                                <th>Class</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for dev in snapshot.usb_devices %}
                            <tr>
                                <td>{{ dev.name or dev.product_name or 'USB Device' }}</td>
                                <td>{{ dev.vendor_id }}</td>
                                <td>{{ dev.product_id }}</td>
                                <td>{{ dev.speed }}</td>
                                <td>{{ dev.class_name }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- PCI Devices -->
        {% if snapshot.pci_devices %}
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>PCI/PCIe Devices</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Device</th>
                                <th>Vendor ID</th>
                                <th>Device ID</th>
                                <th>Class</th>
                                <th>Driver</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for dev in snapshot.pci_devices %}
                            <tr>
                                <td>{{ dev.name }}</td>
                                <td>{{ dev.vendor_id }}</td>
                                <td>{{ dev.device_id }}</td>
                                <td>{{ dev.class_name }}</td>
                                <td>{{ dev.driver or 'N/A' }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Sensors -->
        {% if snapshot.sensors %}
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Sensors</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Category</th>
                                <th>Value</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for sensor in snapshot.sensors %}
                            <tr>
                                <td>{{ sensor.name }}</td>
                                <td><span class="badge badge-blue">{{ sensor.category }}</span></td>
                                <td>{{ "%.1f"|format(sensor.value) }} {{ sensor.unit }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- OS Info -->
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Operating System</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="label">Hostname</div>
                        <div class="value">{{ snapshot.os_info.hostname }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Platform</div>
                        <div class="value">{{ snapshot.os_info.platform }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Kernel</div>
                        <div class="value">{{ snapshot.os_info.kernel_version }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Architecture</div>
                        <div class="value">{{ snapshot.os_info.architecture }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Language</div>
                        <div class="value">{{ snapshot.os_info.language or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Locale</div>
                        <div class="value">{{ snapshot.os_info.locale or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Timezone</div>
                        <div class="value">{{ snapshot.os_info.timezone }}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Security -->
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Security</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="label">TPM</div>
                        <div class="value">
                            {% if snapshot.security.tpm_present %}
                            <span class="badge badge-green">{{ snapshot.security.tpm_version }}</span>
                            {% else %}
                            <span class="badge badge-red">Not Found</span>
                            {% endif %}
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="label">Secure Boot</div>
                        <div class="value">
                            {% if snapshot.security.secure_boot %}
                            <span class="badge {% if 'Enabled' in snapshot.security.secure_boot %}badge-green{% else %}badge-red{% endif %}">{{ snapshot.security.secure_boot }}</span>
                            {% else %}
                            <span class="badge badge-orange">Unknown</span>
                            {% endif %}
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="label">Firewall</div>
                        <div class="value">
                            {% if snapshot.security.firewall_enabled %}
                            <span class="badge badge-green">Enabled</span>
                            {% else %}
                            <span class="badge badge-red">Disabled</span>
                            {% endif %}
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="label">Antivirus</div>
                        <div class="value">{{ snapshot.security.antivirus_name or 'None' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">BitLocker</div>
                        <div class="value">{{ snapshot.security.bitlocker_status or 'N/A' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Virtualization Based Security</div>
                        <div class="value">{{ 'Enabled' if snapshot.security.virtualization_based_security else 'Disabled' }}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Virtualization -->
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Virtualization & Containers</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="label">Docker</div>
                        <div class="value">
                            {% if snapshot.virtualization.docker_installed %}
                            <span class="badge badge-green">{{ snapshot.virtualization.docker_version }}</span>
                            {% else %}
                            <span class="badge badge-red">Not Installed</span>
                            {% endif %}
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="label">Kubernetes</div>
                        <div class="value">
                            {% if snapshot.virtualization.kubernetes_installed %}
                            <span class="badge badge-green">{{ snapshot.virtualization.kubernetes_version }}</span>
                            {% else %}
                            <span class="badge badge-red">Not Installed</span>
                            {% endif %}
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="label">WSL</div>
                        <div class="value">
                            {% if snapshot.virtualization.wsl_installed %}
                            <span class="badge badge-green">{{ snapshot.virtualization.wsl_distributions | join(', ') }}</span>
                            {% else %}
                            <span class="badge badge-red">Not Installed</span>
                            {% endif %}
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="label">Hyper-V</div>
                        <div class="value">{{ 'Enabled' if snapshot.virtualization.hyper_v_enabled else 'Disabled' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">VM Detected</div>
                        <div class="value">{{ snapshot.virtualization.vm_host or 'No' }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Nested Virtualization</div>
                        <div class="value">{{ 'Yes' if snapshot.virtualization.nested_virtualization else 'No' }}</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Wireless -->
        {% if snapshot.wireless %}
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Wireless</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                {% for w in snapshot.wireless %}
                <div class="info-grid" style="grid-template-columns: 1fr;">
                    <div class="info-item">
                        <div class="label">{{ w.adapter_name }}</div>
                        <div class="value">{{ w.current_ssid or 'Not Connected' }}</div>
                        {% if w.current_bssid %}
                        <div style="margin-top: 0.5rem;">
                            <div class="label">BSSID</div>
                            <div class="value">{{ w.current_bssid }}</div>
                        </div>
                        {% endif %}
                        {% if w.rssi_dbm != 0 %}
                        <div style="margin-top: 0.5rem;">
                            <div class="label">Signal Strength</div>
                            <div class="value">{{ w.rssi_dbm }} dBm</div>
                        </div>
                        {% endif %}
                        {% if w.security_type %}
                        <div style="margin-top: 0.5rem;">
                            <div class="label">Security</div>
                            <div class="value">{{ w.security_type }}</div>
                        </div>
                        {% endif %}
                    </div>
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}

        <!-- Battery -->
        {% if snapshot.battery %}
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Battery</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="label">State</div>
                        <div class="value">
                            <span class="badge {% if 'full' in snapshot.battery.state %}badge-green{% elif 'charging' in snapshot.battery.state %}badge-blue{% else %}badge-orange{% endif %}">{{ snapshot.battery.state }}</span>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="label">Charge</div>
                        <div class="value">{{ "%.0f"|format(snapshot.battery.charge_percent) }}%</div>
                        <div class="progress-bar">
                            <div class="progress-fill {% if snapshot.battery.charge_percent > 50 %}progress-green{% elif snapshot.battery.charge_percent > 20 %}progress-orange{% else %}progress-red{% endif %}" style="width: {{ snapshot.battery.charge_percent }}%"></div>
                        </div>
                    </div>
                    <div class="info-item">
                        <div class="label">Design Capacity</div>
                        <div class="value">{{ "%.1f"|format(snapshot.battery.design_capacity_wh) }} Wh</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Full Capacity</div>
                        <div class="value">{{ "%.1f"|format(snapshot.battery.full_capacity_wh) }} Wh</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Health</div>
                        <div class="value">{{ "%.0f"|format(snapshot.battery.health_percent) }}%</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Cycle Count</div>
                        <div class="value">{{ snapshot.battery.cycle_count }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Voltage</div>
                        <div class="value">{{ "%.2f"|format(snapshot.battery.voltage) }} V</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Temperature</div>
                        <div class="value">{{ "%.0f"|format(snapshot.battery.temperature_c) }} °C</div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Bluetooth -->
        {% if snapshot.bluetooth %}
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Bluetooth</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="info-grid">
                    <div class="info-item">
                        <div class="label">Adapter</div>
                        <div class="value">{{ snapshot.bluetooth.adapter_name }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Manufacturer</div>
                        <div class="value">{{ snapshot.bluetooth.adapter_manufacturer }}</div>
                    </div>
                    <div class="info-item">
                        <div class="label">Version</div>
                        <div class="value">{{ snapshot.bluetooth.adapter_version }}</div>
                    </div>
                </div>
            </div>
        </div>
        {% endif %}

        <!-- Processes -->
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Top Processes ({{ snapshot.total_processes }} total)</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>PID</th>
                                <th>Name</th>
                                <th>User</th>
                                <th>CPU %</th>
                                <th>Memory</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for proc in snapshot.processes %}
                            <tr>
                                <td>{{ proc.pid }}</td>
                                <td>{{ proc.name }}</td>
                                <td>{{ proc.user }}</td>
                                <td>{{ "%.1f"|format(proc.cpu_percent) }}%</td>
                                <td>{{ "%.1f"|format(proc.memory_bytes / (1024*1024)) }} MB</td>
                                <td>{{ proc.status }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- Software -->
        {% if snapshot.installed_software %}
        <div class="section">
            <div class="section-header" onclick="toggleSection(this)">
                <h2>Installed Software ({{ snapshot.installed_software | length }})</h2>
                <span class="toggle">&#9662;</span>
            </div>
            <div class="section-content">
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Version</th>
                                <th>Publisher</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for sw in snapshot.installed_software %}
                            <tr>
                                <td>{{ sw.name }}</td>
                                <td>{{ sw.version }}</td>
                                <td>{{ sw.publisher }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        {% endif %}

    </div>

    <div class="footer">
        <p>SysMap System Report - Generated {{ snapshot.timestamp }}</p>
        <p>Platform: {{ snapshot.platform }} | Hostname: {{ snapshot.os_info.hostname }}</p>
    </div>

    <script>
        function toggleSection(header) {
            header.classList.toggle('collapsed');
            const content = header.nextElementSibling;
            content.classList.toggle('collapsed');
        }
    </script>
</body>
</html>"""
