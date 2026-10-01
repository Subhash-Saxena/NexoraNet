"""Intermediate Track Hands-on Labs Seed Data.

Eight comprehensive, interactive labs covering subnetting calculations,
VLSM address boundary design, TCP vs UDP application trade-offs,
TCP three-way handshake dissection, recursive DNS resolution pipelines,
HTTP request header dissection, routing table longest-prefix matching,
and defensive firewall access control rule evaluation.
"""

from typing import Any

INTERMEDIATE_LABS: list[dict[str, Any]] = [
    # LAB 11
    {
        "title": "Calculate Subnet Boundaries and Masks",
        "slug": "calculate-subnet-boundaries",
        "topic_slug": "subnetting",
        "description": "Given a classful /24 network block, calculate subnet masks, prefix lengths, and subnetwork host capacities.",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 25,
        "environment_type": "CONCEPTUAL",
        "instructions": (
            "### Lab Overview\n\n"
            "An enterprise organization has been allocated the private network `192.168.10.0/24`. "
            "You are tasked with partitioning this network into **4 equal subnets** to isolate Engineering, "
            "Sales, Guest Wi-Fi, and Server Infrastructure.\n\n"
            "In this lab, you will perform binary and CIDR math to calculate the new subnet mask and host allocations."
        ),
        "objectives": [
            "Calculate how many host bits must be borrowed to create 4 equal subnets",
            "Determine the resulting CIDR prefix length and dotted-decimal subnet mask",
            "Compute the total number of usable host IP addresses per subnet",
        ],
        "prerequisites": [
            "Understanding of powers of 2 (2, 4, 8, 16, 32, 64, 128, 256)",
            "Basic familiarity with CIDR prefix notation (/24)",
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Calculate Borrowed Bits and New Prefix",
                "description": "Determine the new CIDR prefix when dividing a /24 network into 4 subnets.",
                "instructions": (
                    "To create 4 subnets, we use the formula `2^n >= subnets`, where `n` is borrowed bits:\n\n"
                    "`2^2 = 4`, so we must borrow **2 bits** from the host portion.\n\n"
                    "Initial prefix: `/24`\n"
                    "New prefix: `24 + 2 = ?`\n\n"
                    "Enter the new CIDR prefix length (e.g. 26 or /26)."
                ),
                "hint": "Add 2 borrowed bits to the initial /24 prefix: 24 + 2 = 26.",
                "expected_observation": "The new prefix length is /26.",
                "validation_type": "CIDR",
                "points": 15,
                "is_required": True,
                "question": {
                    "question_text": "What is the new CIDR prefix length after borrowing 2 bits?",
                    "question_type": "CIDR",
                    "points": 15,
                    "answer_data": {
                        "prefix_only": True,
                        "expected_prefix_length": "26",
                        "placeholder": "e.g. /26 or 26",
                        "label": "New CIDR Prefix",
                        "explanation": "Borrowing 2 bits from a /24 adds 2 to the network prefix: 24 + 2 = /26.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Calculate Dotted-Decimal Subnet Mask",
                "description": "Convert the /26 CIDR prefix into dotted-decimal notation.",
                "instructions": (
                    "In a /26 mask, the fourth octet contains 2 network bits (1s) and 6 host bits (0s):\n\n"
                    "Binary: `11000000`\n"
                    "Value: `128 + 64 = 192`\n\n"
                    "Enter the full 32-bit dotted-decimal subnet mask."
                ),
                "hint": "The first three octets are 255.255.255. The fourth octet is 128 + 64 = 192.",
                "expected_observation": "255.255.255.192",
                "validation_type": "IP_ADDRESS",
                "points": 15,
                "is_required": True,
                "question": {
                    "question_text": "Enter the dotted-decimal subnet mask for a /26 prefix:",
                    "question_type": "IP_ADDRESS",
                    "points": 15,
                    "answer_data": {
                        "expected_ip": "255.255.255.192",
                        "expected_version": 4,
                        "placeholder": "e.g. 255.255.255.192",
                        "label": "Subnet Mask",
                        "explanation": "A /26 mask has 26 consecutive 1s: 11111111.11111111.11111111.11000000 = 255.255.255.192.",
                    },
                },
            },
            {
                "step_number": 3,
                "title": "Calculate Usable Host IP Addresses",
                "description": "Determine how many hosts can be assigned in each /26 subnet.",
                "instructions": (
                    "With 6 host bits remaining (`32 - 26 = 6`), total IP addresses = `2^6 = 64`.\n\n"
                    "Because 2 addresses are reserved in every IPv4 subnet (Network ID and Broadcast address), "
                    "the formula for usable hosts is `2^h - 2`.\n\n"
                    "Calculate the number of usable host IP addresses per /26 subnet."
                ),
                "hint": "64 total addresses minus 2 reserved addresses = 62 usable host addresses.",
                "expected_observation": "62 usable hosts.",
                "validation_type": "NUMERICAL",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "How many usable host IP addresses exist in a /26 subnet?",
                    "question_type": "NUMERICAL",
                    "points": 10,
                    "answer_data": {
                        "expected_value": 62,
                        "tolerance": 0,
                        "placeholder": "e.g. 62",
                        "label": "Usable Host Count",
                        "explanation": "2^6 = 64 total addresses. Subtract 2 (Network ID and Broadcast ID) = 62 usable host addresses.",
                    },
                },
            },
        ],
    },
    # LAB 12
    {
        "title": "Find Network and Broadcast Address",
        "slug": "find-network-broadcast-range",
        "topic_slug": "vlsm",
        "description": "Given host IP 192.168.10.37/27, calculate the subnet block size, network address, broadcast address, and valid host range.",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 25,
        "environment_type": "CONCEPTUAL",
        "instructions": (
            "### Lab Overview\n\n"
            "A host has been assigned the IP address `192.168.10.37/27`. "
            "As a network security administrator, you must identify the boundary addresses of this subnet "
            "to configure firewall ACLs and DHCP scopes correctly."
        ),
        "objectives": [
            "Calculate the block size (magic number) for a /27 prefix (32 addresses)",
            "Identify the subnetwork ID by finding the largest multiple of the block size less than or equal to the host IP",
            "Calculate the broadcast address and usable host range",
        ],
        "prerequisites": ["Completed Lab 11: Calculate Subnet Boundaries and Masks"],
        "steps": [
            {
                "step_number": 1,
                "title": "Calculate Subnet Network Address",
                "description": "Determine the network identifier for host 192.168.10.37/27.",
                "instructions": (
                    "A `/27` prefix has 5 host bits (`32 - 27 = 5`).\n\n"
                    "Block size = `2^5 = 32`.\n"
                    "Subnet boundaries increment by 32: `0, 32, 64, 96, 128...`\n\n"
                    "Since the host IP is `192.168.10.37`, it falls between 32 and 63.\n\n"
                    "Enter the Network Address for this subnet."
                ),
                "hint": "The network address is the starting boundary: 192.168.10.32.",
                "expected_observation": "Network Address: 192.168.10.32",
                "validation_type": "IP_ADDRESS",
                "points": 15,
                "is_required": True,
                "question": {
                    "question_text": "Enter the Network Address for host 192.168.10.37/27:",
                    "question_type": "IP_ADDRESS",
                    "points": 15,
                    "answer_data": {
                        "expected_ip": "192.168.10.32",
                        "expected_version": 4,
                        "placeholder": "e.g. 192.168.10.32",
                        "label": "Network Address",
                        "explanation": "In 192.168.10.37/27, the block size is 32. Multiples of 32 are 0, 32, 64. 37 falls into the 192.168.10.32 subnet.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Calculate Subnet Broadcast Address",
                "description": "Determine the all-hosts broadcast address for this subnet.",
                "instructions": (
                    "The broadcast address is the last address in the subnet block (one less than the next subnet boundary).\n\n"
                    "Next subnet starts at: `192.168.10.64`\n"
                    "Broadcast address: `192.168.10.64 - 1 = ?`\n\n"
                    "Enter the Broadcast Address."
                ),
                "hint": "32 + 32 - 1 = 63.",
                "expected_observation": "Broadcast Address: 192.168.10.63",
                "validation_type": "IP_ADDRESS",
                "points": 15,
                "is_required": True,
                "question": {
                    "question_text": "Enter the Broadcast Address for the 192.168.10.32/27 subnet:",
                    "question_type": "IP_ADDRESS",
                    "points": 15,
                    "answer_data": {
                        "expected_ip": "192.168.10.63",
                        "expected_version": 4,
                        "placeholder": "e.g. 192.168.10.63",
                        "label": "Broadcast Address",
                        "explanation": "The broadcast address has all host bits set to 1, which equals 192.168.10.63 for this /27 block.",
                    },
                },
            },
            {
                "step_number": 3,
                "title": "Identify First and Last Usable Host Range",
                "description": "Verify the usable IP addresses between Network ID and Broadcast ID.",
                "instructions": (
                    "Usable hosts run from `Network ID + 1` to `Broadcast ID - 1`.\n\n"
                    "What is the last usable host IP in this subnet?"
                ),
                "hint": "One address before the broadcast address 192.168.10.63 is 192.168.10.62.",
                "expected_observation": "Last usable host: 192.168.10.62",
                "validation_type": "IP_ADDRESS",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Enter the last usable host IP address in the 192.168.10.32/27 subnet:",
                    "question_type": "IP_ADDRESS",
                    "points": 10,
                    "answer_data": {
                        "expected_ip": "192.168.10.62",
                        "expected_version": 4,
                        "placeholder": "e.g. 192.168.10.62",
                        "label": "Last Usable Host",
                        "explanation": "The host range is 192.168.10.33 through 192.168.10.62 (30 total usable hosts).",
                    },
                },
            },
        ],
    },
    # LAB 13
    {
        "title": "TCP vs UDP Protocol Scenario Investigation",
        "slug": "tcp-vs-udp-investigation",
        "topic_slug": "tcp-vs-udp",
        "description": "Evaluate real-world application traffic requirements (latency vs reliability) and select the optimal Layer 4 transport protocol.",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 20,
        "environment_type": "CONCEPTUAL",
        "instructions": (
            "### Lab Overview\n\n"
            "Transport Layer protocols make deliberate engineering trade-offs:\n\n"
            "* **TCP (Transmission Control Protocol)** provides guaranteed delivery, retransmission of lost packets, and ordered byte streaming, but introduces handshake and acknowledgment overhead.\n"
            "* **UDP (User Datagram Protocol)** is connectionless and lightweight with zero retransmission, ideal for real-time traffic where timeliness beats 100% reliability.\n\n"
            "In this lab, you will evaluate four network applications and designate the required transport protocol."
        ),
        "objectives": [
            "Analyze throughput, packet loss tolerance, and latency constraints of network services",
            "Understand why financial transactions and file transfers mandate TCP",
            "Explain why live voice/video streaming and DNS lookups leverage UDP",
        ],
        "prerequisites": ["Basic understanding of Layer 4 transport protocols"],
        "steps": [
            {
                "step_number": 1,
                "title": "Banking & Secure Financial Transactions",
                "description": "Select the required transport protocol for banking data.",
                "instructions": (
                    "A customer submits an online banking transfer of $10,000 over HTTPS. "
                    "If a packet containing account numbers or transaction tokens is dropped in transit, "
                    "can the application tolerate dropped or corrupted packets without retransmission?"
                ),
                "hint": "Financial data cannot lose a single byte; it requires guaranteed delivery.",
                "expected_observation": "TCP is required for 100% data integrity.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Which transport protocol is mandatory for HTTPS banking transactions?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "TCP (Guaranteed delivery and byte-stream retransmission)",
                            "UDP (Connectionless lightweight datagrams)",
                            "ICMP (Echo control packets)",
                            "ARP (Hardware address resolution)",
                        ],
                        "correct_option": "TCP (Guaranteed delivery and byte-stream retransmission)",
                        "explanation": "TCP guarantees reliable delivery through ACKs and retransmits lost packets. Dropping data in a financial transaction could corrupt financial balances.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Real-time Voice over IP (VoIP) Audio",
                "description": "Evaluate transport requirements for live voice communication.",
                "instructions": (
                    "In a live Zoom or Discord voice call, audio packets are transmitted every 20 milliseconds. "
                    "If a 20 ms audio packet is delayed or dropped, retransmitting it 300 ms later is useless because "
                    "the conversation has already moved forward and delayed audio causes robotic stuttering.\n\n"
                    "Which protocol is used for real-time voice and video media?"
                ),
                "hint": "Real-time communication prioritizes low latency over guaranteed retransmission.",
                "expected_observation": "UDP is used for real-time media streams.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Which transport protocol powers real-time VoIP audio and video streaming (RTP)?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "UDP (Low latency without retransmission buffering delay)",
                            "TCP (Guaranteed delivery with retransmissions)",
                            "BGP (Border gateway routing)",
                            "FTP (File transfer control channel)",
                        ],
                        "correct_option": "UDP (Low latency without retransmission buffering delay)",
                        "explanation": "VoIP uses RTP over UDP. Retransmitting lost voice frames causes buffer lag and jitter; dropping a tiny audio millisecond is imperceptible to human ears.",
                    },
                },
            },
        ],
    },
    # LAB 14
    {
        "title": "Deconstruct the TCP Three-Way Handshake",
        "slug": "deconstruct-tcp-handshake",
        "topic_slug": "tcp-basics",
        "description": "Trace SYN, SYN-ACK, and ACK packet sequences, sequence number increments, and analyze SYN flood denial-of-service mechanics.",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 25,
        "environment_type": "CONCEPTUAL",
        "instructions": (
            "### Lab Overview\n\n"
            "Before two computers can transmit data over TCP, they must synchronize initial sequence numbers (ISNs) "
            "through a 3-way handshake: **SYN → SYN-ACK → ACK**.\n\n"
            "In this lab, you will calculate sequence and acknowledgment numbers at each step and examine "
            "how attackers exploit this state machine during SYN Flood denial-of-service attacks."
        ),
        "objectives": [
            "Trace the SYN, SYN-ACK, and ACK state transitions",
            "Calculate Acknowledgment Numbers based on Initial Sequence Numbers (ISN)",
            "Explain how half-open connections exhaust server backlog queues in SYN flood attacks",
        ],
        "prerequisites": ["Understanding of TCP header flags (SYN, ACK, FIN, RST)"],
        "steps": [
            {
                "step_number": 1,
                "title": "Calculate SYN-ACK Acknowledgment Number",
                "description": "Determine the server acknowledgment number responding to a client SYN.",
                "instructions": (
                    "A client initiates a connection to a web server:\n\n"
                    "* Packet 1 (Client → Server): `SYN`, Sequence Number = `1000`\n\n"
                    "Because the SYN flag consumes 1 sequence number in the byte stream, the server responds with:\n\n"
                    "* Packet 2 (Server → Client): `SYN-ACK`, Sequence Number = `5000`, Acknowledgment Number = `?`\n\n"
                    "What acknowledgment number does the server send back to confirm receipt of the client's SYN?"
                ),
                "hint": "The server acknowledges receipt by asking for the next byte: Sequence Number (1000) + 1 = 1001.",
                "expected_observation": "Acknowledgment Number = 1001",
                "validation_type": "NUMERICAL",
                "points": 15,
                "is_required": True,
                "question": {
                    "question_text": "Enter the Acknowledgment Number sent in the SYN-ACK packet:",
                    "question_type": "NUMERICAL",
                    "points": 15,
                    "answer_data": {
                        "expected_value": 1001,
                        "tolerance": 0,
                        "placeholder": "e.g. 1001",
                        "label": "SYN-ACK Ack Number",
                        "explanation": "The SYN flag consumes 1 sequence number. The server acknowledges receipt by setting ACK = Client ISN + 1 (1000 + 1 = 1001).",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Analyze SYN Flood Attack Mitigation",
                "description": "Understand how SYN Cookies defeat half-open backlog queue exhaustion.",
                "instructions": (
                    "In a **SYN Flood** attack, an adversary sends millions of spoofed SYN packets without ever returning the final ACK. "
                    "The server allocates memory in its **SYN backlog queue** for each half-open connection until RAM is exhausted and legitimate users are rejected.\n\n"
                    "What cryptographic defense allows a server to encode connection state into the Initial Sequence Number without allocating memory until the final ACK arrives?"
                ),
                "hint": "This technique is known as SYN Cookies.",
                "expected_observation": "SYN Cookies prevent backlog table exhaustion.",
                "validation_type": "SINGLE_CHOICE",
                "points": 15,
                "is_required": True,
                "question": {
                    "question_text": "What defensive mechanism encodes connection parameters into the ISN to resist SYN floods?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 15,
                    "answer_data": {
                        "options": [
                            "SYN Cookies (encodes state in sequence number without allocating memory)",
                            "Increasing TCP timeout to 120 seconds",
                            "Disabling the TCP ACK flag",
                            "Converting all web traffic to UDP",
                        ],
                        "correct_option": "SYN Cookies (encodes state in sequence number without allocating memory)",
                        "explanation": "SYN Cookies compute a cryptographic hash of client IP, client port, and server secret into the server's ISN. Memory is allocated only when the client returns a valid ACK.",
                    },
                },
            },
        ],
    },
    # LAB 15
    {
        "title": "Trace Recursive DNS Resolution Flow",
        "slug": "trace-dns-resolution-flow",
        "topic_slug": "dns",
        "description": "Map the 6-stage query chain from client resolver to Root, TLD, and Authoritative nameservers, and explore DNS cache poisoning.",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 25,
        "environment_type": "CONCEPTUAL",
        "instructions": (
            "### Lab Overview\n\n"
            "When your browser resolves `www.cyberdefense.org`, it triggers a hierarchical query pipeline:\n\n"
            "1. Browser Cache & OS Resolver\n"
            "2. ISP Recursive Resolver\n"
            "3. Root Nameserver (`.`)\n"
            "4. Top-Level Domain (TLD) Nameserver (`.org`)\n"
            "5. Authoritative Nameserver (`cyberdefense.org`)\n\n"
            "In this lab, you will trace each stage of the recursive resolution process."
        ),
        "objectives": [
            "Order the chronological sequence of DNS servers contacted during recursive resolution",
            "Differentiate between recursive queries (client to resolver) and iterative referrals (resolver to hierarchy)",
            "Identify the role of Time-To-Live (TTL) in cache poisoning defense",
        ],
        "prerequisites": ["Completed Lab 6: Perform a DNS Lookup"],
        "steps": [
            {
                "step_number": 1,
                "title": "Identify Hierarchy Stage for .com / .org",
                "description": "Classify the role of servers managing top-level domain extensions.",
                "instructions": (
                    "When the recursive resolver asks the Root server where to find `www.example.com`, "
                    "the Root server does not know the final IP. Instead, it refers the resolver to the server managing `.com`.\n\n"
                    "What tier of the DNS hierarchy manages extensions like .com, .net, .org, and .gov?"
                ),
                "hint": "TLD stands for Top-Level Domain.",
                "expected_observation": "Top-Level Domain (TLD) Nameservers.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What type of nameserver manages top-level domain extensions such as .com and .org?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "Top-Level Domain (TLD) Nameserver",
                            "Root Nameserver (.)",
                            "Authoritative Nameserver for the specific domain",
                            "Local Stub Resolver",
                        ],
                        "correct_option": "Top-Level Domain (TLD) Nameserver",
                        "explanation": "TLD nameservers (managed by registries like Verisign for .com) maintain delegations to the authoritative nameservers for all domains under that extension.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Analyze Cache Time-To-Live (TTL)",
                "description": "Explain how TTL balances performance with records updates.",
                "instructions": (
                    "DNS resource records include a **Time-To-Live (TTL)** value in seconds (e.g. 3600 = 1 hour).\n\n"
                    "What happens when the TTL expires on a cached record inside a recursive resolver?"
                ),
                "hint": "Once TTL hits zero, the resolver must query the authoritative server again.",
                "expected_observation": "The cached entry is evicted, requiring a fresh resolution.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What occurs when a cached DNS record's TTL counter reaches zero?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "The resolver purges the record and must re-query the authoritative nameserver",
                            "The domain name permanently ceases to function on the internet",
                            "The client computer shuts down its network adapter",
                            "The web browser switches to HTTP port 80",
                        ],
                        "correct_option": "The resolver purges the record and must re-query the authoritative nameserver",
                        "explanation": "TTL determines how long caching resolvers may reuse a record. Upon expiration, the resolver discards the stale record and queries the authoritative server again.",
                    },
                },
            },
        ],
    },
    # LAB 16
    {
        "title": "Dissect HTTP Request and Response Headers",
        "slug": "dissect-http-request-headers",
        "topic_slug": "http",
        "description": "Analyze HTTP/1.1 request lines, mandatory Host headers, response status codes, and TLS session protection.",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 20,
        "environment_type": "CONCEPTUAL",
        "instructions": (
            "### Lab Overview\n\n"
            "The World Wide Web relies on the Hypertext Transfer Protocol (HTTP). "
            "A client sends a request consisting of a Request Line, Headers, and optional Body, "
            "and the server responds with a Status Line (e.g., 200 OK, 404 Not Found).\n\n"
            "In this lab, you will dissect HTTP headers and security status codes."
        ),
        "objectives": [
            "Deconstruct an HTTP request line (Method, URI, Protocol Version)",
            "Explain why the 'Host' header is mandatory in HTTP/1.1 for virtual hosting",
            "Correlate standard HTTP status code ranges (2xx, 3xx, 4xx, 5xx) with operational outcomes",
        ],
        "prerequisites": ["Basic understanding of web browsers and client-server communication"],
        "steps": [
            {
                "step_number": 1,
                "title": "Inspect HTTP/1.1 Mandatory Host Header",
                "description": "Understand why virtual web hosting requires the Host header.",
                "instructions": (
                    "In HTTP/1.1, multiple websites (e.g., `alpha.com` and `beta.com`) can be hosted on a single server "
                    "sharing a single public IP address.\n\n"
                    "What mandatory header allows the web server to route the request to the correct virtual host?"
                ),
                "hint": "The header is literally named 'Host'.",
                "expected_observation": "The Host header specifies the domain name.",
                "validation_type": "TEXT",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Which HTTP request header specifies the domain name being requested by the client?",
                    "question_type": "TEXT",
                    "points": 10,
                    "answer_data": {
                        "accepted_answers": ["host", "host:", "host header"],
                        "case_sensitive": False,
                        "placeholder": "e.g. Host",
                        "explanation": "RFC 2616 made the 'Host' header mandatory in HTTP/1.1, enabling Name-Based Virtual Hosting where one IP serves hundreds of websites.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Classify HTTP Status Codes",
                "description": "Identify standard HTTP response status categories.",
                "instructions": (
                    "Match the status code range to its meaning:\n\n"
                    "* `200 OK`: Successful response\n"
                    "* `301 Moved Permanently`: Redirection\n"
                    "* `403 Forbidden`: Client authorization failure\n"
                    "* `404 Not Found`: Resource does not exist\n"
                    "* `500 Internal Server Error`: Server application crashed\n\n"
                    "What status code is returned when a client attempts to access a restricted resource without valid credentials?"
                ),
                "hint": "403 Forbidden indicates the server understood the request but refuses to authorize it.",
                "expected_observation": "HTTP 403 Forbidden.",
                "validation_type": "NUMERICAL",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What numeric HTTP status code signifies 'Forbidden' access?",
                    "question_type": "NUMERICAL",
                    "points": 10,
                    "answer_data": {
                        "expected_value": 403,
                        "tolerance": 0,
                        "placeholder": "e.g. 403",
                        "label": "HTTP Status Code",
                        "explanation": "HTTP 403 Forbidden indicates the server understands who you are or what was requested, but permission is denied.",
                    },
                },
            },
        ],
    },
    # LAB 17
    {
        "title": "Routing Table Longest Prefix Match Troubleshooting",
        "slug": "routing-longest-prefix-match",
        "topic_slug": "routing",
        "description": "Given a router routing table with overlapping prefixes, apply the Longest Prefix Match (LPM) rule to determine exact egress forwarding.",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 25,
        "environment_type": "CONCEPTUAL",
        "instructions": (
            "### Lab Overview\n\n"
            "Routers frequently hold multiple overlapping routes in their routing tables. "
            "When forwarding a packet, the router applies the **Longest Prefix Match (LPM)** rule: "
            "the route with the highest number of matching network bits (most specific prefix length) ALWAYS wins.\n\n"
            "In this lab, you will evaluate a multi-route routing table and calculate forwarding decisions."
        ),
        "objectives": [
            "Apply the Longest Prefix Match (LPM) algorithm to overlapping route entries",
            "Trace packet egress interfaces based on destination IP evaluation",
            "Understand why the default route (0.0.0.0/0) only applies when no other routes match",
        ],
        "prerequisites": ["Completed Lab 5: Inspect Your Local Routing Table and Lab 11"],
        "steps": [
            {
                "step_number": 1,
                "title": "Evaluate Overlapping Route Table",
                "description": "A router contains the following 4 routes in its forwarding information base.",
                "instructions": (
                    "Routing Table:\n\n"
                    "1. `10.0.0.0/8` via Next-Hop `192.168.1.1` (Interface GigabitEthernet0/1)\n"
                    "2. `10.1.0.0/16` via Next-Hop `192.168.2.1` (Interface GigabitEthernet0/2)\n"
                    "3. `10.1.2.0/24` via Next-Hop `192.168.3.1` (Interface GigabitEthernet0/3)\n"
                    "4. `0.0.0.0/0` via Next-Hop `172.16.1.1` (Interface GigabitEthernet0/0)\n\n"
                    "A packet arrives with Destination IP: `10.1.2.45`.\n\n"
                    "Which route has the longest prefix match for this packet?"
                ),
                "hint": "Compare prefix lengths: /8, /16, /24, /0. The longest matching prefix is /24.",
                "expected_observation": "10.1.2.0/24 is the most specific matching prefix.",
                "validation_type": "SINGLE_CHOICE",
                "points": 15,
                "is_required": True,
                "question": {
                    "question_text": "Which route entry is selected by the router for destination 10.1.2.45?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 15,
                    "answer_data": {
                        "options": [
                            "10.1.2.0/24 (matches 24 bits, most specific)",
                            "10.1.0.0/16 (matches 16 bits)",
                            "10.0.0.0/8 (matches 8 bits)",
                            "0.0.0.0/0 (default route)",
                        ],
                        "correct_option": "10.1.2.0/24 (matches 24 bits, most specific)",
                        "explanation": "Even though 10.1.2.45 matches all four entries, /24 has the most matching network bits (24 bits). Routers always choose the longest matching prefix.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Identify Egress Interface",
                "description": "Select the egress network interface for the matching route.",
                "instructions": (
                    "Based on route #3 (`10.1.2.0/24`), which physical network interface forwards the packet?"
                ),
                "hint": "Route #3 points to GigabitEthernet0/3.",
                "expected_observation": "GigabitEthernet0/3",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Which interface will the router transmit this packet out of?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": ["GigabitEthernet0/3", "GigabitEthernet0/2", "GigabitEthernet0/1", "GigabitEthernet0/0"],
                        "correct_option": "GigabitEthernet0/3",
                        "explanation": "The selected /24 route is bound to interface GigabitEthernet0/3 via next-hop 192.168.3.1.",
                    },
                },
            },
        ],
    },
    # LAB 18
    {
        "title": "Defensive Firewall Access Control Rule Analysis",
        "slug": "firewall-access-control-analysis",
        "topic_slug": "firewall-rules",
        "description": "Evaluate stateful firewall rule tables, assess first-match rule processing, and test default-deny perimeter behavior.",
        "difficulty": "INTERMEDIATE",
        "estimated_minutes": 25,
        "environment_type": "CONCEPTUAL",
        "instructions": (
            "### Lab Overview\n\n"
            "Firewalls inspect incoming and outgoing packets and apply an Access Control List (ACL) rule table. "
            "Standard firewalls process rules sequentially from **Top to Bottom** and apply the action of the "
            "**first matching rule**. If no rules match, the final **Default Deny** rule drops the traffic.\n\n"
            "In this lab, you will audit a corporate perimeter firewall rule set."
        ),
        "objectives": [
            "Interpret a stateful firewall rule table (Rule #, Source, Destination, Port, Protocol, Action)",
            "Apply top-to-bottom rule ordering logic",
            "Verify that unlisted traffic is dropped by the implicit or explicit default-deny rule",
        ],
        "prerequisites": ["Understanding of IP addresses and TCP/UDP port numbers"],
        "steps": [
            {
                "step_number": 1,
                "title": "Evaluate Inbound Web Traffic",
                "description": "Analyze rule processing for inbound HTTP traffic.",
                "instructions": (
                    "Consider this Firewall Rule Table:\n\n"
                    "| Rule # | Action | Protocol | Source IP | Destination IP | Dest Port |\n"
                    "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                    "| 10 | DENY | TCP | 203.0.113.50 | Any | Any |\n"
                    "| 20 | ALLOW | TCP | Any | 192.168.1.100 | 443 |\n"
                    "| 30 | ALLOW | TCP | Any | 192.168.1.100 | 80 |\n"
                    "| 99 | DENY | Any | Any | Any | Any |\n\n"
                    "An external client with IP `198.51.100.22` attempts to connect to `192.168.1.100` on TCP port `80`.\n\n"
                    "What action does the firewall take?"
                ),
                "hint": "Rule 10 doesn't match (IP is different). Rule 20 doesn't match (port is 80, not 443). Rule 30 matches port 80 with action ALLOW.",
                "expected_observation": "The packet is allowed by Rule 30.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What action does the firewall take on the inbound TCP port 80 packet?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "ALLOW (matches Rule 30)",
                            "DENY (blocked by Rule 10)",
                            "DENY (blocked by Rule 99 Default Deny)",
                            "REDIRECT to port 443",
                        ],
                        "correct_option": "ALLOW (matches Rule 30)",
                        "explanation": "The firewall evaluates top-to-bottom. Rule 10 doesn't match. Rule 20 doesn't match. Rule 30 matches (TCP to 192.168.1.100:80) and specifies ALLOW.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Evaluate Default-Deny Security Behavior",
                "description": "Test packet fate when no explicit allow rule matches.",
                "instructions": (
                    "An external client attempts to connect to `192.168.1.100` on UDP port `53` (DNS query).\n\n"
                    "Reviewing Rules 10, 20, 30, and 99:\n\n"
                    "What happens to this UDP packet?"
                ),
                "hint": "None of rules 10-30 match UDP port 53. The packet falls through to Rule 99 (DENY Any Any).",
                "expected_observation": "The packet hits Rule 99 and is dropped.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What is the fate of the unexpected inbound UDP port 53 packet?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "DENY / DROPPED by Rule 99 (Default Deny)",
                            "ALLOWED automatically because UDP is connectionless",
                            "FORWARDED to the default gateway",
                            "STORED in the firewall memory buffer",
                        ],
                        "correct_option": "DENY / DROPPED by Rule 99 (Default Deny)",
                        "explanation": "In defensive firewall architecture, 'Default Deny' ensures that any traffic not explicitly permitted is blocked, preventing unauthorized services from being exposed.",
                    },
                },
            },
        ],
    },
]
