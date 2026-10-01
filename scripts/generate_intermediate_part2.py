#!/usr/bin/env python3
"""
NexoraNet Intermediate Question Bank Generator - Part 2.
Generates:
2. tcp_udp_and_transport.json (35 questions)
3. dns_dhcp_and_application.json (30 questions)
"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data" / "question_bank" / "intermediate"
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


def generate_tcp_udp_transport():
    items = [
        (
            "TCP-001", "tcp-three-way-handshake", "In step 1 of the TCP three-way handshake, what sequence number does the initiating client send to the server?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "The client generates a pseudo-random Initial Sequence Number (ISN) to prevent sequence prediction attacks, and sets the SYN control flag in the TCP header.",
            "Explain initial sequence number generation in TCP.",
            [
                ("A randomized Initial Sequence Number (ISN) selected by the client operating system", True, "Modern operating systems randomize the ISN to protect against TCP sequence prediction and session hijacking."),
                ("Always the number 0", False, "Using static 0 was an early vulnerability; RFC 6528 mandates pseudo-randomized ISNs."),
                ("The client's physical MAC address", False, "Sequence numbers are 32-bit integers tracking byte offsets, not 48-bit MAC addresses."),
                ("The total number of packets remaining on the hard drive", False, "Sequence numbers track transmission bytes, not disk storage capacity.")
            ],
            ["tcp", "three-way-handshake", "isn", "security"]
        ),
        (
            "TCP-002", "tcp-three-way-handshake", "In step 2 of the TCP three-way handshake, what value does the server return in the Acknowledgment Number field?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 55,
            "The server acknowledges the client's SYN by sending an Acknowledgment number equal to the client's Initial Sequence Number plus 1 (ISN_client + 1), signaling the next expected byte.",
            "Calculate expected TCP acknowledgment values.",
            [
                ("Client's Initial Sequence Number plus 1 (Client_ISN + 1)", True, "TCP acknowledges consumed control flags (SYN and FIN) by adding 1 to the received sequence number."),
                ("Client's Initial Sequence Number minus 1", False, "Acknowledgment numbers indicate the NEXT expected byte and advance forward, never backward."),
                ("The server's own Initial Sequence Number", False, "The server's ISN is placed in the Sequence Number field, not the Acknowledgment Number field."),
                ("Always decimal 80", False, "80 is the HTTP port number, not a dynamic TCP sequence/ack value.")
            ],
            ["tcp", "three-way-handshake", "ack", "sequence-numbers"]
        ),
        (
            "TCP-003", "tcp-flags", "Which combination of TCP control flags is set in the packet sent by a server during step 2 of the 3-way handshake?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "During step 2, the server sets both SYN (to synchronize its own sequence number) and ACK (to acknowledge receipt of the client's SYN).",
            "Identify flags set in the second step of the TCP handshake.",
            [
                ("SYN and ACK", True, "The server sets both SYN (synchronize) and ACK (acknowledge) flags."),
                ("SYN and FIN", False, "SYN and FIN are never set simultaneously in legitimate traffic (historically seen in malicious port scans)."),
                ("ACK and RST", False, "RST indicates connection refusal or abort."),
                ("PSH and URG", False, "PSH and URG are data transfer flags, not connection establishment flags.")
            ],
            ["tcp", "tcp-flags", "three-way-handshake"]
        ),
        (
            "TCP-004", "tcp-flags", "What is the security significance of observing a packet with both SYN and FIN flags set simultaneously?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "SYN (open connection) and FIN (close connection) are mutually exclusive under standard RFC 793 state logic. Packets with both flags set represent a SYN-FIN scan designed to evade primitive firewall inspection or fingerprint operating systems.",
            "Recognize abnormal TCP flag combinations used in reconnaissance.",
            [
                ("It is an illegal flag combination often used in stealth port scans to fingerprint OS stacks or evade stateless firewalls", True, "RFC 793 defines SYN and FIN as logically incompatible; seeing them indicates adversarial probing."),
                ("It indicates that the connection has been successfully upgraded to fiber optics", False, "TCP flags are transport layer control bits independent of physical media."),
                ("It is standard behavior when streaming high-definition 4K video", False, "Video streaming uses standard TCP data segments or UDP."),
                ("It proves the packet was generated by an authorized DNS root server", False, "DNS servers never generate SYN-FIN packets.")
            ],
            ["tcp", "tcp-flags", "reconnaissance", "security", "firewall-evasion"]
        ),
        (
            "TCP-005", "tcp-flags", "Which TCP flag informs the receiving host that incoming segment data should be pushed immediately to the application without waiting for buffers to fill?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "The PSH (Push) flag requests that the receiving TCP stack bypass its internal buffering thresholds and pass the data immediately up to the listening application process (common in interactive SSH or Telnet sessions).",
            "Identify the role of the TCP PSH flag.",
            [
                ("PSH (Push)", True, "PSH tells the receiver to empty its buffer and push data immediately to the application."),
                ("URG (Urgent)", False, "URG marks the presence of urgent out-of-band data via the urgent pointer."),
                ("FIN (Finish)", False, "FIN signals graceful connection closing."),
                ("SYN (Synchronize)", False, "SYN synchronizes sequence numbers at startup.")
            ],
            ["tcp", "tcp-flags", "psh", "buffering"]
        ),
        (
            "TCP-006", "tcp-connection-termination", "How many packets are standardly exchanged during a graceful TCP connection teardown?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "A standard graceful TCP termination is a four-way handshake: 1. Host A sends FIN, 2. Host B sends ACK, 3. Host B sends its own FIN, 4. Host A sends final ACK. (In some implementations, steps 2 and 3 can be combined into a single FIN-ACK, creating a 3-way teardown).",
            "Recall standard TCP connection termination exchange.",
            [
                ("4 packets (FIN, ACK, FIN, ACK)", True, "TCP is full-duplex; each direction must be closed independently with a FIN and ACK."),
                ("2 packets (FIN, ACK)", False, "2 packets would only close one half of the bidirectional TCP stream."),
                ("3 packets (SYN, SYN-ACK, ACK)", False, "That is the 3-way connection ESTABLISHMENT handshake."),
                ("1 packet (RST)", False, "A single RST is an abrupt forced abort, not a graceful teardown.")
            ],
            ["tcp", "connection-termination", "fin-ack"]
        ),
        (
            "TCP-007", "tcp-connection-termination", "What is the purpose of the TIME_WAIT state in the TCP state machine on the endpoint that initiated an active close?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "TIME_WAIT ensures that the final ACK was received by the remote endpoint (giving time to re-send the ACK if the remote peer retransmits its FIN), and allows any lingering duplicate packets from the connection to expire on the network before the port can be reused.",
            "Explain the technical rationale for the TCP TIME_WAIT state.",
            [
                ("To ensure the remote peer received the final ACK and to prevent lingering duplicate packets from corrupting a future new connection", True, "TIME_WAIT lasts 2 * MSL (Maximum Segment Lifetime) to safely drain in-flight packets."),
                ("To wait for the user to type their username and password again", False, "TIME_WAIT is a kernel transport state independent of user authentication."),
                ("To allow the CPU fan to cool down the processor", False, "TCP states manage protocol packets, not cooling hardware."),
                ("To notify the local router to reboot its firmware", False, "Routers do not reboot when transport connections terminate.")
            ],
            ["tcp", "time-wait", "tcp-state-machine", "architecture"]
        ),
        (
            "TCP-008", "tcp-basics", "What is the primary function of the TCP 'Window Size' field located in the TCP header?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "Window Size is used for Flow Control. It informs the sender how many bytes of data the receiver's buffer is currently prepared to accept before requiring an acknowledgment, preventing buffer overflow.",
            "Explain TCP flow control via sliding window.",
            [
                ("To advertise the number of bytes the receiving buffer can accept before requiring an acknowledgment (Flow Control)", True, "The receiver dynamically advertises its window size to throttle sender throughput to match its buffer capacity."),
                ("To specify the physical size in inches of the user's computer screen", False, "Window size refers to network buffer bytes, not display monitors."),
                ("To indicate how many web browser tabs can be opened simultaneously", False, "Transport window size has no relation to browser UI tabs."),
                ("To set the expiration date of the server's SSL certificate", False, "Certificates are application/TLS credentials with dates in X.509 format.")
            ],
            ["tcp", "flow-control", "sliding-window"]
        ),
        (
            "TCP-009", "tcp-basics", "What is the difference between TCP Flow Control and TCP Congestion Control?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "Flow Control prevents the sender from overwhelming the RECEIVING HOST'S buffer (managed by advertised Window Size). Congestion Control prevents the sender from overwhelming the INTERVENING NETWORK routers and links (managed by Congestion Window / cwnd).",
            "Contrast Flow Control and Congestion Control in TCP.",
            [
                ("Flow control protects the receiver from buffer overflow; congestion control protects intermediate network links and routers from saturation", True, "Flow control is end-to-end between endpoints; congestion control adapts to network bottleneck capacity."),
                ("Flow control is used only in IPv4; congestion control is used only in IPv6", False, "Both mechanisms operate across all modern IP networks."),
                ("Flow control encrypts the packet; congestion control decrypts the packet", False, "Neither mechanism provides cryptographic encryption."),
                ("Flow control requires satellite dishes; congestion control uses copper wire", False, "Both are transport algorithms independent of physical media.")
            ],
            ["tcp", "flow-control", "congestion-control"]
        ),
        (
            "TCP-010", "tcp-basics", "What happens when a TCP sender does not receive an acknowledgment (ACK) for a transmitted segment before its Retransmission Timeout (RTO) expires?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "If the RTO timer expires without receiving an ACK, TCP assumes the segment was lost or corrupted in transit and automatically retransmits the unacknowledged segment while reducing its congestion window.",
            "Describe TCP segment retransmission behavior.",
            [
                ("It assumes the segment was lost and automatically retransmits it while backing off its transmission rate", True, "TCP reliability guarantees delivery through timer-based retransmissions upon packet loss."),
                ("It immediately crashes the operating system with a blue screen", False, "Packet loss is an expected condition handled gracefully by TCP."),
                ("It switches the entire connection permanently to UDP", False, "TCP connections cannot dynamically morph into UDP sockets."),
                ("It sends a physical electrical shock through the Ethernet cable", False, "Networking hardware strictly adheres to safe low-voltage telecommunication limits.")
            ],
            ["tcp", "retransmission", "reliability", "rto"]
        ),
        (
            "TCP-011", "tcp-flags", "How does a SYN Flood Denial of Service attack exploit the standard TCP three-way handshake?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 60,
            "The attacker sends a deluge of TCP SYN packets with spoofed source IP addresses. The target server allocates memory in its SYN backlog queue and sends SYN-ACKs that never receive the final ACK, eventually filling the connection backlog and rejecting legitimate users.",
            "Analyze the mechanics of a TCP SYN Flood attack.",
            [
                ("The attacker sends numerous SYN packets with spoofed source IPs, filling the server's half-open connection queue (SYN backlog) so legitimate requests are dropped", True, "SYN floods exhaust kernel memory buffers (backlog queue) by leaving connections in SYN_RECEIVED state."),
                ("The attacker sends a giant physical surge of AC electricity that burns out the server's network card", False, "SYN flood is a logical protocol resource exhaustion attack, not an electrical power surge."),
                ("The attacker decrypts the server's private SSH key using rainbow tables", False, "SYN floods do not involve cryptographic key cracking."),
                ("The attacker deletes all DNS records for the root domain of the Internet", False, "SYN floods target a specific host's transport stack, not global DNS registries.")
            ],
            ["tcp", "syn-flood", "ddos", "security", "soc"]
        ),
        (
            "TCP-012", "tcp-flags", "Which defensive mechanism was specifically developed to mitigate TCP SYN flood attacks without consuming server memory for half-open connections?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "SYN Cookies encode the connection state (client IP, client port, server secret) cryptographically into the server's Initial Sequence Number (ISN) in the SYN-ACK response, allowing the server to avoid allocating memory until the client's final ACK arrives.",
            "Explain the defensive function of SYN Cookies.",
            [
                ("SYN Cookies", True, "SYN cookies avoid allocating kernel memory until the final ACK arrives, neutralizing SYN backlog exhaustion."),
                ("Traceroute", False, "Traceroute is a path diagnostic tool."),
                ("ARP Spoofing", False, "ARP spoofing is an attack, not a defensive measure."),
                ("Cat6 Shielded Cabling", False, "Cabling shielding prevents electromagnetic interference, not transport protocol floods.")
            ],
            ["tcp", "syn-cookies", "ddos-mitigation", "defense"]
        ),
        (
            "TCP-013", "udp-communication", "How large is the standard User Datagram Protocol (UDP) header?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 35,
            "The UDP header consists of exactly 8 bytes (64 bits), structured into four 2-byte fields: Source Port, Destination Port, Length, and Checksum.",
            "Recall the size and fields of the UDP header.",
            [
                ("8 bytes (64 bits)", True, "The UDP header is a lightweight 8 bytes containing Source Port, Destination Port, Length, and Checksum."),
                ("20 bytes (160 bits)", False, "20 bytes is the minimum size of a standard TCP or IPv4 header without options."),
                ("48 bytes", False, "48 bits (6 bytes) is a MAC address, not a UDP header."),
                ("64 bytes", False, "64 bytes is the minimum Ethernet frame size.")
            ],
            ["udp", "udp-header", "transport-layer"]
        ),
        (
            "TCP-014", "tcp-basics", "What is the minimum header size of a standard TCP segment without optional header fields?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 35,
            "A standard TCP header with no options is exactly 20 bytes (160 bits). With options (such as Maximum Segment Size, Timestamps, Window Scaling), it can extend up to 60 bytes.",
            "Recall the minimum TCP header size.",
            [
                ("20 bytes", True, "The minimum standard TCP header is 20 bytes."),
                ("8 bytes", False, "8 bytes is the size of a UDP header."),
                ("14 bytes", False, "14 bytes is the size of a standard Ethernet header without 802.1Q tags."),
                ("40 bytes", False, "40 bytes is the fixed header size of IPv6.")
            ],
            ["tcp", "tcp-header", "transport-layer"]
        ),
        (
            "TCP-015", "tcp-flags", "When a client sends a TCP SYN packet to a port on a server where no service is actively listening, what response does the server standardly return?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 50,
            "Under RFC 793, if a segment arrives addressed to a closed port, the host operating system returns a TCP segment with the RST (Reset) and ACK flags set to notify the client that the port is closed and refuse connection.",
            "Predict the response from a closed TCP port.",
            [
                ("A TCP packet with the RST and ACK flags set (RST/ACK)", True, "A closed port responds with RST/ACK to reject the connection attempt."),
                ("A TCP SYN-ACK packet accepting the connection", False, "SYN-ACK is returned only when a service is actively listening on the port."),
                ("An ICMP Echo Reply message", False, "ICMP Echo Reply responds to Echo Request (ping), not TCP SYN packets."),
                ("The server shuts down its power supply immediately", False, "Operating systems routinely reject closed port probes via RST.")
            ],
            ["tcp", "tcp-flags", "rst", "closed-port", "port-scanning"]
        ),
        (
            "TCP-016", "tcp-flags", "When a client sends a UDP packet to a destination port on a server where no application is listening, what ICMP message is standardly returned by the host?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 50,
            "Because UDP has no built-in connection handshake or RST mechanism, the operating system's IP stack returns an ICMP Type 3, Code 3 message: Destination Unreachable (Port Unreachable).",
            "Identify the error returned by a closed UDP port.",
            [
                ("ICMP Destination Unreachable — Port Unreachable (Type 3, Code 3)", True, "Closed UDP ports trigger ICMP Port Unreachable responses from the target OS."),
                ("TCP RST/ACK segment", False, "UDP does not use TCP control segments."),
                ("HTTP 404 Not Found error", False, "HTTP 404 is an application-layer web response, not a transport-layer port failure."),
                ("An ARP Reply with MAC 00:00:00:00:00:00", False, "ARP resolves IP to MAC; it does not report UDP port status.")
            ],
            ["udp", "icmp", "port-unreachable", "port-scanning"]
        ),
        (
            "TCP-017", "tcp-basics", "What is the role of the Maximum Segment Size (MSS) negotiated in TCP SYN options?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "MSS defines the largest amount of data (payload only, excluding IP and TCP headers) that a device is willing to receive in a single TCP segment, typically derived from MTU (e.g. 1500 byte MTU - 20 IP - 20 TCP = 1460 byte MSS).",
            "Explain TCP Maximum Segment Size calculation.",
            [
                ("The largest payload data size in bytes a host can receive in a single segment without fragmentation", True, "Standard Ethernet 1500 MTU yields an MSS of 1460 bytes (1500 - 40 bytes header overhead)."),
                ("The total number of computers allowed on an enterprise Wi-Fi network", False, "MSS is a byte size parameter for TCP segments, not a host count limit."),
                ("The physical length in millimeters of the CPU processor chip", False, "MSS is a network transport parameter."),
                ("The maximum number of characters permitted in an email password", False, "Password limits are application security policies.")
            ],
            ["tcp", "mss", "mtu", "segmentation"]
        ),
        (
            "TCP-018", "ports-and-sockets", "Which command on a Linux or Windows terminal displays all actively listening ports and established TCP connections?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 1, 40,
            "'netstat -ano' (or 'ss -tulpn' on modern Linux) displays active listening sockets, foreign addresses, connection states (ESTABLISHED, LISTENING, TIME_WAIT), and process IDs.",
            "Recall terminal commands to inspect socket connections.",
            [
                ("netstat -ano (or 'ss -tulpn' on Linux)", True, "Netstat and ss display active listening ports and established connection tables."),
                ("ipconfig /renew", False, "Ipconfig /renew requests a new DHCP lease from the DHCP server."),
                ("ping 127.0.0.1", False, "Ping tests loopback IP stack functionality."),
                ("tracert -d 8.8.8.8", False, "Tracert maps router hops along a network path.")
            ],
            ["ports-and-sockets", "netstat", "ss", "cli", "troubleshooting"]
        ),
        (
            "TCP-019", "tcp-basics", "In a TCP header, how many bits are allocated to the Source Port and Destination Port fields?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 35,
            "Both Source Port and Destination Port in TCP (and UDP) are 16-bit fields ($2^{16} = 65,536$ possible port numbers, ranging from 0 to 65535).",
            "Recall bit size of transport layer port fields.",
            [
                ("16 bits each (supporting ports 0 to 65535)", True, "16 bits yields 65,536 total port numbers per IP address."),
                ("32 bits each", False, "32 bits is the size of the Sequence Number and Acknowledgment Number fields."),
                ("8 bits each", False, "8 bits is the size of an IPv4 octet (0-255)."),
                ("48 bits each", False, "48 bits is the length of an Ethernet MAC address.")
            ],
            ["tcp", "ports", "tcp-header"]
        ),
        (
            "TCP-020", "tcp-flags", "What is the primary role of the TCP Urgent Pointer (URG flag)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "The URG flag indicates that the 16-bit Urgent Pointer field is valid and points to the last byte of urgent, out-of-band data that the receiving process should evaluate immediately (e.g. an interrupt signal in Telnet/FTP).",
            "Explain the function of the TCP URG flag.",
            [
                ("It indicates that the Urgent Pointer field is valid, pointing to out-of-band data requiring immediate attention", True, "URG signals that urgent control data takes priority over normal buffered stream data."),
                ("It instructs the sender to double the transmission voltage on the wire", False, "Transport protocols cannot alter electrical voltage."),
                ("It deletes all logs stored on the local router", False, "URG is a stream processing flag, not a log deletion command."),
                ("It forces all web browsers to switch to night mode", False, "UI themes are browser/operating system settings.")
            ],
            ["tcp", "tcp-flags", "urg"]
        ),
        (
            "TCP-021", "tcp-basics", "What does the TCP Cumulative Acknowledgment scheme mean?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "Cumulative ACK means an ACK number $N$ acknowledges that all bytes up to $N - 1$ have been successfully received, and that the receiver is ready to receive byte $N$.",
            "Explain cumulative acknowledgment mechanics.",
            [
                ("An ACK with value N informs the sender that all bytes prior to N have been successfully received", True, "Cumulative ACK implicitly confirms all preceding bytes without needing individual ACKs for every byte."),
                ("The receiver only acknowledges packets once a week", False, "ACKs are sent within milliseconds or delayed ACK intervals."),
                ("The sender must re-send every single packet sent since the connection began", False, "That would defeat the efficiency of sliding window protocols."),
                ("The ACK packet contains a physical signature from the CEO of the company", False, "ACKs are automated cryptographic or protocol-level acknowledgments.")
            ],
            ["tcp", "ack", "cumulative-ack", "reliability"]
        ),
        (
            "TCP-022", "tcp-basics", "What is Selective Acknowledgment (SACK / RFC 2018) in TCP?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "SACK allows a receiver to inform the sender about non-contiguous blocks of data that were received successfully, enabling the sender to retransmit only the specific missing segments rather than an entire window.",
            "Explain the optimization provided by TCP SACK.",
            [
                ("It allows the receiver to report non-contiguous received blocks, enabling the sender to retransmit only missing segments", True, "SACK prevents wasteful retransmission of packets that were already received intact."),
                ("It encrypts email passwords with quantum key distribution", False, "SACK is an unencrypted transport reliability optimization."),
                ("It allows routers to delete packets when network traffic is low", False, "Routers do not delete valid packets unnecessarily."),
                ("It replaces all copper wires with laser beams", False, "SACK is a software protocol option.")
            ],
            ["tcp", "sack", "performance", "retransmission"]
        ),
        (
            "TCP-023", "tcp-connection-termination", "A network engineer observes multiple sockets in the 'CLOSE_WAIT' state on a web server. What does this condition typically indicate?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 60,
            "CLOSE_WAIT indicates that the remote peer sent a FIN and the local OS acknowledged it, but the local application process has not yet called close() on the socket to send its own FIN. High numbers of CLOSE_WAIT sockets indicate an application-level bug or resource leak.",
            "Diagnose sockets hanging in CLOSE_WAIT.",
            [
                ("The remote client closed the connection, but the local application process has not yet closed its socket (application bug or thread leak)", True, "CLOSE_WAIT represents a local application failing to call close() on its socket handles."),
                ("The physical Ethernet cable has been eaten by rodents", False, "CLOSE_WAIT is a protocol state in the local kernel, not physical wire damage."),
                ("The server has successfully completed an automated antivirus update", False, "Connection states are unrelated to antivirus updates."),
                ("The ISP has doubled the server's public IP address pool", False, "CLOSE_WAIT reflects local process socket handling.")
            ],
            ["tcp", "close-wait", "troubleshooting", "application-leak"]
        ),
        (
            "TCP-024", "tcp-basics", "What is Nagle's algorithm designed to prevent in TCP communication?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "Nagle's algorithm (RFC 896) prevents the 'small-packet problem' by buffering small outgoing payloads and combining them into a single larger segment until an ACK is received, preventing 40-byte headers for 1-byte keystrokes.",
            "Explain the purpose of Nagle's algorithm.",
            [
                ("To prevent sending many tiny packets with large header overhead by buffering small outgoing payloads until an ACK is received", True, "Nagle's algorithm improves efficiency by combining small packets into full MSS segments."),
                ("To encrypt passwords using hashing algorithms", False, "Nagle's algorithm is a buffering efficiency algorithm, not cryptography."),
                ("To assign dynamic IP addresses to printer servers", False, "DHCP assigns IP addresses."),
                ("To format computer hard drives during network boot", False, "Nagle's algorithm operates on outbound transport buffers.")
            ],
            ["tcp", "nagle-algorithm", "optimization"]
        ),
        (
            "TCP-025", "tcp-basics", "Which TCP socket option disables Nagle's algorithm for low-latency interactive applications (like gaming or real-time trading)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "Setting the 'TCP_NODELAY' socket option disables Nagle's algorithm, forcing segments to be transmitted immediately without buffering delays.",
            "Identify the socket option that disables Nagle's algorithm.",
            [
                ("TCP_NODELAY", True, "TCP_NODELAY disables Nagle's algorithm to prioritize immediate transmission over bandwidth efficiency."),
                ("SO_KEEPALIVE", False, "SO_KEEPALIVE sends periodic probes on idle connections."),
                ("SO_REUSEADDR", False, "SO_REUSEADDR allows binding to a port currently in TIME_WAIT."),
                ("TCP_MAXSEG", False, "TCP_MAXSEG sets the maximum segment size.")
            ],
            ["tcp", "tcp-nodelay", "socket-options"]
        ),
        (
            "TCP-026", "udp-communication", "Why does User Datagram Protocol (UDP) NOT implement a three-way handshake?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 40,
            "UDP is fundamentally connectionless. It simply wraps application data with an 8-byte header and sends it immediately to the network layer without establishing or maintaining session state.",
            "Explain why UDP operates without connection handshakes.",
            [
                ("UDP is connectionless; it transmits datagrams immediately without establishing or maintaining session state", True, "UDP eliminates handshake latency by treating every datagram as an independent transmission."),
                ("UDP was designed before handshakes were invented by mathematicians", False, "Handshakes existed in early ARPANET protocols prior to UDP."),
                ("UDP cables do not have enough copper wires to transmit handshakes", False, "Transport protocols run over the exact same physical network infrastructure."),
                ("Handshakes are strictly illegal in real-time gaming protocols", False, "Handshakes are not illegal; they simply introduce latency unsuited for real-time traffic.")
            ],
            ["udp", "connectionless", "transport-layer"]
        ),
        (
            "TCP-027", "tcp-basics", "What is the role of the 32-bit Acknowledgment Number in a TCP header during active data transfer?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "The Acknowledgment Number specifies the sequence number of the next byte of data that the receiver expects to receive from the sender.",
            "Explain the meaning of the TCP acknowledgment number during data transfer.",
            [
                ("It indicates the next byte sequence number the receiver is expecting to receive from the sender", True, "Acknowledgment numbers point forward to the next expected byte in the stream."),
                ("It counts the total number of errors detected in the physical copper cable", False, "Error counts are tracked by interface counters, not TCP ack numbers."),
                ("It indicates the price of the server in United States dollars", False, "TCP headers contain transport protocol metadata, not accounting data."),
                ("It records the serial number of the client's hard drive", False, "TCP headers do not store local hardware serial numbers.")
            ],
            ["tcp", "ack", "sequence-numbers"]
        ),
        (
            "TCP-028", "tcp-basics", "What is TCP 'Keep-Alive' and what is its primary purpose?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "TCP Keep-Alive sends small empty probe segments across an idle connection at periodic intervals to verify that the remote peer is still alive and responsive, and to prevent stateful NAT/firewalls from timing out the session.",
            "Explain the function of TCP Keep-Alive probes.",
            [
                ("Periodic empty probe segments sent on idle connections to verify the remote peer is reachable and keep firewall state tables open", True, "Keep-Alives maintain stateful firewall sessions and detect dead peers on long-lived connections."),
                ("A hardware feature that prevents server power cords from falling out", False, "Keep-Alive is a transport protocol mechanism, not a mechanical cord lock."),
                ("A software license that keeps an antivirus program updated", False, "Keep-Alives are TCP transport probes."),
                ("A protocol used to download video files across peer-to-peer networks", False, "BitTorrent is an application protocol; Keep-Alive is a socket feature.")
            ],
            ["tcp", "keep-alive", "firewalls", "state-table"]
        ),
        (
            "TCP-029", "tcp-flags", "In packet analysis, what does a sudden spike of TCP RST packets originating from a internal database server indicate?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 60,
            "A sudden surge of RST packets indicates either that incoming connection attempts are hitting a closed port (e.g. database service crashed or is down) or that an internal scanner/adversary is probing closed database ports.",
            "Analyze the operational meaning of high RST rates from a server.",
            [
                ("Incoming connections are hitting closed ports (e.g., database service is stopped or port scan underway)", True, "RST spikes indicate connection rejections from closed ports or service crashes."),
                ("The database server has successfully doubled its RAM storage", False, "RST packets are network error signals, not memory upgrades."),
                ("All data stored in the database has been securely encrypted with AES-256", False, "RST packets reject connections and do not indicate cryptographic encryption."),
                ("The network switches have switched from copper to optical fiber", False, "Switch physical media changes do not generate transport RST spikes.")
            ],
            ["tcp", "rst", "packet-analysis", "soc", "troubleshooting"]
        ),
        (
            "TCP-030", "tcp-basics", "What is the TCP 'Three-Way Handshake' timeout duration typically set to by operating systems when no response is received to an initial SYN?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "Operating systems retry sending the SYN with exponential backoff (e.g., after 1s, 3s, 6s) before aborting with a connection timeout after approximately 20 to 75 seconds if no SYN-ACK arrives.",
            "Understand TCP connection establishment timeout behavior.",
            [
                ("The OS retries the SYN packet multiple times with exponential backoff before timing out after approximately 20 to 75 seconds", True, "OS stacks retransmit SYN packets with increasing backoff intervals before terminating."),
                ("It times out immediately after 1 millisecond without retrying", False, "Immediate timeout would cause widespread failure over typical Internet latencies."),
                ("It waits indefinitely for 10 years until the server responds", False, "Kernel resources cannot be held indefinitely for failed connections."),
                ("It automatically reboots the router after 3 seconds", False, "Failed TCP handshakes do not cause hardware reboots.")
            ],
            ["tcp", "syn", "timeout", "exponential-backoff"]
        ),
        (
            "TCP-031", "tcp-basics", "What is the function of the TCP 'Checksum' field?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 40,
            "The 16-bit TCP Checksum verifies the integrity of the TCP header, payload data, and a 12-byte 'pseudo-header' (containing source IP, destination IP, protocol, and TCP length) to ensure data was not corrupted during transit.",
            "Explain the coverage of the TCP checksum.",
            [
                ("It verifies that the TCP header, payload, and IP pseudo-header were not corrupted in transit", True, "The TCP checksum includes a pseudo-header to ensure segments were not misdelivered to the wrong IP."),
                ("It encrypts the payload using SHA-256 hashing", False, "Checksums detect accidental transmission bit errors; they do not encrypt data."),
                ("It determines the physical weight of the Ethernet cable", False, "Checksums are mathematical calculations over digital bits."),
                ("It measures the air humidity inside the computer chassis", False, "Checksums are software calculations.")
            ],
            ["tcp", "checksum", "integrity"]
        ),
        (
            "TCP-032", "udp-communication", "Is the checksum field mandatory in standard IPv4 UDP headers?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "In IPv4, the UDP checksum is optional (though strongly recommended); a value of 0 indicates the checksum was omitted. In IPv6, however, the UDP checksum is strictly mandatory.",
            "Recall UDP checksum requirements across IPv4 and IPv6.",
            [
                ("It is optional in IPv4 (0 means omitted), but strictly mandatory in IPv6", True, "IPv4 made UDP checksum optional; IPv6 mandates it because IPv6 eliminated the Network layer header checksum."),
                ("It is mandatory in IPv4, but completely banned in IPv6", False, "IPv6 strictly requires the UDP checksum."),
                ("It is illegal under all RFC networking standards", False, "Checksums are standard integrity fields."),
                ("It only functions when computers are connected via Bluetooth", False, "UDP checksums function across all standard network interfaces.")
            ],
            ["udp", "checksum", "ipv4-vs-ipv6"]
        ),
        (
            "TCP-033", "tcp-basics", "What is 'Window Scaling' (RFC 7323) in TCP and why was it introduced?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "The standard TCP Window field is 16 bits, limiting maximum unacknowledged data to 65,535 bytes (64 KB). Window Scaling introduces a scale factor in options, expanding the effective window up to 1 GB for high-speed, high-latency networks (BDP).",
            "Explain why TCP Window Scaling was developed.",
            [
                ("It expands the 16-bit window limit beyond 64 KB up to 1 GB to utilize high-bandwidth, high-latency network links (High BDP)", True, "Window scaling allows modern high-speed networks to fully utilize available bandwidth-delay product."),
                ("It automatically magnifies the text font size on the user's desktop monitor", False, "Window scaling relates to buffer byte capacity, not graphical desktop display scaling."),
                ("It forces all Ethernet cables to transmit at 10 Mbps maximum", False, "Window scaling was created to support gigabit and 10-gigabit speeds."),
                ("It allows computers to download files without connecting to the Internet", False, "Window scaling is an active TCP communication option.")
            ],
            ["tcp", "window-scaling", "performance", "rfc7323"]
        ),
        (
            "TCP-034", "tcp-flags", "In port scanning terminology, what is a 'TCP FIN Scan' and how does an open port respond?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 2, 60,
            "In a FIN scan, the scanner sends an unsolicited FIN packet. According to RFC 793, a closed port responds with a RST, while an OPEN port ignores the packet and sends NO response. (This behavior allows stealth scanning on RFC-compliant Unix stacks).",
            "Analyze the mechanics of a stealth TCP FIN port scan.",
            [
                ("A closed port responds with RST, while an open port drops the packet and sends no response", True, "RFC 793 mandates that closed ports send RST to unsolicited FINs, while open ports discard them silently."),
                ("An open port responds with a SYN-ACK, while a closed port returns an ICMP Echo Reply", False, "A FIN packet will never elicit a SYN-ACK response."),
                ("Both open and closed ports immediately reboot the server", False, "Port scans do not reboot systems."),
                ("The scanner receives an email containing the server's root password", False, "Port scans discover open ports; they do not steal passwords via FIN responses.")
            ],
            ["tcp", "fin-scan", "port-scanning", "reconnaissance", "security"]
        ),
        (
            "TCP-035", "tcp-flags", "What is a 'TCP Xmas Scan'?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 45,
            "A Xmas (Christmas Tree) scan transmits packets with the FIN, PSH, and URG flags all set simultaneously ('lit up like a Christmas tree'), exploiting RFC 793 closed-port RST behavior for stealth reconnaissance.",
            "Identify the flags set in a TCP Xmas scan.",
            [
                ("A packet with FIN, PSH, and URG flags all set simultaneously", True, "Xmas scan lights up FIN, PSH, and URG flags to observe whether the target returns a RST."),
                ("A holiday email greeting card sent over SMTP port 25", False, "Xmas scan is a transport reconnaissance probe, not an email greeting."),
                ("A packet that plays Christmas music through the computer speakers", False, "Network packets transmit digital bits, not audio through speakers."),
                ("A routine automated backup script that runs only on December 25th", False, "Xmas scan is a security scanner probe technique.")
            ],
            ["tcp", "xmas-scan", "port-scanning", "reconnaissance"]
        ),
    ]
    save_questions("tcp_udp_and_transport.json", items)


def generate_dns_dhcp_app():
    items = [
        (
            "APP-001", "dns-resolution", "What is the difference between a Recursive DNS query and an Iterative DNS query?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "In a recursive query, the client demands that the local DNS resolver do all the work and return the final answer (or an error). In an iterative query, the queried nameserver returns the best referral it knows (next nameserver down the tree) so the querier can follow up.",
            "Contrast recursive and iterative DNS queries.",
            [
                ("A recursive query asks the resolver to find the complete final answer; an iterative query returns referrals to other nameservers", True, "Clients send recursive queries to resolvers; resolvers send iterative queries down the DNS hierarchy."),
                ("Recursive queries are unencrypted; iterative queries use military AES-256 encryption", False, "Standard DNS queries are unencrypted UDP port 53 regardless of query type."),
                ("Iterative queries only work over Bluetooth connections", False, "Iterative queries are standard DNS protocol operations across the Internet."),
                ("Recursive queries can only resolve .gov domain names", False, "Recursive resolvers resolve all valid top-level domains.")
            ],
            ["dns", "recursive-query", "iterative-query", "dns-resolution"]
        ),
        (
            "APP-002", "dns-resolution", "When a recursive DNS resolver receives a query for 'mail.example.com' with an empty cache, what server does it contact FIRST?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "The resolver begins at the top of the DNS hierarchy by contacting one of the 13 Root Nameserver clusters (using pre-configured root hints) to determine the authoritative nameservers for the '.com' Top-Level Domain (TLD).",
            "Trace the first step of cold-cache recursive DNS resolution.",
            [
                ("A DNS Root Nameserver (Root Hints)", True, "Cold resolution always starts at the DNS root zone to locate the appropriate TLD nameserver."),
                ("The authoritative nameserver for example.com directly", False, "The resolver cannot know where example.com is located until it queries the .com TLD server."),
                ("The user's local default gateway router", False, "The resolver is performing the recursive lookup on behalf of the client."),
                ("Google's public search engine web server", False, "DNS resolution uses DNS nameservers, not search engines.")
            ],
            ["dns", "root-nameservers", "dns-hierarchy"]
        ),
        (
            "APP-003", "dns-resolution", "What is the role of Time to Live (TTL) in a DNS resource record?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "TTL specifies the duration in seconds that a caching resolver is permitted to store and serve the DNS record locally before it must discard it and query the authoritative server again.",
            "Explain DNS Time to Live (TTL).",
            [
                ("It defines how long in seconds a resolver may cache the DNS record before re-querying the authoritative nameserver", True, "TTL balances fast cached query responses with timely updates when records change."),
                ("It specifies how many miles an electrical packet can travel before disappearing", False, "TTL in DNS is measured in seconds; in IP it is a hop count."),
                ("It forces the user's computer to reboot when the timer reaches zero", False, "DNS TTL only expires cached DNS records."),
                ("It limits the maximum file size of web downloads to 10 MB", False, "TTL has no relation to file download sizes.")
            ],
            ["dns", "ttl", "caching"]
        ),
        (
            "APP-004", "dns-record-types", "Which DNS record type maps an IPv4 address back to a hostname (Reverse DNS Lookup)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 35,
            "A PTR (Pointer) record maps an IP address back to its canonical domain name in the special 'in-addr.arpa' (IPv4) or 'ip6.arpa' (IPv6) reverse lookup zones.",
            "Identify reverse DNS lookup records.",
            [
                ("PTR record", True, "PTR records perform reverse DNS resolution (IP to domain name)."),
                ("A record", False, "A records perform forward resolution (domain name to IPv4)."),
                ("CNAME record", False, "CNAME maps an alias domain to another domain name."),
                ("SOA record", False, "SOA specifies authoritative zone parameters.")
            ],
            ["dns", "ptr-record", "reverse-dns"]
        ),
        (
            "APP-005", "dns-record-types", "Which DNS record type is commonly used by organizations to publish SPF (Sender Policy Framework) and DKIM keys to prevent email spoofing?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "TXT (Text) records allow domain owners to store arbitrary text strings, widely used for email authentication protocols like SPF, DKIM, and DMARC to combat phishing and spoofing.",
            "Identify the DNS record used for email security policies.",
            [
                ("TXT record", True, "TXT records host SPF, DKIM, and domain ownership verification strings."),
                ("A record", False, "A records store 32-bit IPv4 addresses."),
                ("PTR record", False, "PTR records are for reverse IP lookups."),
                ("NS record", False, "NS records list authoritative nameservers.")
            ],
            ["dns", "txt-record", "spf", "dkim", "email-security"]
        ),
        (
            "APP-006", "dhcp-process", "What happens during the 'Lease Renewal' phase when a DHCP client reaches 50% of its lease time (T1 timer)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "At the T1 timer (50% of lease duration), the client sends a unicast DHCPREQUEST directly to the issuing DHCP server requesting a lease renewal. If the server replies with DHCPACK, the lease is renewed.",
            "Explain DHCP T1 lease renewal behavior.",
            [
                ("The client sends a unicast DHCPREQUEST directly to the issuing DHCP server to extend its lease", True, "At 50% lease time (T1), the client attempts to renew directly with the original DHCP server via unicast."),
                ("The client immediately broadcasts to the entire world that its network card is broken", False, "Lease renewal is an ordinary background maintenance transaction."),
                ("The client deletes its operating system and reboots into BIOS", False, "DHCP renewal never affects disk storage or BIOS."),
                ("The client permanently changes its MAC address to random numbers", False, "Clients keep their hardware MAC address constant during DHCP renewal.")
            ],
            ["dhcp", "lease-renewal", "timers"]
        ),
        (
            "APP-007", "dhcp-process", "What is the role of a 'DHCP Relay Agent' (or Cisco 'ip helper-address') in an enterprise network?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "Routers do not forward Layer 2 broadcasts. A DHCP Relay Agent listens for local DHCP broadcast discovers on a client subnet and forwards them as unicast IP packets across routers to a centralized DHCP server on another subnet.",
            "Explain the purpose of a DHCP Relay Agent.",
            [
                ("It intercepts local client DHCP broadcast messages and forwards them as unicast packets to a DHCP server on a remote subnet", True, "DHCP relay agents allow a single centralized DHCP server to serve multiple remote subnets across routers."),
                ("It converts DHCP packets into encrypted SSH connections", False, "DHCP relay forwards standard UDP port 67/68 traffic."),
                ("It assigns physical Ethernet cable lengths to wall jacks", False, "DHCP relay is a router software feature."),
                ("It prevents users from accessing social media websites during lunch", False, "Content filters restrict websites, not DHCP relay agents.")
            ],
            ["dhcp", "dhcp-relay", "ip-helper", "routing"]
        ),
        (
            "APP-008", "dhcp-process", "What is a 'Rogue DHCP Server' and what security threat does it present?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 60,
            "A rogue DHCP server is an unauthorized DHCP service running on a network (accidentally via a misconfigured home router or maliciously by an attacker). It can provide false default gateways and DNS servers to perform Man-in-the-Middle (MitM) attacks.",
            "Analyze the threat posed by rogue DHCP servers.",
            [
                ("An unauthorized DHCP server that hands out false default gateways and DNS servers to conduct Man-in-the-Middle traffic interception", True, "Rogue DHCP allows an attacker to divert all client traffic through an adversarial gateway."),
                ("A DHCP server that runs out of disk storage memory during backup", False, "Resource exhaustion is not a rogue malicious server."),
                ("A server that charges employees money for every web page they visit", False, "Rogue DHCP is a network spoofing attack, not a billing mechanism."),
                ("A server that only assigns IP addresses to Apple MacBook laptops", False, "Rogue DHCP broadcasts affect all clients on the local broadcast domain.")
            ],
            ["dhcp", "rogue-dhcp", "mitm", "security", "threats"]
        ),
        (
            "APP-009", "dhcp-process", "Which switch security feature is specifically designed to block rogue DHCP servers by validating DHCP messages and filtering untrusted switch ports?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "DHCP Snooping is a Layer 2 switch security feature that designates switch ports as either 'trusted' (connected to authorized DHCP servers) or 'untrusted' (connected to client endpoints), immediately dropping unauthorized DHCP offers from untrusted ports.",
            "Identify the switch security feature protecting against rogue DHCP.",
            [
                ("DHCP Snooping", True, "DHCP Snooping filters unauthorized DHCP server replies and builds the snooping binding database."),
                ("Port Mirroring (SPAN)", False, "Port mirroring copies packets for analysis; it does not filter or block DHCP offers."),
                ("Dynamic Trunking Protocol (DTP)", False, "DTP negotiates switch trunk links."),
                ("Spanning Tree Protocol (STP)", False, "STP prevents Layer 2 switching loops.")
            ],
            ["dhcp", "dhcp-snooping", "switch-security", "defense"]
        ),
        (
            "APP-010", "http-methods", "What is the primary difference between the HTTP GET and POST request methods?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "GET requests retrieve data and encode parameters inside the URL query string (should be idempotent without changing server state). POST sends data inside the request message body, typically modifying server state (e.g. creating records or submitting credentials).",
            "Contrast HTTP GET and POST methods.",
            [
                ("GET retrieves data and includes parameters in the URL; POST transmits data inside the request body and typically alters server state", True, "GET is intended for safe retrieval; POST carries payload data in the message body for processing."),
                ("GET encrypts data with AES-256; POST transmits in plaintext", False, "Encryption is handled by TLS (HTTPS), not by the HTTP method."),
                ("GET can only be used on smartphones; POST can only be used on servers", False, "Both are universal HTTP methods supported across all devices."),
                ("POST can only transfer image files", False, "POST transfers JSON, form data, XML, binary, and all MIME types.")
            ],
            ["http", "http-methods", "get-vs-post"]
        ),
        (
            "APP-011", "http-methods", "Which HTTP method is specifically intended to upload or completely replace a targeted resource at a known URI?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "The HTTP PUT method requests that the enclosed entity be stored under the supplied Request-URI. If the resource already exists, PUT replaces it entirely.",
            "Identify the HTTP replacement method.",
            [
                ("PUT", True, "PUT replaces the resource at the target URL with the supplied request payload."),
                ("GET", False, "GET retrieves data without modifying it."),
                ("DELETE", False, "DELETE removes the resource."),
                ("HEAD", False, "HEAD retrieves only headers without the message body.")
            ],
            ["http", "http-methods", "put"]
        ),
        (
            "APP-012", "http-methods", "What does the HTTP HEAD method do compared to a standard GET request?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 40,
            "The HEAD method requests the exact same headers that a GET request would return, but the server does NOT return the message body. This is used to check resource headers, content length, or caching headers efficiently.",
            "Explain the behavior of the HTTP HEAD method.",
            [
                ("It returns the identical HTTP headers that a GET request would return, but omits the response body", True, "HEAD is used to inspect headers and check resource validity without downloading full payloads."),
                ("It forces the server to reboot immediately", False, "HEAD is a standard read-only inspection request."),
                ("It encrypts the user's hard drive with ransomware", False, "HEAD is a benign RFC-compliant HTTP method."),
                ("It deletes all user accounts on the web server", False, "HEAD cannot modify server data.")
            ],
            ["http", "http-methods", "head"]
        ),
        (
            "APP-013", "http-status-codes", "What does an HTTP '301 Moved Permanently' status code indicate to a client browser?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 40,
            "A 301 status code indicates that the requested resource has been permanently assigned a new URI. The response includes a 'Location' header pointing to the new URL, which search engines and browsers should cache.",
            "Interpret HTTP 301 redirection.",
            [
                ("The requested resource has been permanently moved to a new URI specified in the Location header", True, "301 indicates permanent redirection, prompting clients and search engines to update their bookmarks/indexes."),
                ("The user entered an incorrect account password", False, "401 Unauthorized indicates authentication failure."),
                ("The server hardware has caught fire", False, "301 is an expected redirection response."),
                ("The webpage has been deleted forever with no replacement", False, "410 Gone indicates permanent removal without redirection.")
            ],
            ["http", "http-status-codes", "redirect"]
        ),
        (
            "APP-014", "http-status-codes", "What is the difference between an HTTP '401 Unauthorized' and an HTTP '403 Forbidden' response?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "401 Unauthorized indicates that the client has not provided valid authentication credentials (authentication failure). 403 Forbidden means the server recognizes the client's identity, but the client does not have permission to access the resource (authorization failure).",
            "Differentiate HTTP 401 and 403 status codes.",
            [
                ("401 indicates missing or invalid authentication credentials; 403 means the user is authenticated but lacks authorized permission to access the resource", True, "401 is an authentication problem; 403 is an authorization/permission refusal."),
                ("401 is used only in Europe; 403 is used only in North America", False, "HTTP status codes are universal global standards."),
                ("403 means the file was deleted; 401 means the file was renamed", False, "These status codes govern security access, not file existence."),
                ("401 means the client's monitor is too small", False, "Status codes convey web server response states.")
            ],
            ["http", "http-status-codes", "security", "authorization"]
        ),
        (
            "APP-015", "http-status-codes", "What does an HTTP '500 Internal Server Error' status code indicate?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 40,
            "A 500 status code indicates that the server encountered an unexpected condition or software exception that prevented it from fulfilling the request, signaling a server-side bug or application crash.",
            "Interpret HTTP 500 Internal Server Error.",
            [
                ("The web server encountered an unexpected software exception or crash that prevented fulfilling the request", True, "500 indicates a server-side unhandled exception or backend failure."),
                ("The client disconnected their Ethernet cable before receiving data", False, "500 is sent by the server, proving connectivity exists."),
                ("The requested URL does not exist on the server", False, "Missing URLs return 404 Not Found."),
                ("The user's password contains too few capital letters", False, "Authentication validation returns 400 Bad Request or 422 Unprocessable Entity.")
            ],
            ["http", "http-status-codes", "troubleshooting"]
        ),
        (
            "APP-016", "http-status-codes", "What does an HTTP '502 Bad Gateway' status code mean when received from a reverse proxy or load balancer?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "A 502 Bad Gateway means that the gateway or reverse proxy server (such as Nginx or an AWS ALB) received an invalid response or connection refusal from the upstream backend application server while attempting to fulfill the request.",
            "Interpret HTTP 502 Bad Gateway.",
            [
                ("The reverse proxy or gateway received an invalid response or connection failure from the upstream backend application server", True, "502 signals that the reverse proxy could not communicate properly with the backend application."),
                ("The client entered an invalid credit card number", False, "Payment processing errors return application-specific 4xx errors."),
                ("The user's Wi-Fi router has overheated", False, "502 is generated by remote web proxies, not local Wi-Fi hardware."),
                ("The website requires the user to install a special browser plugin", False, "502 is an infrastructure error, not a client plugin prompt.")
            ],
            ["http", "http-status-codes", "reverse-proxy", "load-balancer"]
        ),
        (
            "APP-017", "https-intermediate", "What two core security objectives are provided by Hypertext Transfer Protocol Secure (HTTPS)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "HTTPS uses TLS/SSL to provide Confidentiality (encrypting traffic to prevent eavesdropping), Integrity (preventing in-flight tampering), and Authentication (verifying server identity via digital certificates).",
            "Identify the security guarantees of HTTPS.",
            [
                ("Data encryption (confidentiality) and server identity verification via digital certificates (authentication)", True, "HTTPS prevents eavesdropping, tampering, and impersonation."),
                ("Free wireless Internet access and unlimited battery life for laptops", False, "HTTPS is a cryptographic transport protocol with no battery benefits."),
                ("Permanent immunity from physical hardware theft", False, "Cryptographic software cannot prevent physical device theft."),
                ("Guaranteed 1000 Mbps download speed on any network", False, "HTTPS adds slight cryptographic overhead and does not increase line speed.")
            ],
            ["https", "security", "tls", "encryption"]
        ),
        (
            "APP-018", "tls-basics", "In the TLS handshake, how is the symmetric session key established between the client and the server?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "The client and server use asymmetric cryptography (traditionally RSA key exchange or modern Ephemeral Diffie-Hellman / ECDHE) to securely agree upon a shared secret, from which symmetric session keys (like AES-GCM) are derived for high-speed bulk data encryption.",
            "Explain key exchange mechanics in the TLS handshake.",
            [
                ("Asymmetric cryptography (e.g. ECDHE or RSA) is used to securely agree on a shared secret, which derives symmetric session keys for bulk data encryption", True, "Asymmetric encryption solves key exchange; symmetric encryption performs bulk data transfer efficiently."),
                ("The server transmits its private key in clear plaintext over UDP port 80", False, "Private keys must never be transmitted; doing so would destroy all security."),
                ("Both parties use their hardware MAC addresses as the encryption password", False, "MAC addresses are public identifiers, not secure cryptographic keys."),
                ("The symmetric key is printed on a physical piece of paper and mailed via postal service", False, "Key establishment occurs digitally in milliseconds over the network.")
            ],
            ["tls", "cryptography", "key-exchange", "symmetric-vs-asymmetric"]
        ),
        (
            "APP-019", "tls-basics", "What is the primary role of a digital SSL/TLS Certificate on an HTTPS web server?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "The digital certificate binds the web server's public key to its verified domain identity, signed by a trusted third-party Certificate Authority (CA) so client browsers can verify they are communicating with the genuine server.",
            "Explain the role of TLS digital certificates.",
            [
                ("It binds the server's public key to its domain name, cryptographically signed by a trusted Certificate Authority (CA)", True, "Certificates enable clients to authenticate the server and obtain its verified public key."),
                ("It allows the web server to access the user's personal webcam without permission", False, "Certificates are cryptographic identity files, not webcam malware."),
                ("It provides insurance payments if the web server experiences a power outage", False, "Certificates verify identity; they are not insurance contracts."),
                ("It compresses all HTML files into MP3 music recordings", False, "Certificates contain cryptographic keys and metadata, not audio compression.")
            ],
            ["tls", "certificates", "pki", "authentication"]
        ),
        (
            "APP-020", "tls-basics", "What security vulnerability occurs if an application or user ignores a 'Certificate Warning: The security certificate presented by this website was not issued by a trusted certificate authority'?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 55,
            "Ignoring untrusted certificate warnings leaves the user completely vulnerable to a Man-in-the-Middle (MitM) attack, where an adversary intercepts the encrypted connection, presents a forged self-signed certificate, and inspects or alters credentials in transit.",
            "Analyze the risks of bypassing TLS certificate validation.",
            [
                ("An adversary conducting a Man-in-the-Middle attack can intercept, decrypt, and manipulate all session traffic", True, "Certificate warnings alert users that the session may be intercepted by an untrusted entity."),
                ("The user's computer monitor will immediately turn off permanently", False, "Certificate errors are browser security alerts, not hardware failures."),
                ("The web browser will automatically format the host operating system drive", False, "Browsers protect users; they do not destroy local operating systems."),
                ("All local network switches will shut down", False, "TLS certificate validation is an end-to-end application layer function.")
            ],
            ["tls", "mitm", "certificates", "security", "soc"]
        ),
        (
            "APP-021", "tls-basics", "What major architectural improvement was introduced in TLS version 1.3 compared to TLS 1.2?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 55,
            "TLS 1.3 removed obsolete, insecure cryptographic algorithms (MD5, SHA-1, RC4, static RSA key exchange), enforced Perfect Forward Secrecy (PFS), and reduced handshake latency from 2 round-trips (2-RTT) to 1 round-trip (1-RTT).",
            "Identify architectural advances in TLS 1.3.",
            [
                ("It reduced handshake latency from 2-RTT to 1-RTT and removed legacy insecure ciphers, mandating Perfect Forward Secrecy", True, "TLS 1.3 is faster (1-RTT) and strictly mandates modern secure ciphers with PFS."),
                ("It completely removed all encryption from HTTPS", False, "TLS 1.3 strengthened encryption."),
                ("It requires all packets to be transmitted over dial-up telephone modems", False, "TLS 1.3 is optimized for modern high-speed broadband and mobile networks."),
                ("It forces web browsers to reload web pages every 2 seconds", False, "TLS 1.3 establishes persistent session tunnels.")
            ],
            ["tls", "tls1.3", "pfs", "security"]
        ),
        (
            "APP-022", "tls-basics", "What is 'Perfect Forward Secrecy' (PFS) in TLS communication?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 60,
            "PFS ensures that even if a server's long-term private key is compromised in the future, past recorded encrypted communications cannot be decrypted, because each session used unique ephemeral session keys (e.g. via ECDHE).",
            "Define Perfect Forward Secrecy.",
            [
                ("A cryptographic feature where compromising the server's long-term private key does not compromise past recorded sessions", True, "PFS uses ephemeral Diffie-Hellman keys so that each session key is independent and discarded after use."),
                ("A feature that makes all computer passwords publicly visible on Twitter", False, "PFS protects confidential communications."),
                ("A technique that guarantees Internet access during deep space travel", False, "PFS is a cryptographic key exchange property."),
                ("A guarantee that an enterprise web server will never crash", False, "PFS prevents retrospective decryption; it is not high-availability hardware.")
            ],
            ["tls", "pfs", "cryptography", "security"]
        ),
        (
            "APP-023", "ssh-intermediate", "During an initial SSH connection to a new server, the client displays: 'The authenticity of host cannot be established. RSA key fingerprint is... Are you sure you want to continue connecting?' What is the client verifying?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "The client is displaying the server's public Host Key fingerprint, asking the administrator to verify that they are connecting to the genuine server and not an imposter conducting a Man-in-the-Middle attack (Trust On First Use / TOFU).",
            "Explain SSH host key fingerprint verification.",
            [
                ("The public host key of the remote server to prevent connecting to an imposter conducting a Man-in-the-Middle attack", True, "SSH relies on Host Keys to authenticate server identity on the first connection (TOFU model)."),
                ("Whether the client's home printer has enough paper", False, "Host keys verify remote server cryptographic identity."),
                ("Whether the remote server is running Windows XP", False, "Fingerprints identify cryptographic keys, not OS brand names."),
                ("The remaining battery percentage of the client laptop", False, "SSH terminal prompts do not display hardware battery levels.")
            ],
            ["ssh", "host-keys", "authentication", "tofu"]
        ),
        (
            "APP-024", "ssh-intermediate", "Where does an SSH server on Linux store the public keys of authorized clients allowed to log in without passwords?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "Public keys for passwordless key-based SSH authentication are stored in the user's home directory in the file '~/.ssh/authorized_keys'.",
            "Recall the location of authorized SSH public keys on Linux.",
            [
                ("~/.ssh/authorized_keys", True, "The authorized_keys file contains public keys permitted to log in as that user."),
                ("/etc/shadow", False, "/etc/shadow stores hashed account passwords."),
                ("/var/log/syslog", False, "/var/log/syslog is the system event log."),
                ("~/.ssh/id_rsa", False, "~/.ssh/id_rsa is the client's PRIVATE key, which must remain secret.")
            ],
            ["ssh", "linux", "authorized-keys", "key-based-auth"]
        ),
        (
            "APP-025", "ssh-intermediate", "What permissions must the private key file (e.g. ~/.ssh/id_rsa) have on a client machine for the OpenSSH client to allow its use?",
            "SINGLE_CHOICE", "INTERMEDIATE", "APPLY", 1, 45,
            "OpenSSH strictly rejects private keys that are accessible by other users. The private key must have permissions restricted to the owner only (typically chmod 600 or 400), or SSH will refuse to use it.",
            "Recall required filesystem permissions for SSH private keys.",
            [
                ("Strictly readable/writable by the owner only (e.g., chmod 600 or 400)", True, "OpenSSH blocks key usage if permissions are too open (e.g., 777 or group-readable)."),
                ("World readable and writable by everyone (chmod 777)", False, "chmod 777 causes OpenSSH to abort with 'Permissions are too open'."),
                ("Execution-only permissions with no read access", False, "The client must be able to read the key file."),
                ("No permissions required; SSH keys can be stored anywhere publicly", False, "Private keys must be protected from unauthorized local user access.")
            ],
            ["ssh", "file-permissions", "linux", "security"]
        ),
        (
            "APP-026", "dns-resolution", "What is 'DNS Cache Poisoning' (DNS Spoofing)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "ANALYZE", 2, 55,
            "DNS cache poisoning occurs when an attacker injects fraudulent DNS records into a caching resolver (e.g. by guessing transaction IDs/ports in Kaminsky attacks), causing all subsequent client queries for legitimate domains (e.g. bank.com) to resolve to an attacker's malicious IP.",
            "Analyze the threat of DNS cache poisoning.",
            [
                ("Injecting fraudulent DNS mapping records into a resolver's cache, redirecting users seeking legitimate sites to malicious servers", True, "Cache poisoning diverts user traffic at scale by corrupting the resolver's cached records."),
                ("Physically pouring poison on the server room cooling pipes", False, "DNS cache poisoning is a logical cyber attack on resolver records."),
                ("A denial-of-service attack that floods a server with 500 million empty emails", False, "Email flooding is mail bombing, not DNS spoofing."),
                ("A bug that causes DNS servers to delete all consonants from domain names", False, "Cache poisoning forges IP address resolutions.")
            ],
            ["dns", "cache-poisoning", "spoofing", "security", "threats"]
        ),
        (
            "APP-027", "dns-resolution", "Which security protocol adds cryptographic signatures to DNS records to protect resolvers against forged or poisoned DNS responses?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 1, 45,
            "Domain Name System Security Extensions (DNSSEC) uses public-key cryptography to digitally sign DNS records (RRSIG, DNSKEY, DS records), allowing resolvers to cryptographically verify data authenticity and integrity.",
            "Identify the protocol providing digital signatures for DNS.",
            [
                ("DNSSEC (DNS Security Extensions)", True, "DNSSEC validates the authenticity and integrity of DNS responses using digital signatures."),
                ("DHCP Snooping", False, "DHCP snooping protects Layer 2 switches from rogue DHCP."),
                ("HTTPS", False, "HTTPS encrypts web application traffic; it does not sign raw DNS zone records."),
                ("SNMPv3", False, "SNMPv3 is for network device management.")
            ],
            ["dns", "dnssec", "cryptography", "security"]
        ),
        (
            "APP-028", "http-methods", "What is an 'idempotent' HTTP method?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "An idempotent HTTP method is one where making multiple identical requests has the exact same effect on the server state as making a single request (e.g., GET, PUT, and DELETE are idempotent; POST is not).",
            "Define idempotency in HTTP protocol design.",
            [
                ("A method where executing multiple identical requests produces the exact same server state as a single request", True, "Methods like GET, PUT, and DELETE are idempotent; repeating them does not create duplicate entries."),
                ("A method that can only be executed by users named 'Ida'", False, "Idempotency is a mathematical and computer science property."),
                ("A method that automatically formats the client's hard drive", False, "HTTP methods do not format client drives."),
                ("A method that is strictly forbidden by RFC standards", False, "Idempotence is an essential design property defined in RFC 7231.")
            ],
            ["http", "idempotent", "api-design", "rest"]
        ),
        (
            "APP-029", "https-intermediate", "What is 'HTTP Strict Transport Security' (HSTS / RFC 6797)?",
            "SINGLE_CHOICE", "INTERMEDIATE", "UNDERSTAND", 2, 50,
            "HSTS is a web security response header ('Strict-Transport-Security') that instructs web browsers to communicate with the website EXCLUSIVELY over encrypted HTTPS connections, preventing SSL-stripping attacks.",
            "Explain the defensive purpose of HSTS.",
            [
                ("A security header instructing browsers to automatically convert all HTTP requests to secure HTTPS and refuse unencrypted connections", True, "HSTS protects users from SSL-stripping MitM attacks by enforcing HTTPS in the browser."),
                ("A protocol used to track user keystrokes for marketing surveys", False, "HSTS enforces HTTPS; it is not a keystroke logger."),
                ("A hardware feature that prevents servers from overheating", False, "HSTS is an HTTP header directive."),
                ("A tool that increases computer RAM memory", False, "Software headers do not increase hardware RAM.")
            ],
            ["https", "hsts", "web-security", "defense"]
        ),
        (
            "APP-030", "dns-record-types", "Which DNS record type specifies the location (hostname and port) of servers for specific services, widely used by Active Directory, SIP VoIP, and XMPP?",
            "SINGLE_CHOICE", "INTERMEDIATE", "REMEMBER", 1, 40,
            "SRV (Service) records define the hostname, port number, priority, and weight for specific services (e.g., _ldap._tcp.example.com), enabling clients to discover service endpoints dynamically.",
            "Identify the DNS record used for service discovery.",
            [
                ("SRV record", True, "SRV records identify hostnames and port numbers for specific application services."),
                ("A record", False, "A records provide IP addresses only, without port numbers."),
                ("MX record", False, "MX records specify mail servers only."),
                ("CNAME record", False, "CNAME provides alias redirection to another domain name.")
            ],
            ["dns", "srv-record", "service-discovery", "active-directory"]
        ),
    ]
    save_questions("dns_dhcp_and_application.json", items)


if __name__ == "__main__":
    generate_tcp_udp_transport()
    generate_dns_dhcp_app()
