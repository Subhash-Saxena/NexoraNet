# NexoraNet — Networking & Cybersecurity Curriculum

> **NexoraNet**: *"Learn. Simulate. Analyze. Defend."*  
> **Course**: Computer Networking & Cybersecurity Engineering  
> **Total Modules**: 19  
> **Total Topics**: 126  
> **Total Seed Lessons**: 38 Comprehensive Lessons (Min. 36 Required)

---

## 1. 10-Point Pedagogical Lesson Structure

Every lesson in NexoraNet follows a rigorous, uniform 10-point educational format designed to bridge theory, technical engineering, offensive exploitation, and defensive operations:

1. **Title & Conceptual Hook**: Engaging introductory question or analogy.
2. **Simple English Explanation ("BCA Simple")**: Intuitive concept foundation without overwhelming jargon.
3. **Technical Deep-Dive**: RFC protocol behavior, state transitions, and low-level specifications.
4. **Packet / Protocol Format & Header Offsets**: Bit/byte diagrams, field sizes, and flag interpretations.
5. **Real-World Engineering Example**: Practical production topology or packet capture trace.
6. **Common Misconceptions & Pitfalls**: Clarifying subtle differences (e.g., collision domains vs broadcast domains).
7. **Cybersecurity & Attack Relevance**: Attacker exploitation, threat vectors, and offensive tooling (Nmap, Wireshark, Scapy).
8. **Defensive Hardening & Detection**: Practical mitigations, firewall configurations, and IDS rules.
9. **Interactive Visual Diagram / Activity**: Interactive browser widget to explore state transitions.
10. **Quick Revision & Key Takeaways**: High-impact bullet points, port tables, and exam interview notes.

---

## 2. Curriculum Tier Structure

```
                  ┌──────────────────────────────────────────────┐
                  │           ADVANCED (Level 3)                 │
                  │  Packet Analysis • Telemetry • SOC • Defense  │
                  └───────────────────────▲──────────────────────┘
                                          │
                  ┌───────────────────────┴──────────────────────┐
                  │         INTERMEDIATE (Level 2)               │
                  │   Subnetting • Routing • Switching • TLS     │
                  └───────────────────────▲──────────────────────┘
                                          │
                  ┌───────────────────────┴──────────────────────┐
                  │           BEGINNER (Level 1)                 │
                  │  Fundamentals • OSI/TCP • Addressing • Ports │
                  └──────────────────────────────────────────────┘
```

---

## 3. Detailed Syllabus & Lesson Directory

### Tier 1: Beginner Track (16 Lessons)
| # | Module | Topic | Lesson Title | Slug |
|---|---|---|---|---|
| 1 | Networking Fundamentals | Network Topologies | Introduction to Computer Networks & Topologies | `what-is-computer-networking-intro` |
| 2 | Networking Fundamentals | Network Topologies | Star, Mesh, Bus & Hybrid Architectures | `network-topologies-star-mesh-bus` |
| 3 | Networking Fundamentals | Network Types | LAN, WAN, MAN & WLAN Architectures | `network-types-lan-wan-man-wlan` |
| 4 | Networking Fundamentals | Bandwidth & Latency | Bandwidth, Throughput, Latency & Jitter | `bandwidth-throughput-latency-jitter` |
| 5 | OSI & TCP/IP Models | OSI 7-Layer Architecture | OSI Model Deep-Dive: Physical to Transport | `osi-model-deep-dive-physical-to-transport` |
| 6 | OSI & TCP/IP Models | OSI 7-Layer Architecture | OSI Model Deep-Dive: Session to Application | `osi-model-deep-dive-session-to-application` |
| 7 | OSI & TCP/IP Models | TCP/IP 4-Layer Architecture | TCP/IP Stack vs OSI Model: Comparative Analysis | `tcpip-stack-vs-osi-model-comparison` |
| 8 | OSI & TCP/IP Models | Encapsulation & Headers | Packet Encapsulation & Protocol Headers | `packet-encapsulation-protocol-headers` |
| 9 | IP Addressing Basics | IPv4 Structure | IPv4 Address Structure & Dotted Decimal | `ipv4-address-structure-octets` |
| 10 | IP Addressing Basics | Address Classes | IPv4 Address Classes & Default Subnet Masks | `ipv4-address-classes-default-masks` |
| 11 | IP Addressing Basics | Public vs Private IP | Public vs Private IP Addresses (RFC 1918) | `public-vs-private-ip-rfc-1918` |
| 12 | IP Addressing Basics | Special IP Ranges | Special IP Ranges: Loopback, APIPA & Multicast | `special-ip-ranges-loopback-apipa` |
| 13 | Core Network Protocols | Address Resolution Protocol | ARP Fundamentals & Frame Mapping | `arp-fundamentals-mac-resolution` |
| 14 | Core Network Protocols | Internet Control Message | ICMP Fundamentals: Ping & Traceroute Mechanics | `icmp-fundamentals-ping-traceroute` |
| 15 | Transport Layer Basics | TCP Protocol Internals | TCP Protocol: Reliable Delivery & 3-Way Handshake | `tcp-protocol-reliable-3way-handshake` |
| 16 | Transport Layer Basics | UDP & Port Multiplexing | UDP Protocol & Well-Known Port Numbers | `udp-protocol-well-known-ports` |

---

