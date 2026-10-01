from app.models.enums import ContentType, DifficultyLevel

COURSE_DATA = {
    "title": "Computer Networking & Cybersecurity",
    "slug": "networking-cybersecurity",
    "description": (
        "Comprehensive, interactive curriculum spanning computer networking fundamentals, "
        "protocol analysis, and defensive cybersecurity operations."
    ),
    "level": DifficultyLevel.BEGINNER,
    "estimated_hours": 120,
    "is_published": True,
}

MODULES_DATA = [
    # LEVEL 1 — BEGINNER
    {
        "title": "Networking Fundamentals",
        "slug": "networking-fundamentals",
        "description": "Foundational architectural models, network topologies, media, and hardware devices.",
        "difficulty": DifficultyLevel.BEGINNER,
        "order_index": 1,
        "topics": [
            (
                "What is Computer Networking?",
                "what-is-computer-networking",
                "Definition, purpose, and evolution of distributed computer networks.",
            ),
            (
                "LAN",
                "lan",
                "Local Area Networks, broadcast domains, and office topology architectures.",
            ),
            (
                "WAN",
                "wan",
                "Wide Area Networks, leased lines, ISP connectivity, and internet exchange points.",
            ),
            (
                "PAN",
                "pan",
                "Personal Area Networks, Bluetooth, and short-range wireless devices.",
            ),
            (
                "MAN",
                "man",
                "Metropolitan Area Networks and municipal fiber ring backbones.",
            ),
            (
                "Client-Server",
                "client-server",
                "Centralized service architectures, resource distribution, and request-response cycles.",
            ),
            (
                "Peer-to-Peer",
                "peer-to-peer",
                "Decentralized compute, distributed hash tables, and symmetric host architectures.",
            ),
            (
                "Network Topologies",
                "network-topologies",
                "Star, Mesh, Ring, Bus, and Hybrid physical and logical topologies.",
            ),
            (
                "Network Devices",
                "network-devices",
                "Hubs, Bridges, Switches, Routers, Wireless Access Points, and Firewalls.",
            ),
            (
                "Network Media",
                "network-media",
                "Twisted pair (UTP/STP), Coaxial, Fiber optic single/multi-mode, and RF channels.",
            ),
        ],
    },
    {
        "title": "OSI Model",
        "slug": "osi-model",
        "description": "The ISO 7-layer reference model for network communication.",
        "difficulty": DifficultyLevel.BEGINNER,
        "order_index": 2,
        "topics": [
            (
                "Seven OSI Layers",
                "seven-osi-layers",
                "Physical, Data Link, Network, Transport, Session, Presentation, Application layers.",
            ),
            (
                "Encapsulation",
                "encapsulation",
                "Wrapping application data into segments, packets, frames, and bits.",
            ),
            (
                "Decapsulation",
                "decapsulation",
                "Receiving hardware stripping headers in bottom-up protocol traversal.",
            ),
            (
                "OSI Troubleshooting",
                "osi-troubleshooting",
                "Structured bottom-up, top-down, and divide-and-conquer diagnostic methodologies.",
            ),
        ],
    },
    {
        "title": "TCP/IP Model",
        "slug": "tcp-ip-model",
        "description": "The practical 4-layer DoD protocol suite powering the global Internet.",
        "difficulty": DifficultyLevel.BEGINNER,
        "order_index": 3,
        "topics": [
            (
                "TCP/IP Layers",
                "tcp-ip-layers",
                "Network Access, Internet, Transport, and Application layers.",
            ),
            (
                "OSI vs TCP/IP",
                "osi-vs-tcp-ip",
                "Side-by-side conceptual comparison, layer mappings, and real-world implementation differences.",
            ),
        ],
    },
    {
        "title": "Basic Addressing",
        "slug": "basic-addressing",
        "description": "Layer 2 MAC hardware addressing, Layer 3 IPv4 logical addressing, and transport ports.",
        "difficulty": DifficultyLevel.BEGINNER,
        "order_index": 4,
        "topics": [
            (
                "IPv4 Basics",
                "ipv4-basics",
                "32-bit logical addresses, octets, and decimal dotted notation.",
            ),
            (
                "IPv4 Address Structure",
                "ipv4-address-structure",
                "Network identifier bits vs Host identifier bits.",
            ),
            (
                "Public vs Private IP",
                "public-vs-private-ip",
                "RFC 1918 address allocations (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) and routability.",
            ),
            (
                "MAC Address",
                "mac-address",
                "48-bit Burned-In Addresses, Organizationally Unique Identifiers (OUI), and NIC hardware IDs.",
            ),
            (
                "Default Gateway",
                "default-gateway",
                "Next-hop routing interface for off-subnet egress traffic.",
            ),
            (
                "Ports",
                "ports",
                "16-bit transport layer software endpoints and well-known service port mappings.",
            ),
        ],
    },
    {
        "title": "Basic Protocols",
        "slug": "basic-protocols",
        "description": "Ubiquitous internet protocol implementations and request-response mechanisms.",
        "difficulty": DifficultyLevel.BEGINNER,
        "order_index": 5,
        "topics": [
            (
                "ICMP",
                "icmp",
                "Internet Control Message Protocol, echo requests, unreachable messages, and TTL expirations.",
            ),
            (
                "ARP",
                "arp",
                "Address Resolution Protocol: mapping IP addresses to physical MAC hardware addresses.",
            ),
            (
                "DNS",
                "dns",
                "Domain Name System hierarchy, resolvers, root servers, and name-to-IP lookup operations.",
            ),
            (
                "DHCP",
                "dhcp",
                "Dynamic Host Configuration Protocol: DORA handshake for automatic IP lease provisioning.",
            ),
            (
                "HTTP",
                "http",
                "Hypertext Transfer Protocol semantics, methods, headers, and stateless request cycles.",
            ),
            (
                "HTTPS",
                "https",
                "Secure HTTP encryption via Transport Layer Security (TLS).",
            ),
            (
                "FTP",
                "ftp",
                "File Transfer Protocol control and data channels, active vs passive modes.",
            ),
            (
                "SSH",
                "ssh",
                "Secure Shell encrypted remote management and asymmetric host key verification.",
            ),
            (
                "SMTP",
                "smtp",
                "Simple Mail Transfer Protocol relaying and message submission standard.",
            ),
        ],
    },
    {
        "title": "TCP and UDP",
        "slug": "tcp-and-udp",
        "description": "Layer 4 transport semantics: reliable connection-oriented streams vs lightweight datagrams.",
        "difficulty": DifficultyLevel.BEGINNER,
        "order_index": 6,
        "topics": [
            (
                "TCP Basics",
                "tcp-basics",
                "Transmission Control Protocol reliability, sequence numbering, and acknowledgments.",
            ),
            (
                "UDP Basics",
                "udp-basics",
                "User Datagram Protocol connectionless semantics and low-overhead streaming.",
            ),
            (
                "TCP vs UDP",
                "tcp-vs-udp",
                "Trade-offs: reliability and flow control vs latency and minimal header overhead.",
            ),
            (
                "Ports and Sockets",
                "ports-and-sockets",
                "IP + Port tuple socket binding and operating system connection tracking.",
            ),
        ],
    },
    {
        "title": "Basic Network Security",
        "slug": "basic-network-security",
        "description": "Introduction to threat models, security controls, and defensive perimeter principles.",
        "difficulty": DifficultyLevel.BEGINNER,
        "order_index": 7,
        "topics": [
            (
                "Firewall Basics",
                "firewall-basics",
                "Packet filtering boundary inspection, permit and deny access control lists.",
            ),
            (
                "Authentication",
                "authentication",
                "Proving identity: passwords, multi-factor keys, certificates, and tokens.",
            ),
            (
                "Encryption",
                "encryption",
                "Symmetric vs asymmetric ciphers, confidentiality, integrity, and hashing.",
            ),
            (
                "Common Network Threats",
                "common-network-threats",
                "Eavesdropping, man-in-the-middle, denial of service, and spoofing attacks.",
            ),
        ],
    },
    # LEVEL 2 — INTERMEDIATE
    {
        "title": "IPv4 & Subnetting",
        "slug": "ipv4-and-subnetting",
        "description": "Classless inter-domain routing, bitwise subnet masks, and variable length subnetting.",
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "order_index": 8,
        "topics": [
            (
                "Subnetting",
                "subnetting",
                "Borrowing host bits for network division and broadcast domain reduction.",
            ),
            (
                "CIDR",
                "cidr",
                "Classless Inter-Domain Routing prefix notation and routing table aggregation.",
            ),
            (
                "Network Address",
                "network-address",
                "Bitwise AND calculation identifying subnetwork boundary.",
            ),
            (
                "Broadcast Address",
                "broadcast-address",
                "All host bits set to 1 for all-station frame targeting.",
            ),
            (
                "Host Range",
                "host-range",
                "Calculating usable first and last host IP addresses within a prefix.",
            ),
            (
                "Subnet Masks",
                "subnet-masks",
                "Contiguous 32-bit binary masks differentiating network from host.",
            ),
            (
                "VLSM",
                "vlsm",
                "Variable Length Subnet Masking: optimizing address allocation across varied subnet sizes.",
            ),
            (
                "Private Addressing",
                "private-addressing",
                "RFC 1918 deployment architectures in enterprise enterprise intranets.",
            ),
            (
                "NAT",
                "nat",
                "Network Address Translation: SNAT, DNAT, and Port Address Translation (PAT).",
            ),
        ],
    },
    {
        "title": "IPv6 Fundamentals",
        "slug": "ipv6-fundamentals",
        "description": "Next-generation 128-bit internet protocol architecture and neighbor discovery.",
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "order_index": 9,
        "topics": [
            (
                "IPv6 Address Structure",
                "ipv6-address-structure",
                "128-bit hexadecimal hextet formatting and shorthand compression rules.",
            ),
            (
                "IPv6 Address Types",
                "ipv6-address-types",
                "Global Unicast (2000::/3), Link-Local (fe80::/10), Unique Local, and Multicast.",
            ),
            (
                "IPv6 Routing Basics",
                "ipv6-routing-basics",
                "Neighbor Discovery Protocol (NDP), Router Advertisements (RA), and SLAAC.",
            ),
        ],
    },
    {
        "title": "Core Protocols & Transport",
        "slug": "core-protocols-and-transport",
        "description": "In-depth protocol handshakes, flags, session teardown, and cryptography.",
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "order_index": 10,
        "topics": [
            (
                "TCP Three-Way Handshake",
                "tcp-three-way-handshake",
                "SYN, SYN-ACK, ACK sequence number synchronization and ISN negotiation.",
            ),
            (
                "TCP Flags",
                "tcp-flags",
                "SYN, ACK, FIN, RST, PSH, URG flag bits and control functions.",
            ),
            (
                "TCP Connection Termination",
                "tcp-connection-termination",
                "Four-way FIN/ACK teardown exchange and TIME_WAIT state purposes.",
            ),
            (
                "UDP Communication",
                "udp-communication",
                "Stateless datagram delivery for DNS queries, VoIP (RTP), and DHCP.",
            ),
            (
                "DNS Resolution",
                "dns-resolution",
                "Recursive vs Iterative queries, root hints, TLD authoritative servers.",
            ),
            (
                "DNS Record Types",
                "dns-record-types",
                "A, AAAA, CNAME, MX, TXT, PTR, NS, and SOA record semantics.",
            ),
            (
                "DHCP Process",
                "dhcp-process",
                "Discover, Offer, Request, Acknowledge packet internals and option fields.",
            ),
            (
                "HTTP Methods",
                "http-methods",
                "GET, POST, PUT, DELETE, PATCH, HEAD, and idempotent semantics.",
            ),
            (
                "HTTP Status Codes",
                "http-status-codes",
                "1xx Informational, 2xx Success, 3xx Redirection, 4xx Client Error, 5xx Server Error.",
            ),
            (
                "HTTPS",
                "https-intermediate",
                "Certificate authorities, digital signatures, and public key verification.",
            ),
            (
                "TLS Basics",
                "tls-basics",
                "TLS 1.2 vs 1.3 handshake, cipher suites, Diffie-Hellman ephemeral key exchanges.",
            ),
            (
                "SSH",
                "ssh-intermediate",
                "Diffie-Hellman key exchange, session key derivation, and public key authentication.",
            ),
        ],
    },
    {
        "title": "Network Infrastructure",
        "slug": "network-infrastructure",
        "description": "Layer 2 switching, MAC table management, VLANs, and Layer 3 routing operations.",
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "order_index": 11,
        "topics": [
            (
                "Switching",
                "switching",
                "Layer 2 frame forwarding, transparent bridging, and flooding unknown unicast frames.",
            ),
            (
                "MAC Address Table",
                "mac-address-table",
                "CAM table source learning, aging timers, and frame filtering.",
            ),
            (
                "VLAN",
                "vlan",
                "Virtual Local Area Networks: logical broadcast domain segmentation.",
            ),
            (
                "Trunking",
                "trunking",
                "IEEE 802.1Q frame tagging, Native VLAN, and multi-switch link aggregation.",
            ),
            (
                "Routing",
                "routing",
                "Layer 3 packet forwarding decisions based on destination IP and longest prefix match.",
            ),
            (
                "Static Routing",
                "static-routing",
                "Administrator-defined next-hop paths and administrative distance.",
            ),
            (
                "Dynamic Routing Concepts",
                "dynamic-routing-concepts",
                "Autonomous systems, IGP vs EGP, metrics, and convergence.",
            ),
            (
                "Default Routes",
                "default-routes",
                "Gateway of last resort (0.0.0.0/0) forwarding rules.",
            ),
        ],
    },
    {
        "title": "Network Troubleshooting",
        "slug": "network-troubleshooting",
        "description": "Essential CLI utilities, interface diagnostics, and route table inspection.",
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "order_index": 12,
        "topics": [
            (
                "Ping",
                "ping",
                "ICMP Echo testing, round-trip time, packet loss, and MTU discovery.",
            ),
            (
                "Traceroute",
                "traceroute",
                "Hop-by-hop path discovery using incrementing TTL values and ICMP Time Exceeded.",
            ),
            (
                "nslookup/dig concepts",
                "nslookup-dig-concepts",
                "Direct DNS query debugging, SOA interrogation, and response flag verification.",
            ),
            (
                "ipconfig/ifconfig/ip",
                "ipconfig-ifconfig-ip",
                "Host interface configuration, subnet verification, and default gateway validation.",
            ),
            (
                "netstat/ss",
                "netstat-ss",
                "Listing active network sockets, listening TCP/UDP ports, and connection states.",
            ),
            (
                "Routing Table Analysis",
                "routing-table-analysis",
                "Evaluating kernel routing tables, metrics, interfaces, and gateway paths.",
            ),
        ],
    },
    {
        "title": "Network Security Defense",
        "slug": "network-security-defense",
        "description": "Stateful firewall inspection, intrusion detection/prevention, and secure protocols.",
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "order_index": 13,
        "topics": [
            (
                "Firewall Rules",
                "firewall-rules",
                "Authoring 5-tuple matching rules (Source IP, Dest IP, Protocol, Source Port, Dest Port).",
            ),
            (
                "NAT Security",
                "nat-security",
                "Hiding internal RFC 1918 topologies behind perimeter addresses.",
            ),
            (
                "IDS",
                "ids",
                "Intrusion Detection Systems: passive network tap monitoring and anomaly detection.",
            ),
            (
                "IPS",
                "ips",
                "Intrusion Prevention Systems: inline packet inspection and automated connection resets.",
            ),
            (
                "Network Segmentation",
                "network-segmentation",
                "Demilitarized zones (DMZ), micro-segmentation, and zero trust perimeters.",
            ),
            (
                "Secure Protocols",
                "secure-protocols",
                "Deprecating cleartext Telnet/FTP/HTTP in favor of SSH/SFTP/HTTPS.",
            ),
        ],
    },
    # LEVEL 3 — ADVANCED
    {
        "title": "Advanced Networking",
        "slug": "advanced-networking",
        "description": "Enterprise routing protocols, VLAN attacks, NAT traversal, and IPv6 security.",
        "difficulty": DifficultyLevel.ADVANCED,
        "order_index": 14,
        "topics": [
            (
                "Advanced Subnetting",
                "advanced-subnetting",
                "Complex supernetting, route summarization, and bit-level partition design.",
            ),
            (
                "VLSM",
                "vlsm-advanced",
                "Variable-length subnetting across multi-tier enterprise branch infrastructures.",
            ),
            (
                "Advanced Routing",
                "advanced-routing",
                "Link-state Dijkstra calculations, distance-vector Bellman-Ford, and path metrics.",
            ),
            (
                "Routing Protocol Concepts",
                "routing-protocol-concepts",
                "OSPF area design (Backbone Area 0), BGP AS-Path attributes, and convergence.",
            ),
            (
                "VLAN Security",
                "vlan-security",
                "Preventing VLAN hopping, double tagging, and rogue switch DTP negotiation.",
            ),
            (
                "Network Segmentation",
                "network-segmentation-advanced",
                "Zero-trust network architecture, east-west micro-segmentation, and NAC.",
            ),
            (
                "NAT Behavior",
                "nat-behavior",
                "Full cone, restricted cone, port restricted cone, and symmetric NAT traversal (STUN/TURN).",
            ),
            (
                "IPv6 Security",
                "ipv6-security",
                "Rogue router advertisement defense (RA Guard), DHCPv6 snooping, and NDP spoofing.",
            ),
        ],
    },
    {
        "title": "Packet Analysis",
        "slug": "packet-analysis",
        "description": "Deep packet inspection, Wireshark filtering, and protocol dissection.",
        "difficulty": DifficultyLevel.ADVANCED,
        "order_index": 15,
        "topics": [
            (
                "Packet Structure",
                "packet-structure",
                "Bit-level layout of PDU headers, flags, options, and payloads.",
            ),
            (
                "Ethernet Frames",
                "ethernet-frames",
                "Preamble, SFD, MAC headers, 802.1Q tags, EtherType, and FCS CRC32 checks.",
            ),
            (
                "IP Packets",
                "ip-packets",
                "Version, IHL, DSCP, Total Length, Identification, Flags, Fragment Offset, TTL, Protocol, Checksum.",
            ),
            (
                "TCP Segments",
                "tcp-segments",
                "Sequence Numbers, Ack Numbers, Data Offset, Reserved, Control Bits, Window Size, Checksum, Urgent Pointer, Options.",
            ),
            (
                "UDP Datagrams",
                "udp-datagrams",
                "8-byte compact headers: Source Port, Destination Port, Length, Checksum.",
            ),
            (
                "DNS Packet Analysis",
                "dns-packet-analysis",
                "Query IDs, flags (QR, Opcode, AA, TC, RD, RA, RCODE), questions, answers, and authority sections.",
            ),
            (
                "HTTP Packet Analysis",
                "http-packet-analysis",
                "Plaintext request URI dissection, response headers, chunked transfer encoding.",
            ),
            (
                "TLS Traffic",
                "tls-traffic",
                "Client Hello, Server Hello, Certificate exchange, Key Exchange, and encrypted application data records.",
            ),
            (
                "TCP Stream Analysis",
                "tcp-stream-analysis",
                "Following TCP streams in Wireshark, tracking sequence jumps, retransmissions, and out-of-order frames.",
            ),
            (
                "Wireshark Filtering Concepts",
                "wireshark-filtering-concepts",
                "Mastering display filters, boolean expressions, protocol offsets, and field comparisons.",
            ),
        ],
    },
    {
        "title": "Advanced Network Security",
        "slug": "advanced-network-security",
        "description": "Stateful firewall internals, traffic baselining, and covert channels.",
        "difficulty": DifficultyLevel.ADVANCED,
        "order_index": 16,
        "topics": [
            (
                "Firewall Architecture",
                "firewall-architecture",
                "Next-Generation Firewalls (NGFW), deep packet inspection, and application awareness.",
            ),
            (
                "Stateful vs Stateless Filtering",
                "stateful-vs-stateless-filtering",
                "Connection state tables (NEW, ESTABLISHED, RELATED) vs simple ACLs.",
            ),
            (
                "IDS/IPS",
                "ids-ips-advanced",
                "Signature matching engines, protocol anomaly detection, and heuristic scoring.",
            ),
            (
                "Network Monitoring",
                "network-monitoring",
                "Flow records (NetFlow, IPFIX, sFlow) and passive network telemetry collection.",
            ),
            (
                "Network Detection",
                "network-detection",
                "Identifying beaconing, lateral movement, port scanning, and exfiltration in network streams.",
            ),
            (
                "Traffic Baselines",
                "traffic-baselines",
                "Establishing statistical norms for bandwidth, protocol ratios, and connection rates.",
            ),
            (
                "Anomalous Traffic",
                "anomalous-traffic",
                "Detecting deviations: sudden outbound surges, non-standard port usage, and ICMP tunneling.",
            ),
            (
                "DNS Security",
                "dns-security",
                "DNSSEC cryptographic validation, DNS over HTTPS (DoH), and fast-flux domain detection.",
            ),
            (
                "Suspicious Connections",
                "suspicious-connections",
                "Identifying long-duration beaconing, anomalous TLS SNI headers, and TOR exit nodes.",
            ),
        ],
    },
    {
        "title": "Reconnaissance & Defense",
        "slug": "reconnaissance-and-defense",
        "description": "Adversary network discovery methods and detection mechanisms.",
        "difficulty": DifficultyLevel.ADVANCED,
        "order_index": 17,
        "topics": [
            (
                "Network Discovery Concepts",
                "network-discovery-concepts",
                "Active ARP sweeps, ICMP sweeps, and passive listening discovery techniques.",
            ),
            (
                "Port Scanning Concepts",
                "port-scanning-concepts",
                "TCP SYN stealth scans, Full Connect scans, UDP scans, and FIN/NULL/Xmas scans.",
            ),
            (
                "Service Enumeration Concepts",
                "service-enumeration-concepts",
                "Banner grabbing, protocol negotiation probes, and service version fingerprinting.",
            ),
            (
                "Reconnaissance Detection",
                "reconnaissance-detection",
                "Catching port scans using threshold triggers, honeypots, and connection failure ratios.",
            ),
        ],
    },
    {
        "title": "Detection Engineering",
        "slug": "detection-engineering",
        "description": "Authoring intrusion detection signatures, Sigma rules, and tuning alerts.",
        "difficulty": DifficultyLevel.ADVANCED,
        "order_index": 18,
        "topics": [
            (
                "Detection Rules",
                "detection-rules",
                "Writing Snort/Suricata rules with header matches, content strings, and PCRE expressions.",
            ),
            (
                "Indicators of Compromise",
                "indicators-of-compromise",
                "Hashes, IP addresses, malicious domains, and behavioral IOC patterns.",
            ),
            (
                "Network Indicators",
                "network-indicators",
                "Suspicious user agents, high-entropy query strings, and abnormal packet sizes.",
            ),
            (
                "Alert Creation",
                "alert-creation",
                "Transforming security telemetry events into actionable SIEM alert tickets.",
            ),
            (
                "False Positives",
                "false-positives",
                "Root cause analysis of benign triggers and legitimate administrative activity.",
            ),
            (
                "Detection Tuning",
                "detection-tuning",
                "Refining signatures, implementing thresholding, and suppressing noisy benign sources.",
            ),
        ],
    },
    {
        "title": "Incident Investigation",
        "slug": "incident-investigation",
        "description": "SOC triage, forensic timeline analysis, evidence handling, and reporting.",
        "difficulty": DifficultyLevel.ADVANCED,
        "order_index": 19,
        "topics": [
            (
                "Alert Triage",
                "alert-triage",
                "First-response severity assessment, scope verification, and false-positive elimination.",
            ),
            (
                "Evidence Collection",
                "evidence-collection",
                "Capturing network PCAPs, preserving firewall logs, and maintaining chain of custody.",
            ),
            (
                "Timeline Analysis",
                "timeline-analysis",
                "Correlating multi-source timestamps across firewalls, proxies, and endpoint logs.",
            ),
            (
                "Network Investigation",
                "network-investigation",
                "Reconstructing lateral movement paths, pivot points, and data staging channels.",
            ),
            (
                "Incident Classification",
                "incident-classification",
                "Assessing breach severity, unauthorized access scope, and compliance impact.",
            ),
            (
                "Incident Reporting",
                "incident-reporting",
                "Drafting executive root-cause summaries and technical mitigation remediation plans.",
            ),
        ],
    },
]

