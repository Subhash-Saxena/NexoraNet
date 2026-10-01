#!/usr/bin/env python3
"""
NexoraNet Advanced Question Bank Generator - Part 1.
Generates:
1. packet_analysis_and_traffic.json (35 questions)
2. network_security_and_defense.json (35 questions)
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "question_bank" / "advanced"
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


def generate_packet_analysis():
    items = [
        (
            "PCAP-001", "packet-structure",
            "An analyst inspects an Ethernet frame in a packet analyzer and observes an EtherType field value of 0x0800. What protocol payload is encapsulated inside this frame?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 45,
            "EtherType 0x0800 identifies an encapsulated IPv4 packet. (In contrast, 0x86DD indicates IPv6, and 0x0806 indicates ARP).",
            "Identify network layer protocols from Layer 2 EtherType values.",
            [
                ("IPv4 (Internet Protocol version 4)", True, "0x0800 is the standard EtherType hex value for IPv4."),
                ("IPv6 (Internet Protocol version 6)", False, "IPv6 is identified by EtherType 0x86DD."),
                ("ARP (Address Resolution Protocol)", False, "ARP is identified by EtherType 0x0806."),
                ("IEEE 802.1Q VLAN Tag", False, "802.1Q tagged frames use EtherType 0x8100.")
            ],
            ["packet-analysis", "ethernet-frames", "ethertype", "wireshark"]
        ),
        (
            "PCAP-002", "packet-structure",
            "In an IPv4 packet header, what protocol number is specified in the 8-bit 'Protocol' field when the encapsulated payload is TCP?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 35,
            "IP Protocol number 6 signifies TCP (Transmission Control Protocol). In contrast, Protocol 17 is UDP, Protocol 1 is ICMP, and Protocol 47 is GRE.",
            "Recall IP header Protocol field numbers.",
            [
                ("Protocol 6", True, "IP Protocol 6 indicates TCP encapsulation."),
                ("Protocol 17", False, "Protocol 17 indicates UDP."),
                ("Protocol 1", False, "Protocol 1 indicates ICMP."),
                ("Protocol 89", False, "Protocol 89 indicates OSPF.")
            ],
            ["packet-analysis", "ip-packets", "protocols", "headers"]
        ),
        (
            "PCAP-003", "wireshark-filtering-concepts",
            "Which Wireshark display filter isolates packets where the TCP SYN flag is set and the ACK flag is cleared (identifying connection initiation attempts)?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 50,
            "The filter 'tcp.flags.syn == 1 && tcp.flags.ack == 0' isolates pure initial SYN packets, useful for identifying new inbound connection attempts and scanning activity.",
            "Construct Wireshark display filters for TCP handshake analysis.",
            [
                ("tcp.flags.syn == 1 && tcp.flags.ack == 0", True, "This filter matches initial connection initiation SYN packets."),
                ("tcp.flags == 0x012", False, "0x012 corresponds to SYN-ACK (SYN=0x002, ACK=0x010)."),
                ("tcp.port == 80 && ip.addr == 1.1.1.1", False, "This filters by IP and port, not by handshake flags."),
                ("http.request.method == 'SYN'", False, "SYN is a Layer 4 TCP flag, not an HTTP Layer 7 method.")
            ],
            ["wireshark", "packet-analysis", "tcp-flags", "display-filters"]
        ),
        (
            "PCAP-004", "tcp-stream-analysis",
            "A SOC analyst examines a packet capture and observes 10 consecutive TCP packets with identical ACK numbers and zero window size progression from a receiver. What condition does this represent?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Receiving consecutive duplicate ACKs indicates that the receiver is missing an intermediate packet (due to packet loss or out-of-order delivery). When three duplicate ACKs are observed, TCP Fast Retransmit is triggered.",
            "Analyze TCP duplicate ACKs in packet captures.",
            [
                ("TCP Duplicate ACKs signaling packet loss and triggering Fast Retransmit", True, "Duplicate ACKs notify the sender that an out-of-order segment arrived and an earlier segment is missing."),
                ("The web browser is loading a high-resolution 8K image", False, "Image loading generates data transfer, not duplicate ACK stalls."),
                ("The server has been infected with an email worm", False, "Duplicate ACKs are standard TCP flow mechanisms indicating dropped packets."),
                ("The client has switched its display monitor to 144Hz refresh rate", False, "Display refresh rates do not affect TCP transport acknowledgments.")
            ],
            ["packet-analysis", "tcp-stream-analysis", "duplicate-acks", "troubleshooting"]
        ),
        (
            "PCAP-005", "dns-packet-analysis",
            "In a packet capture, an analyst observes continuous UDP queries to port 53 where domain names consist of long, random alphanumeric prefixes (e.g. 'a8f7c9b2e1.exfil.attacker.com') carrying high entropy. What threat activity is occurring?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "This pattern indicates DNS Tunneling / Data Exfiltration. Adversaries encode stolen data or command-and-control payloads into the subdomain labels of queries destined for an authoritative nameserver they control.",
            "Identify DNS tunneling and data exfiltration patterns.",
            [
                ("DNS Tunneling used for command-and-control (C2) or data exfiltration", True, "High-entropy, frequent subdomain queries to a single root domain are a classic indicator of DNS tunneling."),
                ("Routine automated Microsoft Windows operating system updates", False, "OS updates use standard HTTPS queries to known CDN domains."),
                ("Normal DHCP IP address lease renewals", False, "DHCP uses UDP ports 67/68 on the local subnet, not external DNS queries."),
                ("The local router synchronizing time with NTP", False, "NTP uses UDP port 123, not port 53 DNS queries.")
            ],
            ["dns", "packet-analysis", "dns-tunneling", "threat-hunting", "soc"]
        ),
        (
            "PCAP-006", "http-packet-analysis",
            "An analyst inspects an unencrypted HTTP POST request in Wireshark and spots the following string in the parameters: 'uname=admin' OR 1=1--'. What web attack is being attempted?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 50,
            "The payload 'admin' OR 1=1--' is a classic SQL Injection (SQLi) authentication bypass exploit intended to manipulate the backend database logic into returning true and logging in without a password.",
            "Recognize SQL injection patterns in HTTP request payloads.",
            [
                ("SQL Injection (SQLi) authentication bypass attack", True, "'OR 1=1--' forces SQL boolean evaluation to true, bypassing password checks."),
                ("Cross-Site Request Forgery (CSRF)", False, "CSRF tricks an authenticated user's browser into submitting forged requests."),
                ("Buffer Overflow attack in the network card firmware", False, "This is an application-layer database injection, not hardware memory corruption."),
                ("DNS Cache Poisoning", False, "This payload targets a web application form, not a DNS resolver cache.")
            ],
            ["packet-analysis", "http", "sql-injection", "application-security", "soc"]
        ),
        (
            "PCAP-007", "tls-traffic",
            "In TLS 1.2 traffic analysis, which packet in the handshake contains the web server's X.509 digital certificate in cleartext?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "In TLS 1.2, the server sends the 'Server Hello' followed by the 'Certificate' message in plaintext before the encrypted session key is derived, allowing passive packet sniffers to inspect the certificate.",
            "Analyze TLS handshake messages in packet captures.",
            [
                ("The Server Hello / Certificate message", True, "In TLS 1.2, the certificate is sent in plaintext; in TLS 1.3, it is encrypted after the Server Hello."),
                ("The Client Key Exchange message", False, "Client Key Exchange contains encrypted premaster secret or parameters."),
                ("The TCP SYN-ACK packet", False, "TCP SYN-ACK is Layer 4; TLS handshake occurs after TCP establishment."),
                ("The HTTP 200 OK response", False, "HTTP traffic is sent inside the encrypted TLS tunnel after handshake completion.")
            ],
            ["tls", "packet-analysis", "certificates", "wireshark"]
        ),
        (
            "PCAP-008", "tls-traffic",
            "What TLS extension allows a client browser to specify the exact hostname it is attempting to connect to during the Client Hello, enabling virtual hosting on HTTPS servers?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 2, 45,
            "Server Name Indication (SNI / RFC 6066) is an extension in the TLS Client Hello where the client specifies the requested domain name, allowing the web server to present the correct SSL certificate among multiple hosted sites.",
            "Recall the role of Server Name Indication (SNI).",
            [
                ("Server Name Indication (SNI)", True, "SNI reveals the target domain in the Client Hello before encryption, allowing multi-tenant certificate selection."),
                ("Session Ticket", False, "Session tickets facilitate fast session resumption."),
                ("Application-Layer Protocol Negotiation (ALPN)", False, "ALPN negotiates application protocols like HTTP/2 or HTTP/3."),
                ("Key Share", False, "Key Share carries Diffie-Hellman public keys in TLS 1.3.")
            ],
            ["tls", "sni", "packet-analysis", "web-hosting"]
        ),
        (
            "PCAP-009", "wireshark-filtering-concepts",
            "Which Wireshark filter restricts the display to traffic involving host 192.168.1.50 communicating over TCP port 443?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 45,
            "In Wireshark display filter syntax, 'ip.addr == 192.168.1.50 && tcp.port == 443' matches packets where either source or destination IP is 192.168.1.50 and either source or destination port is 443.",
            "Construct compound Wireshark display filters.",
            [
                ("ip.addr == 192.168.1.50 && tcp.port == 443", True, "This combines IP address filtering with TCP port filtering."),
                ("host 192.168.1.50 and port 443", False, "This is BPF capture filter syntax (used in tcpdump), not a Wireshark display filter."),
                ("ip.src == 192.168.1.50 || udp.port == 443", False, "This uses logical OR and UDP port instead of TCP."),
                ("ether.addr == 192.168.1.50", False, "Ethernet filters evaluate 48-bit MAC addresses, not IP strings.")
            ],
            ["wireshark", "display-filters", "packet-analysis"]
        ),
        (
            "PCAP-010", "tcp-stream-analysis",
            "An analyst follows a TCP stream in Wireshark and spots the message '220 Microsoft ESMTP MAIL Service ready'. What service was contacted?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 45,
            "Banner '220 ... ESMTP ... ready' is the standard greeting banner returned by a Simple Mail Transfer Protocol (SMTP) server on TCP port 25 or 587.",
            "Identify application protocols from service greeting banners.",
            [
                ("SMTP (Simple Mail Transfer Protocol)", True, "ESMTP banner 220 confirms an active mail exchange service."),
                ("FTP (File Transfer Protocol)", False, "FTP banners typically start with '220 FTP server ready'."),
                ("SSH (Secure Shell)", False, "SSH banners begin with 'SSH-2.0-...'."),
                ("HTTP (Hypertext Transfer Protocol)", False, "HTTP servers respond to requests with 'HTTP/1.1 200 OK', not unsolicited 220 banners.")
            ],
            ["packet-analysis", "smtp", "banners", "service-identification"]
        ),
        (
            "PCAP-011", "tcp-stream-analysis",
            "In packet forensics, what does a 'TCP Zero Window' warning from a destination host signify?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 55,
            "A TCP Zero Window advertisement informs the sender that the receiver's TCP buffer is completely full and cannot accept any more bytes. The sender must pause transmission until the receiver processes data and sends a Window Update.",
            "Analyze TCP Zero Window advertisements in packet traces.",
            [
                ("The receiver's network buffer is completely full, halting data transmission until buffer space is cleared", True, "Zero Window signals severe application backpressure where data is arriving faster than the app can read it."),
                ("The physical cable has disconnected from the wall", False, "Zero Window is an active TCP segment sent across a functional connection."),
                ("The server has revoked its SSL certificate", False, "Zero Window is a Layer 4 flow control condition, not a TLS certificate event."),
                ("The client has closed all open browser windows", False, "Browser UI state does not generate transport zero window frames.")
            ],
            ["packet-analysis", "tcp", "zero-window", "troubleshooting", "performance"]
        ),
        (
            "PCAP-012", "packet-structure",
            "In an IPv4 packet header, what is the purpose of the 'Don't Fragment' (DF) bit?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "The DF bit in the IPv4 Flags field instructs intermediate routers that the packet must NOT be fragmented. If the packet exceeds a link's MTU, the router drops it and returns an ICMP Fragmentation Needed message (used in Path MTU Discovery).",
            "Explain the role of the IPv4 Don't Fragment flag.",
            [
                ("It instructs routers not to fragment the packet; if it exceeds link MTU, the packet is dropped and an ICMP error is returned", True, "DF bit is central to Path MTU Discovery (PMTUD) to prevent fragmentation overhead."),
                ("It instructs the receiving CPU to delete the packet immediately upon receipt", False, "DF bit manages fragmentation, not packet deletion."),
                ("It indicates that the packet contains audio data rather than text", False, "IP flags do not classify media MIME types."),
                ("It ensures that passwords are encrypted using SHA-256", False, "IP header flags provide routing instructions, not cryptographic encryption.")
            ],
            ["ipv4", "fragmentation", "df-bit", "pmtud"]
        ),
        (
            "PCAP-013", "packet-structure",
            "What security risk is associated with IP fragmentation in enterprise networks?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Adversaries can exploit IP fragmentation (e.g. Tiny Fragment attacks, Teardrop, overlapping fragments) to bypass stateless packet filters or evade NIDS inspection by splitting attack signatures across fragment boundaries.",
            "Analyze security vulnerabilities related to IP packet fragmentation.",
            [
                ("Adversaries can split attack signatures across fragment boundaries to evade detection by legacy NIDS and firewalls", True, "Fragmentation evasion splits payloads so sensors that don't reassemble fragments miss the malicious signature."),
                ("Fragments cause copper Ethernet cables to overheat and melt", False, "Fragmentation is a software protocol handling event with no physical cable damage."),
                ("Fragments convert all IPv4 packets into unencrypted Bluetooth signals", False, "Fragmented packets remain on their routed IP medium."),
                ("Fragments prevent web servers from running operating system updates", False, "Fragment reassembly is an ordinary kernel network stack function.")
            ],
            ["packet-analysis", "fragmentation", "evasion", "security", "nids"]
        ),
        (
            "PCAP-014", "dns-packet-analysis",
            "An analyst reviews DNS query logs and spots thousands of queries for 'ANY' records directed to open resolvers with a spoofed target victim IP. What attack is being executed?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "This is a DNS Amplification Distributed Denial of Service (DDoS) attack. Small spoofed requests eliciting massive responses (using 'ANY' queries with EDNS0) reflect and amplify flood traffic onto the victim IP.",
            "Identify DNS amplification and reflection DDoS attacks.",
            [
                ("DNS Amplification / Reflection DDoS attack", True, "DNS amplification uses small spoofed queries to generate massive reflected responses targeting a victim."),
                ("ARP Poisoning Man-in-the-Middle attack", False, "ARP poisoning occurs locally on Layer 2, not over public DNS resolvers."),
                ("SQL Injection attack against an authoritative database", False, "DNS amplification targets network link saturation, not database query logic."),
                ("Pass-the-Hash credential theft", False, "Pass-the-hash is a Windows lateral movement technique.")
            ],
            ["dns", "ddos", "amplification", "reflection", "soc"]
        ),
        (
            "PCAP-015", "wireshark-filtering-concepts",
            "Which Wireshark display filter will display only HTTP requests that generated a 404 (Not Found) or 500 (Internal Server Error) response?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 50,
            "The filter 'http.response.code == 404 || http.response.code == 500' isolates responses matching either specific HTTP status error code.",
            "Construct Wireshark filters for HTTP status troubleshooting.",
            [
                ("http.response.code == 404 || http.response.code == 500", True, "This filter matches either 404 or 500 response codes."),
                ("tcp.port == 404 && tcp.port == 500", False, "404 and 500 are HTTP status codes, not TCP port numbers."),
                ("ip.error == 404", False, "IP headers do not contain HTTP status codes."),
                ("dns.flags.rcode == 404", False, "DNS response codes use RCODE values (e.g. NXDOMAIN), not HTTP codes.")
            ],
            ["wireshark", "http", "display-filters", "troubleshooting"]
        ),
        (
            "PCAP-016", "tcp-stream-analysis",
            "What does a 'TCP Spurious Retransmission' in Wireshark analysis indicate?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "A spurious retransmission occurs when a sender retransmits a segment that the receiver had already received and acknowledged, typically caused by premature RTO expiration due to sudden network latency spikes.",
            "Explain TCP spurious retransmissions.",
            [
                ("The sender retransmitted data that had already been acknowledged, typically caused by premature timer expiration during latency spikes", True, "Spurious retransmissions waste bandwidth when the sender's RTO timer fires before delayed ACKs arrive."),
                ("The packet was generated by an unauthorized malware process", False, "Spurious retransmissions are standard transport behavior under sudden latency jitter."),
                ("The network card is executing a DDoS attack against the switch", False, "It indicates normal protocol recovery under delay."),
                ("The receiver sent a forged MAC address to the router", False, "Spurious retransmissions are Layer 4 sequence timer events.")
            ],
            ["tcp", "spurious-retransmission", "troubleshooting", "packet-analysis"]
        ),
        (
            "PCAP-017", "packet-structure",
            "Where in an IPv4 packet header is the Differentiated Services Code Point (DSCP) field located, and what is its purpose?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "DSCP is a 6-bit field located in the former Type of Service (ToS) byte of the IPv4 header (and Traffic Class in IPv6), used for Quality of Service (QoS) classification to prioritize voice, video, or critical traffic.",
            "Explain the function and location of the DSCP field.",
            [
                ("In the former Type of Service (ToS) byte; it classifies and prioritizes packets for Quality of Service (QoS)", True, "DSCP marks traffic priority (e.g. EF for voice, AF for video) across routers."),
                ("In the TCP options field; it sets the screen brightness of the receiver", False, "DSCP is an IP header field for QoS, not display settings."),
                ("In the Ethernet trailer; it encrypts the user's password", False, "DSCP is in the Layer 3 header."),
                ("In the DNS question section; it counts the characters in the domain name", False, "DSCP is a network layer packet header field.")
            ],
            ["ipv4", "dscp", "qos", "packet-structure"]
        ),
        (
            "PCAP-018", "packet-structure",
            "In an IPv6 header, what field replaces the IPv4 'Time to Live' (TTL) field?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 35,
            "In IPv6, the field is explicitly named 'Hop Limit' (8 bits). It functions identically to IPv4 TTL by decrementing by 1 at each router hop and dropping the packet at 0.",
            "Recall IPv6 header fields corresponding to IPv4 TTL.",
            [
                ("Hop Limit", True, "IPv6 renamed TTL to 'Hop Limit' to accurately reflect that it counts router hops."),
                ("Flow Label", False, "Flow Label (20 bits) identifies specific packet sequences requiring identical handling."),
                ("Next Header", False, "Next Header specifies the protocol encapsulated immediately following the IPv6 header."),
                ("Traffic Class", False, "Traffic Class corresponds to IPv4 Type of Service / DSCP.")
            ],
            ["ipv6", "hop-limit", "ttl", "headers"]
        ),
        (
            "PCAP-019", "packet-structure",
            "In an IPv6 header, what field replaces the IPv4 'Protocol' field to specify the encapsulated payload or extension header?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 35,
            "The 'Next Header' field in IPv6 serves the dual purpose of identifying either an IPv6 extension header (such as Routing or Fragmentation) or the transport layer protocol (such as TCP=6 or UDP=17).",
            "Identify the IPv6 Next Header field.",
            [
                ("Next Header", True, "Next Header specifies the type of the next header or upper-layer protocol."),
                ("Protocol ID", False, "Protocol is the field name in IPv4, not IPv6."),
                ("EtherType", False, "EtherType is a Layer 2 Ethernet field."),
                ("Payload Type", False, "Payload type is used in RTP, not IPv6 headers.")
            ],
            ["ipv6", "next-header", "packet-structure"]
        ),
        (
            "PCAP-020", "wireshark-filtering-concepts",
            "Which Wireshark display filter will display all ARP requests and replies occurring on a network capture?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 1, 35,
            "Typing 'arp' in the Wireshark display filter bar filters packets exclusively to Address Resolution Protocol traffic.",
            "Filter ARP traffic in Wireshark.",
            [
                ("arp", True, "The display filter 'arp' isolates all ARP broadcast requests and unicast replies."),
                ("ip.protocol == 24", False, "ARP operates directly over Ethernet (EtherType 0x0806) and does not use IP protocol numbers."),
                ("tcp.port == arp", False, "ARP does not use TCP."),
                ("ether.broadcast == true", False, "This is not standard Wireshark syntax for ARP filtering.")
            ],
            ["arp", "wireshark", "display-filters"]
        ),
        (
            "PCAP-021", "tcp-stream-analysis",
            "When analyzing a suspicious TCP stream in Wireshark, an analyst sees plaintext commands like 'whoami', 'net user', and 'systeminfo' followed by command prompt outputs. What has been captured?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 55,
            "This indicates an unencrypted reverse shell or bind shell session, where an adversary gained remote command execution on a victim machine and is running discovery commands over an interactive terminal.",
            "Analyze interactive command shell sessions in packet captures.",
            [
                ("An interactive reverse shell or remote command-line session conducted by an adversary", True, "Plaintext execution of host discovery commands over TCP indicates an active compromise shell."),
                ("Normal background synchronization of the computer clock with NTP", False, "NTP synchronizes timestamps via binary UDP, not interactive OS command lines."),
                ("A routine automated backup of user photo albums to Google Drive", False, "Cloud backups transfer binary data over HTTPS."),
                ("The operating system scanning for Wi-Fi printer drivers", False, "Printer discovery uses SSDP/mDNS, not interactive shell commands.")
            ],
            ["packet-analysis", "reverse-shell", "soc", "threat-hunting", "investigation"]
        ),
        (
            "PCAP-022", "dns-packet-analysis",
            "In DNS response analysis, what does a response code (RCODE) of 'NXDOMAIN' (Name Error / RCODE 3) indicate?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 40,
            "NXDOMAIN indicates that the queried domain name does not exist in the DNS hierarchy (the authoritative server has no record for the requested name).",
            "Interpret DNS NXDOMAIN response codes.",
            [
                ("The queried domain name does not exist in the DNS namespace", True, "NXDOMAIN proves the domain has no active DNS record."),
                ("The server refused to process the query due to lack of payment", False, "Refusal returns REFUSED (RCODE 5)."),
                ("The server's physical hard drive has crashed", False, "NXDOMAIN is an authoritative protocol response confirming non-existence of the name."),
                ("The client entered an invalid credit card number", False, "DNS protocol does not process payment credentials.")
            ],
            ["dns", "nxdomain", "rcode", "troubleshooting"]
        ),
        (
            "PCAP-023", "dns-packet-analysis",
            "A security analyst observes a massive surge in NXDOMAIN responses (e.g. hundreds per second) generated by a single internal workstation querying random-looking domain names. What malware behavior does this pattern indicate?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "This pattern is characteristic of malware utilizing a Domain Generation Algorithm (DGA). The malware generates hundreds of pseudo-random domains daily to contact its C2 server; most are unregistered (producing NXDOMAINs) until it finds the active domain registered by the attacker.",
            "Identify Domain Generation Algorithm (DGA) network indicators.",
            [
                ("Domain Generation Algorithm (DGA) used by malware to locate active command-and-control servers", True, "DGAs produce heavy NXDOMAIN bursts because the majority of generated domains are unregistered."),
                ("A user rapidly typing search queries into Google", False, "Search engine queries query google.com, not hundreds of non-existent domains."),
                ("The workstation installing an official Microsoft Windows cumulative update", False, "Windows update queries fixed, registered Microsoft domains."),
                ("The local switch experiencing a broadcast storm", False, "Switch loops circulate Layer 2 frames, not DNS NXDOMAIN responses.")
            ],
            ["dns", "dga", "c2", "malware", "threat-hunting", "soc"]
        ),
        (
            "PCAP-024", "http-packet-analysis",
            "An analyst inspects HTTP traffic and notices that a client's 'User-Agent' header is string 'sqlmap/1.5.2#stable'. What does this indicate?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 45,
            "This indicates that an automated security scanning or exploitation tool (specifically sqlmap, a popular automated SQL injection tool) is being run against the web application.",
            "Identify security scanner User-Agent signatures in HTTP headers.",
            [
                ("An automated SQL injection scanning tool (sqlmap) is actively probing or exploiting the web application", True, "Default tool signatures in User-Agent headers identify automated scanner activity."),
                ("A standard user is viewing the website using Google Chrome", False, "Chrome uses 'Mozilla/5.0 ... Chrome/...' User-Agent strings."),
                ("The web server has successfully created a daily database backup", False, "User-Agent is a client request header, not a server backup status."),
                ("The client's computer monitor has a cracked screen", False, "User-Agent reflects client software identity, not hardware screen condition.")
            ],
            ["http", "user-agent", "sqlmap", "reconnaissance", "soc"]
        ),
        (
            "PCAP-025", "packet-structure",
            "What is the maximum standard Transmission Unit (MTU) size for standard Ethernet version 2 frames on local area networks?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 35,
            "The standard Ethernet v2 MTU is 1500 bytes (referring to the maximum IP packet size excluding the 14-byte Ethernet header and 4-byte FCS trailer).",
            "Recall standard Ethernet MTU size.",
            [
                ("1500 bytes", True, "Standard Ethernet MTU is 1500 bytes."),
                ("9000 bytes", False, "9000 bytes is a Jumbo Frame size used in datacenters."),
                ("576 bytes", False, "576 bytes is the minimum IPv4 reassembly buffer size."),
                ("65535 bytes", False, "65535 bytes is the theoretical maximum size of an IPv4 packet.")
            ],
            ["ethernet", "mtu", "packet-structure"]
        ),
        (
            "PCAP-026", "wireshark-filtering-concepts",
            "Which BPF (Berkeley Packet Filter) capture filter syntax used in tcpdump or Wireshark captures traffic on port 80 or port 443 while excluding traffic to host 10.0.0.1?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 50,
            "In BPF capture filter syntax: '(port 80 or port 443) and not host 10.0.0.1'.",
            "Construct BPF capture filters for tcpdump.",
            [
                ("(port 80 or port 443) and not host 10.0.0.1", True, "This correctly combines port matching with a host exclusion in standard BPF syntax."),
                ("tcp.port in {80, 443} && ip.addr != 10.0.0.1", False, "This is Wireshark display filter syntax, not a BPF capture filter."),
                ("filter port 80, 443 exclude 10.0.0.1", False, "This is pseudocode, not BPF syntax."),
                ("iptables -A INPUT -p tcp --dport 80 -j DROP", False, "This is a Linux firewall command, not a packet capture filter.")
            ],
            ["bpf", "tcpdump", "wireshark", "capture-filters"]
        ),
        (
            "PCAP-027", "tcp-stream-analysis",
            "In a packet capture, what does the presence of the TCP flag combination 'ACK, PSH' indicate during an active data session?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 40,
            "ACK, PSH indicates that the sender is simultaneously acknowledging data previously received (ACK) and delivering an immediate block of payload data that should be pushed straight to the receiving application (PSH).",
            "Interpret the PSH-ACK TCP flag combination.",
            [
                ("The segment acknowledges previously received data and contains payload data that should be pushed immediately to the application", True, "PSH-ACK is the standard flag combination used during active application data exchange."),
                ("The connection is being terminated by the server", False, "Connection termination uses the FIN flag."),
                ("The router has detected an electrical short circuit", False, "Transport flags manage software protocol flows, not electrical shorts."),
                ("The user has changed their password", False, "Transport flags do not indicate credential changes.")
            ],
            ["tcp", "psh-ack", "packet-analysis", "data-transfer"]
        ),
        (
            "PCAP-028", "packet-structure",
            "What is the function of the 3-bit 'Flags' field in the IPv4 header?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 40,
            "The IPv4 Flags field controls and identifies fragmentation: Bit 0 is reserved (must be 0), Bit 1 is the DF (Don't Fragment) bit, and Bit 2 is the MF (More Fragments) bit.",
            "Recall the bit definitions of the IPv4 Flags field.",
            [
                ("Bit 0: Reserved, Bit 1: Don't Fragment (DF), Bit 2: More Fragments (MF)", True, "These 3 bits control and track packet fragmentation across IP networks."),
                ("Bit 0: SYN, Bit 1: ACK, Bit 2: FIN", False, "SYN, ACK, and FIN are Layer 4 TCP flags, not IPv4 header flags."),
                ("Bit 0: Encrypt, Bit 1: Decrypt, Bit 2: Delete", False, "IP header flags do not perform cryptographic operations."),
                ("Bit 0: Red, Bit 1: Green, Bit 2: Blue", False, "Network headers manage routing logic, not color display.")
            ],
            ["ipv4", "flags", "df", "mf", "fragmentation"]
        ),
        (
            "PCAP-029", "http-packet-analysis",
            "An analyst inspects an HTTP request and observes the header 'Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM='. How is this credential string protected in transit?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 50,
            "'Basic' HTTP authentication encodes credentials using Base64, which is NOT encryption—it is merely an encoding scheme that can be instantly decoded back to plaintext ('admin:password123') by anyone who captures the packet.",
            "Evaluate HTTP Basic Authentication security.",
            [
                ("It is merely Base64-encoded (not encrypted) and can be immediately decoded back to plaintext by anyone intercepting the traffic", True, "Base64 is an encoding format, offering zero confidentiality; without HTTPS, credentials are exposed in plaintext."),
                ("It is encrypted with military-grade AES-256 that cannot be broken for 1000 years", False, "Base64 encoding is not encryption."),
                ("It is protected by a hardware quantum key", False, "Base64 is a standard ASCII text encoding algorithm."),
                ("It is permanently unreadable even by the destination web server", False, "The server decodes it directly to check username and password.")
            ],
            ["http", "basic-auth", "base64", "packet-analysis", "security"]
        ),
        (
            "PCAP-030", "dns-packet-analysis",
            "What does a DNS response containing an answer in the 'Authority' section pointing to a 'SOA' record with no A records in the 'Answer' section indicate?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "A response containing an SOA in the authority section with zero answers indicates a negative response: either NXDOMAIN (domain name does not exist) or NODATA (domain exists, but the requested record type does not exist).",
            "Interpret negative DNS response structures.",
            [
                ("A negative response indicating the domain name or requested record type does not exist (NXDOMAIN or NODATA)", True, "The SOA record provides the negative caching TTL for resolvers to cache the non-existence of the record."),
                ("The web server has accepted a credit card payment", False, "DNS responses carry name resolution records, not payment acknowledgments."),
                ("The DNS query was encrypted using AES-GCM", False, "Standard DNS queries and responses are unencrypted."),
                ("The client computer has been disconnected from the electrical power grid", False, "The client received an active network response.")
            ],
            ["dns", "soa", "negative-caching", "troubleshooting"]
        ),
        (
            "PCAP-031", "packet-structure",
            "In packet dissection, what protocol is indicated by EtherType value 0x86DD?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 35,
            "EtherType 0x86DD standardly identifies encapsulated Internet Protocol version 6 (IPv6) packets inside Ethernet frames.",
            "Identify the IPv6 EtherType value.",
            [
                ("IPv6 (Internet Protocol version 6)", True, "0x86DD identifies IPv6 payloads."),
                ("IPv4", False, "IPv4 is 0x0800."),
                ("ARP", False, "ARP is 0x0806."),
                ("MPLS", False, "MPLS unicast is 0x8847.")
            ],
            ["ipv6", "ethertype", "packet-structure"]
        ),
        (
            "PCAP-032", "wireshark-filtering-concepts",
            "Which Wireshark display filter will find all packets containing the plaintext string 'password' anywhere in their payload data?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 50,
            "The filter 'frame contains \"password\"' scans the entire frame (headers and payload) for the specified case-sensitive ASCII text string.",
            "Search for string patterns in Wireshark packet captures.",
            [
                ("frame contains \"password\"", True, "The 'contains' operator searches for ASCII or hex sequences across the entire frame."),
                ("ip.payload == password", False, "This is invalid filter syntax."),
                ("search \"password\"", False, "This is not standard Wireshark display filter syntax."),
                ("tcp.flags == password", False, "TCP flags are numeric bit masks, not text strings.")
            ],
            ["wireshark", "string-search", "packet-analysis", "forensics"]
        ),
        (
            "PCAP-033", "tcp-stream-analysis",
            "An analyst observes a TCP session where the server responds to every client data packet with an immediate ACK, but the receiver's window size remains constant at 0 for several minutes. What should the analyst investigate?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 55,
            "A persistent Zero Window condition accompanied by regular zero window probes indicates that the receiving server application process has hung, deadlocked, or crashed, preventing it from consuming data from its kernel buffer.",
            "Diagnose persistent TCP Zero Window deadlocks.",
            [
                ("The receiving application process has deadlocked or crashed, leaving the kernel buffer unable to drain", True, "When the application stops calling recv()/read(), the buffer fills and stays at zero indefinitely."),
                ("The Ethernet switch has run out of physical RJ-45 copper ports", False, "Zero window is an application buffer consumption failure on the endpoint."),
                ("The user's Wi-Fi router has changed its wireless password", False, "The TCP connection is actively established and transmitting ACKs."),
                ("The client has upgraded its operating system to Windows 11", False, "Zero window reflects application thread stalls, not OS upgrades.")
            ],
            ["tcp", "zero-window", "troubleshooting", "application-hang"]
        ),
        (
            "PCAP-034", "dns-packet-analysis",
            "What is the difference between an Authoritative Answer and a Non-Authoritative Answer in a DNS response packet?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "An Authoritative Answer (AA flag set in DNS header) comes directly from the nameserver that permanently hosts the master zone records for that domain. A Non-Authoritative Answer comes from a resolver's temporary cache.",
            "Distinguish authoritative and non-authoritative DNS answers.",
            [
                ("Authoritative answers come from the server hosting the actual zone file; non-authoritative answers are served from a resolver's cache", True, "The AA bit indicates whether the response originated from the authoritative zone owner or a recursive cache."),
                ("Authoritative answers are encrypted; non-authoritative answers are unencrypted", False, "Both are unencrypted in standard DNS."),
                ("Authoritative answers only work on smartphones", False, "DNS resolution is universal across all devices."),
                ("Non-authoritative answers are always malicious malware attacks", False, "Cached non-authoritative answers are normal, expected DNS operations.")
            ],
            ["dns", "authoritative", "caching", "dns-headers"]
        ),
        (
            "PCAP-035", "packet-structure",
            "What is the minimum physical Ethernet frame size on wire (including destination MAC, source MAC, EtherType, payload, and FCS)?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 40,
            "Under IEEE 802.3, the minimum Ethernet frame size is 64 bytes (14 bytes header + 46 bytes minimum payload + 4 bytes FCS). If a payload is smaller than 46 bytes, padding bytes (zeros) are appended.",
            "Recall minimum Ethernet frame size specifications.",
            [
                ("64 bytes (frames with smaller payloads are padded)", True, "64 bytes is the minimum frame size required for CSMA/CD collision detection slot time."),
                ("1500 bytes", False, "1500 bytes is the standard maximum payload MTU, not the minimum frame size."),
                ("20 bytes", False, "20 bytes is the minimum size of an IP header alone."),
                ("32 bytes", False, "32 bytes is the bit size of an IPv4 address.")
            ],
            ["ethernet", "frame-size", "padding", "csma-cd"]
        ),
    ]
    save_questions("packet_analysis_and_traffic.json", items)


def generate_network_security_defense():
    items = [
        (
            "SEC-DEF-001", "vlan-security",
            "In Private VLAN (PVLAN) architecture, what is the behavior of an 'Isolated' port?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "An Isolated port has complete Layer 2 separation: it can communicate ONLY with promiscuous ports (such as the default gateway router). It cannot communicate with any other isolated port or community port on the same switch.",
            "Explain Private VLAN Isolated port behavior.",
            [
                ("It can only communicate with Promiscuous ports; it cannot communicate with any other isolated or community ports in the VLAN", True, "Isolated ports prevent lateral communication between servers within the same subnet, enforcing microsegmentation."),
                ("It can communicate with all devices on the Internet without a router", False, "Isolated ports restrict Layer 2 traffic, requiring a router to reach other subnets."),
                ("It automatically encrypts all hard drives on connected servers", False, "PVLAN is a Layer 2 switch forwarding control, not disk encryption."),
                ("It is a port that has been physically severed with wire cutters", False, "Isolated is a logical switch configuration mode.")
            ],
            ["vlan-security", "private-vlans", "isolated-ports", "microsegmentation"]
        ),
        (
            "SEC-DEF-002", "vlan-security",
            "In Private VLAN (PVLAN) architecture, what is the role of a 'Promiscuous' port?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A Promiscuous port connects to an upstream device (such as a default gateway router, firewall, or shared backup server) and can communicate bidirectionally with all ports in the PVLAN: isolated, community, and promiscuous.",
            "Explain Private VLAN Promiscuous port behavior.",
            [
                ("It can communicate with all ports in the Private VLAN, typically connected to default gateway routers or firewalls", True, "Promiscuous ports serve as the gateway exit for all isolated and community ports."),
                ("It secretly transmits user passwords to public advertising companies", False, "Promiscuous ports forward authorized network traffic."),
                ("It converts copper cabling into fiber-optic lasers", False, "PVLAN is a switch software forwarding rule."),
                ("It automatically shuts down the switch when an alert is detected", False, "Promiscuous ports operate continuously.")
            ],
            ["vlan-security", "private-vlans", "promiscuous-port", "defense"]
        ),
        (
            "SEC-DEF-003", "stateful-vs-stateless-filtering",
            "How does a stateful firewall protect against TCP out-of-sequence or unexpected ACK scanning attacks?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "A stateful firewall tracks sequence numbers and connection state in its state table. If an incoming packet has an ACK flag but does not correspond to an established session in its state table, the firewall immediately drops the packet.",
            "Explain how stateful inspection neutralizes unsolicited ACK packets.",
            [
                ("It drops incoming ACK packets that do not match an existing, established session in its state table", True, "Stateful tracking prevents ACK scanning and session spoofing by verifying prior handshake state."),
                ("It converts the ACK packet into an email attachment", False, "Firewalls filter transit packets."),
                ("It increases the physical download speed of the server", False, "Stateful filtering performs security checks, not bandwidth acceleration."),
                ("It shuts down all switch ports across the entire building", False, "Stateful drops are executed per-packet without affecting switch hardware.")
            ],
            ["firewall", "stateful-inspection", "tcp-ack-scan", "defense"]
        ),
        (
            "SEC-DEF-004", "ids-ips-advanced",
            "What is the difference between Signature-Based detection and Anomaly-Based (Behavioral) detection in an NIDS/NIPS?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Signature-based detection matches traffic against a database of known attack patterns/rules (like antivirus signatures). Anomaly-based detection compares traffic against a statistical baseline of normal network behavior, alerting on deviations.",
            "Contrast signature-based and anomaly-based intrusion detection.",
            [
                ("Signature-based matches known attack patterns; anomaly-based detects statistical deviations from a baseline of normal behavior", True, "Signatures catch known threats with low false positives; anomaly detection can identify unknown zero-day attacks."),
                ("Signature-based requires physical paper signatures; anomaly-based uses digital computers", False, "Both are digital software algorithms executing on network sensors."),
                ("Anomaly-based only works on computers located in Antarctica", False, "Both detection modes are deployed globally across enterprise networks."),
                ("Signature-based is illegal under modern cybersecurity regulations", False, "Signature-based detection (e.g. Snort/Suricata) is an industry foundation.")
            ],
            ["ids", "ips", "signature-detection", "anomaly-detection", "detection-engineering"]
        ),
        (
            "SEC-DEF-005", "ids-ips-advanced",
            "What is a major limitation of Signature-Based detection in enterprise intrusion defense?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Signature-based detection cannot detect zero-day attacks, new attack variants, or polymorphic malware for which no pre-existing signature has been written and loaded into the detection engine.",
            "Identify limitations of signature-based detection.",
            [
                ("It cannot detect novel zero-day attacks or polymorphic threats that lack pre-authored signatures", True, "Signatures require prior knowledge of the threat; zero-days bypass signature matching."),
                ("It requires servers to operate without electrical power", False, "Security sensors require standard server power."),
                ("It formats the user's hard drive whenever an alert triggers", False, "Sensors log alerts; they do not format drives."),
                ("It can only run on Windows 98", False, "Modern detection engines execute on Linux, BSD, and specialized network OS appliances.")
            ],
            ["ids", "signatures", "zero-day", "limitations"]
        ),
        (
            "SEC-DEF-006", "network-segmentation-advanced",
            "What is a 'Jump Box' (or Bastion Host) in secure network architecture?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A Jump Box is a hardened, highly monitored intermediate server that administrators must log into first (via MFA) before they are permitted to access sensitive servers in isolated internal management zones or production datacenters.",
            "Explain the architectural role of a Jump Box.",
            [
                ("A hardened, audited server used as a single secure gateway for administrators to access sensitive internal networks", True, "Jump boxes centralize administrative access, enforce MFA, and record comprehensive audit session logs."),
                ("A trampoline installed in the datacenter for physical exercise", False, "A jump box is a hardened server, not gym equipment."),
                ("A router that automatically changes its IP address every 5 seconds", False, "Jump boxes have static IP addresses and strict DNS records."),
                ("A tool used to download cracked software games from the Internet", False, "Jump boxes are core enterprise defense infrastructure.")
            ],
            ["network-segmentation", "bastion-host", "jump-box", "access-control"]
        ),
        (
            "SEC-DEF-007", "network-segmentation-advanced",
            "What is the 'Zero Trust' network architecture model (NIST SP 800-207) primarily founded upon?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Zero Trust operates on the principle of 'Never Trust, Always Verify': no user, device, or workload inside or outside the perimeter is implicitly trusted. Every access request must be explicitly authenticated, authorized, and encrypted.",
            "Explain the core philosophy of Zero Trust architecture.",
            [
                ("'Never Trust, Always Verify' — treating internal network traffic as untrusted and requiring continuous authentication and microsegmentation", True, "Zero Trust eliminates implicit trust based on physical location behind a firewall."),
                ("Trusting all internal employees completely and removing all corporate passwords", False, "Zero Trust strictly enforces continuous verification and least privilege."),
                ("Disconnecting all computers from the Internet permanently", False, "Zero Trust enables secure cloud and mobile operations across untrusted networks."),
                ("Replacing all software firewalls with physical concrete barriers", False, "Zero Trust is an identity- and context-aware security architecture.")
            ],
            ["zero-trust", "nist-800-207", "security-architecture", "defense"]
        ),
        (
            "SEC-DEF-008", "ipv6-security",
            "What security risk is introduced by Rogue IPv6 Router Advertisements (RA) on a dual-stack local network?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "In IPv6 Neighbor Discovery Protocol (NDP), rogue Router Advertisements can cause dual-stack clients to automatically configure an attacker's rogue IPv6 gateway and DNS, silently hijacking all client traffic via IPv6 Man-in-the-Middle.",
            "Analyze the threat of rogue IPv6 Router Advertisements.",
            [
                ("Attackers can broadcast false IPv6 RAs, causing dual-stack hosts to route traffic through an attacker-controlled IPv6 gateway (MitM)", True, "Rogue RAs exploit default IPv6 auto-configuration (SLAAC) to hijack traffic even on networks thought to be IPv4-only."),
                ("Rogue RAs immediately delete all files from the victim's hard drive", False, "Rogue RAs alter network gateway routes, not local disk files."),
                ("Rogue RAs cause optical fiber cables to turn into copper wires", False, "Protocol advertisements do not alter physical cabling material."),
                ("Rogue RAs permanently damage the computer's CPU chip", False, "RAs are standard Layer 3 ICMPv6 messages.")
            ],
            ["ipv6-security", "rogue-ra", "slaac", "ndp-spoofing", "mitm"]
        ),
        (
            "SEC-DEF-009", "ipv6-security",
            "Which switch security feature mitigates Rogue IPv6 Router Advertisements by dropping unauthorized RA messages from untrusted switch access ports?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 2, 45,
            "IPv6 RA Guard (RFC 6105) is a Layer 2 switch security feature that inspects incoming ICMPv6 Router Advertisement messages on untrusted access ports and blocks them, permitting RAs only on authorized router trunk ports.",
            "Identify switch defensive features against rogue IPv6 RAs.",
            [
                ("IPv6 RA Guard", True, "IPv6 RA Guard drops unauthorized Router Advertisement messages on access ports."),
                ("Dynamic ARP Inspection (DAI)", False, "DAI protects IPv4 ARP, not IPv6 NDP."),
                ("BGP Flowspec", False, "BGP Flowspec is for WAN DDoS mitigation on core routers."),
                ("Port Fast", False, "PortFast bypasses listening/learning states in STP for immediate access.")
            ],
            ["ipv6-security", "ra-guard", "switch-security", "defense"]
        ),
        (
            "SEC-DEF-010", "ids-ips-advanced",
            "What is 'Traffic Normalization' performed by an inline Intrusion Prevention System (IPS)?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Traffic normalization reassembles packet fragments, resolves overlapping TCP sequence segments, strips invalid flags, and normalizes protocols so that the IPS and the destination target interpret the packet stream identically, neutralizing evasion attacks.",
            "Explain traffic normalization in inline IPS engines.",
            [
                ("Reassembling fragments and resolving protocol ambiguities so the sensor and target interpret traffic identically, defeating evasion", True, "Normalization strips evasion tricks like overlapping TCP segments or malformed headers before inspection."),
                ("Converting all video files into low-resolution black-and-white graphics", False, "Normalization refers to protocol header and fragment standardization."),
                ("Automatically paying the company's electricity utility bill", False, "Normalization is a cryptographic and protocol inspection process."),
                ("Replacing all user passwords with random numbers", False, "Normalization does not alter user credentials.")
            ],
            ["ips", "normalization", "evasion-defense", "detection-engineering"]
        ),
        (
            "SEC-DEF-011", "firewall-architecture",
            "In enterprise network firewall architecture, what is a 'Screened Subnet' design?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A Screened Subnet (DMZ) architecture uses two firewall tiers (an external perimeter firewall and an internal core firewall) or a three-legged firewall to isolate DMZ public servers from both the untrusted Internet and the secure internal corporate network.",
            "Define the Screened Subnet firewall design.",
            [
                ("A DMZ isolated by firewalls from both the public Internet and the internal trusted network", True, "Screened subnets ensure an attacker who breaches a DMZ server must penetrate a second firewall to reach internal LANs."),
                ("A room where computer screens are cleaned with microfiber cloths", False, "Screened subnet is an architectural security design, not janitorial cleaning."),
                ("A subnet where all laptops must turn their monitors off", False, "Screening refers to packet filtering, not visual display hardware."),
                ("A network that can only transmit text messages without images", False, "Screened subnets support full multi-protocol data services.")
            ],
            ["firewall", "dmz", "screened-subnet", "architecture"]
        ),
        (
            "SEC-DEF-012", "network-monitoring",
            "What is the difference between NetFlow / IPFIX flow monitoring and full packet capture (PCAP)?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "NetFlow/IPFIX records flow metadata (source/destination IP, ports, protocol, bytes, duration, TCP flags) without recording payload data, enabling scalable long-term storage. Full PCAP captures every single bit including complete application payloads.",
            "Contrast NetFlow metadata monitoring with full PCAP capture.",
            [
                ("NetFlow records session metadata (IPs, ports, byte counts) for scalable storage; PCAP captures complete packet payloads", True, "NetFlow is like a phone billing record (who called who and for how long); PCAP is like a full voice recording of the conversation."),
                ("NetFlow only works on copper cables; PCAP only works on Wi-Fi", False, "Both monitoring technologies function across all network physical media."),
                ("NetFlow encrypts all web traffic; PCAP permanently deletes all packets", False, "Both are telemetry and diagnostic collection tools."),
                ("NetFlow is illegal in modern enterprise networks", False, "NetFlow/IPFIX is an industry-standard monitoring framework.")
            ],
            ["netflow", "ipfix", "pcap", "monitoring", "telemetry"]
        ),
        (
            "SEC-DEF-013", "dns-security",
            "What is 'DNS Sinkholing' in enterprise threat defense?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "DNS sinkholing intercepts DNS queries for known malicious domains (such as C2 servers or malware distribution sites) and returns a benign, internal loopback or sinkhole IP address, preventing compromised hosts from communicating with the attacker.",
            "Explain the defensive technique of DNS sinkholing.",
            [
                ("Configuring internal DNS resolvers to return a benign internal IP for known malicious domains, blocking C2 communication", True, "Sinkholing prevents compromised endpoints from reaching C2 infrastructure and alerts the SOC to infected hosts."),
                ("Throwing defective DNS servers into a physical water sinkhole", False, "Sinkholing is a DNS routing interception technique, not geological destruction."),
                ("Deleting all .com domain names from the global Internet", False, "Sinkholing targets specific verified threat actor domains."),
                ("Allowing all internal users to visit phishing sites without warnings", False, "Sinkholing blocks access to phishing and C2 domains.")
            ],
            ["dns", "dns-sinkholing", "c2-mitigation", "threat-hunting", "defense"]
        ),
        (
            "SEC-DEF-014", "network-security",
            "What is 'Dynamic ARP Inspection' (DAI) and how does it prevent ARP Spoofing on an enterprise switch?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "DAI intercepts all ARP requests and replies on untrusted switch ports and validates them against the trusted DHCP Snooping binding database (IP-to-MAC mappings), immediately dropping forged or gratuitous ARP packets that attempt to spoof IP mappings.",
            "Explain Dynamic ARP Inspection operation.",
            [
                ("It inspects ARP packets on untrusted ports, validating IP-to-MAC bindings against the DHCP Snooping database to block spoofing", True, "DAI validates ARP traffic against trusted binding tables, completely neutralizing ARP cache poisoning."),
                ("It physically welds Ethernet cables into switch ports", False, "DAI is a switch software security feature."),
                ("It deletes all IP addresses on the network every 10 minutes", False, "DAI validates ARP traffic without deleting host IPs."),
                ("It forces all computers to use static IP addresses without DHCP", False, "DAI works directly in tandem with DHCP Snooping databases.")
            ],
            ["dai", "arp-spoofing", "dhcp-snooping", "switch-security", "defense"]
        ),
        (
            "SEC-DEF-015", "network-security",
            "What is 'IP Source Guard' (IPSG) on an enterprise access switch?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "IP Source Guard uses the DHCP Snooping binding table to restrict IP traffic on untrusted Layer 2 ports, dropping any packet whose source IP address does not match the IP address assigned by DHCP to that specific MAC/port, preventing IP spoofing.",
            "Explain the function of IP Source Guard.",
            [
                ("It filters traffic on untrusted ports, permitting only packets whose source IP matches the legitimate DHCP Snooping binding table", True, "IPSG prevents malicious hosts from spoofing legitimate IP addresses to impersonate servers or bypass ACLs."),
                ("It assigns a public IP address to every employee's personal smartphone", False, "IPSG is a defensive Layer 2 packet filter, not an address allocator."),
                ("It shuts down the switch when the temperature reaches 30 degrees Celsius", False, "IPSG monitors IP packet headers, not hardware thermals."),
                ("It encrypts all Ethernet cables with AES-256", False, "IPSG is an IP anti-spoofing filter.")
            ],
            ["ipsg", "ip-spoofing", "dhcp-snooping", "switch-security"]
        ),
        (
            "SEC-DEF-016", "stateful-vs-stateless-filtering",
            "What is a 'TCP State Exhaustion' Denial of Service attack against a stateful firewall?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Stateful firewalls maintain connection tables in RAM. A state exhaustion attack floods the firewall with thousands of new opening connections, filling the state table to capacity and causing the firewall to drop all subsequent legitimate new connections.",
            "Analyze state exhaustion attacks targeting firewall memory.",
            [
                ("Flooding the firewall with connection setups to fill its state table RAM capacity, dropping all legitimate new connections", True, "State exhaustion targets firewall connection tracking tables rather than raw network bandwidth."),
                ("Physically draining the battery backup of the server rack", False, "State exhaustion is a network protocol resource exhaustion attack."),
                ("Sending emails with fonts that are too large for the screen", False, "State exhaustion operates at Layer 4 transport tracking."),
                ("Deleting all firewall rules from flash memory", False, "The attack exhausts active RAM state tables, not configuration rules.")
            ],
            ["firewall", "state-table", "dos", "resource-exhaustion", "soc"]
        ),
        (
            "SEC-DEF-017", "vlan-security",
            "Why is leaving the default Native VLAN set to VLAN 1 considered a security risk on enterprise 802.1Q trunks?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "VLAN 1 is the default management VLAN on most switches. Leaving the native VLAN as VLAN 1 exposes trunks to double-tagging attacks, unauthorized control plane access, and accidental cross-VLAN leaks.",
            "Explain security risks of default Native VLAN 1.",
            [
                ("VLAN 1 is the default management VLAN; leaving native traffic on VLAN 1 facilitates VLAN hopping and unauthorized control access", True, "Best practice mandates assigning native VLAN to an unused, isolated dummy VLAN ID (e.g. VLAN 999)."),
                ("VLAN 1 packets can only travel 10 meters before dissolving", False, "VLAN IDs do not alter physical electrical propagation."),
                ("VLAN 1 causes all switch passwords to be printed on public printers", False, "VLAN 1 is simply a default logical grouping."),
                ("VLAN 1 is banned by federal telecommunications law", False, "VLAN 1 is standard default IEEE configuration.")
            ],
            ["vlan-security", "native-vlan", "switch-hardening"]
        ),
        (
            "SEC-DEF-018", "firewall-architecture",
            "What is 'SSL/TLS Inspection' (TLS Decryption / Break-and-Inspect) on a Next-Generation Firewall (NGFW)?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Because most modern malware and C2 communications use HTTPS, an NGFW performs forward proxy TLS inspection by terminating the TLS session from the client, decrypting and inspecting the payload for threats, and re-encrypting it before sending to the external server.",
            "Explain TLS decryption and inspection on firewalls.",
            [
                ("The firewall acts as a forward proxy, decrypting HTTPS traffic to inspect payloads for malware before re-encrypting it to the destination", True, "TLS inspection eliminates encryption blind spots, allowing firewalls and IPS to detect threats inside HTTPS."),
                ("The firewall posts all user passwords to a public company bulletin board", False, "TLS inspection is a confidential security gateway inspection process."),
                ("The firewall converts all encrypted websites into unencrypted plain text forever", False, "Traffic is re-encrypted before leaving the firewall."),
                ("The firewall deletes all images from user web pages", False, "TLS inspection inspects malware signatures and malicious scripts.")
            ],
            ["firewall", "tls-inspection", "ngfw", "ssl-decryption", "defense"]
        ),
        (
            "SEC-DEF-019", "ids-ips-advanced",
            "What is a 'Heuristic' detection engine in advanced network security systems?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Heuristic detection uses rule-based algorithms and experience-based decision trees to identify suspicious characteristics and behaviors (e.g. unusual port/protocol combinations, high entropy, rapid execution), rather than requiring an exact signature match.",
            "Explain heuristic detection methodologies.",
            [
                ("An algorithm that evaluates behavioral characteristics and probability metrics to identify suspicious activity without exact signatures", True, "Heuristics detect suspicious characteristics (like odd packet ratios or encrypted payload anomalies) indicative of attacks."),
                ("A tool that tests the physical tension of optical fiber cables", False, "Heuristics is an algorithmic detection methodology, not mechanical cable testing."),
                ("An automated system that orders new hardware parts when servers crash", False, "Heuristics inspects network traffic patterns."),
                ("A protocol used to stream audio recordings across Bluetooth", False, "Heuristics is a cybersecurity analysis methodology.")
            ],
            ["ids", "heuristics", "detection-engineering", "anomaly-detection"]
        ),
        (
            "SEC-DEF-020", "network-monitoring",
            "In network security monitoring, what is the 'Signal-to-Noise Ratio' (SNR) of an alert rule?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "SNR measures the proportion of genuine, actionable security alerts (signal) compared to false positives and benign alerts (noise) produced by a rule. Detection engineers tune rules to maximize SNR and eliminate analyst fatigue.",
            "Explain Signal-to-Noise ratio in detection engineering.",
            [
                ("The proportion of genuine actionable security threats (signal) compared to benign false positives (noise) produced by an alert rule", True, "High SNR rules produce high-confidence, actionable alerts that allow SOC analysts to focus on real attacks."),
                ("The volume in decibels of sound produced by the server room ventilation fans", False, "In detection engineering, SNR refers to alert fidelity, not acoustic decibels."),
                ("The physical ratio of copper wires to glass fiber strands in an office", False, "SNR in monitoring evaluates detection rule precision."),
                ("The number of words in an email message", False, "SNR measures alert fidelity.")
            ],
            ["detection-engineering", "snr", "alert-tuning", "soc", "false-positives"]
        ),
        (
            "SEC-DEF-021", "network-security",
            "What is a 'Honeytoken' or 'Canary Service' deployed on an internal enterprise network?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A Honeytoken or canary is an intentionally placed bogus asset (a fake database credential, unused subnet IP, or fake share) that has zero legitimate business purpose. Any access attempt immediately triggers a high-fidelity alert indicating unauthorized internal reconnaissance.",
            "Explain the use of honeytokens and canary assets.",
            [
                ("An intentionally fake asset with zero legitimate use, where any interaction triggers a high-fidelity alert of malicious activity", True, "Because canaries have no legitimate business traffic, any interaction has near 100% true positive alert fidelity."),
                ("A sweet snack provided to technicians working overtime in datacenters", False, "This is literal wordplay, not a cybersecurity deception asset."),
                ("A cryptographic key that automatically grants root access to all employees", False, "Canary tokens are deception tripwires."),
                ("An automated script that formats the local router every evening", False, "Canary assets generate alerts upon unauthorized access.")
            ],
            ["deception-technology", "honeytoken", "canary", "soc", "high-fidelity"]
        ),
        (
            "SEC-DEF-022", "dns-security",
            "What is 'DNS-over-HTTPS' (DoH / RFC 8484) and what operational challenge does it create for enterprise security teams?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "DoH encrypts DNS queries inside HTTPS sessions over TCP port 443. While protecting user privacy on public Wi-Fi, it conceals DNS traffic from enterprise firewalls, NIDS, and DNS filtering controls, blinding SOC analysts to malicious domain requests.",
            "Analyze the security implications of DNS-over-HTTPS in enterprise environments.",
            [
                ("It encrypts DNS inside HTTPS (port 443), preventing enterprise firewalls and SOC monitoring tools from inspecting and filtering domain queries", True, "DoH blinds enterprise perimeter security controls to DNS tunneling and C2 queries unless internal DoH is enforced or external DoH is blocked."),
                ("It causes optical fiber cables to burn out after 100 queries", False, "DoH is standard application software over HTTPS."),
                ("It permanently disables the user's computer keyboard", False, "DoH encrypts DNS lookups without affecting hardware peripherals."),
                ("It requires all domain names to be written in binary code", False, "DoH resolves standard human-readable domain names.")
            ],
            ["dns", "doh", "dns-security", "encryption-blinds", "soc"]
        ),
        (
            "SEC-DEF-023", "network-segmentation-advanced",
            "What is an 'Out-of-Band' (OOB) network management infrastructure?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "OOB management provides a dedicated, physically or logically isolated network segment used exclusively by administrators to manage networking gear (via console ports, iDRAC, iLO), ensuring management access even if the production data plane collapses or is under attack.",
            "Explain Out-of-Band network management.",
            [
                ("A dedicated, isolated network used exclusively for administering network hardware, separate from production data traffic", True, "OOB ensures that administrative control of switches, routers, and firewalls remains accessible even during major production network outages."),
                ("A musical band performing outside the corporate office building", False, "This is wordplay on the term band."),
                ("A network that can only transmit traffic when disconnected from electrical power", False, "All networking equipment requires power."),
                ("An unencrypted public Wi-Fi network for corporate guests", False, "OOB management is strictly secured internal infrastructure.")
            ],
            ["network-segmentation", "oob-management", "console", "infrastructure"]
        ),
        (
            "SEC-DEF-024", "stateful-vs-stateless-filtering",
            "How does a Next-Generation Firewall (NGFW) with App-ID identify applications compared to a traditional port-based stateful firewall?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Traditional firewalls assume port 80 is HTTP and port 443 is HTTPS. An NGFW inspects the actual protocol signatures, packet behaviors, and payloads across all ports regardless of port number, preventing evasive malware from hiding non-web traffic over port 443.",
            "Explain application identification (App-ID) in NGFWs.",
            [
                ("It inspects protocol signatures and payload characteristics regardless of port number, stopping traffic hiding on non-standard ports", True, "App-ID prevents protocols (like BitTorrent or C2 beacons) from evading policies by simply listening on port 443."),
                ("It checks the color of the Ethernet cable plugged into the wall", False, "Cable colors do not indicate protocol signatures."),
                ("It requires the software developer to sign a paper contract with the firewall company", False, "App-ID uses algorithmic signature inspection on live packet streams."),
                ("It deletes all applications that consume more than 10 MB of RAM", False, "Firewalls filter network packets, not local RAM allocation.")
            ],
            ["ngfw", "app-id", "deep-packet-inspection", "firewall-architecture"]
        ),
        (
            "SEC-DEF-025", "ids-ips-advanced",
            "What is the function of an 'Evasion Technique' such as TCP overlapping fragments when targeting an IDS?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "An attacker sends fragments with overlapping offsets containing conflicting data. If the IDS reassembles the fragments differently than the destination target OS (e.g. favoring the first fragment while the OS favors the second), the IDS misses the malicious payload.",
            "Analyze fragmentation evasion against intrusion detection systems.",
            [
                ("Exploiting differences between how the IDS and the target OS reassemble overlapping fragments to hide malicious payloads from detection", True, "If the IDS reassembly logic does not match target host OS reassembly (BSD vs Linux vs Windows), attacks slip through undetected."),
                ("Accelerating packet transmission to twice the speed of light", False, "Evasion techniques exploit software implementation differences, not physics violations."),
                ("Physically unplugging the sensor from the equipment rack", False, "Overlapping fragments are software protocol evasion techniques."),
                ("Forcing the target server to restart into safe mode", False, "Evasion conceals payloads from security sensors.")
            ],
            ["ids", "evasion", "overlapping-fragments", "tcp", "soc"]
        ),
        (
            "SEC-DEF-026", "network-security",
            "What is '802.1X' Network Access Control (NAC) and where is it enforced?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "IEEE 802.1X is a port-based authentication framework where an endpoint (supplicant) must authenticate (via EAP against a RADIUS server) before the switch or WAP (authenticator) opens the port to permit regular network traffic.",
            "Explain IEEE 802.1X port-based access control.",
            [
                ("A port-based authentication protocol where endpoints must authenticate via RADIUS before the switch port permits network access", True, "802.1X ensures that rogue unauthorized devices plugged into enterprise wall jacks are quarantined until authenticated."),
                ("A wireless standard that enables Wi-Fi transmission over 500 kilometers", False, "802.1X is an authentication framework, not a long-distance wireless radio standard."),
                ("A protocol used to format Linux operating systems over the network", False, "PXE boots operating systems; 802.1X enforces authentication."),
                ("An encryption cipher that protects files stored on floppy disks", False, "802.1X is a Layer 2 network admission control framework.")
            ],
            ["802.1x", "nac", "radius", "access-control", "switch-security"]
        ),
        (
            "SEC-DEF-027", "network-monitoring",
            "In network security operations, what is a 'Promiscuous Mode' configuration on a network interface card (NIC)?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 45,
            "Standard NICs discard frames whose destination MAC does not match their own hardware MAC (or broadcast/multicast). In Promiscuous Mode, the NIC passes ALL captured frames on the wire directly to the OS kernel, enabling packet sniffing and NIDS monitoring.",
            "Define Promiscuous Mode on network interface cards.",
            [
                ("A mode where the NIC passes all received frames on the wire to the OS, regardless of destination MAC address", True, "Promiscuous mode allows packet sniffers (like Wireshark) and NIDS sensors to inspect all passing traffic on a mirrored port."),
                ("A mode that allows the network card to operate without any electrical power", False, "Hardware requires electrical power."),
                ("A mode that deletes all packets passing through the interface", False, "Promiscuous mode captures frames; it does not drop them."),
                ("A mode that automatically sets all user passwords to 'password123'", False, "Hardware NIC modes have no connection to user password policies.")
            ],
            ["packet-analysis", "promiscuous-mode", "nic", "wireshark", "nids"]
        ),
        (
            "SEC-DEF-028", "network-security",
            "What is 'BGP Hijacking' and what threat does it pose to global network routing?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "BGP hijacking occurs when a malicious or misconfigured Autonomous System (AS) falsely advertises IP prefixes it does not own. Global routers adopt the falsified routes, redirecting massive volumes of Internet traffic through the attacker's AS for interception or blackholing.",
            "Analyze BGP route hijacking attacks.",
            [
                ("Falsely advertising ownership of an IP prefix over BGP, redirecting legitimate Internet traffic through an attacker-controlled network", True, "BGP hijacking allows nation-state actors and cybercriminals to intercept, spy on, or drop global Internet traffic."),
                ("Physically stealing router chassis from an ISP datacenter", False, "BGP hijacking is a routing protocol announcement attack, not physical equipment theft."),
                ("A protocol that converts IPv4 addresses into Morse code", False, "BGP is the core exterior gateway routing protocol of the Internet."),
                ("An attack that causes computer monitors to flicker", False, "BGP hijacking manipulates global IP packet forwarding paths.")
            ],
            ["routing", "bgp", "bgp-hijacking", "internet-security", "threats"]
        ),
        (
            "SEC-DEF-029", "network-security",
            "Which cryptographic framework was developed to secure BGP routing by validating that an Autonomous System is authorized to originate a specific IP prefix?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 2, 45,
            "Resource Public Key Infrastructure (RPKI) uses cryptographic Route Origin Authorizations (ROAs) to verify that an AS is legitimate and authorized to announce an IP prefix, mitigating BGP prefix hijacking.",
            "Identify the cryptographic framework securing BGP origin announcements.",
            [
                ("Resource Public Key Infrastructure (RPKI / ROA)", True, "RPKI validates Route Origin Authorizations to stop unauthorized BGP prefix announcements."),
                ("Dynamic Trunking Protocol (DTP)", False, "DTP negotiates switch VLAN trunks on local Ethernet links."),
                ("DHCP Snooping", False, "DHCP snooping protects local switches from rogue DHCP."),
                ("Spanning Tree Protocol (STP)", False, "STP prevents Layer 2 switching loops.")
            ],
            ["bgp", "rpki", "roa", "routing-security"]
        ),
        (
            "SEC-DEF-030", "dns-security",
            "What is a 'Fast Flux' DNS network and why is it employed by advanced cybercrime botnets?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Fast Flux rapidly changes the IP addresses associated with a domain name (using extremely short TTLs and round-robin A records pointing to thousands of compromised bot hosts), making it exceptionally difficult for defenders to block the C2 infrastructure via static IP blacklisting.",
            "Analyze Fast Flux DNS evasion techniques.",
            [
                ("Rapidly cycling IP addresses in DNS records using extremely short TTLs across a botnet to evade IP-based blocking", True, "Fast Flux conceals the true backend server by routing requests through a constantly rotating front-end proxy pool."),
                ("A technique that accelerates download speeds by 500%", False, "Fast Flux is a botnet evasion technique, not a download accelerator."),
                ("A protocol that enables satellites to transmit Internet data across solar flares", False, "Fast Flux operates on standard public DNS infrastructure."),
                ("A physical fan installation that cools server power supplies", False, "Fast Flux is an adversarial DNS management technique.")
            ],
            ["dns", "fast-flux", "botnet", "c2", "evasion", "soc"]
        ),
        (
            "SEC-DEF-031", "firewall-architecture",
            "What is a 'Bastion Host' and what key hardening measures should be applied to it?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A Bastion Host is a publicly exposed server (or management gateway) specifically hardened to withstand attacks by disabling all unnecessary services, enforcing strict MFA authentication, applying minimal firewall rules, and enabling verbose audit logging.",
            "Explain Bastion Host hardening requirements.",
            [
                ("A security-hardened server running minimal necessary services, enforced with MFA and rigorous logging to withstand direct attacks", True, "Bastion hosts are stripped of all unneeded packages and services to minimize exploitable attack surface."),
                ("A server placed in a swimming pool to prevent overheating", False, "Bastion hosts are mounted in standard secure server racks."),
                ("A server that automatically sends all user emails to public websites", False, "Bastion hosts protect private networks."),
                ("A wireless printer that connects without passwords", False, "Bastion hosts enforce strict authentication controls.")
            ],
            ["bastion-host", "system-hardening", "security-architecture"]
        ),
        (
            "SEC-DEF-032", "network-monitoring",
            "What is 'Traffic Baselining' and why is it vital for network anomaly detection?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Traffic baselining establishes a statistical profile of normal network metrics (bandwidth volume, connection counts, protocol distributions, active hours). Anomaly detection relies on this baseline to identify unusual spikes (e.g. off-hours data exfiltration).",
            "Explain the role of traffic baselining in anomaly detection.",
            [
                ("Measuring normal operational network metrics over time so statistical anomalies (such as data exfiltration) can be identified", True, "Without an accurate baseline of normal behavior, identifying anomalous intrusions is impossible."),
                ("Drawing lines on the floor of the server room with white chalk", False, "Baselining is mathematical telemetry profiling, not floor painting."),
                ("Testing the physical tensile strength of copper wires", False, "Baselining evaluates logical packet volumes and protocol distributions."),
                ("Formatting all corporate hard drives on the first day of every month", False, "Baselining is passive traffic telemetry collection.")
            ],
            ["monitoring", "baselining", "anomaly-detection", "soc"]
        ),
        (
            "SEC-DEF-033", "vlan-security",
            "What is 'Double Tagging' in 802.1Q VLAN hopping attacks, and what condition must exist for it to succeed?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "In double tagging, an attacker sends a frame with two 802.1Q tags. The first switch strips the outer tag because it matches the Native VLAN of the trunk. The second switch inspects the remaining inner tag, delivering the frame into the target victim VLAN.",
            "Analyze Double Tagging VLAN hopping mechanics.",
            [
                ("The outer tag matches the trunk's Native VLAN and is stripped by the first switch; the second switch forwards using the inner tag", True, "Double tagging requires the attacker to reside on the same VLAN configured as the native VLAN on the inter-switch trunk."),
                ("The attacker physically attaches two Ethernet cables to one network card", False, "Double tagging operates logically inside the 802.1Q frame headers."),
                ("The switch operating system is running in Spanish language mode", False, "Switch language has no bearing on 802.1Q encapsulation."),
                ("The user's computer monitor has two power supplies", False, "Double tagging is a Layer 2 frame manipulation attack.")
            ],
            ["vlan-security", "double-tagging", "native-vlan", "vlan-hopping"]
        ),
        (
            "SEC-DEF-034", "firewall-architecture",
            "In enterprise network security, what is a 'Forward Proxy' compared to a 'Reverse Proxy'?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A Forward Proxy sits in front of internal clients to monitor, filter, and cache their outbound requests to external Internet servers. A Reverse Proxy sits in front of backend web servers to load-balance, terminate TLS, and shield internal servers from external clients.",
            "Differentiate Forward Proxies and Reverse Proxies.",
            [
                ("A Forward Proxy protects and filters outbound client requests to the Internet; a Reverse Proxy protects and load-balances inbound requests to internal servers", True, "Forward proxies face outbound clients; reverse proxies face inbound external traffic to protect server pools."),
                ("A Forward Proxy only works in moving vehicles; a Reverse Proxy only works when backing up", False, "These are topological architectural proxies, not vehicular mechanisms."),
                ("A Forward Proxy encrypts data; a Reverse Proxy permanently deletes data", False, "Both proxies inspect and forward application traffic."),
                ("Forward proxies are strictly illegal in North America", False, "Forward proxies are standard enterprise web filtering infrastructure.")
            ],
            ["firewall", "forward-proxy", "reverse-proxy", "architecture"]
        ),
        (
            "SEC-DEF-035", "network-monitoring",
            "What is 'Data Exfiltration' in cybersecurity and what network behaviors typically characterize it?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Data exfiltration is the unauthorized transfer of sensitive organizational data to an external server. It is characterized by abnormal outbound bandwidth surges, large file transfers over non-standard ports, sustained DNS tunneling, or unusual cloud uploads off-hours.",
            "Analyze network telemetry indicators of data exfiltration.",
            [
                ("Unauthorized transfer of sensitive internal data to external destinations, characterized by large outbound transfers or tunneling", True, "Exfiltration manifests as anomalous outbound data spikes, unusual destinations, or encoded protocol tunnels."),
                ("Routine printing of office spreadsheets to a local USB printer", False, "Local USB printing is not network data exfiltration."),
                ("Upgrading a laptop's operating system with an official patch", False, "Software updates are legitimate inbound data streams."),
                ("Replacing a blown lightbulb in the server room ceiling", False, "Exfiltration is an adversarial data theft attack, not building maintenance.")
            ],
            ["exfiltration", "threat-hunting", "network-monitoring", "soc"]
        ),
    ]
    save_questions("network_security_and_defense.json", items)


if __name__ == "__main__":
    generate_packet_analysis()
    generate_network_security_defense()
