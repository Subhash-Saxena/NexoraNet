# NexoraNet Interactive Network Simulator

> **Tagline:** Learn. Simulate. Analyze. Defend.  
> **Philosophy:** LEARN → DO → OBSERVE → EXPLAIN → VALIDATE → PRACTICE → TEST → DEFEND

The **NexoraNet Interactive Network Simulator** is a virtual, browser-based network canvas and authoritative educational simulation engine. It allows networking beginners and cybersecurity students to visually construct network topologies, connect devices, configure Layer 2 and Layer 3 interfaces, observe packet transmission hop-by-hop across the OSI stack, and solve guided networking challenges.

---

## 1. High-Level Architecture

The simulator follows a strictly decoupled client-server architecture:

```text
┌────────────────────────────────────────────────────────┐
│                   React + TypeScript UI                │
│ ┌──────────────┐ ┌───────────────────┐ ┌─────────────┐ │
│ │DevicePalette │ │   NetworkCanvas   │ │Properties   │ │
│ └──────────────┘ └───────────────────┘ └─────────────┘ │
│ ┌──────────────┐ ┌───────────────────┐ ┌─────────────┐ │
│ │PacketInspect │ │   EventTimeline   │ │ScenarioDraw │ │
│ └──────────────┘ └───────────────────┘ └─────────────┘ │
└───────────────────────────┬────────────────────────────┘
                            │ REST API (JSON)
                            ▼
┌────────────────────────────────────────────────────────┐
│                 FastAPI Simulator Engine               │
│ ┌────────────────────────┐  ┌────────────────────────┐ │
│ │   Simulation Engine    │  │  Scenario Validator    │ │
│ │ (Switch, Route, ACLs)  │  │  (Objective Evaluator) │ │
│ └────────────────────────┘  └────────────────────────┘ │
│ ┌────────────────────────┐  ┌────────────────────────┐ │
│ │  Topology Repository   │  │  Catalog / Prebuilts   │ │
│ └────────────────────────┘  └────────────────────────┘ │
└───────────────────────────┬────────────────────────────┘
                            │ SQLite / PostgreSQL
                            ▼
               [simulator_topologies]
               [simulator_scenarios]
               [simulator_scenario_attempts]
```

### Safety & Virtual Sandbox Boundary
* **No Real Packets Sent**: Zero raw sockets, zero Scapy execution, zero actual network pings.
* **Deterministic Virtual Emulation**: All packet actions, routing decisions, ARP resolution, and firewall drops are evaluated in-memory using deterministic state machines.
* **Educational Transparency**: Every hop and frame transmission produces educational "Why Did This Happen?" explanations linking low-level protocol actions to fundamental networking theory.

---

## 2. Supported Device Types

| Device Type | Layer | Description & Capabilities |
| :--- | :--- | :--- |
| **PC / Laptop** | L3/L7 | Workstation end device with single NIC (`eth0`), configurable IPv4, subnet mask, default gateway, and local ARP cache. |
| **Server** | L3/L7 | Target host hosting services (HTTP port 80, DNS port 53, DHCP port 67). Configurable IP and gateway. |
| **Switch** | L2 | Multi-port (4-port) Layer 2 switch with dynamic MAC address learning table, broadcast domain flooding, and 802.1Q port VLAN tags. |
| **Router** | L3 | Multi-interface gateway router performing Longest Prefix Matching (LPM) routing, TTL decrement, ARP next-hop resolution, and ICMP Time Exceeded generation. |
| **Firewall** | L3/L4 | Perimeter packet filter with stateful/stateless ACL rules (`ALLOW` / `DENY` based on source IP, destination IP, protocol, and port). |
| **Internet Cloud** | L3 | Virtual WAN gateway representing external networks (e.g. `8.8.8.8`). |
| **DNS Server** | L7 | Domain Name System resolver with record map (`A` records) resolving hostnames to IP addresses. |
| **DHCP Server** | L7 | Dynamic Host Configuration Protocol server allocating IPs from a configured pool via virtual DORA exchange. |

---

## 3. Supported Protocols & Simulation Capabilities

1. **ARP (Address Resolution Protocol)**
   - Resolves target IP addresses to Layer 2 MAC addresses.
   - Populates device ARP caches (`configuration.arp_table`).
   - Simulates ARP Request broadcast (`FF:FF:FF:FF:FF:FF`) and ARP Reply unicast.
2. **Layer 2 Ethernet Switching**
   - Learns source MAC addresses and ingress ports dynamically.
   - Forwards frames out the designated port if destination MAC is known.
   - Floods frames out all other ports if destination MAC is unknown or broadcast.
   - Enforces VLAN isolation: frames on VLAN $X$ are never forwarded to ports on VLAN $Y$.