SAMPLE_LESSONS = [
    {
        "topic_slug": "seven-osi-layers",
        "title": "The Seven Layers of the OSI Model",
        "slug": "seven-layers-osi-model",
        "description": "Deep-dive into the ISO 7-layer theoretical networking framework.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.BEGINNER,
        "estimated_minutes": 20,
        "content": """# The Seven Layers of the OSI Model

The **Open Systems Interconnection (OSI)** model is a conceptual framework standardized by ISO in 1984 to describe how computers exchange data across a network.

## The 7 Layers Explained

1. **Layer 7 — Application**: Where end-user network applications interact (HTTP, DNS, SSH, SMTP).
2. **Layer 6 — Presentation**: Formats, encrypts, and compresses data (TLS, ASCII, JPEG).
3. **Layer 5 — Session**: Manages and terminates communication sessions between software processes.
4. **Layer 4 — Transport**: End-to-end transport, port addressing, flow control, and reliability (TCP, UDP).
5. **Layer 3 — Network**: Logical addressing (IPv4/IPv6), path selection, and routing across internetworks.
6. **Layer 2 — Data Link**: Physical addressing (MAC), framing, switch forwarding, and error detection (Ethernet, 802.11).
7. **Layer 1 — Physical**: Electrical, optical, or radio bitstream transmission across media.

### Memory Mnemonic
> **P**lease **D**o **N**ot **T**hrow **S**ausage **P**izza **A**way
> (Physical -> Data Link -> Network -> Transport -> Session -> Presentation -> Application)
""",
    },
    {
        "topic_slug": "encapsulation",
        "title": "Data Encapsulation and Protocol Data Units",
        "slug": "data-encapsulation-and-pdus",
        "description": "How upper-layer payloads get wrapped with network headers at each stage.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.BEGINNER,
        "estimated_minutes": 15,
        "content": """# Data Encapsulation and Protocol Data Units (PDUs)

When data travels down the protocol stack from the sender, each layer wraps the payload with its own control header.

## Protocol Data Unit (PDU) Names
* **Layer 7-5**: Data / Message
* **Layer 4**: **Segment** (TCP) or **Datagram** (UDP)
* **Layer 3**: **Packet** (IP)
* **Layer 2**: **Frame** (Ethernet)
* **Layer 1**: **Bits**

### The Encapsulation Lifecycle
```
[Application Data]
     ↓
[TCP Header | Application Data]                  (Segment)
     ↓
[IP Header | TCP Header | Application Data]       (Packet)
     ↓
[Eth Header | IP Header | TCP Header | Data | FCS] (Frame)
     ↓
01001101 01100101 01111000 01101111...           (Bits)
```
""",
    },
    {
        "topic_slug": "subnetting",
        "title": "IPv4 Subnetting & CIDR Calculation",
        "slug": "ipv4-subnetting-and-cidr",
        "description": "Learn the mathematics of borrowing host bits to construct custom subnetworks.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 25,
        "content": """# IPv4 Subnetting & Classless Inter-Domain Routing (CIDR)

Subnetting divides a large network block into smaller, isolated broadcast domains.

## The Core Formulas
* **Number of Subnets**: \\(2^n\\), where \\(n\\) is the number of borrowed network bits.
* **Usable Hosts per Subnet**: \\(2^h - 2\\), where \\(h\\) is the remaining host bits (subtract 2 for Network and Broadcast IDs).

### Example: Subnetting a /24 into /26 Subnets
Base prefix: `192.168.1.0/24`
Borrowing 2 bits yields a `/26` mask (`255.255.255.192`):
* Subnet 0: `192.168.1.0/26` (Hosts: `.1` to `.62`, Broadcast: `.63`)
* Subnet 1: `192.168.1.64/26` (Hosts: `.65` to `.126`, Broadcast: `.127`)
* Subnet 2: `192.168.1.128/26` (Hosts: `.129` to `.190`, Broadcast: `.191`)
* Subnet 3: `192.168.1.192/26` (Hosts: `.193` to `.254`, Broadcast: `.255`)
""",
    },
    {
        "topic_slug": "tcp-three-way-handshake",
        "title": "The TCP Three-Way Handshake Protocol",
        "slug": "tcp-three-way-handshake-protocol",
        "description": "Step-by-step synchronization of sequence numbers and port sockets.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 20,
        "content": """# The TCP Three-Way Handshake

Before any application data can flow over TCP, client and server must establish a reliable, full-duplex virtual circuit.

## Handshake Steps
1. **SYN (Synchronize)**: Client sends packet with `SYN=1`, random Initial Sequence Number (`ISN_c`), and destination port.
2. **SYN-ACK**: Server acknowledges client's sequence number (`ACK = ISN_c + 1`) and sends its own `ISN_s` with `SYN=1, ACK=1`.
3. **ACK**: Client acknowledges server's sequence number (`ACK = ISN_s + 1`). Both endpoints transition to `ESTABLISHED`.

### Security Note: SYN Flood Attacks
Adversaries exploit this handshake by sending high-volume SYN requests without ever returning the final ACK, exhausting the server's half-open connection table backlog. Defenders mitigate this with **SYN Cookies**.
""",
    },
    {
        "topic_slug": "packet-structure",
        "title": "Packet Forensics & Frame Dissection",
        "slug": "packet-forensics-and-dissection",
        "description": "Analyzing raw protocol headers and inspecting network traffic captures.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.ADVANCED,
        "estimated_minutes": 30,
        "content": """# Packet Forensics & Frame Dissection

In packet analysis, security analysts dissect captured traffic down to the raw byte offsets.

## Anatomy of an IPv4 Header
* **Version (4 bits)**: 0100 for IPv4.
* **Header Length (4 bits)**: Typically 5 (meaning \\(5 \\times 4 = 20\\) bytes).
* **Time to Live (TTL) (8 bits)**: Decremented by 1 at every router hop.
* **Protocol (8 bits)**: `0x06` for TCP, `0x11` for UDP, `0x01` for ICMP.
* **Source & Destination IP Addresses**: 32-bit addresses each.

### Investigative Application
An anomalous TTL (e.g., TTL=255 suddenly dropping to TTL=64 for the same host) can indicate route flapping, IP spoofing, or unauthorized network proxying.
""",
    },
]