### Tier 2: Intermediate Track (12 Lessons)
| # | Module | Topic | Lesson Title | Slug |
|---|---|---|---|---|
| 17 | Subnetting & IP Architecture | Subnetting & CIDR | Subnetting Primer: Powers of 2 & Binary Foundations | `subnetting-primer-powers-of-2-binary-foundations` |
| 18 | Subnetting & IP Architecture | Subnetting & CIDR | CIDR Notation & Subnet Mask Calculations | `cidr-notation-subnet-mask-calculations` |
| 19 | Subnetting & IP Architecture | VLSM Design | Variable Length Subnet Masking (VLSM) Design | `vlsm-design-variable-length-subnet-masking` |
| 20 | Subnetting & IP Architecture | IPv6 Architecture | IPv6 Architecture: 128-bit Addressing & NDP | `ipv6-architecture-128bit-addressing-ndp` |
| 21 | Application Layer Protocols | DNS Architecture | DNS Architecture: Recursive Resolution & Nameservers | `dns-architecture-recursive-resolution-nameservers` |
| 22 | Application Layer Protocols | DHCP & Auto-Configuration | DHCP Protocol: The DORA Process & Lease Mechanics | `dhcp-protocol-dora-process-lease-mechanics` |
| 23 | Application Layer Protocols | HTTP, HTTPS & TLS | HTTP/1.1 vs HTTP/2 vs HTTP/3 & TLS 1.3 Handshake | `http-https-tls13-handshake-architecture` |
| 24 | Routing & Switching Architecture | Dynamic Routing Fundamentals | Routing Protocols: Distance-Vector vs Link-State (OSPF) | `routing-protocols-distance-vector-link-state-ospf` |
| 25 | Routing & Switching Architecture | BGP & Autonomous Systems | Border Gateway Protocol (BGP) & Internet Routing | `bgp-autonomous-systems-internet-routing` |
| 26 | Routing & Switching Architecture | Ethernet Switching & VLANs | Ethernet Switching Logic, MAC Tables & VLANs (802.1Q) | `ethernet-switching-mac-tables-vlans-8021q` |
| 27 | Routing & Switching Architecture | Spanning Tree Protocol | Spanning Tree Protocol (STP) & Loop Prevention | `spanning-tree-protocol-stp-loop-prevention` |
| 28 | Network Troubleshooting Tools | Command-Line Diagnostics | Essential Diagnostic CLI Tools: Ping, Traceroute & Netstat | `essential-cli-diagnostics-ping-traceroute-netstat` |

---

### Tier 3: Advanced Track (8 Lessons)
| # | Module | Topic | Lesson Title | Slug |
|---|---|---|---|---|
| 29 | Packet Analysis & Forensics | Wireshark Fundamentals | Deep Packet Inspection with Wireshark & BPF Filters | `deep-packet-inspection-wireshark-bpf-filters` |
| 30 | Packet Analysis & Forensics | TCP Stream Reconstruction | TCP Stream Reassembly & Protocol Dissection | `tcp-stream-reassembly-protocol-dissection` |
| 31 | Advanced Enterprise Networking | Multiprotocol Label Switching | MPLS & Overlay Network Architectures (VXLAN) | `mpls-overlay-network-architectures-vxlan` |
| 32 | Network Security Architecture | Firewall Architectures | Stateful Inspection Firewalls & NAT/PAT Translation | `stateful-inspection-firewalls-nat-pat-translation` |
| 33 | Network Security Architecture | Intrusion Detection Systems | IDS/IPS Engineering: Writing Snort & Suricata Signatures | `ids-ips-engineering-snort-suricata-signatures` |
| 34 | Network Security Architecture | Network Telemetry & Flow | Network Flow Telemetry: NetFlow, IPFIX & Baseline Analysis | `network-flow-telemetry-netflow-ipfix-baselines` |
| 35 | Security Operations & Defense | SOC Workflows & Incident Triage | Security Operations Center (SOC) Workflows & Alert Triage | `soc-workflows-alert-triage-incident-handling` |
| 36 | Security Operations & Defense | Network Forensics & C2 | Network Forensics: Investigating Lateral Movement & C2 | `network-forensics-lateral-movement-c2-investigation` |
| 37 | Security Operations & Defense | Detection Engineering | Detection Engineering: MITRE ATT&CK & Zeek Telemetry | `detection-engineering-mitre-attck-zeek-telemetry` |
| 38 | Security Operations & Defense | Zero Trust Architecture | Zero Trust Network Architecture & Microsegmentation | `zero-trust-network-architecture-microsegmentation` |

---

## 4. Prerequisite Dependency Graph

The curriculum incorporates formal prerequisites enforced in SQLite:
- *Networking Fundamentals* ➔ *OSI & TCP/IP Models*
- *OSI & TCP/IP Models* ➔ *IP Addressing Basics*
- *IP Addressing Basics* ➔ *Core Protocols (ARP & ICMP)*
- *IP Addressing Basics* ➔ *Subnetting & CIDR*
- *Core Protocols* ➔ *TCP & UDP Transport*
- *Subnetting & CIDR* ➔ *IPv4 & IPv6 Deep Dive*
- *TCP & UDP Transport* ➔ *Application Protocols (DNS, DHCP, HTTP)*
- *Application Protocols* ➔ *Dynamic Routing Protocols (OSPF, BGP)*
- *Dynamic Routing Protocols* ➔ *Packet Analysis & Wireshark*
- *Packet Analysis* ➔ *IDS/IPS Rule Engineering & Detection Engineering*
- *Detection Engineering* ➔ *SOC Workflows & Incident Investigation*
- *SOC Workflows* ➔ *Zero Trust Architecture*
