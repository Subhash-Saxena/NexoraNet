import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Compass,
  ArrowRight,
} from 'lucide-react'
import type { DifficultyLevel } from '../../types'

interface RoadmapMilestone {
  id: string
  title: string
  slug: string
  category: DifficultyLevel
  description: string
  topicCount: number
  skillsTaught: string[]
}

const ROADMAP_DATA: Record<DifficultyLevel, RoadmapMilestone[]> = {
  BEGINNER: [
    {
      id: 'bg-1',
      title: 'Networking Fundamentals',
      slug: 'networking-fundamentals',
      category: 'BEGINNER',
      description: 'Host types, topologies, transmission mediums, and client-server paradigm.',
      topicCount: 6,
      skillsTaught: ['LAN/WAN concepts', 'Bandwidth vs Latency', 'Duplex modes'],
    },
    {
      id: 'bg-2',
      title: 'OSI & TCP/IP Models',
      slug: 'osi-tcpip-models',
      category: 'BEGINNER',
      description: '7-layer OSI reference, 4-layer TCP/IP stack, and packet encapsulation.',
      topicCount: 7,
      skillsTaught: ['Layer responsibilities', 'PDU mapping', 'Encapsulation overhead'],
    },
    {
      id: 'bg-3',
      title: 'IP Addressing',
      slug: 'ip-addressing-basics',
      category: 'BEGINNER',
      description: 'IPv4 structure, dotted decimal, default masks, and public vs private scopes.',
      topicCount: 6,
      skillsTaught: ['IPv4 Octets', 'RFC 1918 Private Ranges', 'Loopback & APIPA'],
    },
    {
      id: 'bg-4',
      title: 'Core Protocols',
      slug: 'core-protocols-arp-icmp',
      category: 'BEGINNER',
      description: 'ARP resolution, ICMP echo replies, traceroute mechanics, and ping diagnostics.',
      topicCount: 5,
      skillsTaught: ['ARP cache tables', 'ICMP types/codes', 'TTL expiration'],
    },
    {
      id: 'bg-5',
      title: 'TCP & UDP Transport',
      slug: 'tcp-udp-transport',
      category: 'BEGINNER',
      description: 'Connection-oriented TCP vs best-effort UDP, port multiplexing, and handshakes.',
      topicCount: 6,
      skillsTaught: ['3-way handshake', 'Well-known ports', 'Reliability mechanisms'],
    },
    {
      id: 'bg-6',
      title: 'Basic Network Security',
      slug: 'basic-network-security',
      category: 'BEGINNER',
      description: 'Port scanning concepts, perimeter security basics, and cleartext dangers.',
      topicCount: 5,
      skillsTaught: ['Reconnaissance defense', 'Firewall concepts', 'Secure protocols'],
    },
  ],
  INTERMEDIATE: [
    {
      id: 'im-1',
      title: 'Subnetting & CIDR',
      slug: 'subnetting-cidr-mastery',
      category: 'INTERMEDIATE',
      description: 'VLSM, slash notation, block sizes, host calculations, and summarization.',
      topicCount: 8,
      skillsTaught: ['Prefix masks /24 to /30', 'Broadcast calculation', 'Usable IP ranges'],
    },
    {
      id: 'im-2',
      title: 'IPv4 & IPv6 Deep Dive',
      slug: 'ipv4-ipv6-architecture',
      category: 'INTERMEDIATE',
      description: '128-bit IPv6 addressing, SLAAC autoconfiguration, NDP, and dual-stack.',
      topicCount: 7,
      skillsTaught: ['IPv6 hex notation', 'Neighbor Discovery', 'Header comparisons'],
    },
    {
      id: 'im-3',
      title: 'DNS & DHCP Architecture',
      slug: 'dns-dhcp-infrastructure',
      category: 'INTERMEDIATE',
      description: 'Hierarchical resolution, resource records, DORA protocol, and lease management.',
      topicCount: 8,
      skillsTaught: ['A/AAAA/CNAME/MX', 'DHCP options', 'Relay agents'],
    },
    {
      id: 'im-4',
      title: 'HTTP, HTTPS & TLS',
      slug: 'http-https-tls-internals',
      category: 'INTERMEDIATE',
      description: 'HTTP request/response headers, TLS 1.3 handshake, certificates, and PKI.',
      topicCount: 7,
      skillsTaught: ['Cipher suites', 'X.509 cert validation', 'HSTS enforcement'],
    },
    {
      id: 'im-5',
      title: 'Dynamic Routing Protocols',
      slug: 'routing-protocols-ospf-bgp',
      category: 'INTERMEDIATE',
      description: 'Distance-vector vs link-state, Dijkstra SPF algorithm, OSPF areas, and BGP AS.',
      topicCount: 8,
      skillsTaught: ['OSPF LSA exchange', 'Route metrics/AD', 'BGP peering'],
    },
    {
      id: 'im-6',
      title: 'Switching & VLANs',
      slug: 'switching-vlans-trunking',
      category: 'INTERMEDIATE',
      description: 'Ethernet switching logic, CAM tables, 802.1Q trunking, and Spanning Tree (STP).',
      topicCount: 8,
      skillsTaught: ['802.1Q tags', 'STP loop prevention', 'Access vs Trunk ports'],
    },
    {
      id: 'im-7',
      title: 'Network Troubleshooting',
      slug: 'network-troubleshooting-tools',
      category: 'INTERMEDIATE',
      description: 'Systematic diagnosis with ping, traceroute, netstat, ss, curl, dig, and Wireshark.',
      topicCount: 6,
      skillsTaught: ['CLI diagnostics', 'MTU troubleshooting', 'Socket analysis'],
    },
    {
      id: 'im-8',
      title: 'Network Security Architecture',
      slug: 'network-security-controls',
      category: 'INTERMEDIATE',
      description: 'Stateful firewalls, NAT/PAT translation, DMZ segmentation, and VPN tunneling.',
      topicCount: 7,
      skillsTaught: ['Stateful tables', 'Overload PAT', 'IPsec phase 1 & 2'],
    },
  ],
  ADVANCED: [
    {
      id: 'ad-1',
      title: 'Packet Analysis & PCAP',
      slug: 'packet-analysis-wireshark',
      category: 'ADVANCED',
      description: 'Packet dissectors, TCP stream reassembly, BPF display filters, and flow inspection.',
      topicCount: 8,
      skillsTaught: ['Wireshark filters', 'Stream analysis', 'Malformed frames'],
    },
    {
      id: 'ad-2',
      title: 'Advanced Networking Protocols',
      slug: 'advanced-networking-protocols',
      category: 'ADVANCED',
      description: 'MPLS, BGP route reflectors, EVPN, VXLAN overlays, and multicast IGMP.',
      topicCount: 7,
      skillsTaught: ['Label switching', 'Overlay fabrics', 'Multicast distribution'],
    },
    {
      id: 'ad-3',
      title: 'Traffic & Anomaly Analysis',
      slug: 'traffic-analysis-baselines',
      category: 'ADVANCED',
      description: 'NetFlow, IPFIX telemetry, baseline profiling, and volumetric anomaly detection.',
      topicCount: 7,
      skillsTaught: ['Flow metrics', 'Beaconing analysis', 'Exfiltration detection'],
    },
    {
      id: 'ad-4',
      title: 'IDS / IPS Rule Engineering',
      slug: 'ids-ips-rule-engineering',
      category: 'ADVANCED',
      description: 'Writing Snort and Suricata signatures, content offsets, and evasion techniques.',
      topicCount: 8,
      skillsTaught: ['Snort rule syntax', 'Fast pattern matching', 'Thresholding'],
    },
    {
      id: 'ad-5',
      title: 'Detection Engineering',
      slug: 'detection-engineering-threats',
      category: 'ADVANCED',
      description: 'MITRE ATT&CK mapping, network behavioral heuristics, and Zeek bro scripts.',
      topicCount: 7,
      skillsTaught: ['TTP identification', 'Zeek scripting', 'Sigma rules'],
    },
    {
      id: 'ad-6',
      title: 'Mini SOC Fundamentals',
      slug: 'mini-soc-workflows',
      category: 'ADVANCED',
      description: 'SIEM log ingestion, correlation rules, alert triage, and false positive tuning.',
      topicCount: 6,
      skillsTaught: ['Alert prioritization', 'Log correlation', 'Playbook execution'],
    },
    {
      id: 'ad-7',
      title: 'Incident Investigation',
      slug: 'incident-investigation-forensics',
      category: 'ADVANCED',
      description: 'Network forensics, timeline reconstruction, lateral movement tracking, and C2.',
      topicCount: 7,
      skillsTaught: ['Evidence preservation', 'C2 beacon hunting', 'Pivoting analysis'],
    },
    {
      id: 'ad-8',
      title: 'Network Threat Defense',
      slug: 'network-threat-defense',
      category: 'ADVANCED',
      description: 'Zero Trust architecture, micro-segmentation, link encryption, and resilient defense.',
      topicCount: 7,
      skillsTaught: ['Zero trust policy', 'Microsegmentation', 'Defense-in-depth'],
    },
  ],
  MIXED: [],
}

