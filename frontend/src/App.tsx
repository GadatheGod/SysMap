import React, { useState, useEffect } from 'react'
import {
  Cpu, MemoryStick, Monitor, HardDrive, Wifi, Usb,
  Thermometer, Battery, Shield, Database, Settings,
  Globe, ChevronDown, ChevronRight, Download,
  Activity, Zap, Fan, Bluetooth, Layers,
  Cpu as CpuIcon, HardDrive as StorageIcon,
  Monitor as MonitorIcon, Plug, Mic, Camera,
  Network, Fan as FanIcon,
  HardDrive as HDD,
  Monitor as DisplayIcon,
  Usb as UsbIcon,
  AudioLines,
  Bluetooth as BluetoothIcon,
  Camera as CameraIcon,
  Server,
  Package,
  Terminal
} from 'lucide-react'

interface SystemSnapshot {
  timestamp: string
  platform: string
  system: any
  cpu: any
  memory: any
  gpus: any[]
  monitors: any[]
  disks: any[]
  partitions: any[]
  network_adapters: any[]
  usb_devices: any[]
  sensors: any[]
  os_info: any
  security: any
  virtualization: any
  battery: any | null
  wireless: any[]
  processes: any[]
  total_processes: number
  total_threads: number
  installed_software: any[]
}

const API_BASE = '/api'

async function fetchApi(endpoint: string): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}${endpoint}`)
    return await res.json()
  } catch (err) {
    return null
  }
}

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

function Badge({ children, color }: { children: React.ReactNode; color: string }) {
  const classes: Record<string, string> = {
    green: 'badge-green',
    blue: 'badge-blue',
    purple: 'badge-purple',
    orange: 'badge-orange',
    red: 'badge-red',
  }
  return <span className={`badge ${classes[color] || classes.blue}`}>{children}</span>
}

function InfoCard({ label, value, icon }: { label: string; value: string | number; icon?: React.ReactNode }) {
  return (
    <div className="info-card">
      <div className="text-xs text-slate-500 uppercase tracking-wider mb-2 flex items-center gap-2">
        {icon && <span className="text-blue-400">{icon}</span>}
        {label}
      </div>
      <div className="text-sm font-medium text-slate-200 break-all">{value}</div>
    </div>
  )
}

function ProgressBar({ value, max = 100, color = 'blue' }: { value: number; max?: number; color?: string }) {
  const pct = Math.min((value / max) * 100, 100)
  const colorMap: Record<string, string> = {
    green: 'progress-green',
    blue: 'progress-blue',
    orange: 'progress-orange',
    red: 'progress-red',
  }
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs text-slate-400">
        <span>{pct.toFixed(0)}%</span>
        <span>{formatBytes(value)} / {formatBytes(max)}</span>
      </div>
      <div className="progress-bar">
        <div className={`progress-fill ${colorMap[color] || colorMap.blue}`} style={{ width: `${pct}%` }} />
      </div>
    </div>
  )
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  const [open, setOpen] = useState(true)
  return (
    <div className="section-card">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 hover:bg-slate-700/20 transition-colors"
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border border-blue-500/20 flex items-center justify-center">
            <span className="text-blue-400">{icon}</span>
          </div>
          <h3 className="text-base font-semibold text-slate-100">{title}</h3>
        </div>
        <ChevronDown className={`w-4 h-4 text-slate-500 transition-transform duration-200 ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && <div className="p-4 border-t border-slate-700/30">{children}</div>}
    </div>
  )
}

type TabType = 'overview' | 'system' | 'cpu' | 'memory' | 'gpu' | 'storage' | 'network' | 'devices' | 'security' | 'software' | 'processes'

const tabs: { id: TabType; label: string; icon: React.ReactNode }[] = [
  { id: 'overview', label: 'Overview', icon: <Activity className="w-4 h-4" /> },
  { id: 'system', label: 'System', icon: <Settings className="w-4 h-4" /> },
  { id: 'cpu', label: 'CPU', icon: <CpuIcon className="w-4 h-4" /> },
  { id: 'memory', label: 'Memory', icon: <MemoryStick className="w-4 h-4" /> },
  { id: 'gpu', label: 'GPU', icon: <MonitorIcon className="w-4 h-4" /> },
  { id: 'storage', label: 'Storage', icon: <StorageIcon className="w-4 h-4" /> },
  { id: 'network', label: 'Network', icon: <Globe className="w-4 h-4" /> },
  { id: 'devices', label: 'Devices', icon: <Plug className="w-4 h-4" /> },
  { id: 'security', label: 'Security', icon: <Shield className="w-4 h-4" /> },
  { id: 'software', label: 'Software', icon: <Package className="w-4 h-4" /> },
  { id: 'processes', label: 'Processes', icon: <Terminal className="w-4 h-4" /> },
]

