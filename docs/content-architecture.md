# NexoraNet Curriculum & Content Architecture

> Document Version: 1.0.0  
> Scope: 19 Modules, 126 Core Topics, Progressive Difficulty Taxonomy (Beginner → Intermediate → Advanced)

---

## 1. Content Hierarchy Design

NexoraNet organizes knowledge into a 4-tier relational hierarchy:

```
Course (e.g., Computer Networking & Cybersecurity)
  └── Module (e.g., Network Layer & IP Routing)
       └── Topic (e.g., Subnetting & CIDR Calculation) [GLOBAL REUSABLE PIVOT]
            ├── Lessons (e.g., Understanding CIDR Notation, Subnet Masks Explained)
            ├── Hands-on Labs (e.g., VLSM Subnetting Lab)
            ├── Question Bank Items (e.g., Single Choice, Subnetting Math Questions)
            ├── Blueprint Weightings (e.g., 20% in CCNA-style mock test)
            └── Topic Telemetry (e.g., Student Proficiency Score: 85%)
```

### Why the Topic Entity is the Central Knowledge Pivot
In traditional LMS platforms, questions and labs are often tightly coupled to isolated lessons or hardcoded tests. NexoraNet enforces **topic-centric reusability**:
* A student learning IPv4 subnetting reads markdown lessons mapped to the `subnetting-cidr` topic.
* When they launch a practical container lab, the lab's verification checkpoints report back to the `subnetting-cidr` topic.
* Mock test blueprints allocate question quotas from `subnetting-cidr`.
* The progress tracking engine aggregates answers across lessons, labs, and exams into a single normalized **Topic Proficiency Score**.

---

## 2. Curriculum Taxonomy (19 Modules, 126 Topics)

### Level 1: Beginner (Foundations of Networking & Computing)

#### Module 1: Computer Networking Fundamentals (`networking-fundamentals`)
1. `intro-to-networks`: Introduction to Computer Networks & Network Types (LAN, WAN, MAN, PAN)
2. `network-topologies`: Network Topologies (Star, Mesh, Bus, Ring, Hybrid)
3. `osi-model-7-layers`: The 7-Layer OSI Reference Model
4. `tcp-ip-suite`: The 4-Layer TCP/IP Protocol Suite
5. `osi-vs-tcp-ip`: OSI Model vs TCP/IP Comparison
6. `data-encapsulation-pdus`: Data Encapsulation, Decapsulation, and PDUs

#### Module 2: Physical & Data Link Layers (`physical-data-link`)
7. `physical-media-cabling`: Network Transmission Media (Twisted Pair, Coaxial, Fiber Optics)
8. `ethernet-framing-mac`: Ethernet Frame Structure and MAC Addressing
9. `csma-cd-ca`: Collision Domains, Broadcast Domains, and CSMA/CD / CSMA/CA
10. `switches-bridges-hubs`: Hubs vs Bridges vs Layer 2 Switches
11. `mac-address-tables`: Switch MAC Address Table Learning & Frame Forwarding
12. `duplex-speed-autoneg`: Duplex Modes (Half vs Full) and Auto-Negotiation

#### Module 3: Network Layer & Addressing (`network-layer-addressing`)
13. `ipv4-address-structure`: IPv4 Addressing & Address Classes (A, B, C, D, E)
14. `subnetting-cidr`: IPv4 Subnetting, Subnet Masks, and CIDR Notation
15. `vlsm-subnet-design`: Variable Length Subnet Masking (VLSM)
16. `private-public-ips`: RFC 1918 Private vs Public IP Addresses
17. `ipv6-architecture`: IPv6 Address Architecture and Notation
18. `ipv6-address-types`: IPv6 Address Types (Global Unicast, Link-Local, Multicast)

#### Module 4: Transport Layer Protocols (`transport-layer-protocols`)
19. `transport-layer-role`: Transport Layer Responsibilities and Port Multiplexing
20. `tcp-three-way-handshake`: TCP Architecture, 3-Way Handshake, and Connection Teardown
21. `tcp-flow-error-control`: TCP Flow Control, Windowing, Sequence Numbers, and Retransmission
22. `udp-architecture`: UDP Architecture and Characteristics
23. `tcp-vs-udp-matrix`: TCP vs UDP Protocol Comparison & Use Cases
24. `well-known-ports`: Common Port Numbers and Service Assignments (1-1024)

