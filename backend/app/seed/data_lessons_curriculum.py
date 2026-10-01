# NexoraNet Comprehensive Curriculum Lessons & Topic Metadata

TOPIC_PREREQUISITES_MAP = {
    # Intermediate Prerequisites
    "subnetting": ["ipv4-basics"],
    "cidr": ["subnetting"],
    "tcp-three-way-handshake": ["tcp-basics", "ports"],
    "dns-resolution": ["dns", "udp-basics"],
    "dhcp-process": ["dhcp", "arp"],
    "routing": ["ipv4-address-structure", "default-gateway"],
    "switching": ["mac-address", "network-devices"],
    "vlan": ["switching"],
    "nat": ["public-vs-private-ip", "ports"],
    "ping": ["icmp", "default-gateway"],
    "traceroute": ["icmp", "routing"],
    "firewall-rules": ["firewall-basics", "ports"],
    "ids": ["firewall-rules", "tcp-vs-udp"],
    "ips": ["ids"],
    # Advanced Prerequisites
    "packet-structure": ["encapsulation", "seven-osi-layers"],
    "tcp-segments": ["tcp-three-way-handshake", "packet-structure"],
    "dns-packet-analysis": ["dns-resolution", "packet-structure"],
    "traffic-baselines": ["packet-structure", "tcp-segments"],
    "network-indicators": ["firewall-rules", "packet-structure"],
    "detection-engineering-concepts": ["network-indicators", "ids"],
    "recon-detection": ["ports", "packet-structure", "tcp-flags"],
    "alert-triage": ["traffic-baselines", "network-indicators"],
}

