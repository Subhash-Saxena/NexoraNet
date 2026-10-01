# NexoraNet Detection Rule Catalog

> **Version:** 1.0 (Step 11)  
> **Rule Count:** 15 Standard Deterministic Rules  
> **Framework Alignment:** MITRE ATT&CK Enterprise Matrix

---

## Catalog Overview

| Rule ID | Category | Severity | Name | MITRE ATT&CK | Logic Type |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `NET-TCP-001` | TCP | HIGH | Repeated TCP SYN Connection Attempts | T1046 | `SYN_BURST_DETECTION` |
| `NET-TCP-002` | TCP | MEDIUM | TCP RST Spike Following SYN Requests | T1046 | `RST_SPIKE_DETECTION` |
| `NET-TCP-003` | TCP | HIGH | Incomplete TCP Handshake Ratio Above Threshold | T1498 | `INCOMPLETE_HANDSHAKE_RATIO` |
| `NET-CONN-001` | TRAFFIC | MEDIUM | Beaconing Pattern with Regular Intervals | T1071 | `BEACONING_DETECTION` |
| `NET-CONN-002` | RECON | HIGH | Horizontal Host Sweep Across Subnet | T1018 | `HORIZONTAL_SWEEP` |
| `NET-DNS-001` | DNS | MEDIUM | DNS NXDOMAIN Response Burst | T1568.002 | `DNS_NXDOMAIN_BURST` |
| `NET-DNS-002` | DNS | MEDIUM | High-Entropy DNS Subdomain Query Pattern | T1071.004 | `DNS_HIGH_ENTROPY` |
| `NET-DNS-003` | DNS | HIGH | Excessive DNS Request Rate to External Resolver | T1071.004 | `DNS_BURST_VOLUME` |
| `NET-ARP-001` | ARP | CRITICAL | Conflicting MAC Address Mapping for Single IPv4 | T1557.002 | `ARP_CONFLICT_DETECTION` |
| `NET-ICMP-001` | ICMP | MEDIUM | High-Rate ICMP Echo Request Sequence | T1018 | `ICMP_FLOOD_BURST` |
| `NET-PORT-001` | SUSPICIOUS_PORT | HIGH | Traffic Involving Suspicious High-Risk Port | T1071 | `SUSPICIOUS_PORT_TRAFFIC` |
| `NET-TRAFFIC-001`| TRAFFIC | MEDIUM | Flow Byte Ratio Asymmetry Above Threshold | T1048 | `ASYMMETRIC_FLOW_VOLUME` |
| `NET-TRAFFIC-002`| TRAFFIC | MEDIUM | High-Frequency Packet Burst Over Short Window | T1498 | `PACKET_BURST_RATE` |
| `NET-HTTP-001` | HTTP | LOW | HTTP Cleartext Authentication in Packet Payload | T1552 | `HTTP_CLEARTEXT_AUTH` |
| `NET-RECON-001` | RECON | HIGH | Multi-Port Vertical Scan Against Target Host | T1046 | `VERTICAL_PORT_SCAN` |

---

## Detailed Rule Specifications

### 1. `NET-TCP-001`: Repeated TCP SYN Connection Attempts
- **Category:** TCP
- **Severity:** HIGH
- **Default Threshold:** $\ge 5$ SYN packets within 10 seconds without completed three-way handshake.
- **MITRE Technique:** T1046 (Network Service Discovery)
- **Explanation:** Repeated initial TCP SYN packets without completed handshakes indicate that a client is probing for listening network services or attempting rapid connection initialization.
- **Benign Causes:** Unresponsive web server, aggressive browser reconnection logic, mobile network failover, network firewall silently dropping packets.

---

### 2. `NET-TCP-002`: TCP RST Spike Following SYN Requests
- **Category:** TCP
- **Severity:** MEDIUM
- **Default Threshold:** $\ge 4$ RST packets received within 10 seconds.
- **MITRE Technique:** T1046 (Network Service Discovery)
- **Explanation:** A spike in TCP RST (Reset) packets returned by an endpoint typically signals that targeted destination ports are closed or rejecting connections.
- **Benign Causes:** Legacy software scanning local loopback ports, closed server ports, stale keep-alive sessions terminated by middleboxes.

