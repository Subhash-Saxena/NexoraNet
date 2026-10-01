import React, { useState, useRef, useEffect, useCallback } from 'react'
import { ZoomIn, ZoomOut, Maximize2 } from 'lucide-react'
import type { SimDevice, TopologyLink, HopRecord } from '../../types/simulator'

interface NetworkCanvasProps {
  devices: SimDevice[]
  links: TopologyLink[]
  selectedDeviceId: string | null
  selectedLinkId: string | null
  onSelectDevice: (deviceId: string | null) => void
  onSelectLink: (linkId: string | null) => void
  onMoveDevice: (deviceId: string, x: number, y: number) => void
  onConnectDevices: (
    sourceNodeId: string,
    sourceIfaceId: string,
    targetNodeId: string,
    targetIfaceId: string
  ) => void
  onDeleteLink: (linkId: string) => void
  activeHop: HopRecord | null
}

export const NetworkCanvas: React.FC<NetworkCanvasProps> = ({
  devices,
  links,
  selectedDeviceId,
  selectedLinkId,
  onSelectDevice,
  onSelectLink,
  onMoveDevice,
  onConnectDevices,
  onDeleteLink,
  activeHop,
}) => {
  const svgRef = useRef<SVGSVGElement | null>(null)

  // Zoom & Pan state
  const [zoom, setZoom] = useState<number>(1)
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 })
  const [isPanning, setIsPanning] = useState<boolean>(false)
  const [panStart, setPanStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 })

  // Node dragging state
  const [draggingNodeId, setDraggingNodeId] = useState<string | null>(null)
  const [dragOffset, setDragOffset] = useState<{ x: number; y: number }>({ x: 0, y: 0 })

  // Port connection mode state
  const [connectingFrom, setConnectingFrom] = useState<{
    nodeId: string
    ifaceId: string
    x: number
    y: number
  } | null>(null)
  const [mousePos, setMousePos] = useState<{ x: number; y: number }>({ x: 0, y: 0 })

  // Packet animation state
  const [packetProgress, setPacketProgress] = useState<number>(0)

  // Trigger smooth packet animation when activeHop updates
  useEffect(() => {
    if (!activeHop) {
      setPacketProgress(0)
      return
    }
    setPacketProgress(0)
    let start: number | null = null
    const duration = 800 // ms
    let animId: number

    const step = (timestamp: number) => {
      if (!start) start = timestamp
      const elapsed = timestamp - start
      const progress = Math.min(1, elapsed / duration)
      setPacketProgress(progress)
      if (progress < 1) {
        animId = requestAnimationFrame(step)
      }
    }

    animId = requestAnimationFrame(step)
    return () => cancelAnimationFrame(animId)
  }, [activeHop])

  // Mouse coordinate helper
  const getSvgCoordinates = useCallback(
    (e: React.MouseEvent) => {
      if (!svgRef.current) return { x: 0, y: 0 }
      const rect = svgRef.current.getBoundingClientRect()
      return {
        x: (e.clientX - rect.left - pan.x) / zoom,
        y: (e.clientY - rect.top - pan.y) / zoom,
      }
    },
    [pan, zoom]
  )

  // Handle Drag from Palette
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = 'copy'
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    const type = e.dataTransfer.getData('application/nexoranet-device')
    if (!type) return
    const coords = getSvgCoordinates(e)
    // Parent handles adding device
    const customEvent = new CustomEvent('add-device-at', {
      detail: { type, x: Math.round(coords.x), y: Math.round(coords.y) },
    })
    window.dispatchEvent(customEvent)
  }

  // Handle Node MouseDown (drag start)
  const handleNodeMouseDown = (e: React.MouseEvent, node: SimDevice) => {
    e.stopPropagation()
    if (connectingFrom) return
    onSelectDevice(node.id)
    onSelectLink(null)
    const coords = getSvgCoordinates(e)
    setDraggingNodeId(node.id)
    setDragOffset({
      x: coords.x - node.position_x,
      y: coords.y - node.position_y,
    })
  }

  // Handle Port Click (connection creation)
  const handlePortClick = (e: React.MouseEvent, node: SimDevice, ifaceId: string) => {
    e.stopPropagation()
    const portX = node.position_x + 55
    const portY = node.position_y + 35

    if (!connectingFrom) {
      // Start connection
      setConnectingFrom({ nodeId: node.id, ifaceId, x: portX, y: portY })
    } else {
      // Complete connection
      if (connectingFrom.nodeId !== node.id) {
        onConnectDevices(
          connectingFrom.nodeId,
          connectingFrom.ifaceId,
          node.id,
          ifaceId
        )
      }
      setConnectingFrom(null)
    }
  }

  // Canvas Mouse Move
  const handleMouseMove = (e: React.MouseEvent) => {
    const coords = getSvgCoordinates(e)
    setMousePos(coords)

    if (draggingNodeId) {
      onMoveDevice(
        draggingNodeId,
        Math.max(20, Math.round(coords.x - dragOffset.x)),
        Math.max(20, Math.round(coords.y - dragOffset.y))
      )
    } else if (isPanning) {
      setPan({
        x: e.clientX - panStart.x,
        y: e.clientY - panStart.y,
      })
    }
  }

  // Canvas Mouse Up
  const handleMouseUp = () => {
    setDraggingNodeId(null)
    setIsPanning(false)
  }

  // Canvas Background Mouse Down (Pan start or deselect)
  const handleCanvasMouseDown = (e: React.MouseEvent) => {
    if (e.target === svgRef.current || (e.target as HTMLElement).tagName === 'svg') {
      onSelectDevice(null)
      onSelectLink(null)
      setConnectingFrom(null)
      setIsPanning(true)
      setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y })
    }
  }

  const handleZoomIn = () => setZoom((z) => Math.min(2.0, z + 0.15))
  const handleZoomOut = () => setZoom((z) => Math.max(0.5, z - 0.15))
  const handleResetZoom = () => {
    setZoom(1)
    setPan({ x: 0, y: 0 })
  }

  // Node Map for fast link coordinate lookup
  const nodeMap = new Map(devices.map((d) => [d.id, d]))

  return (
    <div
      className="canvas-viewport"
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      data-testid="network-canvas"
    >
      <div className="canvas-grid-bg" />

      {/* Floating Zoom & Pan Controls */}
      <div className="canvas-floating-controls">
        <button
          className="canvas-floating-btn"
          onClick={handleZoomIn}
          title="Zoom In"
          aria-label="Zoom In"
        >
          <ZoomIn size={15} />
        </button>
        <button
          className="canvas-floating-btn"
          onClick={handleZoomOut}
          title="Zoom Out"
          aria-label="Zoom Out"
        >
          <ZoomOut size={15} />
        </button>
        <button
          className="canvas-floating-btn"
          onClick={handleResetZoom}
          title="Reset View"
          aria-label="Reset View"
        >
          <Maximize2 size={15} />
        </button>
      </div>

      <svg
        ref={svgRef}
        className="canvas-svg"
        onMouseDown={handleCanvasMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
      >
        <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
          {/* Render Cable Links */}
          {links.map((link) => {
            const src = nodeMap.get(link.source_node_id)
            const dst = nodeMap.get(link.target_node_id)
            if (!src || !dst) return null

            const x1 = src.position_x + 55
            const y1 = src.position_y + 35
            const x2 = dst.position_x + 55
            const y2 = dst.position_y + 35

            const isSelected = selectedLinkId === link.id
            const isDown = link.status === 'down'

            return (
              <g
                key={link.id}
                onClick={(e) => {
                  e.stopPropagation()
                  onSelectLink(link.id)
                  onSelectDevice(null)
                }}
              >
                {/* Clickable transparent wider stroke */}
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke="transparent"
                  strokeWidth={16}
                  style={{ cursor: 'pointer' }}
                />
                {/* Visual link wire */}
                <line
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  className={`canvas-link ${isDown ? 'down' : ''} ${
                    isSelected ? 'active' : ''
                  }`}
                />
                {/* Delete button when link is selected */}
                {isSelected && (
                  <g
                    className="link-delete-btn"
                    transform={`translate(${(x1 + x2) / 2}, ${(y1 + y2) / 2})`}
                    onClick={(e) => {
                      e.stopPropagation()
                      onDeleteLink(link.id)
                    }}
                    style={{ cursor: 'pointer' }}
                  >
                    <circle r={9} fill="#ef4444" stroke="#ffffff" strokeWidth={1.5} />
                    <text
                      textAnchor="middle"
                      dy=".35em"
                      fill="#ffffff"
                      fontSize="11"
                      fontWeight="bold"
                    >
                      ✕
                    </text>
                  </g>
                )}
              </g>
            )
          })}

          {/* Active Connection Wire in progress */}
          {connectingFrom && (
            <line
              x1={connectingFrom.x}
              y1={connectingFrom.y}
              x2={mousePos.x}
              y2={mousePos.y}
              stroke="#38bdf8"
              strokeWidth={2}
              strokeDasharray="5,5"
              pointerEvents="none"
            />
          )}

          {/* Animated Packet Pulse */}
          {activeHop && (
            (() => {
              const curr = nodeMap.get(activeHop.device_id)
              if (!curr) return null
              // Find adjacent link toward next hop or draw pulse at current node
              const cx = curr.position_x + 55
              const cy = curr.position_y + 35

              return (
                <g>
                  <circle
                    cx={cx}
                    cy={cy}
                    r={10}
                    fill="none"
                    stroke="#38bdf8"
                    strokeWidth={2}
                    opacity={1 - packetProgress}
                  />
                  <circle
                    cx={cx}
                    cy={cy}
                    r={6}
                    fill="#38bdf8"
                    filter="drop-shadow(0 0 6px #00f3ff)"
                  />
                  <text
                    x={cx}
                    y={cy - 12}
                    fill="#38bdf8"
                    fontSize={10}
                    fontWeight="bold"
                    textAnchor="middle"
                  >
                    {activeHop.packet_snapshot.protocol}
                  </text>
                </g>
              )
            })()
          )}

          {/* Render Device Nodes */}
          {devices.map((device) => {
            const isSelected = selectedDeviceId === device.id
            const iface = device.interfaces[0]
            const ip = iface?.ipv4_address || 'Unassigned'

            return (
              <g
                key={device.id}
                className={`canvas-node ${isSelected ? 'selected' : ''}`}
                transform={`translate(${device.position_x}, ${device.position_y})`}
                onMouseDown={(e) => handleNodeMouseDown(e, device)}
              >
                {/* Node Box */}
                <rect
                  className="node-box"
                  width={110}
                  height={70}
                  x={0}
                  y={0}
                />

                {/* Device Type Badge */}
                <rect
                  x={8}
                  y={6}
                  width={34}
                  height={14}
                  rx={3}
                  fill="rgba(56, 189, 248, 0.15)"
                />
                <text
                  x={25}
                  y={16}
                  fill="#38bdf8"
                  fontSize={8}
                  fontWeight="bold"
                  textAnchor="middle"
                >
                  {device.type.slice(0, 5)}
                </text>

                {/* Device Name */}
                <text className="node-label" x={55} y={38}>
                  {device.name}
                </text>

                {/* IP Address Label */}
                <text className="node-sublabel" x={55} y={54}>
                  {ip}
                </text>

                {/* Port Indicators (Left, Right) */}
                {device.interfaces.map((intf, idx) => {
                  const isLeft = idx % 2 === 0
                  const px = isLeft ? 0 : 110
                  const py = 25 + Math.min(30, idx * 16)
                  const isConnecting =
                    connectingFrom?.nodeId === device.id &&
                    connectingFrom.ifaceId === intf.id

                  return (
                    <circle
                      key={intf.id}
                      className={`port-indicator ${
                        isConnecting ? 'connecting' : ''
                      }`}
                      cx={px}
                      cy={py}
                      r={5}
                      onClick={(e) => handlePortClick(e, device, intf.id)}
                    >
                      <title>{`Port: ${intf.name} (${intf.mac_address})`}</title>
                    </circle>
                  )
                })}
              </g>
            )
          })}
        </g>
      </svg>
    </div>
  )
}
