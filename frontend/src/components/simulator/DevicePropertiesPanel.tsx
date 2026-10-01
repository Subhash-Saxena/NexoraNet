import React, { useState } from 'react'
import {
  Sliders,
  Network,
  Trash2,
  Plus,
  Server,
  Info,
} from 'lucide-react'
import type { SimDevice, TopologyLink } from '../../types/simulator'

interface DevicePropertiesPanelProps {
  device: SimDevice | null
  allDevices: SimDevice[]
  links: TopologyLink[]
  onUpdateDevice: (updated: SimDevice) => void
  onDeleteDevice: (deviceId: string) => void
}

type TabType = 'general' | 'interfaces' | 'routing' | 'firewall' | 'services'

export const DevicePropertiesPanel: React.FC<DevicePropertiesPanelProps> = ({
  device,
  allDevices = [],
  links = [],
  onUpdateDevice,
  onDeleteDevice,
}) => {
  const [activeTab, setActiveTab] = useState<TabType>('general')

  // If no device is selected, show Network Overview
  if (!device) {
    const routers = allDevices.filter((d) => d.type === 'ROUTER').length
    const switches = allDevices.filter((d) => d.type === 'SWITCH').length
    const hosts = allDevices.filter((d) => ['PC', 'LAPTOP', 'SERVER'].includes(d.type)).length
    const firewalls = allDevices.filter((d) => d.type === 'FIREWALL').length

    return (
      <aside className="simulator-properties" aria-label="Network Overview">
        <div className="prop-header">
          <span className="prop-title">
            <Info size={16} /> Network Overview
          </span>
        </div>
        <div className="prop-body">
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '1rem' }}>
            Select a device on the canvas to inspect or modify its network interfaces,
            routing tables, and firewall policies.
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(2, 1fr)',
              gap: '0.5rem',
              marginBottom: '1rem',
            }}
          >
            <div style={{ background: '#1e293b', padding: '0.6rem', borderRadius: '0.375rem' }}>
              <div style={{ fontSize: '0.7rem', color: '#64748b' }}>TOTAL DEVICES</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#38bdf8' }}>
                {allDevices.length}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '0.6rem', borderRadius: '0.375rem' }}>
              <div style={{ fontSize: '0.7rem', color: '#64748b' }}>ACTIVE LINKS</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#34d399' }}>
                {links.length}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '0.6rem', borderRadius: '0.375rem' }}>
              <div style={{ fontSize: '0.7rem', color: '#64748b' }}>ROUTERS / L3</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#c084fc' }}>
                {routers}
              </div>
            </div>
            <div style={{ background: '#1e293b', padding: '0.6rem', borderRadius: '0.375rem' }}>
              <div style={{ fontSize: '0.7rem', color: '#64748b' }}>SWITCHES / L2</div>
              <div style={{ fontSize: '1.2rem', fontWeight: 'bold', color: '#f59e0b' }}>
                {switches}
              </div>
            </div>
          </div>

          <div style={{ fontSize: '0.75rem', color: '#64748b', lineHeight: 1.4 }}>
            <div>End Stations: {hosts}</div>
            <div>Firewalls: {firewalls}</div>
          </div>
        </div>
      </aside>
    )
  }

  // Handle General Updates
  const handleNameChange = (name: string) => {
    onUpdateDevice({ ...device, name })
  }

  // Handle Interface Updates
  const handleInterfaceChange = (
    ifaceId: string,
    field: 'ipv4_address' | 'subnet_mask' | 'default_gateway' | 'vlan_id',
    val: any
  ) => {
    const updatedInterfaces = device.interfaces.map((i) => {
      if (i.id === ifaceId) {
        return { ...i, [field]: val }
      }
      return i
    })
    onUpdateDevice({ ...device, interfaces: updatedInterfaces })
  }

  // Handle Adding Static Route
  const handleAddRoute = () => {
    const newRoute = {
      destination: '192.168.0.0',
      netmask: '255.255.255.0',
      next_hop: 'DIRECT',
      interface: device.interfaces[0]?.name || 'eth0',
      metric: 1,
    }
    const currentRoutes = device.configuration.routing_table || []
    onUpdateDevice({
      ...device,
      configuration: {
        ...device.configuration,
        routing_table: [...currentRoutes, newRoute],
      },
    })
  }

  // Handle Adding Firewall Rule
  const handleAddFirewallRule = () => {
    const newRule = {
      id: `FW-${Date.now().toString().slice(-4)}`,
      action: 'ALLOW' as const,
      protocol: 'TCP' as const,
      source_ip: 'ANY',
      destination_ip: 'ANY',
      port: 80,
    }
    const currentRules = device.configuration.firewall_rules || []
    onUpdateDevice({
      ...device,
      configuration: {
        ...device.configuration,
        firewall_rules: [...currentRules, newRule],
      },
    })
  }

  return (
    <aside className="simulator-properties" aria-label="Device Properties">
      <div className="prop-header">
        <span className="prop-title">
          <Sliders size={16} /> {device.name} ({device.type})
        </span>
        <button
          className="sim-btn sim-btn-danger"
          style={{ padding: '0.2rem 0.5rem', fontSize: '0.72rem' }}
          onClick={() => onDeleteDevice(device.id)}
          title="Delete Device"
        >
          <Trash2 size={13} /> Delete
        </button>
      </div>

      {/* Tabs */}
      <div className="prop-tabs">
        <button
          className={`prop-tab-btn ${activeTab === 'general' ? 'active' : ''}`}
          onClick={() => setActiveTab('general')}
        >
          General
        </button>
        <button
          className={`prop-tab-btn ${activeTab === 'interfaces' ? 'active' : ''}`}
          onClick={() => setActiveTab('interfaces')}
        >
          Interfaces ({device.interfaces.length})
        </button>
        {device.type === 'ROUTER' && (
          <button
            className={`prop-tab-btn ${activeTab === 'routing' ? 'active' : ''}`}
            onClick={() => setActiveTab('routing')}
          >
            Routing
          </button>
        )}
        {device.type === 'FIREWALL' && (
          <button
            className={`prop-tab-btn ${activeTab === 'firewall' ? 'active' : ''}`}
            onClick={() => setActiveTab('firewall')}
          >
            Firewall
          </button>
        )}
        {['SERVER', 'DNS_SERVER', 'DHCP_SERVER'].includes(device.type) && (
          <button
            className={`prop-tab-btn ${activeTab === 'services' ? 'active' : ''}`}
            onClick={() => setActiveTab('services')}
          >
            Services
          </button>
        )}
      </div>

      <div className="prop-body">
        {/* Tab 1: General */}
        {activeTab === 'general' && (
          <div>
            <div className="prop-form-group">
              <label className="prop-label">Device Name</label>
              <input
                type="text"
                className="prop-input"
                value={device.name}
                onChange={(e) => handleNameChange(e.target.value)}
              />
            </div>
            <div className="prop-form-group">
              <label className="prop-label">Device Type</label>
              <input
                type="text"
                className="prop-input"
                value={device.type}
                readOnly
                disabled
                style={{ opacity: 0.7 }}
              />
            </div>
            <div className="prop-form-group">
              <label className="prop-label">Operational Status</label>
              <span
                style={{
                  display: 'inline-block',
                  padding: '0.2rem 0.5rem',
                  borderRadius: '0.25rem',
                  fontSize: '0.72rem',
                  background: 'rgba(16, 185, 129, 0.15)',
                  color: '#34d399',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                }}
              >
                ONLINE / ACTIVE
              </span>
            </div>
          </div>
        )}

        {/* Tab 2: Interfaces */}
        {activeTab === 'interfaces' && (
          <div>
            {device.interfaces.map((intf) => (
              <div
                key={intf.id}
                style={{
                  marginBottom: '1rem',
                  padding: '0.6rem',
                  background: '#1e293b',
                  borderRadius: '0.375rem',
                }}
              >
                <div
                  style={{
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    color: '#38bdf8',
                    marginBottom: '0.5rem',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.3rem',
                  }}
                >
                  <Network size={14} /> {intf.name}
                </div>

                <div className="prop-form-group">
                  <label className="prop-label">MAC Address (Virtual)</label>
                  <input
                    type="text"
                    className="prop-input"
                    value={intf.mac_address}
                    readOnly
                    disabled
                    style={{ opacity: 0.6 }}
                  />
                </div>

                {device.type !== 'SWITCH' && (
                  <>
                    <div className="prop-form-group">
                      <label className="prop-label">IPv4 Address</label>
                      <input
                        type="text"
                        className="prop-input"
                        placeholder="e.g. 192.168.1.10"
                        value={intf.ipv4_address || ''}
                        onChange={(e) =>
                          handleInterfaceChange(intf.id, 'ipv4_address', e.target.value)
                        }
                      />
                    </div>

                    <div className="prop-form-group">
                      <label className="prop-label">Subnet Mask</label>
                      <input
                        type="text"
                        className="prop-input"
                        placeholder="255.255.255.0"
                        value={intf.subnet_mask || ''}
                        onChange={(e) =>
                          handleInterfaceChange(intf.id, 'subnet_mask', e.target.value)
                        }
                      />
                    </div>

                    {device.type !== 'ROUTER' && device.type !== 'FIREWALL' && (
                      <div className="prop-form-group">
                        <label className="prop-label">Default Gateway</label>
                        <input
                          type="text"
                          className="prop-input"
                          placeholder="e.g. 192.168.1.1"
                          value={intf.default_gateway || ''}
                          onChange={(e) =>
                            handleInterfaceChange(
                              intf.id,
                              'default_gateway',
                              e.target.value
                            )
                          }
                        />
                      </div>
                    )}
                  </>
                )}

                {device.type === 'SWITCH' && (
                  <div className="prop-form-group">
                    <label className="prop-label">Assigned VLAN ID</label>
                    <input
                      type="number"
                      className="prop-input"
                      value={intf.vlan_id ?? 1}
                      onChange={(e) =>
                        handleInterfaceChange(
                          intf.id,
                          'vlan_id',
                          parseInt(e.target.value, 10) || 1
                        )
                      }
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Tab 3: Routing */}
        {activeTab === 'routing' && device.type === 'ROUTER' && (
          <div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '0.6rem',
              }}
            >
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8' }}>
                Static Routes ({device.configuration.routing_table?.length || 0})
              </span>
              <button
                className="sim-btn sim-btn-primary"
                style={{ padding: '0.2rem 0.5rem', fontSize: '0.72rem' }}
                onClick={handleAddRoute}
              >
                <Plus size={12} /> Add Route
              </button>
            </div>

            {(device.configuration.routing_table || []).map((route, idx) => (
              <div
                key={idx}
                style={{
                  background: '#1e293b',
                  padding: '0.5rem',
                  borderRadius: '0.375rem',
                  marginBottom: '0.5rem',
                  fontSize: '0.75rem',
                }}
              >
                <div style={{ color: '#38bdf8', fontWeight: 600 }}>
                  {route.destination}/{route.netmask}
                </div>
                <div style={{ color: '#94a3b8' }}>
                  Next Hop: {route.next_hop} (via {route.interface})
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 4: Firewall */}
        {activeTab === 'firewall' && device.type === 'FIREWALL' && (
          <div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '0.6rem',
              }}
            >
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#94a3b8' }}>
                Access Rules ({device.configuration.firewall_rules?.length || 0})
              </span>
              <button
                className="sim-btn sim-btn-primary"
                style={{ padding: '0.2rem 0.5rem', fontSize: '0.72rem' }}
                onClick={handleAddFirewallRule}
              >
                <Plus size={12} /> Add Rule
              </button>
            </div>

            {(device.configuration.firewall_rules || []).map((rule, idx) => (
              <div
                key={idx}
                style={{
                  background: '#1e293b',
                  padding: '0.5rem',
                  borderRadius: '0.375rem',
                  marginBottom: '0.5rem',
                  fontSize: '0.75rem',
                  borderLeft: `3px solid ${
                    rule.action === 'ALLOW' ? '#10b981' : '#ef4444'
                  }`,
                }}
              >
                <div style={{ fontWeight: 600, color: '#f8fafc' }}>
                  {rule.action} {rule.protocol} {rule.port !== 'ANY' ? `Port ${rule.port}` : ''}
                </div>
                <div style={{ color: '#94a3b8', fontSize: '0.7rem' }}>
                  {rule.description || 'Stateless rule'}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tab 5: Services */}
        {activeTab === 'services' && (
          <div>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, color: '#38bdf8', marginBottom: '0.5rem' }}>
              <Server size={14} /> Configured Services
            </div>
            {device.configuration.dns_records && (
              <div style={{ background: '#1e293b', padding: '0.6rem', borderRadius: '0.375rem', marginBottom: '0.6rem' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.3rem' }}>
                  DNS 'A' Records
                </div>
                {Object.entries(device.configuration.dns_records).map(([name, ip]) => (
                  <div key={name} style={{ fontSize: '0.75rem', fontFamily: 'monospace' }}>
                    <span style={{ color: '#38bdf8' }}>{name}</span> → {ip}
                  </div>
                ))}
              </div>
            )}
            {device.configuration.dhcp_pool && (
              <div style={{ background: '#1e293b', padding: '0.6rem', borderRadius: '0.375rem' }}>
                <div style={{ fontSize: '0.72rem', fontWeight: 600, color: '#94a3b8', marginBottom: '0.3rem' }}>
                  DHCP Lease Pool
                </div>
                <div style={{ fontSize: '0.75rem' }}>
                  Network: {device.configuration.dhcp_pool.network || '192.168.1.0/24'}
                </div>
                <div style={{ fontSize: '0.75rem' }}>
                  Lease Start: {device.configuration.dhcp_pool.start}
                </div>
                <div style={{ fontSize: '0.75rem' }}>
                  Gateway: {device.configuration.dhcp_pool.gateway}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </aside>
  )
}