---

### 3. `NET-TCP-003`: Incomplete TCP Handshake Ratio Above Threshold
- **Category:** TCP
- **Severity:** HIGH
- **Default Threshold:** Incomplete handshake ratio $\ge 70\%$ with at least 8 total connection attempts.
- **MITRE Technique:** T1498 (Network Denial of Service)
- **Explanation:** A high percentage of incomplete handshakes where SYN packets are sent but never culminate in established sessions suggests network reconnaissance or SYN exhaustion attempts.
- **Benign Causes:** Network routing asymmetry, upstream packet loss, dead server daemon.

---

### 4. `NET-CONN-001`: Beaconing Pattern with Regular Intervals
- **Category:** TRAFFIC
- **Severity:** MEDIUM
- **Default Threshold:** $\ge 5$ periodic events with an interval standard deviation $\le 1.5$ seconds.
- **MITRE Technique:** T1071 (Application Layer Protocol)
- **Explanation:** Consistently timed connection requests with low statistical variance indicate automated periodic check-ins or heartbeat polling.
- **Benign Causes:** NTP synchronization, OS telemetry checks, RSS feed polling, DNS keepalives.

---

### 5. `NET-CONN-002`: Horizontal Host Sweep Across Subnet
- **Category:** RECON
- **Severity:** HIGH
- **Default Threshold:** Single source contacting $\ge 6$ distinct destination IPs on the same destination port.
- **MITRE Technique:** T1018 (Remote System Discovery)
- **Explanation:** A single source sequentially contacting multiple IP addresses within the same subnet on a uniform port indicates horizontal host discovery.
- **Benign Causes:** Asset discovery tooling, network management system (NMS) discovery sweep, Bonjour/mDNS service location.

---

### 6. `NET-DNS-001`: DNS NXDOMAIN Response Burst
- **Category:** DNS
- **Severity:** MEDIUM
- **Default Threshold:** $\ge 5$ NXDOMAIN (Non-Existent Domain) responses within 15 seconds.
- **MITRE Technique:** T1568.002 (Domain Generation Algorithms)
- **Explanation:** A burst of failed domain name resolutions indicates that the host queried nonexistent domain names, characteristic of DGAs or mistyped internal services.
- **Benign Causes:** Stale search-domain suffixes, decommissioned corporate hosts, local DNS typo burst.

---

### 7. `NET-DNS-002`: High-Entropy DNS Subdomain Query Pattern
- **Category:** DNS
- **Severity:** MEDIUM
- **Default Threshold:** Subdomain Shannon entropy $\ge 3.8$ bits or subdomain length $> 25$ characters.
- **MITRE Technique:** T1071.004 (DNS Tunneling)
- **Explanation:** DNS queries containing high-entropy, randomized subdomains can indicate encoded data transmission or automated domain generation.
- **Benign Causes:** Anti-spam DNSBL lookups, CDN routing tags (e.g., Akamai/Cloudflare subdomains), AV definition update lookups.

---

### 8. `NET-DNS-003`: Excessive DNS Request Rate to External Resolver
- **Category:** DNS
- **Severity:** HIGH
- **Default Threshold:** $\ge 20$ DNS query packets within 5 seconds.
- **MITRE Technique:** T1071.004 (Application Layer Protocol: DNS)
- **Explanation:** An unusually elevated rate of outbound DNS requests can indicate DNS tunneling, rapid automated lookup sweeps, or recursive amplification testing.
- **Benign Causes:** Web browser prefetching links on a complex news site, email server resolving MX records in bulk.

---

