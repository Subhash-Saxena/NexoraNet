#!/usr/bin/env python3
"""
NexoraNet Beginner Bank Generator - Part 3.
Generates:
- ports_and_protocols.json (35 questions)
- devices_and_basic_security.json (25 questions)
Completes the full 150-question Beginner Bank!
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


def generate_ports_and_protocols():
    items = [
        (
            "PORT-001", "ports", "What is the standard TCP port used for unencrypted HTTP web traffic?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 30,
            "TCP port 80 is the standardized well-known port assigned by IANA for unencrypted Hypertext Transfer Protocol (HTTP) web server communications.",
            "Recall standard well-known port for HTTP.",
            [
                ("Port 80", True, "TCP port 80 is the default port for HTTP."),
                ("Port 443", False, "TCP port 443 is for encrypted HTTPS."),
                ("Port 22", False, "TCP port 22 is for SSH."),
                ("Port 53", False, "UDP/TCP port 53 is for DNS.")
            ],
            ["ports", "http", "well-known-ports"]
        ),
        (
            "PORT-002", "ports", "What is the standard TCP port used for secure, encrypted HTTPS web traffic?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 30,
            "TCP port 443 is the standard well-known port assigned for Hypertext Transfer Protocol Secure (HTTPS), which encapsulates HTTP inside a TLS/SSL encrypted tunnel.",
            "Recall standard well-known port for HTTPS.",
            [
                ("Port 443", True, "TCP port 443 is the default port for HTTPS."),
                ("Port 80", False, "TCP port 80 is unencrypted HTTP."),
                ("Port 8080", False, "Port 8080 is an alternative HTTP proxy port."),
                ("Port 25", False, "Port 25 is for SMTP mail transfer.")
            ],
            ["ports", "https", "tls", "well-known-ports"]
        ),
        (
            "PORT-003", "dns", "What is the primary function of the Domain Name System (DNS)?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "DNS acts as the phonebook of the Internet, translating human-readable hostnames (such as www.example.com) into machine-routable IP addresses (such as 93.184.216.34).",
            "Explain the core purpose of the Domain Name System.",
            [
                ("To translate human-friendly domain names into numerical IP addresses", True, "DNS resolves domain names to IP addresses and vice versa."),
                ("To dynamically assign IP addresses and default gateways to local clients", False, "That is the role of DHCP (Dynamic Host Configuration Protocol)."),
                ("To physically route fiber-optic pulses under the ocean", False, "Undersea cable routing is physical infrastructure management."),
                ("To compress digital video streams before downloading", False, "Video compression is handled by application/presentation codecs.")
            ],
            ["dns", "protocols", "fundamentals"]
        ),
        (
            "PORT-004", "ports", "Which port and transport protocol is predominantly used by client DNS name queries?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "Standard client DNS resolution queries use UDP port 53 for fast, lightweight name lookups without connection setup overhead (though TCP port 53 is used for large zone transfers).",
            "Identify the transport port and protocol used by DNS queries.",
            [
                ("UDP port 53", True, "DNS client queries standardly use UDP port 53."),
                ("TCP port 21", False, "TCP port 21 is for FTP control."),
                ("UDP port 67", False, "UDP port 67 is for DHCP server listening."),
                ("TCP port 23", False, "TCP port 23 is for unencrypted Telnet.")
            ],
            ["dns", "ports", "udp"]
        ),
        (
            "PORT-005", "dhcp", "What is the primary function of the Dynamic Host Configuration Protocol (DHCP)?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "DHCP automatically assigns network configuration settings—including an IPv4 address, subnet mask, default gateway, and DNS servers—to client devices joining a network.",
            "Explain the function of DHCP in local networks.",
            [
                ("To automatically lease IP addresses, subnet masks, default gateways, and DNS settings to network clients", True, "DHCP automates client IP configuration without manual static entry."),
                ("To translate private IP addresses into public IP addresses on a boundary router", False, "That is Network Address Translation (NAT)."),
                ("To establish encrypted SSH tunnels for remote server administration", False, "That is the role of Secure Shell (SSH)."),
                ("To block incoming malicious packets using stateful inspection", False, "That is the role of a firewall.")
            ],
            ["dhcp", "protocols", "configuration"]
        ),
        (
            "PORT-006", "dhcp", "What is the four-step message exchange process used by DHCP to allocate an IP address to a client?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "DHCP client-server allocation uses the DORA sequence: Discover (broadcast by client), Offer (unicast/broadcast by server), Request (broadcast by client), Acknowledgement (sent by server).",
            "Recall the DORA process in DHCP.",
            [
                ("Discover -> Offer -> Request -> Acknowledge (DORA)", True, "DORA is the standard four-message DHCP handshake sequence."),
                ("SYN -> SYN-ACK -> ACK -> FIN", False, "That describes the TCP 3-way handshake and connection teardown."),
                ("Ping -> Echo -> Trace -> Route", False, "These are CLI troubleshooting commands and ICMP message types."),
                ("Connect -> Authenticate -> Authorize -> Accounting", False, "That describes AAA identity management workflows.")
            ],
            ["dhcp", "dora", "protocols"]
        ),
        (
            "PORT-007", "ports", "Which UDP ports are used by DHCP client requests and DHCP server responses?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "DHCP servers listen on UDP port 67, and DHCP clients listen for responses on UDP port 68.",
            "Identify the UDP ports used by DHCP.",
            [
                ("UDP port 67 (Server) and UDP port 68 (Client)", True, "DHCP uses UDP ports 67 (server) and 68 (client)."),
                ("TCP port 80 and TCP port 443", False, "These are web server ports."),
                ("UDP port 53 and TCP port 53", False, "These are DNS ports."),
                ("TCP port 20 and TCP port 21", False, "These are FTP data and control ports.")
            ],
            ["dhcp", "ports", "udp"]
        ),
        (
            "PORT-008", "arp", "What is the primary function of the Address Resolution Protocol (ARP)?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "ARP resolves a known logical Layer 3 IP address to its corresponding physical Layer 2 MAC address on a local area network segment.",
            "Define the function of ARP.",
            [
                ("To resolve a known IPv4 address to its corresponding physical MAC address on a local LAN", True, "ARP maps IP addresses to MAC hardware addresses on local Ethernet/Wi-Fi links."),
                ("To convert domain names into IP addresses over the Internet", False, "That is the role of DNS."),
                ("To assign cryptographic SSL certificates to web servers", False, "That is the role of a Certificate Authority (CA)."),
                ("To measure the physical length of an Ethernet cable in feet", False, "That is done using a Time-Domain Reflectometer (TDR).")
            ],
            ["arp", "layer2", "layer3", "mac-address"]
        ),
        (
            "PORT-009", "arp", "When a computer sends an ARP Request to find a neighbor's MAC address, what destination MAC address is used in the Ethernet frame?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "Because the host does not yet know the destination MAC address, it sends the ARP Request as a Layer 2 broadcast to FF:FF:FF:FF:FF:FF so that every device on the local switch processes it.",
            "Identify the broadcast destination of ARP requests.",
            [
                ("FF:FF:FF:FF:FF:FF (Broadcast)", True, "ARP requests are broadcast to all hosts on the local network."),
                ("00:00:00:00:00:00", False, "This is not a valid destination broadcast address."),
                ("127.0.0.1", False, "127.0.0.1 is an IPv4 loopback address, not an Ethernet MAC address."),
                ("The destination server's public IP address", False, "Ethernet frames require a MAC address in the Layer 2 header, not an IP address.")
            ],
            ["arp", "broadcast", "ethernet"]
        ),
        (
            "PORT-010", "icmp", "Which core network utility uses ICMP Echo Request and Echo Reply messages to test basic IP connectivity between hosts?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "The 'ping' utility sends ICMP Echo Request (Type 8) messages and listens for ICMP Echo Reply (Type 0) messages to verify Layer 3 connectivity and measure round-trip time.",
            "Identify the utility based on ICMP Echo Request/Reply.",
            [
                ("ping", True, "Ping uses ICMP Echo Request and Echo Reply messages."),
                ("netstat", False, "Netstat displays active network connections, routing tables, and interface stats."),
                ("nslookup", False, "Nslookup queries DNS servers."),
                ("ipconfig", False, "Ipconfig displays local interface IP configurations.")
            ],
            ["icmp", "ping", "troubleshooting"]
        ),
        (
            "PORT-011", "icmp", "At which layer of the TCP/IP model does ICMP (Internet Control Message Protocol) operate?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "ICMP operates at the Internet Layer (OSI Layer 3). While it is encapsulated inside IP packets, it is an integral companion protocol to IP used for network diagnostics and error reporting.",
            "Recall the architectural layer of ICMP.",
            [
                ("Internet Layer (OSI Layer 3)", True, "ICMP operates at the Internet/Network layer alongside IP."),
                ("Application Layer (OSI Layer 7)", False, "ICMP is not an application protocol."),
                ("Transport Layer (OSI Layer 4)", False, "ICMP does not use TCP or UDP ports; it runs directly over IP."),
                ("Physical Layer (OSI Layer 1)", False, "Physical layer deals with electrical signals.")
            ],
            ["icmp", "internet-layer", "osi"]
        ),
        (
            "PORT-012", "tcp-basics", "Which three-way handshake sequence is used by TCP to establish a reliable connection between a client and a server?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "The TCP three-way handshake proceeds as: 1. Client sends SYN (Synchronize), 2. Server responds with SYN-ACK (Synchronize-Acknowledge), 3. Client replies with ACK (Acknowledge).",
            "Recall the TCP 3-way handshake sequence.",
            [
                ("SYN -> SYN-ACK -> ACK", True, "The TCP three-way handshake begins with SYN, responds with SYN-ACK, and concludes with ACK."),
                ("ACK -> SYN-ACK -> FIN", False, "This is not a valid handshake sequence."),
                ("HELLO -> ACK -> DATA", False, "TCP does not use HELLO packets; that terminology is used in routing protocols like OSPF."),
                ("DISCOVER -> OFFER -> REQUEST", False, "That is the DHCP DORA process.")
            ],
            ["tcp", "three-way-handshake", "tcp-flags"]
        ),
        (
            "PORT-013", "tcp-basics", "What is the primary operational difference between TCP and UDP?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "TCP is a connection-oriented protocol providing guaranteed delivery, sequence numbers, and error retransmission. UDP is a connectionless, best-effort protocol that prioritizes low latency without delivery guarantees.",
            "Compare TCP reliability against UDP speed.",
            [
                ("TCP provides connection-oriented reliable delivery with acknowledgements; UDP is connectionless and best-effort with lower latency", True, "TCP guarantees delivery; UDP prioritizes speed and minimal overhead."),
                ("TCP only works over Wi-Fi; UDP only works over copper cables", False, "Both transport protocols work across all network media."),
                ("UDP encrypts all packets; TCP transmits only unencrypted plaintext", False, "Encryption is handled by higher-layer protocols (like TLS), not by UDP."),
                ("TCP is restricted to 10 Mbps maximum bandwidth", False, "TCP scales to multi-gigabit speeds.")
            ],
            ["tcp", "udp", "transport-layer", "comparison"]
        ),
        (
            "PORT-014", "udp-basics", "Which of the following real-time applications typically relies on UDP rather than TCP?",
            "SINGLE_CHOICE", "BEGINNER", "APPLY", 1, 45,
            "Live Voice over IP (VoIP) and real-time streaming use UDP because lost audio packets cannot be retransmitted without introducing unacceptable voice delays; recent data is preferred over late retransmissions.",
            "Identify applications that benefit from UDP transport.",
            [
                ("Live VoIP audio and online multiplayer video games", True, "Real-time interactive audio/video values low latency over guaranteed retransmission."),
                ("Secure financial bank wire transfers", False, "Financial transactions require strict TCP reliability and verification."),
                ("Downloading executable software update patches", False, "Software installers must be complete and uncorrupted, requiring TCP."),
                ("Sending business email attachments via SMTP", False, "Email delivery requires reliable TCP transmission.")
            ],
            ["udp", "voip", "real-time", "applications"]
        ),
        (
            "PORT-015", "ports", "What is the standard TCP port used for Secure Shell (SSH) remote administrative login?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 30,
            "TCP port 22 is the standardized well-known port for Secure Shell (SSH), providing encrypted remote terminal sessions and SFTP file transfer.",
            "Recall standard well-known port for SSH.",
            [
                ("Port 22", True, "TCP port 22 is standard for SSH."),
                ("Port 23", False, "TCP port 23 is Telnet (unencrypted)."),
                ("Port 21", False, "TCP port 21 is FTP control."),
                ("Port 3389", False, "TCP port 3389 is Microsoft RDP.")
            ],
            ["ports", "ssh", "security", "remote-access"]
        ),
        (
            "PORT-016", "ssh", "Why has SSH almost entirely replaced Telnet for command-line server administration?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "Telnet transmits all data—including usernames and passwords—in clear plaintext across the network, making it trivial for eavesdroppers to capture credentials. SSH encrypts the entire communication session.",
            "Explain the security advantage of SSH over Telnet.",
            [
                ("SSH encrypts all traffic including passwords; Telnet transmits credentials in unencrypted plaintext", True, "SSH prevents packet sniffing attacks by encrypting the full session with asymmetric/symmetric cryptography."),
                ("Telnet requires expensive satellite equipment; SSH runs on copper wires", False, "Both protocols run over standard IP networks."),
                ("SSH increases server processor speeds by 500%", False, "SSH does not increase processor clock frequencies."),
                ("Telnet can only be installed on smartphones", False, "Telnet was historically the standard terminal protocol on servers and mainframes.")
            ],
            ["ssh", "telnet", "security", "encryption"]
        ),
        (
            "PORT-017", "ports", "Which protocol and standard port is used to transfer outgoing email from a client to a mail server?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "Simple Mail Transfer Protocol (SMTP) standardly uses TCP port 25 (or port 587 with STARTTLS submission) to transmit outgoing email messages between mail agents.",
            "Identify email transmission protocol and port.",
            [
                ("SMTP on TCP port 25 (or 587)", True, "SMTP handles outgoing email transport on port 25 / 587."),
                ("POP3 on TCP port 110", False, "POP3 is for retrieving email from a mailbox."),
                ("IMAP on TCP port 143", False, "IMAP is for synchronizing and retrieving email from a mailbox."),
                ("SNMP on UDP port 161", False, "SNMP is for network device management.")
            ],
            ["ports", "smtp", "email"]
        ),
        (
            "PORT-018", "ports", "Which two protocols are commonly used by email clients to RETRIEVE emails from a mail server?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "POP3 (Post Office Protocol 3) and IMAP (Internet Message Access Protocol) are the two primary protocols used by client mail applications to fetch stored emails from a mail server.",
            "Recall email retrieval protocols.",
            [
                ("POP3 and IMAP", True, "POP3 and IMAP allow client software to access and read emails stored on a mail server."),
                ("SMTP and DNS", False, "SMTP sends email; DNS resolves domain names."),
                ("FTP and TFTP", False, "FTP and TFTP are file transfer protocols."),
                ("HTTP and DHCP", False, "HTTP is for web pages; DHCP is for IP address assignment.")
            ],
            ["email", "imap", "pop3", "protocols"]
        ),
        (
            "PORT-019", "ports", "What is the standard port for unencrypted File Transfer Protocol (FTP) control connections?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "FTP uses TCP port 21 for its command/control channel (where user authentication and commands are negotiated), and port 20 for active data transfer.",
            "Identify the FTP control port.",
            [
                ("TCP port 21", True, "TCP port 21 is the standard FTP control port."),
                ("TCP port 22", False, "TCP port 22 is SSH / SFTP."),
                ("TCP port 80", False, "TCP port 80 is HTTP."),
                ("UDP port 69", False, "UDP port 69 is Trivial FTP (TFTP).")
            ],
            ["ports", "ftp", "file-transfer"]
        ),
        (
            "PORT-020", "ports-and-sockets", "In computer networking, what two components form a network 'socket'?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "A network socket is defined by the combination of an IP address (identifying the specific host interface) and a port number (identifying the specific process or service on that host), e.g., 192.168.1.50:443.",
            "Define the composition of a network socket.",
            [
                ("An IP address combined with a port number", True, "A socket represents an endpoint of a two-way communication link: IP Address + Port."),
                ("A MAC address combined with an operating system license key", False, "Sockets are Layer 3/4 constructs independent of software licensing."),
                ("A username combined with a hashed password", False, "Sockets identify network endpoints, not user identity credentials."),
                ("An electrical wall outlet combined with a surge protector", False, "In networking software, a socket is an API communication endpoint.")
            ],
            ["ports-and-sockets", "socket", "fundamentals"]
        ),
        (
            "PORT-021", "ports", "What range of port numbers is designated as 'Well-Known Ports' (system ports) by IANA?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "Ports 0 through 1023 are classified as Well-Known Ports, reserved for privileged system services such as HTTP (80), HTTPS (443), SSH (22), and DNS (53).",
            "Recall the IANA well-known port range.",
            [
                ("0 to 1023", True, "0 to 1023 are Well-Known ports reserved for standard system protocols."),
                ("1024 to 49151", False, "1024 to 49151 are Registered ports."),
                ("49152 to 65535", False, "49152 to 65535 are Dynamic or Ephemeral ports."),
                ("1 to 65536", False, "The total 16-bit port range is 0 to 65535.")
            ],
            ["ports", "iana", "well-known-ports"]
        ),
        (
            "PORT-022", "ports-and-sockets", "What term describes the temporary, high-numbered ports dynamically allocated by an operating system to outgoing client connections?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "Ephemeral (or dynamic) ports are high-numbered ports (typically 49152 to 65535) temporarily assigned by the client OS to identify an outbound connection session, and released once closed.",
            "Identify ephemeral port allocation.",
            [
                ("Ephemeral (or dynamic) ports", True, "Ephemeral ports are short-lived client ports allocated from the dynamic range."),
                ("Static system ports", False, "Static ports (0-1023) are permanently bound to listening services."),
                ("Broadcast ports", False, "Ports are transport endpoints, not broadcast addresses."),
                ("Serial COM ports", False, "COM ports are physical serial hardware ports on motherboards.")
            ],
            ["ports", "ephemeral-ports", "sockets"]
        ),
        (
            "PORT-023", "http", "What HTTP request method is standardly used by a web browser to request and retrieve a web page from a server?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "The HTTP GET method is used to retrieve data or resources (HTML documents, images, stylesheets) from a specified web server URI without altering server state.",
            "Identify the standard HTTP retrieval method.",
            [
                ("GET", True, "GET retrieves representation of resources from a web server."),
                ("POST", False, "POST submits data to be processed by the server (e.g. form submissions)."),
                ("DELETE", False, "DELETE requests removal of a resource."),
                ("CONNECT", False, "CONNECT is used to establish tunnels, typically for HTTPS proxies.")
            ],
            ["http", "http-methods", "web"]
        ),
        (
            "PORT-024", "http", "What HTTP response status code family indicates that a request was successfully received, understood, and processed?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "2xx status codes indicate Success. The most common is '200 OK', confirming that the web server successfully processed the request and is returning the payload.",
            "Recognize HTTP success status code ranges.",
            [
                ("2xx (e.g., 200 OK)", True, "2xx status codes indicate successful HTTP transactions."),
                ("4xx (e.g., 404 Not Found)", False, "4xx indicates client-side errors."),
                ("5xx (e.g., 500 Internal Server Error)", False, "5xx indicates server-side errors."),
                ("3xx (e.g., 301 Moved Permanently)", False, "3xx indicates redirection.")
            ],
            ["http", "http-status-codes", "web"]
        ),
        (
            "PORT-025", "http", "What does an HTTP '404 Not Found' status code signify?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 35,
            "A 404 status code is a client-side error indicating that the server could not find the specific resource or URL requested by the browser.",
            "Interpret HTTP 404 Not Found.",
            [
                ("The web server could not find the requested webpage or resource at the specified URL", True, "404 means the requested resource does not exist on the server."),
                ("The client's Ethernet cable has been disconnected", False, "Receiving a 404 proves that network connectivity to the server succeeded."),
                ("The user's computer processor is overheating", False, "HTTP status codes reflect web server resource states, not hardware temperatures."),
                ("The entire Internet has been deleted", False, "A 404 is an ordinary application error indicating a missing file.")
            ],
            ["http", "http-status-codes", "troubleshooting"]
        ),
        (
            "PORT-026", "dns", "Which DNS record type maps a domain name to an IPv4 address?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "An 'A' (Address) record maps a fully qualified domain name (FQDN) to its 32-bit IPv4 address (e.g. example.com -> 93.184.216.34).",
            "Identify IPv4 DNS address records.",
            [
                ("A record", True, "An A record maps a domain name to an IPv4 address."),
                ("AAAA record", False, "An AAAA (quad-A) record maps a domain name to an IPv6 address."),
                ("MX record", False, "An MX record points to the mail server handling email for a domain."),
                ("PTR record", False, "A PTR record maps an IP address back to a hostname (reverse DNS).")
            ],
            ["dns", "dns-records", "ipv4"]
        ),
        (
            "PORT-027", "dns", "Which DNS record type maps a domain name to an IPv6 address?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "An 'AAAA' record (quad-A) maps a domain name to a 128-bit IPv6 address (e.g. example.com -> 2606:2800:220:1:248:1893:25c8:1946).",
            "Identify IPv6 DNS address records.",
            [
                ("AAAA record", True, "An AAAA record maps a domain name to an IPv6 address."),
                ("A record", False, "An A record maps to an IPv4 address."),
                ("CNAME record", False, "A CNAME record maps an alias hostname to a canonical hostname."),
                ("TXT record", False, "A TXT record stores arbitrary text data (e.g., SPF, DKIM verification).")
            ],
            ["dns", "dns-records", "ipv6"]
        ),
        (
            "PORT-028", "dns", "Which DNS record type specifies the mail servers responsible for accepting incoming email for a domain?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "MX (Mail Exchanger) records specify the mail servers authorized to accept incoming email messages for a domain, along with preference priorities.",
            "Identify mail exchanger DNS records.",
            [
                ("MX record", True, "MX records direct email traffic to designated mail servers."),
                ("A record", False, "A records resolve web and general host IPv4 addresses."),
                ("NS record", False, "NS records identify the authoritative nameservers for a zone."),
                ("SOA record", False, "SOA records contain administrative and zone transfer parameters.")
            ],
            ["dns", "mx-record", "email"]
        ),
        (
            "PORT-029", "dns", "What is the purpose of a DNS CNAME (Canonical Name) record?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "A CNAME record creates an alias that points one domain name to another domain name (e.g., pointing 'www.example.com' to 'example.com'), rather than pointing directly to an IP address.",
            "Explain the function of DNS CNAME records.",
            [
                ("To create an alias pointing one domain name to another canonical domain name", True, "CNAME provides alias redirection to another domain name."),
                ("To permanently block all encrypted HTTPS traffic to a server", False, "DNS records resolve addresses; they do not enforce firewall blocks."),
                ("To assign a dynamic private IP address to a home printer", False, "DHCP assigns IP addresses to printers."),
                ("To measure packet round-trip time between two servers", False, "Ping/ICMP measures round-trip latency.")
            ],
            ["dns", "cname", "dns-records"]
        ),
        (
            "PORT-030", "ports", "What is the standard port used by Network Time Protocol (NTP) to synchronize system clocks across network devices?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "Network Time Protocol (NTP) standardly uses UDP port 123 to synchronize device system clocks within milliseconds of Coordinated Universal Time (UTC).",
            "Recall the standard UDP port for NTP.",
            [
                ("UDP port 123", True, "UDP port 123 is the standard port for Network Time Protocol (NTP)."),
                ("TCP port 25", False, "TCP port 25 is SMTP."),
                ("UDP port 69", False, "UDP port 69 is TFTP."),
                ("TCP port 110", False, "TCP port 110 is POP3.")
            ],
            ["ports", "ntp", "time-synchronization"]
        ),
        (
            "PORT-031", "ports", "Why is accurate time synchronization via NTP critically important in cybersecurity incident investigation?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 50,
            "Incident responders correlate log events across firewalls, servers, and endpoint detection agents. If clocks are out of sync, constructing an accurate chronological timeline of an attacker's actions is impossible.",
            "Explain the security value of synchronized system time.",
            [
                ("It ensures log timestamps across all firewalls, servers, and sensors align accurately to construct reliable attack timelines", True, "Accurate log timeline correlation across dispersed systems is essential for incident forensics."),
                ("It automatically disables all user passwords after 5:00 PM every evening", False, "NTP synchronizes time; it does not manage password expiry rules."),
                ("It increases the physical download speed of large video files", False, "NTP synchronization has no effect on network transmission throughput."),
                ("It prevents computers from being affected by electrical power outages", False, "NTP is a software time protocol, not an electrical power battery.")
            ],
            ["ntp", "soc", "incident-investigation", "timestamps"]
        ),
        (
            "PORT-032", "ports", "Which port and protocol is standardly used by Simple Network Management Protocol (SNMP) agents to receive queries from management stations?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "SNMP agents listen for polling queries from Network Management Stations (NMS) on UDP port 161. (Unsolicited SNMP Traps are sent to NMS on UDP port 162).",
            "Identify the standard port for SNMP.",
            [
                ("UDP port 161", True, "UDP port 161 is standard for SNMP agent polling queries."),
                ("TCP port 443", False, "TCP port 443 is HTTPS."),
                ("UDP port 53", False, "UDP port 53 is DNS."),
                ("TCP port 22", False, "TCP port 22 is SSH.")
            ],
            ["ports", "snmp", "network-monitoring"]
        ),
        (
            "PORT-033", "tcp-basics", "Which TCP flag is sent by a host to immediately and abruptly abort/reset an invalid or unrecognized connection?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "The RST (Reset) flag is sent to immediately tear down a connection, commonly when a packet arrives for a closed port or an invalid TCP state occurs.",
            "Identify the function of the TCP RST flag.",
            [
                ("RST (Reset)", True, "RST abruptly terminates or rejects a TCP connection."),
                ("SYN (Synchronize)", False, "SYN initiates a connection."),
                ("ACK (Acknowledge)", False, "ACK acknowledges received data."),
                ("URG (Urgent)", False, "URG marks data that should be processed urgently.")
            ],
            ["tcp", "tcp-flags", "reset"]
        ),
        (
            "PORT-034", "tcp-basics", "Which TCP flag is used to gracefully initiate the termination of a connection once all data has been sent?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "The FIN (Finish) flag is transmitted by a host when it has finished sending data, initiating the graceful 4-step TCP connection teardown sequence.",
            "Identify the TCP flag for graceful termination.",
            [
                ("FIN (Finish)", True, "FIN indicates that the sender has finished transmitting data."),
                ("SYN (Synchronize)", False, "SYN is used for connection startup."),
                ("PSH (Push)", False, "PSH informs the receiver to push data directly to the application."),
                ("RST (Reset)", False, "RST is an abrupt forced termination.")
            ],
            ["tcp", "tcp-flags", "fin"]
        ),
        (
            "PORT-035", "ports", "What is the standard TCP port used by Microsoft Remote Desktop Protocol (RDP) for graphical desktop access?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "TCP port 3389 is the default port for Microsoft Remote Desktop Protocol (RDP), allowing users and administrators to connect graphically to remote Windows workstations and servers.",
            "Recall the standard port for Microsoft RDP.",
            [
                ("TCP port 3389", True, "TCP port 3389 is the default port for RDP."),
                ("TCP port 22", False, "TCP port 22 is SSH (command line)."),
                ("TCP port 443", False, "TCP port 443 is HTTPS."),
                ("TCP port 80", False, "TCP port 80 is HTTP.")
            ],
            ["ports", "rdp", "remote-access"]
        ),
    ]
    save_questions("ports_and_protocols.json", items)


def generate_devices_and_security():
    items = [
        (
            "DEV-SEC-001", "firewall-basics", "What is the primary function of a network firewall?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "A firewall inspects incoming and outgoing network traffic based on established security rules, permitting authorized communications while blocking unauthorized or potentially dangerous traffic.",
            "Explain the core purpose of a network firewall.",
            [
                ("To filter incoming and outgoing traffic based on security policies, permitting or blocking packets", True, "Firewalls enforce access control policies at network perimeter boundaries."),
                ("To assign dynamic IP addresses to wireless laptops", False, "DHCP assigns IP addresses."),
                ("To amplify copper electrical signals over long distances", False, "Repeaters amplify electrical signals."),
                ("To convert PDF documents into raw ASCII binary code", False, "Document conversion is an application software function.")
            ],
            ["firewall", "firewall-basics", "security"]
        ),
        (
            "DEV-SEC-002", "firewall-basics", "What does a 'stateless' firewall examine when determining whether to allow or drop a packet?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "A stateless firewall inspects each packet in isolation, examining only individual packet header fields (source/destination IP, source/destination port, protocol) without tracking prior connection state.",
            "Explain how stateless packet filtering functions.",
            [
                ("It inspects individual packet headers (IP addresses, port numbers) in isolation without tracking connection state", True, "Stateless filtering evaluates each packet independently against static ACL rules."),
                ("It continuously monitors full application layer payloads across years of historical data", False, "Stateless firewalls do not inspect payloads or maintain state tables."),
                ("It monitors the physical temperature of the server room", False, "Firewalls evaluate network packets, not ambient room temperature."),
                ("It forces users to change their account passwords every 10 seconds", False, "Stateless firewalls do not manage user password policies.")
            ],
            ["firewall", "stateless", "filtering"]
        ),
        (
            "DEV-SEC-003", "firewall-basics", "What key capability distinguishes a 'stateful' firewall from a basic stateless packet filter?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 50,
            "A stateful firewall maintains a dynamic state table tracking active TCP and UDP connections. It automatically permits legitimate inbound response traffic belonging to an established outbound session.",
            "Contrast stateful firewalls with stateless filters.",
            [
                ("It tracks the state of active network connections in a state table, automatically allowing return traffic for established sessions", True, "Stateful inspection recognizes established connection contexts and allows valid replies."),
                ("It operates without any electricity using quantum magnets", False, "Firewalls require standard electrical power."),
                ("It encrypts every file stored on all user desktop computers", False, "Firewalls filter transit network packets, not local endpoint disk storage."),
                ("It only allows network traffic on alternate Thursdays", False, "Stateful firewalls operate continuously.")
            ],
            ["firewall", "stateful", "security"]
        ),
        (
            "DEV-SEC-004", "firewall-basics", "In firewall rule design, what does the security principle of 'Implicit Deny' mean?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "Implicit Deny dictates that any network traffic not explicitly permitted by an authorized rule in the access control list (ACL) is automatically dropped by default at the end of the rule list.",
            "Define the principle of Implicit Deny in firewall security.",
            [
                ("Any traffic that does not match an explicit 'allow' rule is automatically dropped by default", True, "Implicit Deny ensures that only explicitly approved traffic can traverse the firewall."),
                ("All traffic is permitted through the firewall unless a user files a formal written complaint", False, "Default permit (open by default) is insecure and contradicts Implicit Deny."),
                ("The firewall denies that it exists when queried by network administrators", False, "Implicit Deny is a packet filtering default rule, not device concealment."),
                ("Computers are forbidden from accessing web pages containing the letter 'E'", False, "Firewall rules filter based on addresses, ports, and protocols.")
            ],
            ["firewall", "implicit-deny", "acl", "defense"]
        ),
        (
            "DEV-SEC-005", "authentication", "In cybersecurity, what are the three classic authentication factors typically combined for Multi-Factor Authentication (MFA)?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 45,
            "The three core authentication factors are: 1. Something you know (password, PIN), 2. Something you have (smartcard, hardware token, phone authenticator), 3. Something you are (biometrics like fingerprint or retina).",
            "Identify the three core authentication factors.",
            [
                ("Something you know, something you have, and something you are", True, "MFA combines knowledge, possession, and inherence factors."),
                ("Something you buy, something you sell, and something you trade", False, "These are commercial financial transactions."),
                ("Your IP address, your MAC address, and your subnet mask", False, "Network addresses identify network interfaces, not authenticated human identities."),
                ("Your CPU speed, your RAM capacity, and your monitor size", False, "These are hardware hardware specifications.")
            ],
            ["authentication", "mfa", "security-fundamentals"]
        ),
        (
            "DEV-SEC-006", "encryption", "What is the primary difference between symmetric and asymmetric encryption?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 50,
            "Symmetric encryption uses the same single secret key for both encryption and decryption (e.g. AES). Asymmetric encryption uses a mathematically linked key pair: a public key for encryption and a private key for decryption (e.g. RSA).",
            "Contrast symmetric and asymmetric encryption.",
            [
                ("Symmetric uses the same key for encryption and decryption; asymmetric uses a public key for encryption and a private key for decryption", True, "Symmetric is fast and uses one shared secret; asymmetric solves key exchange using public/private pairs."),
                ("Symmetric encryption only works on odd-numbered days; asymmetric works on even days", False, "Cryptographic algorithms function continuously without calendar dependencies."),
                ("Asymmetric encryption can only encrypt two words per day", False, "Asymmetric cryptography processes data blocks, though it is computationally heavier than symmetric."),
                ("Symmetric encryption does not require any mathematical algorithms", False, "All digital encryption relies on rigorous mathematical foundations.")
            ],
            ["encryption", "symmetric", "asymmetric", "cryptography"]
        ),
        (
            "DEV-SEC-007", "encryption", "In asymmetric public-key cryptography, which key must ALWAYS be kept strictly confidential by the owner?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "The private key must always be kept secret and protected by its owner. The public key can be freely distributed to anyone worldwide to encrypt messages destined for the owner or verify their digital signature.",
            "Understand public vs private key confidentiality.",
            [
                ("The Private Key", True, "The private key must never be shared; compromising it allows adversaries to decrypt data or forge signatures."),
                ("The Public Key", False, "The public key is designed to be published openly to the world."),
                ("The MAC Address", False, "MAC addresses are hardware identifiers, not cryptographic keys."),
                ("The DNS Root Zone", False, "The DNS root zone is a public Internet database.")
            ],
            ["encryption", "public-key", "private-key", "cryptography"]
        ),
        (
            "DEV-SEC-008", "common-network-threats", "What type of attack involves an adversary flooding a target server with overwhelming volumes of traffic to exhaust its resources and take it offline?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "A Denial of Service (DoS) or Distributed Denial of Service (DDoS) attack seeks to make a machine or network resource unavailable to legitimate users by overwhelming it with flood traffic.",
            "Define Denial of Service attacks.",
            [
                ("Denial of Service (DoS / DDoS) attack", True, "DoS/DDoS exhausts system bandwidth, memory, or processing queues."),
                ("Man-in-the-Middle (MitM) attack", False, "MitM intercepts and alters communications between two parties."),
                ("SQL Injection attack", False, "SQL injection targets backend relational database queries via web inputs."),
                ("Cross-Site Scripting (XSS) attack", False, "XSS injects malicious client-side scripts into web pages viewed by other users.")
            ],
            ["threats", "dos", "ddos", "security"]
        ),
        (
            "DEV-SEC-009", "common-network-threats", "What distinguishes a Distributed Denial of Service (DDoS) attack from a standard Denial of Service (DoS) attack?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "A DoS attack originates from a single sending machine or IP. A DDoS attack uses a botnet of hundreds or thousands of compromised, geographically distributed devices to flood the victim simultaneously.",
            "Contrast DoS and DDoS attack architectures.",
            [
                ("A DDoS attack uses multiple compromised endpoints (a botnet) distributed globally to flood the target simultaneously", True, "DDoS leverages distributed botnets to generate massive aggregate traffic volumes."),
                ("A DDoS attack only targets smartphones over 5G networks", False, "DDoS attacks target web servers, routers, DNS, and infrastructure across all network types."),
                ("A DoS attack is legal under international law, but DDoS is not", False, "Both unauthorized DoS and DDoS attacks are illegal under computer crime statutes worldwide."),
                ("A DDoS attack requires physically cutting all underground fiber cables", False, "DDoS is a network traffic flood, not physical vandalism.")
            ],
            ["threats", "ddos", "botnet", "security"]
        ),
        (
            "DEV-SEC-010", "common-network-threats", "What type of attack occurs when an adversary secretly intercepts, reads, and potentially alters communications between two trusting parties?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 40,
            "A Man-in-the-Middle (MitM) attack occurs when an attacker positions themselves between a client and server (e.g., via ARP spoofing or rogue Wi-Fi) to eavesdrop or tamper with in-flight data.",
            "Define Man-in-the-Middle attacks.",
            [
                ("Man-in-the-Middle (MitM) attack", True, "MitM intercepts and relays communications between two parties who believe they are talking directly."),
                ("Brute Force password attack", False, "Brute force attempts password combinations sequentially."),
                ("Buffer Overflow attack", False, "Buffer overflow exploits memory management bugs in native software applications."),
                ("Phishing email attack", False, "Phishing tricks users into revealing credentials or clicking malicious links.")
            ],
            ["threats", "mitm", "arp-spoofing", "security"]
        ),
        (
            "DEV-SEC-011", "common-network-threats", "What is 'phishing' in the context of cybersecurity?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 35,
            "Phishing is a social engineering attack where fraudulent emails or messages disguise themselves as trustworthy entities (banks, IT departments) to trick victims into revealing sensitive credentials or downloading malware.",
            "Define phishing social engineering attacks.",
            [
                ("Deceptive social engineering communications designed to trick users into divulging sensitive credentials or clicking malicious links", True, "Phishing exploits human trust to compromise credentials and endpoints."),
                ("Using a fishhook to pull Ethernet cables through wall conduits", False, "This is physical cable installation slang, not cyber phishing."),
                ("A protocol used to synchronize clocks between offshore oil platforms", False, "That would be NTP over satellite."),
                ("A hardware tool that tests the electrical voltage of telephone jacks", False, "That is a voltmeter/multimeter.")
            ],
            ["threats", "phishing", "social-engineering"]
        ),
        (
            "DEV-SEC-012", "common-network-threats", "What is 'malware'?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 30,
            "Malware (Malicious Software) is an umbrella term encompassing viruses, worms, trojans, ransomware, spyware, and rootkits designed specifically to damage, disrupt, or gain unauthorized access to computer systems.",
            "Define malware.",
            [
                ("An umbrella term for malicious software designed to disrupt, damage, or gain unauthorized access to computer systems", True, "Malware includes viruses, worms, ransomware, and spyware."),
                ("A hardware chip that speeds up 3D computer graphics processing", False, "That is a Graphics Processing Unit (GPU)."),
                ("A software license agreement required to use open-source Linux", False, "Open-source software licenses are GPL, MIT, Apache, etc."),
                ("A type of optical fiber connector used in telecommunications", False, "Connectors include LC, SC, and ST.")
            ],
            ["threats", "malware", "security-fundamentals"]
        ),
        (
            "DEV-SEC-013", "common-network-threats", "What distinguishes a 'worm' from a standard computer 'virus'?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "A traditional virus requires human action (such as executing an infected program or opening an attachment) to spread. A worm is self-replicating and propagates autonomously across networks by exploiting software vulnerabilities.",
            "Contrast computer viruses with autonomous worms.",
            [
                ("A worm can self-replicate and spread automatically across networks without human intervention; a virus requires human execution", True, "Worms exploit network vulnerabilities to spread autonomously."),
                ("A virus only infects computers on Sundays; worms infect computers on Mondays", False, "Malware execution is independent of days of the week."),
                ("A worm is made of biological DNA; a virus is made of silicon", False, "Both are digital software code executing on microprocessors."),
                ("Worms only target mechanical wristwatches", False, "Worms target network-connected computers and servers.")
            ],
            ["threats", "worm", "virus", "malware"]
        ),
        (
            "DEV-SEC-014", "common-network-threats", "What is 'ransomware'?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "Ransomware is a malicious program that encrypts a victim's files, databases, or operating system and demands extortion payments (typically in cryptocurrency) in exchange for the decryption key.",
            "Explain ransomware operations.",
            [
                ("Malware that encrypts victim files and demands an extortion payment in exchange for the decryption key", True, "Ransomware weaponizes encryption to deny access to organizational data."),
                ("A network monitoring utility that optimizes bandwidth usage during business hours", False, "Monitoring tools optimize performance; they do not hold data for ransom."),
                ("A free security patch released by Microsoft to fix operating system bugs", False, "Patches remediate vulnerabilities, while ransomware exploits them."),
                ("A protocol used to assign public IP addresses to cloud servers", False, "DHCP/IPAM manages IP addresses.")
            ],
            ["threats", "ransomware", "malware"]
        ),
        (
            "DEV-SEC-015", "network-devices", "What is an Intrusion Detection System (IDS)?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "An IDS is a passive security monitoring system that analyzes network traffic for known attack signatures or anomalous patterns, generating alerts when suspicious activity is detected without directly blocking packets.",
            "Define the role of an Intrusion Detection System.",
            [
                ("A passive security sensor that monitors traffic for signatures or anomalies and alerts security analysts without in-line blocking", True, "An IDS detects and alerts on threats out-of-band without disrupting traffic."),
                ("A physical metal lock installed on server rack cabinet doors", False, "An IDS is a network traffic inspection system, not a mechanical padlock."),
                ("A software program that automatically deletes all user emails older than 24 hours", False, "Email retention policies manage mailboxes, not intrusion detection."),
                ("A device that converts 120V household electricity into solar energy", False, "Solar inverters manage solar power.")
            ],
            ["ids", "network-monitoring", "security-devices"]
        ),
        (
            "DEV-SEC-016", "network-devices", "What is the primary difference between an Intrusion Detection System (IDS) and an Intrusion Prevention System (IPS)?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 50,
            "An IDS is deployed passively out-of-band and only generates alerts. An IPS is placed directly in-line with network traffic and actively drops or blocks malicious packets in real time.",
            "Contrast IDS passive monitoring with IPS active prevention.",
            [
                ("An IDS passively detects and alerts; an IPS is placed in-line and actively blocks or drops malicious traffic in real time", True, "IDS detects out-of-band; IPS prevents in-line by dropping malicious packets."),
                ("An IDS works only on IPv6; an IPS works only on IPv4", False, "Both systems inspect both IPv4 and IPv6 traffic."),
                ("An IPS requires all users to write their passwords on sticky notes", False, "Writing passwords on sticky notes is an egregious security vulnerability."),
                ("An IDS can only detect traffic sent over satellite dishes", False, "IDS monitors standard wired and wireless LAN/WAN traffic.")
            ],
            ["ids", "ips", "security-devices", "comparison"]
        ),
        (
            "DEV-SEC-017", "common-network-threats", "What is a 'port scan' used for by network administrators and adversaries?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "A port scan systematically probes a target host across a range of port numbers to discover which services are actively listening, which ports are open, and what applications/versions are running.",
            "Explain the purpose of a port scan.",
            [
                ("To probe a host across port numbers to determine which network services are actively listening and open", True, "Port scans identify active services and potential entry points on a host."),
                ("To physically polish the brass contacts inside an Ethernet wall jack", False, "Physical jack maintenance is unrelated to software port scanning."),
                ("To calculate the total electricity consumed by a computer monitor", False, "Electrical meters measure power consumption."),
                ("To automatically upgrade outdated RAM modules on a remote server", False, "Hardware memory upgrades require physical component replacement.")
            ],
            ["reconnaissance", "port-scanning", "security"]
        ),
        (
            "DEV-SEC-018", "firewall-basics", "Which network security concept places public-facing servers (such as web and email servers) in a semi-isolated zone between the untrusted Internet and the secure internal corporate LAN?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 50,
            "A Demilitarized Zone (DMZ) or perimeter network is a subnet that isolates public-facing servers from the internal trusted network, ensuring that a compromised web server cannot directly access internal endpoints.",
            "Define the concept of a Demilitarized Zone (DMZ).",
            [
                ("Demilitarized Zone (DMZ)", True, "A DMZ buffers the private internal corporate network from public-facing external servers."),
                ("Wide Area Network (WAN)", False, "A WAN connects geographically distant corporate sites."),
                ("Virtual Private Network (VPN)", False, "A VPN provides encrypted tunneling across public infrastructure."),
                ("Personal Area Network (PAN)", False, "A PAN connects personal peripherals like Bluetooth headphones.")
            ],
            ["firewall", "dmz", "segmentation", "architecture"]
        ),
        (
            "DEV-SEC-019", "encryption", "What is a 'Virtual Private Network' (VPN) primarily used for?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "A VPN creates an encrypted, secure tunnel over an untrusted public network (like the Internet), enabling remote workers or branch offices to securely access internal private network resources.",
            "Explain the primary security role of a VPN.",
            [
                ("To establish an encrypted tunnel over a public network, securing communications between remote clients and private networks", True, "VPNs protect data confidentiality and integrity across untrusted public networks."),
                ("To increase the physical download bandwidth of an ISP connection by 1000%", False, "VPN encryption adds small overhead and does not increase underlying line speed."),
                ("To replace all physical Ethernet cables with infrared laser pointers", False, "VPN is a logical software tunnel protocol."),
                ("To eliminate the need for computer power cords", False, "Computers still require electrical power.")
            ],
            ["vpn", "encryption", "tunneling", "remote-access"]
        ),
        (
            "DEV-SEC-020", "common-network-threats", "What is 'social engineering' in cybersecurity?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "Social engineering is the psychological manipulation of people into performing actions or divulging confidential information (such as passwords or financial access), bypassing technical defenses.",
            "Define social engineering manipulation tactics.",
            [
                ("Psychological manipulation of individuals into divulging confidential information or granting unauthorized access", True, "Social engineering targets human vulnerabilities rather than software code."),
                ("Writing software programs that organize corporate employee dinner parties", False, "This is event planning, not cyber social engineering."),
                ("Designing high-speed silicon microprocessor chips for server mainframes", False, "That is semiconductor hardware engineering."),
                ("Configuring OSPF routing metrics on enterprise core routers", False, "That is network engineering.")
            ],
            ["social-engineering", "security-fundamentals", "threats"]
        ),
        (
            "DEV-SEC-021", "common-network-threats", "What is a 'Zero-Day' vulnerability in cybersecurity terminology?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "A Zero-Day vulnerability is a security flaw that is unknown to the software vendor or for which no official security patch currently exists, leaving systems vulnerable to immediate exploitation.",
            "Define Zero-Day security vulnerabilities.",
            [
                ("A software security flaw that is known to attackers but has no vendor security patch available yet", True, "Zero-day means defenders have had zero days to patch the vulnerability."),
                ("A computer that has been powered off for exactly zero days", False, "Uptime metrics are unrelated to zero-day vulnerabilities."),
                ("A network cable that transmits zero packets per second", False, "A dead cable is a hardware fault, not a zero-day exploit."),
                ("A software license that is valid for zero days", False, "Software licensing terms are unrelated to cyber zero-days.")
            ],
            ["threats", "zero-day", "vulnerabilities"]
        ),
        (
            "DEV-SEC-022", "encryption", "What is the primary objective of a cryptographic Hash Function (such as SHA-256)?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "A cryptographic hash function converts input data of arbitrary size into a fixed-length output string (digest) in a one-way mathematical operation, primarily used to verify data integrity.",
            "Explain the purpose of cryptographic hash functions.",
            [
                ("To generate a unique fixed-length digital fingerprint of data to verify integrity (ensuring data has not been modified)", True, "Hashes verify integrity; any change to the input completely alters the output digest."),
                ("To encrypt data so it can be easily decrypted using a password", False, "Hashes are strictly one-way mathematical functions and cannot be decrypted."),
                ("To convert standard English text into Japanese audio files", False, "Text-to-speech translation is handled by audio synthesizer software."),
                ("To compress video files so they occupy zero bytes on a hard drive", False, "Compression cannot reduce files to zero bytes.")
            ],
            ["cryptography", "hashing", "integrity", "sha256"]
        ),
        (
            "DEV-SEC-023", "encryption", "Can a standard cryptographic hash (like SHA-256) be 'decrypted' back into its original input text?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 40,
            "No. Cryptographic hash functions are strictly one-way mathematical operations. They produce a fixed-length digest from variable-length input and cannot be reversed or decrypted.",
            "Recognize the one-way nature of cryptographic hash functions.",
            [
                ("No, cryptographic hash functions are strictly one-way functions that cannot be reversed or decrypted", True, "Hashing is one-way for integrity verification, unlike two-way encryption."),
                ("Yes, by using any standard online decryption key generator", False, "Hashes discard information to produce fixed digests and cannot be decrypted."),
                ("Yes, but only on computers running the Linux operating system", False, "Mathematical properties of hash functions are operating system independent."),
                ("Yes, but only if the user types the hash backwards", False, "Typing a hash backwards does not reverse the mathematical hash algorithm.")
            ],
            ["cryptography", "hashing", "one-way"]
        ),
        (
            "DEV-SEC-024", "authentication", "What is the principle of 'Least Privilege' in cybersecurity access control?",
            "SINGLE_CHOICE", "BEGINNER", "UNDERSTAND", 1, 45,
            "The principle of Least Privilege dictates that users, processes, and systems should only be granted the minimum necessary permissions and access rights required to perform their specific job responsibilities.",
            "Explain the principle of Least Privilege.",
            [
                ("Users and systems should only be granted the minimum necessary permissions required to perform their authorized tasks", True, "Least privilege minimizes damage if an account is compromised."),
                ("Every employee in an organization must be given full domain administrator rights on day one", False, "Granting everyone administrator access violates least privilege and is extremely dangerous."),
                ("Computers must be forbidden from accessing the Internet on weekends", False, "Access schedules are policy rules, not the principle of least privilege."),
                ("All user accounts must share the exact same single master password", False, "Sharing passwords destroys individual accountability and audit trails.")
            ],
            ["security-fundamentals", "least-privilege", "access-control"]
        ),
        (
            "DEV-SEC-025", "network-devices", "Which security appliance combines firewall, intrusion prevention, antivirus, web filtering, and spam inspection into a single integrated platform?",
            "SINGLE_CHOICE", "BEGINNER", "REMEMBER", 1, 45,
            "A Unified Threat Management (UTM) appliance or Next-Generation Firewall (NGFW) bundles multiple defensive security capabilities (firewall, IPS, antimalware, content filtering) into a centralized hardware/software appliance.",
            "Identify Unified Threat Management appliances.",
            [
                ("Unified Threat Management (UTM) / Next-Generation Firewall (NGFW)", True, "UTMs integrate diverse security functions into a single manageable appliance."),
                ("Unmanaged 8-port Ethernet switch", False, "Basic switches forward Layer 2 frames without security inspection features."),
                ("Coaxial cable splitter", False, "A cable splitter is passive analog television/cable wiring."),
                ("Analog landline telephone", False, "Analog phones have no cyber threat defense capabilities.")
            ],
            ["security-devices", "utm", "ngfw", "defense"]
        ),
    ]
    save_questions("devices_and_basic_security.json", items)


if __name__ == "__main__":
    generate_ports_and_protocols()
    generate_devices_and_security()