#### Module 5: Essential Network Services (`essential-network-services`)
25. `dns-architecture-resolution`: DNS Architecture, Records (A, AAAA, CNAME, MX, PTR), and Resolution Flow
26. `dhcp-dora-process`: DHCP Architecture and the DORA Process
27. `nat-pat-translation`: Network Address Translation (NAT) and Port Address Translation (PAT)
28. `arp-and-proxy-arp`: Address Resolution Protocol (ARP) and Gratuitous ARP
29. `icmp-and-ping`: ICMP Architecture, Ping, and Traceroute Mechanics
30. `ntp-time-sync`: Network Time Protocol (NTP) and Time Synchronization

#### Module 6: Networking Command Line & Diagnostics (`network-cli-diagnostics`)
31. `cli-ping-traceroute`: Ping and Traceroute / Tracert Deep Dive
32. `cli-ipconfig-ifconfig`: Host Configuration (`ipconfig`, `ifconfig`, `ip addr`)
33. `cli-netstat-ss`: Socket Inspection (`netstat`, `ss`, `lsof`)
34. `cli-arp-table-mgmt`: Viewing and Managing ARP Tables (`arp -a`, `ip neigh`)
35. `cli-nslookup-dig`: DNS Query Tools (`nslookup`, `dig`, `host`)
36. `cli-route-table-mgmt`: Inspecting Routing Tables (`route print`, `ip route`)

---

### Level 2: Intermediate (Routing, Switching & Network Defense)

#### Module 7: Switching Technologies & VLANs (`switching-vlans`)
37. `vlans-and-segmentation`: VLAN Concepts and Broadcast Domain Segmentation
38. `8021q-trunking`: 802.1Q Frame Tagging and Trunk Ports
39. `dtp-and-vtp`: Dynamic Trunking Protocol (DTP) & VLAN Trunking Protocol (VTP)
40. `inter-vlan-routing`: Inter-VLAN Routing (Router-on-a-Stick vs Layer 3 Switches)
41. `native-vlan-security`: Native VLAN Hazards and Security Best Practices
42. `voice-and-data-vlans`: Voice VLANs and Quality of Service (QoS) Tagging

#### Module 8: Spanning Tree Protocol (`spanning-tree-protocol`)
43. `layer2-switching-loops`: Layer 2 Loops and Broadcast Storm Hazards
44. `stp-8021d-mechanics`: 802.1D Spanning Tree Operation and Root Bridge Election
45. `stp-port-states-roles`: STP Port Roles (Root, Designated, Blocked) and States
46. `rstp-8021w-rapid`: Rapid Spanning Tree Protocol (802.1w) Convergence
47. `stp-security-bpduguard`: STP Security: BPDU Guard, Root Guard, and Loop Guard
48. `mstp-multiple-spanning-tree`: Multiple Spanning Tree (MST / 802.1s) Overview

#### Module 9: IP Routing Technologies (`ip-routing-technologies`)
49. `routing-table-lookup`: Routing Table Lookups and Longest Prefix Match
50. `static-vs-dynamic-routing`: Static Routes vs Default Routes vs Dynamic Routing
51. `administrative-distance-metric`: Administrative Distance and Metrics
52. `distance-vector-vs-link-state`: Distance Vector vs Link-State Routing Algorithms
53. `ospf-single-area`: OSPF Fundamentals, Neighbors, LSAs, and Single Area Setup
54. `ospf-multi-area-dr-bdr`: OSPF DR/BDR Election and Multi-Area Concepts
55. `bgp-fundamentals`: Border Gateway Protocol (BGP) and Autonomous Systems

#### Module 10: Access Control Lists & Traffic Filtering (`acls-traffic-filtering`)
56. `standard-ipv4-acls`: Standard IPv4 Access Control Lists
57. `extended-ipv4-acls`: Extended IPv4 ACLs (Port and Protocol Filtering)
58. `named-vs-numbered-acls`: Numbered vs Named ACL Structure and Syntax
59. `acl-inbound-outbound-placement`: Inbound vs Outbound Placement Rules
60. `time-based-reflexive-acls`: Time-based and Reflexive ACLs
61. `troubleshooting-acl-rules`: Common ACL Misconfigurations and Troubleshooting