### 9. `NET-ARP-001`: Conflicting MAC Address Mapping for Single IPv4
- **Category:** ARP
- **Severity:** CRITICAL
- **Default Threshold:** Single IPv4 address claimed by $\ge 2$ different MAC addresses in ARP packets.
- **MITRE Technique:** T1557.002 (ARP Spoofing / Poisoning)
- **Explanation:** Multiple MAC addresses claiming ownership of the same IPv4 address indicates duplicate IP configuration or potential ARP cache poisoning.
- **Benign Causes:** Virtual IP failover (VRRP / HSRP / CARP), NIC teaming, roaming WiFi client changing APs.

---

### 10. `NET-ICMP-001`: High-Rate ICMP Echo Request Sequence
- **Category:** ICMP
- **Severity:** MEDIUM
- **Default Threshold:** $\ge 15$ ICMP Echo Request packets within 3 seconds.
- **MITRE Technique:** T1018 (Remote System Discovery)
- **Explanation:** Rapid bursts of ICMP Echo Requests (ping) typically indicate active network host discovery or MTU path testing.
- **Benign Causes:** Network administrator ping diagnostic (`ping -f` or `ping -t`), link latency measurement tool.

---

### 11. `NET-PORT-001`: Traffic Involving Suspicious High-Risk Port
- **Category:** SUSPICIOUS_PORT
- **Severity:** HIGH
- **Default Threshold:** Packet observed on known risk ports: 4444 (Metasploit default), 1337, 31337, 6667 (IRC botnets), 5555 (ADB).
- **MITRE Technique:** T1071 (Non-Standard Application Port)
- **Explanation:** Network communication observed on ports historically designated for remote control tools, penetration testing frameworks, or IRC botnets.
- **Benign Causes:** Custom development services, test harness servers, non-standard HTTP proxies.

---

### 12. `NET-TRAFFIC-001`: Flow Byte Ratio Asymmetry Above Threshold
- **Category:** TRAFFIC
- **Severity:** MEDIUM
- **Default Threshold:** Outbound byte volume is $\ge 10\times$ higher than inbound volume with $> 100\text{ KB}$ sent.
- **MITRE Technique:** T1048 (Exfiltration Over Alternative Protocol)
- **Explanation:** Significant disproportion between transmitted and received bytes in an interactive session can indicate bulk data exfiltration or large file upload.
- **Benign Causes:** Cloud backup sync, video upload to streaming service, software artifact deployment.

---

### 13. `NET-TRAFFIC-002`: High-Frequency Packet Burst Over Short Window
- **Category:** TRAFFIC
- **Severity:** MEDIUM
- **Default Threshold:** $\ge 50$ packets within a rolling 1.0-second window.
- **MITRE Technique:** T1498 (Network Denial of Service)
- **Explanation:** A rapid surge of packets concentrated in a sub-second interval suggests burst transmission, buffer stress testing, or automated packet flood.
- **Benign Causes:** Video streaming buffering, software package manager updates, database backup ingestion.

---

### 14. `NET-HTTP-001`: HTTP Cleartext Authentication in Packet Payload
- **Category:** HTTP
- **Severity:** LOW
- **Default Threshold:** Observation of `Authorization: Basic` or login credentials over unencrypted HTTP (Port 80/8080).
- **MITRE Technique:** T1552 (Unsecured Credentials)
- **Explanation:** Transmission of user credentials over unencrypted HTTP exposes tokens and passwords to eavesdropping and credential harvesting on local subnets.
- **Benign Causes:** Legacy router administrative interface, local lab testbed without TLS certificates.

---

### 15. `NET-RECON-001`: Multi-Port Vertical Scan Against Target Host
- **Category:** RECON
- **Severity:** HIGH
- **Default Threshold:** Single source querying $\ge 8$ distinct ports on a single destination host within 15 seconds.
- **MITRE Technique:** T1046 (Network Service Discovery)
- **Explanation:** A source sequentially or concurrently checking multiple ports on a single host indicates a vertical port scan intended to map accessible services.
- **Benign Causes:** Vulnerability scanner scheduled audit, system administrator port validation, local service discovery daemon.
