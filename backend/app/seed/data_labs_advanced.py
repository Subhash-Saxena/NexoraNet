"""Advanced Track Planned Labs Seed Data.

Architectural specifications for future advanced labs:
PCAP packet dissection, C2 exfiltration detection, Snort/Suricata IDS rules,
and Dynamic ARP Inspection defense.
"""

from typing import Any

ADVANCED_PLANNED_LABS: list[dict[str, Any]] = [
    {
        "title": "Deep Packet Inspection & TCP Stream Reassembly",
        "slug": "pcap-wireshark-stream-analysis",
        "topic_slug": "packet-analysis",
        "description": "Analyze malicious PCAP packet traces, reconstruct fragmented TCP payloads, and extract cleartext credentials from intercepted protocol streams.",
        "difficulty": "ADVANCED",
        "estimated_minutes": 35,
        "environment_type": "PCAP",
        "status": "DRAFT",
        "instructions": (
            "### Planned Advanced Lab\n\n"
            "This lab requires the Step 6 PCAP packet dissection engine. "
            "Students will inspect offline packet captures in an isolated, sandboxed analyzer."
        ),
        "objectives": [
            "Apply Berkeley Packet Filters (BPF) to isolate TCP stream sessions",
            "Reconstruct fragmented TCP byte streams to recover transferred payloads",
            "Identify signs of protocol manipulation and port evasion",
        ],
        "prerequisites": ["Completed Intermediate Labs on TCP/UDP and HTTP"],
        "steps": [
            {
                "step_number": 1,
                "title": "Filter TCP Handshake and Reconstruct Stream",
                "description": "Isolate the TCP three-way handshake in the PCAP capture.",
                "instructions": "Use display filter 'tcp.port == 80' to isolate web traffic.",
                "hint": "Wireshark allows right-clicking a packet and selecting 'Follow TCP Stream'.",
                "expected_observation": "Full HTTP transaction reassembled.",
                "validation_type": "TEXT",
                "points": 20,
                "is_required": True,
                "question": {
                    "question_text": "What Wireshark display filter isolates TCP traffic on port 80?",
                    "question_type": "TEXT",
                    "points": 20,
                    "answer_data": {
                        "accepted_answers": ["tcp.port == 80", "tcp.port==80"],
                        "case_sensitive": False,
                        "explanation": "'tcp.port == 80' matches both source and destination port 80 in Wireshark.",
                    },
                },
            }
        ],
    },
    {
        "title": "Detecting DNS Tunneling & C2 Exfiltration",
        "slug": "detecting-dns-tunneling-beacons",
        "topic_slug": "dns",
        "description": "Investigate anomalous high-entropy TXT and A-record queries used by adversaries for covert Command and Control (C2) channels.",
        "difficulty": "ADVANCED",
        "estimated_minutes": 40,
        "environment_type": "LOG_ANALYSIS",
        "status": "DRAFT",
        "instructions": (
            "### Planned Advanced Lab\n\n"
            "This lab will feature synthetic DNS query logs demonstrating base64 data exfiltration "
            "encoded into subdomains."
        ),
        "objectives": [
            "Calculate Shannon entropy on subdomains to detect encoded binary data",
            "Identify suspicious DNS query volume directed to single authoritative domains",
            "Author firewall and Zeek rules to detect and throttle DNS tunneling",
        ],
        "prerequisites": ["Completed Lab 15: Trace Recursive DNS Resolution Flow"],
        "steps": [
            {
                "step_number": 1,
                "title": "Analyze High Entropy Subdomain Query",
                "description": "Inspect suspicious long subdomain queries.",
                "instructions": "Examine the sample query: 'aXNzb2x1dGlvbg.data.exfil.org'.",
                "hint": "High randomness and character count indicate encoded payload.",
                "expected_observation": "Anomalous subdomain length exceeding standard RFC naming norms.",
                "validation_type": "SINGLE_CHOICE",
                "points": 20,
                "is_required": True,
                "question": {
                    "question_text": "Which metric best identifies encoded binary data inside DNS subdomains?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 20,
                    "answer_data": {
                        "options": [
                            "High Shannon entropy and abnormal subdomain character length",
                            "The IP address of the client web browser",
                            "The TCP sequence number in the DNS header",
                            "The TTL value of the local gateway",
                        ],
                        "correct_option": "High Shannon entropy and abnormal subdomain character length",
                        "explanation": "High Shannon entropy indicates cryptographic or compressed binary payloads disguised inside standard DNS queries.",
                    },
                },
            }
        ],
    },
    {
        "title": "Snort & Suricata IDS Signature Authoring",
        "slug": "snort-suricata-ids-signature-authoring",
        "topic_slug": "firewall-rules",
        "description": "Write intrusion detection rules matching exploit patterns, payload offsets, and TCP flag combinations.",
        "difficulty": "ADVANCED",
        "estimated_minutes": 45,
        "environment_type": "CONTAINER",
        "status": "DRAFT",
        "instructions": (
            "### Planned Advanced Lab\n\n"
            "This lab will launch isolated container sandboxes to test Snort rule alert triggers."
        ),
        "objectives": [
            "Construct Snort rule headers: action, protocol, source, destination, ports",
            "Utilize content matching keywords: content, offset, depth, nocase",
            "Verify rule detection against simulated exploit traffic without false positives",
        ],
        "prerequisites": ["Completed Lab 18: Defensive Firewall Access Control"],
        "steps": [
            {
                "step_number": 1,
                "title": "Construct Snort Rule Header",
                "description": "Assemble rule header detecting inbound traffic to port 80.",
                "instructions": "Identify the standard rule format: 'alert tcp $EXTERNAL_NET any -> $HOME_NET 80'.",
                "hint": "Alert action triggers a log entry when matching criteria are satisfied.",
                "expected_observation": "A valid Snort rule header.",
                "validation_type": "SINGLE_CHOICE",
                "points": 20,
                "is_required": True,
                "question": {
                    "question_text": "What action keyword in Snort generates an alert when a rule matches?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 20,
                    "answer_data": {
                        "options": ["alert", "drop", "pass", "log"],
                        "correct_option": "alert",
                        "explanation": "'alert' instructs the IDS engine to generate a notification while continuing to forward or inspect the packet stream.",
                    },
                },
            }
        ],
    },
    {
        "title": "Mitigating ARP Poisoning with Dynamic ARP Inspection",
        "slug": "mitigating-arp-cache-poisoning",
        "topic_slug": "arp",
        "description": "Analyze gratuitous ARP spoofing packets in switched networks and configure switch security defenses including DAI and DHCP Snooping.",
        "difficulty": "ADVANCED",
        "estimated_minutes": 35,
        "environment_type": "SIMULATOR",
        "status": "DRAFT",
        "instructions": (
            "### Planned Advanced Lab\n\n"
            "This lab will simulate switched ethernet segments to demonstrate Man-in-the-Middle ARP poisoning."
        ),
        "objectives": [
            "Inspect Gratuitous ARP packets used to poison switch and host CAM tables",
            "Configure Dynamic ARP Inspection (DAI) against untrusted access ports",
            "Verify that invalid IP-to-MAC mappings are dropped at Layer 2",
        ],
        "prerequisites": ["Completed Lab 3: Find Your MAC Address and Lab 4"],
        "steps": [
            {
                "step_number": 1,
                "title": "Explain ARP Cache Poisoning Mechanics",
                "description": "Understand how an attacker hijacks default gateway traffic.",
                "instructions": "An attacker sends forged ARP replies claiming their MAC belongs to the default gateway IP.",
                "hint": "Hosts update their ARP tables upon receiving unauthenticated ARP replies.",
                "expected_observation": "Workstation sends egress traffic to attacker instead of true router.",
                "validation_type": "SINGLE_CHOICE",
                "points": 20,
                "is_required": True,
                "question": {
                    "question_text": "What switch security feature cross-references ARP replies against the DHCP snooping binding table?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 20,
                    "answer_data": {
                        "options": [
                            "Dynamic ARP Inspection (DAI)",
                            "Spanning Tree Protocol (STP)",
                            "Port Security MAC Limiting",
                            "VLAN Trunking Protocol (VTP)",
                        ],
                        "correct_option": "Dynamic ARP Inspection (DAI)",
                        "explanation": "Dynamic ARP Inspection (DAI) inspects all ARP requests and responses on untrusted ports, discarding invalid packets where the IP and MAC do not match the trusted DHCP snooping binding database.",
                    },
                },
            }
        ],
    },
]
