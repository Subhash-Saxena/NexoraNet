# NexoraNet Advanced Curriculum Lessons (8 Comprehensive Lessons)
from app.models.enums import ContentType, DifficultyLevel

ADVANCED_LESSONS = [
    # 29. Packet Analysis Foundations
    {
        "topic_slug": "packet-structure",
        "title": "Packet Analysis Foundations & Wireshark Dissection",
        "slug": "packet-analysis-foundations-wireshark",
        "description": "Deep packet inspection down to raw byte offsets, Ethernet framing, IP headers, and packet capture tools.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.ADVANCED,
        "estimated_minutes": 40,
        "content": """# Packet Analysis Foundations & Wireshark Dissection

### 1. What is it? (Simple Explanation)
When medical doctors suspect an internal illness, they don't guess based on surface symptoms alone; they order an X-Ray, an MRI, or blood work to inspect the human body at the cellular level.

In computer networking and cybersecurity, **Packet Analysis (Deep Packet Inspection)** is our MRI. It is the art of capturing the raw electrical, optical, and radio bitstreams traversing the wire and dissecting them header-by-header, byte-by-byte, to observe exactly what occurred during a network interaction.

### 2. Technical Explanation
Packet analysis intercepts network frames using a network adapter placed in **Promiscuous Mode** (or Monitor Mode for Wi-Fi), passing all raw frames to user-space capture libraries (such as `libpcap` on Linux/macOS or `Npcap` on Windows).

A complete captured packet consists of encapsulated layers:
1. **Layer 2 (Ethernet II Frame)**: 14 bytes (6-byte Dest MAC, 6-byte Source MAC, 2-byte EtherType `0x0800` for IPv4).
2. **Layer 3 (IPv4 Header)**: 20 bytes minimum.
   * `Version (4 bits)` & `IHL (4 bits)`: Internet Header Length (typically 5, indicating 20 bytes).
   * `Total Length (16 bits)`: Total size of IP packet including payload.
   * `Identification (16 bits)`, `Flags (3 bits)` (DF/MF), `Fragment Offset (13 bits)`.
   * `Time To Live (TTL) (8 bits)`: Hop counter decremented by routers.
   * `Protocol (8 bits)`: `0x06` for TCP, `0x11` for UDP, `0x01` for ICMP.
   * `Source IP (32 bits)` & `Destination IP (32 bits)`.
3. **Layer 4 (Transport Header)**: TCP (20-60 bytes) or UDP (8 bytes).
4. **Layer 7 (Application Payload)**: Raw data stream (HTTP text, DNS query, TLS encrypted record).

### 3. Wireshark Interface Anatomy
* **Packet List Pane (Top)**: Real-time scrolling table of captured packets with timestamps, source/destination IPs, protocols, and info summaries.
* **Packet Details Pane (Middle)**: Collapsible protocol tree breaking down individual field values and flags.
* **Packet Bytes Pane (Bottom)**: Raw hexadecimal and ASCII representations of the exact byte stream on the wire.

### 4. Visual Explanation: Raw Hex Offset Mapping
```
Hex Offset | Raw Hex Data                      | ASCII Translation
-----------+-----------------------------------+------------------
0000       | 00 1a 2b 3c 4d 5e 00 50 56 a1 b2 c3 | ..+<M^.PV...
0010       | 08 00 45 00 00 3c 1a 2b 40 00 40 06 | ..E..<.+@.@.
           |  ▲     ▲
           |  │     └── IPv4 Header Starts (Version 4, IHL 5)
           |  └──────── EtherType: 0x0800 (IPv4)
```

### 5. Wireshark Display Filters Cheat Sheet
```text
# Filter by IP address
ip.addr == 192.168.1.50

# Filter specifically by TCP destination port 443
tcp.dstport == 443

# Show all HTTP GET requests
http.request.method == "GET"

# Find packets containing a specific string in the payload
frame contains "password"
```

### 6. Command Examples
Capturing packets using the command-line standard `tcpdump`:
```bash
# Capture 10 packets on interface eth0 matching port 80 and save to PCAP file
sudo tcpdump -i eth0 -nn -c 10 -w web_capture.pcap port 80
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **Unmasking Malware Evasion**: Sophisticated malware attempts to evade firewalls by running non-standard protocols on standard ports (e.g., establishing a custom encrypted C2 channel over TCP Port 80). Looking at firewall logs shows "Port 80 allowed," but opening the PCAP in Wireshark immediately reveals the payload lacks HTTP headers!
* **Forensic Root Cause Analysis**: When an unauthorized data breach occurs, packet captures provide undeniable, legally admissible evidence of exact files exfiltrated, timestamps, and commands executed.

### 8. Common Troubleshooting Mistakes
* Capture Filters vs Display Filters:
  * **Capture Filters (BPF Syntax)**: Evaluated *during* packet capture to discard unwanted traffic before writing to disk (e.g., `host 192.168.1.1`).
  * **Display Filters (Wireshark Syntax)**: Applied *after* capture to temporarily hide packets on screen without deleting them (e.g., `ip.addr == 192.168.1.1`).

### 9. Quick Revision
* Packet analysis = Deep Packet Inspection down to raw byte offsets.
* Tools: Wireshark (GUI) and tcpdump / tshark (CLI).
* Standard PCAP format stores raw timestamped frame captures.
* Essential for incident response, malware analysis, and network forensics.

### 10. Interview Check
**Q: What is Promiscuous Mode, and why is it necessary for packet capture analysis?**  
**A:** By default, a network interface card (NIC) discards any frame whose destination MAC address does not match its own burned-in MAC (or broadcast/multicast). Promiscuous Mode disables this hardware filter, instructing the NIC to pass every single frame detected on the transmission medium up to the operating system kernel and packet capture software.
""",
    },
    # 30. TCP Packet Analysis
    {
        "topic_slug": "tcp-segments",
        "title": "TCP Packet Analysis & Stream Reconstruction",
        "slug": "tcp-packet-analysis-stream-reconstruction",
        "description": "Inspecting TCP flags, sequence number arithmetic, sliding windows, and reassembling TCP streams.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.ADVANCED,
        "estimated_minutes": 40,
        "content": """# TCP Packet Analysis & Stream Reconstruction

### 1. What is it? (Simple Explanation)
When you download a 50-megabyte file across the Internet, it doesn't travel as one giant block; it is chopped into 35,000 tiny packets that arrive out-of-order, intermingled with traffic from Netflix, Spotify, and system updates.

**TCP Stream Reconstruction** is how Wireshark and defensive network monitors automatically stitch those thousands of fragmented packets back together in correct order, displaying the original unencrypted conversation or downloaded file exactly as it appeared to the user.

### 2. Technical Explanation
TCP stream tracking relies on sequence arithmetic:
* **Relative Sequence Numbers**: Wireshark translates giant 32-bit Initial Sequence Numbers (e.g., `3,412,581,920`) into clean relative integers starting at `0` for human readability.
* **Payload Length Calculation**: If a packet has `Seq=1` and `TCP Payload Length=1460`, the receiver acknowledges `Ack=1461` (meaning: *"I received bytes 1 through 1460; send byte 1461 next!"*).

### 3. Diagnostic Flag Analysis in Wireshark
* `[SYN]`: Connection initiation. Look for high volumes indicative of SYN flooding or port scanning.
* `[SYN, ACK]`: Connection acceptance by the listening service.
* `[RST]`: Abrupt connection reset. Caused by firewalls actively rejecting connections, closed ports, or keep-alive timeouts.
* `[FIN, ACK]`: Graceful connection teardown.
* `[TCP Retransmission]`: Wireshark highlights dropped packets in black/red when it detects a segment re-sent after an unacknowledged timeout.
* `[TCP Dup ACK]`: The receiver notifies the sender that a packet in the sequence was dropped and it is still waiting for the missing segment.

### 4. Following a TCP Stream in Wireshark
1. Right-click any TCP packet in the Wireshark list.
2. Select **Follow -> TCP Stream**.
3. Wireshark extracts the payload from all sequence numbers in both directions, displaying the entire bidirectional ASCII dialogue:
   * **Red Text**: Client-to-server transmission (e.g., HTTP GET request).
   * **Blue Text**: Server-to-client response (e.g., HTTP 200 OK + HTML).

### 5. Visual Explanation: TCP Flag Control Byte
```
Bit 0   Bit 1   Bit 2   Bit 3   Bit 4   Bit 5   Bit 6   Bit 7   Bit 8
[CWR]   [ECE]   [URG]   [ACK]   [PSH]   [RST]   [SYN]   [FIN]
                          ▲       ▲       ▲       ▲       ▲
                          │       │       │       │       └── Teardown
                          │       │       │       └────────── Handshake
                          │       │       └────────────────── Reset
                          │       └────────────────────────── Push Data
                          └────────────────────────────────── Acknowledgment
```

### 6. Command Examples
Filter TCP flags directly using Wireshark display syntax:
```text
# Find all TCP SYN packets with no ACK (Connection initiation / SYN scans)
tcp.flags.syn == 1 && tcp.flags.ack == 0

# Find all abnormal TCP RST packets
tcp.flags.reset == 1

# Filter for retransmitted packets indicative of network degradation
tcp.analysis.retransmission
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **XMAS Scan Detection**: Attackers probe firewall rules using an unusual packet with flags `FIN`, `PSH`, and `URG` all turned on simultaneously (lit up like a Christmas tree). RFC 793 dictates that closed ports must respond with RST, while open ports drop the packet, allowing attackers to map firewall states. Filter: `tcp.flags == 0x029`.
* **Credential Harvesting in Unencrypted Streams**: Following TCP streams on legacy protocols (Telnet, FTP, HTTP) instantly unmasks plaintext authentication credentials transmitted across the wire.

### 8. Common Troubleshooting Mistakes
* Confusing Window Size with Window Scaling: In Wireshark, the raw `Window Size` field in the TCP header is only 16 bits (max 65,535 bytes). High-speed gigabit networks use the `Window Scale Option` negotiated during the SYN handshake to multiply this value up to 1 gigabyte!

### 9. Quick Revision
* Sequence numbers track byte positions; Ack numbers request the next expected byte.
* "Follow TCP Stream" reassembles fragmented packets into clean application payloads.
* Wireshark flags anomalies: Retransmissions, Dup ACKs, Zero Windows.
* Malicious scans exploit obscure flag combinations (XMAS, NULL scans).

### 10. Interview Check
**Q: When analyzing a PCAP capture, you observe thousands of TCP Dup ACK packets followed by rapid TCP Fast Retransmissions. What does this indicate?**  
**A:** This pattern indicates **packet loss on the network path**. The receiver detected a hole in the received sequence numbers (one segment dropped while subsequent segments arrived successfully) and repeatedly sent duplicate ACKs requesting the missing byte offset until the sender executed a Fast Retransmission to recover the dropped packet without waiting for a retransmission timeout.
""",
    },
    # 31. DNS Packet Analysis
    {
        "topic_slug": "dns-packet-analysis",
        "title": "DNS Packet Dissection & Covert Channel Detection",
        "slug": "dns-packet-dissection-tunneling",
        "description": "Wire-format dissection, transaction IDs, analyzing DNS tunneling, and detecting DGAs in PCAPs.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.ADVANCED,
        "estimated_minutes": 35,
        "content": """# DNS Packet Dissection & Covert Channel Detection

### 1. What is it? (Simple Explanation)
Imagine a spy who wants to smuggle secret military documents out of a heavily guarded facility where every backpack and vehicle is searched at the exit gate. The spy notices that the facility's mail room sends out thousands of innocent-looking delivery confirmation postcards every hour without inspection. The spy encodes secret blueprint coordinates into the fine print on those postcards.

**DNS Tunneling** is this exact espionage technique applied to computer networks. Because almost every corporate firewall permits outbound DNS queries on Port 53, adversaries encode stolen data inside DNS queries to smuggle it past security perimeters.

### 2. Technical Explanation
DNS packets (RFC 1035) possess a rigid binary wire format:
* **Transaction ID (16 bits)**: Matches requests to replies.
* **Flags (16 bits)**:
  * `QR (1 bit)`: 0 = Query, 1 = Response.
  * `Opcode (4 bits)`: Standard query (0), Inverse query (1), Status (2).
  * `AA (1 bit)`: Authoritative Answer.
  * `TC (1 bit)`: Truncated (message exceeded 512 bytes).
  * `RD (1 bit)`: Recursion Desired.
  * `RA (1 bit)`: Recursion Available.
  * `RCODE (4 bits)`: Return code (`0 = NoError`, `3 = NXDomain` / Name Error).
* **Question Section**: Domain name, Record Type (A, TXT), Class (IN).
* **Answer, Authority, and Additional Sections**: Resource records returned.

### 3. How DNS Tunneling Works
1. An attacker registers the domain `c2-tunnel.net` and sets their own malicious Command & Control server as the Authoritative Nameserver for that domain.
2. Malware on an infected internal host steals credit card numbers, encrypts them, and encodes them into Base64 or Hex: `4a6f686e446f65`.
3. The malware queries its local internal corporate DNS resolver: `4a6f686e446f65.c2-tunnel.net`.
4. The internal resolver doesn't know the answer, so it dutifully traverses the Internet and forwards the query to the attacker's Authoritative Nameserver!
5. The attacker's server reads the subdomain string, extracts the stolen data, and responds with a `TXT` record containing the next malicious command to execute.

### 4. Visual Explanation: DNS Tunneling Exfiltration
```
Infected Workstation                   Corporate DNS Resolver               Attacker C2 Nameserver
         │                                       │                                     │
         ├─── Query: 4a6f686e.c2-tunnel.net ────>│                                     │
         │    (Encoded Stolen Data)              ├─── Iterative Query Forwarded ──────>│
         │                                       │    (4a6f686e.c2-tunnel.net)         │
         │                                       │                               [Data Extracted!]
         │<── Response: TXT "cmd=whoami" ────────┼<── Response: TXT "cmd=whoami" ──────┤
```

### 5. Wireshark Display Filters for DNS Hunting
```text
# Find anomalous TXT queries (commonly used for large C2 payload transfers)
dns.qry.type == 16

# Find queries resulting in Non-Existent Domain (NXDomain)
dns.flags.rcode == 3

# Filter for long query strings exceeding 50 characters (indicative of tunneling)
dns.qry.name.len > 50
```

### 6. Command Examples
Using `tshark` to calculate the top queried domains in a capture:
```bash
# Extract and count unique DNS query names from a PCAP file
tshark -r capture.pcap -T fields -e dns.qry.name | sort | uniq -c | sort -nr | head -n 10
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **Domain Generation Algorithms (DGA)**: Malware uses DGAs to generate hundreds of pseudo-random domain names per day (e.g., `xjk923mvls091.biz`). SOC analysts hunt for sudden bursts of `NXDomain` (RCODE 3) spikes in DNS telemetry, which occur when malware probes domains that the attacker has not yet registered.
* **DNS Length Anomaly Detection**: Standard legitimate DNS queries average 15 to 30 characters (e.g., `api.slack.com`). Tunneling queries frequently exceed 60+ characters of high-entropy base32/hex strings.

### 8. Common Troubleshooting Mistakes
* Misidentifying Antivirus/Spam Filter Lookups as Tunneling: Security tools like Spamhaus routinely perform reverse DNS queries for IP reputation (e.g., `4.3.2.1.zen.spamhaus.org`) that look like high-volume automated queries but are entirely benign.

### 9. Quick Revision
* DNS wire format: Transaction ID, Flags (QR, AA, RCODE), Questions, Answers.
* Attackers abuse DNS for C2 and data exfiltration (DNS Tunneling).
* Hallmarks of DNS abuse: Long query strings, high entropy, TXT record abuse, NXDomain spikes.
* Mitigate with Protective DNS (PDNS) and payload entropy inspection.

### 10. Interview Check
**Q: How do Security Operations Center (SOC) analysts detect DNS Tunneling in network traffic logs?**  
**A:** Analysts detect DNS tunneling by monitoring for statistical anomalies: unusually high frequency of queries to a single root domain, abnormally long subdomain query lengths (high character count), high information entropy (random alphanumeric/base64 strings), excessive volume of `TXT` record queries, and sudden spikes in `NXDomain` responses.
""",
    },
    # 32. Traffic Analysis & Baselines
    {
        "topic_slug": "traffic-baselines",
        "title": "Network Traffic Analysis & Baseline Profiling",
        "slug": "traffic-analysis-baseline-profiling",
        "description": "Behavioral network monitoring, protocol distribution profiling, NetFlow/IPFIX, and anomaly detection.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.ADVANCED,
        "estimated_minutes": 40,
        "content": """# Network Traffic Analysis & Baseline Profiling

### 1. What is it? (Simple Explanation)
Imagine you manage security for a quiet suburban bank. On average, 20 customers visit between 9 AM and 5 PM, and the front door is locked at night. If you suddenly see 500 people running through the bank lobby at 2:00 AM on a Sunday, you don't need to know the name of every individual person to recognize that something is catastrophically wrong.

**Network Baseline Profiling** is establishing a mathematical definition of what "normal" looks like on your network so that abnormal behavioral spikes (like ransomware staging or massive data exfiltration) stand out immediately.

### 2. Technical Explanation
Network Traffic Analysis (NTA) evaluates communication patterns at scale across two tiers:
1. **Full Packet Capture (FPC)**: High storage cost. Stores complete packet payloads down to Layer 7.
2. **Flow Telemetry (NetFlow v9 / IPFIX)**: Lightweight metadata. Stores connection summaries:
   * Source IP & Port
   * Destination IP & Port
   * Protocol
   * Ingress/Egress Interface
   * Byte Count & Packet Count
   * Session Duration & Timestamps

### 3. Core Baseline Metrics
To construct an enterprise network baseline, security tools profile:
* **Protocol Distribution**: What percentage of traffic is HTTPS vs DNS vs SSH vs SMB?
* **Bandwidth by Time-of-Day**: Typical gigabytes-per-hour on weekdays vs weekends vs midnight hours.
* **Internal East-West vs Perimeter North-South**:
  * **North-South**: Traffic entering or leaving the enterprise toward the Internet.
  * **East-West**: Traffic flowing between internal servers and workstations inside the corporate perimeter.

### 4. Detecting Baseline Deviations
* **Beacons**: Malware calling home to a C2 server often exhibits rigid periodic intervals (e.g., sending a 64-byte packet every exactly 60.0 seconds). Statistical analysis unmasks these heartbeats even over encrypted TLS channels.
* **Data Hoarding / Exfiltration**: A graphic designer's workstation that typically uploads 20 MB per day suddenly transfers 85 Gigabytes to an external IP in Eastern Europe at 3:00 AM.
* **Lateral Movement Spikes**: An administrative workstation suddenly generating thousands of SMB (Port 445) and RDP (Port 3389) connections to 200 internal servers simultaneously (a hallmark of active ransomware propagation).

### 5. Visual Explanation: Traffic Flow Profiling
```
Workstation [10.0.1.50]                           Internal Database [10.0.2.20]
        │                                                     │
Normal Baseline: 10 queries/day (10 KB total)                │
        ├────────────────────────────────────────────────────>│
                                                              │
Ransomware Staging Incident (Anomaly!):                       │
        ├── SMB Session 1: 5 GB downloaded ──────────────────>│
        ├── SMB Session 2: 12 GB downloaded ─────────────────>│
        └── SMB Session 3: 40 GB downloaded (3:00 AM) ───────>│
[NTA Sensor flags 5000% volume surge above baseline!]
```

### 6. Command Examples
Using Zeek (formerly Bro) network security monitor to generate connection summaries:
```bash
# Process a PCAP through Zeek and inspect the generated connection log
zeek -r capture.pcap
cat conn.log | zeek-cut id.orig_h id.resp_h id.resp_p proto orig_bytes resp_bytes duration
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **Encrypted Traffic Visibility**: Modern adversaries encrypt their payloads using TLS 1.3, blinding legacy signature-based IDS engines. Behavioral traffic analysis inspects packet sizes, inter-arrival times, and connection duration rather than decrypted payload bytes, allowing defenders to identify malware activity without breaking encryption.
* **Zero Trust Policy Verification**: Validating that isolated production subnets generate zero unexpected East-West connections to development enclaves.

### 8. Common Troubleshooting Mistakes
* Failing to update baselines after business changes: If the company deploys a new cloud backup solution that uploads 500 GB every Friday night, failure to update the baseline profile will flood the SOC with recurring false-positive exfiltration alarms.

### 9. Quick Revision
* NTA profiles behavioral communication patterns across the network.
* NetFlow / IPFIX provides lightweight connection metadata without full payload storage.
* Tracks North-South (perimeter) and East-West (internal lateral) traffic.
* Identifies C2 beacons, data exfiltration, and lateral movement anomalies.

### 10. Interview Check
**Q: What is the difference between North-South traffic and East-West traffic, and why is monitoring East-West traffic crucial for defending against ransomware?**  
**A:** North-South traffic moves vertically between the internal enterprise network and external entities (the Internet). East-West traffic moves horizontally between internal hosts inside the corporate perimeter (workstation-to-server or server-to-server). Monitoring East-West traffic is crucial because once an initial endpoint is compromised by ransomware, the attacker spreads laterally across internal subnets via SMB, RDP, or SSH; if defenders only monitor the perimeter, internal propagation remains completely invisible.
""",
    },
    # 33. Network Attack Detection
    {
        "topic_slug": "network-indicators",
        "title": "Network Attack Detection & Indicators of Compromise",
        "slug": "network-attack-detection-indicators",
        "description": "Extracting atomic and behavioral IOCs, David Bianco's Pyramid of Pain, and threat intelligence correlation.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.ADVANCED,
        "estimated_minutes": 35,
        "content": """# Network Attack Detection & Indicators of Compromise

### 1. What is it? (Simple Explanation)
When a crime takes place in a physical building, forensic detectives search the scene for physical clues: shoe prints, broken glass, tire marks, and security camera footage of the getaway car's license plate.

In cybersecurity, an **Indicator of Compromise (IOC)** is the digital forensic artifact left behind on networks and endpoints that proves an attack took place. Network IOCs include malicious IP addresses, known malware domains, unusual user-agent strings, and abnormal protocol flags.

### 2. Technical Explanation
Network attack detection extracts and correlates artifacts across three tiers:
1. **Atomic Indicators**: Discrete pieces of data that cannot be broken down further (e.g., IP Address `198.51.100.42`, Port `4444`).
2. **Computed Indicators**: Data derived from forensic analysis (e.g., cryptographic hash of an intercepted payload `SHA256: e3b0c44298fc1c149...`).
3. **Behavioral Indicators (TTPs)**: Tactile patterns and methodologies defined in the MITRE ATT&CK framework (e.g., *"Adversary performs password spraying against external Outlook Web Access on Port 443 followed by SMB lateral movement"*).

### 3. The Pyramid of Pain (David Bianco)
The Pyramid of Pain illustrates how difficult it is for an attacker to adapt when defenders block specific types of indicators:
```
           /\\
          /  \\       TTPs (Tactics, Techniques, Procedures)  [TOUGHEST TO CHANGE]
         /    \\
        / Tools \\    Tools (Mimikatz, Cobalt Strike, Nmap)
       /  Network \\  Network Artifacts & Domains (evil-c2.com)
      / IP Address \\ IP Addresses (198.51.100.5)           [EASY TO CHANGE]
     / Hash Values  \\ Hash Values (SHA256, MD5)              [TRIVIAL TO CHANGE]
    +----------------+
```
* **Hash Values & IPs**: Trivial for attackers to change; they spin up a new cloud VPS or recompile malware in seconds.
* **TTPs**: Forces the attacker to abandon their entire operational playbook and learn brand-new offensive techniques!

### 4. Anatomy of Common Network Attack Signatures
* **SYN Port Scan**: Rapid sequential SYN packets to hundreds of destination ports within milliseconds, leaving connections half-open.
* **ARP Spoofing Signature**: Multiple gratuitous ARP replies arriving on a switch port claiming different IP addresses map to the exact same MAC address.
* **SQL Injection over HTTP**: URL containing SQL syntax: `GET /products?id=1%20UNION%20SELECT%20username,password%20FROM%20users`.

### 5. Visual Explanation: IOC Correlation in SIEM
```
[Firewall Syslog]       --> 10.0.1.15 connected to 203.0.113.88 on Port 4444
          │
[Threat Intel Feed]     --> 203.0.113.88 is a known Cobalt Strike C2 IP!
          │
          ▼ (SIEM Automated Correlation Rule Fires!)
[CRITICAL ALERT]: "Host 10.0.1.15 compromised with Cobalt Strike C2 Beacon"
```

### 6. Command Examples
Hunting for malicious network IOCs in Linux auth and web logs:
```bash
# Identify IP addresses attempting automated SSH brute-force password guessing
grep "Failed password" /var/log/auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr | head -n 10
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **Automated Threat Intelligence Ingestion**: Modern enterprise firewalls subscribe to automated threat intelligence feeds (STIX/TAXII format) that dynamically update blocklists every hour with newly identified malicious IP addresses and phishing domains worldwide.
* **Hunting Historical Breaches (Retroactive Analysis)**: When a new zero-day threat intelligence report is published containing IOCs from a nation-state campaign, SOC analysts search their historical 90-day SIEM logs to verify whether internal hosts communicated with those IPs weeks before the report was released.

### 8. Common Troubleshooting Mistakes
* Over-relying on IP blocklists: Cyber adversaries rotate IP addresses through fast-flux cloud providers and VPNs continuously. Blocking single IP addresses without detecting underlying behavioral TTPs provides only fleeting, temporary protection.

### 9. Quick Revision
* IOC = Indicator of Compromise (digital forensic footprint of an attack).
* Pyramid of Pain: Hashes and IPs are trivial to evade; TTPs are tough to change.
* Threat intelligence feeds automate perimeter blocking of high-confidence IOCs.
* Correlating network logs with host endpoint telemetry unmasks full attack timelines.

### 10. Interview Check
**Q: Explain David Bianco's 'Pyramid of Pain' and why detecting adversary TTPs is significantly more valuable than blocking malicious IP addresses.**  
**A:** The Pyramid of Pain shows that blocking low-level indicators like IP addresses or file hashes causes minimal disruption to sophisticated adversaries, who can change IPs and recompile malware in seconds. Detecting and disrupting **Tactics, Techniques, and Procedures (TTPs)** targets the attacker's core operational methodology, forcing them to spend weeks re-engineering their entire intrusion framework and re-training operators.
""",
    },
    # 34. Detection Engineering
    {
        "topic_slug": "detection-engineering-concepts",
        "title": "Detection Engineering & Rule Authoring",
        "slug": "detection-engineering-rule-authoring",
        "description": "The detection lifecycle, authoring Sigma rules, Snort/Suricata signatures, and tuning false positives.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.ADVANCED,
        "estimated_minutes": 45,
        "content": """# Detection Engineering & Rule Authoring

### 1. What is it? (Simple Explanation)
Imagine an airport metal detector. If you set its sensitivity too low, passengers walk through carrying dangerous weapons without triggering an alarm (False Negative / Catastrophic Breach). If you set its sensitivity too high, the detector shrieks every time someone walks through wearing a metal belt buckle or wrist watch, creating 3-hour security lines and causing guards to ignore the alarm completely (False Positive / Alert Fatigue).

**Detection Engineering** is the disciplined science of building, testing, and fine-tuning automated detection rules so security monitors catch genuine cyber threats accurately without drowning defenders in false alarms.

### 2. Technical Explanation
Detection Engineering is a software engineering discipline applied to defensive cybersecurity. It transforms threat intelligence and attacker behaviors into reliable, automated detection code.

The Detection Engineering Lifecycle:
1. **Threat Modeling & Hypothesis**: Research an adversary technique (e.g., MITRE ATT&CK T1059.001 - PowerShell Download Cradles).
2. **Telemetry Identification**: Determine which specific log source captures this activity (e.g., Windows Event ID 4104 Script Block Logging or Zeek HTTP logs).
3. **Rule Authoring**: Write precise detection logic using open standards like **Sigma** or **Snort/Suricata**.
4. **Adversary Emulation & Testing**: Execute the attack in a controlled test lab (using frameworks like Atomic Red Team) to verify the rule triggers.
5. **False Positive Tuning**: Test against baseline production data to eliminate noisy benign triggers.
6. **Deployment & Monitoring**: Deploy rule to SIEM/EDR and monitor detection fidelity.

### 3. Authoring Generic Detection Rules: The Sigma Standard
**Sigma** is the open-source, vendor-neutral rule format that allows engineers to write detection logic once in YAML and compile it into any target SIEM language (Splunk, Elastic, Microsoft Sentinel):

```yaml
title: Suspicious PowerShell Web Request to External IP
id: b8f4a1c0-21a4-4e2b-8a89-94e82b794f31
status: production
description: Detects PowerShell executing download cradle methods toward numerical IP addresses
logsource:
    category: process_creation
    product: windows
detection:
    selection:
        Image|endswith: '\\powershell.exe'
        CommandLine|contains:
            - 'DownloadFile'
            - 'DownloadString'
            - 'Invoke-WebRequest'
            - 'iwr'
        CommandLine|contains|regex: 'https?://[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}\\.[0-9]{1,3}'
    condition: selection
level: high
tags:
    - attack.execution
    - attack.t1059.001
```

### 4. Network IDS Rule Authoring (Suricata Syntax)
Detecting Cobalt Strike default malleable C2 HTTP profile:
```text
alert http $HOME_NET any -> $EXTERNAL_NET any (
    msg:"ET MALWARE Cobalt Strike Beacon Observed";
    flow:established,to_server;
    http.method; content:"GET";
    http.header; content:"Cookie: __cfduid=";
    http.uri; content:"/submit.php?id=";
    classtype:trojan-activity;
    sid:2030045;
    rev:2;
)
```

### 5. Visual Explanation: The Detection Engineering Pipeline
```
[Threat Intel: New Ransomware TTP]
               │
               ▼
[Identify Log Source (Sysmon / NetFlow)]
               │
               ▼
[Draft Detection Rule (Sigma / Snort)]
               │
               ▼
[Replay Synthetic Attack in Sandbox] ──(Did Rule Alert?)──> [No: Refine Logic]
               │ (Yes!)
               ▼
[Benchmark Against 30 Days of Production Logs]
               │ (Tune out False Positives)
               ▼
[Production SIEM Deployment -> High Fidelity Alert to SOC]
```

### 6. Command Examples
Using `sigmac` (pySigma) to translate a Sigma rule into Splunk SPL query:
```bash
# Convert generic Sigma rule to Splunk Search Processing Language
sigma convert -t splunk -p sysmon rules/windows/process_creation/proc_creation_win_powershell_download.yml
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **Alert Fatigue Elimination**: SOC analysts triage hundreds of alerts every shift. A single poorly written detection rule that generates 5,000 false positives per day burns out analysts and leads to real intrusions being ignored. Detection engineers are measured by **Alert Fidelity** (percentage of alerts that represent true security threats).
* **MITRE ATT&CK Gap Analysis**: Detection engineering teams map their active rule coverage against the MITRE ATT&CK matrix to visually identify blind spots where the organization currently has zero automated detection.

### 8. Common Troubleshooting Mistakes
* Writing rules based strictly on tool names: Authoring a rule that matches `mimikatz.exe` is useless because an attacker can rename the binary to `svchost.exe` in one second. Reliable detection rules trigger on underlying behavioral actions (like accessing `lsass.exe` memory handles) regardless of filename.

### 9. Quick Revision
* Detection Engineering turns threat intelligence into automated detection code.
* Lifecycle: Hypothesis -> Telemetry -> Authoring -> Emulation -> Tuning.
* Sigma = Open vendor-neutral detection rule standard.
* Priority goal: High detection fidelity, zero alert fatigue.

### 10. Interview Check
**Q: What is the difference between a False Positive and a False Negative, and why do detection engineers invest significant effort into tuning false positives?**  
**A:** A False Positive is benign, legitimate traffic that is incorrectly flagged as an attack. A False Negative is a genuine malicious attack that slips past undetected. Detection engineers invest heavily into tuning false positives because high false positive rates cause **alert fatigue**, leading overwhelmed SOC analysts to ignore or disable noisy alerts, which inadvertently creates blind spots where true attacks go unnoticed.
""",
    },
    # 35. Network Reconnaissance Detection
    {
        "topic_slug": "recon-detection",
        "title": "Network Reconnaissance & Port Scan Detection",
        "slug": "reconnaissance-port-scan-detection",
        "description": "Detecting Nmap scans, horizontal IP sweeps, vertical port probes, and adversary discovery TTPs.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.ADVANCED,
        "estimated_minutes": 40,
        "content": """# Network Reconnaissance & Port Scan Detection

### 1. What is it? (Simple Explanation)
Imagine a burglar casing an upscale neighborhood late at night. The burglar doesn't immediately take a sledgehammer to the first front door; they walk quietly down the street, testing the doorknob of every house, checking every ground-floor window, and peering through garage doors to see which houses are unoccupied and unlocked.

In cybersecurity, **Network Reconnaissance** is Phase 1 of an intrusion. Attackers systematically probe subnets and port numbers to discover which servers are active and which software services are vulnerable before launching an exploit.

### 2. Technical Explanation
Reconnaissance is categorized into two scanning geometries:
1. **Horizontal Scan (Ping Sweep / Host Discovery)**: Probing a **single port** across **hundreds of different IP addresses** (e.g., scanning `10.0.0.0/16` on Port 445 to find all active Windows domain controllers).
2. **Vertical Scan (Port Scan)**: Probing **hundreds of different ports** on a **single target IP address** (e.g., scanning ports 1 through 65,535 on `192.168.1.100` to find every listening service).

### 3. Primary Port Scanning Techniques (Nmap Mechanics)
* **TCP Connect Scan (`nmap -sT`)**: Completes the full 3-way handshake (`SYN -> SYN-ACK -> ACK`) and immediately terminates with `FIN` or `RST`. Requires no raw socket privileges, but easily logged by application servers.
* **TCP SYN Stealth Scan (`nmap -sS`)**: The industry standard. Sends a raw `SYN`. If the server replies `SYN-ACK`, Nmap knows the port is **OPEN** and immediately sends an `RST` to abort without completing the handshake!
* **UDP Scan (`nmap -sU`)**: Sends UDP probe datagrams. If an ICMP Type 3 Code 3 (Port Unreachable) error returns, the port is **CLOSED**. If no reply returns or service data returns, the port is **OPEN / FILTERED**.
* **TCP NULL / FIN / XMAS Scans**: Sends malformed packets violating RFC 793 to bypass stateless packet filters.

### 4. Visual Explanation: SYN Stealth Scan vs TCP Connect Scan
```
SYN Stealth Scan (nmap -sS):
Attacker                                           Target Server
   │                                                     │
   ├─── 1. TCP [SYN] Port 80 ───────────────────────────>│
   │<── 2. TCP [SYN, ACK] (Port is OPEN!) ───────────────┤
   ├─── 3. TCP [RST] (Tear down immediately!) ──────────>│
   │    (Connection never completes; unlogged by Apache) │

TCP Connect Scan (nmap -sT):
Attacker                                           Target Server
   │                                                     │
   ├─── 1. TCP [SYN] Port 80 ───────────────────────────>│
   │<── 2. TCP [SYN, ACK] ───────────────────────────────┤
   ├─── 3. TCP [ACK] (Connection ESTABLISHED) ──────────>│
   │    [Logged in web server access.log!]               │
   ├─── 4. TCP [RST / FIN] ─────────────────────────────>│
```

### 5. Detection Signatures & Metrics
Defensive systems detect port scanning through **Thresholding Rules**:
* **Connection Rate Threshold**: A single source IP initiating TCP connections to more than 25 distinct destination ports within a 10-second sliding window.
* **Failed Connection Ratio**: Normal applications establish successful connections; port scans generate a massive ratio of `RST` packets (closed ports) or timeouts relative to successful `ESTABLISHED` sessions.

### 6. Command Examples
Using Snort/Suricata thresholding to alert on port scanning:
```text
# Detect single source connecting to > 20 ports on a single host in 60 seconds
threshold type threshold, track by_src, count 20, seconds 60
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **Early Kill Chain Intervention**: Reconnaissance is Step 1 of the Cyber Kill Chain and MITRE ATT&CK (Technique T1046 - Network Service Discovery). Detecting an attacker at the scanning stage allows SOC teams to block the source IP before the attacker identifies unpatched vulnerabilities and delivers exploits.
* **Deception Technology & Honeypots**: Defensive teams deploy lightweight virtual decoy IP addresses (**Honeypots**) on unused internal subnet addresses. Because no legitimate employee machine ever needs to communicate with an unused decoy IP, any incoming port scan instantly triggers a 100% high-fidelity critical alert!

### 8. Common Troubleshooting Mistakes
* Alerting on internal vulnerability scanners: Internal security tools (like Nessus or Qualys) routinely scan the network for authorized patch management audits. Detection engineers must create explicit whitelist exceptions for authorized scanner IPs.

### 9. Quick Revision
* Horizontal scan = 1 port across many hosts; Vertical scan = many ports on 1 host.
* SYN stealth scan (`nmap -sS`) unmasks open ports without completing the 3-way handshake.
* Detect via thresholding: High connection rate to multiple ports + high RST ratio.
* Catch scans early with **Honeypot Decoy IPs**.

### 10. Interview Check
**Q: How does a TCP SYN scan distinguish between an Open port, a Closed port, and a Filtered port?**  
**A:**  
* **Open Port**: The target returns a TCP **SYN-ACK** response.  
* **Closed Port**: The target returns a TCP **RST** (Reset) response.  
* **Filtered Port**: The probe packet is dropped silently by a firewall (no response returned within the timeout window) or the firewall returns an **ICMP Type 3 (Destination Unreachable)** error packet.
""",
    },
    # 36. Incident Investigation & Triage
    {
        "topic_slug": "alert-triage",
        "title": "SOC Incident Investigation & Alert Triage Workflow",
        "slug": "soc-incident-investigation-alert-triage",
        "description": "Tier 1 triage methodology, gathering forensic evidence, timeline reconstruction, and escalation matrices.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.ADVANCED,
        "estimated_minutes": 45,
        "content": """# SOC Incident Investigation & Alert Triage Workflow

### 1. What is it? (Simple Explanation)
Imagine an emergency room (ER) nurse at a hospital. When ten patients arrive simultaneously in the waiting room, the triage nurse quickly assesses each one: a patient with a minor finger scrape is asked to wait, while a patient experiencing severe chest pains is immediately rushed to the trauma bay with doctors alerted.

A **Security Operations Center (SOC) Tier 1 Analyst** performs this exact emergency triage for cyber threats. When alerts fire in the SIEM console, analysts systematically investigate, gather forensic evidence, determine if the threat is genuine, and initiate containment.

### 2. The 5-Step SOC Triage Workflow
When an alert appears in the SIEM (e.g., *"Potential Cobalt Strike C2 Beaconing Observed"*):
1. **Step 1: Ingestion & Validation**
   * Review the triggering rule logic, timestamp, and affected assets.
   * Identify Source IP, Destination IP, user account, and process names.
2. **Step 2: Contextual Scope Gathering**
   * Is the affected host an internal employee laptop, an external web server, or a core domain controller?
   * What is the threat reputation of the external IP on VirusTotal / AbuseIPDB?
3. **Step 3: Verification (True Positive vs False Positive)**
   * **True Positive (TP)**: The activity is genuinely malicious (e.g., malware beaconing).
   * **False Positive (FP)**: The activity is benign business traffic that triggered a rigid rule (e.g., an admin testing a new software installer). Close alert with documented rationale.
4. **Step 4: Containment & Remediation**
   * If confirmed True Positive: Isolate the host from the network immediately via EDR to prevent lateral movement.
   * Block the external C2 domain/IP at the perimeter firewall.
   * Revoke compromised user credentials.
5. **Step 5: Escalation & Timeline Documentation**
   * Escalate to Tier 2 Incident Responders with a detailed, chronological investigative summary.

### 3. Incident Severity Matrix
* **Severity 1 (Critical)**: Active ransomware encryption, domain controller compromise, confirmed data exfiltration. Response: 15 minutes.
* **Severity 2 (High)**: Individual workstation infected with remote access trojan (RAT), unauthorized privilege escalation. Response: 1 hour.
* **Severity 3 (Medium)**: Internal port scanning, repeated failed login attempts from external IP. Response: 4 hours.
* **Severity 4 (Low)**: Adware detected and quarantined by endpoint antivirus. Response: 24 hours.

### 4. Visual Explanation: SOC Triage Decision Tree
```
[SIEM Alert Fires: High Severity]
               │
               ▼
   [Query Internal Asset DB & IP Reputation]
               │
      Is Destination IP Known Malicious?
             /                  \\
           (No)                 (Yes)
           /                      \\
[Investigate Process]         [TRUE POSITIVE CONFIRMED!]
[Benign Admin Tool?]                       │
   /              \\                       ├─ 1. Isolate Host via EDR
 (Yes)            (No)                     ├─ 2. Block External IP on Firewall
   │               │                       ├─ 3. Reset User Credentials
[Close: FP]    [Investigate Deeper]        └─ 4. Escalate to Incident Response Tier 2
```

### 5. Constructing an Investigation Timeline
A forensic timeline reconstructs the sequence of events with UTC timestamps:
* `14:22:01 UTC`: User opens phishing email attachment `invoice.pdf.exe`.
* `14:22:15 UTC`: PowerShell process spawned (`PID 4912`), executing download cradle.
* `14:22:20 UTC`: Outbound HTTP GET request to `198.51.100.88:8080/stage.bin`.
* `14:22:35 UTC`: New service `WindowsUpdateHelper` registered with persistence.
* `14:23:00 UTC`: Host initiates SMB port scan across internal subnet `10.0.1.0/24`.
* `14:25:00 UTC`: SOC Analyst receives alert, verifies C2 communication, and triggers host network isolation.

### 6. Command Examples
Querying SIEM logs using Splunk Search Processing Language (SPL):
```text
# Splunk query: Hunt for outbound connections to target IP and identify responsible process
index=network dest_ip="198.51.100.88" 
| stats count by _time, src_ip, dest_port, process_name
| sort -_time
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **Mean Time to Detect (MTTD) & Mean Time to Respond (MTTR)**: The two golden metrics of any cybersecurity defense organization. Reducing MTTR from days to minutes stops adversaries in the initial foothold stage before they can deploy enterprise-wide ransomware.
* **Preserving Chain of Custody**: When investigating serious corporate espionage or breach incidents, digital evidence (disk images, PCAPs, volatile RAM dumps) must be preserved with cryptographic hashes to ensure admissibility in legal court proceedings.

### 8. Common Troubleshooting Mistakes
* Immediately powering off an infected computer: Never pull the power plug on an active machine! Powering off destroys volatile RAM, eliminating running process memory, injected DLLs, unwritten network sockets, and encryption keys vital for forensic analysis. Use **Network Isolation** instead!

### 9. Quick Revision
* Triage workflow: Validate -> Gather Context -> Verify TP/FP -> Contain -> Escalate.
* Always construct an accurate chronological forensic timeline.
* Never pull the power plug (destroys volatile memory); use network isolation.
* Measure success by MTTD (detection speed) and MTTR (containment speed).

### 10. Interview Check
**Q: You receive an alert that a critical database server is communicating with a known Command & Control (C2) IP address. What are your immediate first three actions as a SOC analyst?**  
**A:**  
1. **Verify and Contain**: Verify the alert is a True Positive and immediately isolate the database server logically from the network (via firewall block or EDR containment) to prevent data exfiltration or lateral movement while keeping the system powered on to preserve volatile RAM.  
2. **Block Indicator**: Block the destination C2 IP address at the perimeter firewall and perimeter proxy to stop all outbound traffic across the enterprise.  
3. **Escalate and Document**: Notify the Incident Response lead and database administrator, document the initial timeline, and begin volatile memory acquisition and forensic log extraction.
""",
    },
]
