#!/usr/bin/env python3
"""
NexoraNet Advanced Question Bank Generator - Part 2.
Generates:
3. reconnaissance_and_scanning_detection.json (30 questions)
4. detection_engineering_and_indicators.json (35 questions)
5. incident_investigation_and_soc.json (35 questions)
Completes the full 485-question NexoraNet Question Bank!
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


def generate_reconnaissance_detection():
    items = [
        (
            "RECON-001", "port-scanning-concepts",
            "In network reconnaissance, what distinguishes a 'Horizontal Port Scan' from a 'Vertical Port Scan'?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A Horizontal scan probes a single specific port (e.g. port 445 SMB) across many different target IP addresses to find vulnerable systems. A Vertical scan probes many different ports (e.g. ports 1 to 1000) on a single specific target host.",
            "Differentiate horizontal and vertical port scanning patterns.",
            [
                ("Horizontal scans probe one specific port across many IP addresses; vertical scans probe many ports on a single IP address", True, "Horizontal scans search across subnets for a specific service; vertical scans enumerate services on a single host."),
                ("Horizontal scans use optical fiber; vertical scans use copper cabling", False, "Scanning patterns describe logical target selection, not physical media."),
                ("Vertical scans are only conducted by government space satellites", False, "Port scans are executed by network software utilities like Nmap."),
                ("Horizontal scans can only be run on laptops sitting flat on a table", False, "These are topological directional metaphors.")
            ],
            ["reconnaissance", "port-scanning", "horizontal-scan", "vertical-scan", "soc"]
        ),
        (
            "RECON-002", "port-scanning-concepts",
            "How does a 'TCP SYN Stealth Scan' (Nmap -sS / Half-Open Scan) discover open ports without completing the three-way handshake?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "The scanner sends a SYN. If the port is open, the target replies with SYN-ACK. Instead of sending the final ACK to establish the session, the scanner immediately sends a RST (Reset) packet to abort the connection, preventing full application logging.",
            "Explain the mechanics of a TCP half-open SYN scan.",
            [
                ("The scanner sends a SYN; upon receiving a SYN-ACK (open port), it immediately sends a RST to abort the handshake before completion", True, "Tearing down the handshake with RST avoids completing the connection, evading older application-level connection logs."),
                ("The scanner formats the target's operating system with an automated exploit", False, "Port scans query port status; they do not format operating systems."),
                ("The scanner downloads all private files from the server's desktop", False, "Port scanning discovers open ports, not file contents."),
                ("The scanner turns off the target server's cooling fans", False, "Scanning does not alter hardware cooling.")
            ],
            ["reconnaissance", "syn-scan", "half-open", "nmap", "security"]
        ),
        (
            "RECON-003", "port-scanning-concepts",
            "What is a 'TCP Connect() Scan' (Nmap -sT) and why is it more easily detected by defensive logging systems than a SYN scan?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A TCP Connect scan uses the operating system's standard connect() system call to complete the full 3-way handshake (SYN, SYN-ACK, ACK). Because the connection fully completes, the application process logs the connection before it is closed.",
            "Explain TCP Connect scan mechanics and detection visibility.",
            [
                ("It completes the full three-way handshake using the OS network API, causing application services to log the completed connection", True, "Full connection establishment generates system and application logs on the target server."),
                ("It transmits physical electrical sparks across the Ethernet jack", False, "Software port scans do not cause physical electrical sparks."),
                ("It requires all network switches to restart every 30 seconds", False, "Switches forward TCP frames without restarting."),
                ("It cannot scan any ports higher than port 10", False, "Connect scans evaluate any port from 1 to 65535.")
            ],
            ["reconnaissance", "connect-scan", "nmap", "logging", "detection"]
        ),
        (
            "RECON-004", "service-enumeration-concepts",
            "What is 'Banner Grabbing' during network reconnaissance?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 45,
            "Banner grabbing is an enumeration technique where a scanner connects to an open service port and captures the initial greeting text banner returned by the server, revealing exact software brand names, operating system types, and version numbers (e.g. Apache/2.4.41 Ubuntu).",
            "Define service banner grabbing.",
            [
                ("Connecting to an open service port to read the initial greeting message, revealing application names and version details", True, "Service banners provide exact version numbers that adversaries and auditors use to look up known CVE vulnerabilities."),
                ("Physically pulling down cloth marketing banners outside a corporate headquarters", False, "Banner grabbing is a network protocol reconnaissance technique."),
                ("A tool that prevents users from downloading web banner advertisements", False, "Ad blockers block web ads; banner grabbing reads service greetings."),
                ("An algorithm used to compress image graphics files", False, "Banner grabbing reads textual network protocol headers.")
            ],
            ["reconnaissance", "service-enumeration", "banner-grabbing", "cve"]
        ),
        (
            "RECON-005", "reconnaissance-detection",
            "Which network telemetry indicator observed on an internal core switch most strongly suggests an ongoing port scan?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "A massive, abnormal ratio of outbound TCP SYN packets with zero corresponding data payloads, accompanied by a high percentage of RST/ACK connection rejections or ICMP Port Unreachable responses across hundreds of ports, is the hallmark of an active port scan.",
            "Identify telemetry indicators of automated port scans.",
            [
                ("A high volume of outbound SYN packets across diverse ports with a high ratio of RST connection rejections and zero data payload", True, "Port scans generate rapid connection attempts across non-listening ports, resulting in elevated RST response rates."),
                ("A user successfully streaming an educational video on YouTube", False, "Streaming video generates continuous incoming data streams, not port sweeps."),
                ("A server backing up encrypted database files to an authorized storage NAS", False, "Scheduled backups generate high sustained throughput to a single IP/port."),
                ("A workstation synchronizing its clock with an NTP server once an hour", False, "NTP generates a single periodic UDP packet.")
            ],
            ["reconnaissance-detection", "port-scanning", "soc", "telemetry", "anomalous-traffic"]
        ),
        (
            "RECON-006", "service-enumeration-concepts",
            "How do tools like Nmap perform 'OS Fingerprinting' without having authenticated access to a target system?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Different operating system network stacks implement RFC standards with subtle nuances. Scanners send customized probes (with specific TCP options, window sizes, TTLs, and flag combinations) and compare the exact response quirks against a database of known OS fingerprint signatures.",
            "Explain remote operating system fingerprinting techniques.",
            [
                ("By analyzing subtle quirks in how the target's network stack responds to specific TCP options, window sizes, TTLs, and flags", True, "TCP/IP stack fingerprinting examines implementation differences across Windows, Linux, BSD, and Cisco IOS."),
                ("By reading the user's personal diary stored on the desktop", False, "Remote fingerprinting evaluates network packet responses, not local file access."),
                ("By measuring the physical weight of the server equipment rack", False, "Physical weight cannot be measured over network packets."),
                ("By guessing the brand name of the computer monitor", False, "Stack fingerprinting identifies operating system kernels.")
            ],
            ["reconnaissance", "os-fingerprinting", "nmap", "tcp-options"]
        ),
        (
            "RECON-007", "reconnaissance-detection",
            "An analyst reviews firewall logs and notices a single external IP sending TCP SYN packets to port 22 on 500 different internal IP addresses within 30 seconds. What activity is this?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 50,
            "This is a Horizontal Port Sweep targeting SSH (port 22). The adversary is searching across the entire subnet to discover which specific hosts have SSH exposed for subsequent brute-force attacks.",
            "Analyze horizontal port sweep attacks.",
            [
                ("A horizontal port sweep searching for exposed SSH services across the subnet", True, "Probing one specific port across hundreds of hosts is a horizontal sweep to find vulnerable targets."),
                ("A vertical port scan enumerating all services on a single database server", False, "A vertical scan targets one IP across many ports, not many IPs on one port."),
                ("Normal DHCP IP address allocation behavior", False, "DHCP operates locally via broadcast, not external TCP SYN scans."),
                ("An authorized Windows cumulative patch installation", False, "Windows updates do not sweep subnets on port 22.")
            ],
            ["reconnaissance-detection", "horizontal-sweep", "ssh", "soc", "firewall-logs"]
        ),
        (
            "RECON-008", "port-scanning-concepts",
            "Why is a UDP Port Scan typically much slower to execute than a TCP SYN scan?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "UDP has no three-way handshake or positive acknowledgment for open ports. When a UDP port is closed, the host sends an ICMP Port Unreachable error. However, modern operating systems strictly rate-limit ICMP error generation (e.g. 1 per second in Linux), forcing the scanner to wait.",
            "Explain why UDP port scans take significantly longer to complete.",
            [
                ("Open ports often send no reply, and operating systems strictly rate-limit outgoing ICMP Port Unreachable errors for closed ports", True, "RFC 1812 mandates ICMP error rate-limiting, capping UDP scan speed to the OS ICMP generation rate."),
                ("UDP packets can only travel at 1 mile per hour across copper wires", False, "UDP packets travel at standard propagation speeds."),
                ("UDP port scans require manual written approval from the United Nations", False, "Scanning tools are automated software utilities."),
                ("UDP ports do not exist on computers manufactured after 2010", False, "UDP is a core Internet transport protocol supported on all modern systems.")
            ],
            ["reconnaissance", "udp-scan", "icmp-rate-limiting", "performance"]
        ),
        (
            "RECON-009", "reconnaissance-detection",
            "In Snort/Suricata intrusion detection rule writing, which rule header option specifies the network traffic direction?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 35,
            "The direction operator '->' (unidirectional) specifies traffic traveling from source to destination. The operator '<>' (bidirectional) evaluates traffic flowing in both directions.",
            "Identify the direction operators in Snort/Suricata rules.",
            [
                ("-> (unidirectional) and <> (bidirectional)", True, "These operators define the traffic flow direction relative to source and destination IP/port definitions."),
                ("== and !=", False, "These are comparison operators in programming, not Snort rule directional headers."),
                (">> and <<", False, "These are bitwise shift operators."),
                ("TCP and UDP", False, "TCP and UDP are protocol specifications.")
            ],
            ["detection-rules", "snort", "suricata", "rule-syntax"]
        ),
        (
            "RECON-010", "reconnaissance-detection",
            "What does a 'Null Scan' (Nmap -sN) send, and what response is expected from an open port on an RFC-compliant Unix stack?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "A Null scan sends a TCP packet with zero control flags set (all flag bits 0). Under RFC 793, an open port silently drops the invalid packet with NO response, whereas a closed port returns a RST.",
            "Explain the mechanics of a TCP Null scan.",
            [
                ("It sends a packet with no flags set (all zero); an open port drops it silently with no response, while a closed port returns RST", True, "Null scans exploit RFC 793 requirements that closed ports send RST while open ports ignore flagless packets."),
                ("It sends an encrypted email to the system administrator", False, "Null scan sends raw transport segments without payload."),
                ("It forces all server cooling fans to run at maximum speed", False, "Scanning does not alter hardware cooling firmware."),
                ("It changes the server's IP address to 0.0.0.0", False, "Null scan tests port states without altering IP configuration.")
            ],
            ["reconnaissance", "null-scan", "nmap", "tcp-flags"]
        ),
        (
            "RECON-011", "port-scanning-concepts",
            "What is 'Decoy Scanning' (Nmap -D) in network penetration testing?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Decoy scanning allows the attacker to interleave their real IP address with multiple spoofed decoy IP addresses in the scan stream, making it difficult for target security analysts and firewalls to determine which IP was the true scanner.",
            "Explain the purpose of decoy scanning in network reconnaissance.",
            [
                ("Mixing the attacker's real IP with multiple spoofed decoy IPs in the scan stream to conceal the true source of the scan", True, "Decoys flood firewall and IDS logs with alerts from multiple innocent IPs, hiding the real attacker among the noise."),
                ("Using wooden dummy computers to distract datacenter security guards", False, "This is physical deception, not network decoy scanning."),
                ("A tool that automatically deletes all user browser cookies", False, "Decoy scanning is a network packet generation technique."),
                ("A protocol used to download video games across torrent networks", False, "Decoy scanning is an Nmap reconnaissance feature.")
            ],
            ["reconnaissance", "decoy-scan", "nmap", "evasion", "soc"]
        ),
        (
            "RECON-012", "service-enumeration-concepts",
            "When performing service enumeration against a web server, what information is standardly revealed by the 'Server' HTTP response header?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 40,
            "The 'Server' response header typically identifies the web server software name and version (e.g. 'Server: Apache/2.4.41 (Ubuntu)' or 'Server: nginx/1.18.0'), aiding administrators and adversaries in identifying the backend technology stack.",
            "Identify information disclosed by the HTTP Server header.",
            [
                ("The web server software name, version number, and underlying operating system distribution", True, "The Server header discloses web daemon software and version details unless explicitly suppressed or disguised."),
                ("The personal home address of the web developer", False, "HTTP headers carry technical server metadata, not personal residential addresses."),
                ("The secret master password for the MySQL database", False, "Server headers do not disclose backend database credentials."),
                ("The physical room temperature of the datacenter", False, "Server headers do not report ambient environmental thermals.")
            ],
            ["http", "server-header", "banner-grabbing", "information-disclosure"]
        ),
        (
            "RECON-013", "reconnaissance-detection",
            "Why is 'Slow and Low' scanning (scanning ports over days or weeks with randomized delays) used by advanced threat actors?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 55,
            "Slow and low scanning spaces out probes over extended time windows to stay below the threshold limits of automated rate-based intrusion detection systems (e.g. alerts triggering on $> 10$ port probes per second), avoiding automated blocking.",
            "Analyze evasion of threshold-based detection via slow scanning.",
            [
                ("To evade threshold-based IDS/IPS alert rules that look for rapid bursts of connection attempts within short time windows", True, "By spacing probes across minutes or hours, slow scans evade simple rate-limiting detection thresholds."),
                ("Because the attacker's computer has an extremely slow dial-up modem", False, "Slow scanning is an intentional stealth choice by modern adversaries."),
                ("Because scanning faster than 10 packets per second is physically impossible", False, "Modern tools like masscan can scan millions of packets per second."),
                ("To conserve electrical battery power on the victim server", False, "Adversaries do not prioritize victim battery efficiency.")
            ],
            ["reconnaissance-detection", "slow-and-low", "evasion", "ids-tuning", "soc"]
        ),
        (
            "RECON-014", "port-scanning-concepts",
            "What response indicates an 'open' port during an Nmap UDP scan against a service that does not return an application-level response (like TFTP or SNMP)?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "In UDP scanning, if no packet is returned, Nmap cannot tell whether the port is open and the application chose not to reply, or whether a firewall dropped the packet. Nmap marks this state as 'open|filtered'.",
            "Interpret Nmap open|filtered UDP port states.",
            [
                ("open|filtered (no response was received, which could mean open without reply or dropped by a firewall)", True, "UDP's connectionless nature makes silence ambiguous: open services may not reply, and firewalls drop silently."),
                ("closed (an immediate RST was returned)", False, "UDP ports do not return RST segments."),
                ("active (a three-way handshake completed)", False, "UDP does not use three-way handshakes."),
                ("rejected (an HTTP 403 error was returned)", False, "HTTP 403 is a web response, not a raw UDP port state.")
            ],
            ["reconnaissance", "udp-scan", "open-filtered", "nmap"]
        ),
        (
            "RECON-015", "reconnaissance-detection",
            "How does a SIEM or NIDS rule detect a 'Subnet Ping Sweep' conducted by an internal host?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 50,
            "A ping sweep manifests as a single internal source IP generating sequential or rapid ICMP Echo Requests across an entire range of host IP addresses (e.g. 192.168.1.1 to 192.168.1.254) in a very short duration.",
            "Construct detection criteria for subnet ping sweeps.",
            [
                ("A single source IP generating rapid ICMP Echo Requests across sequential destination IPs across an entire subnet", True, "Correlating one source generating sequential ICMP requests to multiple target IPs identifies sweep activity."),
                ("A computer downloading a 10 GB file over HTTPS", False, "File downloads generate TCP data streams to a single destination."),
                ("A user opening multiple browser tabs to Wikipedia", False, "Browsing Wikipedia generates DNS and HTTPS traffic, not ICMP sweeps."),
                ("An unmanaged switch experiencing a broadcast storm", False, "Switch loops circulate frames, not sequential host ping sweeps.")
            ],
            ["reconnaissance-detection", "ping-sweep", "icmp", "siem", "soc"]
        ),
        (
            "RECON-016", "service-enumeration-concepts",
            "What information does an adversary seek to discover when performing 'SMB Enumeration' on TCP port 445?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "SMB enumeration probes Windows file sharing to identify available shared folders (shares), active domain user accounts, password policies, operating system versions, and whether SMBv1/v2 signing is enforced.",
            "Identify the objectives of SMB enumeration.",
            [
                ("Available network shares, user accounts, password policies, and OS version details", True, "SMB enumeration maps internal network resources, shared file repositories, and user accounts."),
                ("The personal credit card number of the CEO", False, "SMB shares store files, not raw credit card credentials by default."),
                ("The physical serial number of the office microwave oven", False, "SMB is a Windows file sharing protocol."),
                ("The optical wavelength of the building's fiber cables", False, "SMB operates at Layer 7 application file sharing.")
            ],
            ["reconnaissance", "smb", "enumeration", "windows", "shares"]
        ),
        (
            "RECON-017", "reconnaissance-detection",
            "What is 'TCP ACK Scanning' (Nmap -sA) used for by an adversary?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "An ACK scan sends packets with only the ACK flag set. It never determines whether a port is open; instead, it is used to map out firewall rules and determine whether the firewall is stateful or stateless, and which ports are filtered vs unfiltered.",
            "Explain the purpose of TCP ACK scanning.",
            [
                ("To map firewall rule sets and determine whether ports are filtered or unfiltered by stateful firewall rules", True, "ACK scans test firewall filtering behavior; open and closed ports both return RST on unfiltered systems."),
                ("To establish a high-speed video call with the target server", False, "ACK scanning is a security reconnaissance technique."),
                ("To permanently delete all firewall logs", False, "ACK packets are network probes, not administrative deletion commands."),
                ("To encrypt the target hard drive with ransomware", False, "Port scans do not infect systems with ransomware.")
            ],
            ["reconnaissance", "ack-scan", "firewall-mapping", "nmap"]
        ),
        (
            "RECON-018", "service-enumeration-concepts",
            "What is 'SNMP Enumeration' on UDP port 161 and why is an unconfigured default community string (like 'public' or 'private') dangerous?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 55,
            "SNMPv1/v2c uses unencrypted plaintext 'community strings' for authentication. If left at the default 'public', an attacker can query the Management Information Base (MIB) to extract interface lists, routing tables, usernames, and running software.",
            "Analyze the risks of default SNMP community strings.",
            [
                ("Attackers can use default community strings ('public') to query the MIB and extract routing tables, interface IPs, and system details", True, "Default community strings grant unauthorized read access to extensive device configuration and state data."),
                ("The router will automatically shut down its power supply", False, "Default strings expose data; they do not trigger immediate power outages."),
                ("The computer monitor will immediately turn off", False, "SNMP is a network management protocol with no monitor display control."),
                ("The router will convert all copper cables into telephone lines", False, "SNMP does not alter physical hardware cabling.")
            ],
            ["reconnaissance", "snmp", "community-strings", "information-disclosure", "mib"]
        ),
        (
            "RECON-019", "port-scanning-concepts",
            "In an Nmap scan output, what does the port state 'filtered' indicate?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 45,
            "'Filtered' indicates that a firewall, packet filter, or network rule is blocking probes from reaching the port, causing probes to be dropped without response or rejected with an ICMP administrative unreachable error.",
            "Interpret Nmap 'filtered' port status.",
            [
                ("A firewall or network filter is actively blocking probes, preventing Nmap from determining if the port is open or closed", True, "Filtered means packet drops or ICMP admin-prohibited errors prevent the probe from reaching the service."),
                ("The service is running normally and accepting connections", False, "Open services return SYN-ACK and are marked 'open'."),
                ("The port is closed and returned an immediate RST packet", False, "Closed ports that return RST are marked 'closed'."),
                ("The server's network cable has been eaten by insects", False, "Filtered is a firewall policy blocking decision.")
            ],
            ["reconnaissance", "filtered-port", "nmap", "firewall"]
        ),
        (
            "RECON-020", "service-enumeration-concepts",
            "What security vulnerability is exposed when an organization allows unrestricted 'DNS Zone Transfers' (AXFR) from its authoritative nameservers to any public IP?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Unrestricted AXFR allows anyone on the Internet to download the entire DNS zone file, instantly revealing all internal hostnames, IP addresses, mail servers, VPN endpoints, and subdomains to an adversary without scanning.",
            "Analyze the risk of unrestricted DNS zone transfers (AXFR).",
            [
                ("An adversary can download the entire DNS zone file, revealing all internal hostnames, IP addresses, and infrastructure topology", True, "Zone transfers disclose the complete organizational DNS map and must be restricted to authorized secondary nameservers."),
                ("The DNS server will immediately catch fire and explode", False, "Zone transfer is an RFC-compliant protocol feature; misconfiguration causes information disclosure, not fires."),
                ("All computer passwords in the company are deleted", False, "DNS zone files contain resource records, not user account passwords."),
                ("The company website becomes permanently unviewable", False, "Zone transfers do not take websites offline.")
            ],
            ["dns", "axfr", "zone-transfer", "information-disclosure", "reconnaissance"]
        ),
        (
            "RECON-021", "reconnaissance-detection",
            "Which Zeek (formerly Bro) log file specifically records all connection metadata—including source/destination IPs, ports, duration, byte counts, and connection state history?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 2, 40,
            "The 'conn.log' file in Zeek records comprehensive metadata for every network connection observed on the monitored link, serving as the foundational log for network traffic analysis and threat hunting.",
            "Identify primary connection logging in Zeek.",
            [
                ("conn.log", True, "conn.log tracks all connection sessions, protocols, byte sizes, and state histories."),
                ("dns.log", False, "dns.log records domain queries, answers, and TTLs."),
                ("http.log", False, "http.log records HTTP request methods, URIs, and status codes."),
                ("ssl.log", False, "ssl.log records TLS certificate subjects, issuers, and cipher suites.")
            ],
            ["zeek", "bro", "conn-log", "network-monitoring", "soc"]
        ),
        (
            "RECON-022", "reconnaissance-detection",
            "In Zeek's conn.log, what does the connection state 'S0' signify?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "In Zeek connection history, 'S0' means that a connection attempt was seen (SYN sent by the client), but NO response was ever seen from the destination server (SYN without reply), characteristic of port scanning or dead targets.",
            "Interpret Zeek conn.log S0 connection state.",
            [
                ("Connection attempt seen (SYN sent), but no response was returned by the destination (unanswered probe)", True, "S0 connections indicate unacknowledged probes, common during scans against non-existent IPs or filtered ports."),
                ("The connection completed a full 3-way handshake and transferred 1 GB of data", False, "That would be SF (normal establishment and termination)."),
                ("The connection was encrypted with TLS 1.3", False, "S0 is a transport-layer connection status."),
                ("The server successfully generated a full backup", False, "Zeek logs network wire states, not backup jobs.")
            ],
            ["zeek", "conn-log", "s0", "port-scanning", "soc"]
        ),
        (
            "RECON-023", "service-enumeration-concepts",
            "What is 'LDAP Enumeration' on TCP port 389/636 and what information can an attacker gather from an Active Directory domain controller?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Lightweight Directory Access Protocol (LDAP) queries can enumerate all Active Directory domain users, group memberships, computer accounts, service principal names (SPNs), and administrative permissions.",
            "Identify the objectives of LDAP enumeration in Active Directory.",
            [
                ("Domain user accounts, security groups, computer objects, and administrative privileges", True, "LDAP enumeration provides a comprehensive directory map of enterprise identity structures."),
                ("The physical serial number of the office coffee machine", False, "LDAP manages directory identity objects, not kitchen appliances."),
                ("The color of the computer monitor casing", False, "LDAP attributes store enterprise directory schema data."),
                ("The physical speed of light in optical fiber", False, "LDAP is an application directory protocol.")
            ],
            ["ldap", "active-directory", "enumeration", "reconnaissance"]
        ),
        (
            "RECON-024", "reconnaissance-detection",
            "An analyst detects thousands of rapid connections to TCP port 445 on a domain controller, resulting in Kerberos error 'KDC_ERR_PREAUTH_FAILED' (Event ID 4771). What attack is occurring?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Event ID 4771 with KDC_ERR_PREAUTH_FAILED indicates Kerberos pre-authentication failure due to an incorrect password. High volumes across multiple accounts signify a Password Spraying or Kerberos Brute-Force attack.",
            "Identify Active Directory Kerberos password attacks.",
            [
                ("A Kerberos password spraying or brute-force attack testing passwords against domain accounts", True, "Pre-authentication failure (4771) across accounts indicates automated password testing."),
                ("Routine automated synchronization of server clocks with NTP", False, "NTP synchronizes time over UDP port 123."),
                ("A physical failure of the domain controller power cord", False, "Active Event ID generation proves the server is online and processing authentication."),
                ("The domain controller downloading a video file from YouTube", False, "Kerberos authentication logs manage domain ticket requests.")
            ],
            ["active-directory", "kerberos", "password-spraying", "brute-force", "soc"]
        ),
        (
            "RECON-025", "port-scanning-concepts",
            "What is 'Zombie Scanning' (or Idle Scan / Nmap -sI) in stealth reconnaissance?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 3, 60,
            "An Idle Scan exploits predictable IP Identification (IP ID) sequence increments on an idle third-party host (the 'zombie') to probe target ports blindly, completely concealing the attacker's true IP address from the victim.",
            "Explain the mechanics of an Idle/Zombie port scan.",
            [
                ("A blind scanning technique that monitors predictable IP ID increments on an idle third-party host to scan a target without sending packets from the attacker's IP", True, "Idle scan achieves total anonymity by using the zombie host as an unwitting reflection oracle."),
                ("An attack that causes computer monitors to turn into zombies", False, "This is wordplay on the term zombie."),
                ("A scan that only operates when all employees in an office are asleep", False, "Idle scan relies on low traffic volume on the zombie host, not human sleep."),
                ("A tool that deletes operating system files from the target", False, "Idle scanning probes port states.")
            ],
            ["reconnaissance", "idle-scan", "ip-id", "stealth-scanning", "nmap"]
        ),
        (
            "RECON-026", "service-enumeration-concepts",
            "What is 'Wappalyzer' or similar browser technology profilers used for during web application reconnaissance?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 40,
            "Technology profilers inspect web page source code, script tags, cookies, and HTTP response headers to identify underlying technologies (e.g. WordPress, React, Apache, PHP, Google Analytics) used by a target website.",
            "Explain web application technology fingerprinting.",
            [
                ("Identifying software frameworks, CMS platforms, JavaScript libraries, and web servers used by a website", True, "Technology profilers map web architecture to identify outdated plugins or software stacks."),
                ("A tool that automatically formats computer hard drives", False, "Web profilers inspect public HTML and HTTP metadata."),
                ("An algorithm used to calculate electrical resistance in Ethernet cables", False, "Technology profilers evaluate web technologies."),
                ("A protocol used to stream audio across Bluetooth", False, "Profilers analyze web application source code.")
            ],
            ["web-security", "reconnaissance", "fingerprinting", "wappalyzer"]
        ),
        (
            "RECON-027", "reconnaissance-detection",
            "In Suricata rules, what does the keyword 'threshold' or 'detection_filter' accomplish?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "The 'threshold' or 'detection_filter' keyword restricts alert generation by requiring an event to occur a specified number of times within a given time interval (e.g. 10 events within 60 seconds) before triggering an alert, reducing alert noise.",
            "Explain rate-limiting and thresholding in Suricata rules.",
            [
                ("It limits alert firing by requiring a rule match to occur a specified number of times within a set time window", True, "Detection filters prevent alert flooding by triggering only when match frequencies exceed defined thresholds."),
                ("It sets the physical temperature limit of the server chassis", False, "Suricata rules inspect network traffic packets, not chassis temperatures."),
                ("It deletes all logs stored on the sensor after 10 minutes", False, "Thresholding controls alert generation rates."),
                ("It encrypts the packet using military AES ciphers", False, "Rule keywords control inspection logic, not packet encryption.")
            ],
            ["detection-engineering", "suricata", "threshold", "alert-tuning", "soc"]
        ),
        (
            "RECON-028", "port-scanning-concepts",
            "Why do penetration testing tools randomize the order of destination ports during a port scan (e.g. Nmap -r disables this)?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Scanning ports in random order rather than sequential order (1, 2, 3...) avoids triggering simple sequential port scan detection rules in firewalls and NIDS that monitor for sequential port access on a single host.",
            "Explain why port scanners randomize target port order.",
            [
                ("To avoid triggering sequential port scan detection rules in firewalls and intrusion detection systems", True, "Randomizing port order bypasses naive sequential detection rules."),
                ("Because computer processors can only count backwards", False, "Processors can count in any direction."),
                ("To make the scan run 500 times faster", False, "Randomization does not increase line transmission speed."),
                ("Because standard networking cables reject sequentially numbered packets", False, "Network hardware forwards packets regardless of port order.")
            ],
            ["port-scanning", "evasion", "randomization", "nmap", "soc"]
        ),
        (
            "RECON-029", "service-enumeration-concepts",
            "What security risk is created by exposing an unauthenticated Redis or Memcached caching server directly to the public Internet?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Redis and Memcached were designed for trusted internal networks without authentication by default. Public exposure allows attackers to read sensitive cached data, write SSH keys to victim systems, or execute massive UDP reflection DDoS attacks.",
            "Analyze the threat of exposed unauthenticated in-memory databases.",
            [
                ("Adversaries can extract sensitive cached data, overwrite files to achieve remote code execution, or launch reflection DDoS", True, "Exposed Redis instances allow unauthorized data dumps and arbitrary file writing (e.g. injecting authorized_keys)."),
                ("The server's physical CPU chip will melt within 5 minutes", False, "Service exposure causes data breach vulnerabilities, not hardware melting."),
                ("The operating system will automatically delete all web browsers", False, "Exposed caching daemons do not uninstall client software."),
                ("The local router will change its Wi-Fi password to 'admin'", False, "Caching servers do not alter router Wi-Fi settings.")
            ],
            ["reconnaissance", "redis", "memcached", "misconfiguration", "vulnerabilities"]
        ),
        (
            "RECON-030", "reconnaissance-detection",
            "What is 'JA3' (or JA4) fingerprinting and how does it assist SOC analysts in identifying malware even over encrypted TLS connections?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "JA3 creates an MD5 hash of specific unencrypted parameters in the TLS Client Hello (TLS version, accepted cipher suites, extensions, elliptic curves, and curve formats). Because different applications/malware have distinct Client Hello configurations, JA3 identifies the client software even when payload is encrypted.",
            "Explain JA3 TLS client fingerprinting in network defense.",
            [
                ("It hashes unencrypted TLS Client Hello parameters to identify client software and malware families regardless of payload encryption", True, "JA3 fingerprinting allows defenders to detect known malware (like Cobalt Strike) by their distinct TLS handshake signatures."),
                ("It decrypts the full TLS payload without requiring a private key", False, "JA3 fingerprints handshake parameters; it does not decrypt the encrypted application payload."),
                ("It measures the physical speed of the CPU processor in gigahertz", False, "JA3 is a network packet fingerprinting algorithm."),
                ("It permanently disables all user passwords across the enterprise", False, "JA3 is a passive network detection telemetry standard.")
            ],
            ["ja3", "tls", "fingerprinting", "malware-detection", "soc", "threat-hunting"]
        ),
    ]
    save_questions("reconnaissance_and_scanning_detection.json", items)


def generate_detection_engineering_indicators():
    items = [
        (
            "DET-001", "detection-rules",
            "Given the following Snort rule:\n`alert tcp $EXTERNAL_NET any -> $HOME_NET 22 (msg:\"SSH Brute Force Attempt\"; flags:S; threshold:type threshold, track by_src, count 5, seconds 30; sid:1000001; rev:1;)`\nWhat traffic pattern triggers this alert?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "This rule triggers an alert when an external source IP sends 5 or more TCP SYN packets (flags:S) to port 22 (SSH) on the internal network within a 30-second window, detecting rapid connection attempts characteristic of brute force.",
            "Analyze Snort detection rule syntax and thresholds.",
            [
                ("An external IP sends 5 or more TCP SYN packets to port 22 on the internal network within 30 seconds", True, "The rule tracks by_src and requires a count of 5 SYN packets to port 22 within 30 seconds."),
                ("An internal user successfully downloads an encrypted file over HTTPS port 443", False, "The rule inspects port 22 (SSH), not 443."),
                ("A DNS server resolves 5 domain names in 30 seconds", False, "The rule inspects TCP port 22, not UDP port 53."),
                ("A computer is powered off for 30 seconds", False, "Snort rules inspect live network packets.")
            ],
            ["detection-rules", "snort", "suricata", "threshold", "ssh", "brute-force"]
        ),
        (
            "DET-002", "indicators-of-compromise",
            "What is the difference between an Atomic Indicator and a Behavioral Indicator in cybersecurity threat detection?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "An Atomic Indicator is a static piece of data that cannot be broken down (e.g. a specific malicious IP address, domain name, or file hash). A Behavioral Indicator describes patterns of adversarial behavior (e.g. process injection followed by rapid outbound connections on non-standard ports).",
            "Contrast atomic indicators and behavioral indicators.",
            [
                ("Atomic indicators are static data points (IPs, hashes, domains); behavioral indicators describe patterns of adversarial activity", True, "Adversaries can easily change atomic indicators (Pyramid of Pain); behavioral patterns are much harder to alter."),
                ("Atomic indicators only exist in nuclear facilities; behavioral indicators exist in schools", False, "Atomic refers to indivisible data elements in threat intelligence terminology."),
                ("Atomic indicators are strictly encrypted; behavioral indicators are unencrypted", False, "Both can be shared in threat intelligence feeds (STIX/TAXII)."),
                ("Atomic indicators only apply to smartphones", False, "Threat indicators apply across all digital systems.")
            ],
            ["threat-intelligence", "iocs", "atomic-indicators", "behavioral-detection", "pyramid-of-pain"]
        ),
        (
            "DET-003", "network-indicators",
            "In network threat hunting, what is 'Beaconing' behavior and what mathematical metric is used by defenders to detect it?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Beaconing is regular, periodic outbound communication from a compromised host to an attacker's C2 server. Defenders calculate the time interval Delta between connections and analyze variance/jitter; low variance (consistent intervals) reveals automated beaconing.",
            "Analyze C2 beaconing detection through delta timing and jitter.",
            [
                ("Periodic outbound communication to a C2 server, detected by analyzing low timing variance (jitter) between connection intervals", True, "Automated malware beacons on fixed or low-jitter intervals (e.g. every 60 seconds +/- 5%), creating recognizable timing patterns."),
                ("A physical light flashing on the server equipment chassis", False, "Beaconing in threat hunting refers to outbound network command-and-control polling."),
                ("A user typing an essay into a word processing application", False, "Manual typing produces erratic, non-periodic network behavior."),
                ("The operating system installing an official security patch", False, "Patch installations are one-off or scheduled maintenance downloads.")
            ],
            ["c2", "beaconing", "threat-hunting", "jitter", "network-indicators", "soc"]
        ),
        (
            "DET-004", "network-indicators",
            "Why do sophisticated threat actors intentionally introduce 'Jitter' (random timing variance) into their malware beaconing intervals?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Malware introduces jitter (e.g. 20% random variance around a 60-second base interval) to disrupt static mathematical regularity, evading simple frequency-based anomaly detection rules that search for exact recurring timestamps.",
            "Explain the purpose of jitter in command-and-control beaconing.",
            [
                ("To vary connection timing and defeat security monitoring rules that look for rigid, perfectly recurring periodic intervals", True, "Jitter blurs the periodic pattern, making automated beacons look more like random human web browsing."),
                ("To make the computer's monitor physically vibrate", False, "Jitter in C2 refers to timing variance, not physical display vibration."),
                ("To increase the download speed of large video files", False, "Jitter is an operational stealth technique, not a throughput optimizer."),
                ("To bypass physical security checkpoints at office doorways", False, "Jitter is a software timing algorithm.")
            ],
            ["c2", "jitter", "beaconing", "evasion", "threat-hunting"]
        ),
        (
            "DET-005", "detection-rules",
            "In a Suricata / Snort rule, what does the 'nocase' modifier do when appended to a content match string (e.g. `content:\"malware\"; nocase;`)?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 35,
            "The 'nocase' modifier specifies that the content search must be case-insensitive, matching 'malware', 'Malware', 'MALWARE', or any combination of uppercase and lowercase letters.",
            "Recall the function of the nocase rule modifier.",
            [
                ("It makes the string match case-insensitive, matching any combination of uppercase and lowercase letters", True, "nocase ensures variations in letter casing do not evade the rule."),
                ("It disables the rule so that it never generates an alert", False, "nocase modifies string evaluation; it does not disable the rule."),
                ("It encrypts the alert message before sending it to the SIEM", False, "Rule modifiers alter pattern matching logic, not alert transport encryption."),
                ("It forces the packet to be dropped immediately", False, "Dropping traffic requires the 'drop' rule action, not the nocase modifier.")
            ],
            ["detection-rules", "snort", "suricata", "nocase", "rule-syntax"]
        ),
        (
            "DET-006", "alert-creation",
            "What is a 'True Positive' in SOC alert triage?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 40,
            "A True Positive occurs when a security alert correctly identifies genuine malicious activity or a real security incident that actually took place on the network.",
            "Define True Positive in alert analysis.",
            [
                ("An alert that correctly identifies genuine malicious activity or a real security threat", True, "True Positives are legitimate alerts requiring investigative triage and response."),
                ("An alert that mistakenly flags legitimate business activity as an attack", False, "That is a False Positive."),
                ("An attack that occurs with zero alerts generated by security tools", False, "That is a False Negative."),
                ("A routine software backup that completes without errors", False, "That is normal operations, not a security threat alert.")
            ],
            ["soc", "triage", "true-positive", "alert-classification"]
        ),
        (
            "DET-007", "false-positives",
            "What is the primary cause of 'Alert Fatigue' among SOC analysts, and what is its operational consequence?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 50,
            "Alert fatigue is caused by overwhelming volumes of low-fidelity, noisy False Positive alerts. It causes analysts to become desensitized and exhausted, drastically increasing the likelihood of missing or ignoring critical True Positive breach alerts.",
            "Analyze the operational impact of alert fatigue in security operations.",
            [
                ("Overwhelming volumes of noisy false positives that exhaust analysts, causing real breach alerts to be overlooked", True, "High false positive rates degrade human triage effectiveness, leading to missed intrusions."),
                ("Analysts drinking too much coffee during night shifts", False, "Alert fatigue is an operational detection engineering flaw, not diet."),
                ("Server hard drives running out of disk space", False, "Alert fatigue is human cognitive exhaustion caused by noisy rules."),
                ("The operating system changing its desktop wallpaper every hour", False, "Desktop UI settings are unrelated to SOC alert volume.")
            ],
            ["soc", "alert-fatigue", "false-positives", "detection-engineering"]
        ),
        (
            "DET-008", "detection-tuning",
            "When tuning a noisy detection rule in a SIEM or NIDS, what is an 'Exception' or 'Suppression' filter?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "An exception or suppression filter explicitly excludes verified, benign business activities (such as an authorized vulnerability scanner IP or scheduled backup script) from triggering the alert, preserving rule sensitivity for real attacks.",
            "Explain alert suppression and rule tuning.",
            [
                ("Excluding verified, legitimate business activities (like authorized vulnerability scanners) from triggering the alert", True, "Tuning suppresses known benign triggers, drastically increasing the rule's signal-to-noise ratio."),
                ("Permanently turning off all firewalls across the entire enterprise", False, "Suppression targets specific known benign triggers, not complete security disabling."),
                ("Deleting all audit logs older than 5 seconds", False, "Audit logs must be preserved for compliance and forensics."),
                ("Allowing all external hackers to log into the database without passwords", False, "Suppression filters benign internal sources, not external adversaries.")
            ],
            ["detection-tuning", "suppression", "alert-fidelity", "soc"]
        ),
        (
            "DET-009", "indicators-of-compromise",
            "According to David Bianco's 'Pyramid of Pain', which Indicator of Compromise (IOC) category causes the greatest difficulty and cost for an adversary when defenders detect and block it?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "At the top of the Pyramid of Pain are TTPs (Tactics, Techniques, and Procedures). Blocking an IP or hash is trivial for an attacker to change; forcing an adversary to abandon and reinvent their core attack techniques causes maximum operational pain.",
            "Identify the most impactful IOC tier in the Pyramid of Pain.",
            [
                ("Tactics, Techniques, and Procedures (TTPs)", True, "TTPs sit at the apex of the Pyramid of Pain; disrupting them forces adversaries to redesign their entire operational methodology."),
                ("Hash Values (MD5 / SHA-256)", False, "Hashes sit at the bottom of the pyramid; changing a single byte in malware creates a new hash trivially."),
                ("IP Addresses", False, "IP addresses are near the bottom; attackers easily rotate IPs via proxies and cloud instances."),
                ("Domain Names", False, "Domain names are easily generated via DGAs or purchased cheaply.")
            ],
            ["pyramid-of-pain", "ttps", "threat-intelligence", "defense"]
        ),
        (
            "DET-010", "detection-rules",
            "What is a 'Sigma' rule in modern detection engineering?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Sigma is an open, vendor-agnostic signature format for log events (written in YAML). It allows detection engineers to write detection rules once and convert them into queries for any SIEM or log platform (Splunk, Elastic, QRadar, Microsoft Sentinel).",
            "Define the role of Sigma rules in detection engineering.",
            [
                ("An open, generic YAML-based detection format that can be converted into queries for any SIEM platform", True, "Sigma provides a standardized, portable signature language for log analysis across diverse SIEM vendors."),
                ("A mathematical formula used to measure physical copper cable thickness", False, "Sigma rules are cyber detection definitions, not cable manufacturing specs."),
                ("A proprietary Microsoft software license required to boot Windows", False, "Sigma is an open-source, vendor-neutral detection community project."),
                ("A tool that automatically formats operating system drives", False, "Sigma rules define detection logic for security logs.")
            ],
            ["sigma", "detection-engineering", "siem", "yaml"]
        ),
        (
            "DET-011", "network-indicators",
            "In network traffic logs, an analyst observes periodic HTTP POST requests containing an uncharacteristically short, fixed-length User-Agent string: 'Mozilla/4.0'. Why is this considered an indicator of interest?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 50,
            "Modern legitimate web browsers send detailed, multi-token User-Agent strings. Bare, obsolete strings like 'Mozilla/4.0' often indicate basic, uncustomized HTTP libraries used by malware, automated scripts, or legacy C2 implants.",
            "Analyze anomalous User-Agent strings in proxy logs.",
            [
                ("Outdated or minimal User-Agent strings often reveal automated malware libraries or unrefined C2 beaconing scripts", True, "Malware developers often hardcode minimal User-Agent strings that stand out from legitimate browser traffic."),
                ("It proves the user is running an authorized update of Google Chrome", False, "Modern Chrome uses detailed multi-platform strings."),
                ("It indicates the server has exceeded its physical electrical power quota", False, "User-Agent is an HTTP request header."),
                ("It proves the packet was generated by an authorized DNS root server", False, "DNS servers do not generate HTTP POST requests.")
            ],
            ["network-indicators", "user-agent", "proxy-logs", "c2", "threat-hunting"]
        ),
        (
            "DET-012", "detection-rules",
            "In a Snort/Suricata rule, what is the purpose of the 'sid' (Signature ID) keyword?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 35,
            "The 'sid' uniquely identifies each rule. Standard convention reserves SIDs under 1,000,000 for official rules, while SIDs 1,000,000 and above are reserved for local, custom-authored enterprise rules.",
            "Recall the purpose of the Snort sid keyword.",
            [
                ("A unique numeric identifier for the rule (SIDs >= 1,000,000 are reserved for custom local rules)", True, "sid uniquely tracks rules; rev tracks version revisions of that rule."),
                ("The speed limit in miles per hour of the network cable", False, "sid is a rule identifier, not physical speed."),
                ("The password required to log into the sensor operating system", False, "sid is a signature index."),
                ("The total number of packets dropped by the firewall", False, "sid is a static rule configuration identifier.")
            ],
            ["detection-rules", "snort", "suricata", "sid"]
        ),
        (
            "DET-013", "network-indicators",
            "An analyst observes an internal Windows workstation suddenly sending thousands of outbound SMB packets (TCP 445) to every other workstation on its local /24 subnet. What threat phase does this behavior indicate?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 55,
            "Rapid outbound SMB connection sweeps across neighboring workstations indicate Lateral Movement / Internal Worm Propagation (e.g. attempting PsExec, WMI execution, or exploiting EternalBlue / SMB vulnerabilities).",
            "Identify network indicators of lateral movement via SMB.",
            [
                ("Lateral movement / internal malware propagation attempting to compromise neighboring hosts via SMB", True, "Spreading via SMB port 445 is standard lateral movement behavior seen in ransomware and worms."),
                ("A user printing a single black-and-white text document to a USB printer", False, "USB printing does not generate network sweeps across 254 workstations."),
                ("Normal background updating of the local computer clock", False, "Clock updates use NTP port 123."),
                ("The router testing optical fiber link attenuation", False, "Layer 3/4 host sweeps originate from compromised endpoints, not router testing.")
            ],
            ["lateral-movement", "smb", "ransomware", "threat-hunting", "soc"]
        ),
        (
            "DET-014", "alert-creation",
            "What information should a high-quality security alert include to enable rapid, effective triage by a Tier 1 SOC analyst?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A high-quality alert must provide context: Source IP/host, Destination IP/host, Timestamp, Threat description, Severity score, specific triggering evidence (matching packet/log snippet), and recommended triage steps.",
            "Identify essential components of actionable SOC alerts.",
            [
                ("Contextual data: Source/Destination, Timestamp, Severity, triggered evidence, and recommended investigation steps", True, "Rich contextual alerts enable rapid triage and reduce time-to-respond (MTTR)."),
                ("Only the single word 'ERROR' with no other text", False, "Vague alerts create confusion and delay triage."),
                ("A complete copy of the company's annual financial tax returns", False, "Alerts must contain technical incident telemetry."),
                ("The personal home address of the software engineer who wrote the rule", False, "Author contact is not part of incident telemetry.")
            ],
            ["alert-creation", "soc", "triage", "best-practices"]
        ),
        (
            "DET-015", "detection-tuning",
            "When should a detection engineer adjust an alert rule from 'Low Severity' to 'High / Critical Severity'?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 55,
            "Severity should be escalated to High/Critical when the detected activity represents an imminent, high-impact threat to organizational operations or core crown-jewel assets (e.g. ransomware encryption active, domain controller compromise, active data exfiltration).",
            "Apply severity classification principles in detection engineering.",
            [
                ("When the activity indicates active compromise of critical assets, ransomware deployment, or confirmed data exfiltration", True, "Critical severity is reserved for active threats requiring immediate operational containment."),
                ("When an employee forgets their password on a Monday morning", False, "Password resets are routine IT helpdesk tickets, not critical security incidents."),
                ("When an email contains an image that loads slowly", False, "Slow loading is an application performance issue."),
                ("When a computer has been powered on for more than 24 hours", False, "Server uptime is normal and desirable.")
            ],
            ["detection-engineering", "severity-scoring", "soc", "risk-assessment"]
        ),
        (
            "DET-016", "network-indicators",
            "What is 'Living off the Land' (LotL) and why does it make network and endpoint detection challenging?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Living off the Land involves adversaries using legitimate, built-in administrative tools (like PowerShell, WMI, certutil, netsh, ssh) rather than dropping custom malware, making their activity blend in with normal administrative operations.",
            "Explain Living off the Land tactics.",
            [
                ("Adversaries use legitimate built-in administrative tools (PowerShell, certutil, WMI) to blend in with normal traffic", True, "LotL avoids dropping suspicious executable binaries, requiring behavioral and contextual detection."),
                ("Adversaries physically camping in agricultural fields near datacenters", False, "This is literal wordplay, not a cybersecurity tactic."),
                ("Adversaries replacing all software on a computer with agricultural farming simulators", False, "LotL weaponizes native operating system utilities."),
                ("Adversaries transmitting network traffic exclusively over analog telephone lines", False, "LotL tools execute on modern operating systems.")
            ],
            ["lotl", "powershell", "wmi", "evasion", "threat-hunting"]
        ),
        (
            "DET-017", "detection-rules",
            "In Snort/Suricata, what is the purpose of the 'flow:established,to_server' option?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "This option ensures that the rule only evaluates traffic matching an active, ESTABLISHED TCP connection traveling in the direction of client to server, ignoring dropped or uncompleted SYN packets and drastically reducing false positives.",
            "Explain the flow keyword in Snort rules.",
            [
                ("It restricts inspection to established TCP sessions traveling from client to server, eliminating unestablished scan noise", True, "flow:established ensures the rule only inspects genuine ongoing sessions, not rejected SYN packets."),
                ("It converts the packet stream into a video recording", False, "flow manages TCP session tracking state."),
                ("It deletes all logs from the sensor hard drive", False, "flow is an inspection filter."),
                ("It requires all users to write their passwords in capital letters", False, "flow evaluates transport-layer session state.")
            ],
            ["detection-rules", "snort", "suricata", "flow", "alert-tuning"]
        ),
        (
            "DET-018", "network-indicators",
            "What is a 'DGA-Generated Domain' and what visual characteristic often distinguishes it from legitimate domain names?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Domain Generation Algorithms (DGAs) generate domains programmatically using random seed algorithms, producing long, unpronounceable strings with high character entropy (e.g. 'qx7k9p2m3w1v.biz') that stand out from human-registered brand names.",
            "Identify visual and mathematical characteristics of DGA domains.",
            [
                ("High character entropy, unpronounceable random strings of consonants/numbers, and unusual top-level domains", True, "DGAs produce randomized strings lacking standard linguistic word patterns, with elevated Shannon entropy."),
                ("Domain names that always end in the letters '.gov'", False, ".gov domains are strictly restricted to verified government entities."),
                ("Domain names that are exactly 3 letters long and spell common dictionary words", False, "Short dictionary domains are premium brand domains, not DGAs."),
                ("Domain names printed in blue ink on physical paper", False, "DGA domains are digital DNS records.")
            ],
            ["dns", "dga", "entropy", "c2", "threat-hunting"]
        ),
        (
            "DET-019", "false-positives",
            "A newly deployed NIDS rule generates 10,000 alerts per hour because a vulnerability scanner runs authorized scans every night. What detection engineering action should be taken?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 55,
            "The detection engineer should tune the rule by adding an exception filter for the authorized vulnerability scanner's source IP address (or dedicated management subnet), silencing the noise without disabling the rule for unauthorized external scanners.",
            "Apply detection tuning to resolve vulnerability scanner alert noise.",
            [
                ("Add a suppression or exception filter for the authorized vulnerability scanner's source IP address", True, "Filtering the authorized scanner IP preserves the rule's capability while eliminating 10,000 false alerts."),
                ("Permanently delete the NIDS sensor and unplug all power cords", False, "Deleting monitoring leaves the network completely blind to real threats."),
                ("Disable the vulnerability scanner permanently and never scan for security bugs again", False, "Vulnerability scanning is a vital defensive hygiene practice."),
                ("Ignore all alerts and delete the SIEM database every morning", False, "Ignoring alerts guarantees undetected breaches.")
            ],
            ["detection-tuning", "vulnerability-scanner", "suppression", "soc"]
        ),
        (
            "DET-020", "indicators-of-compromise",
            "Why are IP addresses considered 'Low' value (easy to change) on the Pyramid of Pain?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 45,
            "Threat actors can effortlessly rotate IP addresses within seconds using dynamic cloud VPS instances, Tor exit nodes, residential proxy networks, or infected botnet hosts, making simple IP blacklisting easy for attackers to overcome.",
            "Explain why IP addresses are low-tier indicators on the Pyramid of Pain.",
            [
                ("Attackers can rapidly rotate IP addresses using proxies, Tor, and cloud infrastructure with minimal effort and cost", True, "IP blacklisting provides short-term defense because adversaries switch source IPs effortlessly."),
                ("Because IP addresses can only be owned by government agencies", False, "Anyone can obtain and lease IP addresses."),
                ("Because IP addresses are encrypted with military-grade AES-256", False, "IP addresses in packet headers are public, unencrypted routing data."),
                ("Because IPv4 has an infinite number of addresses", False, "IPv4 is limited to 4.3 billion addresses.")
            ],
            ["pyramid-of-pain", "ip-addresses", "threat-intelligence", "soc"]
        ),
        (
            "DET-021", "network-indicators",
            "What is an 'Unusual Port' indicator in perimeter firewall logs?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Traffic utilizing non-standard or high-numbered ports for standard protocols (e.g. HTTP/HTTPS running over port 8443 or port 4444, or SSH running over port 53) often indicates an adversary attempting to bypass port-based egress filters.",
            "Explain unusual port usage indicators.",
            [
                ("Standard protocols running on non-standard ports, or unexpected outbound connections on unassigned high ports", True, "Adversaries often bind C2 listeners to ports like 4444 or run non-DNS traffic over port 53 to evade egress blocks."),
                ("A computer port physically painted yellow instead of black", False, "Port indicators refer to Layer 4 TCP/UDP numbers, not physical paint colors."),
                ("An Ethernet cable plugged into the wall upside down", False, "RJ-45 jacks only insert in one physical orientation."),
                ("A printer that prints pages in reverse order", False, "Unusual port refers to network transport numbers.")
            ],
            ["network-indicators", "non-standard-ports", "egress-filtering", "c2"]
        ),
        (
            "DET-022", "detection-rules",
            "In detection engineering, what is the role of 'Offset' and 'Depth' keywords in content matching rules?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "'Offset' tells the inspection engine how many bytes into the payload to skip before beginning the search. 'Depth' limits how many bytes to search beyond the offset. Restricting the search window dramatically improves inspection performance.",
            "Explain the optimization provided by offset and depth keywords.",
            [
                ("They constrain the payload search to a specific byte window, accelerating inspection and preventing full-payload scans", True, "Offset and depth optimize performance by checking headers or protocols at predictable byte positions."),
                ("They specify the physical depth underground where cables are buried", False, "Offset and depth are byte boundaries in packet memory buffers."),
                ("They calculate the electrical voltage running through the processor", False, "These are pattern matching bounds."),
                ("They dictate how many hours a security analyst must work per day", False, "They are signature configuration parameters.")
            ],
            ["detection-rules", "snort", "suricata", "optimization", "offset-depth"]
        ),
        (
            "DET-023", "network-indicators",
            "What does a sudden, sustained spike in outbound ICMP traffic with large payload byte sizes (e.g. 1000 bytes per ping) suggest?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Standard ping packets carry small, static payloads (e.g. 32 to 64 bytes). Sustained high-volume pings with large, variable payloads are indicative of ICMP Tunneling / Data Exfiltration, where an adversary encapsulates stolen data inside ICMP Echo Requests.",
            "Identify ICMP tunneling and data exfiltration patterns.",
            [
                ("ICMP Tunneling / Data Exfiltration concealing stolen data inside ICMP Echo Request payloads", True, "ICMP tunnels bypass basic port blocks by encoding arbitrary data inside ping payload fields."),
                ("A user rapidly clicking the refresh button on a web browser", False, "Browser refresh generates HTTP/HTTPS requests, not large ICMP payloads."),
                ("The operating system installing an official security update", False, "OS updates download over HTTPS, not ICMP."),
                ("A switch port automatically recovering from an err-disable state", False, "Err-disable recovery does not generate large external ping bursts.")
            ],
            ["icmp", "tunneling", "exfiltration", "threat-hunting", "soc"]
        ),
        (
            "DET-024", "alert-creation",
            "In a Security Information and Event Management (SIEM) system, what is 'Correlation'?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Correlation links multiple disparate security events occurring across firewalls, endpoints, DNS, and authentication servers over time, synthesizing them into a single high-confidence incident (e.g. failed logins followed by successful login and immediate large outbound transfer).",
            "Explain event correlation in SIEM platforms.",
            [
                ("Connecting multiple related log events across different systems and timeframes to identify multi-stage attack patterns", True, "Correlation combines weak individual signals into strong composite attack detections."),
                ("Deleting all logs that contain the letter 'S'", False, "Correlation analyzes data; it does not delete logs."),
                ("Physically soldering two server motherboards together", False, "SIEM correlation is software log analysis."),
                ("Setting all computer desktop screens to identical brightness levels", False, "Correlation is event log analysis.")
            ],
            ["siem", "correlation", "soc", "detection-engineering"]
        ),
        (
            "DET-025", "detection-tuning",
            "What is 'Alert Throttling' or 'Rate Limiting' in SOC monitoring systems?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 45,
            "Throttling limits the frequency at which an alert fires for identical criteria (e.g. only generating one alert per source IP every 15 minutes, even if 10,000 matches occur), preventing inbox flooding and SIEM pipeline saturation.",
            "Explain alert throttling.",
            [
                ("Suppressing duplicate alerts for the same source/threat within a time window to prevent alert flooding", True, "Throttling prevents a single ongoing scan or flood from creating thousands of redundant tickets."),
                ("Physically choking the Ethernet cable to reduce data flow", False, "Throttling is a software notification control."),
                ("Deleting user email accounts that receive spam", False, "Throttling manages monitoring notifications."),
                ("Restricting employee lunch breaks to 10 minutes", False, "Throttling governs alerting frequency.")
            ],
            ["alert-tuning", "throttling", "soc", "siem"]
        ),
        (
            "DET-026", "indicators-of-compromise",
            "What is an 'IoA' (Indicator of Attack) compared to an 'IoC' (Indicator of Compromise)?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "An IoC is forensic evidence that an attack HAS ALREADY occurred (after the fact, e.g. malware hash on disk). An IoA focuses on the attacker's active intent and behavior IN PROGRESS (e.g. unauthorized privilege escalation, living-off-the-land activity), enabling proactive intervention.",
            "Differentiate Indicators of Attack from Indicators of Compromise.",
            [
                ("An IoC is historical evidence of a past breach; an IoA detects active adversarial intent and behavior in real time", True, "IoCs ask 'What was compromised?'; IoAs ask 'What is the attacker doing right now?'"),
                ("IoAs are used only in outer space; IoCs are used on Earth", False, "Both are cybersecurity threat detection models."),
                ("IoCs are legally binding contracts signed with banks", False, "Both are technical cybersecurity telemetry concepts."),
                ("There is zero difference; they are exact identical synonyms", False, "They represent fundamentally different reactive vs proactive paradigms.")
            ],
            ["ioa", "ioc", "proactive-defense", "threat-hunting", "soc"]
        ),
        (
            "DET-027", "network-indicators",
            "An analyst reviews proxy logs and notices recurring connections to an external IP with an exact 5-minute interval ($300$ seconds) with $0\%$ jitter lasting for 72 hours. What does this suggest?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 55,
            "A rigid, exact 300-second interval with zero jitter running continuously for days is undeniably automated machine behavior. It could represent an unjittered malware C2 beacon or an automated legitimate software health check/telemetry agent.",
            "Analyze exact periodic connection timing in proxy logs.",
            [
                ("Automated machine polling (either an unjittered malware C2 beacon or a routine software health check)", True, "Zero jitter indicates automated programmatic scheduling, warranting process verification."),
                ("A human user manually typing website addresses every 300 seconds without sleeping for 3 days", False, "Humans cannot type with microsecond precision for 72 continuous hours."),
                ("A physical failure of the fiber-optic transceivers", False, "The connection is succeeding reliably every 5 minutes."),
                ("A computer running without any operating system installed", False, "Executing network sockets requires an operating system stack.")
            ],
            ["c2", "beaconing", "threat-hunting", "proxy-logs", "soc"]
        ),
        (
            "DET-028", "detection-rules",
            "What is the function of the 'classtype' keyword in Snort/Suricata rules?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 35,
            "The 'classtype' keyword assigns the rule to a standardized attack category (e.g. 'trojan-activity', 'attempted-admin', 'web-application-attack') and automatically assigns a default priority/severity level.",
            "Recall the function of the classtype keyword.",
            [
                ("It categorizes the alert into a standard threat classification and assigns default priority/severity", True, "classtype standardizes alert taxonomies and default priority levels in Snort."),
                ("It classifies which programming language was used to compile the operating system", False, "classtype classifies attack categories."),
                ("It sets the physical dimensions of the equipment rack", False, "classtype is an alert metadata keyword."),
                ("It encrypts the packet before writing to disk", False, "classtype does not perform cryptographic operations.")
            ],
            ["detection-rules", "snort", "suricata", "classtype", "metadata"]
        ),
        (
            "DET-029", "detection-tuning",
            "What is 'Baseline Drift' in anomaly detection systems and how must security engineers address it?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Baseline drift occurs as legitimate business network behavior naturally changes over time (new software deployments, business growth, seasonal traffic shifts). If the baseline is not periodically updated, false positives will rise or real anomalies will be missed.",
            "Explain baseline drift in behavioral detection systems.",
            [
                ("Legitimate network traffic patterns evolve over time, requiring periodic baseline updates to prevent false alerts", True, "Dynamic networks evolve; static baselines become obsolete and noisy without periodic recalibration."),
                ("Cables slowly shifting their physical position inside wall conduits", False, "Baseline drift refers to statistical traffic models, not cable movement."),
                ("The operating system clock running backward", False, "Drift refers to changing behavioral statistical norms."),
                ("The computer screen slowly moving to the left", False, "Baseline drift is a telemetry profiling concept.")
            ],
            ["anomaly-detection", "baseline-drift", "detection-tuning", "machine-learning"]
        ),
        (
            "DET-030", "indicators-of-compromise",
            "Why is sharing threat intelligence in standardized formats (such as STIX/TAXII and MISP) advantageous for SOC teams?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Structured formats (STIX) and automated transport protocols (TAXII) allow security tools (SIEMs, firewalls, EDRs) to ingest, share, and operationalize machine-readable threat intelligence automatically without manual analyst data entry.",
            "Explain the benefits of standardized threat intelligence sharing.",
            [
                ("It enables automated machine-to-machine ingestion and enforcement of threat intelligence across diverse security tools", True, "STIX/TAXII automates threat indicator sharing and ingestion into defensive sensors."),
                ("It makes all computer passwords publicly visible on the dark web", False, "Threat intelligence sharing aims to protect organizational assets."),
                ("It forces all computers to use the same operating system", False, "Standards are platform-independent."),
                ("It eliminates the need for software firewalls", False, "Firewalls ingest threat intelligence feeds to block malicious IPs/domains.")
            ],
            ["threat-intelligence", "stix", "taxii", "misp", "soc"]
        ),
        (
            "DET-031", "network-indicators",
            "In DNS telemetry, what does an abnormally high ratio of TXT record queries compared to standard A/AAAA queries from a single host suggest?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "TXT records can carry large arbitrary payloads (up to 255 bytes per string). A disproportionate volume of TXT queries often indicates DNS tunneling used by malware for command-and-control payloads or stage payload downloads.",
            "Analyze anomalous DNS TXT record query ratios.",
            [
                ("DNS Tunneling used for command-and-control payload delivery or data exfiltration", True, "TXT records carry large payloads, making them a preferred mechanism for DNS-based C2 channels."),
                ("A user verifying their email password with Active Directory", False, "Active Directory authentication uses Kerberos/LDAP, not public TXT queries."),
                ("The computer installing a printer ink cartridge", False, "Printer maintenance does not generate heavy external TXT queries."),
                ("Normal web browsing to news websites", False, "Web browsing primarily queries A and AAAA records.")
            ],
            ["dns", "txt-record", "dns-tunneling", "c2", "threat-hunting"]
        ),
        (
            "DET-032", "detection-rules",
            "In Snort/Suricata, what is the role of the 'byte_test' rule option?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "'byte_test' extracts a specified number of bytes from a given offset in the packet payload, converts them to an integer, and performs a mathematical comparison (e.g. greater than, equal to, less than) against an expected numeric value.",
            "Explain the function of byte_test in Snort rules.",
            [
                ("It extracts numeric bytes from a payload offset and performs a mathematical comparison against a value", True, "byte_test enables validating binary protocol fields, length parameters, or numeric exploit triggers."),
                ("It measures the physical weight in bytes of the computer hard drive", False, "byte_test inspects packet payloads in memory."),
                ("It deletes all emails containing more than 100 bytes", False, "byte_test is a packet inspection evaluation condition."),
                ("It tests the electrical battery level of the router", False, "byte_test evaluates digital protocol bytes.")
            ],
            ["detection-rules", "snort", "suricata", "byte-test", "packet-inspection"]
        ),
        (
            "DET-033", "network-indicators",
            "What does a 'Port Knocking' sequence indicate when observed in firewall connection logs?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Port knocking is a stealth authentication method where a client sends connection attempts to a specific secret sequence of closed ports (e.g. 7000, 8000, 9000). A daemon monitoring the firewall logs recognizes the sequence and dynamically opens a firewall port (e.g. SSH).",
            "Explain the mechanics of port knocking.",
            [
                ("A client attempts connections to a secret sequence of closed ports to dynamically open a hidden firewall port (e.g. SSH)", True, "Port knocking keeps services completely concealed from port scans until the secret sequence is knocked."),
                ("A physical intruder knocking on the server room door with their knuckles", False, "Port knocking is a software firewall authentication mechanism."),
                ("A network loop causing switches to crash", False, "Port knocking is an intentional authentication technique."),
                ("A router rebooting due to a power outage", False, "Port knocking involves deliberate client connection packets.")
            ],
            ["port-knocking", "firewall", "stealth", "authentication"]
        ),
        (
            "DET-034", "detection-tuning",
            "What is a 'Canary Rule' in detection engineering?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A canary rule is a newly authored detection rule deployed in 'test' or 'alert-only' mode (without triggering automated blocking or pager alerts) to evaluate its performance, measure false positive rates, and tune logic before promoting it to production.",
            "Explain the purpose of canary detection rules.",
            [
                ("A newly authored rule deployed in test/silent mode to validate accuracy and false-positive rates before production promotion", True, "Canary deployment ensures new detection rules do not trigger unexpected false-positive floods or service outages."),
                ("A rule that monitors the health of pet birds kept in datacenters", False, "Canary rule is a software testing metaphor derived from coal mine canaries."),
                ("A rule that formats computer drives after 30 days", False, "Canary rules monitor packet streams silently."),
                ("A rule that increases the speed of optical fiber lasers", False, "Canary rules evaluate detection logic accuracy.")
            ],
            ["detection-engineering", "canary-rule", "testing", "alert-tuning", "soc"]
        ),
        (
            "DET-035", "network-indicators",
            "Why is monitoring outbound SMTP traffic (TCP port 25) originating from general employee desktop subnets critically important in network defense?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 55,
            "General workstations have zero legitimate reason to initiate direct outbound connections on port 25 (email clients send mail to authorized corporate relays via port 587). Outbound port 25 traffic from desktops is a classic indicator of a spam botnet infection.",
            "Analyze the security risk of outbound SMTP port 25 from client workstations.",
            [
                ("Client endpoints should never connect directly to external mail servers on port 25; doing so indicates a spam botnet or malware", True, "Legitimate email uses internal submission relays (port 587); direct port 25 from workstations indicates botnet spamming."),
                ("Port 25 is strictly reserved for high-definition 4K video streaming", False, "Port 25 is SMTP mail transport."),
                ("Port 25 traffic causes optical fiber cables to burn out", False, "Port 25 is standard digital network traffic."),
                ("Port 25 is required for users to view websites in Google Chrome", False, "Web browsing uses ports 80 and 443, not port 25.")
            ],
            ["smtp", "egress-filtering", "botnet", "spam", "network-indicators", "soc"]
        ),
    ]
    save_questions("detection_engineering_and_indicators.json", items)


def generate_incident_investigation_soc():
    items = [
        (
            "SOC-001", "alert-triage",
            "In a Security Operations Center (SOC), what is the primary objective of 'Tier 1 Alert Triage'?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 45,
            "Tier 1 triage rapidly reviews incoming security alerts to determine whether each alert is a True Positive (real attack) or False Positive (benign activity), assess immediate impact, and escalate verified incidents to Tier 2/3 responders.",
            "Define the core purpose of Tier 1 SOC alert triage.",
            [
                ("To rapidly validate alerts as True or False Positives, assess initial severity, and escalate confirmed threats to Tier 2", True, "Tier 1 filters noise, verifies initial evidence, and escalates actionable incidents."),
                ("To physically replace broken hardware motherboards in server racks", False, "Hardware repair is data center facilities maintenance, not SOC alert triage."),
                ("To write complete software operating systems from scratch", False, "SOC analysts investigate security alerts, not OS kernel programming."),
                ("To answer general customer billing support phone calls", False, "Billing is handled by customer finance teams.")
            ],
            ["soc", "triage", "tier1", "incident-response"]
        ),
        (
            "SOC-002", "alert-triage",
            "What is 'Scoping the Blast Radius' during an active cybersecurity incident investigation?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "Scoping the blast radius determines the full extent and spread of the compromise across the organization: identifying all affected endpoints, compromised user accounts, accessed databases, and lateral movement paths.",
            "Explain blast radius scoping during incident investigation.",
            [
                ("Determining the full extent of the compromise, including all affected endpoints, accounts, and accessed data", True, "Scoping ensures incident responders understand the entire footprint of the intrusion before taking containment actions."),
                ("Measuring the physical damage caused by an exploding computer battery", False, "Blast radius in cybersecurity is a metaphor for the scope of logical compromise."),
                ("Calculating how many miles of network cable exist in a building", False, "Scoping assesses asset compromise, not cable length."),
                ("Formatting all corporate computers without investigating", False, "Premature formatting destroys forensic evidence before the breach scope is known.")
            ],
            ["soc", "incident-investigation", "blast-radius", "scoping"]
        ),
        (
            "SOC-003", "evidence-collection",
            "According to RFC 3227 (Guidelines for Evidence Collection and Archiving), what is the 'Order of Volatility'?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "The Order of Volatility mandates that forensic evidence must be collected starting with the most volatile data (data that is lost when power is disconnected, like CPU registers, cache, and RAM) before moving to less volatile data (disk, backups).",
            "Recall RFC 3227 Order of Volatility in forensic collection.",
            [
                ("Collecting evidence from most volatile to least volatile: CPU registers/cache -> RAM -> Network state -> Disk -> Archival media", True, "Volatile data is lost on reboot; collecting it first preserves ephemeral memory artifacts."),
                ("Collecting evidence in alphabetical order based on file names", False, "Forensic collection follows volatility, not alphabetical names."),
                ("Collecting all physical paper manuals before touching any computers", False, "Digital memory artifacts take precedence."),
                ("Formatting all hard drives before taking a memory snapshot", False, "Formatting destroys forensic evidence.")
            ],
            ["forensics", "evidence-collection", "rfc3227", "order-of-volatility", "soc"]
        ),
        (
            "SOC-004", "timeline-analysis",
            "Why must a forensic analyst convert all log timestamps from disparate network devices into Coordinated Universal Time (UTC) during timeline reconstruction?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Network devices may reside in different physical time zones or have different local clock settings. Normalizing all timestamps to a single standard time base (UTC) is necessary to correlate events in their true chronological order.",
            "Explain the necessity of normalizing forensic timestamps to UTC.",
            [
                ("To align events across devices spanning multiple time zones into a consistent, accurate chronological sequence", True, "UTC normalization prevents chronological confusion caused by local daylight saving or time zone offsets."),
                ("Because computer processors can only calculate math in the UTC language", False, "Processors calculate math on binary integers."),
                ("To make the forensic report twice as long", False, "Normalization ensures chronological accuracy."),
                ("Because UTC timestamps prevent hard drives from getting infected with viruses", False, "Timestamps record time; they do not block viruses.")
            ],
            ["timeline-analysis", "forensics", "utc", "timestamps", "soc"]
        ),
        (
            "SOC-005", "network-investigation",
            "An analyst investigates a host that made an unauthorized outbound connection to a known malicious C2 IP. Which log source should be checked to identify which local process initiated the socket connection?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 55,
            "Endpoint Detection and Response (EDR) or Windows Sysmon Event ID 3 (Network Connection) logs record the initiating process name, process ID (PID), command-line arguments, user account, and destination IP/port.",
            "Identify log sources correlating network connections to endpoint processes.",
            [
                ("Endpoint Detection and Response (EDR) or Windows Sysmon Event ID 3 (Network Connection)", True, "Sysmon Event ID 3 specifically links network socket events to the exact executable process on the endpoint."),
                ("The building's physical door badge entry logs", False, "Badge logs record physical human door access, not software process socket creation."),
                ("The web browser's bookmark list", False, "Bookmarks list saved URLs, not real-time network connection PIDs."),
                ("The printer's remaining toner level indicator", False, "Printer toner status does not record network socket processes.")
            ],
            ["edr", "sysmon", "process-tracking", "network-investigation", "soc"]
        ),
        (
            "SOC-006", "alert-triage",
            "During an investigation, an analyst discovers that a suspected compromised endpoint has been generating outbound connections to malicious C2 infrastructure for 6 hours. What is the immediate first containment action?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 50,
            "The analyst should immediately isolate the endpoint from the network (logically via EDR network containment or by disconnecting its network link) to stop active C2 control and prevent lateral movement, while keeping power on to preserve volatile RAM.",
            "Identify initial containment actions for active C2 compromises.",
            [
                ("Isolate the endpoint from the network (via EDR isolation or link disconnect) while keeping power on to preserve RAM", True, "Network isolation halts attacker command execution and lateral movement without destroying volatile RAM evidence."),
                ("Power off the computer immediately by pulling the electrical plug", False, "Powering off destroys all volatile RAM evidence (running malware, injected keys, memory artifacts)."),
                ("Send an angry email to the attacker demanding they stop", False, "Communicating with adversaries compromises the investigation and provides zero containment."),
                ("Format the hard drive immediately before taking memory snapshots", False, "Formatting destroys all forensic evidence.")
            ],
            ["containment", "incident-response", "edr-isolation", "soc"]
        ),
        (
            "SOC-007", "network-investigation",
            "What is 'Pass-the-Hash' (PtH) and how is it detected in Windows network authentication logs?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Pass-the-Hash is a lateral movement technique where an attacker uses a captured NTLM password hash directly to authenticate over SMB/RPC without cracking the plaintext password, detected via Windows Event ID 4624 (Logon Type 3: Network) using NTLM authentication instead of Kerberos.",
            "Analyze Pass-the-Hash lateral movement detection.",
            [
                ("Using captured NTLM hashes to authenticate across network services without cracking plaintext, seen as Type 3 NTLM logons", True, "PtH exploits NTLM acceptance of raw password hashes, detectable by unexpected NTLM authentications across internal endpoints."),
                ("Giving the computer password to a colleague during lunchtime", False, "PtH is an adversarial credential re-use attack technique."),
                ("A tool used to hash files before uploading them to Google Drive", False, "PtH weaponizes stolen credentials to move laterally."),
                ("A hardware fault in the computer power supply", False, "PtH is a cyber attack technique.")
            ],
            ["pass-the-hash", "lateral-movement", "ntlm", "event-id-4624", "soc"]
        ),
        (
            "SOC-008", "incident-classification",
            "According to NIST SP 800-61 (Computer Security Incident Handling Guide), what are the four core phases of the Incident Response Lifecycle?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 2, 45,
            "NIST SP 800-61 defines the four lifecycle phases as: 1. Preparation, 2. Detection and Analysis, 3. Containment, Eradication, and Recovery, 4. Post-Incident Activity (Lessons Learned).",
            "Recall the four phases of the NIST Incident Response lifecycle.",
            [
                ("Preparation -> Detection & Analysis -> Containment, Eradication & Recovery -> Post-Incident Activity", True, "This is the foundational four-phase incident response cycle defined in NIST SP 800-61."),
                ("Discover -> Offer -> Request -> Acknowledge", False, "That is the DHCP DORA process."),
                ("SYN -> SYN-ACK -> ACK -> FIN", False, "That is the TCP connection lifecycle."),
                ("Identify -> Authenticate -> Authorize -> Audit", False, "That is the AAA security access model.")
            ],
            ["incident-response", "nist-800-61", "lifecycle", "soc"]
        ),
        (
            "SOC-009", "evidence-collection",
            "Why is a strict 'Chain of Custody' maintained for digital forensic evidence?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Chain of custody provides a documented chronological record showing who collected, handled, transferred, analyzed, and secured forensic evidence, ensuring its integrity and admissibility in legal court proceedings.",
            "Explain the importance of Chain of Custody in forensics.",
            [
                ("To provide a verifiable audit trail proving who handled the evidence and ensuring it was not tampered with for legal admissibility", True, "A broken chain of custody makes evidence inadmissible in criminal or civil court cases."),
                ("To physically tie all server cables together with a metal chain", False, "Chain of custody is a legal documentation process, not physical hardware chains."),
                ("To ensure that employees wear matching uniforms in the datacenter", False, "Chain of custody tracks evidence provenance."),
                ("To calculate the total electricity consumed during an investigation", False, "Chain of custody documents evidence handling.")
            ],
            ["forensics", "chain-of-custody", "evidence-handling", "legal-admissibility"]
        ),
        (
            "SOC-010", "network-investigation",
            "An analyst investigates a compromised workstation and observes that 'certutil.exe' was used to make an outbound HTTP connection to an external IP. What technique is the attacker executing?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 55,
            "Adversaries frequently abuse 'certutil.exe' (a legitimate Windows certificate utility with a '-urlcache -split -f' download feature) as a Living-off-the-Land Binary (LOLBIN) to download second-stage malware or tools from external servers.",
            "Identify LOLBIN misuse of certutil for malware download.",
            [
                ("LOLBIN abuse: using built-in Windows certutil as an ingress tool to download second-stage malware payloads", True, "certutil -urlcache is a common LOLBIN technique used to download files while bypassing basic execution blocks."),
                ("The workstation installing an official Microsoft Windows security update", False, "Official updates download via Windows Update services, not command-line certutil URL caching."),
                ("Normal synchronization of the computer clock with NTP", False, "NTP uses port 123, not certutil HTTP downloads."),
                ("A routine automated backup of the MySQL database", False, "certutil is a Windows certificate utility.")
            ],
            ["lolbin", "certutil", "ingress-tool-transfer", "threat-hunting", "soc"]
        ),
        (
            "SOC-011", "incident-reporting",
            "What is the primary objective of a 'Post-Incident Review' (Lessons Learned meeting) following the resolution of a major security breach?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Lessons Learned reviews analyze what happened, how well the team responded, what tools or documentation failed, and what preventive controls, detection rules, or architectural changes must be implemented to prevent future recurrence.",
            "Explain the purpose of Lessons Learned post-incident reviews.",
            [
                ("To evaluate the response, identify operational gaps, and implement defensive improvements to prevent future incidents", True, "Lessons Learned ensures organizations continually improve defenses and incident handling procedures based on real-world experiences."),
                ("To assign blame and publicly fire the youngest employee in the department", False, "Lessons Learned should be blameless and focused on systemic engineering improvements."),
                ("To delete all logs and pretend the security breach never occurred", False, "Hiding breaches violates regulatory laws and leaves vulnerabilities open."),
                ("To celebrate by playing video games during business hours", False, "Post-incident review is a structured technical review.")
            ],
            ["incident-response", "lessons-learned", "post-incident-activity", "soc"]
        ),
        (
            "SOC-012", "timeline-analysis",
            "In network forensics, what is 'Pivot Point' analysis?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Pivot point analysis uses a verified piece of evidence (e.g. an identified attacker IP, a specific malicious User-Agent, or a timestamp) to search across all other log sources and uncover related connections, lateral movements, or additional compromised hosts.",
            "Explain pivoting in digital forensics and threat hunting.",
            [
                ("Using a confirmed indicator (e.g. an IP, domain, or timestamp) to search across other logs and uncover the broader extent of the attack", True, "Pivoting allows analysts to expand an investigation from an initial clue to uncover the full campaign footprint."),
                ("Physically rotating a server chassis 90 degrees in the equipment rack", False, "Pivoting is an analytical investigation technique, not mechanical rotation."),
                ("A feature that formats hard drives when they reach 90% capacity", False, "Pivoting is investigative correlation."),
                ("An algorithm used to calculate copper wire electrical conductivity", False, "Pivoting is forensic log analysis.")
            ],
            ["threat-hunting", "pivoting", "forensics", "investigation-methodology"]
        ),
        (
            "SOC-013", "network-investigation",
            "What is 'Kerberoasting' and what network traffic characterizes this attack?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Kerberoasting is an attack where a domain user requests Kerberos Ticket Granting Service (TGS) tickets for service accounts with Service Principal Names (SPNs). The tickets are encrypted with the service account's password hash and can be extracted from traffic and cracked offline.",
            "Analyze the mechanics and detection of Kerberoasting.",
            [
                ("Requesting Kerberos TGS tickets for SPN service accounts to crack their password hashes offline, seen via Event ID 4769", True, "Kerberoasting generates TGS requests (Event 4769) with RC4 encryption (0x17) targeting service accounts."),
                ("Physically cooking a computer motherboard in an oven", False, "Kerberoasting is an Active Directory authentication exploit."),
                ("Flooding a domain controller with 5 million empty ping packets", False, "Kerberoasting is credential theft, not a DoS flood."),
                ("Deleting all Active Directory user accounts", False, "Kerberoasting operates stealthily to steal service credentials.")
            ],
            ["kerberoasting", "active-directory", "credential-theft", "kerberos", "soc"]
        ),
        (
            "SOC-014", "alert-triage",
            "An alert fires stating that a finance workstation accessed an external IP flagged as a known Cobalt Strike C2 server. What should the Tier 1 analyst check FIRST to verify the alert?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 55,
            "The analyst should verify whether the connection was actually successful (established TCP handshake, bytes transferred) or if it was blocked by the perimeter firewall/EDR, and verify the reputation of the external IP in threat intelligence feeds.",
            "Formulate initial triage verification steps for C2 alerts.",
            [
                ("Verify whether the connection succeeded (bytes transferred, established state) or was blocked, and check IP reputation", True, "Distinguishing between a blocked attempt and an active established session determines immediate incident severity."),
                ("Format the finance workstation immediately without checking any logs", False, "Formatting destroys evidence before scoping the incident."),
                ("Call the local news station to report a corporate emergency", False, "Premature public disclosure violates incident handling policies."),
                ("Tell the finance employee that their computer is permanently broken", False, "Triage requires technical log verification before alerting users.")
            ],
            ["alert-triage", "c2", "cobalt-strike", "verification", "soc"]
        ),
        (
            "SOC-015", "network-investigation",
            "What is 'Golden Ticket' attack in Active Directory and what does it grant an adversary?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 3, 60,
            "A Golden Ticket attack forges a Kerberos Ticket Granting Ticket (TGT) using the compromised password hash of the Active Directory KRBTGT account, granting the attacker unrestricted, permanent domain administrator access across the entire AD forest.",
            "Explain the impact of an Active Directory Golden Ticket attack.",
            [
                ("Forging a Kerberos TGT using the compromised KRBTGT account hash, granting total unrestricted domain administrative control", True, "Golden Ticket attacks represent complete Active Directory forest compromise with arbitrary ticket generation."),
                ("A gold-plated Ethernet cable awarded to top-performing IT employees", False, "This is literal wordplay, not an Active Directory attack."),
                ("A promotional coupon that offers free cloud hosting for 30 days", False, "Golden Ticket is a critical post-exploitation attack."),
                ("A feature that speeds up printer spooling queues", False, "Golden Ticket operates at the core of Kerberos domain authentication.")
            ],
            ["active-directory", "golden-ticket", "krbtgt", "kerberos", "post-exploitation"]
        ),
        (
            "SOC-016", "evidence-collection",
            "Why must an analyst calculate cryptographic hashes (like SHA-256) of forensic disk images and packet captures IMMEDIATELY upon acquisition?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Calculating the hash immediately establishes an immutable baseline digital fingerprint. Matching this baseline hash later proves in court that the evidence was preserved intact and was never altered or tampered with during analysis.",
            "Explain the purpose of cryptographic hashing during evidence acquisition.",
            [
                ("To establish a baseline digital fingerprint proving the evidence has not been altered or tampered with during analysis", True, "Hash verification proves forensic integrity and guarantees legal chain-of-custody compliance."),
                ("To encrypt the disk image so even the forensic analyst cannot read it", False, "Hashing verifies integrity; it does not prevent authorized forensic examination."),
                ("To increase the download speed of the disk image across Wi-Fi", False, "Hashing calculates mathematical digests; it does not accelerate networks."),
                ("To delete all viruses from the hard drive automatically", False, "Hashing is a passive integrity calculation.")
            ],
            ["forensics", "hashing", "evidence-integrity", "sha256", "chain-of-custody"]
        ),
        (
            "SOC-017", "network-investigation",
            "What is 'DCSync' attack and what Windows event indicates an attempt to perform it?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "A DCSync attack uses the Directory Replication Service (DRS) Remote Protocol to impersonate a domain controller and request password hashes directly from an authentic DC, detected via Directory Service Access (Event ID 4662) on replicating accounts.",
            "Identify DCSync attacks against Active Directory.",
            [
                ("Impersonating a domain controller using replication protocols to extract password hashes (e.g. via mimikatz)", True, "DCSync extracts hashes over DRS replication without running code directly on the target domain controller."),
                ("Synchronizing computer clocks with public NTP servers", False, "DCSync is an AD credential replication exploit, not clock synchronization."),
                ("A user syncing their personal smartphone calendar with Microsoft Outlook", False, "Personal calendar sync uses Exchange ActiveSync, not DCSync."),
                ("A network switch rebooting due to high memory utilization", False, "DCSync operates against domain controller directory replication.")
            ],
            ["active-directory", "dcsync", "mimikatz", "credential-theft", "soc"]
        ),
        (
            "SOC-018", "incident-classification",
            "In SOC operations, what is Mean Time to Detect (MTTD) and Mean Time to Respond (MTTR)?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 45,
            "MTTD measures the average time elapsed from when an intrusion occurs to when it is detected. MTTR measures the average time from detection to when the incident is contained, eradicated, and resolved.",
            "Define MTTD and MTTR metrics in SOC performance evaluation.",
            [
                ("MTTD is the average time to detect an intrusion; MTTR is the average time to contain and resolve the incident", True, "Lower MTTD and MTTR represent higher security maturity and lower potential breach impact."),
                ("MTTD is the time to purchase new computers; MTTR is the time to unpack them", False, "These are cybersecurity incident response metrics, not hardware procurement."),
                ("MTTD is the download speed of a file; MTTR is the upload speed", False, "These measure security operations response times."),
                ("MTTD is employee vacation time; MTTR is employee sick leave", False, "These measure threat detection and response velocity.")
            ],
            ["soc-metrics", "mttd", "mttr", "incident-response"]
        ),
        (
            "SOC-019", "network-investigation",
            "An analyst investigates a host that communicated with a known ransomware payment portal. In proxy logs, they see an initial outbound connection to an unknown domain 45 minutes earlier followed by an executable download. What was that initial connection?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 2, 55,
            "The initial connection was the initial staging / payload delivery phase (often via a phishing lure or drive-by download), where the victim system downloaded the second-stage loader/ransomware binary that subsequently detonated.",
            "Reconstruct multi-stage attack infection sequences.",
            [
                ("Initial compromise and second-stage payload delivery preceding the ransomware detonation phase", True, "Attacks occur in phases (Cyber Kill Chain): initial access -> payload staging -> execution -> extortion."),
                ("Routine automated updating of the user's web browser", False, "Web browser updates download from official vendor domains, not ransomware precursors."),
                ("The employee purchasing office supplies online", False, "Legitimate retail transactions do not execute ransomware payloads."),
                ("The local router synchronizing time with NTP", False, "Time sync does not download executable binaries.")
            ],
            ["kill-chain", "ransomware", "payload-delivery", "incident-investigation", "soc"]
        ),
        (
            "SOC-020", "timeline-analysis",
            "What is 'Log Tampering' and what evidence in Windows event logs indicates that an attacker cleared the Security log?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Log tampering occurs when an adversary clears event logs to conceal their tracks. On Windows, clearing the Security event log generates a distinct, non-suppressible event: Event ID 1102 ('The audit log was cleared'), which is a high-priority alert for SOC analysts.",
            "Identify evidence of security log clearing.",
            [
                ("Windows Event ID 1102 ('The audit log was cleared'), signaling an adversary attempting to conceal their tracks", True, "Event 1102 is recorded when the security log is wiped, serving as a critical indicator of compromise."),
                ("The computer screen turning blue and restarting", False, "A blue screen (BSOD) is an operating system kernel crash."),
                ("The computer's clock jumping forward by 100 years", False, "Log clearing does not manipulate system clock settings."),
                ("The printer running out of physical paper", False, "Log clearing is an operating system audit event manipulation.")
            ],
            ["log-tampering", "event-id-1102", "anti-forensics", "soc"]
        ),
        (
            "SOC-021", "alert-triage",
            "What is a 'Playbook' (or Runbook) in Security Orchestration, Automation, and Response (SOAR)?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 45,
            "A SOAR Playbook is a pre-defined, standardized workflow of automated actions and guided manual steps executed by security systems and analysts to respond to a specific type of threat (e.g. phishing triage, host containment, malware analysis).",
            "Explain SOAR playbooks in automated incident response.",
            [
                ("A standardized, automated workflow of triage and containment actions executed in response to a specific threat type", True, "Playbooks ensure consistent, rapid incident response by automating repetitive tasks (IP lookups, containment)."),
                ("A book containing sports strategies for football coaches", False, "In cybersecurity, playbooks are automated incident handling workflows."),
                ("A manual explaining how to install copper cables in walls", False, "Playbooks govern security incident investigation and remediation."),
                ("A software license agreement required to use open-source tools", False, "Playbooks define operational response procedures.")
            ],
            ["soar", "playbook", "automation", "incident-response", "soc"]
        ),
        (
            "SOC-022", "network-investigation",
            "What is 'Ransomware Pre-Encryption Staging' and what network activity reveals it before encryption begins?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Before launching encryption, modern ransomware gangs perform data exfiltration (Double Extortion). Detecting large outbound archive uploads (via Mega, Rclone, or FTP) during off-hours gives defenders a vital window to intervene before systems are encrypted.",
            "Analyze pre-encryption data exfiltration indicators.",
            [
                ("Massive outbound data uploads (e.g. via Rclone or Mega) to exfiltrate confidential data before encrypting local drives", True, "Modern double-extortion ransomware exfiltrates data first; catching the exfiltration allows containment before encryption."),
                ("A user saving a small text file to their local desktop folder", False, "Saving small local files is normal routine work."),
                ("The computer screen turning off when the user walks away", False, "Screen sleeping is an operating system power-saving feature."),
                ("The local printer printing a 2-page document", False, "Local printing does not indicate ransomware staging.")
            ],
            ["ransomware", "data-exfiltration", "rclone", "double-extortion", "soc"]
        ),
        (
            "SOC-023", "evidence-collection",
            "Why must a forensic analyst never examine or execute suspicious files directly on the original live evidence drive?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Interacting directly with the original drive alters timestamps, modifies system registry keys, creates temporary swap files, and potentially triggers destructive anti-forensics malware. Analysts must always work on a bit-for-bit forensic copy using hardware write-blockers.",
            "Explain the necessity of forensic copies and write blockers.",
            [
                ("Live interaction modifies timestamps, alters registry data, and risks triggering anti-forensics destruction; working on copies preserves original evidence", True, "Working on bit-for-bit forensic images with write blockers preserves original evidence pristine for legal scrutiny."),
                ("Because hard drives can only be plugged into a computer once in their lifetime", False, "Hard drives can be read repeatedly under write-blocked conditions."),
                ("Because examining evidence on the original drive violates copyright law", False, "This is a forensic evidence integrity rule, not copyright."),
                ("Because files on an original drive automatically delete themselves after 5 minutes", False, "Drives do not delete files unless instructed by software.")
            ],
            ["forensics", "write-blocker", "evidence-handling", "integrity"]
        ),
        (
            "SOC-024", "network-investigation",
            "An analyst detects that an internal web application was breached via an unauthenticated file upload vulnerability. What network or server evidence reveals where the uploaded webshell was placed?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Web server access logs (e.g. Nginx or Apache access.log) will record an HTTP POST request to the vulnerable upload endpoint, followed by subsequent HTTP GET/POST requests accessing the newly created file in an uploads directory (e.g. '/uploads/shell.php').",
            "Correlate web server access logs to identify webshell locations.",
            [
                ("Web server access logs showing an HTTP POST to the upload form followed by HTTP GET/POST requests accessing the newly uploaded script", True, "Correlating the upload POST request with subsequent requests to files in the uploads folder identifies the webshell path."),
                ("The building's air conditioning thermostat logs", False, "HVAC logs record temperatures, not web server file paths."),
                ("The router's physical serial number label", False, "Router serial numbers do not record web server directories."),
                ("The user's personal web browser history on their home phone", False, "Web server access logs capture all incoming HTTP requests.")
            ],
            ["webshell", "web-application-security", "log-analysis", "incident-investigation"]
        ),
        (
            "SOC-025", "timeline-analysis",
            "What is 'MFT Analysis' (Master File Table) in Windows forensic timeline reconstruction?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "The NTFS Master File Table ($MFT) records metadata for every file and folder on the volume (including creation, modification, access, and MFT record change timestamps: $STANDARD_INFORMATION and $FILE_NAME), enabling microsecond-precision file activity timelines.",
            "Explain MFT analysis in Windows forensic investigations.",
            [
                ("Analyzing the NTFS $MFT to extract precise file creation, modification, and access timestamps across all volume files", True, "$MFT provides forensic proof of when files were dropped, modified, or executed, exposing timestamp manipulation (timestomping)."),
                ("A tool that tests the physical rotation speed of hard drive platters", False, "MFT is a filesystem metadata structure, not a mechanical tachometer."),
                ("An algorithm used to calculate employee payroll taxes", False, "MFT is the core filesystem database of Windows NTFS."),
                ("A protocol that enables wireless printing over Bluetooth", False, "MFT operates on local disk filesystems.")
            ],
            ["mft", "ntfs", "forensics", "timeline-analysis", "timestomping"]
        ),
        (
            "SOC-026", "network-investigation",
            "What is 'Timestomping' and how does an analyst detect it?",
            "SINGLE_CHOICE", "ADVANCED", "ANALYZE", 3, 60,
            "Timestomping is an anti-forensics technique where an attacker alters file timestamps (e.g. setting creation date back to 2015 to blend in with legitimate system binaries). Analysts detect it by comparing the easily modified $STANDARD_INFORMATION attribute with the harder-to-modify $FILE_NAME attribute in the MFT.",
            "Analyze timestomping detection in NTFS forensics.",
            [
                ("Manipulating file timestamps to blend with legitimate files; detected by comparing $STANDARD_INFORMATION with $FILE_NAME in the MFT", True, "Inconsistencies between $STANDARD_INFORMATION and $FILE_NAME timestamps reveal timestomping."),
                ("A physical intruder stomping on a computer with their shoes", False, "Timestomping is a digital anti-forensics timestamp modification technique."),
                ("A clock error that occurs during daylight saving time", False, "Timestomping is deliberate adversarial modification of metadata."),
                ("A technique that accelerates computer processor clock speed", False, "Timestomping alters file timestamps, not CPU frequency.")
            ],
            ["anti-forensics", "timestomping", "mft", "forensic-analysis", "soc"]
        ),
        (
            "SOC-027", "alert-triage",
            "What does a 'P1 / Critical' incident classification typically mandate in an enterprise Incident Response policy?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "A P1/Critical incident involves severe business disruption, active ransomware, or widespread unauthorized domain control. It mandates immediate 24/7 incident response activation, executive/legal escalation, and continuous containment until resolved.",
            "Recall operational requirements for P1 Critical incidents.",
            [
                ("Immediate 24/7 emergency response team activation, executive escalation, and active containment until business risk is mitigated", True, "P1 incidents threaten critical business operations and require immediate all-hands operational containment."),
                ("Sending an email that will be reviewed next week after vacation", False, "P1 incidents cannot wait for delayed review."),
                ("Immediately deleting all company social media accounts", False, "Incident handling follows structured operational response playbooks."),
                ("Rebooting the building's main electrical generator", False, "P1 is a cyber severity classification.")
            ],
            ["incident-classification", "p1-severity", "soc-policy", "sla"]
        ),
        (
            "SOC-028", "network-investigation",
            "An analyst discovers that an attacker used PowerShell to execute a Base64-encoded command. What command parameter allows PowerShell to run encoded scripts directly, and how does the analyst decode it?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 2, 50,
            "PowerShell accepts Base64-encoded UTF-16LE scripts via the '-EncodedCommand' (or '-enc') parameter. An analyst can decode the payload using tools like CyberChef or Python base64 decoding with utf-16le encoding.",
            "Analyze encoded PowerShell execution.",
            [
                ("The -EncodedCommand (-enc) parameter; decoded by Base64-decoding the string as UTF-16LE text", True, "PowerShell expects UTF-16LE encoding; decoding it reveals the underlying command script."),
                ("The -DeleteEverything parameter; decoded by running it in safe mode", False, "That is an imaginary parameter."),
                ("The -Password parameter; decoded by typing it backwards", False, "Base64 decoding requires standard mathematical string decoding."),
                ("The -ColorBlue parameter; decoded by changing screen brightness", False, "Parameters govern command interpreter execution.")
            ],
            ["powershell", "encodedcommand", "base64", "cyberchef", "soc"]
        ),
        (
            "SOC-029", "evidence-collection",
            "What tool on Linux is commonly used to create a bit-for-bit forensic clone of a storage drive while avoiding accidental write modifications?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 1, 40,
            "'dd' (or specialized forensic variants 'dc3dd' and 'dcfldd') reads raw blocks from an input drive (if=/dev/sdb) and writes an identical bit-for-bit raw image to an output file (of=image.raw) with hashing verification.",
            "Identify forensic disk imaging tools on Linux.",
            [
                ("dd (or forensic variants dc3dd / dcfldd)", True, "dd and dcfldd create raw bit-stream copies of physical storage drives for forensic analysis."),
                ("rm -rf", False, "rm -rf deletes files recursively and must never be used on evidence."),
                ("fdisk -l", False, "fdisk -l lists partitions but does not create drive images."),
                ("chmod 777", False, "chmod changes file permissions.")
            ],
            ["forensics", "disk-imaging", "dd", "dc3dd", "evidence-collection"]
        ),
        (
            "SOC-030", "timeline-analysis",
            "What is 'Super Timeline' creation in digital forensics (e.g. using log2timeline / Plaso)?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 55,
            "A Super Timeline aggregates and sorts timestamps from all available forensic artifacts across a system ($MFT, registry hives, event logs, browser history, prefetch, USB logs) into a single unified chronological timeline of all activities on the machine.",
            "Explain Super Timeline generation in forensic analysis.",
            [
                ("Aggregating timestamps from all filesystem, registry, event log, and application artifacts into a unified chronological master timeline", True, "Super timelines provide holistic chronological visibility into every event that occurred on a compromised host."),
                ("A timeline showing the release dates of superhero movies", False, "This is wordplay on the term super timeline."),
                ("A calendar used exclusively by company executives to schedule vacations", False, "Super timelines are deep technical forensic artifact databases."),
                ("A tool that automatically speeds up the computer's CPU clock speed", False, "Super timelines analyze forensic disk artifacts.")
            ],
            ["forensics", "plaso", "log2timeline", "super-timeline", "soc"]
        ),
        (
            "SOC-031", "network-investigation",
            "In Windows forensics, what artifact records evidence of application execution—including execution timestamp, run count, and referenced DLLs—even if the executable has been deleted from disk?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 2, 45,
            "Windows Prefetch files (.pf located in C:\\Windows\\Prefetch) record application execution evidence, including the executable name, run count, hash, and the last 8 execution timestamps (in Windows 10/11), proving execution even if the binary was deleted.",
            "Identify Windows Prefetch execution artifacts.",
            [
                ("Windows Prefetch files (.pf in C:\\Windows\\Prefetch)", True, "Prefetch files prove whether and when an executable was launched on a Windows system."),
                ("The Windows Recycle Bin", False, "The Recycle Bin holds deleted files but does not track execution counts or timestamps."),
                ("The web browser bookmarks folder", False, "Bookmarks store URLs, not binary execution tracking."),
                ("The system audio driver settings", False, "Audio drivers do not record application execution histories.")
            ],
            ["forensics", "prefetch", "windows", "execution-artifacts", "soc"]
        ),
        (
            "SOC-032", "incident-classification",
            "In incident handling, what is the difference between 'Eradication' and 'Recovery'?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 2, 50,
            "Eradication involves identifying and completely eliminating all elements of the threat (removing malware, deleting webshells, closing compromised accounts, patching vulnerabilities). Recovery restores systems to normal production operations (restoring from clean backups, verifying functionality).",
            "Contrast incident Eradication and Recovery phases.",
            [
                ("Eradication removes all malware, persistence, and vulnerabilities; Recovery restores systems safely back to normal production operations", True, "Eradication purges the threat; Recovery brings sanitized systems back into operational service."),
                ("Eradication is done by the legal team; Recovery is done by marketing", False, "Both are technical phases executed by incident response and IT teams."),
                ("Eradication means deleting the company's website permanently", False, "Eradication eliminates the threat artifacts, not legitimate business assets."),
                ("There is zero difference; they are exact identical synonyms", False, "They are distinct sequential phases in the NIST incident response lifecycle.")
            ],
            ["incident-response", "eradication", "recovery", "nist-800-61", "soc"]
        ),
        (
            "SOC-033", "network-investigation",
            "What Windows event log ID records the installation of a new Windows Service, a classic persistence mechanism used by adversaries?",
            "SINGLE_CHOICE", "ADVANCED", "REMEMBER", 2, 45,
            "Windows System Event ID 7045 ('A service was installed in the system') records service installations, detailing the service name, service type, and the exact binary image path executed, exposing persistence implants.",
            "Recall Event ID for Windows service installation.",
            [
                ("System Event ID 7045 ('A service was installed in the system')", True, "Event 7045 captures new service creation, exposing persistence implants and privilege escalation binaries."),
                ("Security Event ID 4624 ('An account was successfully logged on')", False, "Event 4624 records logon sessions, not service installations."),
                ("Security Event ID 4625 ('An account failed to log on')", False, "Event 4625 records failed logon attempts."),
                ("System Event ID 6005 ('The Event log service was started')", False, "Event 6005 records system boot/eventlog startup.")
            ],
            ["windows-events", "event-id-7045", "persistence", "forensics", "soc"]
        ),
        (
            "SOC-034", "alert-triage",
            "What is a 'True Negative' in cybersecurity detection evaluation?",
            "SINGLE_CHOICE", "ADVANCED", "UNDERSTAND", 1, 40,
            "A True Negative occurs when normal, benign network activity takes place and the security system correctly does NOT generate an alert (normal activity correctly recognized as benign).",
            "Define True Negative.",
            [
                ("Benign, normal activity that correctly generates zero security alerts", True, "True Negatives represent the vast majority of legitimate business traffic that passes without alert noise."),
                ("An attack that occurs with zero alerts generated", False, "That is a dangerous False Negative."),
                ("A false alarm triggered by an authorized administrator", False, "That is a False Positive."),
                ("An alert that correctly catches a real hacker", False, "That is a True Positive.")
            ],
            ["soc", "metrics", "true-negative", "detection-evaluation"]
        ),
        (
            "SOC-035", "network-investigation",
            "An analyst discovers that a threat actor maintained persistence on a compromised Linux server via a malicious 'Cron' job. Where are user and system cron jobs standardly configured on Linux?",
            "SINGLE_CHOICE", "ADVANCED", "APPLY", 1, 40,
            "Linux scheduled tasks are configured in '/etc/crontab', the directory '/etc/cron.d/', hourly/daily directories ('/etc/cron.daily/'), and per-user crontab spool files in '/var/spool/cron/crontabs/'.",
            "Recall Linux cron job persistence locations.",
            [
                ("/etc/crontab, /etc/cron.d/, and /var/spool/cron/crontabs/", True, "These directories host system-wide and user-specific scheduled tasks in Linux environments."),
                ("C:\\Windows\\System32\\Tasks", False, "That is the Windows Task Scheduler directory."),
                ("/usr/share/fonts", False, "Fonts directories store graphical typography files."),
                ("/tmp/cache.dat", False, "That is a temporary file path, not standard crontab storage.")
            ],
            ["linux", "cron", "persistence", "incident-investigation", "soc"]
        ),
    ]
    save_questions("incident_investigation_and_soc.json", items)


if __name__ == "__main__":
    generate_reconnaissance_detection()
    generate_detection_engineering_indicators()
    generate_incident_investigation_soc()
