# SysMap - Complete System Profiler

> Capture all hardware and software information from your system and generate beautiful reports. Like HWiNFO + GPU-Z + dxdiag combined.

**Developed by Praveen** | MIT License

![Platform](https://img.shields.io/badge/Linux-FF0000?style=for-the-badge&logo=linux&logoColor=white)
![Platform](https://img.shields.io/badge/Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white)
![Platform](https://img.shields.io/badge/macOS-000000?style=for-the-badge&logo=apple&logoColor=white)

## Screenshots

![SysMap Dashboard](https://raw.githubusercontent.com/praveen/sysmap/main/screenshots/dashboard.png)
![SysMap System Info](https://raw.githubusercontent.com/praveen/sysmap/main/screenshots/system.png)
![SysMap Storage](https://raw.githubusercontent.com/praveen/sysmap/main/screenshots/storage.png)

## What is SysMap and How is it Useful?

SysMap is a comprehensive system profiling tool that captures **1000+ data points** from your computer including CPU, RAM, GPU, storage, network, USB devices, sensors, BIOS, and much more.

### Why you need SysMap:

- **IT Administrators**: Quickly inventory all systems in your network without manual inspection
- **Developers**: Share exact system specs when reporting bugs or asking for help
- **Gamers**: Check GPU details, VRAM, driver versions, and system compatibility
- **System Builders**: Verify all components are detected and working properly
- **Troubleshooting**: Identify hardware issues via SMART status, temperatures, and sensor data
- **Reporting**: Generate professional PDF/HTML reports for documentation or audits
- **Cross-platform**: Works on Linux, Windows, and macOS with consistent output
- **Export Options**: Get data as interactive dashboard, PDF report, HTML report, Markdown, or JSON

### Use Cases:

```bash
# Generate a full system report for your IT department
sysmap report --pdf

# Share your specs with a developer forum
sysmap export-json -o specs.json

# Quick check before buying a new GPU
sysmap info

# Monitor temperatures and sensors
sysmap server  # then open dashboard
```

## Features

- **Comprehensive Data Collection**: CPU, RAM, GPU, storage, network, USB, Bluetooth, sensors, battery, wireless, PCI devices, and more
- **Cross-Platform**: Works on Linux, Windows, and macOS
- **Interactive Dashboard**: Beautiful React-based web interface with tabbed navigation
- **Report Generation**: Export to HTML, PDF, Markdown, or JSON
- **CLI Tool**: Quick system info from terminal
- **Multiple GPU Support**: Detects all GPUs including NVIDIA, AMD, and Intel
- **Real-time Data**: Live system information via web dashboard

## Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Quick Install (Recommended)

```bash
pip install sysmap
```

### Install from Source

```bash
# Clone the repository
git clone https://github.com/GadatheGod/sysmap.git
cd sysmap

# Install the package
pip install -e .

# For PDF support
pip install -e ".[pdf]"

# For development
pip install -e ".[dev]"
```

## Usage

### Quick System Summary

```bash
sysmap info
```

Output:
```
============================================================
  SysMap - System Summary
============================================================
  Platform:    linux
  Hostname:    mycomputer
  CPU:         Intel(R) Core(TM) i7-10700K @ 3.80GHz
  RAM:         32.0 GB
  GPU:         NVIDIA GeForce RTX 3080
  Storage:     2048 GB
  OS:          Linux-6.5.0-generic-x86_64
  Processes:   342
============================================================
```

### Launch Interactive Dashboard

```bash
sysmap server
```

This starts a web server at `http://localhost:8000` with:
- Real-time system monitoring
- Tabbed navigation (Overview, System, CPU, Memory, GPU, Storage, Network, Devices, Security, Software, Processes)
- Beautiful dark-themed UI
- Download buttons for PDF, Markdown, and JSON exports

### Generate Reports

```bash
# Generate HTML report
sysmap report

# Generate PDF report (requires weasyprint)
sysmap report --pdf

# Generate JSON export
sysmap report --json

# Generate Markdown export
sysmap export-json -o report.md

# Custom output path
sysmap report -o /path/to/report.html
```

### API Endpoints

The server exposes REST API endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /api/snapshot` | Complete system snapshot |
| `GET /api/summary` | Quick summary |
| `GET /api/cpu` | CPU information |
| `GET /api/memory` | Memory information |
| `GET /api/gpus` | All GPU information |
| `GET /api/disks` | Storage devices |
| `GET /api/partitions` | Partitions and filesystems |
| `GET /api/network` | Network adapters |
| `GET /api/sensors` | Sensor readings |
| `GET /api/system` | System information |
| `GET /api/os` | OS information |
| `GET /api/security` | Security status |
| `GET /api/virtualization` | Virtualization info |
| `GET /api/usb` | USB devices and controllers |
| `GET /api/processes` | Running processes |
| `GET /api/monitors` | Monitor information |
| `GET /api/battery` | Battery information |
| `GET /api/bluetooth` | Bluetooth information |
| `GET /api/audio` | Audio devices |
| `GET /api/pci` | PCI devices |
| `GET /api/wireless` | Wireless information |
| `GET /api/cooling` | Cooling information |
| `GET /api/software` | Installed software |
| `GET /api/services` | Services |
| `GET /api/export/pdf` | Download PDF report |
| `GET /api/export/md` | Download Markdown report |
| `GET /api/export/json` | Download JSON data |

## Data Collected

### System Information
- Manufacturer, model, serial number, SKU, UUID
- Motherboard details, BIOS/UEFI information
- Chassis type, SMBIOS version

### CPU
- Name, manufacturer, cores, threads
- Clock speeds (base, boost, per-core)
- Cache (L1/L2/L3), TDP
- Instruction extensions, virtualization support
- Per-core utilization and temperature

### Memory
- Total/available physical RAM
- Swap space, virtual memory
- Memory type, speed, voltage
- Slot information, ECC support

### GPU (All GPUs Detected)
- Name, architecture, VRAM, bus width
- Driver version, DirectX/OpenGL/Vulkan versions
- CUDA cores/stream processors
- Temperature, power draw, fan speed
- PCIe interface details

### Storage
- Disk models, capacities, interfaces
- SMART health, temperature, power-on hours
- Partitions, filesystems, mount points
- Usage percentages

### Network
- All adapters (Ethernet, WiFi, etc.)
- IP addresses, MAC addresses, DNS
- Speed, duplex, MTU
- I/O statistics

### USB
- All connected devices with vendor/product IDs
- USB controllers
- Speed, class, driver information

### Sensors
- CPU/GPU/disk temperatures
- Fan speeds (RPM)
- Voltages (Vcore, +12V, +5V, +3.3V)
- Power readings

### OS & Security
- OS version, kernel, architecture
- TPM, Secure Boot, BitLocker
- Firewall, antivirus status
- Virtualization (Docker, Kubernetes, WSL, Hyper-V)

### And much more!
- Bluetooth devices, audio devices
- PCI/PCIe devices, wireless adapters
- Battery information (laptops), cooling systems
- Installed software, running processes

## Architecture

```
sysmap/
├── sysmap/               # Python package
│   ├── collector/        # Cross-platform data collection
│   │   ├── models.py     # Pydantic data models
│   │   ├── shared.py     # Shared utilities
│   │   ├── platform_linux.py
│   │   ├── platform_windows.py
│   │   ├── platform_mac.py
│   │   └── __init__.py
│   ├── server/           # FastAPI backend
│   │   ├── app.py        # API server
│   │   ├── export_html.py
│   │   └── export_pdf.py
│   └── cli.py            # CLI entry point
├── frontend/             # React dashboard
│   └── src/
├── pyproject.toml
└── README.md
```

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Lint
ruff check .

# Type check
mypy .
```

## License

MIT License - Developed by Praveen

Copyright (c) 2025 Praveen

See [LICENSE](LICENSE) for details.
