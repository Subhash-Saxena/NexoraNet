"""Seed script for Step 19 CTF Challenges & Training Tracks.

Seeds 40 comprehensive challenges across 4 difficulties and 12 categories,
with 5 structured curriculum training tracks.
All data is 100% synthetic, offline, and non-destructive.
"""

import json
from typing import Any

from app.models.challenge import (
    Challenge,
    ChallengeEvidence,
    ChallengeHint,
    ChallengeTrack,
    ChallengeTrackItem,
)
from app.models.enums import (
    ChallengeCategory,
    ChallengeDifficulty,
    ChallengeType,
)
from app.services.challenges.flag_service import flag_service
from sqlalchemy import select
from sqlalchemy.orm import Session

RAW_CHALLENGES: list[dict[str, Any]] = [
    # =========================================================================
    # BEGINNER (10 Challenges)
    # =========================================================================
    {
        "challenge_id": "CHAL-BEG-001",
        "title": "Identify the Private IP Address",
        "category": ChallengeCategory.NETWORKING,
        "difficulty": ChallengeDifficulty.BEGINNER,
        "challenge_type": ChallengeType.IP_ADDRESS,
        "points": 50,
        "estimated_minutes": 10,
        "description": "Analyze network interface configuration output and identify the RFC 1918 private IPv4 address assigned to the host.",
        "scenario": "A junior workstation on the internal corporate network received an IP configuration via DHCP. Inspect the synthetic interface data to find the private address.",
        "learning_objectives": ["Distinguish RFC 1918 private IPv4 ranges (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16) from public routable addresses."],
        "prerequisites": ["IPv4 addressing basics", "RFC 1918 private ranges"],
        "environment_description": "Synthetic Linux workstation network interface status (ip addr show).",
        "tasks": ["Inspect interface eth0 details in the evidence tab.", "Identify the IPv4 address belonging to an RFC 1918 range.", "Submit the flag in format: FLAG{10.10.10.25}."],
        "skills_tested": ["IPv4 addressing", "Network interface inspection", "RFC 1918 subnetting"],
        "related_lesson_slug": "ipv4-addressing-and-subnetting",
        "related_lab_slug": "ip-addressing-basics",
        "flag": "FLAG{10.10.10.25}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "In RFC 1918, 10.0.0.0/8 is reserved for private networks. The interface eth0 is bound to 10.10.10.25/24, whereas 203.0.113.5 on eth1 is a public test address.",
        "common_mistakes": ["Confusing the loopback address 127.0.0.1 with private LAN IP.", "Submitting the subnet mask instead of host IP."],
        "hints": [
            {"hint_number": 1, "hint_text": "Remember RFC 1918 ranges: 10.x.x.x, 172.16-31.x.x, 192.168.x.x.", "penalty_percent": 10.0, "penalty_points": 5},
            {"hint_number": 2, "hint_text": "Look closely at interface eth0 in the synthetic network dump.", "penalty_percent": 25.0, "penalty_points": 12},
        ],
        "evidence": [
            {
                "evidence_type": "CONFIG",
                "title": "workstation_ip_addr.txt",
                "description": "Output of synthetic 'ip addr show' command",
                "content": json.dumps({
                    "interfaces": [
                        {"name": "lo", "inet": "127.0.0.1/8", "status": "UP"},
                        {"name": "eth0", "inet": "10.10.10.25/24", "status": "UP", "mac": "00:1a:2b:3c:4d:5e"},
                        {"name": "eth1", "inet": "203.0.113.5/24", "status": "UP", "mac": "00:1a:2b:3c:4d:5f"}
                    ]
                })
            }
        ]
    },
    {
        "challenge_id": "CHAL-BEG-002",
        "title": "Find the Default Gateway",
        "category": ChallengeCategory.NETWORKING,
        "difficulty": ChallengeDifficulty.BEGINNER,
        "challenge_type": ChallengeType.IP_ADDRESS,
        "points": 50,
        "estimated_minutes": 10,
        "description": "Inspect the synthetic routing table of a corporate server and determine the default gateway IP address.",
        "scenario": "A host cannot communicate beyond its local broadcast domain. The administrator asks you to verify the configured default route destination.",
        "learning_objectives": ["Understand default routes (0.0.0.0/0) and next-hop gateway resolution."],
        "prerequisites": ["Routing fundamentals"],
        "environment_description": "Synthetic Linux kernel IP routing table.",
        "tasks": ["Examine the route table in evidence.", "Find the next-hop IP associated with destination 0.0.0.0.", "Submit flag in format: FLAG{192.168.1.1}."],
        "skills_tested": ["Routing table analysis", "Default gateway identification"],
        "related_lesson_slug": "routing-fundamentals",
        "flag": "FLAG{192.168.1.1}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "The default route is represented by Destination 0.0.0.0 with Genmask 0.0.0.0. Its Gateway column specifies 192.168.1.1 as the next-hop router.",
        "common_mistakes": ["Entering 0.0.0.0 instead of the gateway IP.", "Confusing destination IP with gateway IP."],
        "hints": [
            {"hint_number": 1, "hint_text": "Look for the entry where destination is 0.0.0.0/0 or 'default'.", "penalty_percent": 15.0, "penalty_points": 7},
        ],
        "evidence": [
            {
                "evidence_type": "CONFIG",
                "title": "routing_table.txt",
                "description": "Synthetic route -n dump",
                "content": json.dumps([
                    {"destination": "0.0.0.0", "gateway": "192.168.1.1", "genmask": "0.0.0.0", "iface": "eth0"},
                    {"destination": "192.168.1.0", "gateway": "0.0.0.0", "genmask": "255.255.255.0", "iface": "eth0"}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-BEG-003",
        "title": "Identify TCP vs UDP Protocol",
        "category": ChallengeCategory.NETWORKING,
        "difficulty": ChallengeDifficulty.BEGINNER,
        "challenge_type": ChallengeType.SHORT_ANSWER,
        "points": 50,
        "estimated_minutes": 10,
        "description": "Determine whether the recorded packet transmission represents a connection-oriented (TCP) or connectionless (UDP) transport protocol.",
        "scenario": "A firewall log records high-speed audio-streaming traffic with low overhead and no sequence acknowledgments.",
        "learning_objectives": ["Understand transport layer differences between TCP and UDP."],
        "prerequisites": ["Transport layer protocols"],
        "environment_description": "Synthetic network packet header dissection.",
        "tasks": ["Inspect the transport header fields in evidence.", "Identify whether the flow uses TCP or UDP.", "Submit flag in format: FLAG{udp}."],
        "skills_tested": ["Transport protocol analysis", "Header field inspection"],
        "related_lesson_slug": "tcp-and-udp-transport-protocols",
        "flag": "FLAG{udp}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "The packet header contains Source Port, Destination Port, Length, and Checksum without Sequence or Acknowledgment numbers or TCP flags, matching RFC 768 UDP.",
        "common_mistakes": ["Assuming all streaming uses TCP.", "Confusing TCP sequence numbers with UDP length."],
        "hints": [
            {"hint_number": 1, "hint_text": "Check if SYN/ACK flags or 32-bit sequence numbers exist in the header.", "penalty_percent": 15.0, "penalty_points": 7},
        ],
        "evidence": [
            {
                "evidence_type": "PCAP",
                "title": "packet_header.json",
                "description": "Transport header fields",
                "content": json.dumps({
                    "transport_layer": "UDP",
                    "src_port": 5004,
                    "dst_port": 5004,
                    "length": 160,
                    "checksum": "0x4a12",
                    "flags": None
                })
            }
        ]
    },
    {
        "challenge_id": "CHAL-BEG-004",
        "title": "Find the Primary DNS Server",
        "category": ChallengeCategory.NETWORKING,
        "difficulty": ChallengeDifficulty.BEGINNER,
        "challenge_type": ChallengeType.IP_ADDRESS,
        "points": 50,
        "estimated_minutes": 10,
        "description": "Examine the client system DNS resolver configuration and determine the primary nameserver IP.",
        "scenario": "A workstation cannot resolve intranet hostnames. Check the /etc/resolv.conf synthetic file to identify which nameserver is queried first.",
        "learning_objectives": ["Understand DNS client resolver configuration."],
        "prerequisites": ["DNS resolution basics"],
        "environment_description": "Synthetic resolv.conf configuration file.",
        "tasks": ["Inspect resolv.conf file in evidence.", "Identify the first active nameserver listed.", "Submit flag in format: FLAG{192.0.2.53}."],
        "skills_tested": ["DNS resolver configuration", "System settings inspection"],
        "related_lesson_slug": "dns-architecture-and-resolution",
        "flag": "FLAG{192.0.2.53}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "In standard resolver configuration, the first nameserver line specifies the primary DNS server queried by getaddrinfo.",
        "common_mistakes": ["Submitting the secondary nameserver instead of primary."],
        "hints": [
            {"hint_number": 1, "hint_text": "The primary nameserver is listed on the first 'nameserver' directive.", "penalty_percent": 10.0, "penalty_points": 5},
        ],
        "evidence": [
            {
                "evidence_type": "CONFIG",
                "title": "resolv.conf",
                "description": "Synthetic DNS resolver file",
                "content": "search corp.local\nnameserver 192.0.2.53\nnameserver 192.0.2.54\noptions timeout:2"
            }
        ]
    },
    {
        "challenge_id": "CHAL-BEG-005",
        "title": "Identify the Standard HTTP Port",
        "category": ChallengeCategory.NETWORKING,
        "difficulty": ChallengeDifficulty.BEGINNER,
        "challenge_type": ChallengeType.NUMERICAL,
        "points": 50,
        "estimated_minutes": 5,
        "description": "Identify the default IANA well-known destination port used for unencrypted HTTP traffic.",
        "scenario": "A perimeter firewall rule allows inbound unencrypted web browsing traffic. Identify the port number specified in the rule.",
        "learning_objectives": ["Identify standard IANA well-known transport ports."],
        "prerequisites": ["Port numbers and services"],
        "environment_description": "Synthetic firewall rule list.",
        "tasks": ["Inspect the firewall rule in evidence.", "Identify the port corresponding to service 'http'.", "Submit flag in format: FLAG{80}."],
        "skills_tested": ["Port service mapping", "Firewall rule analysis"],
        "related_lesson_slug": "ports-protocols-and-services",
        "flag": "FLAG{80}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Port 80 is the IANA standard port for HTTP. (Port 443 is HTTPS).",
        "common_mistakes": ["Confusing HTTP (80) with HTTPS (443) or alternative 8080."],
        "hints": [
            {"hint_number": 1, "hint_text": "HTTP is well-known port 80; HTTPS is 443.", "penalty_percent": 10.0, "penalty_points": 5},
        ],
        "evidence": [
            {
                "evidence_type": "CONFIG",
                "title": "firewall_rules.txt",
                "description": "Perimeter ingress rules",
                "content": json.dumps([
                    {"rule_id": 1, "action": "ALLOW", "proto": "TCP", "port": 80, "service": "HTTP"},
                    {"rule_id": 2, "action": "ALLOW", "proto": "TCP", "port": 443, "service": "HTTPS"}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-BEG-006",
        "title": "Identify a TCP Three-Way Handshake",
        "category": ChallengeCategory.PACKET_ANALYSIS,
        "difficulty": ChallengeDifficulty.BEGINNER,
        "challenge_type": ChallengeType.PACKET_ANALYSIS,
        "points": 75,
        "estimated_minutes": 15,
        "description": "Analyze a sequence of three synthetic network packets and identify the flag combination that establishes a reliable TCP connection.",
        "scenario": "A security analyst is reviewing a packet trace to verify whether an inbound client successfully completed a connection.",
        "learning_objectives": ["Understand TCP connection establishment sequence (SYN, SYN-ACK, ACK)."],
        "prerequisites": ["TCP 3-way handshake"],
        "environment_description": "Synthetic packet capture stream.",
        "tasks": ["Inspect the three sequential packets in evidence.", "Identify the flags present in packet 1, 2, and 3.", "Submit flag in format: FLAG{syn_synack_ack}."],
        "skills_tested": ["Packet sequence analysis", "TCP flag interpretation"],
        "related_lesson_slug": "tcp-3-way-handshake-and-connection-lifecycle",
        "flag": "FLAG{syn_synack_ack}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "A complete TCP handshake proceeds in order: Client sends SYN -> Server responds SYN-ACK -> Client replies ACK.",
        "common_mistakes": ["Confusing RST-ACK with SYN-ACK."],
        "hints": [
            {"hint_number": 1, "hint_text": "Packet 1 is SYN, Packet 2 is SYN-ACK, Packet 3 is ACK.", "penalty_percent": 15.0, "penalty_points": 10},
        ],
        "evidence": [
            {
                "evidence_type": "PCAP",
                "title": "handshake.pcap.json",
                "description": "Synthetic 3-packet handshake trace",
                "content": json.dumps([
                    {"packet_no": 1, "flags": ["SYN"], "seq": 1000, "ack": 0},
                    {"packet_no": 2, "flags": ["SYN", "ACK"], "seq": 5000, "ack": 1001},
                    {"packet_no": 3, "flags": ["ACK"], "seq": 1001, "ack": 5001}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-BEG-007",
        "title": "Find the Subnet Broadcast Address",
        "category": ChallengeCategory.NETWORKING,
        "difficulty": ChallengeDifficulty.BEGINNER,
        "challenge_type": ChallengeType.IP_ADDRESS,
        "points": 60,
        "estimated_minutes": 10,
        "description": "Given an IPv4 subnet of 192.168.1.0/24, determine the directed broadcast address for the local segment.",
        "scenario": "A system administrator needs to configure an ARP broadcast diagnostic ping across the entire local subnet.",
        "learning_objectives": ["Calculate subnet directed broadcast addresses."],
        "prerequisites": ["IPv4 subnetting"],
        "environment_description": "Subnet configuration worksheet.",
        "tasks": ["Calculate the highest host address in 192.168.1.0/24 where all host bits are 1.", "Submit flag in format: FLAG{192.168.1.255}."],
        "skills_tested": ["Subnet calculation", "Broadcast address identification"],
        "related_lesson_slug": "ipv4-addressing-and-subnetting",
        "flag": "FLAG{192.168.1.255}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "In a /24 prefix (255.255.255.0), host bits span .0 to .255. .0 is network ID, and .255 is directed broadcast.",
        "common_mistakes": ["Using .254 (highest usable host) instead of .255 (broadcast)."],
        "hints": [
            {"hint_number": 1, "hint_text": "With a /24 mask, the last octet with all 1s is 255.", "penalty_percent": 10.0, "penalty_points": 6},
        ],
        "evidence": [
            {
                "evidence_type": "CONFIG",
                "title": "subnet_info.txt",
                "description": "Network CIDR specification",
                "content": "Network: 192.168.1.0/24\nNetmask: 255.255.255.0\nUsable range: 192.168.1.1 - 192.168.1.254"
            }
        ]
    },
    {
        "challenge_id": "CHAL-BEG-008",
        "title": "Identify a Failed Connection (TCP RST)",
        "category": ChallengeCategory.PACKET_ANALYSIS,
        "difficulty": ChallengeDifficulty.BEGINNER,
        "challenge_type": ChallengeType.SHORT_ANSWER,
        "points": 60,
        "estimated_minutes": 10,
        "description": "Inspect a packet response indicating a rejected connection attempt to a closed port.",
        "scenario": "A client attempts to connect to port 22 on a server where sshd is not running. The server immediately terminates the connection with a specific flag combination.",
        "learning_objectives": ["Identify TCP connection rejection via RST/ACK."],
        "prerequisites": ["TCP flags"],
        "environment_description": "Synthetic packet stream of rejected connection.",
        "tasks": ["Inspect the response packet from the server in evidence.", "Identify the TCP flags sent to reject the connection.", "Submit flag in format: FLAG{tcp_rst_ack}."],
        "skills_tested": ["TCP flag analysis", "Connection rejection identification"],
        "related_lesson_slug": "tcp-3-way-handshake-and-connection-lifecycle",
        "flag": "FLAG{tcp_rst_ack}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "When a port is closed, the TCP stack responds to incoming SYN packets with a RST,ACK segment to reset the attempt.",
        "common_mistakes": ["Confusing FIN (graceful close) with RST (abrupt reset)."],
        "hints": [
            {"hint_number": 1, "hint_text": "Look for the Reset (RST) and Acknowledgment (ACK) flags.", "penalty_percent": 15.0, "penalty_points": 9},
        ],
        "evidence": [
            {
                "evidence_type": "PCAP",
                "title": "rejected_connection.json",
                "description": "Packet dump of closed port rejection",
                "content": json.dumps({
                    "packet_1": {"src": "10.0.0.5", "dst": "10.0.0.10:22", "flags": ["SYN"]},
                    "packet_2": {"src": "10.0.0.10:22", "dst": "10.0.0.5", "flags": ["RST", "ACK"], "reason": "Connection Refused"}
                })
            }
        ]
    },
    {
        "challenge_id": "CHAL-BEG-009",
        "title": "Identify Network Layer Protocol",
        "category": ChallengeCategory.NETWORKING,
        "difficulty": ChallengeDifficulty.BEGINNER,
        "challenge_type": ChallengeType.SHORT_ANSWER,
        "points": 50,
        "estimated_minutes": 5,
        "description": "Identify the Layer 3 protocol responsible for packet addressing and routing across internetworks.",
        "scenario": "An analyst reviews an Ethernet II frame header containing EtherType 0x0800.",
        "learning_objectives": ["Recognize Layer 3 IPv4 EtherType mapping."],
        "prerequisites": ["OSI Layer 3 and Ethernet framing"],
        "environment_description": "Synthetic Ethernet frame dissection.",
        "tasks": ["Inspect EtherType in frame header.", "Determine which Layer 3 protocol is encapsulated.", "Submit flag in format: FLAG{ipv4}."],
        "skills_tested": ["EtherType identification", "Network layer protocol mapping"],
        "related_lesson_slug": "osi-model-deep-dive",
        "flag": "FLAG{ipv4}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "EtherType 0x0800 designates IPv4 encapsulation. (0x86DD designates IPv6, 0x0806 designates ARP).",
        "common_mistakes": ["Entering IPv6 or ARP instead of IPv4."],
        "hints": [
            {"hint_number": 1, "hint_text": "EtherType 0x0800 corresponds to Internet Protocol version 4.", "penalty_percent": 10.0, "penalty_points": 5},
        ],
        "evidence": [
            {
                "evidence_type": "PCAP",
                "title": "ethernet_frame.json",
                "description": "Ethernet II header dump",
                "content": json.dumps({"dst_mac": "ff:ff:ff:ff:ff:ff", "src_mac": "00:11:22:33:44:55", "ethertype": "0x0800"})
            }
        ]
    },
    {
        "challenge_id": "CHAL-BEG-010",
        "title": "Basic Alert Triage & Severity",
        "category": ChallengeCategory.SOC_ANALYSIS,
        "difficulty": ChallengeDifficulty.BEGINNER,
        "challenge_type": ChallengeType.SOC_ANALYSIS,
        "points": 75,
        "estimated_minutes": 15,
        "description": "Triage three incoming SOC alerts and identify which alert warrants CRITICAL priority classification.",
        "scenario": "You are a Tier 1 SOC analyst reviewing the morning queue. Three alerts fired: informational policy notification, low-priority ping sweep, and an active ransomware Canary file modification.",
        "learning_objectives": ["Prioritize alerts based on threat impact and severity indicators."],
        "prerequisites": ["SOC alert triage basics"],
        "environment_description": "Synthetic SOC alert queue snapshot.",
        "tasks": ["Review the three alerts in evidence.", "Identify the severity level of Alert ALT-103.", "Submit flag in format: FLAG{critical}."],
        "skills_tested": ["Alert triage", "Severity prioritization"],
        "related_lesson_slug": "soc-alert-triage-fundamentals",
        "flag": "FLAG{critical}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Canary file modification in user directories indicates immediate ransomware activity, demanding CRITICAL priority response.",
        "common_mistakes": ["Assigning LOW or MEDIUM to active disk encryption triggers."],
        "hints": [
            {"hint_number": 1, "hint_text": "Ransomware canary file alerts are always CRITICAL severity.", "penalty_percent": 15.0, "penalty_points": 10},
        ],
        "evidence": [
            {
                "evidence_type": "DETECTION_ALERT",
                "title": "alert_queue.json",
                "description": "Three pending SOC alerts",
                "content": json.dumps([
                    {"alert_id": "ALT-101", "name": "ICMP Ping Sweep", "severity": "LOW"},
                    {"alert_id": "ALT-102", "name": "Password Expiry Notice", "severity": "INFO"},
                    {"alert_id": "ALT-103", "name": "Ransomware Canary File Tamper", "severity": "CRITICAL"}
                ])
            }
        ]
    },

    # =========================================================================
    # INTERMEDIATE (12 Challenges)
    # =========================================================================
    {
        "challenge_id": "CHAL-INT-001",
        "title": "DNS NXDOMAIN Spike Investigation",
        "category": ChallengeCategory.PACKET_ANALYSIS,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.PACKET_ANALYSIS,
        "points": 100,
        "estimated_minutes": 20,
        "description": "Investigate a synthetic packet capture where a host generates a massive burst of failed DNS queries.",
        "scenario": "A host infected with a Domain Generation Algorithm (DGA) malware family generates hundreds of non-existent domain queries per minute attempting to find an active C2 server.",
        "learning_objectives": ["Identify DGA and DNS anomalies through NXDOMAIN response codes."],
        "prerequisites": ["DNS protocol", "Packet analysis"],
        "environment_description": "Synthetic DNS traffic capture with RCODE counts.",
        "tasks": ["Inspect the DNS query logs in evidence.", "Identify the anomalous query behavior pattern.", "Submit flag: FLAG{dns_nxdomain_spike}."],
        "skills_tested": ["DNS packet inspection", "DGA recognition", "Error code analysis"],
        "related_lesson_slug": "dns-architecture-and-resolution",
        "related_mitre_technique": "T1568.002",
        "flag": "FLAG{dns_nxdomain_spike}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "The host generated 184 queries in 2 minutes, 142 of which returned RCODE 3 (NXDOMAIN), characteristic of DGA malware C2 rendezvous attempts.",
        "common_mistakes": ["Assuming legitimate web browsing causes 80%+ NXDOMAIN responses."],
        "hints": [
            {"hint_number": 1, "hint_text": "Look at the proportion of RCODE 3 (NXDOMAIN) responses.", "penalty_percent": 15.0, "penalty_points": 15},
            {"hint_number": 2, "hint_text": "The pattern indicates an NXDOMAIN spike.", "penalty_percent": 25.0, "penalty_points": 25},
        ],
        "evidence": [
            {
                "evidence_type": "PCAP",
                "title": "dns_stream.json",
                "description": "DNS query records with RCODE statistics",
                "content": json.dumps({
                    "src_ip": "10.10.10.45",
                    "total_queries": 184,
                    "rcode_distribution": {"NOERROR (0)": 42, "NXDOMAIN (3)": 142},
                    "sample_domains": ["x892ka.biz", "plm9812.info", "zzq901a.org"]
                })
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-002",
        "title": "TCP Half-Open SYN Stealth Scan",
        "category": ChallengeCategory.PACKET_ANALYSIS,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.PACKET_ANALYSIS,
        "points": 100,
        "estimated_minutes": 20,
        "description": "Examine a packet capture containing a scan where the sender sends SYN, receives SYN-ACK, and immediately resets with RST without completing the handshake.",
        "scenario": "A port scanner probes open services while avoiding application-layer logging by never completing the 3-way handshake.",
        "learning_objectives": ["Identify TCP SYN stealth scan techniques."],
        "prerequisites": ["TCP flags", "Reconnaissance techniques"],
        "environment_description": "Synthetic port scan packet capture.",
        "tasks": ["Inspect the flag sequences in the scan trace.", "Identify the scanning technique.", "Submit flag: FLAG{syn_stealth_scan}."],
        "skills_tested": ["Port scan pattern recognition", "TCP state dissection"],
        "related_mitre_technique": "T1046",
        "flag": "FLAG{syn_stealth_scan}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "A SYN scan (nmap -sS) sends a SYN, waits for SYN-ACK to confirm the port is open, and immediately replies with RST to abort the connection.",
        "common_mistakes": ["Confusing a full connect scan (-sT) with half-open SYN scan (-sS)."],
        "hints": [
            {"hint_number": 1, "hint_text": "Notice that the client sends RST instead of final ACK after server SYN-ACK.", "penalty_percent": 15.0, "penalty_points": 15},
        ],
        "evidence": [
            {
                "evidence_type": "PCAP",
                "title": "scan_trace.json",
                "description": "Probe sequence for ports 21, 22, 80",
                "content": json.dumps([
                    {"step": 1, "src": "192.168.1.100", "dst": "192.168.1.50:80", "flag": "SYN"},
                    {"step": 2, "src": "192.168.1.50:80", "dst": "192.168.1.100", "flag": "SYN,ACK"},
                    {"step": 3, "src": "192.168.1.100", "dst": "192.168.1.50:80", "flag": "RST"}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-003",
        "title": "Suspicious Port Pattern Hunt",
        "category": ChallengeCategory.NETWORKING,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.SHORT_ANSWER,
        "points": 100,
        "estimated_minutes": 15,
        "description": "Correlate netstat output and identify a suspicious listening port commonly associated with Metasploit payload defaults.",
        "scenario": "A Linux server shows an unusual process listening on port 4444 bound to all interfaces (0.0.0.0).",
        "learning_objectives": ["Identify default adversary backdoor listening ports."],
        "prerequisites": ["Port analysis", "Netstat inspection"],
        "environment_description": "Synthetic netstat -tuln output.",
        "tasks": ["Inspect listening sockets in evidence.", "Identify the port and service type.", "Submit flag: FLAG{port_4444_bindshell}."],
        "skills_tested": ["Port reconnaissance", "Backdoor detection"],
        "related_mitre_technique": "T1571",
        "flag": "FLAG{port_4444_bindshell}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Port 4444 is historically the default listening port for Metasploit bind/reverse shells.",
        "common_mistakes": ["Overlooking port 4444 as benign."],
        "hints": [
            {"hint_number": 1, "hint_text": "Port 4444 is widely known as Metasploit's default shell port.", "penalty_percent": 15.0, "penalty_points": 15},
        ],
        "evidence": [
            {
                "evidence_type": "CONFIG",
                "title": "netstat_output.txt",
                "description": "Listening sockets",
                "content": "tcp 0 0 0.0.0.0:22 0.0.0.0:* LISTEN 812/sshd\ntcp 0 0 0.0.0.0:80 0.0.0.0:* LISTEN 945/nginx\ntcp 0 0 0.0.0.0:4444 0.0.0.0:* LISTEN 4892/nc"
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-004",
        "title": "SIEM Authentication Brute-Force",
        "category": ChallengeCategory.SIEM,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.LOG_ANALYSIS,
        "points": 100,
        "estimated_minutes": 20,
        "description": "Query synthetic Windows Event logs to identify a brute-force authentication attack reaching threshold.",
        "scenario": "A domain controller records 45 consecutive Event ID 4625 (Logon Failure) entries for account 'administrator' within 60 seconds from an internal IP.",
        "learning_objectives": ["Analyze Windows authentication failure logs (Event ID 4625)."],
        "prerequisites": ["Windows Security Event logs", "SIEM search"],
        "environment_description": "Synthetic Windows Event Log dataset.",
        "tasks": ["Filter logs by Event ID 4625.", "Identify the trigger threshold condition.", "Submit flag: FLAG{event_4625_threshold}."],
        "skills_tested": ["SIEM log correlation", "Authentication brute force detection"],
        "related_lesson_slug": "siem-query-languages-and-search",
        "related_mitre_technique": "T1110.001",
        "flag": "FLAG{event_4625_threshold}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Event 4625 corresponds to An account failed to log on. Rapid occurrences against a single user indicate password guessing/brute force.",
        "common_mistakes": ["Confusing Event 4624 (Logon Success) with 4625 (Logon Failure)."],
        "hints": [
            {"hint_number": 1, "hint_text": "Windows Event ID 4625 represents logon failures.", "penalty_percent": 15.0, "penalty_points": 15},
        ],
        "evidence": [
            {
                "evidence_type": "SIEM_LOG",
                "title": "auth_failures.json",
                "description": "Windows Security Event Logs",
                "content": json.dumps([
                    {"event_id": 4625, "user": "administrator", "src_ip": "10.10.10.88", "count": 45, "time_window": "60s", "status": "0xC000006A"}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-005",
        "title": "HTTP 500 Error Pattern Spike",
        "category": ChallengeCategory.SIEM,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.LOG_ANALYSIS,
        "points": 100,
        "estimated_minutes": 15,
        "description": "Analyze web server access logs to uncover SQL injection attempts causing internal database errors.",
        "scenario": "A web application starts throwing HTTP 500 Internal Server Errors in response to URL query parameters containing UNION SELECT statements.",
        "learning_objectives": ["Correlate web server status codes with malicious payloads."],
        "prerequisites": ["Web server log analysis", "SQL injection fundamentals"],
        "environment_description": "Synthetic Nginx web server access logs.",
        "tasks": ["Inspect the HTTP request query strings and status codes in evidence.", "Identify the attack type.", "Submit flag: FLAG{sqli_union_select}."],
        "skills_tested": ["Web access log investigation", "SQLi pattern detection"],
        "related_mitre_technique": "T1190",
        "flag": "FLAG{sqli_union_select}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Requests containing 'id=1 UNION SELECT null,username,password FROM users' caused HTTP 500 database execution failures.",
        "common_mistakes": ["Assuming 500 errors are always server infrastructure bugs without checking query parameters."],
        "hints": [
            {"hint_number": 1, "hint_text": "Look for SQL syntax keywords in the URI query string.", "penalty_percent": 15.0, "penalty_points": 15},
        ],
        "evidence": [
            {
                "evidence_type": "SIEM_LOG",
                "title": "nginx_access.log",
                "description": "Web server request records",
                "content": '198.51.100.22 - - [20/Sep/2026:10:14:02 +0000] "GET /products.php?id=1%20UNION%20SELECT%201,2,table_name%20FROM%20information_schema.tables HTTP/1.1" 500 1024'
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-006",
        "title": "ARP Cache Poisoning Anomaly",
        "category": ChallengeCategory.PACKET_ANALYSIS,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.PACKET_ANALYSIS,
        "points": 100,
        "estimated_minutes": 20,
        "description": "Detect an ARP spoofing attack where an attacker maps the default gateway IP to their own MAC address.",
        "scenario": "A workstation receives unsolicited gratuitous ARP replies claiming that the default gateway 192.168.1.1 now resides at a different MAC address.",
        "learning_objectives": ["Identify ARP spoofing and Man-in-the-Middle indicators."],
        "prerequisites": ["ARP protocol and caching"],
        "environment_description": "Synthetic ARP packet capture and host ARP cache.",
        "tasks": ["Compare the legitimate gateway MAC with the unsolicited ARP reply.", "Identify the anomaly.", "Submit flag: FLAG{arp_duplicate_mac}."],
        "skills_tested": ["ARP spoofing detection", "MAC address correlation"],
        "related_mitre_technique": "T1557.002",
        "flag": "FLAG{arp_duplicate_mac}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "The attacker broadcast gratuitous ARP replies associating gateway 192.168.1.1 with attacker MAC aa:bb:cc:dd:ee:ff.",
        "common_mistakes": ["Overlooking duplicate IP-to-MAC associations."],
        "hints": [
            {"hint_number": 1, "hint_text": "Look at the MAC address in the gratuitous ARP reply.", "penalty_percent": 15.0, "penalty_points": 15},
        ],
        "evidence": [
            {
                "evidence_type": "PCAP",
                "title": "arp_traffic.json",
                "description": "ARP traffic logs",
                "content": json.dumps([
                    {"sender_ip": "192.168.1.1", "sender_mac": "00:00:5e:00:53:01", "note": "Original Gateway"},
                    {"sender_ip": "192.168.1.1", "sender_mac": "aa:bb:cc:dd:ee:ff", "note": "Unsolicited Gratuitous ARP"}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-007",
        "title": "Network Traffic Beaconing Interval",
        "category": ChallengeCategory.PACKET_ANALYSIS,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.PACKET_ANALYSIS,
        "points": 100,
        "estimated_minutes": 20,
        "description": "Identify periodic network beaconing intervals in synthetic egress flow telemetry.",
        "scenario": "A compromised endpoint establishes regular outbound HTTPS connections every 60 seconds with minor jitter.",
        "learning_objectives": ["Detect periodic C2 beaconing using connection timestamps."],
        "prerequisites": ["C2 beaconing concepts"],
        "environment_description": "Synthetic firewall egress connection timestamps.",
        "tasks": ["Compute the delta between consecutive outbound connections in evidence.", "Determine the nominal beacon period.", "Submit flag: FLAG{beacon_60s_jitter}."],
        "skills_tested": ["Beaconing detection", "Time-series connection analysis"],
        "related_mitre_technique": "T1071.001",
        "flag": "FLAG{beacon_60s_jitter}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Connection intervals are: 59.8s, 60.2s, 60.1s, 59.9s, demonstrating a 60-second beacon with low jitter.",
        "common_mistakes": ["Assuming beaconing must be strictly 100% exact to the millisecond."],
        "hints": [
            {"hint_number": 1, "hint_text": "Subtract timestamp N from timestamp N+1 to find the ~60s interval.", "penalty_percent": 15.0, "penalty_points": 15},
        ],
        "evidence": [
            {
                "evidence_type": "PCAP",
                "title": "egress_connections.json",
                "description": "Connection start timestamps to 203.0.113.80",
                "content": json.dumps([
                    "2026-10-01T10:00:00Z",
                    "2026-10-01T10:01:00Z",
                    "2026-10-01T10:02:00Z",
                    "2026-10-01T10:03:00Z"
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-008",
        "title": "Suspicious IOC Normalization",
        "category": ChallengeCategory.THREAT_INTELLIGENCE,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.SHORT_ANSWER,
        "points": 100,
        "estimated_minutes": 15,
        "description": "Extract and classify an obfuscated indicator of compromise (defanged IP) from an incident report.",
        "scenario": "A threat intelligence report mentions a defanged C2 address: '198[.]51[.]100[.]44'. Refang and classify the indicator.",
        "learning_objectives": ["Understand IOC defanging and normalization conventions."],
        "prerequisites": ["Threat intelligence observables"],
        "environment_description": "Synthetic threat bulletin snippet.",
        "tasks": ["Refang the bracketed IP address.", "Classify indicator type.", "Submit flag: FLAG{malicious_ipv4_c2}."],
        "skills_tested": ["IOC refanging", "Observable classification"],
        "related_lesson_slug": "threat-intelligence-sources-and-feeds",
        "flag": "FLAG{malicious_ipv4_c2}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Defanged IP 198[.]51[.]100[.]44 refangs to 198.51.100.44 and represents a malicious IPv4 C2 node.",
        "common_mistakes": ["Leaving brackets in the submitted address."],
        "hints": [
            {"hint_number": 1, "hint_text": "Remove brackets around dots to refang the IP.", "penalty_percent": 10.0, "penalty_points": 10},
        ],
        "evidence": [
            {
                "evidence_type": "IOC",
                "title": "intel_bulletin.txt",
                "description": "Threat bulletin excerpt",
                "content": "Adversary infrastructure observed hosting Cobalt Strike teamserver at 198[.]51[.]100[.]44 on port 50050."
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-009",
        "title": "Detection Rule False Positive Analysis",
        "category": ChallengeCategory.DETECTION_ENGINEERING,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.DETECTION_ENGINEERING,
        "points": 100,
        "estimated_minutes": 20,
        "description": "Investigate why an educational Sigma rule for mass file access fired on a legitimate nightly backup job.",
        "scenario": "A detection rule 'Mass File Read' fired at 02:00 UTC. Telemetry reveals the actor was service account 'svc_backup'.",
        "learning_objectives": ["Analyze detection logic and identify exclusion opportunities."],
        "prerequisites": ["Detection engineering fundamentals"],
        "environment_description": "Synthetic rule YAML and firing context.",
        "tasks": ["Inspect the rule logic and alerting entity in evidence.", "Identify why it is a false positive.", "Submit flag: FLAG{backup_service_account}."],
        "skills_tested": ["False positive analysis", "Detection tuning"],
        "related_lesson_slug": "detection-engineering-and-rule-authoring",
        "flag": "FLAG{backup_service_account}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "The rule lacked an exclusion for the authorized backup account 'svc_backup', which performs planned bulk reads every night.",
        "common_mistakes": ["Assuming every alert firing indicates malicious compromise."],
        "hints": [
            {"hint_number": 1, "hint_text": "Check the user account that triggered the alert.", "penalty_percent": 15.0, "penalty_points": 15},
        ],
        "evidence": [
            {
                "evidence_type": "DETECTION_ALERT",
                "title": "firing_telemetry.json",
                "description": "Alert details and process owner",
                "content": json.dumps({"rule_name": "Mass File Read", "username": "svc_backup", "process": "backup_agent.exe", "files_accessed": 15000})
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-010",
        "title": "Endpoint Process Lineage Correlation",
        "category": ChallengeCategory.ENDPOINT_SECURITY,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.ENDPOINT_SECURITY,
        "points": 100,
        "estimated_minutes": 20,
        "description": "Investigate parent-child process relationships to detect Microsoft Office spawning a command interpreter.",
        "scenario": "An employee opened a malicious phishing document. Sysmon telemetry records WINWORD.EXE spawning powershell.exe.",
        "learning_objectives": ["Analyze process trees to identify execution evasion."],
        "prerequisites": ["Process parent-child relationships"],
        "environment_description": "Synthetic Sysmon Event ID 1 process creation log.",
        "tasks": ["Inspect process creation hierarchy in evidence.", "Identify parent and child processes.", "Submit flag: FLAG{winword_spawns_powershell}."],
        "skills_tested": ["Process tree investigation", "Phishing execution tracking"],
        "related_lesson_slug": "endpoint-investigation-fundamentals",
        "related_mitre_technique": "T1059.001",
        "flag": "FLAG{winword_spawns_powershell}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Office applications (WINWORD.EXE) spawning PowerShell or cmd.exe is a classic indicator of weaponized macro execution.",
        "common_mistakes": ["Looking at explorer.exe instead of WINWORD.EXE as parent."],
        "hints": [
            {"hint_number": 1, "hint_text": "Check ParentImage vs Image in Sysmon Event 1.", "penalty_percent": 15.0, "penalty_points": 15},
        ],
        "evidence": [
            {
                "evidence_type": "ENDPOINT_EVENT",
                "title": "sysmon_process_create.json",
                "description": "Sysmon Event ID 1 record",
                "content": json.dumps({
                    "event_id": 1,
                    "parent_image": "C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE",
                    "image": "C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe",
                    "command_line": "powershell.exe -w hidden -enc JABzAD0ATgBlAHcALQBPAGIAagBlAGMAdAA="
                })
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-011",
        "title": "Timeline Reconstruction of Breach",
        "category": ChallengeCategory.INCIDENT_RESPONSE,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.TIMELINE_ANALYSIS,
        "points": 100,
        "estimated_minutes": 20,
        "description": "Reconstruct initial access technique from an incident chronological event log.",
        "scenario": "An adversary logged in via VPN using compromised credentials at 03:00 UTC, bypassing perimeter defenses.",
        "learning_objectives": ["Build chronological incident timelines and identify initial access mechanisms."],
        "prerequisites": ["Incident timeline reconstruction"],
        "environment_description": "Synthetic incident timeline table.",
        "tasks": ["Review the chronologically sorted timeline in evidence.", "Identify the initial access MITRE technique.", "Submit flag: FLAG{t1078_valid_accounts}."],
        "skills_tested": ["Timeline reconstruction", "MITRE technique alignment"],
        "related_mitre_technique": "T1078",
        "flag": "FLAG{t1078_valid_accounts}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Adversary gained initial access via T1078 Valid Accounts over external VPN gateway.",
        "common_mistakes": ["Assuming phishing occurred when logs show direct valid credential VPN logon."],
        "hints": [
            {"hint_number": 1, "hint_text": "Initial entry was via external VPN with legitimate user credentials.", "penalty_percent": 15.0, "penalty_points": 15},
        ],
        "evidence": [
            {
                "evidence_type": "TIMELINE",
                "title": "incident_chronology.json",
                "description": "Chronological audit events",
                "content": json.dumps([
                    {"timestamp": "2026-10-01T03:00:15Z", "action": "VPN_LOGON_SUCCESS", "user": "finance_mgr", "ip": "198.51.100.99"},
                    {"timestamp": "2026-10-01T03:02:40Z", "action": "SMB_SHARE_MOUNT", "user": "finance_mgr", "target": "\\\\FS01\\Confidential"}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-INT-012",
        "title": "MITRE ATT&CK Defense Evasion Mapping",
        "category": ChallengeCategory.MITRE_ATTACK,
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "challenge_type": ChallengeType.MITRE_MAPPING,
        "points": 100,
        "estimated_minutes": 15,
        "description": "Map base64-encoded script commands to the corresponding MITRE ATT&CK Enterprise technique ID.",
        "scenario": "PowerShell was invoked with -EncodedCommand JABzAD0ATg... to obfuscate payload parameters.",
        "learning_objectives": ["Map obfuscation tactics to MITRE ATT&CK."],
        "prerequisites": ["MITRE ATT&CK Enterprise Matrix"],
        "environment_description": "Synthetic PowerShell command execution log.",
        "tasks": ["Analyze the evasion technique.", "Identify the MITRE ATT&CK sub-technique ID.", "Submit flag: FLAG{t1027_obfuscated_files}."],
        "skills_tested": ["MITRE ATT&CK mapping", "Defense evasion analysis"],
        "related_mitre_technique": "T1027",
        "flag": "FLAG{t1027_obfuscated_files}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "T1027 (Obfuscated Files or Information) encompasses encoding, compression, and encryption to evade signature detection.",
        "common_mistakes": ["Selecting Command and Scripting Interpreter (T1059) instead of Obfuscation (T1027)."],
        "hints": [
            {"hint_number": 1, "hint_text": "The adversary obfuscated their payload using base64 (T1027).", "penalty_percent": 15.0, "penalty_points": 15},
        ],
        "evidence": [
            {
                "evidence_type": "ENDPOINT_EVENT",
                "title": "powershell_cmd.txt",
                "description": "Executed command line",
                "content": "powershell.exe -NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand SQBFAFgA"
            }
        ]
    },

    # =========================================================================
    # ADVANCED (12 Challenges)
    # =========================================================================
    {
        "challenge_id": "CHAL-ADV-001",
        "title": "Multi-Source Network Exfiltration Investigation",
        "category": ChallengeCategory.PACKET_ANALYSIS,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.INVESTIGATION,
        "points": 150,
        "estimated_minutes": 30,
        "description": "Correlate packet captures and DNS query data to detect data exfiltration concealed in DNS TXT records.",
        "scenario": "An adversary staged proprietary CAD documents and chunked the ciphertext into outbound DNS TXT query queries directed to a rogue authoritative nameserver.",
        "learning_objectives": ["Detect DNS-based data exfiltration across high volume query logs."],
        "prerequisites": ["DNS tunneling", "Advanced packet forensics"],
        "environment_description": "Synthetic PCAP stream and DNS resolution metrics.",
        "tasks": ["Identify the high-volume query domain and payload delivery mechanism.", "Submit flag: FLAG{dns_txt_data_exfil}."],
        "skills_tested": ["DNS tunneling detection", "Data exfiltration analysis"],
        "related_mitre_technique": "T1048.003",
        "flag": "FLAG{dns_txt_data_exfil}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Over 2,000 queries to *.exfil.attacker.net contained hex-encoded file chunks in TXT query responses.",
        "common_mistakes": ["Assuming DNS traffic cannot carry file payloads."],
        "hints": [
            {"hint_number": 1, "hint_text": "Check TXT record queries to the authoritative subdomains.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "PCAP",
                "title": "dns_exfil.json",
                "description": "Captured DNS TXT query records",
                "content": json.dumps([
                    {"query": "chunk01.exfil.attacker.net", "type": "TXT", "length": 255},
                    {"query": "chunk02.exfil.attacker.net", "type": "TXT", "length": 255}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-002",
        "title": "Covert DNS Tunneling Decoding",
        "category": ChallengeCategory.THREAT_HUNTING,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.EVIDENCE_CORRELATION,
        "points": 150,
        "estimated_minutes": 25,
        "description": "Hunt for covert communication channels utilizing synthetic base64-encoded labels in subdomain prefixes.",
        "scenario": "A threat hunter discovers high entropy subdomain strings querying an external nameserver.",
        "learning_objectives": ["Hunt for DNS covert channels using entropy and character set analysis."],
        "prerequisites": ["Threat hunting hypothesis generation", "DNS protocol"],
        "environment_description": "Synthetic threat hunting query results.",
        "tasks": ["Form hypothesis around DNS tunneling.", "Identify the encoding scheme.", "Submit flag: FLAG{tunnel_b64_records}."],
        "skills_tested": ["DNS threat hunting", "Covert channel analysis"],
        "related_mitre_technique": "T1071.004",
        "flag": "FLAG{tunnel_b64_records}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Subdomain prefixes exhibited Shannon entropy above 4.5 and matched base64 character sets.",
        "common_mistakes": ["Mistaking CDN domain hashes for DNS tunneling."],
        "hints": [
            {"hint_number": 1, "hint_text": "Check the character set and padding of subdomain labels.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "IOC",
                "title": "dns_queries_entropy.json",
                "description": "Calculated entropy metrics",
                "content": json.dumps({"domain": "dGVzdF9jMg==.c2.net", "entropy": 4.82, "encoding": "base64"})
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-003",
        "title": "Slow-and-Low TCP Reconnaissance Pattern",
        "category": ChallengeCategory.DETECTION_ENGINEERING,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.DETECTION_ENGINEERING,
        "points": 150,
        "estimated_minutes": 25,
        "description": "Evaluate detection rule thresholds to detect distributed stealth scans designed to bypass rate limiters.",
        "scenario": "An adversary probes one port every 15 minutes across multiple source IP addresses to evade standard threshold alerting.",
        "learning_objectives": ["Identify detection blindspots caused by fixed time-window aggregation."],
        "prerequisites": ["Detection rule authoring", "Sliding window correlation"],
        "environment_description": "Synthetic detection rule and firing log.",
        "tasks": ["Inspect scan timing in evidence.", "Identify the stealth reconnaissance pattern.", "Submit flag: FLAG{subtle_syn_sweep}."],
        "skills_tested": ["Detection gap analysis", "Reconnaissance evasion detection"],
        "related_mitre_technique": "T1046",
        "flag": "FLAG{subtle_syn_sweep}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Fixed 5-minute rules fail on slow-and-low scans. Detection requires 24-hour sliding window aggregation across source subnets.",
        "common_mistakes": ["Assuming high-rate thresholds catch all scanning activity."],
        "hints": [
            {"hint_number": 1, "hint_text": "The adversary intentionally probes below the 5-minute threshold.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "DETECTION_ALERT",
                "title": "scan_event_log.json",
                "description": "Probe timing across 4 hours",
                "content": json.dumps([
                    {"time": "10:00", "dst_port": 22},
                    {"time": "10:15", "dst_port": 80},
                    {"time": "10:30", "dst_port": 443},
                    {"time": "10:45", "dst_port": 3389}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-004",
        "title": "Endpoint & Network Egress Correlation",
        "category": ChallengeCategory.ENDPOINT_SECURITY,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.EVIDENCE_CORRELATION,
        "points": 150,
        "estimated_minutes": 25,
        "description": "Correlate Windows rundll32 process activity with outbound network socket telemetry.",
        "scenario": "A malicious DLL executed via rundll32.exe immediately established an encrypted outbound socket to an external C2 server.",
        "learning_objectives": ["Correlate host PID execution with network socket connections."],
        "prerequisites": ["Endpoint telemetry", "Network connection analysis"],
        "environment_description": "Synthetic Sysmon Process and Network connection events.",
        "tasks": ["Correlate ProcessID 5124 across process create and network connect logs.", "Submit flag: FLAG{rundll32_outbound_c2}."],
        "skills_tested": ["Cross-telemetry correlation", "Living-off-the-land binary (LOLBAS) tracking"],
        "related_mitre_technique": "T1218.011",
        "flag": "FLAG{rundll32_outbound_c2}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "rundll32.exe (PID 5124) established TCP connection to 198.51.100.89:443.",
        "common_mistakes": ["Focusing on the parent process instead of the network-initiating child binary."],
        "hints": [
            {"hint_number": 1, "hint_text": "Match PID 5124 between Sysmon Event 1 and Event 3.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "ENDPOINT_EVENT",
                "title": "sysmon_correlation.json",
                "description": "Sysmon Events 1 & 3",
                "content": json.dumps({
                    "event_1": {"pid": 5124, "image": "rundll32.exe", "cmd": "rundll32.exe payload.dll,Start"},
                    "event_3": {"pid": 5124, "dst_ip": "198.51.100.89", "dst_port": 443}
                })
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-005",
        "title": "SIEM & PCAP Joint Dissection",
        "category": ChallengeCategory.SIEM,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.INVESTIGATION,
        "points": 150,
        "estimated_minutes": 30,
        "description": "Correlate SIEM SMB authentication events with PCAP packet traces to detect PsExec lateral movement.",
        "scenario": "An attacker moved laterally using PsExec, writing an executable to ADMIN$ and starting a service named PSEXESVC.",
        "learning_objectives": ["Detect PsExec lateral movement combining network SMB and system event logs."],
        "prerequisites": ["SMB protocol", "Windows Service creation Event 7045"],
        "environment_description": "Synthetic SIEM events and packet stream.",
        "tasks": ["Inspect the service creation event and SMB share access.", "Identify the tool.", "Submit flag: FLAG{lateral_smb_psexec}."],
        "skills_tested": ["Lateral movement detection", "SMB traffic forensics"],
        "related_mitre_technique": "T1021.002",
        "flag": "FLAG{lateral_smb_psexec}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Access to IPC$ and ADMIN$ followed by service installation PSEXESVC characterizes Sysinternals PsExec lateral movement.",
        "common_mistakes": ["Confusing WMI lateral movement with SMB/PsExec service installation."],
        "hints": [
            {"hint_number": 1, "hint_text": "Look for service installation named PSEXESVC.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "SIEM_LOG",
                "title": "smb_event_7045.json",
                "description": "Event ID 7045 New Service Installed",
                "content": json.dumps({"event_id": 7045, "service_name": "PSEXESVC", "image": "%SystemRoot%\\PSEXESVC.exe"})
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-006",
        "title": "High-Confidence Threat Actor Attribution",
        "category": ChallengeCategory.THREAT_INTELLIGENCE,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.SHORT_ANSWER,
        "points": 150,
        "estimated_minutes": 25,
        "description": "Analyze TTPs, malware hashes, and target sectors to attribute campaign indicators to APT29 (Cozy Bear).",
        "scenario": "Indicators include WellMess malware, Tor exit nodes, and targeting of healthcare research institutions.",
        "learning_objectives": ["Attribute threat campaigns using MITRE ATT&CK group profiles."],
        "prerequisites": ["Threat actor TTP profiling"],
        "environment_description": "Synthetic threat intelligence correlation matrix.",
        "tasks": ["Map indicators to known threat actor groups.", "Identify the actor.", "Submit flag: FLAG{apt29_cozy_bear}."],
        "skills_tested": ["Threat actor profiling", "Intelligence correlation"],
        "related_mitre_technique": "T1071.001",
        "flag": "FLAG{apt29_cozy_bear}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "WellMess malware combined with specific infrastructure overlaps strongly attributes to APT29 (Cozy Bear).",
        "common_mistakes": ["Confusing APT28 (Fancy Bear) with APT29 (Cozy Bear)."],
        "hints": [
            {"hint_number": 1, "hint_text": "This group is also known as Cozy Bear or Nobelium.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "IOC",
                "title": "actor_ttps.json",
                "description": "Observed actor behavioral profile",
                "content": json.dumps({"malware": ["WellMess", "WellMail"], "target": "Vaccine Research", "infrastructure": "Compromised VPS"})
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-007",
        "title": "Detection Coverage Gap in Kerberoasting",
        "category": ChallengeCategory.DETECTION_ENGINEERING,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.DETECTION_ENGINEERING,
        "points": 150,
        "estimated_minutes": 25,
        "description": "Identify a missing detection rule parameter for Kerberoast attacks requesting RC4 encryption downgrade.",
        "scenario": "A Kerberoasting attack fired Event 4769 requesting ticket encryption 0x17 (RC4) for service accounts.",
        "learning_objectives": ["Detect Kerberoasting via Ticket Granting Service (TGS) encryption downgrade."],
        "prerequisites": ["Active Directory Kerberos security", "Event 4769"],
        "environment_description": "Synthetic Kerberos TGS request log.",
        "tasks": ["Inspect Ticket Encryption Type in Event 4769.", "Identify why RC4 requests are suspicious.", "Submit flag: FLAG{rc4_ticket_request}."],
        "skills_tested": ["Kerberoasting detection", "Encryption type analysis"],
        "related_mitre_technique": "T1558.003",
        "flag": "FLAG{rc4_ticket_request}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Attackers request RC4 (0x17) tickets because RC4 hashes are significantly faster to crack offline than AES.",
        "common_mistakes": ["Assuming all ticket requests are benign without checking encryption downgrade."],
        "hints": [
            {"hint_number": 1, "hint_text": "Look for Ticket Encryption Type: 0x17 (RC4).", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "SIEM_LOG",
                "title": "event_4769.json",
                "description": "TGS Ticket Request",
                "content": json.dumps({"event_id": 4769, "service_name": "MSSQLSvc", "ticket_options": "0x40810000", "ticket_encryption_type": "0x17"})
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-008",
        "title": "Incident Timeline Multi-Host Reconstruction",
        "category": ChallengeCategory.INCIDENT_RESPONSE,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.TIMELINE_ANALYSIS,
        "points": 150,
        "estimated_minutes": 30,
        "description": "Reconstruct adversary lateral movement across three internal hosts to identify the initial pivot point.",
        "scenario": "Workstations WKSTN-01, WKSTN-02, and DC-01 recorded security events. Determine which workstation served as the attacker's initial pivot.",
        "learning_objectives": ["Identify pivot hosts in multi-system intrusion timelines."],
        "prerequisites": ["Lateral movement tracking", "Timeline analysis"],
        "environment_description": "Multi-host event chronology.",
        "tasks": ["Sort events chronologically across all three hosts.", "Identify initial pivot workstation.", "Submit flag: FLAG{initial_pivot_wkstn02}."],
        "skills_tested": ["Multi-system correlation", "Root cause timeline analysis"],
        "related_mitre_technique": "T1021",
        "flag": "FLAG{initial_pivot_wkstn02}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "WKSTN-02 received the initial external connection at 01:15 UTC before initiating outbound SMB connections to WKSTN-01 and DC-01.",
        "common_mistakes": ["Assuming the domain controller was the initial breach point."],
        "hints": [
            {"hint_number": 1, "hint_text": "Find the host with the earliest timestamp.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "TIMELINE",
                "title": "multi_host_timeline.json",
                "description": "Cross-host chronological logs",
                "content": json.dumps([
                    {"time": "01:15:00", "host": "WKSTN-02", "event": "External Ingress RDP"},
                    {"time": "01:25:00", "host": "WKSTN-02", "target": "WKSTN-01", "event": "Outbound SMB"},
                    {"time": "01:40:00", "host": "WKSTN-01", "target": "DC-01", "event": "LDAP Query"}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-009",
        "title": "Complete MITRE Attack Chain Construction",
        "category": ChallengeCategory.MITRE_ATTACK,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.MITRE_MAPPING,
        "points": 150,
        "estimated_minutes": 30,
        "description": "Construct an end-to-end 4-stage MITRE ATT&CK chain from initial access through data exfiltration.",
        "scenario": "An intrusion involved Phishing (Initial Access) -> PowerShell (Execution) -> C2 Beaconing -> Data Exfiltration.",
        "learning_objectives": ["Map full intrusion lifecycles to MITRE tactics."],
        "prerequisites": ["MITRE ATT&CK lifecycle"],
        "environment_description": "Attack campaign report summary.",
        "tasks": ["Map each campaign phase to its primary ATT&CK tactic.", "Submit flag: FLAG{chain_initial_execution_exfil}."],
        "skills_tested": ["Attack chain modeling", "Tactics progression analysis"],
        "related_mitre_technique": "T1566",
        "flag": "FLAG{chain_initial_execution_exfil}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "The attack progressed through Initial Access -> Execution -> Command and Control -> Exfiltration.",
        "common_mistakes": ["Mixing up tactics (goals) with techniques (methods)."],
        "hints": [
            {"hint_number": 1, "hint_text": "Chain: Initial -> Execution -> Exfil.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "TIMELINE",
                "title": "attack_phases.json",
                "description": "Intrusion milestones",
                "content": json.dumps(["Phishing attachment", "PowerShell macro execution", "HTTPS C2 beacon", "FTP file upload"])
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-010",
        "title": "SOC Alert Prioritization & Containment",
        "category": ChallengeCategory.SOC_ANALYSIS,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.SOC_ANALYSIS,
        "points": 150,
        "estimated_minutes": 25,
        "description": "Triage simultaneous security alerts across multiple critical servers and isolate the primary target asset.",
        "scenario": "Alerts fire on web frontends and the production SQL database server. The DB server shows active data dumping into /tmp.",
        "learning_objectives": ["Execute prioritized containment on high-value compromised assets."],
        "prerequisites": ["SOC triage and containment strategies"],
        "environment_description": "Synthetic SOC active incident board.",
        "tasks": ["Identify which host requires immediate simulated network isolation.", "Submit flag: FLAG{contain_db_server}."],
        "skills_tested": ["Containment decision making", "Asset critical value ranking"],
        "related_mitre_technique": "T1565",
        "flag": "FLAG{contain_db_server}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Active uncontained data dumping on the database server presents immediate catastrophic risk, prioritizing it for immediate containment.",
        "common_mistakes": ["Containing web proxies while leaving database exfiltration active."],
        "hints": [
            {"hint_number": 1, "hint_text": "Prioritize the database server experiencing active data loss.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "DETECTION_ALERT",
                "title": "active_alerts.json",
                "description": "Active alerts dashboard",
                "content": json.dumps([
                    {"host": "WEB-01", "alert": "High CPU", "severity": "MEDIUM"},
                    {"host": "DB-PROD-01", "alert": "Bulk Database Dump to /tmp", "severity": "CRITICAL"}
                ])
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-011",
        "title": "Multi-Stage Endpoint Persistence Investigation",
        "category": ChallengeCategory.ENDPOINT_SECURITY,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.INVESTIGATION,
        "points": 150,
        "estimated_minutes": 30,
        "description": "Investigate scheduled task creation used by an adversary for persistent execution across reboots.",
        "scenario": "An attacker executed schtasks.exe to establish a task 'WindowsUpdateCheck' executing every morning at 08:00.",
        "learning_objectives": ["Detect Scheduled Task persistence mechanisms in endpoint telemetry."],
        "prerequisites": ["Windows Persistence mechanisms", "Sysmon Event 1"],
        "environment_description": "Synthetic process creation telemetry.",
        "tasks": ["Inspect the command line parameters of schtasks.exe.", "Identify persistence method.", "Submit flag: FLAG{scheduled_task_schtasks}."],
        "skills_tested": ["Persistence detection", "Command line argument analysis"],
        "related_mitre_technique": "T1053.005",
        "flag": "FLAG{scheduled_task_schtasks}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Adversary used schtasks.exe /create /sc daily /tn WindowsUpdateCheck /tr C:\\Windows\\Temp\\update.exe.",
        "common_mistakes": ["Assuming scheduled tasks named 'WindowsUpdate' are always genuine OS processes."],
        "hints": [
            {"hint_number": 1, "hint_text": "Look for schtasks.exe with /create flag.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "ENDPOINT_EVENT",
                "title": "schtasks_command.json",
                "description": "Command line execution log",
                "content": json.dumps({"image": "schtasks.exe", "command": "schtasks.exe /create /tn WindowsUpdateCheck /tr C:\\Temp\\rev.exe /sc onlogon"})
            }
        ]
    },
    {
        "challenge_id": "CHAL-ADV-012",
        "title": "Incident Response Containment Strategy",
        "category": ChallengeCategory.INCIDENT_RESPONSE,
        "difficulty": ChallengeDifficulty.ADVANCED,
        "challenge_type": ChallengeType.INVESTIGATION,
        "points": 150,
        "estimated_minutes": 30,
        "description": "Formulate a comprehensive containment and eradication response plan for compromised domain credentials.",
        "scenario": "An adversary compromised domain admin credentials. Isolate the affected host and revoke active Kerberos/VPN sessions.",
        "learning_objectives": ["Select proportional, effective containment measures."],
        "prerequisites": ["Incident response playbooks"],
        "environment_description": "Incident response plan options.",
        "tasks": ["Identify the primary two containment actions required.", "Submit flag: FLAG{isolate_and_rotate_creds}."],
        "skills_tested": ["Incident response planning", "Remediation decision making"],
        "related_mitre_technique": "T1078",
        "flag": "FLAG{isolate_and_rotate_creds}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Network host isolation halts lateral movement, while immediate credential reset terminates active sessions.",
        "common_mistakes": ["Rebooting the host without changing compromised passwords."],
        "hints": [
            {"hint_number": 1, "hint_text": "Isolate the host and rotate compromised credentials.", "penalty_percent": 20.0, "penalty_points": 30},
        ],
        "evidence": [
            {
                "evidence_type": "TIMELINE",
                "title": "ir_response_plan.json",
                "description": "Proposed actions",
                "content": json.dumps(["Host Network Isolation", "Compromised Password Reset", "Kerberos Golden Ticket Revocation"])
            }
        ]
    },

    # =========================================================================
    # EXPERT (6 Challenges)
    # =========================================================================
    {
        "challenge_id": "CHAL-EXP-001",
        "title": "Multi-Stage Network Intrusion Forensic Investigation",
        "category": ChallengeCategory.FORENSICS,
        "difficulty": ChallengeDifficulty.EXPERT,
        "challenge_type": ChallengeType.INVESTIGATION,
        "points": 200,
        "estimated_minutes": 45,
        "description": "Execute a full-scope forensic reconstruction of a sophisticated nation-state pivot across boundary firewalls.",
        "scenario": "An APT actor compromised an edge VPN concentrator, injected SSH keys, and established an internal SOCKS proxy into the DMZ.",
        "learning_objectives": ["Conduct complex multi-stage digital forensic investigations across edge infrastructure."],
        "prerequisites": ["Advanced network forensics", "Multi-stage incident analysis"],
        "environment_description": "Synthetic multi-source forensic image logs.",
        "tasks": ["Correlate VPN session tokens, SSH authorized_keys modifications, and internal proxy flows.", "Submit flag: FLAG{apt_shadow_broker_pivot}."],
        "skills_tested": ["Edge appliance forensics", "Proxy chain deconstruction", "APT investigation"],
        "related_mitre_technique": "T1133",
        "flag": "FLAG{apt_shadow_broker_pivot}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "The actor exploited a known edge flaw, authorized SSH keys for user 'nobody', and bridged a SOCKS proxy into the 10.0.0.0/8 enclave.",
        "common_mistakes": ["Stopping the investigation at the edge appliance without checking internal lateral connections."],
        "hints": [
            {"hint_number": 1, "hint_text": "Check the SSH key additions right after the initial edge session.", "penalty_percent": 25.0, "penalty_points": 50},
            {"hint_number": 2, "hint_text": "Look for internal SOCKS tunneling on non-standard ports.", "penalty_percent": 50.0, "penalty_points": 100},
        ],
        "evidence": [
            {
                "evidence_type": "METADATA",
                "title": "edge_forensics.json",
                "description": "Edge concentrator logs",
                "content": json.dumps({"edge_device": "VPN-GW-01", "unauth_ssh_key": "ssh-rsa AAAAB3NzaC1... apt_shadow_broker_pivot", "proxy_port": 1080})
            }
        ]
    },
    {
        "challenge_id": "CHAL-EXP-002",
        "title": "Advanced Fast-Flux DNS & C2 Resiliency",
        "category": ChallengeCategory.THREAT_HUNTING,
        "difficulty": ChallengeDifficulty.EXPERT,
        "challenge_type": ChallengeType.THREAT_HUNTING,
        "points": 200,
        "estimated_minutes": 40,
        "description": "Deconstruct a fast-flux DNS infrastructure utilizing ultra-short TTLs and rotating IP pools.",
        "scenario": "A resilient botnet updates DNS A records every 120 seconds across a pool of 50 compromised residential IP nodes.",
        "learning_objectives": ["Identify fast-flux botnet architectures using TTL and A-record churn."],
        "prerequisites": ["DNS fast-flux concepts", "Threat hunting telemetry"],
        "environment_description": "Synthetic DNS historical resolution database.",
        "tasks": ["Analyze TTL values and IP churn rates.", "Identify the architecture.", "Submit flag: FLAG{fastflux_ttl_short}."],
        "skills_tested": ["Fast-flux hunting", "C2 infrastructure analysis"],
        "related_mitre_technique": "T1568.001",
        "flag": "FLAG{fastflux_ttl_short}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Fast-flux DNS is characterized by TTLs under 300 seconds and rapid rotation of A records across diverse autonomous systems.",
        "common_mistakes": ["Assuming IP changes are caused by legitimate cloud load balancers."],
        "hints": [
            {"hint_number": 1, "hint_text": "TTL is unusually short (under 120s) with 20+ different IP addresses.", "penalty_percent": 25.0, "penalty_points": 50},
        ],
        "evidence": [
            {
                "evidence_type": "IOC",
                "title": "fast_flux_dns.json",
                "description": "DNS resolution history",
                "content": json.dumps({"fqdn": "c2.stealthbot.biz", "ttl": 120, "unique_ips_resolved_24h": 48})
            }
        ]
    },
    {
        "challenge_id": "CHAL-EXP-003",
        "title": "Cross-Engine Tri-Correlation (Endpoint + SIEM + PCAP)",
        "category": ChallengeCategory.CYBERSECURITY_REASONING,
        "difficulty": ChallengeDifficulty.EXPERT,
        "challenge_type": ChallengeType.INVESTIGATION,
        "points": 200,
        "estimated_minutes": 45,
        "description": "Perform complex correlation across Sysmon logs, Windows Security events, and raw packet captures to detect Golden Ticket forging.",
        "scenario": "An attacker compromised the Active Directory KRBTGT account hash and forged a Kerberos Ticket Granting Ticket granting domain admin privileges.",
        "learning_objectives": ["Correlate Kerberos ticket lifetimes across SIEM, packet headers, and endpoint auth."],
        "prerequisites": ["Kerberos protocol deep dive", "Golden Ticket attack mechanics"],
        "environment_description": "Multi-engine synthetic telemetry correlation dataset.",
        "tasks": ["Inspect the Kerberos ticket validity window in evidence.", "Identify Golden Ticket forge indicator.", "Submit flag: FLAG{golden_ticket_pass_the_hash}."],
        "skills_tested": ["Golden Ticket detection", "Multi-engine correlation", "Kerberos ticket analysis"],
        "related_mitre_technique": "T1558.001",
        "flag": "FLAG{golden_ticket_pass_the_hash}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Forged tickets typically exhibit a 10-year validity lifetime (standard is 10 hours), proving Kerberos ticket forgery with KRBTGT key.",
        "common_mistakes": ["Looking for password brute force when authentication used ticket forgery."],
        "hints": [
            {"hint_number": 1, "hint_text": "Check the expiration time of the Kerberos ticket (10 years instead of 10 hours).", "penalty_percent": 25.0, "penalty_points": 50},
        ],
        "evidence": [
            {
                "evidence_type": "SIEM_LOG",
                "title": "kerberos_ticket_dump.json",
                "description": "TGS Event with 10-year lifetime",
                "content": json.dumps({"service": "krbtgt", "ticket_issued": "2026-10-01", "ticket_expires": "2036-10-01", "validity_hours": 87600})
            }
        ]
    },
    {
        "challenge_id": "CHAL-EXP-004",
        "title": "Advanced Detection Engineering & Bypass Analysis",
        "category": ChallengeCategory.DETECTION_ENGINEERING,
        "difficulty": ChallengeDifficulty.EXPERT,
        "challenge_type": ChallengeType.DETECTION_ENGINEERING,
        "points": 200,
        "estimated_minutes": 40,
        "description": "Analyze an EDR telemetry blackout caused by memory unhooking and Event Tracing for Windows (ETW) patching.",
        "scenario": "An adversary modified ntdll.dll memory structures to patch EtwEventWrite, silencing EDR user-mode telemetry.",
        "learning_objectives": ["Detect EDR evasion techniques involving memory unhooking and ETW blinding."],
        "prerequisites": ["EDR architecture", "Windows user-mode hooking"],
        "environment_description": "Synthetic memory integrity audit logs.",
        "tasks": ["Identify the memory modification in ntdll.dll.", "Determine the bypass technique.", "Submit flag: FLAG{etw_patching_unhook}."],
        "skills_tested": ["EDR bypass detection", "Memory integrity analysis"],
        "related_mitre_technique": "T1562.001",
        "flag": "FLAG{etw_patching_unhook}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Adversary patched the first byte of ntdll!EtwEventWrite to RET (0xC3), silencing EDR sensors relying on user-mode hooks.",
        "common_mistakes": ["Assuming lack of alerts means no suspicious activity occurred."],
        "hints": [
            {"hint_number": 1, "hint_text": "Notice that EtwEventWrite in ntdll was patched with a 0xC3 (RET) instruction.", "penalty_percent": 25.0, "penalty_points": 50},
        ],
        "evidence": [
            {
                "evidence_type": "ENDPOINT_EVENT",
                "title": "memory_hook_audit.json",
                "description": "DLL memory modification",
                "content": json.dumps({"module": "ntdll.dll", "function": "EtwEventWrite", "original_bytes": "48 89 5c 24", "current_bytes": "c3 90 90 90"})
            }
        ]
    },
    {
        "challenge_id": "CHAL-EXP-005",
        "title": "Complex Multi-Host Ransomware Pre-Encryption Staging",
        "category": ChallengeCategory.INCIDENT_RESPONSE,
        "difficulty": ChallengeDifficulty.EXPERT,
        "challenge_type": ChallengeType.INVESTIGATION,
        "points": 200,
        "estimated_minutes": 45,
        "description": "Intercept pre-encryption staging commands before ransomware begins disk encryption.",
        "scenario": "Adversary issues commands to delete Volume Shadow Copies via vssadmin and disable Windows recovery mode.",
        "learning_objectives": ["Identify critical pre-encryption indicators to stop ransomware attacks."],
        "prerequisites": ["Ransomware attack lifecycles", "Shadow copy deletion"],
        "environment_description": "Synthetic command execution audit stream.",
        "tasks": ["Inspect the command line in evidence.", "Identify the critical recovery deletion command.", "Submit flag: FLAG{vssadmin_shadows_delete}."],
        "skills_tested": ["Ransomware defense", "Pre-encryption containment"],
        "related_mitre_technique": "T1490",
        "flag": "FLAG{vssadmin_shadows_delete}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Command 'vssadmin.exe delete shadows /all /quiet' destroys local backup points, signaling imminent encryption within minutes.",
        "common_mistakes": ["Waiting until files are encrypted before declaring high-severity containment."],
        "hints": [
            {"hint_number": 1, "hint_text": "Look for vssadmin delete shadows command.", "penalty_percent": 25.0, "penalty_points": 50},
        ],
        "evidence": [
            {
                "evidence_type": "ENDPOINT_EVENT",
                "title": "shadow_deletion.json",
                "description": "Executed process telemetry",
                "content": json.dumps({"image": "vssadmin.exe", "command": "vssadmin.exe delete shadows /all /quiet", "parent": "cmd.exe"})
            }
        ]
    },
    {
        "challenge_id": "CHAL-EXP-006",
        "title": "Full-Spectrum SOC Major Incident Command",
        "category": ChallengeCategory.SOC_ANALYSIS,
        "difficulty": ChallengeDifficulty.EXPERT,
        "challenge_type": ChallengeType.INVESTIGATION,
        "points": 200,
        "estimated_minutes": 50,
        "description": "Lead the investigation and complete full remediation of a simulated multi-vector enterprise compromise.",
        "scenario": "Simultaneous phishing ingress, active credential dumping, and database staging require coordination of tier 1-3 response playbooks.",
        "learning_objectives": ["Coordinate end-to-end multi-disciplinary incident containment."],
        "prerequisites": ["Senior SOC investigation methodology"],
        "environment_description": "Master incident command dashboard.",
        "tasks": ["Evaluate cross-vector evidence and execute complete eradication playbook.", "Submit flag: FLAG{full_incident_remediation_complete}."],
        "skills_tested": ["Major incident management", "Cross-vector defensive coordination"],
        "related_mitre_technique": "T1059",
        "flag": "FLAG{full_incident_remediation_complete}",
        "validation_type": "CASE_INSENSITIVE",
        "solution_explanation": "Successful resolution involved isolating hosts, revoking compromised service credentials, and blocking C2 domains concurrently.",
        "common_mistakes": ["Remediating only the initial infected host while missing concurrent persistence mechanisms."],
        "hints": [
            {"hint_number": 1, "hint_text": "Verify all 3 vectors (host, network, identity) are neutralized.", "penalty_percent": 25.0, "penalty_points": 50},
        ],
        "evidence": [
            {
                "evidence_type": "TIMELINE",
                "title": "incident_master_board.json",
                "description": "Multi-vector attack board",
                "content": json.dumps({"vectors": ["Phishing", "Credential Access", "C2 Beacon", "Database Staging"], "status": "ESCALATED"})
            }
        ]
    }
]

TRACKS_CONFIG = [
    {
        "track_id": "TRACK-NET-DEFENDER",
        "title": "Track 1 — Network Defender",
        "description": "Master fundamental network architectures, addressing, packet inspection, and traffic anomaly identification.",
        "target_role": "Network Security Analyst",
        "difficulty": ChallengeDifficulty.BEGINNER,
        "order_index": 1,
        "badge_name": "Certified Network Defender",
        "challenge_ids": [
            "CHAL-BEG-001", "CHAL-BEG-002", "CHAL-BEG-003", "CHAL-BEG-004", "CHAL-BEG-005",
            "CHAL-BEG-006", "CHAL-BEG-007", "CHAL-BEG-009"
        ]
    },
    {
        "track_id": "TRACK-SOC-ANALYST",
        "title": "Track 2 — SOC Analyst",
        "description": "Learn alert triage, SIEM query analysis, correlation, IOC validation, and incident escalation.",
        "target_role": "Tier 1/2 SOC Analyst",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "order_index": 2,
        "badge_name": "Certified SOC Specialist",
        "challenge_ids": [
            "CHAL-BEG-010", "CHAL-INT-004", "CHAL-INT-005", "CHAL-INT-008",
            "CHAL-INT-009", "CHAL-INT-010", "CHAL-ADV-010", "CHAL-EXP-006"
        ]
    },
    {
        "track_id": "TRACK-NET-DETECTION",
        "title": "Track 3 — Network Detection",
        "description": "Dive deep into packet flows, stealth port scans, DNS anomalies, and detection engineering rule logic.",
        "target_role": "Detection Engineer",
        "difficulty": ChallengeDifficulty.INTERMEDIATE,
        "order_index": 3,
        "badge_name": "Network Detection Specialist",
        "challenge_ids": [
            "CHAL-BEG-006", "CHAL-BEG-008", "CHAL-INT-001", "CHAL-INT-002",
            "CHAL-INT-006", "CHAL-INT-007", "CHAL-ADV-001", "CHAL-ADV-003"
        ]
    },
    {
        "track_id": "TRACK-INCIDENT-INVESTIGATOR",
        "title": "Track 4 — Incident Investigator",
        "description": "Reconstruct multi-host incident timelines, correlate attack chains, and map evidence to MITRE ATT&CK.",
        "target_role": "Incident Responder",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "order_index": 4,
        "badge_name": "Master Incident Investigator",
        "challenge_ids": [
            "CHAL-INT-011", "CHAL-INT-012", "CHAL-ADV-008", "CHAL-ADV-009",
            "CHAL-ADV-012", "CHAL-EXP-001", "CHAL-EXP-003", "CHAL-EXP-005"
        ]
    },
    {
        "track_id": "TRACK-ENDPOINT-INVESTIGATOR",
        "title": "Track 5 — Endpoint Investigator",
        "description": "Investigate process trees, parent-child execution, scheduled task persistence, and memory unhooking.",
        "target_role": "Host & Endpoint Forensics Analyst",
        "difficulty": ChallengeDifficulty.ADVANCED,
        "order_index": 5,
        "badge_name": "Endpoint Security Specialist",
        "challenge_ids": [
            "CHAL-INT-003", "CHAL-INT-010", "CHAL-ADV-004", "CHAL-ADV-005",
            "CHAL-ADV-007", "CHAL-ADV-011", "CHAL-EXP-002", "CHAL-EXP-004"
        ]
    }
]


def seed_challenges(db: Session) -> None:
    """Seed synthetic challenges, hints, evidence, and tracks into database."""
    print("Seeding Step 19 CTF Challenges & Training Tracks...")

    for chal_data in RAW_CHALLENGES:
        existing = db.scalars(
            select(Challenge).where(Challenge.challenge_id == chal_data["challenge_id"])
        ).first()

        salt = flag_service.generate_salt()
        flag_val = chal_data["flag"]
        val_type = chal_data.get("validation_type", "CASE_INSENSITIVE")
        flag_h = flag_service.hash_flag(flag_val, salt, val_type)

        if not existing:
            ch = Challenge(
                challenge_id=chal_data["challenge_id"],
                title=chal_data["title"],
                category=chal_data["category"],
                difficulty=chal_data["difficulty"],
                challenge_type=chal_data["challenge_type"],
                points=chal_data["points"],
                estimated_minutes=chal_data["estimated_minutes"],
                description=chal_data["description"],
                scenario=chal_data["scenario"],
                learning_objectives=json.dumps(chal_data.get("learning_objectives", [])),
                prerequisites=json.dumps(chal_data.get("prerequisites", [])),
                environment_description=chal_data["environment_description"],
                tasks_json=json.dumps(chal_data.get("tasks", [])),
                skills_tested_json=json.dumps(chal_data.get("skills_tested", [])),
                related_lesson_slug=chal_data.get("related_lesson_slug"),
                related_lab_slug=chal_data.get("related_lab_slug"),
                related_mitre_technique=chal_data.get("related_mitre_technique"),
                flag_hash=flag_h,
                flag_salt=salt,
                flag_format="FLAG{...}",
                validation_type=val_type,
                solution_explanation=chal_data["solution_explanation"],
                common_mistakes=json.dumps(chal_data.get("common_mistakes", [])),
                is_active=True,
                is_multi_stage=False,
                simulation_only=True,
            )
            db.add(ch)
            db.flush()

            # Add hints
            for h_info in chal_data.get("hints", []):
                hint = ChallengeHint(
                    challenge_id=ch.id,
                    hint_number=h_info["hint_number"],
                    hint_text=h_info["hint_text"],
                    penalty_percent=h_info.get("penalty_percent", 10.0),
                    penalty_points=h_info.get("penalty_points", 10),
                )
                db.add(hint)

            # Add evidence
            for idx, ev_info in enumerate(chal_data.get("evidence", []), 1):
                evidence = ChallengeEvidence(
                    challenge_id=ch.id,
                    evidence_type=ev_info["evidence_type"],
                    title=ev_info["title"],
                    description=ev_info["description"],
                    content_json=ev_info["content"],
                    order_index=idx,
                )
                db.add(evidence)

    db.commit()

    # Seed Tracks
    for track_info in TRACKS_CONFIG:
        existing_track = db.scalars(
            select(ChallengeTrack).where(ChallengeTrack.track_id == track_info["track_id"])
        ).first()

        if not existing_track:
            track = ChallengeTrack(
                track_id=track_info["track_id"],
                title=track_info["title"],
                description=track_info["description"],
                target_role=track_info["target_role"],
                difficulty=track_info["difficulty"],
                order_index=track_info["order_index"],
                badge_name=track_info["badge_name"],
                is_active=True,
            )
            db.add(track)
            db.flush()

            for order_idx, c_id in enumerate(track_info["challenge_ids"], 1):
                ch_obj = db.scalars(
                    select(Challenge).where(Challenge.challenge_id == c_id)
                ).first()
                if ch_obj:
                    item = ChallengeTrackItem(
                        track_id=track.id,
                        challenge_id=ch_obj.id,
                        order_index=order_idx,
                        is_required=True,
                    )
                    db.add(item)

    db.commit()
    print("Successfully seeded 40 challenges and 5 tracks!")
