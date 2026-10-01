# NexoraNet Simulation Engine Algorithms

The **NexoraNet Simulation Engine** (`backend/app/services/simulation_engine.py`) is an authoritative in-memory network protocol simulator designed for educational rigor, determinism, and safety.

---

## 1. Network Topology Graph Representation

A network topology is modeled as an undirected multigraph $G = (V, E)$:
- **Vertices $V$**: Network devices (`SimDeviceSchema`), each possessing a list of network interfaces (`DeviceInterfaceSchema`), an ARP table, a MAC forwarding table, a routing table, and firewall ACLs.
- **Edges $E$**: Physical cable links (`TopologyLinkSchema`) binding an interface on device $A$ to an interface on device $B$.

---

## 2. Layer 2 Ethernet Switching & Learning Algorithm

When an Ethernet frame arrives on switch port $P_{\text{in}}$ with source MAC $M_{\text{src}}$ and destination MAC $M_{\text{dst}}$:

```text
               ┌────────────────────────┐
               │ Frame Ingress on Port  │
               └───────────┬────────────┘
                           ▼
          ┌──────────────────────────────────┐
          │  Learn Source MAC:               │
          │  MAC_Table[M_src] = (P_in, VLAN) │
          └────────────────┬─────────────────┘
                           ▼
          ┌──────────────────────────────────┐
          │ Destination MAC Broadcast or     │
          │ Unknown in MAC_Table?            │
          └────────┬─────────────────┬───────┘
                YES│                 │NO
                   ▼                 ▼
          ┌─────────────────┐ ┌─────────────────┐
          │ Flood frame out │ │ Forward frame   │
          │ all other ports │ │ ONLY out mapped │
          │ on SAME VLAN    │ │ port P_out      │
          └─────────────────┘ └─────────────────┘
```

1. **MAC Address Learning**:
   The switch inspects the frame header. It updates its MAC table:
   $$\text{MAC\_Table}[M_{\text{src}}] \leftarrow (P_{\text{in}}, \text{VLAN}_{\text{port}})$$
   An educational event is generated explaining how switches build forwarding databases automatically without user intervention.

2. **VLAN Segmentation Check**:
   Before forwarding or flooding, the engine verifies the 802.1Q port membership:
   $$\text{VLAN}(P_{\text{out}}) == \text{VLAN}(P_{\text{in}})$$
   If ports belong to different VLANs and no trunk/router is present, the frame is filtered:
   $$\text{Drop Reason} \leftarrow \text{"VLAN isolation: Port } P_{\text{in}} \text{ (VLAN } A \text{) cannot forward to Port } P_{\text{out}} \text{ (VLAN } B \text{)"}$$

3. **Unicast Forwarding vs Flooding**:
   - If $M_{\text{dst}} == \text{"FF:FF:FF:FF:FF:FF"}$, the frame is flooded to all ports in the ingress VLAN except $P_{\text{in}}$.
   - If $M_{\text{dst}} \in \text{MAC\_Table}$, the frame is forwarded solely to $P_{\text{out}}$.
   - If $M_{\text{dst}} \notin \text{MAC\_Table}$, the frame is flooded (unknown unicast flooding) to discover the host.

---

## 3. Layer 3 Routing & Longest Prefix Match (LPM)

When an IPv4 packet arrives at a Layer 3 Router or multi-homed host:

1. **Destination Address Evaluation**:
   If the packet's destination IP matches one of the router's own interface addresses, the packet is delivered locally to the router's control plane.

2. **TTL Decrement & Loop Protection**:
   The router decrements the IPv4 Time-To-Live:
   $$\text{TTL}_{\text{new}} \leftarrow \text{TTL}_{\text{old}} - 1$$
   If $\text{TTL}_{\text{new}} \le 0$:
   - The packet is dropped immediately.
   - An `ICMP Time Exceeded (Type 11, Code 0)` response is generated back to the source.
   - An event explains how TTL prevents infinite routing loops in looped topologies.

3. **Longest Prefix Matching (LPM)**:
   The routing table contains entries of the form $(\text{Destination Prefix}, \text{Netmask}, \text{Next Hop}, \text{Egress Interface})$.
   For a destination IP $D$:
   $$\text{Match}(D, \text{Prefix}, \text{Netmask}) \iff (D \ \& \ \text{Netmask}) == \text{Prefix}$$
   Among all matching routes, the engine selects the route with the highest prefix length (e.g. `/24` takes precedence over `/16`, which takes precedence over default `/0`).