export interface LearningRoadmapProps {
  onSelectMilestone?: (slug: string) => void
  onSelectDifficulty?: (level: DifficultyLevel) => void
}

export const LearningRoadmap: React.FC<LearningRoadmapProps> = ({
  onSelectMilestone,
  onSelectDifficulty,
}) => {
  const [activeLevel, setActiveLevel] = useState<DifficultyLevel>('BEGINNER')
  const [selectedMilestone, setSelectedMilestone] = useState<RoadmapMilestone>(ROADMAP_DATA.BEGINNER[0])

  const levels: DifficultyLevel[] = ['BEGINNER', 'INTERMEDIATE', 'ADVANCED']

  const handleLevelChange = (lvl: DifficultyLevel) => {
    setActiveLevel(lvl)
    setSelectedMilestone(ROADMAP_DATA[lvl][0])
    if (onSelectDifficulty) onSelectDifficulty(lvl)
  }

  const handleMilestoneClick = (milestone: RoadmapMilestone) => {
    setSelectedMilestone(milestone)
    if (onSelectMilestone) onSelectMilestone(milestone.slug)
  }

  return (
    <div className="roadmap-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--text-main)', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Compass size={20} color="var(--cyan-primary)" />
            <span>Interactive Learning Roadmap</span>
          </h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.84rem', marginTop: '2px' }}>
            Step-by-step curriculum progression from foundational bits to enterprise threat defense
          </p>
        </div>

        {/* Level Switcher */}
        <div style={{ display: 'flex', gap: '8px' }}>
          {levels.map((lvl) => {
            const isActive = activeLevel === lvl
            const color = lvl === 'BEGINNER' ? 'var(--emerald-success)' : lvl === 'INTERMEDIATE' ? 'var(--cyan-primary)' : 'var(--purple-soc)'
            return (
              <button
                key={lvl}
                onClick={() => handleLevelChange(lvl)}
                style={{
                  padding: '8px 16px',
                  borderRadius: 'var(--radius-sm)',
                  fontSize: '0.82rem',
                  fontWeight: 700,
                  cursor: 'pointer',
                  border: '1px solid',
                  borderColor: isActive ? color : 'var(--border-color)',
                  background: isActive ? 'rgba(255, 255, 255, 0.08)' : 'rgba(255, 255, 255, 0.02)',
                  color: isActive ? color : 'var(--text-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  transition: 'all 0.15s ease',
                }}
              >
                <span>{lvl}</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Horizontal Milestone Pipeline */}
      <div className="roadmap-nodes-flow" style={{ marginBottom: '20px' }}>
        {ROADMAP_DATA[activeLevel].map((item, idx) => {
          const isSelected = selectedMilestone.id === item.id
          const isLast = idx === ROADMAP_DATA[activeLevel].length - 1
          return (
            <React.Fragment key={item.id}>
              <div
                onClick={() => handleMilestoneClick(item)}
                className={`roadmap-node ${isSelected ? 'active-milestone' : ''}`}
                style={{
                  borderColor: isSelected
                    ? activeLevel === 'BEGINNER'
                      ? 'var(--emerald-success)'
                      : activeLevel === 'INTERMEDIATE'
                      ? 'var(--cyan-primary)'
                      : 'var(--purple-soc)'
                    : undefined,
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 700 }}>
                    #{idx + 1}
                  </span>
                  <span className="badge badge-phase" style={{ fontSize: '0.65rem' }}>
                    {item.topicCount} topics
                  </span>
                </div>
                <div style={{ fontSize: '0.88rem', fontWeight: 700, color: 'var(--text-main)', marginTop: '4px' }}>
                  {item.title}
                </div>
              </div>

              {!isLast && (
                <div className="roadmap-connector-arrow">
                  <ArrowRight size={16} />
                </div>
              )}
            </React.Fragment>
          )
        })}
      </div>

      {/* Selected Milestone Information Card */}
      <div
        style={{
          background: 'rgba(14, 23, 42, 0.85)',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-md)',
          padding: '20px 24px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          gap: '20px',
          flexWrap: 'wrap',
        }}
      >
        <div style={{ flex: 1, minWidth: '260px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span
              className="badge"
              style={{
                background:
                  activeLevel === 'BEGINNER'
                    ? 'rgba(16, 185, 129, 0.15)'
                    : activeLevel === 'INTERMEDIATE'
                    ? 'rgba(6, 182, 212, 0.15)'
                    : 'rgba(139, 92, 246, 0.15)',
                color:
                  activeLevel === 'BEGINNER'
                    ? 'var(--emerald-success)'
                    : activeLevel === 'INTERMEDIATE'
                    ? 'var(--cyan-primary)'
                    : 'var(--purple-soc)',
              }}
            >
              {selectedMilestone.category} TRACK
            </span>
            <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-main)' }}>
              {selectedMilestone.title}
            </h4>
          </div>

          <p style={{ color: '#cbd5e1', fontSize: '0.88rem', lineHeight: 1.5, marginBottom: '12px' }}>
            {selectedMilestone.description}
          </p>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)', fontWeight: 600 }}>Key Competencies:</span>
            {selectedMilestone.skillsTaught.map((skill, sIdx) => (
              <span
                key={sIdx}
                style={{
                  background: 'rgba(255, 255, 255, 0.04)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  padding: '2px 8px',
                  fontSize: '0.74rem',
                  color: 'var(--cyan-primary)',
                }}
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

        <Link
          to={`/learning/topics/${selectedMilestone.slug}`}
          className="diagram-btn primary"
          style={{ padding: '10px 18px', textDecoration: 'none' }}
        >
          <span>Explore Syllabus Topics</span>
          <ArrowRight size={16} />
        </Link>
      </div>
    </div>
  )
}