3. **Layer 3 IPv4 Routing**
   - Implements Longest Prefix Match (LPM) route table lookup.
   - Decrements IPv4 TTL (Time-To-Live). Drops packet with `ICMP Time Exceeded (TTL expired)` if TTL reaches 0.
   - Performs default gateway lookup for remote subnets.
4. **Firewall Access Control Lists (ACLs)**
   - Evaluates ordered firewall rules matching protocol (`ICMP`, `TCP`, `UDP`, `ANY`), source CIDR, destination CIDR, and port.
   - Supports explicit `ALLOW` and `DENY` rules with default fallback policy.
5. **ICMP (Ping)**
   - Simulates ICMP Echo Request (`Type 8`) and ICMP Echo Reply (`Type 0`).
   - Verifies round-trip reachability between hosts.
6. **TCP 3-Way Handshake**
   - Simulates `SYN` → `SYN-ACK` → `ACK` connection establishment.
   - Identifies closed ports with `RST` responses.
7. **DNS Resolution**
   - Transmits UDP port 53 DNS Queries.
   - Server looks up `A` records and replies with target IP or NXDOMAIN.
8. **DHCP (Dynamic Host Configuration Protocol)**
   - Simulates 4-way DORA handshake: `Discover` → `Offer` → `Request` → `Acknowledge`.
   - Assigns dynamic IP, netmask, default gateway, and DNS server to client.

---

## 4. User Interface Architecture

The simulator UI consists of synchronized interactive components:

* **NetworkCanvas (`NetworkCanvas.tsx`)**:
  - Interactive SVG canvas with grid background, zoom in/out, and panning.
  - Drag-and-drop node placement and repositioning.
  - Interactive port indicators for cable drawing mode.
  - Glowing pulse animations for active simulated packets in transit.
  - Midpoint deletion badges (`✕`) for removing links.
* **DevicePalette (`DevicePalette.tsx`)**:
  - Left dock categorizing End Devices, Network Devices, and Infrastructure Services.
  - Supports both click-to-add and drag-and-drop to canvas coordinates.
* **DevicePropertiesPanel (`DevicePropertiesPanel.tsx`)**:
  - Contextual inspector panel updating when a node is selected.
  - Tabbed interface: General, Interfaces (IPv4/MAC/VLAN), Routing Table, Firewall Rules, Infrastructure Services.
  - Renders Network Overview summary (total devices, active links, routers, switches) when no device is selected.
* **SimulationControls (`SimulationControls.tsx`)**:
  - Source and destination device selectors.
  - Protocol switcher (`ICMP`, `TCP`, `DNS`, `DHCP`).
  - Prebuilt sample topology loader dropdown.
  - Topology Export / Import JSON functionality.
  - Guided Scenarios toggle button.
* **PacketInspector (`PacketInspector.tsx`)**:
  - 5-Layer OSI stack visualization (Physical, Data Link, Network, Transport, Application).
  - Highlights active protocol layers for the selected packet hop.
  - Protocol header field decapsulation (Ethernet MAC, EtherType, IPv4 source/dest/TTL, L4 ports/flags, ICMP codes).
* **EventTimeline (`EventTimeline.tsx`)**:
  - Chronological event stream recording each network action with severity badges (`INFO`, `SUCCESS`, `WARNING`, `ERROR`).
  - Interactive **"Why Did This Happen?"** buttons displaying pedagogical explanations and cybersecurity relevance.
* **ScenarioDrawer (`ScenarioDrawer.tsx`)**:
  - Slide-over challenge drawer featuring guided missions.
  - Tasks checklist with real-time pass/fail status.
  - Progressive 3-step hint system.
  - Server-authoritative "Check Solution & Score" verification.

---

## 5. API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/simulator/topologies` | Retrieve catalog of prebuilt and saved topologies. |
| `GET` | `/api/v1/simulator/topologies/{id_or_slug}` | Get topology details by ID or slug. |
| `POST` | `/api/v1/simulator/topologies` | Create and save user topology. |
| `PUT` | `/api/v1/simulator/topologies/{id}` | Update existing user topology. |
| `DELETE` | `/api/v1/simulator/topologies/{id}` | Delete user topology. |
| `POST` | `/api/v1/simulator/topologies/validate` | Audit topology for IP conflicts, invalid masks, or missing gateways. |
| `POST` | `/api/v1/simulator/simulate/packet` | Authoritative packet simulation across graph topology. |
| `GET` | `/api/v1/simulator/scenarios` | List all guided learning scenarios. |
| `GET` | `/api/v1/simulator/scenarios/{slug}` | Get scenario definition, initial topology, and hints. |
| `POST` | `/api/v1/simulator/scenarios/{slug}/validate` | Validate user topology against scenario objective rules. |
