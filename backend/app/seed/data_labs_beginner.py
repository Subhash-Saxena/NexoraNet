"""Beginner Track Hands-on Labs Seed Data.

Ten complete, production-quality hands-on labs covering host networking,
interface inspection, MAC addressing, gateway routing, DNS lookup,
localhost connectivity, and socket diagnostics.
"""

from typing import Any

BEGINNER_LABS: list[dict[str, Any]] = [
    # LAB 1
    {
        "title": "Find Your Local IP Address",
        "slug": "find-local-ip-address",
        "topic_slug": "ipv4-basics",
        "description": "Discover your active network interface and extract your host IPv4 address and subnet mask using native operating system diagnostics.",
        "difficulty": "BEGINNER",
        "estimated_minutes": 15,
        "environment_type": "LOCAL_SYSTEM",
        "instructions": (
            "### Lab Overview\n\n"
            "Every computer connected to a network requires an IP address to send and receive packets. "
            "In this lab, you will run your operating system's native network query tool, locate your primary "
            "network interface, and record your local IPv4 address.\n\n"
            "> [!NOTE]\n"
            "> This lab runs entirely safely on your local workstation. NexoraNet never runs commands on your system."
        ),
        "objectives": [
            "Execute operating system command-line networking tools (ipconfig / ip addr / ifconfig)",
            "Identify the active network interface currently providing internet or LAN connectivity",
            "Locate and verify your host IPv4 dotted-decimal address",
            "Classify whether your IP address belongs to an RFC 1918 private address space",
        ],
        "prerequisites": [
            "Basic familiarity with opening a command terminal (Command Prompt, PowerShell, or Bash)",
            "Fundamental understanding of IPv4 dotted-decimal format (X.X.X.X)",
        ],
        "steps": [
            {
                "step_number": 1,
                "title": "Execute Network Configuration Command",
                "description": "Run the appropriate network interrogation utility for your operating system.",
                "instructions": (
                    "Open your terminal and run the network configuration command corresponding to your OS:\n\n"
                    "* **Windows (PowerShell or CMD)**: `ipconfig`\n"
                    "* **Linux**: `ip addr` or `ip a`\n"
                    "* **macOS**: `ifconfig`\n\n"
                    "Observe the output list of network adapters (Ethernet, Wi-Fi, Wireless LAN, or eth0/wlan0)."
                ),
                "hint": "On Windows, typing 'ipconfig' and pressing Enter displays all active network adapters.",
                "expected_observation": "A list of adapters with IPv4 addresses, subnet masks, and default gateways.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Which command-line utility did you use to inspect your network adapter configuration?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": ["ipconfig", "ip addr", "ifconfig", "traceroute"],
                        "correct_options": ["ipconfig", "ip addr", "ifconfig"],
                        "correct_option": "ipconfig",
                        "allow_any_correct": True,
                        "explanation": "Both ipconfig (Windows) and ip addr / ifconfig (Linux/macOS) are standard diagnostic utilities for listing IP addresses.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Extract Your Host IPv4 Address",
                "description": "Identify the dotted-decimal IPv4 address assigned to your active connection.",
                "instructions": (
                    "Look for the line labeled **IPv4 Address** (Windows) or **inet** (Linux/macOS) under your active adapter.\n\n"
                    "Enter your local IPv4 address below. Valid examples include `192.168.1.45`, `10.0.0.15`, or `172.16.1.100`."
                ),
                "hint": "IPv4 addresses consist of four numbers separated by dots (e.g., 192.168.x.x or 10.x.x.x).",
                "expected_observation": "A 32-bit dotted-decimal address assigned to your Wi-Fi or Ethernet adapter.",
                "validation_type": "IP_ADDRESS",
                "points": 15,
                "is_required": True,
                "question": {
                    "question_text": "Enter your active host IPv4 address:",
                    "question_type": "IP_ADDRESS",
                    "points": 15,
                    "answer_data": {
                        "expected_version": 4,
                        "placeholder": "e.g. 192.168.1.50",
                        "label": "Your Local IPv4 Address",
                        "explanation": "A valid IPv4 address consists of 4 octets (0-255) separated by periods.",
                    },
                },
            },
            {
                "step_number": 3,
                "title": "Classify Address Scope (Private vs Public)",
                "description": "Determine if your host address is an RFC 1918 private IP or public routable address.",
                "instructions": (
                    "Inspect the first octet of your IP address:\n\n"
                    "* **10.0.0.0 – 10.255.255.255** (10.0.0.0/8): Class A Private\n"
                    "* **172.16.0.0 – 172.31.255.255** (172.16.0.0/12): Class B Private\n"
                    "* **192.168.0.0 – 192.168.255.255** (192.168.0.0/16): Class C Private\n"
                    "* **127.0.0.0/8**: Loopback\n\n"
                    "Most home, campus, and office networks assign RFC 1918 private addresses behind a NAT router."
                ),
                "hint": "If your IP begins with 192.168, 10., or 172.16-31, it is an RFC 1918 private address.",
                "expected_observation": "Almost all end-user workstations run within private address space.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What type of address scope is assigned to your workstation's local network adapter?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "RFC 1918 Private Address (10.x, 172.16-31.x, 192.168.x)",
                            "Public Globally Routable Address",
                            "APIPA / Link-Local Auto-Assigned (169.254.x.x)",
                            "Loopback Diagnostic (127.0.0.1)",
                        ],
                        "correct_option": "RFC 1918 Private Address (10.x, 172.16-31.x, 192.168.x)",
                        "explanation": "RFC 1918 reserves 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16 for private LANs. Workstations reach the public internet via Network Address Translation (NAT).",
                    },
                },
            },
        ],
    },
    # LAB 2
    {
        "title": "Identify Your Network Interface",
        "slug": "identify-network-interfaces",
        "topic_slug": "network-devices",
        "description": "Inspect your machine's physical network interface cards (NICs) and virtual adapters to determine their operational link status.",
        "difficulty": "BEGINNER",
        "estimated_minutes": 15,
        "environment_type": "LOCAL_SYSTEM",
        "instructions": (
            "### Lab Overview\n\n"
            "Operating systems manage communication through Network Interface Cards (NICs), either physical "
            "(Ethernet ports, Wi-Fi antennas) or virtual (VPN tunnels, loopback, Docker bridges). "
            "In this lab, you will identify your machine's primary active NIC."
        ),
        "objectives": [
            "Distinguish physical hardware network adapters from virtual software interfaces",
            "Check operational state (UP / Connected vs DOWN / Media Disconnected)",
            "Identify the interface name recognized by the operating system kernel",
        ],
        "prerequisites": ["Completed Lab 1: Find Your Local IP Address"],
        "steps": [
            {
                "step_number": 1,
                "title": "List All Network Interfaces",
                "description": "Query all installed physical and virtual network adapters.",
                "instructions": (
                    "Run the following command:\n\n"
                    "* **Windows (PowerShell)**: `Get-NetAdapter` or `ipconfig /all`\n"
                    "* **Linux**: `ip link show`\n"
                    "* **macOS**: `networksetup -listallhardwareports`\n\n"
                    "Note the names of the adapters (e.g. Wi-Fi, Ethernet, eth0, en0, wlan0)."
                ),
                "hint": "In PowerShell, 'Get-NetAdapter' prints a neat table showing Name, InterfaceDescription, Status, and LinkSpeed.",
                "expected_observation": "Adapters labeled with status 'Up' or 'Connected'.",
                "validation_type": "TEXT",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Enter the name of your active adapter (e.g. 'Wi-Fi', 'Ethernet', 'eth0', 'en0', or 'wlan0'):",
                    "question_type": "TEXT",
                    "points": 10,
                    "answer_data": {
                        "accepted_answers": ["wi-fi", "wifi", "ethernet", "eth0", "eth1", "en0", "en1", "wlan0", "wlan1", "local area connection", "veth"],
                        "case_sensitive": False,
                        "placeholder": "e.g. Wi-Fi or eth0",
                        "explanation": "Operating systems designate hardware adapters with human-readable names or standard kernel prefixes (en=Ethernet, wl=Wireless).",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Verify Operational State",
                "description": "Confirm that the interface has an active carrier signal.",
                "instructions": (
                    "Examine the status column for your active adapter. In Linux, look for `<UP,BROADCAST,RUNNING>`. "
                    "In Windows, look for `Status: Up`.\n\n"
                    "What is the operational status of your active adapter?"
                ),
                "hint": "Active interfaces currently passing packets display the status 'Up' or 'Connected'.",
                "expected_observation": "The status is 'Up' or 'Connected'.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What is the operational link status of your active network adapter?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": ["Up / Connected", "Down / Disconnected", "Disabled", "Testing"],
                        "correct_option": "Up / Connected",
                        "explanation": "An interface must be in the UP operational state with a physical or wireless carrier signal to transmit Layer 2 frames.",
                    },
                },
            },
        ],
    },
    # LAB 3
    {
        "title": "Find Your MAC Address",
        "slug": "find-mac-address",
        "topic_slug": "mac-address",
        "description": "Inspect your hardware Layer 2 physical address (MAC) and understand the difference between OUI vendor bits and host identifier bytes.",
        "difficulty": "BEGINNER",
        "estimated_minutes": 15,
        "environment_type": "LOCAL_SYSTEM",
        "instructions": (
            "### Lab Overview\n\n"
            "While IP addresses change when moving between networks, the Media Access Control (MAC) address "
            "is a 48-bit physical hardware identifier burned into your Network Interface Card. "
            "In this lab, you will find your MAC address and analyze its structure."
        ),
        "objectives": [
            "Inspect the 48-bit EUI-48 physical address of your network card",
            "Differentiate the Organizationally Unique Identifier (OUI) from the device serial portion",
            "Understand why MAC addresses operate strictly at Layer 2 (Data Link layer)",
        ],
        "prerequisites": ["Basic understanding of hexadecimal notation"],
        "steps": [
            {
                "step_number": 1,
                "title": "Query Physical Hardware Address",
                "description": "Execute the tool to view the physical MAC address.",
                "instructions": (
                    "Run:\n\n"
                    "* **Windows**: `getmac /v` or `ipconfig /all` (look for Physical Address)\n"
                    "* **Linux**: `ip link show` (look for `link/ether`)\n"
                    "* **macOS**: `ifconfig en0` (look for `ether`)\n\n"
                    "A MAC address consists of 6 pairs of hexadecimal digits (e.g. `00:1A:2B:3C:4D:5E` or `00-1A-2B-3C-4D-5E`)."
                ),
                "hint": "Look for 12 hexadecimal characters separated by colons or hyphens.",
                "expected_observation": "A 6-byte hexadecimal physical address.",
                "validation_type": "TEXT",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "How many total bits compose a standard IEEE 802 MAC address?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": ["48 bits (6 bytes)", "32 bits (4 bytes)", "64 bits (8 bytes)", "128 bits (16 bytes)"],
                        "correct_option": "48 bits (6 bytes)",
                        "explanation": "A standard MAC address is 48 bits (6 octets). The first 24 bits represent the Organizationally Unique Identifier (OUI), and the last 24 bits are assigned by the manufacturer.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Distinguish OUI from NIC Serial",
                "description": "Analyze the two halves of a standard MAC address.",
                "instructions": (
                    "The IEEE assigns the first 3 octets (24 bits) to hardware vendors (such as Intel, Realtek, or Apple). "
                    "This prefix is known as the **Organizationally Unique Identifier (OUI)**.\n\n"
                    "What entity assigns and manages the OUI prefix pool?"
                ),
                "hint": "The Institute of Electrical and Electronics Engineers (IEEE) regulates MAC address allocations.",
                "expected_observation": "Understanding OUI manufacturer prefixes.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What does the first 24 bits (3 octets) of a MAC address represent?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "Organizationally Unique Identifier (OUI) assigned to the vendor",
                            "The subnet mask of the host adapter",
                            "The default gateway router identifier",
                            "The IP address mapped via DHCP",
                        ],
                        "correct_option": "Organizationally Unique Identifier (OUI) assigned to the vendor",
                        "explanation": "The first 3 bytes (24 bits) of a MAC address form the OUI registered with the IEEE. For example, 00:0C:29 is registered to VMware.",
                    },
                },
            },
        ],
    },
    # LAB 4
    {
        "title": "Find Your Default Gateway",
        "slug": "find-default-gateway",
        "topic_slug": "default-gateway",
        "description": "Locate the default gateway router on your local subnet and explain how packets leave your LAN.",
        "difficulty": "BEGINNER",
        "estimated_minutes": 15,
        "environment_type": "LOCAL_SYSTEM",
        "instructions": (
            "### Lab Overview\n\n"
            "When a computer wants to send data to an IP address outside its local subnet (such as a website on the internet), "
            "it forwards the frame to the **Default Gateway**—usually your home or office router. "
            "In this lab, you will find your default gateway's IP address."
        ),
        "objectives": [
            "Locate the default gateway IP address on your system",
            "Understand why a gateway is required to communicate outside your local broadcast domain",
            "Verify that your default gateway shares the same network prefix as your host IP",
        ],
        "prerequisites": ["Completed Lab 1: Find Your Local IP Address"],
        "steps": [
            {
                "step_number": 1,
                "title": "Identify Default Gateway IP",
                "description": "Extract the gateway router IP from your network settings.",
                "instructions": (
                    "Run:\n\n"
                    "* **Windows**: `ipconfig` (look for `Default Gateway`)\n"
                    "* **Linux**: `ip route | grep default`\n"
                    "* **macOS**: `netstat -nr | grep default`\n\n"
                    "Common default gateway IPs include `192.168.1.1`, `192.168.0.1`, or `10.0.0.1`."
                ),
                "hint": "The default gateway is the local router IP that forwards off-subnet traffic.",
                "expected_observation": "An IPv4 address ending typically in .1 or .254.",
                "validation_type": "IP_ADDRESS",
                "points": 15,
                "is_required": True,
                "question": {
                    "question_text": "Enter your network's Default Gateway IPv4 address:",
                    "question_type": "IP_ADDRESS",
                    "points": 15,
                    "answer_data": {
                        "expected_version": 4,
                        "placeholder": "e.g. 192.168.1.1",
                        "label": "Default Gateway IP",
                        "explanation": "The default gateway is the Layer 3 router on your local subnet that routes packets destined for foreign networks.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Understand Gateway Purpose",
                "description": "Explain how host routing logic decides when to send packets to the gateway.",
                "instructions": (
                    "When your host determines that a destination IP is **not** on the local subnet (by applying the subnet mask), "
                    "what does it do with the packet?"
                ),
                "hint": "Packets for remote networks are addressed at Layer 2 to the default gateway's MAC address.",
                "expected_observation": "Frames are forwarded to the default gateway router.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Where does a host forward a packet when the destination IP is on a remote network?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "To the Default Gateway's MAC address for routing",
                            "Directly to the destination host over broadcast",
                            "To the local DNS resolver server",
                            "It drops the packet immediately",
                        ],
                        "correct_option": "To the Default Gateway's MAC address for routing",
                        "explanation": "If the destination IP does not match the local subnet, the host resolves the gateway's MAC address via ARP and forwards the frame to the gateway router.",
                    },
                },
            },
        ],
    },
    # LAB 5
    {
        "title": "Inspect Your Local Routing Table",
        "slug": "inspect-routing-table",
        "topic_slug": "routing-table-analysis",
        "description": "Read the operating system kernel IP routing table, identify the 0.0.0.0 default route, and understand route metrics.",
        "difficulty": "BEGINNER",
        "estimated_minutes": 20,
        "environment_type": "LOCAL_SYSTEM",
        "instructions": (
            "### Lab Overview\n\n"
            "Every host maintains a local routing table in memory that tells the OS kernel how to route packets. "
            "In this lab, you will inspect your host routing table and identify the default route of last resort."
        ),
        "objectives": [
            "Display the host IP routing table using CLI diagnostic tools",
            "Locate the default route of last resort (0.0.0.0 with mask 0.0.0.0)",
            "Explain the role of route metrics in multi-homed path selection",
        ],
        "prerequisites": ["Completed Lab 4: Find Your Default Gateway"],
        "steps": [
            {
                "step_number": 1,
                "title": "Display Kernel Routing Table",
                "description": "Execute the route print command to list active routes.",
                "instructions": (
                    "Run:\n\n"
                    "* **Windows**: `route print` or `netstat -r`\n"
                    "* **Linux**: `ip route` or `netstat -rn`\n"
                    "* **macOS**: `netstat -nr`\n\n"
                    "Observe the column headers: Network Destination, Netmask, Gateway, Interface, and Metric."
                ),
                "hint": "The route table shows all destinations your computer knows how to reach.",
                "expected_observation": "A routing table containing loopback routes, local subnet routes, and the 0.0.0.0 default route.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What network destination represents the default route (gateway of last resort)?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "0.0.0.0 (with mask 0.0.0.0 or /0)",
                            "127.0.0.1 (with mask 255.0.0.0)",
                            "255.255.255.255 (with mask 255.255.255.255)",
                            "192.168.1.255 (with mask 255.255.255.0)",
                        ],
                        "correct_option": "0.0.0.0 (with mask 0.0.0.0 or /0)",
                        "explanation": "0.0.0.0/0 matches any destination IP that doesn't have a more specific route entry in the routing table.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Understand Route Metrics",
                "description": "Explain how the operating system decides between multiple active adapters.",
                "instructions": (
                    "If your computer has both Ethernet and Wi-Fi connected simultaneously, both adapters may offer a default route. "
                    "The operating system uses the **Metric** value to break ties.\n\n"
                    "Does the operating system prefer a lower or higher route metric?"
                ),
                "hint": "Just like golf scores or distance, lower routing metrics represent faster, more preferred paths.",
                "expected_observation": "Lower metric routes are prioritized.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "When two matching routes exist, which route metric is prioritized by the routing engine?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "Lower metric (represents lower cost or higher bandwidth)",
                            "Higher metric (represents higher capacity)",
                            "Random selection between available paths",
                            "The route that was added most recently",
                        ],
                        "correct_option": "Lower metric (represents lower cost or higher bandwidth)",
                        "explanation": "In IP routing, lower metric values indicate a preferred, lower-cost path. Fast Ethernet typically gets a lower metric than slower Wi-Fi.",
                    },
                },
            },
        ],
    },
    # LAB 6
    {
        "title": "Perform a DNS Lookup",
        "slug": "perform-dns-lookup",
        "topic_slug": "dns",
        "description": "Query domain name system records using nslookup, inspect the responding resolver server, and verify A record resolution.",
        "difficulty": "BEGINNER",
        "estimated_minutes": 15,
        "environment_type": "LOCAL_SYSTEM",
        "instructions": (
            "### Lab Overview\n\n"
            "Humans remember domain names like `example.com`, but routers require numeric IP addresses. "
            "The Domain Name System (DNS) translates human names into IP addresses. "
            "In this lab, you will query a domain name and inspect the DNS response."
        ),
        "objectives": [
            "Use the nslookup command-line tool to query DNS records",
            "Identify the configured DNS resolver server IP address servicing your request",
            "Distinguish between authoritative and non-authoritative DNS responses",
        ],
        "prerequisites": ["Basic understanding of domain names and IP addresses"],
        "steps": [
            {
                "step_number": 1,
                "title": "Query Domain Resolution",
                "description": "Run nslookup against a standard safe test domain.",
                "instructions": (
                    "Open your terminal and run:\n\n"
                    "```bash\nnslookup example.com\n```\n\n"
                    "Look at the first two lines showing **Server** and **Address**. That is your configured DNS recursive resolver."
                ),
                "hint": "The first section indicates the DNS server answering your query (such as your router, 8.8.8.8, or 1.1.1.1).",
                "expected_observation": "The resolver IP and the resolved IPv4 A record for example.com (93.184.215.14 or similar).",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What standard DNS record type maps a hostname to an IPv4 address?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": ["A Record", "AAAA Record", "MX Record", "CNAME Record"],
                        "correct_option": "A Record",
                        "explanation": "An 'A' record (Address record) maps a hostname to an IPv4 address. 'AAAA' maps to IPv6, 'MX' maps mail servers, and 'CNAME' creates an alias.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Identify DNS Server Port",
                "description": "Verify the standard transport port utilized by DNS queries.",
                "instructions": (
                    "When your computer sends a DNS query to your recursive resolver, what destination transport port does it use?"
                ),
                "hint": "DNS operates over UDP (and TCP for large responses) on standard port 53.",
                "expected_observation": "Port 53 is used for DNS.",
                "validation_type": "PORT",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What standard port number is used by the Domain Name System (DNS)?",
                    "question_type": "PORT",
                    "points": 10,
                    "answer_data": {
                        "expected_port": 53,
                        "placeholder": "e.g. 53",
                        "label": "DNS Port Number",
                        "explanation": "DNS uses UDP port 53 for standard queries and TCP port 53 for zone transfers or responses exceeding 512 bytes.",
                    },
                },
            },
        ],
    },
    # LAB 7
    {
        "title": "Test Localhost Connectivity",
        "slug": "test-localhost-connectivity",
        "topic_slug": "icmp",
        "description": "Verify that your host's local TCP/IP protocol stack is functioning properly by pinging the loopback address 127.0.0.1 and ::1.",
        "difficulty": "BEGINNER",
        "estimated_minutes": 15,
        "environment_type": "LOCAL_SYSTEM",
        "instructions": (
            "### Lab Overview\n\n"
            "The loopback address (127.0.0.1 in IPv4 and ::1 in IPv6) is a special internal address "
            "that routes packets directly back into your computer's operating system kernel without transmitting "
            "any electrical or radio signals onto the physical wire. "
            "Pinging loopback verifies that your TCP/IP protocol stack is healthy."
        ),
        "objectives": [
            "Execute an ICMP echo test against the loopback interface",
            "Understand why loopback traffic never traverses the physical network wire",
            "Identify the IPv4 and IPv6 loopback reserved addresses",
        ],
        "prerequisites": ["Basic command-line terminal usage"],
        "steps": [
            {
                "step_number": 1,
                "title": "Ping IPv4 Loopback",
                "description": "Send ICMP echo requests to 127.0.0.1.",
                "instructions": (
                    "Run in your terminal:\n\n"
                    "```bash\nping 127.0.0.1\n```\n\n"
                    "Observe the round-trip time (RTT). It should typically be <1 ms because the kernel handles the packet internally."
                ),
                "hint": "A successful ping returns 'Reply from 127.0.0.1: bytes=32 time<1ms TTL=128'.",
                "expected_observation": "Four successful ICMP replies with near-zero latency.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What does a successful ping to 127.0.0.1 confirm about your computer?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "The local TCP/IP protocol stack and network drivers are installed and functioning",
                            "Your computer has an active internet connection to Google",
                            "Your router's Wi-Fi antenna is broadcasting an SSID",
                            "The DNS server is reachable and resolving names",
                        ],
                        "correct_option": "The local TCP/IP protocol stack and network drivers are installed and functioning",
                        "explanation": "Pinging loopback tests only internal operating system networking software. It succeeds even if your network cable is unplugged and Wi-Fi is turned off.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Verify IPv6 Loopback",
                "description": "Ping the IPv6 equivalent of the loopback interface.",
                "instructions": (
                    "In IPv6, the entire loopback address space is compressed down to a single address: `::1`.\n\n"
                    "Run:\n\n"
                    "```bash\nping ::1\n```\n\n"
                    "Enter the IPv6 loopback address below."
                ),
                "hint": "IPv6 loopback is written as two colons followed by a one: ::1.",
                "expected_observation": "Successful ICMPv6 ping to ::1.",
                "validation_type": "IP_ADDRESS",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Enter the standard IPv6 loopback address:",
                    "question_type": "IP_ADDRESS",
                    "points": 10,
                    "answer_data": {
                        "expected_ip": "::1",
                        "expected_version": 6,
                        "placeholder": "e.g. ::1",
                        "label": "IPv6 Loopback Address",
                        "explanation": "::1 represents 0000:0000:0000:0000:0000:0000:0000:0001, the official IPv6 loopback address defined in RFC 4291.",
                    },
                },
            },
        ],
    },
    # LAB 8
    {
        "title": "Identify Listening Ports and Services",
        "slug": "identify-listening-ports",
        "topic_slug": "ports-and-sockets",
        "description": "Inspect active network sockets on your system using netstat or ss, filter for LISTENING states, and correlate port numbers with network services.",
        "difficulty": "BEGINNER",
        "estimated_minutes": 20,
        "environment_type": "LOCAL_SYSTEM",
        "instructions": (
            "### Lab Overview\n\n"
            "Server applications (like web servers, SSH daemons, or database servers) open network ports and wait "
            "for incoming client connections. This state is known as **LISTENING**. "
            "In this lab, you will discover which ports are currently open on your machine."
        ),
        "objectives": [
            "Use socket inspection tools (netstat / ss) to view local listening ports",
            "Understand the difference between 0.0.0.0:port (all interfaces) and 127.0.0.1:port (local only)",
            "Identify the security implications of open listening ports",
        ],
        "prerequisites": ["Basic understanding of TCP and UDP ports"],
        "steps": [
            {
                "step_number": 1,
                "title": "List Listening Sockets",
                "description": "Execute socket status command to view listening ports.",
                "instructions": (
                    "Run in your terminal:\n\n"
                    "* **Windows**: `netstat -ano | findstr LISTENING`\n"
                    "* **Linux**: `ss -tuln` or `netstat -tuln`\n"
                    "* **macOS**: `netstat -an | grep LISTEN`\n\n"
                    "Notice the columns: Proto (TCP/UDP), Local Address (IP:Port), and State (LISTENING)."
                ),
                "hint": "A socket bound to 127.0.0.1 only accepts connections from the local machine. 0.0.0.0 accepts connections from any network interface.",
                "expected_observation": "A list of listening TCP ports with their process IDs (PIDs).",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What does a socket listening on 127.0.0.1:8080 signify from a security perspective?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "It can only be accessed by applications running locally on the same machine",
                            "It is publicly accessible to any attacker on the local Wi-Fi network",
                            "It has been blocked by the operating system firewall",
                            "It uses UDP instead of TCP for transport",
                        ],
                        "correct_option": "It can only be accessed by applications running locally on the same machine",
                        "explanation": "Binding a service to 127.0.0.1 restricts access strictly to the local host, preventing remote attackers on the LAN or Internet from connecting.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Match Standard Web Port",
                "description": "Identify the standard encrypted web port.",
                "instructions": (
                    "When a web server hosts a secure website using HTTPS with TLS encryption, what standard TCP port does it listen on?"
                ),
                "hint": "HTTP is 80, HTTPS is 443.",
                "expected_observation": "HTTPS listens on port 443.",
                "validation_type": "PORT",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What standard TCP port is utilized by secure HTTPS web servers?",
                    "question_type": "PORT",
                    "points": 10,
                    "answer_data": {
                        "expected_port": 443,
                        "placeholder": "e.g. 443",
                        "label": "HTTPS Port",
                        "explanation": "TCP port 443 is the IANA-assigned standard port for HTTPS (HTTP over TLS/SSL).",
                    },
                },
            },
        ],
    },
    # LAB 9
    {
        "title": "Compare IPv4 and IPv6 Configurations",
        "slug": "compare-ipv4-ipv6",
        "topic_slug": "ipv4-address-structure",
        "description": "Analyze both IPv4 and IPv6 address formats assigned to your host adapter and understand address sizing and link-local scopes.",
        "difficulty": "BEGINNER",
        "estimated_minutes": 15,
        "environment_type": "LOCAL_SYSTEM",
        "instructions": (
            "### Lab Overview\n\n"
            "Modern operating systems run 'dual-stack' networking, operating IPv4 and IPv6 simultaneously. "
            "In this lab, you will compare 32-bit IPv4 addresses with 128-bit IPv6 addresses on your workstation."
        ),
        "objectives": [
            "Identify link-local IPv6 addresses (fe80::/10) on your adapter",
            "Contrast the 32-bit (4 billion addresses) IPv4 pool with the 128-bit (340 undecillion) IPv6 pool",
            "Understand why link-local IPv6 addresses do not require a DHCP server",
        ],
        "prerequisites": ["Basic understanding of hexadecimal and binary numbering"],
        "steps": [
            {
                "step_number": 1,
                "title": "Inspect Link-Local IPv6 Address",
                "description": "Locate the fe80:: address on your network adapter.",
                "instructions": (
                    "Run `ipconfig` (Windows) or `ip addr` (Linux) and look for **Link-local IPv6 Address**.\n\n"
                    "All link-local IPv6 addresses begin with the prefix `fe80::`."
                ),
                "hint": "Link-local addresses start with fe80: and are automatically generated for communication on the local segment.",
                "expected_observation": "An address starting with fe80: followed by hexadecimal chunks.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "What prefix identifies an IPv6 Link-Local address?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": ["fe80::/10", "2001::/16", "192.168.0.0/16", "fc00::/7"],
                        "correct_option": "fe80::/10",
                        "explanation": "fe80::/10 is reserved for link-local unicast. These addresses are automatically configured on every IPv6 interface for intra-segment communication.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Calculate Address Space Capacity",
                "description": "Compare total bits between IPv4 and IPv6.",
                "instructions": (
                    "How many bits comprise an IPv6 address compared to an IPv4 address?"
                ),
                "hint": "IPv4 has 32 bits. IPv6 quadruples the bit length to 128 bits.",
                "expected_observation": "IPv6 has 128 bits.",
                "validation_type": "NUMERICAL",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "How many total bits make up an IPv6 address?",
                    "question_type": "NUMERICAL",
                    "points": 10,
                    "answer_data": {
                        "expected_value": 128,
                        "tolerance": 0,
                        "placeholder": "e.g. 128",
                        "label": "IPv6 Bit Length",
                        "explanation": "IPv6 addresses are 128 bits long (16 bytes), providing 2^128 (approx. 3.4 x 10^38) unique addresses.",
                    },
                },
            },
        ],
    },
    # LAB 10
    {
        "title": "Map Your Complete Network Configuration",
        "slug": "map-network-configuration",
        "topic_slug": "ipconfig-ifconfig-ip",
        "description": "Synthesize a full host networking profile: IP address, subnet mask, default gateway, DNS server, and MAC address.",
        "difficulty": "BEGINNER",
        "estimated_minutes": 20,
        "environment_type": "LOCAL_SYSTEM",
        "instructions": (
            "### Lab Overview\n\n"
            "Network engineers and cybersecurity analysts frequently map a host's entire network identity "
            "during incident triage. In this capstone Beginner lab, you will synthesize all parameters: "
            "IP, Subnet Mask, Gateway, DNS, and MAC."
        ),
        "objectives": [
            "Extract the complete 5-parameter network identity of your host",
            "Verify that your host IP and Gateway share the same network prefix via the subnet mask",
            "Synthesize host networking concepts learned across all Beginner labs",
        ],
        "prerequisites": ["Completed Labs 1 through 9"],
        "steps": [
            {
                "step_number": 1,
                "title": "Extract Subnet Mask",
                "description": "Identify the 32-bit subnet mask configured on your adapter.",
                "instructions": (
                    "Run `ipconfig` (Windows) or `ifconfig` / `ip -o -f inet addr show` (Linux).\n\n"
                    "Common subnet masks on home/office LANs include `255.255.255.0` (/24) or `255.255.0.0` (/16).\n\n"
                    "Enter your subnet mask below."
                ),
                "hint": "Standard Class C LANs use 255.255.255.0.",
                "expected_observation": "A contiguous mask such as 255.255.255.0.",
                "validation_type": "IP_ADDRESS",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Enter your adapter's IPv4 Subnet Mask:",
                    "question_type": "IP_ADDRESS",
                    "points": 10,
                    "answer_data": {
                        "expected_version": 4,
                        "placeholder": "e.g. 255.255.255.0",
                        "label": "Subnet Mask",
                        "explanation": "The subnet mask defines where the network bits end and where the host bits begin.",
                    },
                },
            },
            {
                "step_number": 2,
                "title": "Confirm Subnet Membership Logic",
                "description": "Verify why host IP and Default Gateway must share the same network prefix.",
                "instructions": (
                    "Why must your host IP address and your default gateway share the same network portion of the address?"
                ),
                "hint": "A host cannot send packets directly to a gateway that is on a different subnet without already having a router.",
                "expected_observation": "The gateway must be locally reachable on the same broadcast domain.",
                "validation_type": "SINGLE_CHOICE",
                "points": 10,
                "is_required": True,
                "question": {
                    "question_text": "Why must a workstation and its default gateway share the same network prefix?",
                    "question_type": "SINGLE_CHOICE",
                    "points": 10,
                    "answer_data": {
                        "options": [
                            "So the host can reach the gateway directly via Layer 2 ARP on the local broadcast domain",
                            "Because IPv4 requires all devices in a country to share the same prefix",
                            "So the DNS server can resolve private hostnames",
                            "To encrypt packets sent over the physical wire",
                        ],
                        "correct_option": "So the host can reach the gateway directly via Layer 2 ARP on the local broadcast domain",
                        "explanation": "A workstation uses ARP to discover the gateway's MAC address. ARP broadcasts cannot cross routers, so the gateway must reside on the same local subnet.",
                    },
                },
            },
        ],
    },
]
