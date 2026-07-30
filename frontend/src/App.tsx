import React, { useState, useEffect } from 'react'
import {
  Cpu, MemoryStick, Monitor, HardDrive, Wifi, Usb,
  Thermometer, Battery, Shield, Database, Settings,
  Globe, Info, ChevronDown, ChevronRight, Download,
  Activity, Zap, Fan, Bluetooth, AudioLines, Layers
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
    console.error(`Failed to fetch ${endpoint}:`, err)
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

function formatPercent(pct: number): string {
  return `${pct.toFixed(1)}%`
}

function Badge({ children, color }: { children: React.ReactNode; color: string }) {
  const colorMap: Record<string, string> = {
    green: 'bg-emerald-900/50 text-emerald-400 border border-emerald-800',
    blue: 'bg-blue-900/50 text-blue-400 border border-blue-800',
    purple: 'bg-purple-900/50 text-purple-400 border border-purple-800',
    orange: 'bg-amber-900/50 text-amber-400 border border-amber-800',
    red: 'bg-red-900/50 text-red-400 border border-red-800',
  }
  return (
    <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${colorMap[color] || colorMap.blue}`}>
      {children}
    </span>
  )
}

function InfoCard({ label, value, icon }: { label: string; value: string | number; icon?: React.ReactNode }) {
  return (
    <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4 hover:border-slate-600/50 transition-colors">
      <div className="text-xs text-slate-500 uppercase tracking-wider mb-1 flex items-center gap-2">
        {icon}
        {label}
      </div>
      <div className="text-sm font-medium text-slate-200 break-all">{value}</div>
    </div>
  )
}

function ProgressBar({ value, max = 100, color = 'blue' }: { value: number; max?: number; color?: string }) {
  const pct = Math.min((value / max) * 100, 100)
  const colorMap: Record<string, string> = {
    green: 'bg-emerald-500',
    blue: 'bg-blue-500',
    orange: 'bg-amber-500',
    red: 'bg-red-500',
  }
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs text-slate-400 mb-1">
        <span>{formatPercent(pct)}</span>
        <span>{formatBytes(value)} / {formatBytes(max)}</span>
      </div>
      <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${colorMap[color] || colorMap.blue}`}
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

function Section({ title, icon, children }: { title: string; icon: React.ReactNode; children: React.ReactNode }) {
  const [open, setOpen] = useState(true)
  return (
    <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl overflow-hidden">
      <button
        onClick={() => setOpen(!open)}
        className="w-full flex items-center justify-between p-4 hover:bg-slate-700/30 transition-colors"
      >
        <div className="flex items-center gap-3">
          <span className="text-blue-400">{icon}</span>
          <h2 className="text-lg font-semibold text-slate-100">{title}</h2>
        </div>
        {open ? <ChevronDown className="w-5 h-5 text-slate-400" /> : <ChevronRight className="w-5 h-5 text-slate-400" />}
      </button>
      {open && <div className="p-4 border-t border-slate-700/50">{children}</div>}
    </div>
  )
}

export default function App() {
  const [snapshot, setSnapshot] = useState<SystemSnapshot | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [summary, setSummary] = useState<any>(null)

  useEffect(() => {
    async function loadData() {
      try {
        const [snap, sum] = await Promise.all([
          fetchApi('/snapshot'),
          fetchApi('/summary'),
        ])
        setSnapshot(snap)
        setSummary(sum)
        setLoading(false)
      } catch (err) {
        setError('Failed to connect to server. Make sure the server is running.')
        setLoading(false)
      }
    }
    loadData()
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4" />
          <p className="text-slate-400">Loading system information...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center p-8">
          <div className="text-red-400 text-xl mb-4">⚠️</div>
          <p className="text-slate-300 mb-4">{error}</p>
          <p className="text-slate-500 text-sm">Make sure to run: sysmap server</p>
        </div>
      </div>
    )
  }

  if (!snapshot) return null

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100">
      {/* Header */}
      <header className="bg-slate-800/80 backdrop-blur-sm border-b border-slate-700/50 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">
                  SysMap
                </h1>
                <p className="text-xs text-slate-500">System Profiler</p>
              </div>
            </div>
            <div className="flex items-center gap-4 text-xs text-slate-500">
              <span>{snapshot.os_info.hostname}</span>
              <span>•</span>
              <span>{snapshot.platform}</span>
              <span>•</span>
              <span>{new Date(snapshot.timestamp).toLocaleString()}</span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6 space-y-6">
        {/* Summary Cards */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center">
            <Cpu className="w-6 h-6 text-blue-400 mx-auto mb-2" />
            <div className="text-xs text-slate-500 mb-1">CPU</div>
            <div className="text-sm font-medium text-slate-200 truncate">{snapshot.cpu.name?.split(' ').slice(0, 3).join(' ') || 'N/A'}</div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center">
            <MemoryStick className="w-6 h-6 text-purple-400 mx-auto mb-2" />
            <div className="text-xs text-slate-500 mb-1">RAM</div>
            <div className="text-sm font-medium text-slate-200">{formatBytes(snapshot.memory.total_physical_bytes)}</div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center">
            <Monitor className="w-6 h-6 text-green-400 mx-auto mb-2" />
            <div className="text-xs text-slate-500 mb-1">GPU</div>
            <div className="text-sm font-medium text-slate-200 truncate">{snapshot.gpus[0]?.name?.split(' ').slice(0, 3).join(' ') || 'N/A'}</div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center">
            <HardDrive className="w-6 h-6 text-amber-400 mx-auto mb-2" />
            <div className="text-xs text-slate-500 mb-1">Storage</div>
            <div className="text-sm font-medium text-slate-200">
              {formatBytes(snapshot.disks.reduce((a, d) => a + d.capacity_bytes, 0))}
            </div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center">
            <Shield className="w-6 h-6 text-emerald-400 mx-auto mb-2" />
            <div className="text-xs text-slate-500 mb-1">OS</div>
            <div className="text-sm font-medium text-slate-200 truncate">{snapshot.os_info.platform?.split(' ')[0] || 'N/A'}</div>
          </div>
          <div className="bg-slate-800/50 border border-slate-700/50 rounded-xl p-4 text-center">
            <Database className="w-6 h-6 text-cyan-400 mx-auto mb-2" />
            <div className="text-xs text-slate-500 mb-1">Processes</div>
            <div className="text-sm font-medium text-slate-200">{snapshot.total_processes}</div>
          </div>
        </div>

        {/* System Info */}
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

        {/* CPU Info */}
        <Section title="CPU" icon={<Cpu className="w-5 h-5" />}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <InfoCard label="Name" value={snapshot.cpu.name || 'N/A'} icon={<Cpu className="w-4 h-4" />} />
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
            <InfoCard label="Instruction Extensions" value={snapshot.cpu.extensions.slice(0, 5).join(', ') || 'N/A'} />
          </div>
        </Section>

        {/* Memory */}
        <Section title="Memory" icon={<MemoryStick className="w-5 h-5" />}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <InfoCard label="Total Physical RAM" value={formatBytes(snapshot.memory.total_physical_bytes)} />
            <InfoCard label="Available Physical RAM" value={formatBytes(snapshot.memory.available_physical_bytes)} />
            <InfoCard label="Total Virtual Memory" value={formatBytes(snapshot.memory.total_virtual_bytes)} />
            <InfoCard label="Total Swap" value={formatBytes(snapshot.memory.total_swap_bytes)} />
            <InfoCard label="Memory Type" value={snapshot.memory.memory_type || 'N/A'} />
            <InfoCard label="Memory Speed" value={`${snapshot.memory.memory_speed_mts} MT/s`} />
            <InfoCard label="ECC Supported" value={snapshot.memory.ecc_supported ? 'Yes' : 'No'} />
            <InfoCard label="Memory Slots" value={`${snapshot.memory.slots_used} / ${snapshot.memory.slots_total}`} />
          </div>
          {snapshot.memory.total_physical_bytes > 0 && (
            <div className="mt-4">
              <ProgressBar
                value={snapshot.memory.total_physical_bytes - snapshot.memory.available_physical_bytes}
                max={snapshot.memory.total_physical_bytes}
                color={
                  (snapshot.memory.total_physical_bytes - snapshot.memory.available_physical_bytes) / snapshot.memory.total_physical_bytes > 0.9
                    ? 'red'
                    : (snapshot.memory.total_physical_bytes - snapshot.memory.available_physical_bytes) / snapshot.memory.total_physical_bytes > 0.7
                    ? 'orange'
                    : 'green'
                }
              />
            </div>
          )}
        </Section>

        {/* GPU Info */}
        {snapshot.gpus.map((gpu, idx) => (
          <Section key={idx} title={`GPU: ${gpu.name}`} icon={<Monitor className="w-5 h-5" />}>
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
        ))}

        {/* Storage */}
        <Section title="Storage" icon={<HardDrive className="w-5 h-5" />}>
          {snapshot.disks.length === 0 ? (
            <p className="text-slate-500">No storage devices detected</p>
          ) : (
            <div className="space-y-4">
              {snapshot.disks.map((disk, idx) => (
                <div key={idx} className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-3">
                    <div>
                      <h4 className="font-medium text-slate-200">{disk.model || 'Unknown Device'}</h4>
                      <p className="text-xs text-slate-500">{disk.name}</p>
                    </div>
                    <Badge color="blue">{formatBytes(disk.capacity_bytes)}</Badge>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                    <div>
                      <span className="text-slate-500">Interface:</span>{' '}
                      <span className="text-slate-300">{disk.interface} {disk.protocol}</span>
                    </div>
                    {disk.temperature_c > 0 && (
                      <div>
                        <span className="text-slate-500">Temperature:</span>{' '}
                        <span className="text-slate-300">{disk.temperature_c.toFixed(0)} °C</span>
                      </div>
                    )}
                    {disk.health_status && (
                      <div>
                        <span className="text-slate-500">SMART:</span>{' '}
                        <Badge color={disk.health_status.toUpperCase().includes('PASS') ? 'green' : 'orange'}>
                          {disk.health_status}
                        </Badge>
                      </div>
                    )}
                    {disk.power_on_hours > 0 && (
                      <div>
                        <span className="text-slate-500">Power-On Hours:</span>{' '}
                        <span className="text-slate-300">{disk.power_on_hours}</span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </Section>

        {/* Partitions */}
        <Section title="Partitions & Filesystems" icon={<Layers className="w-5 h-5" />}>
          {snapshot.partitions.length === 0 ? (
            <p className="text-slate-500">No partitions detected</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Device</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Mount Point</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Filesystem</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Total</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Used</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Free</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Usage</th>
                  </tr>
                </thead>
                <tbody>
                  {snapshot.partitions.map((part, idx) => (
                    <tr key={idx} className="border-b border-slate-800 hover:bg-slate-800/30">
                      <td className="py-3 px-4 font-mono text-xs">{part.name}</td>
                      <td className="py-3 px-4">{part.mount_point || 'N/A'}</td>
                      <td className="py-3 px-4"><Badge color="purple">{part.filesystem}</Badge></td>
                      <td className="py-3 px-4">{formatBytes(part.size_bytes)}</td>
                      <td className="py-3 px-4">{formatBytes(part.used_bytes)}</td>
                      <td className="py-3 px-4">{formatBytes(part.free_bytes)}</td>
                      <td className="py-3 px-4 w-32">
                        <ProgressBar
                          value={part.used_bytes}
                          max={part.size_bytes}
                          color={part.usage_percent > 90 ? 'red' : part.usage_percent > 70 ? 'orange' : 'green'}
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </Section>

        {/* Network */}
        <Section title="Network Adapters" icon={<Globe className="w-5 h-5" />}>
          <div className="space-y-3">
            {snapshot.network_adapters.map((adapter, idx) => (
              <div key={idx} className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-medium text-slate-200">{adapter.name}</h4>
                  <Badge color={adapter.connection_state === 'UP' ? 'green' : 'red'}>{adapter.adapter_type}</Badge>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                  <div>
                    <span className="text-slate-500">MAC:</span>{' '}
                    <span className="text-slate-300 font-mono">{adapter.mac_address || 'N/A'}</span>
                  </div>
                  <div>
                    <span className="text-slate-500">IPv4:</span>{' '}
                    <span className="text-slate-300 font-mono">{adapter.ipv4_address || 'N/A'}</span>
                  </div>
                  {adapter.speed_mbps > 0 && (
                    <div>
                      <span className="text-slate-500">Speed:</span>{' '}
                      <span className="text-slate-300">{adapter.speed_mbps} Mbps</span>
                    </div>
                  )}
                  <div>
                    <span className="text-slate-500">State:</span>{' '}
                    <Badge color={adapter.connection_state === 'UP' ? 'green' : 'red'}>{adapter.connection_state}</Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Section>

        {/* Sensors */}
        <Section title="Sensors" icon={<Thermometer className="w-5 h-5" />}>
          {snapshot.sensors.length === 0 ? (
            <p className="text-slate-500">No sensor data available</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {snapshot.sensors.map((sensor, idx) => (
                <InfoCard
                  key={idx}
                  label={sensor.name}
                  value={`${sensor.value.toFixed(1)} ${sensor.unit}`}
                  icon={<Thermometer className="w-4 h-4" />}
                />
              ))}
            </div>
          )}
        </Section>

        {/* OS Info */}
        <Section title="Operating System" icon={<Settings className="w-5 h-5" />}>
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

        {/* Security */}
        <Section title="Security" icon={<Shield className="w-5 h-5" />}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">TPM</div>
              {snapshot.security.tpm_present ? (
                <Badge color="green">{snapshot.security.tpm_version}</Badge>
              ) : (
                <Badge color="red">Not Found</Badge>
              )}
            </div>
            <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Secure Boot</div>
              {snapshot.security.secure_boot ? (
                <Badge color={snapshot.security.secure_boot.includes('Enabled') ? 'green' : 'red'}>
                  {snapshot.security.secure_boot}
                </Badge>
              ) : (
                <Badge color="orange">Unknown</Badge>
              )}
            </div>
            <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Firewall</div>
              <Badge color={snapshot.security.firewall_enabled ? 'green' : 'red'}>
                {snapshot.security.firewall_enabled ? 'Enabled' : 'Disabled'}
              </Badge>
            </div>
            <InfoCard label="Antivirus" value={snapshot.security.antivirus_name || 'None'} />
            <InfoCard label="BitLocker" value={snapshot.security.bitlocker_status || 'N/A'} />
            <InfoCard label="VBS" value={snapshot.security.virtualization_based_security ? 'Enabled' : 'Disabled'} />
          </div>
        </Section>

        {/* Virtualization */}
        <Section title="Virtualization & Containers" icon={<Database className="w-5 h-5" />}>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Docker</div>
              {snapshot.virtualization.docker_installed ? (
                <Badge color="green">{snapshot.virtualization.docker_version}</Badge>
              ) : (
                <Badge color="red">Not Installed</Badge>
              )}
            </div>
            <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">Kubernetes</div>
              {snapshot.virtualization.kubernetes_installed ? (
                <Badge color="green">{snapshot.virtualization.kubernetes_version}</Badge>
              ) : (
                <Badge color="red">Not Installed</Badge>
              )}
            </div>
            <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
              <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">WSL</div>
              {snapshot.virtualization.wsl_installed ? (
                <Badge color="green">{snapshot.virtualization.wsl_distributions.join(', ')}</Badge>
              ) : (
                <Badge color="red">Not Installed</Badge>
              )}
            </div>
            <InfoCard label="Hyper-V" value={snapshot.virtualization.hyper_v_enabled ? 'Enabled' : 'Disabled'} />
            <InfoCard label="VM Detected" value={snapshot.virtualization.vm_host || 'No'} />
            <InfoCard label="Nested Virtualization" value={snapshot.virtualization.nested_virtualization ? 'Yes' : 'No'} />
          </div>
        </Section>

        {/* Battery */}
        {snapshot.battery && (
          <Section title="Battery" icon={<Battery className="w-5 h-5" />}>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              <div className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
                <div className="text-xs text-slate-500 uppercase tracking-wider mb-2">State</div>
                <Badge color={
                  snapshot.battery.state.includes('full') ? 'green' :
                  snapshot.battery.state.includes('charging') ? 'blue' : 'orange'
                }>
                  {snapshot.battery.state}
                </Badge>
              </div>
              <InfoCard label="Charge" value={`${snapshot.battery.charge_percent.toFixed(0)}%`} />
              <InfoCard label="Design Capacity" value={`${snapshot.battery.design_capacity_wh.toFixed(1)} Wh`} />
              <InfoCard label="Full Capacity" value={`${snapshot.battery.full_capacity_wh.toFixed(1)} Wh`} />
              <InfoCard label="Health" value={`${snapshot.battery.health_percent.toFixed(0)}%`} />
              <InfoCard label="Cycle Count" value={snapshot.battery.cycle_count} />
              <InfoCard label="Voltage" value={`${snapshot.battery.voltage.toFixed(2)} V`} />
              <InfoCard label="Temperature" value={`${snapshot.battery.temperature_c.toFixed(0)} °C`} />
            </div>
            <div className="mt-4">
              <ProgressBar
                value={snapshot.battery.charge_percent}
                max={100}
                color={
                  snapshot.battery.charge_percent > 50 ? 'green' :
                  snapshot.battery.charge_percent > 20 ? 'orange' : 'red'
                }
              />
            </div>
          </Section>
        )}

        {/* Wireless */}
        {snapshot.wireless.length > 0 && (
          <Section title="Wireless" icon={<Wifi className="w-5 h-5" />}>
            {snapshot.wireless.map((w, idx) => (
              <div key={idx} className="bg-slate-900/50 border border-slate-700/50 rounded-lg p-4">
                <h4 className="font-medium text-slate-200 mb-2">{w.adapter_name}</h4>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
                  <div>
                    <span className="text-slate-500">SSID:</span>{' '}
                    <span className="text-slate-300">{w.current_ssid || 'Not Connected'}</span>
                  </div>
                  {w.current_bssid && (
                    <div>
                      <span className="text-slate-500">BSSID:</span>{' '}
                      <span className="text-slate-300 font-mono">{w.current_bssid}</span>
                    </div>
                  )}
                  {w.rssi_dbm !== 0 && (
                    <div>
                      <span className="text-slate-500">Signal:</span>{' '}
                      <span className="text-slate-300">{w.rssi_dbm} dBm</span>
                    </div>
                  )}
                  {w.security_type && (
                    <div>
                      <span className="text-slate-500">Security:</span>{' '}
                      <span className="text-slate-300">{w.security_type}</span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </Section>
        )}

        {/* USB Devices */}
        {snapshot.usb_devices.length > 0 && (
          <Section title="USB Devices" icon={<Usb className="w-5 h-5" />}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Device</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Vendor ID</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Product ID</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Speed</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Class</th>
                  </tr>
                </thead>
                <tbody>
                  {snapshot.usb_devices.map((dev, idx) => (
                    <tr key={idx} className="border-b border-slate-800 hover:bg-slate-800/30">
                      <td className="py-3 px-4">{dev.name || dev.product_name || 'USB Device'}</td>
                      <td className="py-3 px-4 font-mono text-xs">{dev.vendor_id}</td>
                      <td className="py-3 px-4 font-mono text-xs">{dev.product_id}</td>
                      <td className="py-3 px-4">{dev.speed}</td>
                      <td className="py-3 px-4"><Badge color="blue">{dev.class_name}</Badge></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        )}

        {/* Processes */}
        <Section title={`Top Processes (${snapshot.total_processes} total)`} icon={<Database className="w-5 h-5" />}>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">PID</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Name</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">User</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">CPU %</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Memory</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Status</th>
                </tr>
              </thead>
              <tbody>
                {snapshot.processes.map((proc, idx) => (
                  <tr key={idx} className="border-b border-slate-800 hover:bg-slate-800/30">
                    <td className="py-3 px-4 font-mono text-xs">{proc.pid}</td>
                    <td className="py-3 px-4">{proc.name}</td>
                    <td className="py-3 px-4">{proc.user}</td>
                    <td className="py-3 px-4">{proc.cpu_percent.toFixed(1)}%</td>
                    <td className="py-3 px-4">{formatBytes(proc.memory_bytes)}</td>
                    <td className="py-3 px-4"><Badge color={proc.status === 'running' ? 'green' : 'orange'}>{proc.status}</Badge></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Section>

        {/* Software */}
        {snapshot.installed_software.length > 0 && (
          <Section title={`Installed Software (${snapshot.installed_software.length})`} icon={<Download className="w-5 h-5" />}>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Name</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Version</th>
                    <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase">Publisher</th>
                  </tr>
                </thead>
                <tbody>
                  {snapshot.installed_software.map((sw, idx) => (
                    <tr key={idx} className="border-b border-slate-800 hover:bg-slate-800/30">
                      <td className="py-3 px-4">{sw.name}</td>
                      <td className="py-3 px-4 font-mono text-xs">{sw.version}</td>
                      <td className="py-3 px-4">{sw.publisher}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Section>
        )}

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800 mt-8 py-6 text-center text-xs text-slate-600">
        <p>SysMap System Profiler - {snapshot.timestamp}</p>
        <p className="mt-1">{snapshot.platform} | {snapshot.os_info.hostname}</p>
      </footer>
    </div>
  )
}
