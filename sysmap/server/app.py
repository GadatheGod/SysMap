"""FastAPI server for sysmap."""

import json
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def dashboard():
    """Serve the React dashboard."""
    frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"
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