#### Module 11: Wireless Networking Fundamentals (`wireless-networking`)
62. `wireless-standards-80211`: IEEE 802.11 Standards (a/b/g/n/ac/ax/be)
63. `wireless-frequencies-channels`: 2.4 GHz vs 5 GHz vs 6 GHz Frequencies and Channel Overlap
64. `wireless-topologies-bssid`: SSIDs, BSSIDs, ESSIDs, and Wireless Topologies
65. `wireless-security-wpa`: WEP, WPA, WPA2 (PSK vs Enterprise), and WPA3 Security
66. `wireless-controller-architectures`: Autonomous APs vs Lightweight APs and WLC Architectures
67. `wireless-troubleshooting-tools`: RF Interference, Coverage Holes, and Wireless Analysis Tools

#### Module 12: Network Security Essentials (`network-security-essentials`)
68. `cia-triad-cybersecurity`: The CIA Triad: Confidentiality, Integrity, and Availability
69. `network-attack-types`: Overview of Common Network Attacks
70. `dos-ddos-mechanics`: DoS and DDoS Attack Mechanisms (SYN Flood, UDP Flood, Amplification)
71. `arp-poisoning-spoofing`: ARP Poisoning and Man-in-the-Middle (MITM) Attacks
72. `dns-spoofing-cache-poisoning`: DNS Spoofing, Cache Poisoning, and DNS Amplification
73. `rogue-dhcp-starvation`: Rogue DHCP Servers and DHCP Starvation
74. `mac-flooding-and-attacks`: MAC Address Flooding and CAM Table Overflow

#### Module 13: Cryptography & Secure Communication (`crypto-secure-comms`)
75. `crypto-symmetric-encryption`: Symmetric Encryption (AES, DES, 3DES, ChaCha20)
76. `crypto-asymmetric-encryption`: Asymmetric Encryption (RSA, ECC, Diffie-Hellman)
77. `crypto-hashing-mac`: Cryptographic Hash Functions (SHA-256, MD5) and HMAC
78. `pki-certificates-cas`: Public Key Infrastructure (PKI), Digital Signatures, and CAs
79. `ssl-tls-handshake-ciphers`: SSL/TLS Architecture and Handshake Negotiation
80. `ipsec-vpn-protocols`: IPsec VPNs: AH, ESP, and IKEv1/IKEv2 Tunnel vs Transport Modes
81. `ssh-secure-shell-internals`: Secure Shell (SSH) Protocol Architecture and Key Exchange

---

### Level 3: Advanced (Packet Analysis, Detection & Mini SOC)

#### Module 14: Packet Analysis with Wireshark & tcpdump (`packet-analysis-wireshark`)
82. `wireshark-fundamentals-ui`: Wireshark Interface, Dissectors, and Packet Capture Setup
83. `capture-vs-display-filters`: Capture Filters (BPF Syntax) vs Display Filters
84. `analyzing-arp-icmp-pcaps`: PCAP Dissection: ARP Requests/Replies and ICMP Types
85. `analyzing-tcp-handshakes-pcaps`: PCAP Dissection: TCP Handshakes, Window Resizing, and RSTs
86. `analyzing-dns-http-pcaps`: PCAP Dissection: DNS Lookups and HTTP Request/Response Streams
87. `spotting-malicious-traffic`: Identifying Malicious Traffic Patterns in Wiresharks
88. `tcpdump-cli-mastery`: Command-Line Packet Capture with `tcpdump`

#### Module 15: Network Reconnaissance & Port Scanning (`reconnaissance-scanning`)
89. `passive-vs-active-recon`: Passive vs Active Reconnaissance Methodologies
90. `osint-footprinting-basics`: DNS Footprinting, WHOIS, and OSINT Techniques
91. `port-scanning-theory`: Port Scanning Theory (TCP SYN, Full Connect, NULL, FIN, XMAS)
92. `nmap-fundamentals-flags`: Nmap Scanning Techniques, Flags, and Host Discovery
93. `service-os-fingerprinting`: Service Version Detection and OS Fingerprinting
94. `nmap-scripting-engine-nse`: Nmap Scripting Engine (NSE) for Vulnerability Detection
95. `recon-evasion-firewall-bypass`: Firewall Evasion and Detection Mitigation Strategies

