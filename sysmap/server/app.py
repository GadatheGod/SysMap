"""FastAPI server for sysmap."""

import json
import math
import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from contextlib import asynccontextmanager

from sysmap.collector import collect_all, collect_summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start the collector on startup."""
    app.state.snapshot = None
    yield


app = FastAPI(
    title="SysMap",
    description="Complete System Profiler - captures all hardware/software info",
    version="0.1.0",
    lifespan=lifespan,
)

frontend_dist = Path(__file__).parent.parent.parent / "frontend" / "dist"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend static assets
app.mount("/assets", StaticFiles(directory=str(frontend_dist / "assets")), name="assets")


@app.get("/")
async def dashboard():
    """Serve the React dashboard."""
    frontend_dir = Path(__file__).parent.parent.parent / "frontend" / "dist"
    index_html = frontend_dir / "index.html"

    if index_html.exists():
        return FileResponse(index_html)

    # Fallback: serve a simple HTML page if frontend not built
    return HTMLResponse(
        content="""<!DOCTYPE html>
<html>
<head><title>SysMap</title></head>
<body>
<h1>SysMap - System Profiler</h1>
<p>Frontend not built yet. Run the CLI to generate reports.</p>
<p>Usage: <code>sysmap report</code> to generate HTML report</p>
</body>
</html>"""
    )


@app.get("/api/snapshot")
async def get_snapshot():
    """Get the complete system snapshot."""
    try:
        snapshot = collect_all()
        return snapshot.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary")
async def get_summary():
    """Get a quick system summary."""
    try:
        return collect_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cpu")
async def get_cpu():
    """Get CPU info."""
    try:
        snapshot = collect_all()
        return snapshot.cpu.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory")
async def get_memory():
    """Get memory info."""
    try:
        snapshot = collect_all()
        return snapshot.memory.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/gpus")
async def get_gpus():
    """Get GPU info."""
    try:
        snapshot = collect_all()
        return [g.model_dump(mode='json') for g in snapshot.gpus]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/disks")
async def get_disks():
    """Get disk info."""
    try:
        snapshot = collect_all()
        return [d.model_dump(mode='json') for d in snapshot.disks]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/partitions")
async def get_partitions():
    """Get partition info."""
    try:
        snapshot = collect_all()
        return [p.model_dump(mode='json') for p in snapshot.partitions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/network")
async def get_network():
    """Get network adapter info."""
    try:
        snapshot = collect_all()
        return [n.model_dump(mode='json') for n in snapshot.network_adapters]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sensors")
async def get_sensors():
    """Get sensor readings."""
    try:
        snapshot = collect_all()
        return [s.model_dump(mode='json') for s in snapshot.sensors]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/system")
async def get_system():
    """Get system info."""
    try:
        snapshot = collect_all()
        return snapshot.system.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/os")
async def get_os():
    """Get OS info."""
    try:
        snapshot = collect_all()
        return snapshot.os_info.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/security")
async def get_security():
    """Get security info."""
    try:
        snapshot = collect_all()
        return snapshot.security.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/virtualization")
async def get_virtualization():
    """Get virtualization info."""
    try:
        snapshot = collect_all()
        return snapshot.virtualization.model_dump(mode='json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/usb")
async def get_usb():
    """Get USB device info."""
    try:
        snapshot = collect_all()
        return {
            "devices": [d.model_dump(mode='json') for d in snapshot.usb_devices],
            "controllers": [c.model_dump(mode='json') for c in snapshot.usb_controllers],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/processes")
async def get_processes():
    """Get process info."""
    try:
        snapshot = collect_all()
        return {
            "processes": [p.model_dump(mode='json') for p in snapshot.processes],
            "total_processes": snapshot.total_processes,
            "total_threads": snapshot.total_threads,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/monitors")
async def get_monitors():
    """Get monitor info."""
    try:
        snapshot = collect_all()
        return [m.model_dump(mode='json') for m in snapshot.monitors]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/battery")
async def get_battery():
    """Get battery info."""
    try:
        snapshot = collect_all()
        if snapshot.battery:
            return snapshot.battery.model_dump(mode='json')
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/bluetooth")
async def get_bluetooth():
    """Get Bluetooth info."""
    try:
        snapshot = collect_all()
        if snapshot.bluetooth:
            return snapshot.bluetooth.model_dump(mode='json')
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/audio")
async def get_audio():
    """Get audio device info."""
    try:
        snapshot = collect_all()
        return [a.model_dump(mode='json') for a in snapshot.audio_devices]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/pci")
async def get_pci():
    """Get PCI device info."""
    try:
        snapshot = collect_all()
        return [p.model_dump(mode='json') for p in snapshot.pci_devices]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wireless")
async def get_wireless():
    """Get wireless info."""
    try:
        snapshot = collect_all()
        return [w.model_dump(mode='json') for w in snapshot.wireless]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cooling")
async def get_cooling():
    """Get cooling info."""
    try:
        snapshot = collect_all()
        return [c.model_dump(mode='json') for c in snapshot.cooling]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/software")
async def get_software():
    """Get installed software."""
    try:
        snapshot = collect_all()
        return [s.model_dump(mode='json') for s in snapshot.installed_software]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/services")
async def get_services():
    """Get services info."""
    try:
        snapshot = collect_all()
        return [s.model_dump(mode='json') for s in snapshot.services]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/json")
async def export_json():
    """Export full snapshot as JSON."""
    try:
        snapshot = collect_all()
        import tempfile
        fd, path = tempfile.mkstemp(suffix='.json')
        with os.fdopen(fd, 'w') as f:
            json.dump(snapshot.model_dump(mode='json'), f, indent=2)
        return FileResponse(path, media_type='application/json', filename='sysmap_report.json')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/export/pdf")
async def export_pdf():
    """Export full snapshot as PDF."""
    try:
        from sysmap.server.export_html import generate_html_report
        from sysmap.server.export_pdf import generate_pdf_report
        import tempfile

        snapshot = collect_all()
        fd_html, html_path = tempfile.mkstemp(suffix='.html')
        os.close(fd_html)
        generate_html_report(snapshot, html_path)

        fd_pdf, pdf_path = tempfile.mkstemp(suffix='.pdf')
        os.close(fd_pdf)
        generate_pdf_report(pdf_path, html_path)

        # Clean up HTML
        try:
            os.unlink(html_path)
        except Exception:
            pass

        return FileResponse(pdf_path, media_type='application/pdf', filename='sysmap_report.pdf')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF export failed: {str(e)}")


@app.get("/api/export/md")
async def export_md():
    """Export full snapshot as Markdown."""
    try:
        snapshot = collect_all()

        md = generate_markdown(snapshot)

        import tempfile
        fd, path = tempfile.mkstemp(suffix='.md')
        with os.fdopen(fd, 'w') as f:
            f.write(md)

        return FileResponse(path, media_type='text/markdown', filename='sysmap_report.md')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Markdown export failed: {str(e)}")


def generate_markdown(snapshot) -> str:
    """Generate a Markdown report from snapshot data."""
    lines = []
    lines.append("# SysMap System Report")
    lines.append("")
    lines.append(f"**Generated:** {snapshot.timestamp}")
    lines.append(f"**Platform:** {snapshot.platform}")
    lines.append(f"**Hostname:** {snapshot.os_info.hostname}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # System
    lines.append("## System Information")
    lines.append("")
    lines.append(f"- **Manufacturer:** {snapshot.system.manufacturer or 'N/A'}")
    lines.append(f"- **Model:** {snapshot.system.model or 'N/A'}")
    lines.append(f"- **Serial Number:** {snapshot.system.serial or 'N/A'}")
    lines.append(f"- **Motherboard:** {snapshot.system.motherboard_model or 'N/A'}")
    lines.append(f"- **BIOS Vendor:** {snapshot.system.bios_vendor or 'N/A'}")
    lines.append(f"- **BIOS Version:** {snapshot.system.bios_version or 'N/A'}")
    lines.append(f"- **BIOS Date:** {snapshot.system.bios_date or 'N/A'}")
    lines.append(f"- **UEFI Mode:** {'Yes' if snapshot.system.uefi_mode else 'No'}")
    lines.append(f"- **Chassis Type:** {snapshot.system.chassis_type or 'N/A'}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # CPU
    lines.append("## CPU")
    lines.append("")
    lines.append(f"- **Name:** {snapshot.cpu.name or 'N/A'}")
    lines.append(f"- **Manufacturer:** {snapshot.cpu.manufacturer or 'N/A'}")
    lines.append(f"- **Physical Cores:** {snapshot.cpu.physical_cores}")
    lines.append(f"- **Logical Cores / Threads:** {snapshot.cpu.logical_cores} / {snapshot.cpu.threads}")
    lines.append(f"- **Base Clock:** {(snapshot.cpu.base_clock_mhz / 1000):.2f} GHz")
    lines.append(f"- **Boost Clock:** {(snapshot.cpu.boost_clock_mhz / 1000):.2f} GHz")
    lines.append(f"- **L1 Cache:** {snapshot.cpu.l1_cache_kb} KB")
    lines.append(f"- **L2 Cache:** {snapshot.cpu.l2_cache_kb} KB")
    lines.append(f"- **L3 Cache:** {snapshot.cpu.l3_cache_kb} KB")
    lines.append(f"- **TDP:** {snapshot.cpu.tdp_watts:.0f} W")
    lines.append(f"- **Virtualization:** {'Yes' if snapshot.cpu.virtualization else 'No'}")
    lines.append(f"- **Extensions:** {', '.join(snapshot.cpu.extensions[:10]) or 'N/A'}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Memory
    lines.append("## Memory")
    lines.append("")
    lines.append(f"- **Total Physical RAM:** {format_bytes(snapshot.memory.total_physical_bytes)}")
    lines.append(f"- **Available Physical RAM:** {format_bytes(snapshot.memory.available_physical_bytes)}")
    lines.append(f"- **Total Virtual Memory:** {format_bytes(snapshot.memory.total_virtual_bytes)}")
    lines.append(f"- **Total Swap:** {format_bytes(snapshot.memory.total_swap_bytes)}")
    lines.append(f"- **Memory Type:** {snapshot.memory.memory_type or 'N/A'}")
    lines.append(f"- **Memory Speed:** {snapshot.memory.memory_speed_mts} MT/s")
    lines.append(f"- **ECC Supported:** {'Yes' if snapshot.memory.ecc_supported else 'No'}")
    lines.append(f"- **Memory Slots:** {snapshot.memory.slots_used} / {snapshot.memory.slots_total}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # GPUs
    for gpu in snapshot.gpus:
        lines.append("## GPU")
        lines.append("")
        lines.append(f"### {gpu.name}")
        lines.append("")
        lines.append(f"- **Architecture:** {gpu.architecture or 'N/A'}")
        lines.append(f"- **VRAM:** {format_bytes(gpu.vram_bytes)} {gpu.vram_type}")
        lines.append(f"- **VRAM Speed:** {gpu.vram_speed_mts} MT/s")
        lines.append(f"- **Bus Width:** {gpu.vram_bus_width} bit")
        lines.append(f"- **Driver Version:** {gpu.driver_version or 'N/A'}")
        lines.append(f"- **DirectX:** {gpu.directx_version or 'N/A'}")
        lines.append(f"- **OpenGL:** {gpu.opengl_version or 'N/A'}")
        lines.append(f"- **Vulkan:** {gpu.vulkan_version or 'N/A'}")
        lines.append(f"- **CUDA Cores:** {gpu.cuda_cores or 'N/A'}")
        lines.append(f"- **PCIe Interface:** {gpu.pci_interface} {gpu.pci_generation}")
        if gpu.temperature_c > 0:
            lines.append(f"- **Temperature:** {gpu.temperature_c:.0f} °C")
        if gpu.power_draw_w > 0:
            lines.append(f"- **Power Draw:** {gpu.power_draw_w:.1f} W")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Storage
    lines.append("## Storage")
    lines.append("")
    for disk in snapshot.disks:
        lines.append(f"### {disk.model or 'Unknown'}")
        lines.append("")
        lines.append(f"- **Device:** `{disk.name}`")
        lines.append(f"- **Capacity:** {format_bytes(disk.capacity_bytes)}")
        lines.append(f"- **Interface:** {disk.interface} {disk.protocol}")
        if disk.temperature_c > 0:
            lines.append(f"- **Temperature:** {disk.temperature_c:.0f} °C")
        if disk.health_status:
            lines.append(f"- **SMART Health:** {disk.health_status}")
        if disk.power_on_hours > 0:
            lines.append(f"- **Power-On Hours:** {disk.power_on_hours}")
        lines.append("")

    if not snapshot.disks:
        lines.append("No storage devices detected.")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Partitions
    lines.append("## Partitions & Filesystems")
    lines.append("")
    if snapshot.partitions:
        lines.append("| Device | Mount Point | Filesystem | Total | Used | Free | Usage |")
        lines.append("|--------|-------------|------------|-------|------|------|-------|")
        for part in snapshot.partitions:
            lines.append(f"| `{part.name}` | {part.mount_point or 'N/A'} | {part.filesystem} | {format_bytes(part.size_bytes)} | {format_bytes(part.used_bytes)} | {format_bytes(part.free_bytes)} | {part.usage_percent:.0f}% |")
    else:
        lines.append("No partitions detected.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Network
    lines.append("## Network Adapters")
    lines.append("")
    for adapter in snapshot.network_adapters:
        lines.append(f"### {adapter.name}")
        lines.append("")
        lines.append(f"- **Type:** {adapter.adapter_type}")
        lines.append(f"- **MAC:** `{adapter.mac_address or 'N/A'}`")
        lines.append(f"- **IPv4:** `{adapter.ipv4_address or 'N/A'}`")
        if adapter.speed_mbps > 0:
            lines.append(f"- **Speed:** {adapter.speed_mbps} Mbps")
        lines.append(f"- **State:** {adapter.connection_state}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # OS
    lines.append("## Operating System")
    lines.append("")
    lines.append(f"- **Hostname:** {snapshot.os_info.hostname}")
    lines.append(f"- **Platform:** {snapshot.os_info.platform}")
    lines.append(f"- **Kernel:** {snapshot.os_info.kernel_version}")
    lines.append(f"- **Architecture:** {snapshot.os_info.architecture}")
    lines.append(f"- **Language:** {snapshot.os_info.language or 'N/A'}")
    lines.append(f"- **Locale:** {snapshot.os_info.locale or 'N/A'}")
    lines.append(f"- **Timezone:** {snapshot.os_info.timezone}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Security
    lines.append("## Security")
    lines.append("")
    lines.append(f"- **TPM:** {snapshot.security.tpm_version if snapshot.security.tpm_present else 'Not Found'}")
    lines.append(f"- **Secure Boot:** {snapshot.security.secure_boot or 'Unknown'}")
    lines.append(f"- **Firewall:** {'Enabled' if snapshot.security.firewall_enabled else 'Disabled'}")
    lines.append(f"- **Antivirus:** {snapshot.security.antivirus_name or 'None'}")
    lines.append(f"- **BitLocker:** {snapshot.security.bitlocker_status or 'N/A'}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Virtualization
    lines.append("## Virtualization & Containers")
    lines.append("")
    lines.append(f"- **Docker:** {'Yes' if snapshot.virtualization.docker_installed else 'No'}")
    lines.append(f"- **Kubernetes:** {'Yes' if snapshot.virtualization.kubernetes_installed else 'No'}")
    lines.append(f"- **WSL:** {'Yes' if snapshot.virtualization.wsl_installed else 'No'}")
    lines.append(f"- **Hyper-V:** {'Enabled' if snapshot.virtualization.hyper_v_enabled else 'Disabled'}")
    lines.append(f"- **VM Detected:** {snapshot.virtualization.vm_host or 'No'}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Processes
    lines.append("## Top Processes")
    lines.append("")
    lines.append(f"Total processes: {snapshot.total_processes}")
    lines.append("")
    if snapshot.processes:
        lines.append("| PID | Name | User | CPU % | Memory | Status |")
        lines.append("|-----|------|------|-------|--------|--------|")
        for proc in snapshot.processes:
            lines.append(f"| {proc.pid} | {proc.name} | {proc.user} | {proc.cpu_percent:.1f}% | {format_bytes(proc.memory_bytes)} | {proc.status} |")
    lines.append("")

    return "\n".join(lines)


def format_bytes(bytes_val):
    """Format bytes to human readable string."""
    if bytes_val == 0:
        return "0 B"
    k = 1024
    sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    i = int(math.log(bytes_val) / math.log(k))
    return f"{bytes_val / (k ** i):.1f} {sizes[i]}"
