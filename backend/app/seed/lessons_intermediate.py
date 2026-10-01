# NexoraNet Intermediate Curriculum Lessons (12 Comprehensive Lessons)
from app.models.enums import ContentType, DifficultyLevel

INTERMEDIATE_LESSONS = [
    # 17. Subnetting
    {
        "topic_slug": "subnetting",
        "title": "IPv4 Subnetting & Address Partitioning",
        "slug": "ipv4-subnetting-partitioning",
        "description": "Borrowing host bits to create subnets, determining subnet boundaries, and calculating usable hosts.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 35,
        "content": """# IPv4 Subnetting & Address Partitioning

### 1. What is it? (Simple Explanation)
Imagine you own a large plot of land. If you leave it as one giant open field, hundreds of people might wander around aimlessly, shouting across the property and causing chaos. Instead, you divide the land into neat, gated residential cul-de-sacs with their own private streets and addresses.

**Subnetting** is dividing a large single IP network block into multiple smaller, logically isolated sub-networks (subnets).

### 2. Technical Explanation
In Classless Inter-Domain Routing (CIDR), an IP address is partitioned into a **Network Portion** and a **Host Portion**. Subnetting borrows bits from the host portion and assigns them to the network portion, effectively creating sub-networks.

The two fundamental formulas of subnetting:
* **Number of Created Subnets**: \\(2^n\\), where \\(n\\) is the number of borrowed bits.
* **Usable Hosts per Subnet**: \\(2^h - 2\\), where \\(h\\) is the number of remaining host bits.
  *(We subtract 2 because the very first address is the **Network ID** and the very last address is the **Broadcast Address**; neither can be assigned to an interface).*

### 3. Step-by-Step Calculation: Subnetting a /24 into /26
Suppose your company is allocated `192.168.1.0/24` (256 total IP addresses). You need to split this into 4 separate departments.
1. To get 4 subnets: \\(2^n = 4 \\implies n = 2\\) bits borrowed.
2. New prefix length: \\(24 + 2 = /26\\).
3. Remaining host bits: \\(32 - 26 = 6\\) bits.
4. Usable hosts per subnet: \\(2^6 - 2 = 64 - 2 = 62\\) usable hosts per department.
5. **Block Size (Magic Number)**: \\(256 - 192 = 64\\) (increment value).

The 4 Resulting Subnets:
* **Subnet 1**: Network: `192.168.1.0/26` | Usable: `.1` – `.62` | Broadcast: `.63`
* **Subnet 2**: Network: `192.168.1.64/26` | Usable: `.65` – `.126` | Broadcast: `.127`
* **Subnet 3**: Network: `192.168.1.128/26` | Usable: `.129` – `.190` | Broadcast: `.191`
* **Subnet 4**: Network: `192.168.1.192/26` | Usable: `.193` – `.254` | Broadcast: `.255`

### 4. Real-World Scenario
A hospital network requires separate subnets for:
1. Patient Medical Monitors (High Security)
2. Administrative Staff (Medium Security)
3. Guest Patient Wi-Fi (Low Security / Untrusted)
Subnetting ensures that a compromised laptop on the Guest Wi-Fi cannot directly broadcast or send packets to intensive care life-support monitors without traversing an intervening firewall.

### 5. Visual Explanation: Binary Bit Borrowing
```
Original /24 Mask: 255.255.255.0
11111111 . 11111111 . 11111111 . [ 0 0 0 0 0 0 0 0 ]  (254 hosts)

Subnetted /26 Mask: 255.255.255.192
11111111 . 11111111 . 11111111 . [ 1 1 | 0 0 0 0 0 0 ]
                                   Subnet   Host Bits (62 hosts/sub)
```

### 6. Command Examples
Verify your current subnet mask and network calculation:
```powershell
# Windows PowerShell: View IP and IPv4 Subnet Mask length
Get-NetIPAddress -AddressFamily IPv4 | Format-Table IPAddress, PrefixLength, InterfaceAlias
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **Blast Radius Reduction**: In an unsegmented flat network, malware (like worm-based ransomware) broadcasts ARP probes and scans every host on the network within seconds. Subnetting confines broadcasts to local segments, forcing inter-subnet traffic through firewall inspection points.
* **Micro-segmentation**: Zero-Trust security models employ ultra-small subnets (even `/30` or `/32` point-to-point links) to enforce least-privilege traffic flow between individual application tiers.

### 8. Common Troubleshooting Mistakes
* Assigning the Network ID or Broadcast address to a host interface: Configuring a computer with `192.168.1.64/26` will result in an "Invalid IP Address" error because `.64` is the network identifier.
* Subnet Mask Mismatches: If Host A has mask `255.255.255.0` and Host B on the same wire has `255.255.255.192`, Host A will think Host B is local while Host B will attempt to send replies through its gateway, causing asymmetric connection failures.

### 9. Quick Revision
* Subnetting = borrowing host bits to create sub-networks.
* Subnets = \\(2^n\\); Usable hosts = \\(2^h - 2\\).
* Always reserve the first address (Network ID) and last address (Broadcast).
* Isolates broadcast domains and limits cyber incident blast radiuses.

### 10. Interview Check
**Q: Given the IP address `10.10.5.130/28`, calculate the Network Address, Broadcast Address, and number of usable host addresses.**  
**A:** A `/28` prefix leaves \\(32 - 28 = 4\\) host bits. Total addresses per block = \\(2^4 = 16\\). The multiples of 16 closest to 130 are 128 and 144.  
* **Network Address**: `10.10.5.128`  
* **Broadcast Address**: `10.10.5.143` (128 + 16 - 1)  
* **Usable Host Range**: `10.10.5.129` through `10.10.5.142`  
* **Usable Hosts**: \\(2^4 - 2 = 14\\) hosts.
""",
    },
    # 18. CIDR
    {
        "topic_slug": "cidr",
        "title": "Classless Inter-Domain Routing (CIDR) & Prefix Notation",
        "slug": "cidr-prefix-notation-summarization",
        "description": "Slash notation, eliminating obsolete classful boundaries, and route summarization.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 30,
        "content": """# Classless Inter-Domain Routing (CIDR) & Prefix Notation

### 1. What is it? (Simple Explanation)
In the early days of the Internet, IP addresses were handed out in rigid, inflexible packages called "Classes": Class A gave you 16 million addresses (way too many for almost anyone), and Class C gave you 256 addresses (often too few for medium businesses). This caused massive waste of the IPv4 address pool.

**CIDR (Classless Inter-Domain Routing)**, introduced in 1993, threw away those rigid classes and allowed network engineers to cut IP blocks to any custom size needed using convenient slash notation like `/23` or `/28`.

### 2. Technical Explanation
CIDR (RFC 1519) replaces class-based allocation with **Prefix Routing**:
* The prefix notation (e.g., `/24`) specifies exactly how many contiguous bits in the 32-bit address represent the Network ID.
* The remaining bits represent the Host ID.

### CIDR Prefix to Subnet Mask Conversion Table
| CIDR Prefix | Subnet Mask | Total Addresses | Usable Hosts |
| :--- | :--- | :--- | :--- |
| **/30** | `255.255.255.252` | 4 | 2 (Point-to-Point links) |
| **/29** | `255.255.255.248` | 8 | 6 |
| **/28** | `255.255.255.240` | 16 | 14 |
| **/27** | `255.255.255.224` | 32 | 30 |
| **/26** | `255.255.255.192` | 64 | 62 |
| **/25** | `255.255.255.128` | 128 | 126 |
| **/24** | `255.255.255.0` | 256 | 254 |
| **/23** | `255.255.254.0` | 512 | 510 |
| **/22** | `255.255.252.0` | 1,024 | 1,022 |
| **/16** | `255.255.0.0` | 65,536 | 65,534 |

### 3. Route Summarization (Supernetting)
CIDR also enables **Route Summarization**: combining multiple contiguous smaller network prefixes into a single consolidated routing announcement.
Example: Instead of advertising four separate routes:
* `10.0.0.0/24`
* `10.0.1.0/24`
* `10.0.2.0/24`
* `10.0.3.0/24`
A core router can advertise a single summary route: `10.0.0.0/22`. This dramatically shrinks core Internet routing tables and saves router memory and CPU cycles.

### 4. Visual Explanation
```
Classful (Obsolete):
[ Class A (/8) ]      [ Class B (/16) ]      [ Class C (/24) ]
   16M Hosts              65K Hosts              254 Hosts

Classless (CIDR):
[ /30 ] [ /29 ] [ /28 ] ... [ /24 ] ... [ /20 ] ... [ /12 ]
  Any power-of-two block size matched to exact business need!
```

### 5. Command Examples
Using Python to calculate CIDR properties:
```python
import ipaddress
net = ipaddress.ip_network("192.168.10.0/27")
print(f"Mask: {net.netmask}")
print(f"Usable Hosts: {net.num_addresses - 2}")
print(f"Host Range: {list(net.hosts())[0]} - {list(net.hosts())[-1]}")
```

### 6. Cybersecurity Relevance (Defensive Perspective)
* **Firewall Rules & Cloud Security Groups**: Cloud access control lists (such as AWS Security Groups or Azure Network Security Groups) exclusively use CIDR notation to define inbound and outbound permissions. Writing `0.0.0.0/0` inadvertently opens the port to the entire global Internet!
* **BGP Route Hijacking**: Autonomous Systems announce IP prefixes via BGP. If a rogue network announces a more specific prefix (e.g., announcing a `/24` when the legitimate owner announces a `/22`), global routers prioritize the more specific route, redirecting traffic through the attacker's network.

### 7. Common Troubleshooting Mistakes
* The `/31` Subnet Exception: RFC 3021 permits `/31` subnets for point-to-point router links without reserving network/broadcast addresses, but legacy operating systems and end-user devices will reject `/31` configurations.

### 8. Quick Revision
* CIDR replaces legacy Class A/B/C networking with slash prefix notation.
* Prefix length (`/24`) indicates number of network bits.
* Enables Route Summarization to keep global routing tables scalable.
* Universal standard for cloud security groups and firewall rules.

### 9. Interview Check
**Q: How does Longest Prefix Match dictate routing decisions in CIDR?**  
**A:** When a router receives a packet, it compares the destination IP against its routing table. If multiple routes match the destination (e.g., `10.0.0.0/16` and `10.0.5.0/24`), the router always selects the route with the longest prefix (most specific mask, `/24`), because it represents the most precise path to the target.
""",
    },
    # 19. TCP Three-Way Handshake
    {
        "topic_slug": "tcp-three-way-handshake",
        "title": "TCP Three-Way Handshake Deep Dive",
        "slug": "tcp-three-way-handshake-deep-dive",
        "description": "SYN, SYN-ACK, ACK packet exchange, sequence numbers, and SYN flood defense.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 35,
        "content": """# TCP Three-Way Handshake Deep Dive

### 1. What is it? (Simple Explanation)
Imagine two radio operators communicating over long distances:
* Operator 1: *"Alpha, this is Bravo, can you hear me? Over."* (SYN)
* Operator 2: *"Bravo, this is Alpha, I hear you loud and clear. Can you hear me? Over."* (SYN-ACK)
* Operator 1: *"Alpha, I hear you too! Ready to transmit data."* (ACK)

Both operators have now verified that both the transmission and reception paths work in both directions before transmitting critical messages. This is the **TCP Three-Way Handshake**.

### 2. Technical Explanation
Before full-duplex byte stream transmission can begin, client and server must synchronize their Initial Sequence Numbers (ISNs) and confirm mutual socket readiness.

The handshake steps (RFC 793):
1. **SYN (Step 1)**: Client sends a TCP segment with control flag `SYN=1`.
   * Picks a random Initial Sequence Number: `Seq = ISN_Client`.
   * Sets options (Maximum Segment Size, Window Scaling, SACK).
   * Client state transitions: `CLOSED -> SYN-SENT`.
2. **SYN-ACK (Step 2)**: Server receives the SYN, allocates a transmission control block (TCB) in memory, and replies with `SYN=1, ACK=1`.
   * Acknowledges client's ISN: `Ack = ISN_Client + 1`.
   * Picks its own random Initial Sequence Number: `Seq = ISN_Server`.
   * Server state transitions: `LISTEN -> SYN-RECEIVED`.
3. **ACK (Step 3)**: Client confirms receipt with `ACK=1`.
   * Acknowledges server's ISN: `Ack = ISN_Server + 1`.
   * Both endpoints transition to `ESTABLISHED` state. Data can now flow.

### 3. Visual Sequence Diagram
```
Client Host                                      Server Host
(State: CLOSED)                                  (State: LISTEN)
      │                                                │
      ├─────── 1. [SYN] Seq=1000 ─────────────────────>│ (State: SYN-RECEIVED)
      │                                                │
      │<────── 2. [SYN, ACK] Seq=5000, Ack=1001 ───────┤
(State: ESTABLISHED)                                   │
      ├─────── 3. [ACK] Seq=1001, Ack=5001 ───────────>│ (State: ESTABLISHED)
      │                                                │
================ Data Transfer In Progress ================
```

### 4. Real-World Packet Dissection
In Wireshark:
* Frame 1: `TCP 66 52412 -> 443 [SYN] Seq=0 Win=64240 Len=0 MSS=1460`
* Frame 2: `TCP 66 443 -> 52412 [SYN, ACK] Seq=0 Ack=1 Win=65535 Len=0 MSS=1460`
* Frame 3: `TCP 54 52412 -> 443 [ACK] Seq=1 Ack=1 Win=64240 Len=0`

### 5. Cybersecurity Relevance (Defensive Perspective)
* **SYN Flood Attacks**: The server reserves kernel buffer memory at Step 2 (`SYN-RECEIVED`). Attackers send high volumes of spoofed SYN packets without sending Step 3. The server's connection backlog table fills up, rejecting legitimate users.
* **SYN Cookies**: A cryptographic countermeasure where the server encodes the connection state inside its own `ISN_Server` hash instead of allocating memory. Only when the client returns a valid ACK does the server allocate memory!
* **TCP Stealth Scan (SYN Scan)**: Tools like Nmap send a SYN packet. If the port replies with `SYN-ACK`, the port is **OPEN**. Nmap immediately sends an `RST` to terminate without completing the connection, evading older application-layer access logs.

### 6. Common Troubleshooting Mistakes
* Asymmetric routing drops: If the client's SYN travels via Firewall A, but the server's SYN-ACK returns via Router B, Firewall A will never see the SYN-ACK. When the client sends the final ACK, Firewall A drops it as an invalid out-of-state packet.

### 7. Quick Revision
* 3 Steps: SYN (Client) -> SYN-ACK (Server) -> ACK (Client).
* Establishes bidirectional sequence numbers and window sizing.
* Both sides end in `ESTABLISHED` state.
* Target of SYN flood attacks; defended with **SYN Cookies**.

### 8. Interview Check
**Q: Why does TCP use randomized Initial Sequence Numbers (ISNs) instead of starting every new connection at sequence number 0?**  
**A:** Randomized ISNs prevent **TCP Sequence Prediction and Session Hijacking** attacks. If ISNs were predictable (e.g., always starting at 0 or incrementing by a fixed amount), a blind off-path attacker could forge packets with the correct anticipated sequence numbers to inject malicious commands into an active session.
""",
    },
    # 20. DNS Resolution
    {
        "topic_slug": "dns-resolution",
        "title": "DNS Resolution Flow & Hierarchy",
        "slug": "dns-resolution-flow-hierarchy",
        "description": "Recursive vs iterative queries, root hints, TLD servers, and authoritative delegation.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 30,
        "content": """# DNS Resolution Flow & Hierarchy

### 1. What is it? (Simple Explanation)
Imagine you want to look up an obscure book in a multi-story library. You don't wander randomly; you ask the head research librarian at the front desk (Recursive Resolver). The librarian asks the Floor Director (Root Server), who points to the History Wing (TLD Server), who points to the 20th Century section shelf (Authoritative Server), pulls the exact book, and hands it back to you.

The **DNS Resolution Flow** is the systematic traversal through the global domain hierarchy to find the exact IP address mapped to any domain name.

### 2. Technical Explanation
DNS resolution uses two types of queries:
1. **Recursive Query**: The client requests: *"Find the IP address for `mail.example.com` or tell me it doesn't exist."* The recursive resolver bears the full burden of traversing the hierarchy until it finds the final answer.
2. **Iterative Query**: The resolver queries nameservers asking: *"Do you have this record?"* The queried nameserver replies: *"No, but I know the next authoritative server you should ask."*

### 3. Step-by-Step Resolution Architecture
When resolving `app.nexoranet.internal`:
1. **Stub Resolver (Client OS)**: Checks local memory cache and `/etc/hosts`. If not found, sends a recursive query to configured resolver (e.g., `8.8.8.8`).
2. **Root Nameservers (`.` )**: 13 root server clusters (`a.root-servers.net` to `m.root-servers.net`). Directs resolver to the TLD nameserver.
3. **TLD Nameservers (`.internal` / `.com`)**: Manages Top-Level Domain registry records. Refers resolver to the domain's Authoritative Nameservers.
4. **Authoritative Nameservers**: Holds the master zone file records. Returns the definitive `A` record containing the final destination IP address.
5. **Resolver Response & Caching**: Resolver caches the answer for the duration of the record's **TTL (Time To Live)** and returns it to the client.

### 4. Visual Explanation
```
[Client] ──(1. Recursive Query)──> [Recursive Resolver]
                                          │
       ┌──────────────────────────────────┼──────────────────────────────────┐
       │ (2. Where is .com?)              │ (4. Where is example.com?)       │ (6. What is app.example.com?)
       ▼                                  ▼                                  ▼
[Root Server (. )]             [TLD Server (.com)]          [Authoritative Server]
 (3. Refer to .com TLD)         (5. Refer to Auth NS)         (7. IP: 198.51.100.25!)
```

### 5. Command Examples
Perform step-by-step query tracing with `dig`:
```bash
# Trace the full resolution path from root to authoritative server
dig +trace app.example.com
```

### 6. Cybersecurity Relevance (Defensive Perspective)
* **DNS Sinkholing**: Enterprise security teams configure resolvers to intercept lookups for known malicious domains and return an internal honeypot/sinkhole IP, neutralizing malware command & control.
* **DNS over HTTPS (DoH) / DNS over TLS (DoT)**: Encrypts queries between client and resolver, preventing local Wi-Fi eavesdroppers from observing visited domains.
* **Fast-Flux Botnets**: Cybercriminals rapidly change DNS `A` records every few minutes with very low TTLs (e.g., 60 seconds) pointing to thousands of compromised consumer computers to make takedowns impossible.

### 7. Common Troubleshooting Mistakes
* Ignoring TTL during DNS migrations: Lower the TTL to 300 seconds (5 minutes) a few days *before* migrating a server to a new IP so client resolvers flush their caches rapidly.

### 8. Quick Revision
* Client -> Recursive Resolver -> Root (`.`) -> TLD -> Authoritative Server.
* Recursive query = "Give me the answer"; Iterative query = "Give me the next hop".
* Records are cached based on TTL.
* Key defense: DNS Sinkholing and Protective DNS (PDNS).

### 9. Interview Check
**Q: What is DNS Cache Poisoning, and how does DNSSEC prevent it?**  
**A:** DNS Cache Poisoning occurs when an attacker injects forged responses into a recursive resolver's cache, redirecting legitimate users to phishing sites. **DNSSEC (DNS Security Extensions)** prevents this by adding cryptographic digital signatures to DNS records, allowing resolvers to cryptographically verify that the answer came from the genuine authoritative nameserver and was not altered in transit.
""",
    },
    # 21. DHCP Process
    {
        "topic_slug": "dhcp-process",
        "title": "DHCP DORA Handshake & Relay Agents",
        "slug": "dhcp-dora-handshake-relay",
        "description": "Deep packet analysis of DORA, DHCP options, lease renewals, and IP helper relay across routers.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 30,
        "content": """# DHCP DORA Handshake & Relay Agents

### 1. What is it? (Simple Explanation)
We learned that DHCP automatically assigns IP addresses via the DORA handshake. But what happens in a large university or enterprise with 50 different buildings and 100 separate subnets? Do you have to buy 100 physical DHCP servers—one for every single room?

No! You use a **DHCP Relay Agent** (often called an IP Helper). The local router catches the client's local broadcast, converts it into a direct unicast message, and forwards it across the network to a single centralized corporate DHCP server.

### 2. Technical Explanation
DHCP operates over UDP using Port 67 (Server) and Port 68 (Client).
* Because a new client has no IP address, it sends its initial **DHCPDISCOVER** using:
  * `Source IP`: `0.0.0.0`
  * `Destination IP`: `255.255.255.255` (Limited Broadcast)
  * `Source MAC`: Client's hardware MAC
  * `Destination MAC`: `FF:FF:FF:FF:FF:FF`
  * Embedded inside the payload is the client's Transaction ID (`xid`) to match replies.

### 3. The Role of DHCP Relay (IP Helper)
Routers do not forward Layer 2 broadcasts by default. When a DHCP broadcast arrives at a router interface configured with a relay agent:
1. The router intercepts the broadcast packet.
2. The router adds its own interface IP into the **GIADDR (Gateway IP Address)** field of the DHCP header.
3. The router converts the packet into a unicast UDP packet routed directly to the centralized DHCP server IP.
4. The DHCP server uses the `GIADDR` field to determine *which specific subnet pool* to allocate the IP from!

### 4. DHCP Lease Lifecycle & Timers
* **T1 Timer (50% Lease Duration)**: The client attempts a **unicast** `DHCPREQUEST` to the original server to renew its lease.
* **T2 Timer (87.5% Lease Duration)**: If the original server failed to respond, the client broadcasts a `DHCPREQUEST` to *any* available DHCP server on the network.
* **Lease Expiration (100%)**: If no server acknowledges renewal, the client immediately drops the IP and reverts to the Discover phase.

### 5. Visual Explanation: DHCP Relay
```
[Client Subnet: 10.0.1.0/24]                      [Central Data Center]
Client [0.0.0.0]        Router (Relay Agent)      DHCP Server [10.50.0.10]
      │                          │                          │
      ├─ DHCPDISCOVER (Bcast) ──>│                          │
      │   (255.255.255.255)      ├─ DHCPDISCOVER (Unicast) >│ (GIADDR = 10.0.1.1)
      │                          │<── DHCPOFFER (Unicast) ──┤ (Offers 10.0.1.50)
      │<─ DHCPOFFER (To Client) ─┤                          │
```

### 6. Command Examples
Verify DHCP lease status and parameters:
```powershell
# Windows PowerShell: View detailed DHCP lease and server information
Get-NetIPConfiguration | Format-List IPv4Address, IPv4DefaultGateway, DNSServer
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **DHCP Starvation (Denial of Service)**: Attackers flood the network with thousands of DISCOVER requests using spoofed MACs to deplete the IP pool.
* **DHCP Snooping Mitigation**: Enterprise switches maintain a dynamic **DHCP Snooping Binding Table** tracking MAC, IP, Lease Time, and Port. Ports connected to users are designated **Untrusted**; only switches/routers on **Trusted** ports are permitted to send DHCPOFFER and DHCPACK packets.

### 8. Common Troubleshooting Mistakes
* Forgetting the Relay Agent: Creating a new VLAN on a switch without configuring `ip helper-address <DHCP-Server-IP>` on the Layer 3 router interface will leave all clients on that VLAN stranded without an IP address.

### 9. Quick Revision
* Handshake = Discover -> Offer -> Request -> Acknowledge.
* Client broadcast = Source 0.0.0.0, Dest 255.255.255.255.
* DHCP Relay (IP Helper) forwards broadcasts as unicast across routers.
* Protect against rogue servers using **DHCP Snooping**.

### 10. Interview Check
**Q: How does a centralized DHCP server know which IP subnet to lease an address from when requests arrive via a DHCP Relay Agent?**  
**A:** When the relay agent (router) forwards the broadcast as a unicast packet, it inserts its own local interface IP into the **GIADDR (Gateway IP Address)** field of the DHCP header. The DHCP server inspects the GIADDR field and selects an available address from the pool configured for that specific subnet.
""",
    },
    # 22. Routing
    {
        "topic_slug": "routing",
        "title": "IP Routing Fundamentals & Longest Prefix Match",
        "slug": "ip-routing-longest-prefix-match",
        "description": "Layer 3 packet forwarding, routing table lookups, administrative distance, and static vs dynamic routes.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 35,
        "content": """# IP Routing Fundamentals & Longest Prefix Match

### 1. What is it? (Simple Explanation)
Imagine you arrive at a major highway interchange in a car. Overhead signs point in different directions: "Highway 95 North to Boston", "Highway 95 South to Miami", and "Local Exit 12". You consult your GPS map, check your destination city, and steer into the exact lane that moves you one step closer to your final destination.

A **router** is the digital highway navigator. Its sole job is to receive IP packets, consult its internal **Routing Table**, determine the best exit interface, and forward the packet toward the next hop.

### 2. Technical Explanation
Routing is Layer 3 packet forwarding based on destination IP addresses:
1. **Routing Table**: A database maintained in router memory listing destination network prefixes, next-hop IP addresses, exit interfaces, and administrative metrics.
2. **Longest Prefix Match (LPM)**: When a packet matches multiple routes in the routing table, the router **always** selects the route with the most specific mask (longest prefix).

### 3. Administrative Distance (AD)
When a router learns about the same destination network from multiple different sources, it uses **Administrative Distance** (a trustworthiness score from 0 to 255; lower is better) to choose which route installs into the routing table:
* **Directly Connected Interface**: AD = `0`
* **Static Route**: AD = `1`
* **BGP (External)**: AD = `20`
* **OSPF**: AD = `110`
* **RIP**: AD = `120`

### 4. Step-by-Step Longest Prefix Match Example
A router receives a packet destined for `10.1.2.55`.
Its routing table contains:
* Route A: `10.0.0.0/8` via Interface 1 (Matches first 8 bits)
* Route B: `10.1.0.0/16` via Interface 2 (Matches first 16 bits)
* Route C: `10.1.2.0/24` via Interface 3 (Matches first 24 bits)
* Route D: `0.0.0.0/0` via Interface 4 (Default route, matches 0 bits)

**Decision**: The router forwards the packet out **Interface 3** because `/24` is the longest (most specific) prefix match!

### 5. Visual Explanation: Router Forwarding Cycle
```
Incoming Packet [Dest: 10.1.2.55]
              │
              ▼
   [Strip Layer 2 Frame Header]
              │
              ▼
   [Inspect Destination IP: 10.1.2.55]
              │
              ▼
   [Consult Routing Table (LPM)]
   Matches: 10.1.2.0/24 -> Next Hop 192.168.10.2 on eth1
              │
              ▼
   [Decrement TTL (TTL = TTL - 1)]
   (If TTL == 0, drop and send ICMP Time Exceeded)
              │
              ▼
   [Re-encapsulate with new Layer 2 MACs and transmit on eth1]
```

### 6. Command Examples
View your operating system's routing table:
```powershell
# Windows: Display active IPv4 routes
route print -4
```
```bash
# Linux: Modern kernel routing table inspection
ip route show
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **BGP Route Hijacking**: Threat actors announce illegitimate prefixes to upstream Tier-1 ISPs. Global routers prioritize the rogue announcement (especially if more specific), rerouting sensitive traffic through hostile nation-state infrastructure before passing it along.
* **Routing Loop DoS**: Misconfigured routing tables can bounce packets back and forth between two routers indefinitely until the TTL reaches zero, exhausting router interface bandwidth.

### 8. Common Troubleshooting Mistakes
* Asymmetric Routing: Traffic leaves via Firewall A but returns via Router B. If Firewall A is stateful, outbound sessions will never see returning ACK packets, breaking TCP connections.
* Gateway of Last Resort: Forgetting to configure a default route (`0.0.0.0/0`) means the router will drop all packets destined for addresses not explicitly defined in its table.

### 9. Quick Revision
* Routers forward packets based on destination IP.
* Selection rule: **Longest Prefix Match (most specific mask wins)**.
* Tiebreaker between routing protocols: **Administrative Distance (lower is better)**.
* Decrements TTL by 1 at every hop.

### 10. Interview Check
**Q: What happens when a router receives an IP packet whose destination IP matches no specific route in its routing table?**  
**A:** If a Default Route (`0.0.0.0/0`, Gateway of Last Resort) is configured, the router forwards the packet out the default gateway interface. If no default route exists, the router drops the packet and sends an **ICMP Type 3, Code 0 (Destination Network Unreachable)** message back to the sending host.
""",
    },
    # 23. Switching
    {
        "topic_slug": "switching",
        "title": "Ethernet Switching & MAC Address Tables",
        "slug": "ethernet-switching-mac-tables",
        "description": "Layer 2 frame forwarding, transparent bridging, CAM tables, and MAC flooding attacks.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 30,
        "content": """# Ethernet Switching & MAC Address Tables

### 1. What is it? (Simple Explanation)
Imagine an office receptionist who sits at a switchboard. When a courier drops off an envelope, the receptionist looks at the recipient's name, checks their internal employee directory desk chart, and walks the envelope directly to that person's desk.

A **network switch** does this for millions of Ethernet frames per second. It observes incoming network traffic, builds a real-time directory of which computer's MAC address is plugged into which physical port, and sends frames directly to the intended recipient.

### 2. Technical Explanation
A Layer 2 switch operates as a high-speed transparent multi-port bridge governed by three core rules:
1. **Learning**: Inspects the **Source MAC** address of every incoming frame and records `(Source MAC, Port, Timestamp)` into its **CAM (Content Addressable Memory) Table**.
2. **Forwarding (Filtering)**: Inspects the **Destination MAC**. If the destination MAC is already known in the CAM table, the switch forwards the frame exclusively out that specific port.
3. **Flooding**: If the Destination MAC is unknown (Unknown Unicast) or is the Broadcast MAC (`FF:FF:FF:FF:FF:FF`), the switch floods the frame out of **every port** except the port on which it arrived.

### 3. Aging Timers
To ensure switches adapt when laptops are unplugged or moved to different desks, CAM table entries have an **Aging Timer** (typically 300 seconds / 5 minutes). If no frames arrive from that MAC address within 5 minutes, the entry is quietly flushed.

### 4. Visual Explanation: The 3 Rules in Action
```
Switch CAM Table:
[ 00:AA:BB:11:22:33 -> Port 1 ]
[ 00:AA:BB:44:55:66 -> Port 3 ]

Scenario 1: Frame arrives on Port 1 for 00:AA:BB:44:55:66
--> Switch checks CAM table: Found on Port 3!
--> FORWARDS frame directly to Port 3 ONLY.

Scenario 2: Frame arrives on Port 1 for 00:AA:BB:99:99:99 (Unknown)
--> Switch checks CAM table: NOT FOUND!
--> FLOODS frame out Port 2, Port 3, Port 4... (All except Port 1).
```

### 5. Command Examples
Inspect the MAC address table on a network switch (Cisco IOS syntax):
```text
Switch# show mac address-table dynamic
          Mac Address Table
-------------------------------------------
Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    001a.2b3c.4d5e    DYNAMIC     Gi0/1
   1    0050.56a1.2233    DYNAMIC     Gi0/2
```

### 6. Cybersecurity Relevance (Defensive Perspective)
* **CAM Table Overflow (MAC Flooding Attack)**: A switch's CAM table has finite memory (e.g., 8,000 to 128,000 entries). An attacker uses tools like `macof` to flood the switch with millions of fake, randomized MAC addresses. When the table fills up, the switch can no longer learn new addresses and **fails open**—behaving like a hub and broadcasting all private traffic across every port!
* **Port Security Mitigation**: Network engineers configure switch ports to limit the maximum number of MAC addresses allowed per port (e.g., `switchport port-security maximum 1`) and set the violation action to `shutdown`.

### 7. Common Troubleshooting Mistakes
* Switching Loops: Connecting two switches with two cables without Spanning Tree Protocol (STP) enabled will cause broadcast frames to loop forever, generating a **Broadcast Storm** that exhausts switch CPUs and brings down the entire network in seconds.

### 8. Quick Revision
* Switches operate at Layer 2 using MAC addresses.
* Learns on Source MAC; Forwards or Floods on Destination MAC.
* CAM table stores mappings; entries age out after 300 seconds.
* Mitigate MAC flooding using switch **Port Security**.

### 9. Interview Check
**Q: What is 'Unknown Unicast Flooding', and why is it necessary for switch operation?**  
**A:** Unknown Unicast Flooding occurs when a switch receives a unicast frame destined for a MAC address that is not currently present in its CAM table. The switch must flood the frame out of all ports (except the ingress port) so that the destination host receives it and replies, allowing the switch to learn its location without dropping legitimate communication.
""",
    },
    # 24. VLAN
    {
        "topic_slug": "vlan",
        "title": "Virtual Local Area Networks (VLANs) & 802.1Q",
        "slug": "vlans-8021q-trunking",
        "description": "Logical network segmentation, broadcast domain isolation, trunking, and inter-VLAN routing.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 35,
        "content": """# Virtual Local Area Networks (VLANs) & 802.1Q

### 1. What is it? (Simple Explanation)
Imagine you work in a 3-story office building where Finance, HR, and Engineering employees sit intermingled on every floor. You want to make sure Finance computers cannot see HR computers on the network. Without VLANs, you would have to buy separate physical switches and run duplicate physical cables to every desk.

A **VLAN (Virtual Local Area Network)** allows you to divide a single physical switch into multiple isolated virtual switches inside software.

### 2. Technical Explanation
A VLAN is a logically isolated Layer 2 broadcast domain configured on network switches:
* Devices on different VLANs **cannot** communicate directly at Layer 2, even if plugged into adjacent ports on the same physical switch.
* To pass traffic between VLANs, packets must traverse a Layer 3 routing device (**Inter-VLAN Routing**).

### 3. Access Ports vs Trunk Ports
* **Access Port**: Carries traffic for only **one single VLAN**. End-user devices (PCs, printers) plug into access ports. Frames traversing access ports are standard, untagged Ethernet frames.
* **Trunk Port**: Carries traffic for **multiple VLANs simultaneously** across a single physical link connecting two switches or a switch to a router.

### 4. IEEE 802.1Q Frame Tagging
When an Ethernet frame crosses a trunk link, the switch inserts a **4-byte 802.1Q Tag** into the frame header:
* **TPID (Tag Protocol Identifier)**: `0x8100` (identifies 802.1Q).
* **VLAN ID (VID) (12 bits)**: Specifies the VLAN number from `1` to `4094`.
When the frame arrives at the receiving switch, the switch reads the VLAN ID, strips the 4-byte tag, and delivers the clean untagged frame to the correct destination access port.

### 5. Visual Explanation: 802.1Q Trunking
```
Switch A                                                       Switch B
[Port 1: VLAN 10 (Sales)]                                     [Port 1: VLAN 10 (Sales)]
[Port 2: VLAN 20 (HR)]   ─── [Trunk Link: 802.1Q Tagged] ───> [Port 2: VLAN 20 (HR)]
                             [Frame + VLAN ID: 10 Tag]
```

### 6. Command Examples
Cisco switch configuration syntax for creating VLANs and trunks:
```text
Switch(config)# vlan 10
Switch(config-vlan)# name Accounting
Switch(config)# interface GigabitEthernet0/1
Switch(config-if)# switchport mode access
Switch(config-if)# switchport access vlan 10

Switch(config)# interface GigabitEthernet0/24
Switch(config-if)# switchport mode trunk
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **PCI-DSS Compliance & Isolation**: Payment card regulations require isolating Point-of-Sale credit card terminals from general employee internet access. VLANs provide this foundational logical separation.
* **VLAN Hopping Attacks**:
  * **Switch Spoofing**: An attacker connects a rogue laptop running DTP (Dynamic Trunking Protocol) negotiation to trick an unhardened switch into opening a trunk port, granting access to all VLANs.
  * **Double Tagging**: An attacker crafts a packet with two 802.1Q headers (Outer Tag = Native VLAN, Inner Tag = Target Victim VLAN). The first switch strips the outer tag, and the second switch forwards it to the victim VLAN!
  * **Defense**: Always disable DTP (`switchport nonegotiate`), disable unused ports, and change the Native VLAN to an unused ID.

### 8. Common Troubleshooting Mistakes
* Native VLAN Mismatch: If Switch A has Native VLAN 1 and Switch B has Native VLAN 99 on opposite sides of a trunk, frames will leak between different VLANs, generating syslog warnings and security risks.

### 9. Quick Revision
* VLAN = Logical Layer 2 broadcast domain on a switch.
* Access port = Single VLAN (untagged); Trunk port = Multiple VLANs (tagged).
* 802.1Q tag inserts a 12-bit VLAN ID (1-4094).
* Traffic between VLANs requires a Layer 3 router or multilayer switch.

### 10. Interview Check
**Q: What is a 'Router-on-a-Stick', and how does it enable Inter-VLAN routing?**  
**A:** Router-on-a-Stick is an inter-VLAN routing design where a single physical Ethernet interface on a router is connected to a switch trunk port. The physical router interface is partitioned into logical **sub-interfaces** (e.g., `g0/0.10`, `g0/0.20`), each configured with 802.1Q encapsulation and an IP address serving as the default gateway for that respective VLAN.
""",
    },
    # 25. NAT
    {
        "topic_slug": "nat",
        "title": "Network Address Translation (NAT) & PAT",
        "slug": "network-address-translation-pat",
        "description": "Static NAT, Dynamic NAT, Port Address Translation (PAT), and IP preservation.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 30,
        "content": """# Network Address Translation (NAT) & PAT

### 1. What is it? (Simple Explanation)
Imagine an international corporate office with 500 employees. Every employee has their own desk with an internal 3-digit extension number (Private IP). However, the company only pays the telephone company for a single public phone number (Public IP). When an employee makes an outside call, the central company switchboard routes the call out using the main corporate number, keeping track of who dialed whom.

**Network Address Translation (NAT)** is this exact mechanism for IP networks. It allows hundreds of computers using private IP addresses to share a single public IP address on the Internet.

### 2. Technical Explanation
Standardized in RFC 1631 and RFC 3022, NAT modifies IP address information in packet headers while in transit across a traffic routing device.

Three primary types of NAT:
1. **Static NAT**: One-to-one permanent mapping of an internal private IP to an external public IP (commonly used for public web servers).
2. **Dynamic NAT**: Many-to-many mapping from a pool of registered public IP addresses on a first-come, first-served basis.
3. **Port Address Translation (PAT / NAT Overload)**: Many-to-one mapping where thousands of private internal hosts share a single public IP by multiplexing unique Layer 4 source port numbers.

### 3. The PAT Translation Table
When Host A (`10.0.1.50:51234`) requests a webpage from Google:
1. The packet hits the perimeter router.
2. The router rewrites the source IP to its public IP `203.0.113.1` and allocates a unique public source port `61001`.
3. The router logs this mapping in its state table: `10.0.1.50:51234 <-> 203.0.113.1:61001`.
4. When Google replies to `203.0.113.1:61001`, the router consults the table, translates the destination back to `10.0.1.50:51234`, and forwards it to Host A.

### 4. Visual Explanation: PAT Operation
```
Internal Private Network                  NAT Gateway                 Public Internet
[PC 1: 10.0.1.10:5001] ──┐             (Public IP: 203.0.113.1)       [Web Server: 142.250.190.46]
                         ├──> [ Router NAT Table ] ───────────────>
[PC 2: 10.0.1.20:5001] ──┘    10.0.1.10:5001 <-> 203.0.113.1:40001
                              10.0.1.20:5001 <-> 203.0.113.1:40002
```

### 5. Command Examples
Check your current public IP vs your local private IP:
```powershell
# Windows: Local private IP
(Get-NetIPAddress -InterfaceAlias "Wi-Fi" -AddressFamily IPv4).IPAddress

# Query public IP as seen by the outside world through NAT
(Invoke-RestMethod -Uri "https://api.ipify.org")
```

### 6. Cybersecurity Relevance (Defensive Perspective)
* **Inherent Perimeter Shielding**: By default, PAT only translates outbound connections. Unsolicited inbound connection attempts from the public internet cannot reach internal private IPs because no state translation entry exists, shielding internal desktops from direct external port scans.
* **Forensic Attribution Challenges**: For SOC analysts and digital investigators, NAT complicates attribution. If an abuse report arrives stating that `203.0.113.1` attacked a bank, investigators cannot know which internal employee was responsible unless the firewall's **NAT translation logs** are preserved with precise timestamps.

### 7. Common Troubleshooting Mistakes
* Double NAT: Connecting a personal Wi-Fi router to an ISP modem that is also performing NAT creates two layers of translation, causing severe issues for VoIP protocols, VPN tunnels, and peer-to-peer applications.

### 8. Quick Revision
* NAT maps private RFC 1918 IPs to public routable IPs.
* PAT (NAT Overload) tracks connections using unique source port numbers.
* Extensively delayed IPv4 exhaustion.
* Essential for perimeter security, but requires NAT logging for forensics.

### 9. Interview Check
**Q: What is the difference between Static NAT and Port Address Translation (PAT)?**  
**A:** Static NAT provides a permanent one-to-one mapping between an internal private IP and an external public IP, allowing external clients to initiate inbound connections to internal servers. PAT (NAT Overload) maps multiple private IP addresses to a single public IP by tracking unique source port numbers, allowing thousands of internal clients to share one public IP for outbound sessions.
""",
    },
    # 26. Network Troubleshooting
    {
        "topic_slug": "ping",
        "title": "Network Troubleshooting Commands & Methodology",
        "slug": "network-troubleshooting-commands-methodology",
        "description": "Systematic diagnostic workflow using ping, traceroute, netstat, arp, and nslookup.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 30,
        "content": """# Network Troubleshooting Commands & Methodology

### 1. What is it? (Simple Explanation)
When your home Wi-Fi stops working, panicking and randomly unplugging every cable rarely fixes the issue. A professional network engineer acts like a skilled doctor: observing symptoms, formulating a hypothesis, and testing one specific layer at a time in a disciplined diagnostic sequence.

This lesson covers the core CLI diagnostic toolkit—`ipconfig`, `ping`, `traceroute`, `arp`, and `netstat`—and the standard **Bottom-Up Troubleshooting Methodology**.

### 2. The 7-Step Bottom-Up Troubleshooting Sequence
When a user reports: *"I cannot open the company intranet website!"*
1. **Step 1: Check Local Interface (Layer 1 & 2)**
   * Is the cable plugged in? Are link lights solid green?
   * Command: `ipconfig` (Windows) / `ip link` (Linux)
   * Verify host has a valid IP address and not an APIPA address (`169.254.x.x`).
2. **Step 2: Ping Loopback (TCP/IP Stack Integrity)**
   * Command: `ping 127.0.0.1`
   * Proves the local operating system network drivers and TCP/IP stack are functioning.
3. **Step 3: Ping Local Default Gateway (LAN Connectivity)**
   * Command: `ping 192.168.1.1`
   * Proves the local switch, cable, and router interface are communicating.
4. **Step 4: Ping External Public IP (WAN / ISP Routing)**
   * Command: `ping 8.8.8.8` or `ping 1.1.1.1`
   * Proves routing across the internet is functional and the ISP link is up.
5. **Step 5: Test DNS Resolution (Layer 7)**
   * Command: `nslookup intranet.corp.internal`
   * If Step 4 works (pinging `8.8.8.8` succeeds) but browsing by name fails, DNS is the root cause!
6. **Step 6: Test Transport Port Reachability (Layer 4)**
   * Command: `Test-NetConnection intranet.corp.internal -Port 443`
   * Proves the server process is listening and firewalls permit traffic.
7. **Step 7: Check Application Response (Layer 7)**
   * Command: `curl -I https://intranet.corp.internal`
   * Check for HTTP error codes (e.g., 500 Internal Server Error).

### 3. Diagnostic Command Quick Reference
| Tool | Layer | Primary Diagnostic Function |
| :--- | :--- | :--- |
| `ping` | Layer 3 | Tests reachability and latency via ICMP Echo Request/Reply. |
| `traceroute` (`tracert`) | Layer 3 | Identifies hop-by-hop router paths and pinpoint where packet loss occurs. |
| `arp -a` | Layer 2 | Inspects resolved IP-to-MAC hardware bindings on the local subnet. |
| `netstat` / `ss` | Layer 4 | Lists active TCP connections, listening ports, and socket states. |
| `nslookup` / `dig` | Layer 7 | Interrogates DNS servers directly to test name-to-IP resolution. |

### 4. Visual Explanation: Diagnostic Ladder
```
[Step 5: DNS]               nslookup google.com   ──> Fails? DNS Problem!
     ▲
[Step 4: Internet Router]   ping 8.8.8.8          ──> Fails? ISP / Gateway Routing Problem!
     ▲
[Step 3: Default Gateway]   ping 192.168.1.1      ──> Fails? Local Switch / Cable Problem!
     ▲
[Step 2: Loopback]          ping 127.0.0.1        ──> Fails? OS Protocol Stack Corrupted!
     ▲
[Step 1: Physical Link]     ipconfig / ip link    ──> Fails? Cable Unplugged / No IP!
```

### 5. Command Examples
Execute a multi-stage diagnostic script:
```powershell
# Windows PowerShell diagnostic sequence
Write-Host "1. Testing Gateway..." -ForegroundColor Cyan
Test-Connection 192.168.1.1 -Count 2

Write-Host "2. Testing DNS..." -ForegroundColor Cyan
Resolve-DnsName google.com

Write-Host "3. Testing Web Port 443..." -ForegroundColor Cyan
Test-NetConnection google.com -Port 443
```

### 6. Cybersecurity Relevance (Defensive Perspective)
* **Incident Containment Verification**: When isolating an infected workstation from the network, security analysts verify containment by confirming the host fails to ping internal subnets while retaining visibility to the EDR sensor.
* **Malicious Connection Hunting**: Running `netstat -ano` on a compromised server allows analysts to identify outbound TCP connections established to unknown foreign IP addresses and pinpoint the malicious executable via its Process ID (PID).

### 7. Common Troubleshooting Mistakes
* Testing with domain names first: Always test with numerical IP addresses (`8.8.8.8`) before domain names (`google.com`) so you don't confuse a simple DNS resolution failure with total network disconnectivity.

### 8. Quick Revision
* Follow disciplined Bottom-Up methodology: Link -> Loopback -> Gateway -> Internet -> DNS -> Application.
* `ping` = reachability; `traceroute` = hop-by-hop path latency; `netstat` = open ports.
* Always isolate DNS issues from IP connectivity issues.

### 9. Interview Check
**Q: A user can reach external websites by typing their IP address into a browser, but typing the domain name fails with 'Server Not Found'. What is the root cause and how do you verify it?**  
**A:** The root cause is a **DNS resolution failure**; Layer 1 through Layer 3 connectivity is fully operational since numerical IPs load properly. You verify this by running `nslookup <domain>` to check if the configured DNS server is reachable and responding, and by checking the client's DNS server configuration in `ipconfig /all`.
""",
    },
    # 27. Firewalls
    {
        "topic_slug": "firewall-rules",
        "title": "Firewall Rule Architecture & Traffic Filtering",
        "slug": "firewall-rule-architecture-filtering",
        "description": "5-tuple rulebases, stateful connection tracking, rule ordering, and security zone segmentation.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 35,
        "content": """# Firewall Rule Architecture & Traffic Filtering

### 1. What is it? (Simple Explanation)
Imagine an apartment building with an intercom and an electronic security gate. The landlord programs rules: "Delivery drivers may enter between 9 AM and 5 PM; residents may enter anytime; unauthorized solicitors are permanently denied."

In an enterprise network, **firewall rules** are the programmed security instructions that determine which packets are permitted to pass between network zones and which are immediately dropped.

### 2. Technical Explanation
Enterprise firewalls evaluate traffic against an ordered sequence of access control rules known as an **Access Control List (ACL)** or **Rulebase**.

Every packet is evaluated against the classic **5-Tuple**:
1. **Source IP Address** (or subnet / network object)
2. **Destination IP Address** (or subnet / network object)
3. **Protocol** (TCP, UDP, ICMP)
4. **Source Port** (Typically wildcard/any for clients)
5. **Destination Port** (Well-known service port, e.g., 443, 22)
6. **Action**: `PERMIT` (Allow), `DENY` (Silently Drop), or `REJECT` (Drop and send ICMP unreachable).

### 3. Critical Rulebase Design Principles
1. **First Match Wins**: The firewall evaluates rules from top to bottom (Rule 1, Rule 2, Rule 3...). As soon as a packet matches a rule's criteria, the action is taken and evaluation stops immediately!
2. **Specific Rules Above Generic Rules**: Place strict, specific rules (e.g., "Allow Host A to Server B on Port 22") at the top; broad rules (e.g., "Allow Subnet to Internet") go below.
3. **Implicit Deny All**: The final rule must always be `DENY ALL ANY ANY`.

### 4. Real-World Zone-Based Firewall Policy
Enterprise firewalls divide networks into **Security Zones**:
* **Untrusted (WAN / Internet)**: Lowest trust level.
* **DMZ (Demilitarized Zone)**: Medium trust; holds public-facing web servers.
* **Trusted (LAN / Internal)**: High trust; employee workstations.
* **Restricted (Database / Core)**: Maximum trust; financial databases, domain controllers.

Traffic Rules Matrix:
* Internal LAN -> DMZ: **Permitted** on Port 443.
* Internet -> DMZ: **Permitted** on Port 443 only.
* DMZ -> Internal Database: **Permitted** on Port 3306 only.
* DMZ -> Internal LAN: **DENIED**. (If the web server is hacked, it cannot attack workstations!).

### 5. Visual Explanation: Zone-Based Architecture
```
[Untrusted Internet]
        │
        ▼ (Port 443 Only)
  [Firewall Perimeter]
        │
        ├──────────────────────┐
        ▼                      ▼
  [DMZ Zone]             [Internal LAN Zone]
  (Public Web Server)    (Staff Workstations)
        │                      │
        │ (Port 3306 Only)     │ (Blocked!)
        ▼                      ▼
  [Restricted Zone: Database Server]
```

### 6. Command Examples
Configuring a stateful firewall rule using Linux `iptables`:
```bash
# Allow established returning traffic (Stateful SPI)
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# Allow inbound HTTPS to local web server
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# Default policy: Drop everything else
iptables -P INPUT DROP
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **Shadow Rules**: A misconfiguration where an overly broad rule placed higher in the rulebase inadvertently matches traffic intended for a stricter rule below it, rendering the security rule dead and ineffective.
* **Egress Data Exfiltration Defense**: Attackers who compromise internal systems attempt to establish outbound reverse shells over unusual ports (like Port 4444 or 1337). Enforcing strict outbound egress filtering prevents reverse shells from connecting back to the attacker's infrastructure.

### 8. Common Troubleshooting Mistakes
* Placing a `DENY` rule above an `ALLOW` rule: If Rule 5 denies all traffic from Subnet 10.0.1.0/24, adding Rule 6 to allow Port 80 for Host 10.0.1.50 will fail because the firewall stops at Rule 5!

### 9. Quick Revision
* Firewalls evaluate the 5-Tuple: Source IP, Dest IP, Protocol, Source Port, Dest Port.
* Processing order: **Top to bottom, first match wins**.
* Always terminate with **Implicit Deny**.
* Segment into security zones (LAN, DMZ, WAN, Restricted).

### 10. Interview Check
**Q: What is the difference between a firewall DROP action and a REJECT action, and which is preferred on external perimeter interfaces?**  
**A:** `DROP` silently discards the packet without sending any response back to the sender. `REJECT` discards the packet and sends an active error response (like a TCP RST or ICMP Port Unreachable). On external internet-facing perimeters, `DROP` is strongly preferred because it forces attacker port scanners to wait for connection timeouts, significantly slowing down reconnaissance and revealing zero information about firewall existence.
""",
    },
    # 28. IDS/IPS
    {
        "topic_slug": "ids",
        "title": "Intrusion Detection & Prevention Systems (IDS/IPS)",
        "slug": "intrusion-detection-prevention-systems",
        "description": "Signature vs anomaly detection, in-line IPS vs out-of-band IDS, and Snort rule mechanics.",
        "content_type": ContentType.LESSON,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "estimated_minutes": 35,
        "content": """# Intrusion Detection & Prevention Systems (IDS/IPS)

### 1. What is it? (Simple Explanation)
A standard network firewall is like a locked front door: it checks who you are and permits or denies entry based on your badge (IP and Port). But what if an authorized visitor walks through the front door, pulls a spray can out of their backpack, and begins vandalizing the walls? The door lock cannot stop them because they were allowed in legally.

An **Intrusion Detection System (IDS)** is the security camera and burglar alarm that watches what visitors actually *do* inside. An **Intrusion Prevention System (IPS)** is an armed security guard standing directly in the hallway who actively tackles the vandal the instant they pull out the spray can.

### 2. Technical Explanation
* **IDS (Intrusion Detection System)**: Deployed **out-of-band** (passively). It receives a mirrored copy of network traffic via a switch SPAN port or physical network TAP. It analyzes packets and generates alerts for SOC analysts without impacting traffic flow.
* **IPS (Intrusion Prevention System)**: Deployed **in-line** directly in the physical traffic path. Packets physically pass through the IPS engine before reaching their destination. It can actively drop malicious packets, terminate TCP connections with RST flags, or reconfigure firewalls in real-time.

### 3. Detection Methodologies
1. **Signature-Based Detection**: Compares traffic against a database of known exploit patterns, byte sequences, or regular expressions (e.g., matching a known Metasploit buffer overflow payload). Fast and accurate, but blind to brand-new zero-day attacks.
2. **Anomaly / Behavioral Detection**: Establishes a baseline of normal network activity (e.g., "This server usually handles 50 DNS queries per minute"). Alerts when deviations occur (e.g., "Server suddenly sent 10,000 DNS queries in 10 seconds"). Detects zero-days, but prone to false positives.

### 4. Anatomy of an IDS Rule (Snort / Suricata Syntax)
```text
alert tcp any any -> 192.168.1.0/24 80 (msg:"ATTACK-RESPONSES /etc/passwd in HTTP response"; content:"root:x:0:0:"; sid:1000001; rev:1;)
```
* **Action**: `alert` (or `drop` in IPS mode)
* **Protocol & Direction**: `tcp` from `any` source to internal subnet `192.168.1.0/24` on port `80`
* **Rule Options**:
  * `msg`: Human-readable alert name displayed in SIEM.
  * `content`: Exact malicious byte pattern to match inside the payload (`root:x:0:0:`).
  * `sid`: Snort Rule ID unique integer.

### 5. Visual Explanation: Out-of-Band IDS vs In-Line IPS
```
IDS (Passive / Out-of-Band):
[Internet] ─── [Switch] ───────────────────────────> [Internal Servers]
                  │ (SPAN / Mirror Port)
                  ▼
            [IDS Sensor] ──> [Alert Generated in SOC Console]

IPS (Active / In-Line):
[Internet] ───> [In-Line IPS Sensor] ───(Clean Traffic)───> [Internal Servers]
                     │
              (Malicious packet dropped instantly!)
```

### 6. Command Examples
Inspecting alert output from an open-source IDS sensor:
```bash
# View real-time alert logs from Suricata / Snort
tail -f /var/log/suricata/fast.log
```

### 7. Cybersecurity Relevance (Defensive Perspective)
* **False Positives vs False Negatives**:
  * **False Positive**: Harmless benign traffic flagged as an attack (causes alert fatigue for SOC analysts).
  * **False Negative**: A genuine attack slips past undetected (dangerous security breach!).
* **Inline Latency & Failure Modes**: Because an IPS sits in-line, any engine crash or processing slowdown creates a network bottleneck. Enterprise IPS appliances include hardware "fail-open" bypass relays that pass traffic uninterrupted if the appliance loses power.

### 8. Common Troubleshooting Mistakes
* Deploying an IPS in "Blocking" mode on Day 1: New IDS/IPS installations should run in **Detection / Audit Mode** for several weeks to benchmark traffic, identify benign internal quirks, and tune rules before switching to active blocking mode, preventing unintended outages.

### 9. Quick Revision
* IDS = Passive, out-of-band, alerts only.
* IPS = Active, in-line, blocks malicious packets in real-time.
* Signature-based = matches known patterns; Anomaly-based = detects deviations from baseline.
* Essential component of network defense-in-depth.

### 10. Interview Check
**Q: What is the primary operational trade-off between deploying an IDS out-of-band versus deploying an IPS in-line?**  
**A:** An out-of-band IDS introduces zero network latency and cannot cause a network outage if it fails, but it cannot actively prevent an attack from reaching the victim before an alert is reviewed. An in-line IPS can actively block attacks in real-time, but it introduces minor packet processing latency and represents a potential single point of failure that could disrupt legitimate network traffic if it malfunctions or triggers a false positive.
""",
    },
]