#### Module 16: Firewalls, IDS & IPS (`firewalls-ids-ips`)
96. `firewall-technologies-comparison`: Packet Filtering, Stateful Inspection, and Next-Gen Firewalls (NGFW)
97. `ids-vs-ips-architectures`: Intrusion Detection vs Intrusion Prevention (In-line vs Out-of-band)
98. `signature-vs-anomaly-detection`: Signature-based vs Anomaly-based vs Behavioral Detection
99. `snort-suricata-rule-syntax`: Snort and Suricata Rule Syntax and Header Dissection
100. `writing-custom-ids-rules`: Writing Custom Detection Signatures for Malicious Traffic
101. `firewall-zone-architecture`: Firewall Zone Architecture (DMZ, Internal, External)
102. `evaluating-alert-fidelity`: Tuning False Positives and Evaluating Detection Fidelity

#### Module 17: Detection Engineering & Rule Writing (`detection-engineering`)
103. `detection-engineering-lifecycle`: Detection Engineering Lifecycle and Methodology
104. `sigma-rule-standard`: Sigma Rule Format: Generic Signatures for Log Analysis
105. `snort-rule-crafting`: Advanced Snort Rule Writing (Payload Inspection, `content`, `pcre`)
106. `zeek-bro-network-monitoring`: Zeek (Bro) Network Security Monitoring and Event Logs
107. `yara-rules-payload-matching`: YARA Rule Fundamentals for Network Payload Inspection
108. `testing-validating-rules`: Replaying Attacks to Validate and Benchmark Detection Rules
109. `mitre-attck-network-mapping`: Mapping Network Detections to MITRE ATT&CK Matrix

#### Module 18: Security Operations Center (SOC) Workflows (`soc-workflows-siem`)
110. `soc-roles-tiers-workflow`: SOC Overview: Tier 1, Tier 2, Tier 3 Roles and Escalation Ladders
111. `siem-architecture-log-pipeline`: SIEM Architecture: Log Ingestion, Normalization, and Parsing
112. `alert-triage-investigation`: Alert Triage: Validating True Positives vs False Positives
113. `ioc-extraction-correlation`: Extracting and Correlating Indicators of Compromise (IOCs)
114. `incident-response-lifecycle`: Incident Response Lifecycle (NIST SP 800-61 / SANS Framework)
115. `soc-playbooks-runbooks`: Incident Containment Playbooks and Standard Operating Procedures
116. `post-incident-reporting`: Root Cause Analysis, Timeline Reconstruction, and Post-Mortem Reporting

#### Module 19: Network Defense & Hardening (`network-defense-hardening`)
117. `device-hardening-best-practices`: Hardening Routers and Switches (Disabling Unneeded Services)
118. `aaa-radius-tacacs`: AAA Architecture: Authentication, Authorization, Accounting (RADIUS/TACACS+)
119. `port-security-mac-limiting`: Switch Port Security: Static, Dynamic, and Sticky MAC Limiting
120. `dhcp-snooping-mitigation`: DHCP Snooping Implementation and Trusted Ports
121. `dynamic-arp-inspection-dai`: Dynamic ARP Inspection (DAI) Configuration
122. `ip-source-guard-ipsg`: IP Source Guard (IPSG) Defense Against IP Spoofing
123. `network-segmentation-microseg`: Zero Trust Network Architecture and Microsegmentation
124. `honeypots-deception-tech`: Deception Technology, Canaries, and Network Honeypots
125. `vpn-architecture-remote-access`: Enterprise VPN Architecture (Site-to-Site vs Remote Access)
126. `patch-mgmt-firmware-updates`: Network Device Patch Management, CVE Tracking, and Firmware Integrity

---

## 3. Lesson Content Payload Standard

Each lesson in the `lessons` table stores standard Markdown enhanced with educational cues:
* **Conceptual Overview**: Context and protocol purpose.
* **Protocol Frame / Packet Anatomy**: Visual ASCII or Mermaid headers.
* **Practical Wireshark / CLI Output**: Real-world captures.
* **Cybersecurity Defense Notes**: Common vulnerabilities and mitigation strategies.
* **Check Your Understanding**: Interactive self-check points.