TOPIC_METADATA_EXTRAS = {
    "what-is-computer-networking": {
        "estimated_minutes": 25,
        "learning_objectives": [
            "Define the core purpose and anatomy of computer networks",
            "Distinguish between PAN, LAN, MAN, and WAN topologies",
            "Explain client-server vs peer-to-peer operational models",
            "Identify key cybersecurity concerns for network perimeters",
        ],
        "security_relevance": "Understanding network boundaries and connectivity models allows defenders to map enterprise attack surfaces, isolate sensitive assets, and segment unauthorized lateral movement.",
    },
    "network-devices": {
        "estimated_minutes": 30,
        "learning_objectives": [
            "Differentiate between Hubs, Switches, Routers, and Firewalls",
            "Explain collision domains vs broadcast domains across hardware",
            "Identify Layer 2 forwarding vs Layer 3 routing devices",
            "Explain how rogue hardware devices threaten network security",
        ],
        "security_relevance": "Unmanaged network hardware (like rogue access points or hubs) bypass perimeter controls and introduce tap points for eavesdropping and MITM attacks.",
    },
    "seven-osi-layers": {
        "estimated_minutes": 35,
        "learning_objectives": [
            "Recite and explain the functions of all 7 OSI reference layers",
            "Map common protocols and hardware devices to their respective layers",
            "Apply top-down and bottom-up troubleshooting models",
            "Analyze attack vectors targeting specific OSI layers (L2 ARP spoofing vs L7 SQLi)",
        ],
        "security_relevance": "Cybersecurity defenders employ defense-in-depth across the OSI model: Layer 2 port security, Layer 3/4 packet filters, Layer 6 TLS ciphers, and Layer 7 Web Application Firewalls (WAF).",
    },
    "tcp-ip-layers": {
        "estimated_minutes": 25,
        "learning_objectives": [
            "Explain the 4-layer TCP/IP architecture (Network Access, Internet, Transport, Application)",
            "Compare the theoretical 7-layer OSI model with practical 4-layer TCP/IP",
            "Identify protocol encapsulation at each layer",
        ],
        "security_relevance": "The internet was engineered for open availability rather than authentication; understanding TCP/IP header lack of inherent encryption explains why TLS and IPsec must be layered on top.",
    },
    "ipv4-basics": {
        "estimated_minutes": 30,
        "learning_objectives": [
            "Understand 32-bit binary structure and dotted-decimal IPv4 notation",
            "Distinguish between network portion and host portion of an IP",
            "Recognize IPv4 address classes (Class A, B, C, D, E) and default masks",
            "Identify loopback, link-local, and RFC 1918 private ranges",
        ],
        "security_relevance": "Network access control and firewall policies depend on IP attribution. Attackers spoof source IP addresses to bypass ingress filters or conduct amplification DDoS attacks.",
    },
    "mac-address": {
        "estimated_minutes": 25,
        "learning_objectives": [
            "Explain the 48-bit hexadecimal structure of MAC hardware addresses",
            "Identify the Organizationally Unique Identifier (OUI) vs NIC serial number",
            "Explain how switch MAC tables forward local frames",
            "Understand MAC address spoofing and port security mitigation",
        ],
        "security_relevance": "MAC addresses provide local physical identity. Threat actors spoof MAC addresses to bypass MAC filtering, conduct ARP poisoning, or evade captive portals.",
    },
    "ports": {
        "estimated_minutes": 25,
        "learning_objectives": [
            "Explain 16-bit transport port multiplexing (ports 0 to 65535)",
            "Differentiate Well-Known (0-1023), Registered (1024-49151), and Ephemeral (49152-65535) ports",
            "Recognize standard service port numbers (HTTP 80, HTTPS 443, SSH 22, DNS 53)",
            "Explain how port scanning reveals system attack surfaces",
        ],
        "security_relevance": "Unnecessary open ports represent exposed attack surfaces. Defenders minimize risk by closing unused ports, auditing listening services, and deploying host firewalls.",
    },
    "dns": {
        "estimated_minutes": 30,
        "learning_objectives": [
            "Explain the hierarchical domain name system architecture",
            "Identify common DNS record types (A, AAAA, CNAME, MX, TXT, PTR)",
            "Differentiate recursive resolvers from authoritative nameservers",
            "Understand DNS cache poisoning, hijacking, and tunneling",
        ],
        "security_relevance": "Over 90% of malware uses DNS for Command & Control (C2) communication. DNS telemetry provides vital indicators of compromise (IOCs) for security operations centers.",
    },
    "dhcp": {
        "estimated_minutes": 25,
        "learning_objectives": [
            "Explain automated IP configuration using DHCP",
            "Dissect the 4-step DORA handshake (Discover, Offer, Request, Acknowledge)",
            "Identify DHCP option parameters (gateway, subnet mask, DNS servers)",
            "Understand Rogue DHCP servers and DHCP starvation attacks",
        ],
        "security_relevance": "Rogue DHCP servers can distribute malicious default gateways and DNS servers to local clients, establishing effortless Man-in-the-Middle (MITM) interception.",
    },
    "tcp-basics": {
        "estimated_minutes": 30,
        "learning_objectives": [
            "Explain connection-oriented reliable byte-stream semantics",
            "Identify TCP sequence numbers, acknowledgment numbers, and window sizing",
            "Understand TCP connection establishment, data transfer, and teardown",
            "Explain TCP SYN floods and connection state table exhaustion",
        ],
        "security_relevance": "Adversaries exploit TCP connection state backlogs through SYN floods. Analysts inspect TCP flags and retransmissions to detect network anomalies and reconnaissance scans.",
    },
    "udp-basics": {
        "estimated_minutes": 25,
        "learning_objectives": [
            "Explain connectionless, lightweight datagram delivery",
            "Identify the minimal 8-byte UDP header structure",
            "Compare throughput and latency advantages of UDP for VoIP, DNS, and streaming",
            "Understand UDP reflection and amplification DDoS attacks",
        ],
        "security_relevance": "Because UDP is connectionless and does not perform handshakes, source IPs are trivially spoofed, making UDP protocols (NTP, DNS, SNMP) the primary vector for reflection amplification attacks.",
    },
    "http": {
        "estimated_minutes": 25,
        "learning_objectives": [
            "Explain Hypertext Transfer Protocol stateless client-server cycles",
            "Dissect standard HTTP request methods (GET, POST, PUT, DELETE, HEAD)",
            "Interpret HTTP response status code families (2xx, 3xx, 4xx, 5xx)",
            "Recognize the security hazards of transmitting plaintext credentials over HTTP",
        ],
        "security_relevance": "Plaintext HTTP exposes passwords, session cookies, and sensitive payloads to passive eavesdropping. Unsanitized HTTP parameters are the entry point for OWASP Top 10 vulnerabilities.",
    },
    "https": {
        "estimated_minutes": 30,
        "learning_objectives": [
            "Explain TLS encryption wrapping HTTP transport",
            "Understand public key cryptography, digital certificates, and Certificate Authorities (CAs)",
            "Explain the difference between symmetric session encryption and asymmetric key exchange",
            "Identify certificate validation errors and MITM inspection techniques",
        ],
        "security_relevance": "HTTPS prevents wiretapping and tampering on public Wi-Fi networks. Threat actors also use HTTPS to encrypt their malicious C2 channels, requiring TLS inspection proxies in enterprise SOCs.",
    },
    "arp": {
        "estimated_minutes": 25,
        "learning_objectives": [
            "Explain how Address Resolution Protocol resolves Layer 3 IP to Layer 2 MAC",
            "Differentiate ARP request broadcasts from ARP reply unicasts",
            "Inspect and manage operating system ARP cache tables",
            "Understand ARP poisoning and Man-in-the-Middle (MITM) attacks",
        ],
        "security_relevance": "ARP has no authentication; devices accept unsolicited ARP replies. Attackers broadcast fake ARP mappings to poison victim ARP tables and redirect all traffic through the attacker's machine.",
    },
    "icmp": {
        "estimated_minutes": 25,
        "learning_objectives": [
            "Explain the purpose of ICMP as a network-layer diagnostic and control protocol",
            "Identify key ICMP message types (Echo Request/Reply, Destination Unreachable, Time Exceeded)",
            "Explain how `ping` and `traceroute` utilize ICMP",
            "Understand ICMP tunneling, Ping of Death, and smurf attacks",
        ],
        "security_relevance": "Adversaries use ICMP for host discovery ping sweeps and covert data exfiltration (ICMP tunneling) through firewalls that permit outbound ping.",
    },
    "firewall-basics": {
        "estimated_minutes": 30,
        "learning_objectives": [
            "Define the role of network firewalls in enforcing security perimeters",
            "Explain stateless packet filtering vs stateful connection tracking",
            "Understand default-deny vs default-permit security philosophies",
            "Read and interpret simple 5-tuple firewall rule sets",
        ],
        "security_relevance": "Firewalls are the foundational barrier between untrusted public networks and trusted corporate enclaves, enforcing strict access controls based on business necessity.",
    },
    "subnetting": {
        "estimated_minutes": 40,
        "learning_objectives": [
            "Calculate subnet masks, network addresses, and broadcast addresses for any IPv4 prefix",
            "Determine the number of usable hosts per subnet using 2^h - 2",
            "Partition an enterprise address space into departmental subnets",
            "Explain how subnetting isolates broadcast storms and constrains lateral attack movement",
        ],
        "security_relevance": "Proper subnet design restricts blast radiuses during cybersecurity incidents by preventing infected hosts from broadcasting or freely communicating across subnet boundaries.",
    },
    "cidr": {
        "estimated_minutes": 35,
        "learning_objectives": [
            "Explain Classless Inter-Domain Routing slash notation (/24, /26, /30)",
            "Perform fast bit-to-decimal conversions for subnet masks",
            "Calculate route summarization (supernetting) to minimize routing table sizes",
            "Evaluate firewall rules and access lists using CIDR blocks",
        ],
        "security_relevance": "CIDR notation is universal in firewall configurations, cloud security group definitions (AWS/Azure), and SIEM network range classifications.",
    },
    "tcp-three-way-handshake": {
        "estimated_minutes": 35,
        "learning_objectives": [
            "Trace the exact packet exchange: SYN -> SYN-ACK -> ACK",
            "Explain Initial Sequence Number (ISN) randomization to prevent TCP sequence prediction",
            "Identify TCP flags in Wireshark and tcpdump captures",
            "Explain SYN flood attacks and defense mechanisms like SYN cookies",
        ],
        "security_relevance": "The handshake allocates OS kernel memory resources before authentication. SYN flood attacks target this vulnerability, and Port Scans (SYN stealth scans) observe handshake replies to map listening ports without completing connections.",
    },
    "dns-resolution": {
        "estimated_minutes": 35,
        "learning_objectives": [
            "Follow the complete recursive query flow: Client -> Resolver -> Root (.) -> TLD (.com) -> Authoritative Nameserver",
            "Explain DNS caching TTL mechanics at client, router, and ISP resolvers",
            "Differentiate authoritative answers from cached non-authoritative answers",
            "Analyze DNS hijacking and fast-flux botnet domain switching",
        ],
        "security_relevance": "Understanding recursive resolution allows security teams to implement protective DNS resolvers (DNS sinkholing) that block malware lookups before connections can ever be initiated.",
    },
    "dhcp-process": {
        "estimated_minutes": 30,
        "learning_objectives": [
            "Dissect DHCP broadcast traffic (Source: 0.0.0.0, Destination: 255.255.255.255)",
            "Explain lease expiration, renewal (T1 timer at 50%), and rebind (T2 timer at 87.5%)",
            "Identify DHCP option 82 relay agent information",
            "Configure and verify DHCP Snooping on Layer 2 enterprise switches",
        ],
        "security_relevance": "DHCP Snooping validates DHCP messages received on untrusted switch ports, blocking rogue DHCP servers and preventing unauthorized gateway impersonation.",
    },
    "routing": {
        "estimated_minutes": 40,
        "learning_objectives": [
            "Explain how routers determine the best path using Longest Prefix Match",
            "Differentiate static routes from dynamic interior gateway protocols (OSPF, EIGRP)",
            "Explain Administrative Distance (AD) and routing metrics (Hop count, cost, bandwidth)",
            "Identify routing table poisoning, BGP route leaks, and rogue announcements",
        ],
        "security_relevance": "Compromised routing tables allow adversaries to hijack internet traffic, route corporate sessions through rogue surveillance points, or cause widespread denial of service.",
    },
    "switching": {
        "estimated_minutes": 35,
        "learning_objectives": [
            "Explain MAC address table learning, frame forwarding, and frame flooding",
            "Describe the impact of Layer 2 loops and broadcast storms",
            "Explain MAC flooding attacks against switch Content Addressable Memory (CAM)",
            "Implement switch Port Security to limit MAC learning on access ports",
        ],
        "security_relevance": "When a switch's CAM table overflows during a MAC flooding attack, the switch fails open and behaves like a hub, broadcasting all confidential traffic to all ports where an attacker can capture it.",
    },
    "vlan": {
        "estimated_minutes": 35,
        "learning_objectives": [
            "Explain logical network segregation using Virtual Local Area Networks (VLANs)",
            "Dissect IEEE 802.1Q trunk headers and the 12-bit VLAN ID tag",
            "Explain Inter-VLAN routing using Router-on-a-Stick or Layer 3 switches",
            "Understand VLAN hopping attacks (switch spoofing and double tagging) and defensive mitigations",
        ],
        "security_relevance": "VLANs prevent unauthorized lateral traffic between sensitive environments (e.g., PCI-DSS payment zones, guest Wi-Fi, and employee workstations). Proper trunk hardening prevents VLAN hopping.",
    },
    "nat": {
        "estimated_minutes": 30,
        "learning_objectives": [
            "Explain the difference between Static NAT, Dynamic NAT, and Port Address Translation (PAT)",
            "Trace the state translation table: Inside Local, Inside Global, Outside Local, Outside Global",
            "Explain why PAT allows thousands of internal hosts to share a single public IP address",
            "Analyze how NAT impacts network forensic log correlation and attribution",
        ],
        "security_relevance": "NAT hides internal network topology from direct internet port scans. However, for security investigators, NAT complicates attribution unless firewall NAT translation logs are preserved and synchronized with NTP.",
    },
    "ping": {
        "estimated_minutes": 25,
        "learning_objectives": [
            "Use `ping` to test Layer 3 reachability, latency, and packet loss",
            "Interpret ping responses: Reply, Request timed out, and Destination host unreachable",
            "Explain how Time-to-Live (TTL) prevents routing loops and helps identify remote operating systems",
            "Understand why security administrators selectively restrict ICMP on perimeter firewalls",
        ],
        "security_relevance": "Ping sweep tools (like `nmap -sn` or `fping`) rapidly discover live hosts on target subnets. Defensive engineers filter ICMP at boundaries while keeping it enabled internally for diagnostic health monitoring.",
    },
    "firewall-rules": {
        "estimated_minutes": 35,
        "learning_objectives": [
            "Author and audit 5-tuple firewall rules: Source IP, Dest IP, Protocol, Source Port, Dest Port, Action",
            "Explain rule processing order: first-match wins and implicit deny",
            "Differentiate stateless packet inspection from stateful session tracking",
            "Identify common firewall misconfigurations that leave enterprise services exposed",
        ],
        "security_relevance": "Firewall misconfigurations are among the leading causes of cloud and enterprise data breaches. Clean, audited rulebases enforce the principle of least privilege across network zones.",
    },
    "ids": {
        "estimated_minutes": 35,
        "learning_objectives": [
            "Explain Intrusion Detection System (IDS) architecture (SPAN ports, network taps)",
            "Differentiate signature-based matching from anomaly/behavioral detection",
            "Read and dissect simple Snort/Suricata rule syntax",
            "Understand false positives vs false negatives and alert tuning methodologies",
        ],
        "security_relevance": "IDS sensors provide continuous visibility into network traffic, alerting SOC analysts to exploit attempts, malware beacons, and policy violations in real-time.",
    },
    "packet-structure": {
        "estimated_minutes": 40,
        "learning_objectives": [
            "Analyze raw protocol headers down to bit-level offsets in Wireshark",
            "Dissect Ethernet frame headers (Preamble, MACs, EtherType, CRC/FCS)",
            "Dissect IPv4 packet headers (IHL, TTL, Protocol, Checksum, Options)",
            "Identify malformed or crafted packets generated by exploitation frameworks",
        ],
        "security_relevance": "Packet inspection is the gold standard of network forensics. Attackers craft unusual packet flags or header anomalies to evade firewalls; analyzing raw structures unmasks these evasion techniques.",
    },
    "tcp-segments": {
        "estimated_minutes": 40,
        "learning_objectives": [
            "Inspect TCP header control flags (SYN, ACK, FIN, RST, PSH, URG, ECN)",
            "Trace sequence number increments and acknowledgment numbers across bidirectional streams",
            "Follow and reassemble TCP streams in Wireshark to reconstruct transmitted application files",
            "Identify anomalous TCP flag combinations (XMAS scan: FIN+PSH+URG, NULL scan: no flags)",
        ],
        "security_relevance": "Adversaries manipulate TCP flag combinations to probe closed vs open ports while bypassing basic stateless firewalls. Deep inspection of TCP streams reveals data exfiltration and credential theft.",
    },
    "dns-packet-analysis": {
        "estimated_minutes": 35,
        "learning_objectives": [
            "Dissect DNS wire format: Transaction ID, Flags (QR, Opcode, AA, TC, RD, RA, RCODE), Questions, Answers",
            "Identify base64/hex-encoded domain queries characteristic of DNS tunneling",
            "Analyze domain generation algorithms (DGA) in network packet captures",
            "Construct Wireshark display filters to isolate anomalous DNS query volumes",
        ],
        "security_relevance": "Because DNS traffic is almost universally permitted through firewalls, malware authors abuse DNS for covert C2 communications and data exfiltration (DNS tunneling). PCAP dissection reveals these covert channels.",
    },
    "traffic-baselines": {
        "estimated_minutes": 40,
        "learning_objectives": [
            "Establish normal network protocol and bandwidth baselines for enterprise environments",
            "Identify statistical traffic spikes indicative of DDoS or massive exfiltration",
            "Detect anomalous protocol-port pairing (e.g., SSH running over port 80 or 443)",
            "Utilize NetFlow/IPFIX flow statistics for wide-area traffic profiling",
        ],
        "security_relevance": "Behavioral detection relies on knowing what 'normal' looks like. Baseline deviations trigger high-fidelity alerts for insider threats, ransomware staging, and lateral credential movement.",
    },
    "network-indicators": {
        "estimated_minutes": 35,
        "learning_objectives": [
            "Extract atomic, computed, and behavioral Indicators of Compromise (IOCs) from network traffic",
            "Classify indicators using David Bianco's Pyramid of Pain (Hash, IP, Domain, Network Artifact, Tool, TTP)",
            "Feed high-confidence IOCs into firewalls, SIEMs, and threat intelligence platforms",
            "Correlate IP and domain indicators across historical proxy and firewall logs",
        ],
        "security_relevance": "Network indicators allow security teams to rapidly detect active campaigns across thousands of endpoints and systematically block adversary infrastructure.",
    },
    "detection-engineering-concepts": {
        "estimated_minutes": 45,
        "learning_objectives": [
            "Understand the detection engineering lifecycle: Threat modeling -> Log source identification -> Rule authoring -> Testing -> Tuning",
            "Write detection logic in generic Sigma format and translate it to SIEM queries",
            "Map detection coverage against the MITRE ATT&CK Enterprise matrix",
            "Benchmark rule performance and eliminate false positive noise",
        ],
        "security_relevance": "Detection engineering transforms raw threat intelligence into automated defense logic, ensuring that newly discovered adversary techniques are immediately detected across corporate infrastructure.",
    },
    "recon-detection": {
        "estimated_minutes": 40,
        "learning_objectives": [
            "Identify signatures of network reconnaissance tools (Nmap, Masscan, ZMap)",
            "Differentiate TCP SYN stealth scans, TCP Connect scans, UDP scans, and ACK firewall probes",
            "Detect horizontal IP sweeps vs vertical port scans across server subnets",
            "Configure IDS threshold rules to automatically block aggressive scanning sources",
        ],
        "security_relevance": "Reconnaissance is Phase 1 of the Cyber Kill Chain and MITRE ATT&CK framework (T1046). Detecting port scanning early enables defenders to block attackers before vulnerabilities are discovered and exploited.",
    },
    "alert-triage": {
        "estimated_minutes": 45,
        "learning_objectives": [
            "Execute the Tier 1 SOC alert triage workflow under time pressure",
            "Gather contextual evidence: Source IP, Destination IP, user identity, host telemetry, and threat intelligence reputation",
            "Distinguish True Positives from False Positives with documented rationale",
            "Escalate confirmed security incidents according to severity matrices (Low, Medium, High, Critical)",
        ],
        "security_relevance": "Alert triage is the frontline defense of any enterprise SOC. Fast, accurate triage stops intrusions in their initial compromise stages before attackers achieve ransomware encryption or data exfiltration.",
    },
}
