#!/usr/bin/env python3
"""
Generate the Step 7 Mock Test Catalog JSON definitions in backend/data/mock_tests/.
Produces:
- beginner.json (14 tests)
- intermediate.json (16 tests)
- advanced.json (13 tests)
- full_mocks.json (3 tests)
Total: 46 structured, pedagogical mock tests.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "mock_tests"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_beginner_tests():
    return [
        {
            "code": "BEGINNER-NETWORKING-001",
            "title": "Networking Fundamentals",
            "slug": "networking-fundamentals",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 20,
            "total_questions": 20,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Test your understanding of core computer networking fundamentals, network topologies (star, mesh, bus), transmission media, LAN vs WAN boundaries, and client-server communication models.",
            "instructions": "Answer 20 multiple-choice questions within 20 minutes. Score 70% or higher to achieve a passing grade.",
            "prerequisites": "None. Suitable for beginners starting their computer networking journey.",
            "tags": ["fundamentals", "lan", "wan", "topologies", "client-server"],
            "what_you_will_practice": [
                "Distinguish between LAN, WAN, MAN, and PAN scales",
                "Identify star, mesh, bus, and ring network topologies",
                "Understand client-server vs peer-to-peer architectures",
                "Recognize standard transmission media and signaling properties"
            ],
            "blueprint": {
                "title": "Networking Fundamentals Blueprint",
                "description": "Assesses foundational computer networking concepts, topologies, and transmission media.",
                "topics": [
                    {"topic_slug": "what-is-computer-networking", "question_count": 5, "difficulty": "BEGINNER"},
                    {"topic_slug": "network-topologies", "question_count": 5, "difficulty": "BEGINNER"},
                    {"topic_slug": "lan", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "wan", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "client-server", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "peer-to-peer", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "network-media", "question_count": 2, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-OSI-001",
            "title": "OSI 7-Layer Reference Model",
            "slug": "osi-model",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 20,
            "total_questions": 20,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Assess your understanding of the 7-Layer OSI Reference Model, protocol data units (PDU), data encapsulation, decapsulation, and layer-by-layer troubleshooting methodologies.",
            "instructions": "Answer 20 multiple-choice questions within 20 minutes. 70% required to pass.",
            "prerequisites": "Basic understanding of computer networks.",
            "tags": ["osi", "encapsulation", "decapsulation", "pdu", "troubleshooting"],
            "what_you_will_practice": [
                "Map standard networking protocols to their correct OSI layers",
                "Track PDU transformations from Application down to Physical bits",
                "Diagnose network faults using top-down and bottom-up OSI troubleshooting",
                "Explain the distinct roles of transport, network, and data link layers"
            ],
            "blueprint": {
                "title": "OSI Reference Model Blueprint",
                "description": "Assesses knowledge of the seven OSI layers and encapsulation flow.",
                "topics": [
                    {"topic_slug": "seven-osi-layers", "question_count": 15, "difficulty": "BEGINNER"},
                    {"topic_slug": "encapsulation", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "decapsulation", "question_count": 1, "difficulty": "BEGINNER"},
                    {"topic_slug": "osi-troubleshooting", "question_count": 2, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-TCPIP-001",
            "title": "TCP/IP Protocol Suite Basics",
            "slug": "tcp-ip-basics",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 15,
            "total_questions": 15,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Evaluate your knowledge of the 4-layer TCP/IP protocol architecture, protocol comparison against the OSI stack, transport protocols, and fundamental packet framing.",
            "instructions": "Complete 15 questions in 15 minutes. 70% pass threshold.",
            "prerequisites": "OSI Model fundamentals.",
            "tags": ["tcp-ip", "osi-vs-tcp-ip", "protocols", "architecture"],
            "what_you_will_practice": [
                "Contrast the 4-layer TCP/IP model with the 7-layer OSI stack",
                "Identify protocols operating at the Network Access, Internet, Transport, and Application layers",
                "Understand how IP headers and TCP segments encapsulate application data"
            ],
            "blueprint": {
                "title": "TCP/IP Suite Blueprint",
                "description": "Evaluates understanding of the practical Internet TCP/IP stack.",
                "topics": [
                    {"topic_slug": "tcp-ip-layers", "question_count": 6, "difficulty": "BEGINNER"},
                    {"topic_slug": "osi-vs-tcp-ip", "question_count": 1, "difficulty": "BEGINNER"},
                    {"topic_slug": "encapsulation", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "tcp-basics", "question_count": 4, "difficulty": "BEGINNER"},
                    {"topic_slug": "udp-basics", "question_count": 2, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-DEVICES-001",
            "title": "Network Devices & Infrastructure",
            "slug": "network-devices",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 15,
            "total_questions": 15,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Test your knowledge of core networking hardware including Layer 2 switches, Layer 3 routers, default gateways, hubs, wireless access points, and boundary firewalls.",
            "instructions": "15 questions, 15 minutes. Minimum 70% passing score.",
            "prerequisites": "Basic understanding of networking communication.",
            "tags": ["router", "switch", "gateway", "hardware", "firewall"],
            "what_you_will_practice": [
                "Differentiate collision domains and broadcast domains across hubs, switches, and routers",
                "Explain the role of default gateways in routing traffic outside the local subnet",
                "Identify where firewalls and access points fit into network topologies"
            ],
            "blueprint": {
                "title": "Network Devices Blueprint",
                "description": "Assesses functional roles of hardware devices in enterprise infrastructure.",
                "topics": [
                    {"topic_slug": "network-devices", "question_count": 10, "difficulty": "BEGINNER"},
                    {"topic_slug": "default-gateway", "question_count": 3, "difficulty": "BEGINNER"},
                    {"topic_slug": "network-media", "question_count": 2, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-ETHERNET-001",
            "title": "Ethernet & MAC Addressing",
            "slug": "ethernet-and-mac",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 15,
            "total_questions": 12,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Examine your understanding of Layer 2 physical addressing, 48-bit MAC address structure (OUI vs NIC), unicast/multicast/broadcast addresses, and Address Resolution Protocol (ARP).",
            "instructions": "12 questions in 15 minutes.",
            "prerequisites": "OSI Layer 2 basics.",
            "tags": ["ethernet", "mac-address", "oui", "layer2", "arp"],
            "what_you_will_practice": [
                "Dissect 48-bit MAC address hex representations and the Organizationally Unique Identifier (OUI)",
                "Explain how Address Resolution Protocol (ARP) discovers Layer 2 addresses from IP addresses",
                "Differentiate unicast, broadcast, and multicast destination MAC addresses"
            ],
            "blueprint": {
                "title": "Ethernet & MAC Blueprint",
                "description": "Assesses Layer 2 addressing and frame transmission mechanics.",
                "topics": [
                    {"topic_slug": "mac-address", "question_count": 9, "difficulty": "BEGINNER"},
                    {"topic_slug": "arp", "question_count": 3, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-IPV4-001",
            "title": "IPv4 Addressing Fundamentals",
            "slug": "ipv4-basics",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 20,
            "total_questions": 20,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Test your mastery of 32-bit IPv4 address structure, dotted-decimal notation, legacy address classes (A, B, C), default subnet masks, and network vs host ID division.",
            "instructions": "20 questions, 20 minutes, 70% passing threshold.",
            "prerequisites": "Binary conversion and basic networking.",
            "tags": ["ipv4", "addressing", "classes", "subnet-mask", "layer3"],
            "what_you_will_practice": [
                "Calculate total addresses and octet boundaries in 32-bit IPv4",
                "Recognize legacy Class A, B, and C address ranges and default masks",
                "Distinguish network identifier bits from host identifier bits"
            ],
            "blueprint": {
                "title": "IPv4 Fundamentals Blueprint",
                "description": "Evaluates foundational Layer 3 logical addressing concepts.",
                "topics": [
                    {"topic_slug": "ipv4-basics", "question_count": 9, "difficulty": "BEGINNER"},
                    {"topic_slug": "ipv4-address-structure", "question_count": 6, "difficulty": "BEGINNER"},
                    {"topic_slug": "public-vs-private-ip", "question_count": 5, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-PRIV-PUB-IP-001",
            "title": "Public vs Private IP Addresses",
            "slug": "public-vs-private-ip",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 15,
            "total_questions": 12,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Verify your understanding of RFC 1918 private address ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16), globally routable public IPs, loopback (127.0.0.1), and APIPA (169.254.0.0/16).",
            "instructions": "12 questions, 15 minutes.",
            "prerequisites": "IPv4 address basics.",
            "tags": ["rfc1918", "private-ip", "public-ip", "loopback", "apipa"],
            "what_you_will_practice": [
                "Identify RFC 1918 private IPv4 blocks used in home and enterprise LANs",
                "Recognize loopback diagnostics (127.0.0.1) and APIPA auto-configuration",
                "Explain why private IP addresses cannot route across the public Internet without NAT"
            ],
            "blueprint": {
                "title": "Public vs Private IP Blueprint",
                "description": "Tests recognition and application of private and special-purpose IP ranges.",
                "topics": [
                    {"topic_slug": "public-vs-private-ip", "question_count": 7, "difficulty": "BEGINNER"},
                    {"topic_slug": "ipv4-basics", "question_count": 5, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-PORTS-001",
            "title": "Standard Ports & Protocols",
            "slug": "ports-and-protocols",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 20,
            "total_questions": 20,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Assess recall and understanding of IANA well-known ports (0-1023), registered ports, and essential application protocols including HTTP, HTTPS, SSH, FTP, DNS, and SMTP.",
            "instructions": "20 questions, 20 minutes.",
            "prerequisites": "Transport layer and client-server concepts.",
            "tags": ["ports", "protocols", "iana", "transport", "ssh", "http"],
            "what_you_will_practice": [
                "Recall standard port numbers (SSH:22, HTTP:80, HTTPS:443, DNS:53, DHCP:67/68)",
                "Differentiate well-known ports from dynamic ephemeral client ports",
                "Map common application protocols to their underlying transport mechanism (TCP vs UDP)"
            ],
            "blueprint": {
                "title": "Ports & Protocols Blueprint",
                "description": "Assesses familiarity with standard ports and foundational protocols.",
                "topics": [
                    {"topic_slug": "ports", "question_count": 15, "difficulty": "BEGINNER"},
                    {"topic_slug": "ports-and-sockets", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "http", "question_count": 3, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-DNS-001",
            "title": "DNS Fundamentals & Name Resolution",
            "slug": "dns-basics",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 20,
            "total_questions": 20,
            "passing_percentage": 70.0,
            "status": "DRAFT",
            "description": "Assess your understanding of the Domain Name System (DNS), hierarchical domain resolution, root nameservers, TLDs, and standard resource record types (A, AAAA, CNAME, MX).",
            "instructions": "20 questions, 20 minutes. Note: Currently in draft status while additional beginner DNS items are staged.",
            "prerequisites": "Ports and IP addressing.",
            "tags": ["dns", "name-resolution", "records", "udp53"],
            "what_you_will_practice": [
                "Trace recursive and iterative DNS resolution workflows",
                "Identify functions of A, AAAA, CNAME, and MX records",
                "Explain the role of DNS caching in web performance"
            ],
            "blueprint": {
                "title": "DNS Fundamentals Blueprint",
                "description": "Tests understanding of DNS hierarchy and record lookups.",
                "topics": [
                    {"topic_slug": "dns", "question_count": 20, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-DHCP-001",
            "title": "DHCP & Dynamic Host Configuration",
            "slug": "dhcp-basics",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 20,
            "total_questions": 20,
            "passing_percentage": 70.0,
            "status": "DRAFT",
            "description": "Examine the dynamic IP configuration process, DHCP DORA exchange (Discover, Offer, Request, Acknowledge), lease management, and DHCP scopes.",
            "instructions": "20 questions, 20 minutes. Currently in draft status.",
            "prerequisites": "LAN communication and IP basics.",
            "tags": ["dhcp", "dora", "ip-assignment", "leases"],
            "what_you_will_practice": [
                "Understand the 4-step DHCP DORA negotiation sequence",
                "Identify information delivered via DHCP (IP, subnet mask, gateway, DNS servers)",
                "Explain DHCP lease renewal and expiration"
            ],
            "blueprint": {
                "title": "DHCP Configuration Blueprint",
                "description": "Assesses dynamic IP assignment and lease maintenance.",
                "topics": [
                    {"topic_slug": "dhcp", "question_count": 20, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-TCP-UDP-001",
            "title": "TCP & UDP Transport Mechanics",
            "slug": "tcp-and-udp-basics",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 15,
            "total_questions": 10,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Compare connection-oriented TCP with connectionless UDP. Practice distinguishing reliability, flow control, overhead, and appropriate application use cases.",
            "instructions": "10 questions, 15 minutes. 70% passing threshold.",
            "prerequisites": "Transport layer fundamentals.",
            "tags": ["tcp", "udp", "connection-oriented", "reliability", "transport"],
            "what_you_will_practice": [
                "Contrast TCP reliability (sequencing, ACKs) with UDP low-latency streaming",
                "Match real-time applications (VoIP, video, DNS queries) with UDP",
                "Match file transfer and secure web protocols with TCP"
            ],
            "blueprint": {
                "title": "TCP & UDP Basics Blueprint",
                "description": "Contrasts transport protocols and operational characteristics.",
                "topics": [
                    {"topic_slug": "tcp-basics", "question_count": 4, "difficulty": "BEGINNER"},
                    {"topic_slug": "udp-basics", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "tcp-vs-udp", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "ports-and-sockets", "question_count": 2, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-HTTP-001",
            "title": "HTTP, HTTPS & Web Communication",
            "slug": "http-and-https-basics",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 15,
            "total_questions": 10,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Test your understanding of World Wide Web protocols, plaintext HTTP vs encrypted HTTPS, standard request methods (GET, POST), status code families, and TLS encryption.",
            "instructions": "10 questions, 15 minutes.",
            "prerequisites": "Client-server and port basics.",
            "tags": ["http", "https", "web", "tls", "status-codes"],
            "what_you_will_practice": [
                "Differentiate plaintext HTTP on port 80 from TLS-encrypted HTTPS on port 443",
                "Recognize common HTTP status codes (200 OK, 301 Redirect, 404 Not Found, 500 Error)",
                "Explain the security risks of transmitting sensitive credentials over unencrypted HTTP"
            ],
            "blueprint": {
                "title": "HTTP & HTTPS Basics Blueprint",
                "description": "Assesses web communication protocols and encryption requirements.",
                "topics": [
                    {"topic_slug": "http", "question_count": 3, "difficulty": "BEGINNER"},
                    {"topic_slug": "encryption", "question_count": 5, "difficulty": "BEGINNER"},
                    {"topic_slug": "common-network-threats", "question_count": 2, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-SECURITY-001",
            "title": "Basic Network Security & Threat Defense",
            "slug": "basic-network-security",
            "test_type": "TOPIC",
            "difficulty": "BEGINNER",
            "duration_minutes": 20,
            "total_questions": 20,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Assess foundational cybersecurity concepts including firewalls, encryption vs hashing, multi-factor authentication, malware transmission vectors, and common network attacks.",
            "instructions": "20 questions, 20 minutes.",
            "prerequisites": "Networking fundamentals.",
            "tags": ["security", "firewall", "encryption", "threats", "defense"],
            "what_you_will_practice": [
                "Understand the CIA triad (Confidentiality, Integrity, Availability)",
                "Identify common network attacks (man-in-the-middle, eavesdropping, spoofing)",
                "Explain the role of packet filtering firewalls in isolating untrusted networks"
            ],
            "blueprint": {
                "title": "Basic Network Security Blueprint",
                "description": "Tests foundational defensive cybersecurity principles.",
                "topics": [
                    {"topic_slug": "common-network-threats", "question_count": 10, "difficulty": "BEGINNER"},
                    {"topic_slug": "firewall-basics", "question_count": 6, "difficulty": "BEGINNER"},
                    {"topic_slug": "encryption", "question_count": 4, "difficulty": "BEGINNER"}
                ]
            }
        },
        {
            "code": "BEGINNER-COMPREHENSIVE-001",
            "title": "Beginner Comprehensive Networking Exam",
            "slug": "beginner-comprehensive-networking-test",
            "test_type": "COMPREHENSIVE",
            "difficulty": "BEGINNER",
            "duration_minutes": 30,
            "total_questions": 30,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "The definitive beginner assessment. Synthesizes knowledge across the entire beginner curriculum: fundamentals, OSI model, TCP/IP stack, devices, Ethernet, IPv4, ports, DNS, and basic security.",
            "instructions": "30 comprehensive questions in 30 minutes. Timed exam simulating CCNA / Network+ entry-level competency.",
            "prerequisites": "Completion of Beginner networking modules.",
            "tags": ["comprehensive", "beginner", "exam", "certification-prep", "ccna"],
            "what_you_will_practice": [
                "Holistic validation across all beginner computer networking domains",
                "Integrate OSI and TCP/IP models with real hardware and protocols",
                "Diagnose foundational connectivity failures and assess network security readiness"
            ],
            "blueprint": {
                "title": "Beginner Comprehensive Blueprint",
                "description": "Full-spectrum beginner examination covering all foundational networking topics.",
                "topics": [
                    {"topic_slug": "what-is-computer-networking", "question_count": 3, "difficulty": "BEGINNER"},
                    {"topic_slug": "seven-osi-layers", "question_count": 5, "difficulty": "BEGINNER"},
                    {"topic_slug": "tcp-ip-layers", "question_count": 3, "difficulty": "BEGINNER"},
                    {"topic_slug": "network-devices", "question_count": 3, "difficulty": "BEGINNER"},
                    {"topic_slug": "ipv4-basics", "question_count": 4, "difficulty": "BEGINNER"},
                    {"topic_slug": "ports", "question_count": 4, "difficulty": "BEGINNER"},
                    {"topic_slug": "dns", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "tcp-basics", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "common-network-threats", "question_count": 4, "difficulty": "BEGINNER"}
                ]
            }
        }
    ]


def get_intermediate_tests():
    return [
        {
            "code": "INTERMEDIATE-SUBNET-001",
            "title": "IPv4 Subnetting Mastery",
            "slug": "ipv4-and-subnetting",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 30,
            "total_questions": 25,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "A rigorous, calculation-driven exam evaluating your ability to determine network addresses, broadcast addresses, subnet masks, and usable host ranges for arbitrary CIDR prefixes.",
            "instructions": "25 questions in 30 minutes. Programmatically verified mathematical subnetting questions. Requires 75% or higher to pass.",
            "prerequisites": "IPv4 addressing and binary math fundamentals.",
            "tags": ["subnetting", "cidr", "network-address", "broadcast", "host-range"],
            "what_you_will_practice": [
                "Calculate valid host ranges and broadcast addresses for /24 through /30 subnets",
                "Identify which subnet an arbitrary host IP belongs to",
                "Determine required prefix lengths for specified departmental host counts"
            ],
            "blueprint": {
                "title": "Subnetting Mastery Blueprint",
                "description": "Calculates and verifies host ranges, broadcast addresses, and CIDR masks.",
                "topics": [
                    {"topic_slug": "subnetting", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "cidr", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "network-address", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "broadcast-address", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "host-range", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "subnet-masks", "question_count": 3, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-CIDR-001",
            "title": "CIDR & Variable Length Subnet Masking (VLSM)",
            "slug": "cidr-and-vlsm",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 25,
            "total_questions": 18,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Master Classless Inter-Domain Routing (CIDR) and Variable Length Subnet Masking (VLSM). Practice optimizing IP allocations across multi-tier networks without address wastage.",
            "instructions": "18 questions, 25 minutes. 75% pass mark.",
            "prerequisites": "IPv4 subnetting.",
            "tags": ["cidr", "vlsm", "route-aggregation", "efficiency"],
            "what_you_will_practice": [
                "Design VLSM hierarchical subnet plans minimizing address depletion",
                "Perform route summarization (supernetting) across contiguous CIDR blocks",
                "Allocate /30 and /31 point-to-point router transit links"
            ],
            "blueprint": {
                "title": "CIDR and VLSM Blueprint",
                "description": "Assesses hierarchical subnet planning and route summarization.",
                "topics": [
                    {"topic_slug": "cidr", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "vlsm", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "subnet-masks", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "host-range", "question_count": 6, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-TCP-UDP-001",
            "title": "TCP & UDP Transport Protocol Mechanics",
            "slug": "intermediate-tcp-and-udp",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 25,
            "total_questions": 25,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Deep dive into Layer 4 mechanics: TCP flags (SYN, ACK, FIN, RST, PSH, URG), sequence and acknowledgment number calculation, 3-way handshakes, 4-step teardowns, and socket states.",
            "instructions": "25 questions in 25 minutes. 75% passing threshold.",
            "prerequisites": "Transport layer basics.",
            "tags": ["tcp", "handshake", "flags", "sequence-numbers", "sockets"],
            "what_you_will_practice": [
                "Track sequence and acknowledgment number increments across TCP sessions",
                "Identify control flags set in connection establishment, data flow, and resets",
                "Analyze TCP state transitions: SYN_SENT, ESTABLISHED, FIN_WAIT, and TIME_WAIT"
            ],
            "blueprint": {
                "title": "TCP Protocol Mechanics Blueprint",
                "description": "Detailed evaluation of transport layer connection state and flow control.",
                "topics": [
                    {"topic_slug": "tcp-basics", "question_count": 10, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "tcp-three-way-handshake", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "tcp-flags", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "tcp-connection-termination", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "udp-communication", "question_count": 3, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-DNS-DHCP-001",
            "title": "DNS & DHCP Network Services",
            "slug": "dns-and-dhcp-services",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 20,
            "total_questions": 14,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Assess core infrastructure network services. Covers recursive DNS resolution, zone transfer concepts, authoritativeness, DHCP relay agents, and lease option configuration.",
            "instructions": "14 questions in 20 minutes.",
            "prerequisites": "Application layer and IP configuration.",
            "tags": ["dns", "dhcp", "services", "dora", "relay-agent"],
            "what_you_will_practice": [
                "Analyze recursive vs iterative DNS resolution workflows",
                "Understand DHCP Relay Agent (IP Helper) mechanics across subnets",
                "Interpret nslookup and dig query diagnostics"
            ],
            "blueprint": {
                "title": "DNS & DHCP Services Blueprint",
                "description": "Evaluates enterprise domain resolution and automated host configuration.",
                "topics": [
                    {"topic_slug": "dns-resolution", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "dns-record-types", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "dhcp-process", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "nslookup-dig-concepts", "question_count": 2, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-WEB-001",
            "title": "HTTP, HTTPS & TLS Encryption",
            "slug": "http-https-and-tls",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 20,
            "total_questions": 15,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Test understanding of web application transport: HTTP/1.1 vs HTTP/2, idempotent methods (GET, PUT, DELETE), header analysis, TLS cryptographic handshakes, and certificate verification.",
            "instructions": "15 questions, 20 minutes.",
            "prerequisites": "Application layer and basic security.",
            "tags": ["http", "https", "tls", "certificates", "crypto"],
            "what_you_will_practice": [
                "Explain the TLS handshake: ClientHello, ServerHello, and key exchange",
                "Identify safe and idempotent HTTP request methods",
                "Understand PKI certificate authorities and digital signature validation"
            ],
            "blueprint": {
                "title": "HTTP and TLS Security Blueprint",
                "description": "Assesses web protocols and transport layer cryptographic security.",
                "topics": [
                    {"topic_slug": "http-methods", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "http-status-codes", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "https-intermediate", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "tls-basics", "question_count": 5, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-ROUTING-001",
            "title": "Routing Principles & Protocol Concepts",
            "slug": "routing-fundamentals",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 20,
            "total_questions": 15,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Evaluate routing logic: longest prefix match, administrative distance, metric calculation, static vs dynamic routing, default routes (0.0.0.0/0), and link-state vs distance-vector.",
            "instructions": "15 questions, 20 minutes.",
            "prerequisites": "IPv4 subnetting and Layer 3 basics.",
            "tags": ["routing", "static-routing", "dynamic-routing", "longest-prefix-match"],
            "what_you_will_practice": [
                "Perform routing table lookups using the Longest Prefix Match rule",
                "Compare Administrative Distance between Static, OSPF, and EIGRP routes",
                "Configure default gateway static routes (0.0.0.0/0)"
            ],
            "blueprint": {
                "title": "Routing Fundamentals Blueprint",
                "description": "Tests packet forwarding decisions and routing table analysis.",
                "topics": [
                    {"topic_slug": "routing", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "static-routing", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "dynamic-routing-concepts", "question_count": 6, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "default-routes", "question_count": 2, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-SWITCHING-001",
            "title": "Switching Mechanics & MAC Learning",
            "slug": "switching-and-mac-tables",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 20,
            "total_questions": 15,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Assess Layer 2 switch forwarding operations: MAC address table aging and learning, unknown unicast flooding, broadcast forwarding, and basic loop prevention.",
            "instructions": "15 questions in 20 minutes.",
            "prerequisites": "Ethernet and MAC addressing.",
            "tags": ["switching", "mac-table", "flooding", "layer2", "cams"],
            "what_you_will_practice": [
                "Track how a switch populates its CAM/MAC address table from ingress source MACs",
                "Analyze switch behavior when handling unknown unicast vs broadcast frames",
                "Understand why Layer 2 forwarding loops cause catastrophic broadcast storms"
            ],
            "blueprint": {
                "title": "Switching Mechanics Blueprint",
                "description": "Evaluates switch frame processing and forwarding table operations.",
                "topics": [
                    {"topic_slug": "switching", "question_count": 10, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "mac-address-table", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "trunking", "question_count": 2, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-VLAN-001",
            "title": "VLAN Segmentation & Trunking",
            "slug": "vlan-and-trunking",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 15,
            "total_questions": 10,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Test your mastery of Virtual Local Area Networks (VLANs), IEEE 802.1Q trunk tagging, native VLANs, access ports, and inter-VLAN routing (Router-on-a-Stick).",
            "instructions": "10 questions, 15 minutes.",
            "prerequisites": "Switching mechanics.",
            "tags": ["vlan", "802.1q", "trunking", "segmentation", "native-vlan"],
            "what_you_will_practice": [
                "Explain the role of IEEE 802.1Q tags in multiplexing VLAN traffic across trunks",
                "Differentiate access ports from trunk ports on enterprise switches",
                "Identify security risks associated with the default native VLAN 1"
            ],
            "blueprint": {
                "title": "VLAN Architecture Blueprint",
                "description": "Assesses broadcast segmentation and multi-switch trunking.",
                "topics": [
                    {"topic_slug": "vlan", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "trunking", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "switching", "question_count": 3, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-ARP-ICMP-001",
            "title": "ARP & ICMP Diagnostic Protocols",
            "slug": "arp-and-icmp-protocols",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 15,
            "total_questions": 10,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Evaluate protocols that enable IP connectivity and diagnostic tools: ARP request/reply cycles, gratuitous ARP, ICMP Echo Request/Reply (Type 8/0), and Time Exceeded (Type 11).",
            "instructions": "10 questions, 15 minutes.",
            "prerequisites": "IPv4 and Layer 2.",
            "tags": ["arp", "icmp", "ping", "traceroute", "diagnostics"],
            "what_you_will_practice": [
                "Analyze ICMP message types used by ping and traceroute",
                "Understand the security implications of unauthenticated ARP broadcasts",
                "Diagnose host-unreachable vs timeout response codes"
            ],
            "blueprint": {
                "title": "ARP and ICMP Blueprint",
                "description": "Tests connectivity resolution and control message diagnostics.",
                "topics": [
                    {"topic_slug": "ping", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "traceroute", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "arp", "question_count": 1, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "netstat-ss", "question_count": 2, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-NAT-001",
            "title": "NAT & Port Address Translation (PAT)",
            "slug": "network-address-translation",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 15,
            "total_questions": 8,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Assess Network Address Translation (RFC 1631): Static 1:1 NAT, Dynamic Pool NAT, and Port Address Translation (PAT / NAT Overload) using Layer 4 source port multiplexing.",
            "instructions": "8 questions, 15 minutes.",
            "prerequisites": "Public vs Private IP addresses.",
            "tags": ["nat", "pat", "nat-overload", "translation", "firewall"],
            "what_you_will_practice": [
                "Differentiate Static NAT, Dynamic NAT, and PAT (NAT Overload)",
                "Explain how PAT tracks state to map many private IPs to one public IP",
                "Identify when port forwarding (destination NAT) is required for inbound hosting"
            ],
            "blueprint": {
                "title": "NAT and PAT Blueprint",
                "description": "Assesses address translation mechanics and state tracking.",
                "topics": [
                    {"topic_slug": "nat", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "nat-security", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "network-segmentation", "question_count": 2, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-TROUBLESHOOT-001",
            "title": "Network Troubleshooting & CLI Tools",
            "slug": "network-troubleshooting",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 20,
            "total_questions": 15,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Scenario-driven network diagnostic examination: isolate failures across physical, link, IP, and DNS layers using ping, traceroute, ipconfig/ifconfig, netstat/ss, and dig.",
            "instructions": "15 questions, 20 minutes.",
            "prerequisites": "Networking tools and protocol knowledge.",
            "tags": ["troubleshooting", "cli", "ping", "traceroute", "netstat", "dig"],
            "what_you_will_practice": [
                "Differentiate DNS failures from Layer 3 IP routing failures",
                "Analyze traceroute hop asterisks and identify upstream drop points",
                "Use netstat/ss to determine active listening ports and established sockets"
            ],
            "blueprint": {
                "title": "Network Troubleshooting Blueprint",
                "description": "Tests systematic fault isolation using command-line diagnostic tools.",
                "topics": [
                    {"topic_slug": "ping", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "traceroute", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "netstat-ss", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "nslookup-dig-concepts", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "routing", "question_count": 3, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-SECURITY-001",
            "title": "Intermediate Network Defense & ACLs",
            "slug": "network-security",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 20,
            "total_questions": 14,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Evaluate Access Control List (ACL) rule processing, top-to-bottom matching, implicit deny, stateful vs stateless filtering, and network microsegmentation principles.",
            "instructions": "14 questions, 20 minutes.",
            "prerequisites": "Basic security and transport ports.",
            "tags": ["acl", "firewall", "security", "segmentation", "defense"],
            "what_you_will_practice": [
                "Analyze firewall ACL top-down rule ordering and identify shadow rules",
                "Explain the role of the implicit deny at the end of access lists",
                "Contrast stateful connection tracking with stateless packet filters"
            ],
            "blueprint": {
                "title": "Network Security and ACL Blueprint",
                "description": "Assesses access filtering, stateful tracking, and segmentation.",
                "topics": [
                    {"topic_slug": "firewall-rules", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "firewall-basics", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "network-segmentation", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "stateful-vs-stateless-filtering", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "ids", "question_count": 1, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "ips", "question_count": 1, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-FIREWALLS-001",
            "title": "Firewalls & Rule Evaluation",
            "slug": "firewalls",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 15,
            "total_questions": 10,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Detailed examination of firewall architectures, state table inspection, egress filtering policies, and Layer 7 Web Application Firewalls (WAF).",
            "instructions": "10 questions, 15 minutes.",
            "prerequisites": "Firewall and port fundamentals.",
            "tags": ["firewall", "state-table", "egress-filtering", "rules"],
            "what_you_will_practice": [
                "Analyze state table entry creation and teardown for TCP/UDP",
                "Understand why egress filtering is critical to prevent malware C2 beaconing",
                "Contrast Layer 4 packet filters with Layer 7 application inspection"
            ],
            "blueprint": {
                "title": "Firewall Rule Evaluation Blueprint",
                "description": "Tests firewall policy design and packet filtering behavior.",
                "topics": [
                    {"topic_slug": "firewall-rules", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "firewall-basics", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "stateful-vs-stateless-filtering", "question_count": 2, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-IDS-001",
            "title": "IDS & IPS Intrusion Detection",
            "slug": "ids-ips",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 25,
            "total_questions": 20,
            "passing_percentage": 70.0,
            "status": "DRAFT",
            "description": "Assess intrusion detection (NIDS) vs intrusion prevention (NIPS), inline vs span/tap deployment, signature-based detection, and false positive tuning.",
            "instructions": "20 questions, 25 minutes. Note: Currently in draft status pending intermediate sensor question staging.",
            "prerequisites": "Network security basics.",
            "tags": ["ids", "ips", "nids", "suricata", "snort"],
            "what_you_will_practice": [
                "Differentiate out-of-band monitoring (SPAN/TAP) from inline blocking (IPS)",
                "Identify signature vs anomaly behavioral detection techniques"
            ],
            "blueprint": {
                "title": "IDS and IPS Fundamentals Blueprint",
                "description": "Tests intrusion detection architecture and deployment modes.",
                "topics": [
                    {"topic_slug": "ids-ips-advanced", "question_count": 20, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-PACKET-001",
            "title": "Packet Analysis Fundamentals",
            "slug": "packet-analysis-fundamentals",
            "test_type": "TOPIC",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 25,
            "total_questions": 20,
            "passing_percentage": 70.0,
            "status": "DRAFT",
            "description": "Introduction to packet dissection, Wireshark capture display filters, and protocol field identification.",
            "instructions": "20 questions, 25 minutes. Currently in draft status.",
            "prerequisites": "Protocol and packet basics.",
            "tags": ["pcap", "wireshark", "packets", "filters"],
            "what_you_will_practice": [
                "Construct Wireshark display filters by IP, port, and protocol",
                "Dissect Ethernet frame and IPv4 packet header fields"
            ],
            "blueprint": {
                "title": "Packet Analysis Fundamentals Blueprint",
                "description": "Tests packet header extraction and filter authoring.",
                "topics": [
                    {"topic_slug": "wireshark-filtering-concepts", "question_count": 20, "difficulty": "INTERMEDIATE"}
                ]
            }
        },
        {
            "code": "INTERMEDIATE-COMPREHENSIVE-001",
            "title": "Intermediate Comprehensive Networking Exam",
            "slug": "intermediate-comprehensive",
            "test_type": "COMPREHENSIVE",
            "difficulty": "INTERMEDIATE",
            "duration_minutes": 40,
            "total_questions": 35,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "A comprehensive examination covering the full Intermediate syllabus: advanced subnetting, TCP/UDP states, VLANs, static/dynamic routing, NAT, firewall filtering, and diagnostic CLI tools.",
            "instructions": "35 questions in 40 minutes. Simulates associate-level networking certification examinations (CCNA / Network+).",
            "prerequisites": "Completion of all Intermediate learning modules.",
            "tags": ["comprehensive", "intermediate", "certification-prep", "ccna", "exam"],
            "what_you_will_practice": [
                "Synthesize subnet calculations with practical routing and switching scenarios",
                "Analyze protocol handshakes, transport flags, and socket lifecycles",
                "Diagnose multi-hop network outages and evaluate security boundary rules"
            ],
            "blueprint": {
                "title": "Intermediate Comprehensive Blueprint",
                "description": "Full-spectrum assessment across all intermediate networking domains.",
                "topics": [
                    {"topic_slug": "subnetting", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "network-address", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "tcp-basics", "question_count": 5, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "tcp-flags", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "switching", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "routing", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "nat", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "firewall-rules", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "ping", "question_count": 2, "difficulty": "INTERMEDIATE"}
                ]
            }
        }
    ]


def get_advanced_tests():
    return [
        {
            "code": "ADVANCED-TCPIP-001",
            "title": "Advanced TCP/IP & Protocol Forensics",
            "slug": "advanced-tcp-ip",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 25,
            "total_questions": 20,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Dissect advanced TCP/IP behaviors: TCP Zero Window probes, Selective Acknowledgment (SACK), sliding window scaling, out-of-order retransmissions, and anomalous flag combinations.",
            "instructions": "20 questions, 25 minutes. Deep protocol analysis.",
            "prerequisites": "Intermediate TCP/UDP mechanics.",
            "tags": ["tcp", "window-size", "sack", "pcap", "forensics"],
            "what_you_will_practice": [
                "Diagnose application deadlocks from TCP Zero Window conditions",
                "Calculate sliding window throughput from TCP Window Scale options",
                "Analyze anomalous TCP flag combinations in transit captures"
            ],
            "blueprint": {
                "title": "Advanced TCP/IP Blueprint",
                "description": "Assesses deep transport layer mechanics and windowing operations.",
                "topics": [
                    {"topic_slug": "packet-structure", "question_count": 8, "difficulty": "ADVANCED"},
                    {"topic_slug": "tcp-stream-analysis", "question_count": 6, "difficulty": "ADVANCED"},
                    {"topic_slug": "wireshark-filtering-concepts", "question_count": 6, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-SUBNET-001",
            "title": "Advanced Subnetting & Carrier Routing",
            "slug": "advanced-subnetting",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 35,
            "total_questions": 25,
            "passing_percentage": 75.0,
            "status": "DRAFT",
            "description": "Carrier-scale IP address planning, multi-protocol BGP aggregation, and complex enterprise IPv6 transition planning.",
            "instructions": "25 questions in 35 minutes. Note: Currently in draft status.",
            "prerequisites": "Intermediate VLSM.",
            "tags": ["subnetting", "bgp", "ipv6", "supernetting"],
            "what_you_will_practice": [
                "Perform carrier-grade address allocation and summarization"
            ],
            "blueprint": {
                "title": "Advanced Subnetting Blueprint",
                "description": "Assesses carrier-grade routing and aggregation.",
                "topics": [
                    {"topic_slug": "ipv6-security", "question_count": 25, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-ROUTING-SWITCHING-001",
            "title": "Routing & Switching Security Analysis",
            "slug": "routing-and-switching-analysis",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 30,
            "total_questions": 25,
            "passing_percentage": 75.0,
            "status": "DRAFT",
            "description": "Analyze Layer 2 switch attacks (MAC flooding, VLAN hopping, STP manipulation) and Layer 3 routing protocol attacks (BGP route leaks, rogue OSPF LSAs).",
            "instructions": "25 questions in 30 minutes. Note: Currently in draft status (requires 25, available 12).",
            "prerequisites": "Enterprise switching and dynamic routing.",
            "tags": ["layer2-attacks", "bgp-hijacking", "vlan-hopping", "stp"],
            "what_you_will_practice": [
                "Neutralize VLAN hopping and switch spoofing attacks",
                "Implement Private VLANs (PVLAN) to isolate compromised hosts",
                "Analyze BGP hijacking and RPKI route origin validation"
            ],
            "blueprint": {
                "title": "Routing and Switching Security Blueprint",
                "description": "Assesses protocol exploitation and hardening at Layers 2 and 3.",
                "topics": [
                    {"topic_slug": "vlan-security", "question_count": 15, "difficulty": "ADVANCED"},
                    {"topic_slug": "network-segmentation-advanced", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "routing-protocol-concepts", "question_count": 5, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-SEC-DEFENSE-001",
            "title": "Advanced Network Security & Defense Architecture",
            "slug": "advanced-network-security",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 25,
            "total_questions": 20,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Enterprise defensive architecture: Private VLAN (PVLAN) isolated and promiscuous ports, stateful TCP state exhaustion attacks, Dynamic ARP Inspection (DAI), and Jump Box bastion design.",
            "instructions": "20 questions, 25 minutes. 75% pass mark.",
            "prerequisites": "Intermediate network security.",
            "tags": ["defense", "pvlan", "dai", "bastion", "hardening", "ngfw"],
            "what_you_will_practice": [
                "Implement Private VLAN isolated vs community port boundaries",
                "Deploy Dynamic ARP Inspection (DAI) and DHCP Snooping against spoofing",
                "Architect Next-Generation Firewall (NGFW) deep packet inspection zones"
            ],
            "blueprint": {
                "title": "Advanced Network Defense Blueprint",
                "description": "Tests enterprise microsegmentation and L2/L3 security architecture.",
                "topics": [
                    {"topic_slug": "vlan-security", "question_count": 7, "difficulty": "ADVANCED"},
                    {"topic_slug": "stateful-vs-stateless-filtering", "question_count": 4, "difficulty": "ADVANCED"},
                    {"topic_slug": "firewall-architecture", "question_count": 4, "difficulty": "ADVANCED"},
                    {"topic_slug": "ids-ips-advanced", "question_count": 5, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-PCAP-001",
            "title": "Packet Analysis & Wireshark Stream Forensics",
            "slug": "packet-analysis",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 30,
            "total_questions": 25,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Authentic packet forensic investigation: Dissect hex dumps, Ethernet frame byte alignments, IPv4 TTL decrementing, TCP reassembly streams, and complex Wireshark display filters.",
            "instructions": "25 questions in 30 minutes. 75% required to pass.",
            "prerequisites": "Intermediate packet analysis.",
            "tags": ["wireshark", "pcap", "hex-dump", "forensics", "packet-dissection"],
            "what_you_will_practice": [
                "Dissect raw Ethernet and IP byte offsets in packet capture dumps",
                "Reconstruct full TCP data streams from bidirectional conversations",
                "Craft complex Wireshark display filters combining protocols and byte slices"
            ],
            "blueprint": {
                "title": "Packet Forensics Blueprint",
                "description": "Assesses PCAP dissection and Wireshark stream forensic analysis.",
                "topics": [
                    {"topic_slug": "packet-structure", "question_count": 11, "difficulty": "ADVANCED"},
                    {"topic_slug": "wireshark-filtering-concepts", "question_count": 7, "difficulty": "ADVANCED"},
                    {"topic_slug": "tcp-stream-analysis", "question_count": 7, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-TRAFFIC-001",
            "title": "Traffic Analysis & Network Baselining",
            "slug": "traffic-analysis",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 20,
            "total_questions": 15,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Analyze network baselines, anomalous traffic volume spikes, DNS tunneling exfiltration patterns, HTTP user-agent anomalies, and TLS SNI discrepancy indicators.",
            "instructions": "15 questions, 20 minutes.",
            "prerequisites": "Packet analysis and application protocols.",
            "tags": ["traffic-analysis", "baselining", "dns-tunneling", "anomalies", "sni"],
            "what_you_will_practice": [
                "Detect DNS tunneling and data exfiltration from anomalous query lengths",
                "Identify TLS Server Name Indication (SNI) spoofing and domain fronting",
                "Recognize periodic C2 beaconing rhythms and jitter patterns"
            ],
            "blueprint": {
                "title": "Traffic Baselining Blueprint",
                "description": "Evaluates detection of statistical and protocol traffic anomalies.",
                "topics": [
                    {"topic_slug": "network-monitoring", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "dns-packet-analysis", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "http-packet-analysis", "question_count": 3, "difficulty": "ADVANCED"},
                    {"topic_slug": "tls-traffic", "question_count": 2, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-IDS-IPS-001",
            "title": "IDS / IPS Analysis & Evasion Techniques",
            "slug": "ids-ips-analysis",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 20,
            "total_questions": 15,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Evaluate deep NIDS/NIPS operations: Snort/Suricata rule syntax, content modifiers (fast_pattern, distance, within), packet fragmentation evasion, and false positive reduction.",
            "instructions": "15 questions in 20 minutes.",
            "prerequisites": "IDS/IPS fundamentals.",
            "tags": ["ids", "ips", "snort", "suricata", "evasion", "signatures"],
            "what_you_will_practice": [
                "Dissect Snort/Suricata rule options and payload pattern matching",
                "Detect IP fragmentation overlap attacks used to evade sensor reassembly",
                "Tune rule thresholds to eliminate benign operational false positives"
            ],
            "blueprint": {
                "title": "IDS and IPS Evasion Blueprint",
                "description": "Assesses signature evaluation, payload inspection, and evasion countermeasures.",
                "topics": [
                    {"topic_slug": "ids-ips-advanced", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "detection-rules", "question_count": 6, "difficulty": "ADVANCED"},
                    {"topic_slug": "detection-tuning", "question_count": 4, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-DETECTION-001",
            "title": "Network Detection Engineering",
            "slug": "network-detection",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 25,
            "total_questions": 20,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Design and author high-fidelity detection rules: Snort alert headers, regular expressions, byte-test offsets, flowbit state tracking, and alert lifecycle management.",
            "instructions": "20 questions, 25 minutes. 75% pass threshold.",
            "prerequisites": "Snort/Suricata syntax and regex.",
            "tags": ["detection-engineering", "snort", "rules", "flowbits", "signatures"],
            "what_you_will_practice": [
                "Author multi-packet stateful detection rules using flowbits",
                "Utilize depth, offset, and within modifiers for precise binary matching",
                "Tune detection logic to maintain high signal-to-noise ratios"
            ],
            "blueprint": {
                "title": "Detection Engineering Blueprint",
                "description": "Tests authoring and optimization of network detection signatures.",
                "topics": [
                    {"topic_slug": "detection-rules", "question_count": 9, "difficulty": "ADVANCED"},
                    {"topic_slug": "detection-tuning", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "indicators-of-compromise", "question_count": 4, "difficulty": "ADVANCED"},
                    {"topic_slug": "false-positives", "question_count": 2, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-IOC-001",
            "title": "Network Indicators & Telemetry Corroboration",
            "slug": "detection-engineering",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 25,
            "total_questions": 20,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Corroborate Indicators of Compromise (IoCs): JA3/JA3S TLS client hashes, HTTP URI patterns, anomalous beacon intervals, and threat intelligence matching against network flow logs.",
            "instructions": "20 questions, 25 minutes.",
            "prerequisites": "Threat intelligence and telemetry logs.",
            "tags": ["ioc", "ja3", "c2", "threat-intel", "telemetry"],
            "what_you_will_practice": [
                "Fingerprint malicious TLS client tools using JA3/JA3S hashes",
                "Identify C2 beacon intervals from proxy access logs",
                "Correlate firewall flow records with known malicious IP reputations"
            ],
            "blueprint": {
                "title": "Network Indicators Blueprint",
                "description": "Assesses identification and validation of network compromise indicators.",
                "topics": [
                    {"topic_slug": "network-indicators", "question_count": 12, "difficulty": "ADVANCED"},
                    {"topic_slug": "indicators-of-compromise", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "alert-creation", "question_count": 3, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-RECON-001",
            "title": "Network Reconnaissance & Port Scan Detection",
            "slug": "network-reconnaissance-detection",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 30,
            "total_questions": 25,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Detect and analyze offensive network reconnaissance: TCP SYN stealth scans, TCP FIN scans, Xmas scans, Null scans, UDP sweeps, idle zombie scans, and OS fingerprinting probes.",
            "instructions": "25 questions in 30 minutes. 75% required to pass.",
            "prerequisites": "TCP flag mechanics and port scanning theory.",
            "tags": ["reconnaissance", "nmap", "syn-scan", "xmas-scan", "fingerprinting"],
            "what_you_will_practice": [
                "Differentiate full-connect (TCP connect) scans from SYN half-open scans",
                "Explain RFC 793 closed-port RST behavior utilized in FIN, Null, and Xmas scans",
                "Detect OS fingerprinting attempts probing TCP options and initial window sizes"
            ],
            "blueprint": {
                "title": "Reconnaissance Detection Blueprint",
                "description": "Evaluates detection and signature matching of adversary port scans.",
                "topics": [
                    {"topic_slug": "reconnaissance-detection", "question_count": 11, "difficulty": "ADVANCED"},
                    {"topic_slug": "port-scanning-concepts", "question_count": 7, "difficulty": "ADVANCED"},
                    {"topic_slug": "service-enumeration-concepts", "question_count": 7, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-INCIDENT-001",
            "title": "Incident Investigation & Network Evidence",
            "slug": "incident-investigation",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 25,
            "total_questions": 20,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Perform forensic network incident investigation: reconstruct attacker lateral movement, establish attack timelines, preserve volatile network evidence, and document chain of custody.",
            "instructions": "20 questions, 25 minutes.",
            "prerequisites": "Packet analysis and incident handling fundamentals.",
            "tags": ["incident-response", "forensics", "timeline", "evidence", "lateral-movement"],
            "what_you_will_practice": [
                "Reconstruct multi-stage attack timelines from network connection records",
                "Identify lateral movement protocols (SMB, RPC, SSH) across internal zones",
                "Ensure cryptographic hashing and chain of custody preservation for PCAP evidence"
            ],
            "blueprint": {
                "title": "Incident Investigation Blueprint",
                "description": "Tests forensic reconstruction of network intrusion events.",
                "topics": [
                    {"topic_slug": "network-investigation", "question_count": 10, "difficulty": "ADVANCED"},
                    {"topic_slug": "evidence-collection", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "timeline-analysis", "question_count": 5, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-SOC-001",
            "title": "SOC Network Analysis & Alert Triage",
            "slug": "soc-network-analysis",
            "test_type": "TOPIC",
            "difficulty": "ADVANCED",
            "duration_minutes": 25,
            "total_questions": 20,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "Step into the role of a Tier-1/Tier-2 Security Operations Center (SOC) analyst: triage incoming SIEM alerts, differentiate True Positives from False Positives, and determine escalation priorities.",
            "instructions": "20 questions in 25 minutes. Simulates enterprise SOC triage drills.",
            "prerequisites": "Network security and log analysis.",
            "tags": ["soc", "alert-triage", "siem", "true-positive", "escalation"],
            "what_you_will_practice": [
                "Evaluate alert severity and prioritize critical incident responses",
                "Validate whether network alerts represent genuine intrusions or benign business traffic",
                "Execute initial host containment steps to isolate compromised endpoints"
            ],
            "blueprint": {
                "title": "SOC Alert Triage Blueprint",
                "description": "Assesses operational triage and incident escalation workflows.",
                "topics": [
                    {"topic_slug": "alert-triage", "question_count": 7, "difficulty": "ADVANCED"},
                    {"topic_slug": "network-investigation", "question_count": 10, "difficulty": "ADVANCED"},
                    {"topic_slug": "incident-classification", "question_count": 3, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "ADVANCED-COMPREHENSIVE-001",
            "title": "Advanced Comprehensive Cyber Defense Exam",
            "slug": "advanced-comprehensive",
            "test_type": "COMPREHENSIVE",
            "difficulty": "ADVANCED",
            "duration_minutes": 45,
            "total_questions": 35,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "The capstone advanced defensive examination. Tests comprehensive mastery across packet dissection, reconnaissance detection, Snort rule writing, indicator corroboration, and SOC incident triage.",
            "instructions": "35 questions in 45 minutes. Advanced practical cyber defense examination.",
            "prerequisites": "Completion of all Advanced learning modules.",
            "tags": ["comprehensive", "advanced", "cyber-defense", "soc", "packet-forensics"],
            "what_you_will_practice": [
                "Synthesize packet forensic skills with enterprise intrusion detection",
                "Evaluate multi-stage cyber attacks and coordinate defensive countermeasures",
                "Corroborate telemetry across switches, firewalls, and endpoint sensors"
            ],
            "blueprint": {
                "title": "Advanced Cyber Defense Blueprint",
                "description": "Full-spectrum advanced assessment across packet forensics and SOC analysis.",
                "topics": [
                    {"topic_slug": "reconnaissance-detection", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "packet-structure", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "detection-rules", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "network-indicators", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "alert-triage", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "evidence-collection", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "vlan-security", "question_count": 5, "difficulty": "ADVANCED"}
                ]
            }
        }
    ]


def get_full_mocks():
    return [
        {
            "code": "FULL-MOCK-001",
            "title": "Full Networking Mock Exam",
            "slug": "full-networking-mock-exam",
            "test_type": "FULL_MOCK",
            "difficulty": "MIXED",
            "duration_minutes": 60,
            "total_questions": 50,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Full-length 50-question mock examination simulating industrial networking certification tests (Cisco CCNA 200-301 / CompTIA Network+ N10-008). Balanced across Beginner, Intermediate, and Advanced networking domains.",
            "instructions": "50 questions, 60 minutes. Timed exam simulating official certification conditions. 70% passing score.",
            "prerequisites": "Broad knowledge of computer networking from foundational frames to dynamic routing.",
            "tags": ["full-mock", "ccna", "network-plus", "certification", "exam", "mixed"],
            "what_you_will_practice": [
                "Full certification simulation under authentic 60-minute time constraints",
                "Cross-tier synthesis from physical Ethernet frames to application HTTP/TLS",
                "Diagnostic subnetting, routing lookups, switching tables, and protocol troubleshooting"
            ],
            "blueprint": {
                "title": "Full Networking Mock Blueprint",
                "description": "50-question multi-tier blueprint assessing comprehensive networking competency.",
                "topics": [
                    {"topic_slug": "what-is-computer-networking", "question_count": 3, "difficulty": "BEGINNER"},
                    {"topic_slug": "seven-osi-layers", "question_count": 4, "difficulty": "BEGINNER"},
                    {"topic_slug": "ipv4-basics", "question_count": 4, "difficulty": "BEGINNER"},
                    {"topic_slug": "network-devices", "question_count": 4, "difficulty": "BEGINNER"},
                    {"topic_slug": "subnetting", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "network-address", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "tcp-basics", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "tcp-flags", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "switching", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "routing", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "nat", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "firewall-rules", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "ping", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "packet-structure", "question_count": 3, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "FULL-MOCK-002",
            "title": "Full Networking Security Mock Exam",
            "slug": "full-networking-security-mock-exam",
            "test_type": "FULL_MOCK",
            "difficulty": "MIXED",
            "duration_minutes": 60,
            "total_questions": 50,
            "passing_percentage": 70.0,
            "status": "PUBLISHED",
            "description": "Full-length 50-question examination focusing on defensive cybersecurity, packet forensics, and intrusion detection (simulating CompTIA Security+ / Cisco CyberOps Associate).",
            "instructions": "50 questions, 60 minutes. Timed defensive examination. 70% passing threshold.",
            "prerequisites": "Solid networking foundations and security concepts.",
            "tags": ["full-mock", "security-plus", "cyberops", "soc", "defense", "exam"],
            "what_you_will_practice": [
                "Full-scope cyber defense examination testing defensive posture from L2 up to L7",
                "Analyze adversary reconnaissance scans, port probes, and evasion patterns",
                "Evaluate NIDS/NIPS rules, IOC telemetry, and SOC incident containment steps"
            ],
            "blueprint": {
                "title": "Full Network Security Blueprint",
                "description": "50-question blueprint assessing comprehensive defensive network security.",
                "topics": [
                    {"topic_slug": "common-network-threats", "question_count": 5, "difficulty": "BEGINNER"},
                    {"topic_slug": "encryption", "question_count": 3, "difficulty": "BEGINNER"},
                    {"topic_slug": "firewall-basics", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "firewall-rules", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "network-segmentation", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "stateful-vs-stateless-filtering", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "vlan-security", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "packet-structure", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "reconnaissance-detection", "question_count": 6, "difficulty": "ADVANCED"},
                    {"topic_slug": "detection-rules", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "network-indicators", "question_count": 5, "difficulty": "ADVANCED"},
                    {"topic_slug": "alert-triage", "question_count": 6, "difficulty": "ADVANCED"}
                ]
            }
        },
        {
            "code": "FULL-MOCK-003",
            "title": "Full Networking + Security Comprehensive Exam",
            "slug": "full-networking-security-comprehensive-exam",
            "test_type": "FULL_MOCK",
            "difficulty": "MIXED",
            "duration_minutes": 75,
            "total_questions": 60,
            "passing_percentage": 75.0,
            "status": "PUBLISHED",
            "description": "The flagship NexoraNet capstone examination. 60 questions covering the entire computer networking and cyber defense curriculum. Designed to evaluate comprehensive mastery across theory, hands-on diagnostics, packet forensics, and SOC operations.",
            "instructions": "60 questions, 75 minutes. Flagship comprehensive examination. 75% required to pass.",
            "prerequisites": "Completion of all Beginner, Intermediate, and Advanced networking and security tracks.",
            "tags": ["capstone", "full-mock", "flagship", "comprehensive", "mastery"],
            "what_you_will_practice": [
                "Rigorous end-to-end evaluation covering all 102 curriculum topics",
                "Seamless integration of protocol mechanics, subnetting calculations, and cyber defense",
                "Advanced packet forensics, detection rule authoring, and incident triage under pressure"
            ],
            "blueprint": {
                "title": "Flagship Capstone Comprehensive Blueprint",
                "description": "60-question capstone blueprint covering the complete NexoraNet curriculum.",
                "topics": [
                    {"topic_slug": "what-is-computer-networking", "question_count": 2, "difficulty": "BEGINNER"},
                    {"topic_slug": "seven-osi-layers", "question_count": 4, "difficulty": "BEGINNER"},
                    {"topic_slug": "ipv4-basics", "question_count": 3, "difficulty": "BEGINNER"},
                    {"topic_slug": "ports", "question_count": 3, "difficulty": "BEGINNER"},
                    {"topic_slug": "common-network-threats", "question_count": 3, "difficulty": "BEGINNER"},
                    {"topic_slug": "subnetting", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "network-address", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "tcp-basics", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "tcp-flags", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "switching", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "routing", "question_count": 4, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "nat", "question_count": 2, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "firewall-rules", "question_count": 3, "difficulty": "INTERMEDIATE"},
                    {"topic_slug": "packet-structure", "question_count": 4, "difficulty": "ADVANCED"},
                    {"topic_slug": "wireshark-filtering-concepts", "question_count": 3, "difficulty": "ADVANCED"},
                    {"topic_slug": "reconnaissance-detection", "question_count": 4, "difficulty": "ADVANCED"},
                    {"topic_slug": "detection-rules", "question_count": 3, "difficulty": "ADVANCED"},
                    {"topic_slug": "alert-triage", "question_count": 4, "difficulty": "ADVANCED"}
                ]
            }
        }
    ]


def main():
    beginner = get_beginner_tests()
    intermediate = get_intermediate_tests()
    advanced = get_advanced_tests()
    full_mocks = get_full_mocks()

    with open(DATA_DIR / "beginner.json", "w", encoding="utf-8") as f:
        json.dump(beginner, f, indent=2)
    print(f"Wrote {len(beginner)} tests to {DATA_DIR / 'beginner.json'}")

    with open(DATA_DIR / "intermediate.json", "w", encoding="utf-8") as f:
        json.dump(intermediate, f, indent=2)
    print(f"Wrote {len(intermediate)} tests to {DATA_DIR / 'intermediate.json'}")

    with open(DATA_DIR / "advanced.json", "w", encoding="utf-8") as f:
        json.dump(advanced, f, indent=2)
    print(f"Wrote {len(advanced)} tests to {DATA_DIR / 'advanced.json'}")

    with open(DATA_DIR / "full_mocks.json", "w", encoding="utf-8") as f:
        json.dump(full_mocks, f, indent=2)
    print(f"Wrote {len(full_mocks)} tests to {DATA_DIR / 'full_mocks.json'}")

    total = len(beginner) + len(intermediate) + len(advanced) + len(full_mocks)
    print(f"\nTotal mock tests defined: {total}")


if __name__ == "__main__":
    main()