export default function App() {
  const [snapshot, setSnapshot] = useState<SystemSnapshot | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<TabType>('overview')

  useEffect(() => {
    async function loadData() {
      try {
        const snap = await fetchApi('/snapshot')
        setSnapshot(snap)
        setLoading(false)
      } catch (err) {
        setError('Failed to connect to server. Run: sysmap server')
        setLoading(false)
      }
    }
    loadData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center animate-pulse">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <p className="text-slate-300">Loading system information...</p>
        </div>
      </div>
    )
  }

  if (error || !snapshot) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center p-8">
          <div className="w-16 h-16 mx-auto rounded-2xl bg-red-500/10 border border-red-500/20 flex items-center justify-center mb-4">
            <span className="text-2xl">⚠️</span>
          </div>
          <p className="text-slate-300 mb-2">{error || 'No data available'}</p>
          <p className="text-slate-500 text-sm">Run: <code className="text-blue-400">sysmap server</code></p>
        </div>
      </div>
    )
  }

  const totalStorage = snapshot.disks.reduce((a, d) => a + d.capacity_bytes, 0)
  const ramUsed = snapshot.memory.total_physical_bytes - snapshot.memory.available_physical_bytes
  const ramPct = snapshot.memory.total_physical_bytes > 0 ? (ramUsed / snapshot.memory.total_physical_bytes) * 100 : 0
  const ramColor = ramPct > 90 ? 'red' : ramPct > 70 ? 'orange' : 'green'

  const renderTab = () => {
    switch (activeTab) {
      case 'overview':
        return (
          <>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
              {[
                { icon: <CpuIcon className="w-5 h-5" />, label: 'CPU', value: snapshot.cpu.name?.split(' ').slice(0, 3).join(' ') || 'N/A', color: 'from-blue-500/20 to-cyan-500/20' },
                { icon: <MemoryStick className="w-5 h-5" />, label: 'RAM', value: formatBytes(snapshot.memory.total_physical_bytes), color: 'from-purple-500/20 to-pink-500/20' },
                { icon: <MonitorIcon className="w-5 h-5" />, label: 'GPU', value: snapshot.gpus[0]?.name?.split(' ').slice(0, 3).join(' ') || 'N/A', color: 'from-emerald-500/20 to-teal-500/20' },
                { icon: <StorageIcon className="w-5 h-5" />, label: 'Storage', value: formatBytes(totalStorage), color: 'from-amber-500/20 to-orange-500/20' },
                { icon: <Settings className="w-5 h-5" />, label: 'OS', value: snapshot.os_info.platform?.split(' ')[0] || 'N/A', color: 'from-indigo-500/20 to-violet-500/20' },
                { icon: <Database className="w-5 h-5" />, label: 'Processes', value: snapshot.total_processes.toString(), color: 'from-rose-500/20 to-red-500/20' },
              ].map((card, i) => (
                <div key={i} className={`card-glow rounded-xl p-4 text-center bg-gradient-to-br ${card.color}`}>
                  <div className="flex justify-center mb-2 text-slate-400">{card.icon}</div>
                  <div className="text-xs text-slate-500 mb-1">{card.label}</div>
                  <div className="text-sm font-semibold text-slate-200 truncate">{card.value}</div>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mt-4">
              <Section title="Memory Usage" icon={<MemoryStick className="w-5 h-5" />}>
                <div className="max-w-md">
                  <ProgressBar value={ramUsed} max={snapshot.memory.total_physical_bytes} color={ramColor} />
                </div>
              </Section>
              {snapshot.battery && (
                <Section title="Battery" icon={<Battery className="w-5 h-5" />}>
                  <div className="max-w-md">
                    <ProgressBar value={snapshot.battery.charge_percent} max={100} color={snapshot.battery.charge_percent > 50 ? 'green' : snapshot.battery.charge_percent > 20 ? 'orange' : 'red'} />
                    <div className="mt-2 text-xs text-slate-400">State: {snapshot.battery.state}</div>
                  </div>
                </Section>
              )}
            </div>
          </>
        )

      case 'system':
        return (
          <Section title="System Information" icon={<Settings className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <InfoCard label="Manufacturer" value={snapshot.system.manufacturer || 'N/A'} />
              <InfoCard label="Model" value={snapshot.system.model || 'N/A'} />
              <InfoCard label="Serial Number" value={snapshot.system.serial || 'N/A'} />
              <InfoCard label="Motherboard" value={snapshot.system.motherboard_model || 'N/A'} />
              <InfoCard label="BIOS Vendor" value={snapshot.system.bios_vendor || 'N/A'} />
              <InfoCard label="BIOS Version" value={snapshot.system.bios_version || 'N/A'} />
              <InfoCard label="BIOS Date" value={snapshot.system.bios_date || 'N/A'} />
              <InfoCard label="UEFI Mode" value={snapshot.system.uefi_mode ? 'Yes' : 'No'} />
              <InfoCard label="Chassis Type" value={snapshot.system.chassis_type || 'N/A'} />
            </div>
          </Section>
        )

      case 'cpu':
        return (
          <Section title="CPU Details" icon={<CpuIcon className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <InfoCard label="Name" value={snapshot.cpu.name || 'N/A'} icon={<CpuIcon className="w-4 h-4" />} />
              <InfoCard label="Manufacturer" value={snapshot.cpu.manufacturer || 'N/A'} />
              <InfoCard label="Physical Cores" value={snapshot.cpu.physical_cores} />
              <InfoCard label="Logical Cores / Threads" value={`${snapshot.cpu.logical_cores} / ${snapshot.cpu.threads}`} />
              <InfoCard label="Base Clock" value={`${(snapshot.cpu.base_clock_mhz / 1000).toFixed(2)} GHz`} />
              <InfoCard label="Boost Clock" value={`${(snapshot.cpu.boost_clock_mhz / 1000).toFixed(2)} GHz`} />
              <InfoCard label="L1 Cache" value={`${snapshot.cpu.l1_cache_kb} KB`} />
              <InfoCard label="L2 Cache" value={`${snapshot.cpu.l2_cache_kb} KB`} />
              <InfoCard label="L3 Cache" value={`${snapshot.cpu.l3_cache_kb} KB`} />
              <InfoCard label="TDP" value={`${snapshot.cpu.tdp_watts.toFixed(0)} W`} />
              <InfoCard label="Virtualization" value={snapshot.cpu.virtualization ? 'Yes' : 'No'} />
              <InfoCard label="Extensions" value={snapshot.cpu.extensions.slice(0, 5).join(', ') || 'N/A'} />
            </div>
          </Section>
        )

      case 'memory':
        return (
          <Section title="Memory Details" icon={<MemoryStick className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <InfoCard label="Total Physical RAM" value={formatBytes(snapshot.memory.total_physical_bytes)} />
              <InfoCard label="Available Physical RAM" value={formatBytes(snapshot.memory.available_physical_bytes)} />
              <InfoCard label="Total Virtual Memory" value={formatBytes(snapshot.memory.total_virtual_bytes)} />
              <InfoCard label="Total Swap" value={formatBytes(snapshot.memory.total_swap_bytes)} />
              <InfoCard label="Memory Type" value={snapshot.memory.memory_type || 'N/A'} />
              <InfoCard label="Memory Speed" value={`${snapshot.memory.memory_speed_mts} MT/s`} />
              <InfoCard label="ECC Supported" value={snapshot.memory.ecc_supported ? 'Yes' : 'No'} />
              <InfoCard label="Memory Slots" value={`${snapshot.memory.slots_used} / ${snapshot.memory.slots_total}`} />
            </div>
            <div className="mt-4 max-w-md">
              <ProgressBar value={ramUsed} max={snapshot.memory.total_physical_bytes} color={ramColor} />
            </div>
          </Section>
        )

      case 'gpu':
        return snapshot.gpus.map((gpu, idx) => (
          <Section key={idx} title={`GPU: ${gpu.name}`} icon={<MonitorIcon className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <InfoCard label="Architecture" value={gpu.architecture || 'N/A'} />
              <InfoCard label="VRAM" value={`${formatBytes(gpu.vram_bytes)} ${gpu.vram_type}`} />
              <InfoCard label="VRAM Speed" value={`${gpu.vram_speed_mts} MT/s`} />
              <InfoCard label="Bus Width" value={`${gpu.vram_bus_width} bit`} />
              <InfoCard label="Driver Version" value={gpu.driver_version || 'N/A'} />
              <InfoCard label="DirectX" value={gpu.directx_version || 'N/A'} />
              <InfoCard label="OpenGL" value={gpu.opengl_version || 'N/A'} />
              <InfoCard label="Vulkan" value={gpu.vulkan_version || 'N/A'} />
              <InfoCard label="CUDA Cores" value={gpu.cuda_cores?.toString() || 'N/A'} />
              <InfoCard label="PCIe Interface" value={`${gpu.pci_interface} ${gpu.pci_generation}`} />
              {gpu.temperature_c > 0 && <InfoCard label="Temperature" value={`${gpu.temperature_c.toFixed(0)} °C`} icon={<Thermometer className="w-4 h-4" />} />}
              {gpu.power_draw_w > 0 && <InfoCard label="Power Draw" value={`${gpu.power_draw_w.toFixed(1)} W`} icon={<Zap className="w-4 h-4" />} />}
            </div>
          </Section>
        ))

      case 'storage':
        return (
          <>
            <Section title="Storage Devices" icon={<StorageIcon className="w-5 h-5" />}>
              {snapshot.disks.length === 0 ? (
                <p className="text-slate-500">No storage devices detected. Try running with sudo.</p>
              ) : (
                <div className="space-y-3">
                  {snapshot.disks.map((disk, idx) => (
                    <div key={idx} className="card-glow rounded-xl p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div>
                          <h4 className="font-semibold text-slate-200">{disk.model || 'Unknown Device'}</h4>
                          <p className="text-xs text-slate-500 font-mono">{disk.name}</p>
                        </div>
                        <Badge color="blue">{formatBytes(disk.capacity_bytes)}</Badge>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                        <div className="bg-slate-900/40 rounded-lg p-2">
                          <div className="text-slate-500 mb-1">Interface</div>
                          <div className="text-slate-300">{disk.interface} {disk.protocol}</div>
                        </div>
                        {disk.temperature_c > 0 && (
                          <div className="bg-slate-900/40 rounded-lg p-2">
                            <div className="text-slate-500 mb-1">Temperature</div>
                            <div className="text-slate-300">{disk.temperature_c.toFixed(0)} °C</div>
                          </div>
                        )}
                        {disk.health_status && (
                          <div className="bg-slate-900/40 rounded-lg p-2">
                            <div className="text-slate-500 mb-1">SMART</div>
                            <Badge color={disk.health_status.toUpperCase().includes('PASS') ? 'green' : 'orange'}>{disk.health_status}</Badge>
                          </div>
                        )}
                        {disk.power_on_hours > 0 && (
                          <div className="bg-slate-900/40 rounded-lg p-2">
                            <div className="text-slate-500 mb-1">Power-On Hours</div>
                            <div className="text-slate-300">{disk.power_on_hours}</div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </Section>
            <Section title="Partitions & Filesystems" icon={<Layers className="w-5 h-5" />}>
              {snapshot.partitions.length === 0 ? (
                <p className="text-slate-500">No partitions detected.</p>
              ) : (
                <div className="overflow-x-auto rounded-xl border border-slate-700/30">
                  <table className="w-full text-sm">
                    <thead>
                      <tr>
                        <th className="table-header">Device</th>
                        <th className="table-header">Mount Point</th>
                        <th className="table-header">Filesystem</th>
                        <th className="table-header">Total</th>
                        <th className="table-header">Used</th>
                        <th className="table-header">Free</th>
                        <th className="table-header">Usage</th>
                      </tr>
                    </thead>
                    <tbody>
                      {snapshot.partitions.map((part, idx) => (
                        <tr key={idx} className="table-row">
                          <td className="table-cell font-mono text-xs">{part.name}</td>
                          <td className="table-cell">{part.mount_point || 'N/A'}</td>
                          <td className="table-cell"><Badge color="purple">{part.filesystem}</Badge></td>
                          <td className="table-cell">{formatBytes(part.size_bytes)}</td>
                          <td className="table-cell">{formatBytes(part.used_bytes)}</td>
                          <td className="table-cell">{formatBytes(part.free_bytes)}</td>
                          <td className="table-cell w-40">
                            <ProgressBar value={part.used_bytes} max={part.size_bytes} color={part.usage_percent > 90 ? 'red' : part.usage_percent > 70 ? 'orange' : 'green'} />
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </Section>
          </>
        )

      case 'network':
        return (
          <Section title="Network Adapters" icon={<Globe className="w-5 h-5" />}>
            <div className="space-y-3">
              {snapshot.network_adapters.map((adapter, idx) => (
                <div key={idx} className="card-glow rounded-xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-slate-200">{adapter.name}</h4>
                    <Badge color={adapter.connection_state === 'UP' ? 'green' : 'red'}>{adapter.adapter_type}</Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                    <div className="bg-slate-900/40 rounded-lg p-2">
                      <div className="text-slate-500 mb-1">MAC</div>
                      <div className="text-slate-300 font-mono">{adapter.mac_address || 'N/A'}</div>
                    </div>
                    <div className="bg-slate-900/40 rounded-lg p-2">
                      <div className="text-slate-500 mb-1">IPv4</div>
                      <div className="text-slate-300 font-mono">{adapter.ipv4_address || 'N/A'}</div>
                    </div>
                    {adapter.speed_mbps > 0 && (
                      <div className="bg-slate-900/40 rounded-lg p-2">
                        <div className="text-slate-500 mb-1">Speed</div>
                        <div className="text-slate-300">{adapter.speed_mbps} Mbps</div>
                      </div>
                    )}
                    <div className="bg-slate-900/40 rounded-lg p-2">
                      <div className="text-slate-500 mb-1">State</div>
                      <Badge color={adapter.connection_state === 'UP' ? 'green' : 'red'}>{adapter.connection_state}</Badge>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Section>
        )

      case 'devices':
        return (
          <>
            {snapshot.sensors.length > 0 && (
              <Section title="Sensors" icon={<Thermometer className="w-5 h-5" />}>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {snapshot.sensors.map((sensor, idx) => (
                    <InfoCard key={idx} label={sensor.name} value={`${sensor.value.toFixed(1)} ${sensor.unit}`} icon={<Thermometer className="w-4 h-4" />} />
                  ))}
                </div>
              </Section>
            )}
            {snapshot.usb_devices.length > 0 && (
              <Section title="USB Devices" icon={<UsbIcon className="w-5 h-5" />}>
                <div className="overflow-x-auto rounded-xl border border-slate-700/30">
                  <table className="w-full text-sm">
                    <thead>
                      <tr>
                        <th className="table-header">Device</th>
                        <th className="table-header">Vendor ID</th>
                        <th className="table-header">Product ID</th>
                        <th className="table-header">Speed</th>
                        <th className="table-header">Class</th>
                      </tr>
                    </thead>
                    <tbody>
                      {snapshot.usb_devices.map((dev, idx) => (
                        <tr key={idx} className="table-row">
                          <td className="table-cell">{dev.name || dev.product_name || 'USB Device'}</td>
                          <td className="table-cell font-mono text-xs">{dev.vendor_id}</td>
                          <td className="table-cell font-mono text-xs">{dev.product_id}</td>
                          <td className="table-cell">{dev.speed}</td>
                          <td className="table-cell"><Badge color="blue">{dev.class_name}</Badge></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Section>
            )}
            {snapshot.wireless.length > 0 && (
              <Section title="Wireless" icon={<Wifi className="w-5 h-5" />}>
                {snapshot.wireless.map((w, idx) => (
                  <div key={idx} className="card-glow rounded-xl p-4">
                    <h4 className="font-semibold text-slate-200 mb-2">{w.adapter_name}</h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                      <div className="bg-slate-900/40 rounded-lg p-2">
                        <div className="text-slate-500 mb-1">SSID</div>
                        <div className="text-slate-300">{w.current_ssid || 'Not Connected'}</div>
                      </div>
                      {w.current_bssid && (
                        <div className="bg-slate-900/40 rounded-lg p-2">
                          <div className="text-slate-500 mb-1">BSSID</div>
                          <div className="text-slate-300 font-mono">{w.current_bssid}</div>
                        </div>
                      )}
                      {w.rssi_dbm !== 0 && (
                        <div className="bg-slate-900/40 rounded-lg p-2">
                          <div className="text-slate-500 mb-1">Signal</div>
                          <div className="text-slate-300">{w.rssi_dbm} dBm</div>
                        </div>
                      )}
                      {w.security_type && (
                        <div className="bg-slate-900/40 rounded-lg p-2">
                          <div className="text-slate-500 mb-1">Security</div>
                          <div className="text-slate-300">{w.security_type}</div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </Section>
            )}
            {snapshot.battery && (
              <Section title="Battery" icon={<Battery className="w-5 h-5" />}>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  <div className="card-glow rounded-xl p-4">
                    <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">State</div>
                    <Badge color={snapshot.battery.state.includes('full') ? 'green' : snapshot.battery.state.includes('charging') ? 'blue' : 'orange'}>
                      {snapshot.battery.state}
                    </Badge>
                  </div>
                  <InfoCard label="Charge" value={`${snapshot.battery.charge_percent.toFixed(0)}%`} />
                  <InfoCard label="Design Capacity" value={`${snapshot.battery.design_capacity_wh.toFixed(1)} Wh`} />
                  <InfoCard label="Full Capacity" value={`${snapshot.battery.full_capacity_wh.toFixed(1)} Wh`} />
                  <InfoCard label="Health" value={`${snapshot.battery.health_percent.toFixed(0)}%`} />
                  <InfoCard label="Cycle Count" value={snapshot.battery.cycle_count} />
                </div>
                <div className="mt-4 max-w-md">
                  <ProgressBar value={snapshot.battery.charge_percent} max={100} color={snapshot.battery.charge_percent > 50 ? 'green' : snapshot.battery.charge_percent > 20 ? 'orange' : 'red'} />
                </div>
              </Section>
            )}
          </>
        )

      case 'security':
        return (
          <Section title="Security" icon={<Shield className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <div className="card-glow rounded-xl p-4">
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">TPM</div>
                {snapshot.security.tpm_present ? <Badge color="green">{snapshot.security.tpm_version}</Badge> : <Badge color="red">Not Found</Badge>}
              </div>
              <div className="card-glow rounded-xl p-4">
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Secure Boot</div>
                {snapshot.security.secure_boot ? <Badge color={snapshot.security.secure_boot.includes('Enabled') ? 'green' : 'red'}>{snapshot.security.secure_boot}</Badge> : <Badge color="orange">Unknown</Badge>}
              </div>
              <div className="card-glow rounded-xl p-4">
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Firewall</div>
                <Badge color={snapshot.security.firewall_enabled ? 'green' : 'red'}>{snapshot.security.firewall_enabled ? 'Enabled' : 'Disabled'}</Badge>
              </div>
              <InfoCard label="Antivirus" value={snapshot.security.antivirus_name || 'None'} />
              <InfoCard label="BitLocker" value={snapshot.security.bitlocker_status || 'N/A'} />
              <InfoCard label="VBS" value={snapshot.security.virtualization_based_security ? 'Enabled' : 'Disabled'} />
            </div>
          </Section>
        )

      case 'software':
        return (
          <>
            <Section title="OS Information" icon={<Settings className="w-5 h-5" />}>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                <InfoCard label="Hostname" value={snapshot.os_info.hostname} />
                <InfoCard label="Platform" value={snapshot.os_info.platform} />
                <InfoCard label="Kernel" value={snapshot.os_info.kernel_version} />
                <InfoCard label="Architecture" value={snapshot.os_info.architecture} />
                <InfoCard label="Language" value={snapshot.os_info.language || 'N/A'} />
                <InfoCard label="Locale" value={snapshot.os_info.locale || 'N/A'} />
                <InfoCard label="Timezone" value={snapshot.os_info.timezone} />
              </div>
            </Section>
            <Section title="Virtualization & Containers" icon={<Server className="w-5 h-5" />}>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                <div className="card-glow rounded-xl p-4">
                  <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Docker</div>
                  {snapshot.virtualization.docker_installed ? <Badge color="green">{snapshot.virtualization.docker_version}</Badge> : <Badge color="red">Not Installed</Badge>}
                </div>
                <div className="card-glow rounded-xl p-4">
                  <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Kubernetes</div>
                  {snapshot.virtualization.kubernetes_installed ? <Badge color="green">{snapshot.virtualization.kubernetes_version}</Badge> : <Badge color="red">Not Installed</Badge>}
                </div>
                <div className="card-glow rounded-xl p-4">
                  <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">WSL</div>
                  {snapshot.virtualization.wsl_installed ? <Badge color="green">{snapshot.virtualization.wsl_distributions.join(', ')}</Badge> : <Badge color="red">Not Installed</Badge>}
                </div>
                <InfoCard label="Hyper-V" value={snapshot.virtualization.hyper_v_enabled ? 'Enabled' : 'Disabled'} />
                <InfoCard label="VM Detected" value={snapshot.virtualization.vm_host || 'No'} />
                <InfoCard label="Nested Virtualization" value={snapshot.virtualization.nested_virtualization ? 'Yes' : 'No'} />
              </div>
            </Section>
            {snapshot.installed_software.length > 0 && (
              <Section title={`Installed Software (${snapshot.installed_software.length})`} icon={<Package className="w-5 h-5" />}>
                <div className="overflow-x-auto rounded-xl border border-slate-700/30">
                  <table className="w-full text-sm">
                    <thead>
                      <tr>
                        <th className="table-header">Name</th>
                        <th className="table-header">Version</th>
                        <th className="table-header">Publisher</th>
                      </tr>
                    </thead>
                    <tbody>
                      {snapshot.installed_software.map((sw, idx) => (
                        <tr key={idx} className="table-row">
                          <td className="table-cell">{sw.name}</td>
                          <td className="table-cell font-mono text-xs">{sw.version}</td>
                          <td className="table-cell">{sw.publisher}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </Section>
            )}
          </>
        )

      case 'processes':
        return (
          <Section title={`Top Processes (${snapshot.total_processes} total)`} icon={<Terminal className="w-5 h-5" />}>
            <div className="overflow-x-auto rounded-xl border border-slate-700/30">
              <table className="w-full text-sm">
                <thead>
                  <tr>
                    <th className="table-header">PID</th>
                    <th className="table-header">Name</th>
                    <th className="table-header">User</th>
                    <th className="table-header">CPU %</th>
                    <th className="table-header">Memory</th>
                    <th className="table-header">Status</th>
                  </tr>
                </thead>
                <tbody>
                  {snapshot.processes.map((proc, idx) => (
                    <tr key={idx} className="table-row">
                      <td className="table-cell font-mono text-xs">{proc.pid}</td>
                      <td className="table-cell">{proc.name}</td>
                      <td className="table-cell">{proc.user}</td>
                      <td className="table-cell">{proc.cpu_percent.toFixed(1)}%</td>
                      <td className="table-cell">{formatBytes(proc.memory_bytes)}</td>
                      <td className="table-cell"><Badge color={proc.status === 'running' ? 'green' : 'orange'}>{proc.status}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        )

      default:
        return null
    }
  }

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-56 bg-slate-900/90 backdrop-blur-xl border-r border-slate-700/50 fixed top-0 left-0 h-full overflow-y-auto z-40">
        <div className="p-4 border-b border-slate-700/50">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
              <Activity className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="text-sm font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">SysMap</h1>
              <p className="text-xs text-slate-500">System Profiler</p>
            </div>
          </div>
        </div>
        <nav className="p-2 space-y-1">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
              }`}
            >
              {tab.icon}
              <span>{tab.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main content */}
      <main className="ml-56 flex-1 min-h-screen">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-slate-900/80 backdrop-blur-xl border-b border-slate-700/50">
          <div className="px-6 py-3 flex items-center justify-between">
            <div className="flex items-center gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                Live
              </span>
              <span>•</span>
              <span>{snapshot.os_info.hostname}</span>
              <span>•</span>
              <span>{snapshot.platform}</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="text-xs text-slate-500">
                {new Date(snapshot.timestamp).toLocaleString()}
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => window.open('/api/export/pdf', '_blank')}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-red-500/10 border border-red-500/20 text-red-400 rounded-lg text-xs font-medium hover:bg-red-500/20 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  PDF
                </button>
                <button
                  onClick={() => window.open('/api/export/md', '_blank')}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-blue-500/10 border border-blue-500/20 text-blue-400 rounded-lg text-xs font-medium hover:bg-blue-500/20 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  Markdown
                </button>
                <button
                  onClick={() => window.open('/api/export/json', '_blank')}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-purple-500/10 border border-purple-500/20 text-purple-400 rounded-lg text-xs font-medium hover:bg-purple-500/20 transition-colors"
                >
                  <Download className="w-3.5 h-3.5" />
                  JSON
                </button>
              </div>
            </div>
          </div>
        </header>

        {/* Tab content */}
        <div className="p-6 space-y-4">
          {renderTab()}
        </div>
      </main>
    </div>
  )
}
