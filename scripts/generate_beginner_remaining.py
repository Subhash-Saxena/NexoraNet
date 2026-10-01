#!/usr/bin/env python3
"""
NexoraNet Beginner Bank Generator - Part 2.
Generates:
- osi_and_tcpip_layers.json (30 questions)
- ipv4_and_mac_addressing.json (30 questions)
- ports_and_protocols.json (35 questions)
- devices_and_basic_security.json (25 questions)
Total: 120 questions.
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "question_bank" / "beginner"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def save_questions(filename, raw_items):
    questions = []
    for item in raw_items:
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
    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)
    print(f"Created {len(questions)} questions in {filename}")


def generate_osi_tcpip():
    items = [
        (
            "OSI-001", "seven-osi-layers", "How many layers are defined in the standard ISO/IEC 7498-1 Open Systems Interconnection (OSI) reference model?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 30,
            "The standard OSI reference model defines exactly seven abstract layers: Physical, Data Link, Network, Transport, Session, Presentation, and Application.",
            "Recall the structure of the OSI 7-layer model.",
            [
                ("7 layers", True, "The OSI model consists of 7 hierarchical layers."),
                ("4 layers", False, "The TCP/IP model has 4 layers, whereas OSI has 7."),
                ("5 layers", False, "The hybrid pedagogical model often uses 5 layers, but OSI strictly defines 7."),
                ("9 layers", False, "No standard networking model defines 9 layers.")
            ],
            ["osi", "seven-osi-layers", "conceptual"]
        ),
        (
            "OSI-002", "seven-osi-layers", "Which OSI layer is directly responsible for converting digital bits into physical signals (electrical voltages, light pulses, or radio waves)?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "Layer 1 (Physical Layer) defines electrical, mechanical, optical, and timing specifications for transmitting raw bit streams over a physical communication medium.",
            "Identify the role of OSI Layer 1.",
            [
                ("Layer 1 — Physical", True, "The Physical layer encodes bits into physical media signals."),
                ("Layer 2 — Data Link", False, "Data Link organizes bits into frames and handles local MAC addressing."),
                ("Layer 3 — Network", False, "Network handles logical IP addressing and path routing."),
                ("Layer 4 — Transport", False, "Transport handles end-to-end process communication and segmentation.")
            ],
            ["osi", "physical-layer", "signals"]
        ),
        (
            "OSI-003", "seven-osi-layers", "What is the Protocol Data Unit (PDU) at the OSI Data Link layer (Layer 2)?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "At Layer 2 (Data Link), the Protocol Data Unit is called a Frame. Frames encapsulate network packets and include header fields like source and destination MAC addresses.",
            "Identify Layer 2 Protocol Data Units.",
            [
                ("Frame", True, "Layer 2 encapsulates packets into frames."),
                ("Packet", False, "Packets are the PDU of Layer 3 (Network)."),
                ("Segment", False, "Segments are the PDU of Layer 4 (Transport)."),
                ("Bit", False, "Bits are the transmission unit of Layer 1 (Physical).")
            ],
            ["osi", "data-link", "pdu", "frames"]
        ),
        (
            "OSI-004", "seven-osi-layers", "What is the Protocol Data Unit (PDU) at the OSI Network layer (Layer 3)?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "At Layer 3 (Network), the Protocol Data Unit is called a Packet (or datagram). It contains source and destination logical IP addresses and routing control information.",
            "Identify Layer 3 Protocol Data Units.",
            [
                ("Packet", True, "Layer 3 PDUs are packets (or datagrams)."),
                ("Frame", False, "Frames are Layer 2 PDUs."),
                ("Segment", False, "Segments are Layer 4 PDUs."),
                ("Bit", False, "Bits are Layer 1 units.")
            ],
            ["osi", "network-layer", "pdu", "packets"]
        ),
        (
            "OSI-005", "seven-osi-layers", "What is the Protocol Data Unit (PDU) at the OSI Transport layer (Layer 4) when using TCP?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "At Layer 4 (Transport), data encapsulated with a TCP header is called a Segment. (When UDP is used, it is commonly called a Datagram).",
            "Identify Layer 4 Protocol Data Units.",
            [
                ("Segment", True, "TCP PDUs at Layer 4 are known as segments."),
                ("Frame", False, "Frames are Layer 2 PDUs."),
                ("Packet", False, "Packets are Layer 3 PDUs."),
                ("Payload", False, "Payload refers to the encapsulated data within a PDU.")
            ],
            ["osi", "transport-layer", "pdu", "tcp"]
        ),
        (
            "OSI-006", "seven-osi-layers", "Which OSI layer provides logical addressing (IP addresses) and path determination across interconnected networks?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "Layer 3 (Network Layer) is responsible for logical addressing (IPv4/IPv6) and routing packets across intermediate routers to their ultimate destination network.",
            "Define the primary role of the OSI Network layer.",
            [
                ("Layer 3 — Network", True, "Layer 3 handles logical IP addressing and routing."),
                ("Layer 2 — Data Link", False, "Layer 2 uses physical MAC addresses within a single local segment."),
                ("Layer 4 — Transport", False, "Layer 4 uses port numbers to multiplex process communication."),
                ("Layer 5 — Session", False, "Layer 5 manages session dialogues between applications.")
            ],
            ["osi", "network-layer", "ip", "routing"]
        ),
        (
            "OSI-007", "seven-osi-layers", "Which OSI layer is responsible for establishing, maintaining, and synchronizing dialogues between two communicating applications?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "Layer 5 (Session Layer) controls dialogues (connections) between computers, establishing, managing, and terminating sessions between local and remote applications.",
            "Recall the function of the Session layer.",
            [
                ("Layer 5 — Session", True, "Session layer coordinates dialogue establishment and checkpointing."),
                ("Layer 2 — Data Link", False, "Data link manages hop-to-hop frame transmission."),
                ("Layer 3 — Network", False, "Network manages end-to-end packet delivery."),
                ("Layer 1 — Physical", False, "Physical layer transmits raw unstructured bit streams.")
            ],
            ["osi", "session-layer", "dialogue"]
        ),
        (
            "OSI-008", "seven-osi-layers", "Which OSI layer handles data formatting, compression, and cryptographic encryption/decryption (such as ASCII, JPEG, and TLS presentations)?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "Layer 6 (Presentation Layer) ensures that data passed from the application layer is formatted, translated, compressed, or encrypted into a standardized syntax the receiver can interpret.",
            "Recall the responsibilities of the Presentation layer.",
            [
                ("Layer 6 — Presentation", True, "Presentation layer handles data representation, encryption, and compression."),
                ("Layer 4 — Transport", False, "Transport handles end-to-end transport and flow control."),
                ("Layer 3 — Network", False, "Network handles packet forwarding and addressing."),
                ("Layer 2 — Data Link", False, "Data Link handles frame delimiters and MAC media access.")
            ],
            ["osi", "presentation-layer", "encryption", "formatting"]
        ),
        (
            "OSI-009", "seven-osi-layers", "Which OSI layer interfaces directly with end-user software applications (such as web browsers and email clients)?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "Layer 7 (Application Layer) provides network services directly to software applications, hosting protocols like HTTP, DNS, SMTP, and SSH.",
            "Identify the role of the Application layer.",
            [
                ("Layer 7 — Application", True, "Application layer protocols interact directly with software processes."),
                ("Layer 1 — Physical", False, "Physical layer deals with hardware cables and electrical signals."),
                ("Layer 4 — Transport", False, "Transport layer delivers data to port sockets, not directly to UI applications."),
                ("Layer 2 — Data Link", False, "Data link layer interacts with network interface hardware.")
            ],
            ["osi", "application-layer", "protocols"]
        ),
        (
            "OSI-010", "encapsulation", "What happens during the network encapsulation process as data travels DOWN the protocol stack from the sender?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "As data travels down the stack, each lower layer adds its own protocol header (and sometimes trailer, like Layer 2 FCS) containing control information needed by that layer.",
            "Explain the encapsulation mechanism.",
            [
                ("Each layer prepends its own header containing metadata to the payload passed from the layer above", True, "Encapsulation wraps higher-layer data with lower-layer headers."),
                ("Each layer strips away headers to make the packet as small as possible before transmission", False, "Stripping headers is decapsulation, which occurs on the receiver."),
                ("The application data is permanently erased and replaced with random hex characters", False, "Encapsulation preserves payload data intact inside headers."),
                ("All IP addresses are permanently converted into website domain names", False, "Encapsulation adds protocol headers; it does not replace addresses with domain names.")
            ],
            ["encapsulation", "protocol-stack", "osi"]
        ),
        (
            "OSI-011", "decapsulation", "What happens during the decapsulation process when a destination computer receives an incoming Ethernet frame?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "Decapsulation occurs on the receiver: each layer unpacks the PDU, verifies the header for errors and addressing, strips that header off, and passes the remaining payload UP to the next higher layer.",
            "Describe the decapsulation workflow on receiving endpoints.",
            [
                ("Each layer inspects and removes its corresponding header, passing the unpackaged payload up to the layer above", True, "Decapsulation unwraps headers progressively as data moves up to Layer 7."),
                ("The receiver adds three extra layers of encryption before saving the file to disk", False, "Decapsulation removes transport and framing headers; it does not add encryption layers."),
                ("The frame is immediately broadcast out to every other host on the Internet", False, "Unicast decapsulation is processed locally by the intended recipient host."),
                ("The receiver converts all IP addresses into MAC addresses", False, "Decapsulation reads existing MAC and IP headers without altering them.")
            ],
            ["decapsulation", "protocol-stack", "osi"]
        ),
        (
            "OSI-012", "tcp-ip-layers", "How many layers are in the original DARPA / DoD TCP/IP architectural model (RFC 1122)?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "The standard TCP/IP model defines four layers: Network Access (Link), Internet, Transport (Host-to-Host), and Application.",
            "State the number of layers in the TCP/IP model.",
            [
                ("4 layers", True, "The TCP/IP model defines 4 layers: Link/Network Access, Internet, Transport, and Application."),
                ("7 layers", False, "7 layers corresponds to the OSI reference model."),
                ("3 layers", False, "TCP/IP has 4 layers."),
                ("6 layers", False, "6 layers does not correspond to standard networking models.")
            ],
            ["tcp-ip-layers", "tcp-ip", "conceptual"]
        ),
        (
            "OSI-013", "tcp-ip-layers", "Which TCP/IP model layer corresponds to OSI Layer 3 (Network Layer)?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "The Internet Layer of the TCP/IP model corresponds directly to Layer 3 (Network Layer) of the OSI model, hosting IP (IPv4/IPv6), ICMP, and ARP.",
            "Map TCP/IP layers to OSI equivalents.",
            [
                ("Internet Layer", True, "The TCP/IP Internet Layer performs the same role as OSI Layer 3 Network."),
                ("Network Access Layer", False, "Network Access corresponds to OSI Layers 1 and 2."),
                ("Transport Layer", False, "Transport corresponds to OSI Layer 4."),
                ("Application Layer", False, "Application corresponds to OSI Layers 5, 6, and 7.")
            ],
            ["tcp-ip-layers", "osi-vs-tcp-ip", "mapping"]
        ),
        (
            "OSI-014", "tcp-ip-layers", "Which OSI model layers are consolidated into the single 'Application' layer within the 4-layer TCP/IP model?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "The TCP/IP Application layer encompasses the functionality of OSI Layers 5 (Session), 6 (Presentation), and 7 (Application).",
            "Explain layer consolidation between OSI and TCP/IP.",
            [
                ("Session, Presentation, and Application layers", True, "TCP/IP consolidates OSI Layers 5, 6, and 7 into its Application layer."),
                ("Physical and Data Link layers", False, "Physical and Data Link are combined into the Network Access layer."),
                ("Network and Transport layers", False, "Internet and Transport are separate layers in TCP/IP."),
                ("Data Link, Network, and Transport layers", False, "These represent separate functionalities across both models.")
            ],
            ["tcp-ip-layers", "osi-vs-tcp-ip", "architecture"]
        ),
        (
            "OSI-015", "osi-troubleshooting", "A technician troubleshoots network connectivity using the 'bottom-up' approach. Which component should be checked first?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 50,
            "Bottom-up troubleshooting begins at Layer 1 (Physical). The technician first checks physical cables, link indicator lights, power supplies, and transceiver connections before moving to higher layers.",
            "Apply bottom-up troubleshooting methodology.",
            [
                ("Physical cables, port link lights, and cable integrity", True, "Bottom-up starts at Layer 1 Physical before checking IP addresses or applications."),
                ("The web browser cache and cookie settings", False, "Checking web browser cache is a top-down application layer check."),
                ("DNS A records on the corporate authoritative nameserver", False, "DNS checking is a higher-layer (Layer 7) troubleshooting step."),
                ("The user's Active Directory group policy permissions", False, "User permissions represent an application/administrative layer issue.")
            ],
            ["osi-troubleshooting", "bottom-up", "troubleshooting"]
        ),
        (
            "OSI-016", "osi-troubleshooting", "A technician uses a 'top-down' troubleshooting approach for a user reporting that an internal website will not load. What should be verified first?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 50,
            "Top-down troubleshooting starts at Layer 7 (Application). The technician checks application-level configurations first (URL accuracy, web browser, application service status) before checking physical cables.",
            "Apply top-down troubleshooting methodology.",
            [
                ("The application configuration, URL spelling, and browser settings", True, "Top-down starts at Layer 7 Application."),
                ("Whether the copper patch cable is seated properly in the wall jack", False, "Checking the patch cable is a bottom-up Layer 1 check."),
                ("The electrical voltage running through the building conduit", False, "That is an electrician's physical infrastructure test."),
                ("The router's BGP routing table entries", False, "Checking BGP routing tables is an intermediate Layer 3 check.")
            ],
            ["osi-troubleshooting", "top-down", "troubleshooting"]
        ),
        (
            "OSI-017", "seven-osi-layers", "At which OSI layer do port numbers (such as TCP port 80 or UDP port 53) function?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "Port numbers are Layer 4 (Transport Layer) identifiers used by TCP and UDP to direct communication streams to the correct application process on a host.",
            "Identify the layer where port numbers operate.",
            [
                ("Layer 4 — Transport", True, "Port numbers reside in TCP and UDP headers at the Transport layer."),
                ("Layer 2 — Data Link", False, "Data link uses MAC addresses."),
                ("Layer 3 — Network", False, "Network layer uses IP addresses."),
                ("Layer 1 — Physical", False, "Physical layer operates on bits and signals.")
            ],
            ["osi", "transport-layer", "ports"]
        ),
        (
            "OSI-018", "seven-osi-layers", "Which OSI layer uses MAC (Media Access Control) addresses to direct traffic within a local broadcast domain?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "MAC addresses are hardware-burned Layer 2 (Data Link Layer) addresses used by network interface cards (NICs) and switches to deliver frames across a local link.",
            "Identify the layer of MAC addresses.",
            [
                ("Layer 2 — Data Link", True, "MAC addresses operate strictly at Layer 2 Data Link."),
                ("Layer 3 — Network", False, "Layer 3 uses IP addresses."),
                ("Layer 4 — Transport", False, "Layer 4 uses port numbers."),
                ("Layer 7 — Application", False, "Layer 7 uses domain names and URLs.")
            ],
            ["osi", "data-link", "mac-address"]
        ),
        (
            "OSI-019", "osi-troubleshooting", "In OSI-based troubleshooting, what does the 'divide-and-conquer' approach involve?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 50,
            "Divide-and-conquer starts troubleshooting at the middle layer (usually Layer 3 Network by running a ping test). If ping succeeds, Layers 1-3 are verified, and the problem must be at Layers 4-7.",
            "Explain the divide-and-conquer troubleshooting strategy.",
            [
                ("Starting investigation at Layer 3 (e.g. testing with ping) to immediately isolate whether the issue is at lower layers (1-2) or upper layers (4-7)", True, "Testing Layer 3 with ping effectively splits the 7 layers in half, saving diagnostic time."),
                ("Splitting the physical Ethernet cable in half with wire cutters to check copper purity", False, "Severing cables destroys physical connectivity."),
                ("Assigning two technicians to yell at each other across the datacenter", False, "This is not an engineering methodology."),
                ("Reinstalling the operating system before testing any network cables", False, "Reinstalling OS is a drastic measure that should never precede basic diagnostics.")
            ],
            ["osi-troubleshooting", "divide-and-conquer", "ping"]
        ),
        (
            "OSI-020", "seven-osi-layers", "Which layer of the OSI model is responsible for flow control, windowing, and error recovery in reliable data delivery?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "Layer 4 (Transport Layer), through protocols like TCP, provides end-to-end flow control (sliding windows), sequence numbers, acknowledgements, and retransmissions of dropped segments.",
            "Identify Transport layer reliability mechanisms.",
            [
                ("Layer 4 — Transport", True, "Transport layer manages flow control, sequence tracking, and error recovery."),
                ("Layer 1 — Physical", False, "Physical layer cannot detect or recover from dropped packets."),
                ("Layer 3 — Network", False, "IPv4 and IPv6 are best-effort protocols without built-in reliability recovery."),
                ("Layer 6 — Presentation", False, "Presentation formats and translates syntax.")
            ],
            ["osi", "transport-layer", "flow-control", "reliability"]
        ),
        (
            "OSI-021", "seven-osi-layers", "What is the primary function of the Frame Check Sequence (FCS) located in an Ethernet frame trailer at Layer 2?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "The Frame Check Sequence (FCS) uses a Cyclic Redundancy Check (CRC-32) algorithm to detect whether any bits in the frame were corrupted during physical transmission over the wire.",
            "Explain the purpose of the Frame Check Sequence.",
            [
                ("To detect bit-level data corruption that occurred during physical transmission", True, "FCS checks for transmission corruption; corrupted frames are discarded."),
                ("To encrypt the payload using a symmetric cryptographic key", False, "FCS is an error-detecting checksum, not an encryption cipher."),
                ("To inform Google Analytics of the user's geographical location", False, "Ethernet trailers have no connection to web marketing analytics."),
                ("To accelerate the electrical signal to twice the speed of light", False, "Electrical signals cannot exceed the speed of light in the transmission medium.")
            ],
            ["osi", "data-link", "fcs", "error-detection"]
        ),
        (
            "OSI-022", "tcp-ip-layers", "Which protocol functions at the Internet layer of the TCP/IP model?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "Internet Protocol (IP), along with ICMP and ARP, operates at the Internet layer of the TCP/IP model, handling logical addressing and routing.",
            "Identify Internet layer protocols.",
            [
                ("Internet Protocol (IP)", True, "IP is the cornerstone protocol of the TCP/IP Internet layer."),
                ("Transmission Control Protocol (TCP)", False, "TCP operates at the Transport layer."),
                ("Simple Mail Transfer Protocol (SMTP)", False, "SMTP operates at the Application layer."),
                ("Ethernet", False, "Ethernet operates at the Link / Network Access layer.")
            ],
            ["tcp-ip-layers", "internet-layer", "ip"]
        ),
        (
            "OSI-023", "tcp-ip-layers", "Which protocol operates at the Transport layer of the TCP/IP model?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "Both Transmission Control Protocol (TCP) and User Datagram Protocol (UDP) operate at the Transport layer of the TCP/IP model.",
            "Identify Transport layer protocols.",
            [
                ("User Datagram Protocol (UDP)", True, "UDP is a core Transport layer protocol."),
                ("Hypertext Transfer Protocol (HTTP)", False, "HTTP operates at the Application layer."),
                ("Address Resolution Protocol (ARP)", False, "ARP operates at the Link/Internet boundary."),
                ("Internet Protocol version 6 (IPv6)", False, "IPv6 operates at the Internet layer.")
            ],
            ["tcp-ip-layers", "transport-layer", "udp"]
        ),
        (
            "OSI-024", "seven-osi-layers", "What term describes the chunk of data generated by an application (Layer 7) before any network encapsulation occurs?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "At the upper application layers (Layers 7, 6, 5), data is simply referred to as 'Data' or Application Data (Payload) prior to Transport layer segmentation.",
            "Identify upper-layer data terminology.",
            [
                ("Data / Payload", True, "At Layers 5-7, data is referred to generally as Data or Payload."),
                ("Frame", False, "Frame is Layer 2 PDU."),
                ("Packet", False, "Packet is Layer 3 PDU."),
                ("Bit", False, "Bit is Layer 1 transmission unit.")
            ],
            ["osi", "application-layer", "payload"]
        ),
        (
            "OSI-025", "seven-osi-layers", "Why does an Ethernet frame require both a header and a trailer, whereas IP packets only have a header?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 50,
            "Layer 2 frames require a trailer containing the Frame Check Sequence (FCS) so that receiving hardware can compute the CRC checksum over the entire frame contents as bits arrive.",
            "Understand why Layer 2 incorporates a trailer.",
            [
                ("The trailer contains the FCS checksum computed over the frame, allowing the receiver to verify data integrity upon receipt", True, "Layer 2 puts the FCS in a trailer so it can be calculated on-the-fly during transmission."),
                ("The trailer contains the user's personal credit card information", False, "Networking trailers contain protocol integrity metadata, never payment credentials."),
                ("IP packets are forbidden by RFC standards from detecting errors", False, "IPv4 includes a header checksum, but Layer 2 validates the entire physical frame."),
                ("Ethernet cables can only carry data backwards", False, "Ethernet transmission is sequential from preamble to trailer.")
            ],
            ["osi", "data-link", "fcs", "trailer"]
        ),
        (
            "OSI-026", "seven-osi-layers", "Which layer in the OSI model is responsible for assigning source and destination IP addresses?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "The Network layer (Layer 3) adds source and destination logical IP addresses in its header during packet encapsulation.",
            "Identify the layer responsible for IP addressing.",
            [
                ("Layer 3 — Network", True, "Source and destination IP addresses are added at Layer 3."),
                ("Layer 2 — Data Link", False, "Data link adds MAC addresses."),
                ("Layer 4 — Transport", False, "Transport adds port numbers."),
                ("Layer 5 — Session", False, "Session does not handle IP addressing.")
            ],
            ["osi", "network-layer", "ip-addresses"]
        ),
        (
            "OSI-027", "seven-osi-layers", "Which OSI layer determines whether communication should be connection-oriented (reliable) or connectionless (unreliable)?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "The Transport layer (Layer 4) selects between connection-oriented transport (TCP) or connectionless transport (UDP) depending on application requirements.",
            "Understand Transport layer service modes.",
            [
                ("Layer 4 — Transport", True, "Transport layer protocols determine connection-oriented vs connectionless modes."),
                ("Layer 1 — Physical", False, "Physical layer only transmits electrical/optical bits without connection awareness."),
                ("Layer 2 — Data Link", False, "Data link deals with local media framing."),
                ("Layer 6 — Presentation", False, "Presentation deals with data translation.")
            ],
            ["osi", "transport-layer", "connection-oriented", "tcp-udp"]
        ),
        (
            "OSI-028", "osi-vs-tcp-ip", "What is one key philosophical difference between the OSI reference model and the TCP/IP model?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 50,
            "The OSI model was designed as a theoretical, protocol-independent reference architecture before protocols were created. TCP/IP was developed practically around working protocols implemented in ARPANET/Unix.",
            "Compare OSI and TCP/IP historical design philosophies.",
            [
                ("OSI was designed as a theoretical reference model, whereas TCP/IP was built around working, implemented protocols", True, "TCP/IP is pragmatic and protocol-specific; OSI is a formal conceptual framework."),
                ("OSI was designed for wireless smartphones; TCP/IP was designed for analog landline telephones", False, "Both models predate modern smartphones by decades."),
                ("TCP/IP requires exactly seven layers; OSI has only four", False, "TCP/IP has 4 layers; OSI has 7 layers."),
                ("OSI completely bans the use of routers and switches", False, "OSI explicitly incorporates routing at Layer 3 and switching at Layer 2.")
            ],
            ["osi-vs-tcp-ip", "history", "architecture"]
        ),
        (
            "OSI-029", "seven-osi-layers", "At which layer of the OSI model does an unmanaged Layer 1 repeater or electrical amplifier operate?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "A repeater operates at Layer 1 (Physical). It regenerates and amplifies electrical or optical signals to overcome attenuation without reading frame headers or IP addresses.",
            "Identify the operational layer of repeaters.",
            [
                ("Layer 1 — Physical", True, "Repeaters regenerate raw physical signals at Layer 1."),
                ("Layer 2 — Data Link", False, "Layer 2 devices (bridges/switches) inspect MAC frames."),
                ("Layer 3 — Network", False, "Layer 3 devices (routers) inspect IP packets."),
                ("Layer 4 — Transport", False, "Layer 4 devices (firewalls) inspect transport ports.")
            ],
            ["osi", "physical-layer", "repeater"]
        ),
        (
            "OSI-030", "encapsulation", "When viewing an Ethernet frame captured on a wire, in what order do headers appear from outermost to innermost?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 55,
            "During transmission, lower-layer headers enclose higher-layer headers: Ethernet Header (Layer 2) comes first, followed by IP Header (Layer 3), then TCP/UDP Header (Layer 4), and finally the Application Data (Layer 7).",
            "Trace header order in encapsulated frames.",
            [
                ("Ethernet Header -> IP Header -> TCP Header -> Application Data", True, "Outer encapsulation layer comes first on the wire: Layer 2 -> Layer 3 -> Layer 4 -> Payload."),
                ("Application Data -> TCP Header -> IP Header -> Ethernet Header", False, "This is reverse order; the frame header arrives first on the wire."),
                ("IP Header -> Ethernet Header -> Application Data -> TCP Header", False, "Ethernet header wraps the IP packet, so Ethernet header comes first."),
                ("TCP Header -> IP Header -> Ethernet Header -> Application Data", False, "TCP is encapsulated inside IP, which is encapsulated inside Ethernet.")
            ],
            ["encapsulation", "headers", "packet-structure"]
        ),
    ]
    save_questions("osi_and_tcpip_layers.json", items)


def generate_ipv4_mac():
    items = [
        (
            "IPV4-001", "ipv4-basics", "How many bits are in an IPv4 address?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 30,
            "An IPv4 address consists of exactly 32 bits, divided into four 8-bit sections called octets.",
            "Recall IPv4 address bit length.",
            [
                ("32 bits", True, "IPv4 addresses are 32 bits (4 bytes) in length."),
                ("64 bits", False, "64 bits is the size of standard computer memory registers, not IPv4."),
                ("128 bits", False, "128 bits is the bit length of an IPv6 address."),
                ("48 bits", False, "48 bits is the length of an Ethernet MAC address.")
            ],
            ["ipv4", "ipv4-basics", "fundamentals"]
        ),
        (
            "IPV4-002", "ipv4-basics", "How many octets are in an IPv4 address when written in standard dotted-decimal notation?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 30,
            "An IPv4 address is formatted as four decimal numbers separated by dots (e.g., 192.168.1.1), where each decimal number represents one 8-bit octet (byte).",
            "Identify the number of octets in IPv4.",
            [
                ("4 octets", True, "IPv4 has 4 octets (8 bits * 4 = 32 bits)."),
                ("6 octets", False, "6 octets (48 bits) is the structure of a MAC address."),
                ("8 octets", False, "IPv6 has 8 groups of hexadecimal digits."),
                ("2 octets", False, "2 octets is only 16 bits.")
            ],
            ["ipv4", "ipv4-address-structure", "octets"]
        ),
        (
            "IPV4-003", "ipv4-address-structure", "What is the maximum decimal value that can be represented in a single 8-bit IPv4 octet?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "An 8-bit binary number can represent $2^8 = 256$ possible values, ranging from decimal 0 (00000000) to 255 (11111111).",
            "Calculate maximum octet value in IPv4.",
            [
                ("255", True, "255 is the maximum 8-bit value (11111111 in binary)."),
                ("256", False, "256 requires 9 bits (100000000 in binary)."),
                ("128", False, "128 is the value of the most significant bit (2^7)."),
                ("512", False, "512 requires 10 bits.")
            ],
            ["ipv4", "ipv4-address-structure", "binary"]
        ),
        (
            "IPV4-004", "ipv4-basics", "Which of the following is an INVALID IPv4 address?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 40,
            "192.168.1.256 is invalid because octet values in IPv4 cannot exceed decimal 255 (8 bits).",
            "Recognize valid IPv4 decimal syntax.",
            [
                ("192.168.1.256", True, "256 exceeds the maximum possible 8-bit octet value of 255."),
                ("10.0.0.1", False, "10.0.0.1 is a perfectly valid Class A private IPv4 address."),
                ("172.16.254.1", False, "172.16.254.1 is a valid Class B private IPv4 address."),
                ("8.8.8.8", False, "8.8.8.8 is a valid public IPv4 address (Google DNS).")
            ],
            ["ipv4", "ipv4-basics", "validation"]
        ),
        (
            "IPV4-005", "public-vs-private-ip", "According to RFC 1918, which of the following is a designated Private IPv4 address range?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 45,
            "RFC 1918 reserves three private address spaces: 10.0.0.0/8, 172.16.0.0/12, and 192.168.0.0/16. 10.0.0.0 to 10.255.255.255 is the Class A private block.",
            "Recall RFC 1918 private IPv4 address blocks.",
            [
                ("10.0.0.0 to 10.255.255.255 (10.0.0.0/8)", True, "10.0.0.0/8 is reserved for private intranets under RFC 1918."),
                ("11.0.0.0 to 11.255.255.255", False, "11.0.0.0/8 is public routable address space."),
                ("172.32.0.0 to 172.63.255.255", False, "RFC 1918 only covers 172.16.0.0 to 172.31.255.255."),
                ("192.169.0.0 to 192.169.255.255", False, "RFC 1918 covers 192.168.0.0/16, not 192.169.0.0/16.")
            ],
            ["public-vs-private-ip", "rfc1918", "private-ip"]
        ),
        (
            "IPV4-006", "public-vs-private-ip", "Why are RFC 1918 private IP addresses non-routable on the public Internet?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "Internet Service Provider (ISP) core routers drop packets addressed to RFC 1918 private IP addresses. They are intended for internal LANs and must be translated using NAT to reach public hosts.",
            "Explain the non-routable nature of RFC 1918 addresses.",
            [
                ("Public Internet routers drop private IP addresses by convention; NAT is required to communicate with public hosts", True, "Private IPs are reused across millions of homes/businesses and cannot be routed globally."),
                ("Private IP packets carry a self-destruct software virus that crashes routers", False, "Private addresses are a standard addressing convention, not malicious payloads."),
                ("Private IPs cannot be processed by computers running modern operating systems", False, "All modern OS stacks fully support private IP configurations."),
                ("Private IPs require optical quantum modems to transmit signals", False, "Private IPs transmit over standard Ethernet and Wi-Fi.")
            ],
            ["public-vs-private-ip", "nat", "routing"]
        ),
        (
            "IPV4-007", "ipv4-basics", "Which IPv4 address is universally reserved for the host loopback interface (localhost)?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "The entire 127.0.0.0/8 block is reserved for loopback testing, with 127.0.0.1 being the standard address that points directly back to the local computer's TCP/IP stack.",
            "Identify the IPv4 loopback address.",
            [
                ("127.0.0.1", True, "127.0.0.1 is the standard loopback address pointing to the local host."),
                ("192.168.1.1", False, "192.168.1.1 is typically a default gateway router address on home LANs."),
                ("255.255.255.255", False, "255.255.255.255 is the IPv4 limited broadcast address."),
                ("0.0.0.0", False, "0.0.0.0 represents an unknown or default route address.")
            ],
            ["ipv4", "loopback", "localhost"]
        ),
        (
            "IPV4-008", "mac-address", "How many bits are in a standard Ethernet MAC (Media Access Control) address?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "A standard Ethernet MAC address is 48 bits (6 bytes) long, typically formatted as six pairs of hexadecimal digits (e.g., 00:1A:2B:3C:4D:5E).",
            "Recall MAC address bit length.",
            [
                ("48 bits", True, "Ethernet MAC addresses are 48 bits (6 octets)."),
                ("32 bits", False, "32 bits is the length of an IPv4 address."),
                ("64 bits", False, "64 bits is EUI-64 format."),
                ("128 bits", False, "128 bits is the length of an IPv6 address.")
            ],
            ["mac-address", "ethernet", "data-link"]
        ),
        (
            "IPV4-009", "mac-address", "What do the first 24 bits (3 bytes) of an Ethernet MAC address represent?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "The first 24 bits of a MAC address are the Organizationally Unique Identifier (OUI), assigned by the IEEE to identify the network hardware manufacturer (e.g., Cisco, Intel, Apple).",
            "Identify the OUI portion of a MAC address.",
            [
                ("Organizationally Unique Identifier (OUI) identifying the hardware manufacturer", True, "The OUI identifies the vendor who manufactured the network interface card."),
                ("The user's secret cryptographic encryption key", False, "MAC addresses are public Layer 2 hardware identifiers with no secret keys."),
                ("The geographical GPS coordinates of the computer", False, "MAC addresses do not record real-time GPS locations."),
                ("The ISP account billing identification number", False, "MAC addresses are assigned at hardware manufacturing, independent of ISPs.")
            ],
            ["mac-address", "oui", "hardware"]
        ),
        (
            "IPV4-010", "mac-address", "Which of the following represents the universal Ethernet broadcast MAC address?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "FF:FF:FF:FF:FF:FF (all 48 bits set to 1) is the universal Layer 2 broadcast address. Every NIC on the local LAN processes frames addressed to this destination.",
            "Recall the universal Layer 2 broadcast MAC address.",
            [
                ("FF:FF:FF:FF:FF:FF", True, "All 48 bits set to binary 1 represents the Layer 2 broadcast address."),
                ("00:00:00:00:00:00", False, "00:00:00:00:00:00 is an unassigned or invalid source address."),
                ("127.0.0.1", False, "127.0.0.1 is an IPv4 Layer 3 loopback address, not a MAC address."),
                ("FF:00:00:00:00:00", False, "This is not a standard broadcast address.")
            ],
            ["mac-address", "broadcast", "layer2"]
        ),
        (
            "IPV4-011", "default-gateway", "What is the primary role of a 'Default Gateway' configured on a host workstation?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "The default gateway is the local router interface IP address that a host sends packets to whenever the destination IP address lies outside its local subnet.",
            "Explain the purpose of a default gateway.",
            [
                ("The router IP address a host forwards packets to when communicating with destinations outside the local subnet", True, "Hosts forward all off-subnet traffic to their default gateway router."),
                ("The web browser homepage URL displayed when opening Google Chrome", False, "The default gateway is a Layer 3 routing parameter, not a web browser URL."),
                ("The physical power outlet in the server rack", False, "The default gateway is a logical IP address on a router."),
                ("A database password required to authenticate to local switches", False, "Default gateway is for packet forwarding, not database authentication.")
            ],
            ["default-gateway", "routing", "host-configuration"]
        ),
        (
            "IPV4-012", "ipv4-address-structure", "An IPv4 address is divided into two logical portions. What are they?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "Every IPv4 address consists of a Network portion (identifying the specific subnet) and a Host portion (identifying the specific device on that subnet), determined by the subnet mask.",
            "Differentiate network and host portions of an IP address.",
            [
                ("Network portion and Host portion", True, "The subnet mask separates the address into network bits and host bits."),
                ("Username portion and Password portion", False, "IP addresses identify interfaces, not user credentials."),
                ("MAC portion and Port portion", False, "MAC is Layer 2 and Port is Layer 4; they are not parts of an IPv4 address."),
                ("Encryption portion and Decryption portion", False, "IP addresses are not divided into cryptographic components.")
            ],
            ["ipv4", "ipv4-address-structure", "subnet-mask"]
        ),
        (
            "IPV4-013", "public-vs-private-ip", "Which of the following addresses falls within the RFC 1918 Class B private address block?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 45,
            "The Class B private address range spans from 172.16.0.0 through 172.31.255.255 (a /12 prefix). 172.20.10.5 falls squarely within this range.",
            "Identify Class B private IP addresses.",
            [
                ("172.20.10.5", True, "172.20.10.5 falls within 172.16.0.0 - 172.31.255.255."),
                ("172.15.1.1", False, "172.15.1.1 is lower than 172.16.0.0 and is a public IP address."),
                ("172.32.1.1", False, "172.32.1.1 is higher than 172.31.255.255 and is a public IP address."),
                ("192.168.1.1", False, "192.168.1.1 is a Class C private address, not Class B.")
            ],
            ["public-vs-private-ip", "class-b", "rfc1918"]
        ),
        (
            "IPV4-014", "public-vs-private-ip", "What address range is designated for Automatic Private IP Addressing (APIPA / Link-Local) in IPv4 when a DHCP server fails to respond?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 45,
            "When a Windows or macOS client configured for DHCP fails to contact a DHCP server, it self-assigns an APIPA link-local address in the 169.254.0.0/16 range (RFC 3927).",
            "Identify the IPv4 APIPA address range.",
            [
                ("169.254.0.1 to 169.254.255.254 (169.254.0.0/16)", True, "169.254.0.0/16 is the designated link-local APIPA block."),
                ("192.168.0.0 to 192.168.255.255", False, "192.168.0.0/16 is standard private space assigned by DHCP routers."),
                ("127.0.0.0 to 127.255.255.255", False, "127.0.0.0/8 is reserved for loopback."),
                ("10.0.0.0 to 10.255.255.255", False, "10.0.0.0/8 is Class A private space.")
            ],
            ["apipa", "dhcp", "troubleshooting", "link-local"]
        ),
        (
            "IPV4-015", "default-gateway", "A student types 'ipconfig' and observes their IPv4 address is 169.254.45.12. What does this indicate?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 50,
            "An address starting with 169.254.x.x is an APIPA address, indicating that the client's network interface is active but was unable to obtain an IP lease from a local DHCP server.",
            "Diagnose APIPA symptom during network troubleshooting.",
            [
                ("The client was unable to contact a DHCP server to obtain an IP address and self-assigned an APIPA address", True, "169.254.x.x indicates DHCP failure."),
                ("The computer has been infected with ransomware that modified its IP address", False, "APIPA is a standard operating system feature, not malware."),
                ("The computer is connected directly to the root DNS server of the Internet", False, "APIPA addresses cannot route to the Internet."),
                ("The network card is defective and must be physically discarded", False, "DHCP failure is typically caused by cabling, VLAN, or DHCP server outages, not hardware death.")
            ],
            ["apipa", "dhcp", "ipconfig", "troubleshooting"]
        ),
        (
            "IPV4-016", "mac-address", "Why is a MAC address often referred to as a 'physical' or 'burned-in' address (BIA)?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "Traditionally, the manufacturer burns the MAC address permanently into the Read-Only Memory (ROM) of the Network Interface Card (NIC) during hardware fabrication.",
            "Explain the origin of the term 'burned-in address'.",
            [
                ("It is permanently encoded into the hardware ROM of the network interface card during manufacturing", True, "MAC addresses are hardcoded into NIC firmware at production."),
                ("It requires extreme heat from a blowtorch to configure on a motherboard", False, "Burned-in is a metaphor for ROM chip flashing, not thermal burning."),
                ("It dissolves automatically after 30 days of continuous operation", False, "Hardware MAC addresses remain permanent."),
                ("It is only used when server rooms exceed 100 degrees Celsius", False, "MAC addresses function in all standard operating conditions.")
            ],
            ["mac-address", "hardware", "nic"]
        ),
        (
            "IPV4-017", "ipv4-address-structure", "In an IPv4 address with a /24 subnet mask (255.255.255.0), how many bits are allocated to the network portion?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "The '/24' prefix notation indicates that the first 24 bits are mask bits allocated to identify the network, leaving the remaining 8 bits ($32 - 24 = 8$) for host addressing.",
            "Interpret prefix length notation in IPv4.",
            [
                ("24 bits", True, "A /24 mask means the first 24 bits identify the network."),
                ("8 bits", False, "8 bits is the host portion (32 - 24 = 8)."),
                ("16 bits", False, "16 bits corresponds to a /16 subnet mask."),
                ("32 bits", False, "32 bits corresponds to a /32 host route.")
            ],
            ["ipv4", "cidr", "subnet-mask"]
        ),
        (
            "IPV4-018", "public-vs-private-ip", "Which address is an example of a public, globally routable IPv4 address?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 40,
            "93.184.216.34 (the public IP for example.com) is outside all RFC 1918 private ranges, loopback (127.0.0.0/8), and APIPA (169.254.0.0/16), making it globally routable.",
            "Distinguish public routable IP addresses from reserved blocks.",
            [
                ("93.184.216.34", True, "93.184.216.34 is a globally routable public IPv4 address."),
                ("10.50.1.1", False, "10.50.1.1 is within RFC 1918 Class A private space."),
                ("192.168.100.1", False, "192.168.100.1 is within RFC 1918 Class C private space."),
                ("172.16.1.1", False, "172.16.1.1 is within RFC 1918 Class B private space.")
            ],
            ["public-vs-private-ip", "public-ip", "routing"]
        ),
        (
            "IPV4-019", "mac-address", "Which command on a Windows workstation displays the MAC address of the network interface card?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "'getmac' or 'ipconfig /all' on Windows displays the physical (MAC) address of each active network adapter.",
            "Recall commands to inspect MAC addresses on Windows.",
            [
                ("getmac (or ipconfig /all)", True, "'getmac' and 'ipconfig /all' output physical MAC addresses on Windows."),
                ("ping localhost", False, "'ping localhost' tests IP stack functionality without displaying MAC addresses."),
                ("tracert 8.8.8.8", False, "'tracert' displays intermediate Layer 3 router hops."),
                ("nslookup google.com", False, "'nslookup' queries DNS servers for IP records.")
            ],
            ["mac-address", "windows", "cli", "ipconfig"]
        ),
        (
            "IPV4-020", "mac-address", "Can a network packet cross multiple routers across the Internet while keeping its original source MAC address intact?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 50,
            "No. MAC addresses are strictly Layer 2 local hop-to-hop identifiers. Every router along the path strips the incoming Layer 2 frame and creates a brand-new Layer 2 frame with its own outgoing MAC address for the next hop.",
            "Understand hop-by-hop MAC address rewriting by routers.",
            [
                ("No, routers rewrite the source and destination MAC addresses at every single hop along the path", True, "MAC addresses change at every router hop; only source/destination IP addresses remain end-to-end."),
                ("Yes, MAC addresses remain unchanged from source host to ultimate destination server", False, "Frames are local to each link and do not traverse routers unchanged."),
                ("Yes, but only if the packet is transmitted on Tuesdays", False, "MAC address behavior is governed by networking protocol standards, not days of the week."),
                ("No, because MAC addresses are deleted by DNS servers", False, "DNS resolves names to IPs and has nothing to do with frame forwarding.")
            ],
            ["mac-address", "routing", "layer2-vs-layer3"]
        ),
        (
            "IPV4-021", "ipv4-basics", "What is the dotted-decimal representation of a /24 subnet mask?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 30,
            "A /24 subnet mask contains 24 consecutive binary 1s followed by 8 binary 0s: 11111111.11111111.11111111.00000000, which converts in decimal to 255.255.255.0.",
            "Convert prefix notation /24 to dotted-decimal.",
            [
                ("255.255.255.0", True, "24 bits of ones equals 255.255.255.0."),
                ("255.255.0.0", False, "255.255.0.0 corresponds to a /16 mask."),
                ("255.0.0.0", False, "255.0.0.0 corresponds to a /8 mask."),
                ("255.255.255.255", False, "255.255.255.255 corresponds to a /32 mask.")
            ],
            ["ipv4", "subnet-masks", "conversion"]
        ),
        (
            "IPV4-022", "ipv4-address-structure", "What is the dotted-decimal representation of a /16 subnet mask?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 30,
            "A /16 subnet mask contains 16 consecutive binary 1s followed by 16 binary 0s: 11111111.11111111.00000000.00000000, which converts to 255.255.0.0.",
            "Convert prefix notation /16 to dotted-decimal.",
            [
                ("255.255.0.0", True, "16 bits of ones equals 255.255.0.0."),
                ("255.255.255.0", False, "255.255.255.0 is /24."),
                ("255.0.0.0", False, "255.0.0.0 is /8."),
                ("255.255.240.0", False, "255.255.240.0 is /20.")
            ],
            ["ipv4", "subnet-masks", "conversion"]
        ),
        (
            "IPV4-023", "ipv4-address-structure", "What is the dotted-decimal representation of a /8 subnet mask?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 30,
            "A /8 subnet mask contains 8 consecutive binary 1s followed by 24 binary 0s: 11111111.00000000.00000000.00000000, which converts to 255.0.0.0.",
            "Convert prefix notation /8 to dotted-decimal.",
            [
                ("255.0.0.0", True, "8 bits of ones equals 255.0.0.0."),
                ("255.255.0.0", False, "255.255.0.0 is /16."),
                ("255.255.255.0", False, "255.255.255.0 is /24."),
                ("255.255.255.255", False, "255.255.255.255 is /32.")
            ],
            ["ipv4", "subnet-masks", "conversion"]
        ),
        (
            "IPV4-024", "mac-address", "What is the hexadecimal representation format of an Ethernet MAC address?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "MAC addresses are represented as 12 hexadecimal characters, commonly separated by colons (e.g. 00:1A:2B:3C:4D:5E), hyphens (00-1A-2B-3C-4D-5E), or Cisco dot notation (001a.2b3c.4d5e).",
            "Identify standard MAC address formatting.",
            [
                ("12 hexadecimal digits separated into pairs by colons or hyphens", True, "Standard MAC notation uses 6 pairs of hex digits (48 bits)."),
                ("Four decimal numbers separated by dots from 0 to 255", False, "That is IPv4 dotted-decimal notation."),
                ("Eight 4-digit hexadecimal groups separated by colons", False, "That is IPv6 address notation."),
                ("A single 10-digit telephone number", False, "MAC addresses are not telephone numbers.")
            ],
            ["mac-address", "hexadecimal", "syntax"]
        ),
        (
            "IPV4-025", "default-gateway", "What occurs if a workstation has a valid IP address and subnet mask, but NO default gateway configured?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "Without a default gateway, the workstation can communicate normally with other computers on its own local subnet, but cannot send packets to any remote IP addresses outside that subnet (such as the Internet).",
            "Predict the connectivity consequence of a missing default gateway.",
            [
                ("It can communicate with devices on its local subnet, but cannot access external networks or the Internet", True, "The gateway is required to route traffic beyond the local subnet."),
                ("It cannot communicate with any device at all, even on its local switch", False, "Local communication uses direct ARP and switch forwarding without needing a gateway."),
                ("The computer's hard drive automatically formats itself", False, "Default gateway configuration does not affect local storage disks."),
                ("All local traffic is automatically encrypted with quantum keys", False, "Missing a gateway does not alter local encryption.")
            ],
            ["default-gateway", "troubleshooting", "routing"]
        ),
        (
            "IPV4-026", "public-vs-private-ip", "Which address is an example of an RFC 1918 Class C private address?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 40,
            "192.168.1.100 is within the RFC 1918 Class C private address block (192.168.0.0 through 192.168.255.255 /16).",
            "Identify Class C private addresses.",
            [
                ("192.168.1.100", True, "192.168.0.0/16 is the Class C private address block."),
                ("10.1.1.1", False, "10.0.0.0/8 is Class A private."),
                ("172.16.0.1", False, "172.16.0.0/12 is Class B private."),
                ("8.8.4.4", False, "8.8.4.4 is a public IP address.")
            ],
            ["public-vs-private-ip", "class-c", "rfc1918"]
        ),
        (
            "IPV4-027", "ipv4-basics", "Which IPv4 address represents the directed broadcast address on the 192.168.1.0/24 network?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 45,
            "On a /24 network with network address 192.168.1.0, the last address with all 8 host bits set to 1 is 192.168.1.255, which is the directed broadcast address.",
            "Determine the broadcast address for a /24 network.",
            [
                ("192.168.1.255", True, "192.168.1.255 is the broadcast address for 192.168.1.0/24."),
                ("192.168.1.0", False, "192.168.1.0 is the network identifier address."),
                ("192.168.1.1", False, "192.168.1.1 is typically the first usable host IP."),
                ("192.168.1.254", False, "192.168.1.254 is the last usable host IP.")
            ],
            ["ipv4", "broadcast-address", "subnetting"]
        ),
        (
            "IPV4-028", "ipv4-basics", "What is the network address for the host IP 10.20.30.40 with subnet mask 255.255.255.0 (/24)?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 45,
            "With a /24 mask (255.255.255.0), the first 3 octets are network bits and the last octet is set to 0 for the network address: 10.20.30.0.",
            "Determine the network address given a host IP and /24 mask.",
            [
                ("10.20.30.0", True, "Masking the host bits (the 4th octet) to 0 yields 10.20.30.0."),
                ("10.20.30.40", False, "10.20.30.40 is the host IP itself."),
                ("10.20.30.255", False, "10.20.30.255 is the broadcast address."),
                ("10.0.0.0", False, "10.0.0.0 would be the network address if the mask were /8.")
            ],
            ["ipv4", "network-address", "subnetting"]
        ),
        (
            "IPV4-029", "mac-address", "Can two network interface cards manufactured anywhere in the world legally share the same physical MAC address?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "No. Under IEEE 802 specifications, each globally administered MAC address is globally unique to ensure conflict-free communication on local area networks.",
            "Recognize the global uniqueness of standard MAC addresses.",
            [
                ("No, globally administered MAC addresses are designed to be universally unique across all hardware vendors", True, "IEEE coordinates OUI assignments to maintain global MAC uniqueness."),
                ("Yes, all computers made in the same year have identical MAC addresses", False, "Manufacture year does not duplicate MAC addresses."),
                ("Yes, but only if they are plugged into the same power strip", False, "Electrical power has no relation to MAC addressing."),
                ("Yes, because there are only 256 total MAC addresses available worldwide", False, "48-bit MAC addresses support over 281 trillion unique addresses ($2^{48}$).")
            ],
            ["mac-address", "uniqueness", "hardware"]
        ),
        (
            "IPV4-030", "ipv4-basics", "How many usable host IP addresses are available on a standard /24 IPv4 network?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "A /24 network has 8 host bits ($2^8 = 256$ total addresses). Subtracting the network address (first) and the broadcast address (last), there are $256 - 2 = 254$ usable host addresses.",
            "Calculate usable host addresses on a /24 network.",
            [
                ("254 usable hosts", True, "2^8 - 2 = 256 - 2 = 254 usable host addresses."),
                ("256 usable hosts", False, "256 is the total number of addresses; 2 are reserved."),
                ("255 usable hosts", False, "Both the network and broadcast addresses cannot be assigned to hosts."),
                ("128 usable hosts", False, "128 addresses corresponds to a /25 network.")
            ],
            ["ipv4", "usable-hosts", "subnetting"]
        ),
    ]
    save_questions("ipv4_and_mac_addressing.json", items)


if __name__ == "__main__":
    generate_osi_tcpip()
    generate_ipv4_mac()