4. **Next Hop ARP Resolution**:
   - If the route specifies a next-hop gateway (e.g., `10.0.0.1`), the router checks its ARP table for the gateway's MAC.
   - If the next-hop MAC is unknown, an ARP cycle is simulated before transmission.

---

## 4. Firewall Rule Evaluation Engine

Firewall devices evaluate packets sequentially against an ordered list of Access Control List (ACL) rules:

| Rule Attribute | Supported Values |
| :--- | :--- |
| **Action** | `ALLOW` or `DENY` |
| **Protocol** | `ANY`, `ICMP`, `TCP`, `UDP` |
| **Source IP** | IPv4 address or CIDR network (`192.168.1.0/24`, `0.0.0.0/0`) |
| **Destination IP** | IPv4 address or CIDR network |
| **Port** | Target port (`80`, `443`, `22`) or `"ANY"` |

### Evaluation Order:
1. Rules are evaluated from index 0 to $N-1$ (First Match Wins).
2. If a rule matches the packet's headers:
   - If `Action == "DENY"`, the packet is dropped immediately with an explanatory drop reason:
     $$\text{Drop Reason} \leftarrow \text{"Blocked by Firewall Rule #" } + i + \text{ (" } + \text{rule.description} + \text{ ")"}$$
   - If `Action == "ALLOW"`, evaluation stops and forwarding proceeds.
3. Default Policy:
   If no rule matches, the configured default policy (`ALLOW` or `DENY`) is applied.

---

## 5. End-to-End Protocol Handshakes

### A. ICMP Ping Simulation
1. Source generates `ICMP Echo Request (Type 8, Code 0)`.
2. Graph path traversal evaluates Layer 2 switches and Layer 3 routers.
3. Destination validates IP, generates `ICMP Echo Reply (Type 0, Code 0)` reversing source and destination.
4. Total round-trip latency is calculated based on simulated hop count ($0.5\text{ ms}$ per switch, $1.2\text{ ms}$ per router).

### B. TCP 3-Way Handshake
1. **Client $\to$ Server (`SYN`)**:
   Client generates TCP packet with flag `SYN=1`, random client sequence number (e.g., $1000$).
2. **Server $\to$ Client (`SYN-ACK`)**:
   If server port is open, server responds with `SYN=1, ACK=1`, $\text{Ack Number} = 1001$, server sequence number $5000$.
   If server port is closed, server responds with `RST=1, ACK=1` and handshake terminates.
3. **Client $\to$ Server (`ACK`)**:
   Client acknowledges server sequence number with `ACK=1`, $\text{Ack Number} = 5001$. Connection state transitions to `ESTABLISHED`.

### C. DNS Resolution
1. Client generates UDP frame to configured DNS Server on port 53.
2. Server queries internal record database (`configuration.dns_records`).
3. If domain is found (e.g., `www.example.local -> 192.168.1.50`), returns `A` record with IP.
4. If not found, returns `NXDOMAIN` error code.

### D. DHCP DORA Simulation
1. **Discover**: Unconfigured client broadcasts `DHCPDISCOVER` from `0.0.0.0:68` to `255.255.255.255:67`.
2. **Offer**: DHCP Server with configured pool unicasts/broadcasts `DHCPOFFER` with candidate IP (e.g., `192.168.1.100`), mask, gateway, and DNS.
3. **Request**: Client broadcasts `DHCPREQUEST` requesting the offered IP.
4. **Acknowledge**: DHCP Server registers lease in internal table and sends `DHCPACK`.
5. Engine updates client interface with newly acquired IPv4 configuration.

---

## 6. Pedagogical Event Telemetry

Every hop produces a structured `HopRecord` and corresponding `SimulationEvent` with:
- **`explanation`**: Technical description of the operation (e.g., *"Switch learned MAC 02:00:00:00:01:01 on port 1"*).
- **`why_reason`**: Pedagogical rationale answering beginner confusion (e.g., *"Switches learn MAC addresses dynamically from the source address of incoming frames to avoid broadcasting future traffic."*).
- **`cyber_relevance`**: Real-world cybersecurity application (e.g., *"Attackers exploit switch learning via MAC Flooding attacks to overflow CAM tables and turn switches into broadcast hubs for passive eavesdropping."*).
