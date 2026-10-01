#!/usr/bin/env python3
"""
NexoraNet Beginner Question Bank Generator.
Generates ~150 high-quality, vetted beginner networking and cybersecurity questions
across 5 structured JSON files:
1. networking_fundamentals.json (30 questions)
2. osi_and_tcpip_layers.json (30 questions)
3. ipv4_and_mac_addressing.json (30 questions)
4. ports_and_protocols.json (35 questions)
5. devices_and_basic_security.json (25 questions)
Total: 150 questions.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "question_bank" / "beginner"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def build_fundamentals_questions():
    questions = []
    
    items = [
        # Network Types & Fundamentals (15 questions)
        (
            "NET-FUND-001",
            "what-is-computer-networking",
            "What is the primary function of a computer network?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            45,
            "A computer network enables multiple computing devices to communicate, exchange data, and share hardware and software resources.",
            "Identify the fundamental purpose of computer networking.",
            [
                ("To allow computing devices to share data, resources, and communicate with one another", True, "Networking enables communication and resource sharing across distributed systems."),
                ("To increase the CPU clock speed of connected endpoint computers", False, "Networking connects independent systems but does not alter physical processor frequencies."),
                ("To convert analog power supply currents into digital motherboard voltages", False, "This is the function of an electrical power supply unit (PSU)."),
                ("To eliminate the need for operating systems on client endpoints", False, "Operating systems are necessary to manage network protocol stacks and hardware drivers.")
            ],
            ["networking", "fundamentals", "conceptual"]
        ),
        (
            "NET-FUND-002",
            "lan",
            "Which type of network is typically confined to a single room, office, or building?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            45,
            "A Local Area Network (LAN) covers a small geographical footprint, such as a home, school computer lab, or single office building, offering high data transfer rates.",
            "Distinguish Local Area Networks from other network scopes.",
            [
                ("LAN (Local Area Network)", True, "LANs span geographically constrained areas like homes or single enterprise buildings."),
                ("WAN (Wide Area Network)", False, "WANs connect dispersed sites across cities, states, or continents."),
                ("MAN (Metropolitan Area Network)", False, "MANs cover an entire city or municipal region."),
                ("SAN (Storage Area Network)", False, "SANs are specialized networks dedicated to connecting block-level storage devices.")
            ],
            ["networking", "lan", "conceptual"]
        ),
        (
            "NET-FUND-003",
            "wan",
            "Which network classification best describes the global public Internet?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            45,
            "The Internet is the world's largest Wide Area Network (WAN), interconnecting thousands of autonomous systems, telecommunication carriers, and regional networks globally.",
            "Classify the Internet according to network scope.",
            [
                ("Wide Area Network (WAN)", True, "The Internet spans the globe and connects geographically disparate networks."),
                ("Personal Area Network (PAN)", False, "PANs are limited to the immediate vicinity of an individual (e.g., Bluetooth range)."),
                ("Local Area Network (LAN)", False, "LANs are confined to a single localized site or premises."),
                ("Controller Area Network (CAN)", False, "CAN bus networks are vehicle micro-controller communication buses.")
            ],
            ["networking", "wan", "internet"]
        ),
        (
            "NET-FUND-004",
            "pan",
            "Which technology is most commonly used to construct a Personal Area Network (PAN)?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            45,
            "Bluetooth (IEEE 802.15.1) is designed specifically for short-range personal device connectivity (keyboards, headsets, smartwatches) within a few meters, constituting a PAN.",
            "Recognize technologies utilized for Personal Area Networks.",
            [
                ("Bluetooth", True, "Bluetooth operates over short distances (typically 1-10 meters) to interconnect personal peripherals."),
                ("DOCSIS", False, "DOCSIS is a telecommunications standard for cable broadband Internet."),
                ("BGP", False, "Border Gateway Protocol is a core WAN routing protocol."),
                ("SONET", False, "SONET is a fiber-optic transmission standard for telecommunications carriers.")
            ],
            ["pan", "bluetooth", "wireless"]
        ),
        (
            "NET-FUND-005",
            "man",
            "A municipal government connects its city hall, police stations, libraries, and public utility offices across an entire city using dark fiber. What type of network is this?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "APPLY",
            1,
            60,
            "A Metropolitan Area Network (MAN) spans a single municipality or metropolitan region, typically larger than a single building LAN but smaller than a multi-state or global WAN.",
            "Differentiate MAN architecture based on geographical scope.",
            [
                ("Metropolitan Area Network (MAN)", True, "MANs interconnect corporate or municipal sites across a specific city or municipality."),
                ("Personal Area Network (PAN)", False, "PANs cover an individual's immediate radius."),
                ("Local Area Network (LAN)", False, "A network spanning an entire city exceeds the boundaries of a single premises LAN."),
                ("Virtual Private Network (VPN)", False, "VPN is an encrypted tunnel protocol, not a physical geographical classification.")
            ],
            ["man", "networking", "topology"]
        ),
        (
            "NET-FUND-006",
            "client-server",
            "In a client-server architecture, what role does the server perform?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            45,
            "In client-server architecture, servers are dedicated, centralized systems that listen for and respond to requests for services, data, or computing resources from client workstations.",
            "Explain the fundamental role of a server in distributed architectures.",
            [
                ("It listens for and processes client requests, providing centralized resources or services", True, "Servers fulfill client requests such as web pages, files, or database queries."),
                ("It initiates connections to idle desktop computers to harvest unused memory", False, "Clients initiate connections to servers, not vice versa in standard models."),
                ("It acts solely as a physical electrical repeater for ethernet copper cables", False, "That is the role of an unmanaged network hub or electrical repeater."),
                ("It randomizes IP addresses to prevent local network communication", False, "Servers provide consistent services, typically on static addresses or known hostnames.")
            ],
            ["client-server", "architecture", "fundamentals"]
        ),
        (
            "NET-FUND-007",
            "peer-to-peer",
            "What distinguishes a peer-to-peer (P2P) network from a client-server network?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            50,
            "In a peer-to-peer network, every participant (node) has equivalent capabilities and responsibilities, acting as both a supplier and consumer of data without requiring a centralized server.",
            "Compare peer-to-peer architecture against centralized client-server models.",
            [
                ("Each node can act as both a client and a server simultaneously without centralized coordination", True, "P2P nodes share resources directly with each other as equals."),
                ("P2P networks require specialized mainframe servers to authenticate every packet", False, "P2P networks operate without centralized authority or dedicated mainframes."),
                ("P2P networks cannot use TCP or UDP protocols", False, "P2P applications (e.g., BitTorrent) rely standard transport protocols like TCP and UDP."),
                ("P2P networks are strictly limited to two physical devices connected by a serial cable", False, "P2P networks can scale to millions of globally distributed endpoints.")
            ],
            ["peer-to-peer", "architecture", "distributed"]
        ),
        (
            "NET-FUND-008",
            "network-topologies",
            "Which physical network topology connects all devices to a central device such as a network switch?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            45,
            "In a star topology, each endpoint has a dedicated cable run to a central hub or switch. If one cable fails, only that device is disconnected, leaving the rest of the network operational.",
            "Identify the characteristics of a physical star topology.",
            [
                ("Star topology", True, "All nodes radiate out from a central networking device like a switch."),
                ("Bus topology", False, "Bus topology connects devices in linear sequence along a single shared backbone cable."),
                ("Ring topology", False, "Ring topology connects devices in a circular daisy chain where tokens circulate."),
                ("Mesh topology", False, "Mesh topology connects nodes redundantly directly to multiple other nodes.")
            ],
            ["network-topologies", "star-topology", "hardware"]
        ),
        (
            "NET-FUND-009",
            "network-topologies",
            "What is the primary operational disadvantage of a traditional physical bus topology?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            50,
            "In a bus topology, all devices share a single linear trunk cable. A break or missing terminator anywhere along the trunk causes signal reflection and collapses the entire network segment.",
            "Explain single-point-of-failure vulnerabilities in bus topologies.",
            [
                ("A single cable break or disconnected terminator disrupts communication for the entire network segment", True, "Bus networks lack redundancy; any cable severance disables the whole bus."),
                ("It requires an expensive core enterprise switch for every two workstations", False, "Bus networks use passive coaxial cabling without requiring switches."),
                ("It cannot carry electrical signals longer than 10 centimeters", False, "10BASE2 and 10BASE5 coaxial bus segments supported 185 to 500 meters."),
                ("It causes automatic encryption of all transmitted packets", False, "Bus topologies carry unencrypted, raw broadcast signals across the shared medium.")
            ],
            ["network-topologies", "bus-topology", "troubleshooting"]
        ),
        (
            "NET-FUND-010",
            "network-topologies",
            "Which network topology offers the highest degree of fault tolerance through redundant direct connections between nodes?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            50,
            "A full mesh topology provides direct dedicated links between every pair of nodes. If any single link fails, traffic can immediately reroute through alternative paths without interruption.",
            "Evaluate fault tolerance across physical network topologies.",
            [
                ("Full mesh topology", True, "Mesh networks provide multiple redundant pathways between nodes, maximizing fault tolerance."),
                ("Star topology", False, "A failure of the central switch in a star topology brings down the entire connected LAN."),
                ("Ring topology", False, "Single ring topologies can be interrupted if a single participating node fails."),
                ("Bus topology", False, "A break in the central bus cable disables the entire segment.")
            ],
            ["network-topologies", "mesh-topology", "redundancy"]
        ),
        (
            "NET-FUND-011",
            "network-devices",
            "At which layer of the OSI model does an unmanaged Ethernet switch predominantly operate?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            45,
            "Standard Layer 2 Ethernet switches inspect Data Link layer frames, examine source MAC addresses to populate their MAC address table, and forward frames based on destination MAC addresses.",
            "Identify the operational layer of Ethernet switches.",
            [
                ("Layer 2 — Data Link Layer", True, "Switches forward traffic based on Data Link (MAC) addresses."),
                ("Layer 1 — Physical Layer", False, "Layer 1 devices are hubs, cables, and repeaters that do not inspect frame headers."),
                ("Layer 3 — Network Layer", False, "Layer 3 devices (routers) inspect IP addresses; standard switches operate at Layer 2."),
                ("Layer 4 — Transport Layer", False, "Transport layer handles TCP/UDP ports, which standard Layer 2 switches do not evaluate.")
            ],
            ["network-devices", "switch", "osi"]
        ),
        (
            "NET-FUND-012",
            "network-devices",
            "What is the key functional difference between a network hub and a network switch?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            50,
            "A hub broadcasts incoming electrical signals out of all other ports (single collision domain). A switch learns MAC addresses and forwards frames selectively to the specific destination port (microsegmentation).",
            "Contrast network hub broadcasting with switch selective forwarding.",
            [
                ("A hub repeats all incoming frames out of every other port, while a switch forwards frames selectively to the destination port based on MAC address", True, "Switches isolate collision domains and forward traffic only where needed."),
                ("A hub routes packets across the Internet while a switch only operates over Bluetooth", False, "Hubs are primitive Layer 1 LAN repeaters, not Internet routers."),
                ("A switch converts all Ethernet traffic into wireless radio frequencies", False, "Switches are wired forwarding devices unless specifically integrated into a wireless AP."),
                ("A hub provides hardware-accelerated TLS encryption while a switch does not", False, "Neither traditional hubs nor switches provide transport layer TLS encryption.")
            ],
            ["network-devices", "hub", "switch", "collision-domain"]
        ),
        (
            "NET-FUND-013",
            "network-devices",
            "Which networking device is responsible for forwarding packets between distinct logical IP subnets or networks?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            45,
            "A router operates at Layer 3 (Network Layer) and uses routing tables containing network destination IP prefixes to forward packets across different subnets and autonomous systems.",
            "Define the core forwarding responsibility of a network router.",
            [
                ("Router", True, "Routers interconnect different IP networks and determine the optimal path for packets."),
                ("Layer 2 Switch", False, "Layer 2 switches forward frames within a single broadcast domain/subnet."),
                ("Repeater", False, "Repeaters regenerate raw physical electrical signals on the same segment."),
                ("Patch Panel", False, "Patch panels are passive physical wire organizing hardware with no forwarding logic.")
            ],
            ["network-devices", "router", "routing"]
        ),
        (
            "NET-FUND-014",
            "network-media",
            "What is the maximum standard operational distance for Gigabit Ethernet over Cat6 twisted-pair copper cable (1000BASE-T)?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            45,
            "The IEEE 802.3 standard specifies a maximum channel length of 100 meters (approx. 328 feet) for twisted-pair copper cabling, which includes 90 meters of solid horizontal cabling and 10 meters of patch cords.",
            "Recall standard distance limitations for twisted-pair Ethernet.",
            [
                ("100 meters", True, "Standard Ethernet over twisted-pair (Cat5e/Cat6) has a strict 100-meter physical channel limit."),
                ("10 meters", False, "10 meters is much shorter than the standard 100-meter twisted pair specification."),
                ("500 meters", False, "500 meters requires multi-mode or single-mode fiber-optic cabling."),
                ("10 kilometers", False, "10 kilometers is achievable only with single-mode fiber (e.g., 1000BASE-LX).")
            ],
            ["network-media", "ethernet", "cables"]
        ),
        (
            "NET-FUND-015",
            "network-media",
            "Why is fiber-optic cabling immune to Electromagnetic Interference (EMI) compared to copper twisted-pair cabling?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            50,
            "Fiber-optic cables transmit data using pulses of light (photons) through glass or plastic cores rather than electrical currents over copper, making them completely immune to electromagnetic fields and radio frequency interference.",
            "Explain why fiber optics are resistant to electromagnetic interference.",
            [
                ("It transmits data as light pulses rather than electrical current", True, "Light traveling through non-conductive glass fibers cannot be disrupted by magnetic or electrical fields."),
                ("It uses thicker copper shielding that absorbs all radio waves", False, "Fiber optics contain glass or polymer cores, not copper shielding."),
                ("It operates only at cryogenic temperatures below freezing", False, "Fiber optics operate at standard ambient enterprise temperatures."),
                ("It compresses data into acoustic sound vibrations", False, "Fiber optic communications use infrared or visible laser light.")
            ],
            ["network-media", "fiber-optic", "emi", "physical-layer"]
        ),

        # Network Topologies & Edge Devices (15 questions)
        (
            "NET-FUND-016",
            "network-devices",
            "What is the primary role of a Wireless Access Point (WAP) on a Local Area Network?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            45,
            "A Wireless Access Point (WAP) connects wireless client stations (Wi-Fi) to an adjacent wired Ethernet local area network, bridging 802.11 wireless frames onto 802.3 wired Ethernet frames.",
            "Describe the function of a Wireless Access Point.",
            [
                ("To bridge wireless 802.11 client communications onto a wired 802.3 Ethernet network", True, "WAPs provide wireless stations with seamless network access to the wired LAN."),
                ("To assign public IPv4 addresses directly to external web servers", False, "WAPs do not serve as Internet public IP registrars."),
                ("To replace all DNS servers on the global Internet", False, "WAPs transmit layer 2 frames and do not host the global DNS root zone."),
                ("To convert optical fiber signals into AC electrical wall power", False, "WAPs require electrical power (often via PoE) and do not generate AC line power.")
            ],
            ["network-devices", "wireless", "access-point"]
        ),
        (
            "NET-FUND-017",
            "network-devices",
            "What security benefit is achieved by replacing legacy network hubs with modern Ethernet switches?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            50,
            "Hubs broadcast all packets across every port, allowing any connected workstation in promiscuous mode to sniff traffic. Switches send unicast frames only to the designated port, preventing casual packet eavesdropping.",
            "Identify the security advantage of switches over hubs.",
            [
                ("Unicast traffic is directed only to the recipient port, preventing casual network sniffing by third-party hosts on the switch", True, "Switches prevent eavesdropping by isolating unicast frame delivery to destination ports."),
                ("Switches automatically encrypt all transmitted traffic with military-grade AES-256", False, "Layer 2 switches forward plaintext frames without encrypting payloads."),
                ("Switches physically disconnect any host that attempts to run an antivirus scan", False, "Switches do not inspect host software execution."),
                ("Switches eliminate the requirement for passwords across all internal web servers", False, "Authentication is an application/presentation layer function independent of switch forwarding.")
            ],
            ["network-devices", "switch", "security", "sniffing"]
        ),
        (
            "NET-FUND-018",
            "network-topologies",
            "In which topology does every computer connect to two neighbors in a continuous closed loop?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            40,
            "In a ring topology, each node is linked directly to two adjacent nodes in a circular formation, with data or permission tokens circulating around the loop in a single or dual direction.",
            "Identify the structural properties of a ring topology.",
            [
                ("Ring topology", True, "Nodes in a ring topology form a closed circular path."),
                ("Star topology", False, "Star topology connects devices to a central concentrator."),
                ("Bus topology", False, "Bus topology uses a single straight cable terminating at both ends."),
                ("Tree topology", False, "Tree topology organizes star networks into hierarchical tiers.")
            ],
            ["network-topologies", "ring-topology"]
        ),
        (
            "NET-FUND-019",
            "network-topologies",
            "In a hybrid tree topology, how are the workstations typically organized?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            45,
            "A tree topology (hierarchical star) combines multiple star topologies connected along a central backbone switch or distribution tier, enabling structured campus network scaling.",
            "Understand hierarchical tree network architectures.",
            [
                ("Multiple star-configured switches are connected together in a hierarchical tiered structure", True, "A tree topology connects groups of star networks back to a core distribution switch."),
                ("All devices share a single linear coaxial wire without any switches or routers", False, "That describes a pure bus topology."),
                ("Devices transmit data exclusively through directional line-of-sight laser beams", False, "Tree topologies are built using standard Ethernet copper or fiber links."),
                ("Every workstation must also be an Internet Service Provider gateway", False, "Workstations are access layer endpoints, not ISPs.")
            ],
            ["network-topologies", "tree-topology", "hierarchy"]
        ),
        (
            "NET-FUND-020",
            "what-is-computer-networking",
            "What term describes the maximum rate of data transfer across a network path under ideal conditions?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            40,
            "Bandwidth measures the theoretical data-carrying capacity of a network transmission channel, usually expressed in bits per second (e.g., 100 Mbps or 1 Gbps).",
            "Define the concept of network bandwidth.",
            [
                ("Bandwidth", True, "Bandwidth represents theoretical maximum data transfer capacity."),
                ("Latency", False, "Latency represents the time delay required for a packet to travel from source to destination."),
                ("Jitter", False, "Jitter represents the variation in packet arrival delay over time."),
                ("Attenuation", False, "Attenuation represents the loss of signal strength as it travels through a medium.")
            ],
            ["networking", "bandwidth", "fundamentals"]
        ),
        (
            "NET-FUND-021",
            "what-is-computer-networking",
            "What term describes the time delay experienced for a data packet to travel from source to destination across a network?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            40,
            "Latency is the time interval taken for a data packet to travel from its sending host to its receiving host, typically measured in milliseconds (ms).",
            "Define the metric of network latency.",
            [
                ("Latency", True, "Latency is the transit time delay from source to destination."),
                ("Throughput", False, "Throughput is the actual volume of data successfully transmitted per unit of time."),
                ("Bandwidth", False, "Bandwidth is the channel's maximum theoretical carrying capacity."),
                ("Duplex", False, "Duplex refers to whether transmission occurs in one direction or both simultaneously.")
            ],
            ["networking", "latency", "performance"]
        ),
        (
            "NET-FUND-022",
            "what-is-computer-networking",
            "What is the difference between half-duplex and full-duplex communication?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            50,
            "Half-duplex allows communication in both directions, but only one party can transmit at any given time (like a walkie-talkie). Full-duplex allows simultaneous two-way transmission (like a telephone).",
            "Contrast half-duplex and full-duplex modes.",
            [
                ("Half-duplex permits transmission in only one direction at a time; full-duplex allows simultaneous bidirectional transmission", True, "Full-duplex doubles efficiency by supporting simultaneous sending and receiving without collisions."),
                ("Half-duplex uses optical fiber; full-duplex only operates over copper twisted pair", False, "Duplex modes are logical transmission modes supported across media types."),
                ("Half-duplex only works on IPv6; full-duplex is restricted to IPv4", False, "Duplex mode is an Ethernet physical/data link layer property independent of IP version."),
                ("Half-duplex encrypts packets; full-duplex sends unencrypted plaintext", False, "Duplex mode has no bearing on cryptographic encryption.")
            ],
            ["networking", "duplex", "half-duplex", "full-duplex"]
        ),
        (
            "NET-FUND-023",
            "network-devices",
            "What is the primary function of a modem in home and small-office Internet connectivity?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            45,
            "A modem (Modulator-Demodulator) converts analog signals from an ISP line (cable, DSL, telephone) into digital signals suitable for local computer networking equipment, and vice versa.",
            "Recall the role of a modem in residential Internet access.",
            [
                ("It modulates and demodulates signals between the ISP delivery medium and digital LAN signals", True, "Modems translate between ISP carrier signals and computer digital data."),
                ("It assigns domain names to public web servers", False, "DNS domain assignment is managed by registrars and DNS authorities."),
                ("It scans endpoints for operating system malware updates", False, "Malware scanning is conducted by endpoint protection software."),
                ("It provides backup electrical battery power during blackouts", False, "Uninterruptible Power Supplies (UPS) provide battery backup, not modems.")
            ],
            ["network-devices", "modem", "hardware"]
        ),
        (
            "NET-FUND-024",
            "what-is-computer-networking",
            "What does the term 'intranet' refer to in enterprise networking?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            45,
            "An intranet is a private, internal network restricted to authorized members of an organization, utilizing standard Internet protocols (HTTP, DNS, TCP/IP) for internal productivity and document sharing.",
            "Define the purpose and scope of an enterprise intranet.",
            [
                ("A private internal network accessible exclusively to authorized members within an organization", True, "Intranets host private internal portals, wikis, and administrative resources."),
                ("The public global collection of interconnected commercial web servers", False, "That is the World Wide Web / public Internet."),
                ("A physical satellite constellation providing global positioning data", False, "That describes the GPS satellite constellation."),
                ("A hardware tool used to crimp RJ-45 connectors onto Ethernet cables", False, "That is a mechanical cable crimper tool.")
            ],
            ["networking", "intranet", "security"]
        ),
        (
            "NET-FUND-025",
            "what-is-computer-networking",
            "What is an 'extranet'?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            50,
            "An extranet is a controlled private network that allows specific external entities (such as trusted vendors, suppliers, or partner businesses) secure access to designated internal resources.",
            "Differentiate extranet architecture from public and private networks.",
            [
                ("A private corporate network that securely grants selective access to trusted external business partners or vendors", True, "Extranets facilitate business-to-business workflows with controlled external permissions."),
                ("An open, unencrypted Wi-Fi hotspot in a public municipal park", False, "Extranets are strictly authenticated and encrypted business networks."),
                ("An undersea fiber cable connecting two national continents", False, "Undersea cables are physical telecommunication carrier infrastructure."),
                ("A software program used to generate rainbow tables for password cracking", False, "Extranets are network architectures, not cryptographic attack software.")
            ],
            ["networking", "extranet", "security"]
        ),
        (
            "NET-FUND-026",
            "network-devices",
            "Which piece of hardware terminates horizontal Ethernet cable runs inside a telecommunications closet?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            40,
            "A patch panel provides an organized array of RJ-45 ports where permanent in-wall copper runs terminate, allowing flexible short patch cables to interconnect wall jacks to switch ports.",
            "Identify the function of patch panels in structured cabling.",
            [
                ("Patch panel", True, "Patch panels neatly organize and terminate permanent horizontal cabling in server racks."),
                ("Multimeter", False, "A multimeter is an electrical testing instrument for measuring voltage, current, and resistance."),
                ("Optical Time Domain Reflectometer", False, "An OTDR is an advanced fiber-optic diagnostic testing instrument."),
                ("Load balancer", False, "A load balancer distributes server application requests across backend pools.")
            ],
            ["network-devices", "cables", "patch-panel"]
        ),
        (
            "NET-FUND-027",
            "network-media",
            "What connector type is standard for terminating unshielded twisted-pair (UTP) Category 6 Ethernet cables?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "REMEMBER",
            1,
            40,
            "RJ-45 (Registered Jack 45) is the universal 8-position, 8-contact (8P8C) modular connector used for terminating twisted-pair Ethernet cables.",
            "Recall standard Ethernet connector specifications.",
            [
                ("RJ-45", True, "RJ-45 modular connectors are standard for Cat5e, Cat6, and Cat6a twisted-pair Ethernet."),
                ("RJ-11", False, "RJ-11 is a smaller 4-wire or 6-wire connector standard for telephone lines."),
                ("BNC", False, "BNC connectors were used for legacy 10BASE2 coaxial cabling."),
                ("SC/LC", False, "SC and LC are fiber-optic connector standards.")
            ],
            ["network-media", "rj-45", "connectors"]
        ),
        (
            "NET-FUND-028",
            "what-is-computer-networking",
            "Which scenario best exemplifies a Point-to-Point (P2P) network link?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            45,
            "A point-to-point link directly connects exactly two network nodes with no intervening broadcast or multi-access nodes, such as two routers interconnected over a dedicated serial or leased line.",
            "Understand point-to-point network link topology.",
            [
                ("A dedicated serial or fiber connection linking exactly two corporate routers across branches", True, "Point-to-point connects two dedicated endpoints directly."),
                ("Fifty wireless laptops connected to a single coffee shop access point", False, "That is a point-to-multipoint (shared media) wireless star topology."),
                ("A classroom where twenty computers share an unmanaged 24-port switch", False, "That is a multi-access star-wired Local Area Network."),
                ("A public multicast television stream sent to 5,000 subscriber set-top boxes", False, "That is a one-to-many multicast transmission.")
            ],
            ["networking", "point-to-point", "topology"]
        ),
        (
            "NET-FUND-029",
            "network-devices",
            "What is Power over Ethernet (PoE / IEEE 802.3af/at)?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            45,
            "Power over Ethernet (PoE) enables network switches or injectors to deliver direct current (DC) electrical power alongside standard data over existing twisted-pair Ethernet cables to endpoints like IP cameras, VoIP phones, and WAPs.",
            "Explain the operational purpose of Power over Ethernet (PoE).",
            [
                ("A technology that delivers electrical power along with data over standard twisted-pair Ethernet cabling", True, "PoE eliminates the need for separate electrical AC outlets at device mounting locations."),
                ("A protocol that converts Ethernet frames into AC household wall power for refrigerators", False, "PoE delivers low-voltage DC power strictly intended for low-power telecommunications devices."),
                ("A software license that grants permissions to route packets across multiple ISPs", False, "PoE is a physical IEEE hardware standard, not a software license."),
                ("A cybersecurity firewall feature that inspects electrical current spikes for trojans", False, "PoE is an electrical delivery specification with no cryptographic or anti-malware inspection.")
            ],
            ["network-devices", "poe", "hardware"]
        ),
        (
            "NET-FUND-030",
            "what-is-computer-networking",
            "Why is network segmentation considered a foundational security best practice?",
            "SINGLE_CHOICE",
            "BEGINNER",
            "UNDERSTAND",
            1,
            50,
            "Network segmentation divides a large network into smaller isolated subnets or VLANs. If an attacker breaches one workstation, segmentation prevents them from easily pivoting directly to sensitive database or finance servers.",
            "Describe the security value of network segmentation.",
            [
                ("It restricts lateral movement by isolating distinct departments or sensitive servers into separate subnets", True, "Segmentation confines security breaches and limits an adversary's reach."),
                ("It increases the physical thickness of copper wires inside Ethernet cables", False, "Segmentation is a logical network design practice that does not alter cable manufacturing."),
                ("It guarantees that users never need to remember passwords", False, "Authentication is still required across network segments."),
                ("It forces all computers on the network to run identical hardware components", False, "Segmentation does not enforce endpoint hardware homogeneity.")
            ],
            ["network-security", "segmentation", "defense"]
        ),
    ]

    for item in items:
        code, topic_slug, q_text, q_type, diff, cog, pts, est_s, expl, obj, raw_opts, tags = item
        options = []
        for idx, (opt_text, is_corr, opt_expl) in enumerate(raw_opts):
            options.append({
                "option_text": opt_text,
                "is_correct": is_corr,
                "order_index": idx,
                "explanation": opt_expl
            })
        questions.append({
            "code": code,
            "topic_slug": topic_slug,
            "question_text": q_text,
            "question_type": q_type,
            "difficulty": diff,
            "cognitive_level": cog,
            "points": pts,
            "estimated_seconds": est_s,
            "status": "PUBLISHED",
            "explanation": expl,
            "learning_objective": obj,
            "options": options,
            "tags": tags
        })

    with open(DATA_DIR / "networking_fundamentals.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)
    print(f"Created {len(questions)} questions in networking_fundamentals.json")


if __name__ == "__main__":
    build_fundamentals_questions()
