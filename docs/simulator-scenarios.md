# NexoraNet Simulator Prebuilt Topologies & Scenarios

The **NexoraNet Simulator Catalog** (`backend/app/services/simulator_catalog_service.py`) provides ready-to-load educational network topologies and guided interactive missions.

---

## 1. Prebuilt Topologies Library

Students can instantly load 6 pre-configured reference topologies from the top bar:

| Slug | Title | Difficulty | Architecture Summary |
| :--- | :--- | :--- | :--- |
| `two-pcs-direct` | **Direct Two PC Link** | Beginner | Two PCs (`192.168.1.10` and `192.168.1.20`) connected via a direct Ethernet cable. Demonstrates peer-to-peer communication without switches. |
| `simple-switched-lan` | **Simple Switched LAN** | Beginner | Three workstations connected through a 4-port Layer 2 switch on subnet `192.168.1.0/24`. Demonstrates switch MAC learning and broadcast domains. |
| `dual-subnet-router` | **Dual Subnet Router** | Intermediate | Two subnets (`192.168.1.0/24` and `192.168.2.0/24`) connected via a two-legged Layer 3 router. Demonstrates default gateways and cross-subnet routing. |
| `segmented-vlan-network` | **Segmented VLAN Network** | Intermediate | Four PCs on an L2 switch separated into VLAN 10 (Engineering) and VLAN 20 (Finance). Demonstrates Layer 2 isolation. |
| `dmz-firewall-perimeter` | **DMZ Firewall Perimeter** | Advanced | Enterprise perimeter with Internal LAN, DMZ Web Server (`172.16.1.10`), and external WAN Internet Cloud, secured by an ACL Firewall. |
| `dhcp-dns-services-lab` | **Enterprise DNS & DHCP Services** | Intermediate | Central switch linking dynamic workstations, a DNS server (`192.168.1.53`), and a DHCP server (`192.168.1.67`). |

---

## 2. Guided Scenarios Catalog

Guided scenarios present students with structured hands-on missions, task checklists, progressive hints, and automated scoring:

```text
BEGINNER TIER
 ├── 1. First Ping: Peer-to-Peer
 ├── 2. Build Your First Switched LAN
 ├── 3. Subnet Configuration Mastery
 └── 4. Default Gateway Setup

INTERMEDIATE TIER
 ├── 5. Connect Two Subnets with a Router
 ├── 6. VLAN Segmentation Challenge
 ├── 7. Configure Automated DHCP Service
 └── 8. Set Up Local DNS Resolution

ADVANCED TIER
 ├── 9. Secure the Web Server with a Firewall
 └── 10. Troubleshoot the Broken Enterprise Network
```

### Scenario Specifications

#### 1. First Ping: Peer-to-Peer (`first-ping`)
* **Difficulty**: Beginner | **Est. Time**: 5 mins | **Max Score**: 100 pts
* **Objective**: Connect PC1 (`192.168.1.10`) directly to PC2 (`192.168.1.20`) using an Ethernet cable and verify ICMP ping delivery.
* **Validation Rules**: `DEVICE_CONNECTED` (PC1 $\leftrightarrow$ PC2), `PING_SUCCESS` (PC1 $\to$ PC2).

#### 2. Build Your First Switched LAN (`build-switched-lan`)
* **Difficulty**: Beginner | **Est. Time**: 10 mins | **Max Score**: 100 pts
* **Objective**: Drag a Switch onto the canvas, wire 3 PCs into ports 1, 2, and 3, and ensure all devices can communicate.
* **Validation Rules**: `DEVICE_EXISTS` (Switch), `DEVICE_CONNECTED` (PC1 $\to$ Switch, PC2 $\to$ Switch, PC3 $\to$ Switch), `PING_SUCCESS` (PC1 $\to$ PC3).

#### 3. Subnet Configuration Mastery (`subnet-configuration-mastery`)
* **Difficulty**: Beginner | **Est. Time**: 10 mins | **Max Score**: 100 pts
* **Objective**: Fix a misconfigured workstation (`192.168.2.50`) plugged into a `192.168.1.0/24` switch by changing its IP address to match the subnet.
* **Validation Rules**: `SUBNET_MATCH` (PC2 on `192.168.1.0/24`), `PING_SUCCESS` (PC1 $\to$ PC2).

#### 4. Default Gateway Setup (`default-gateway-setup`)
* **Difficulty**: Beginner | **Est. Time**: 10 mins | **Max Score**: 100 pts
* **Objective**: Configure PC1 and PC2 with their router interface IP (`192.168.1.1`) as their default gateway so traffic destined for the internet reaches the router.
* **Validation Rules**: `GATEWAY_MATCH` (PC1 gateway = `192.168.1.1`), `GATEWAY_MATCH` (PC2 gateway = `192.168.1.1`).

#### 5. Connect Two Subnets with a Router (`route-two-subnets`)
* **Difficulty**: Intermediate | **Est. Time**: 15 mins | **Max Score**: 100 pts
* **Objective**: Add a Router between LAN A (`192.168.1.0/24`) and LAN B (`192.168.2.0/24`). Configure router interfaces and verify cross-subnet ping.
* **Validation Rules**: `ROUTE_EXISTS` (Router interfaces configured for both subnets), `PING_SUCCESS` (PC1 $\to$ PC2 across router).

#### 6. VLAN Segmentation Challenge (`vlan-segmentation`)
* **Difficulty**: Intermediate | **Est. Time**: 15 mins | **Max Score**: 100 pts
* **Objective**: Isolate Sales (Ports 1 & 2 on VLAN 10) from HR (Ports 3 & 4 on VLAN 20). Verify Sales PCs can ping each other, but cannot ping HR.
* **Validation Rules**: `VLAN_MATCH` (Port 1 = VLAN 10, Port 3 = VLAN 20), `PING_SUCCESS` (PC1 $\to$ PC2 on VLAN 10), `PING_BLOCKED` (PC1 $\to$ PC3 on VLAN 20).

#### 7. Configure Automated DHCP Service (`configure-dhcp-service`)
* **Difficulty**: Intermediate | **Est. Time**: 15 mins | **Max Score**: 100 pts
* **Objective**: Deploy a DHCP server with pool `192.168.1.100 - 192.168.1.200`. Send a DHCP discover from an unconfigured PC to lease an address.
* **Validation Rules**: `DEVICE_EXISTS` (DHCP Server), `IP_MATCH` (PC received leased IP within range).

#### 8. Set Up Local DNS Resolution (`setup-local-dns`)
* **Difficulty**: Intermediate | **Est. Time**: 15 mins | **Max Score**: 100 pts
* **Objective**: Add `intra.corp -> 192.168.1.50` to the DNS server. Configure PC1's DNS setting and perform a DNS lookup.
* **Validation Rules**: `DNS_RECORD_EXISTS` (`intra.corp`), `DNS_QUERY_SUCCESS` (PC1 resolves `intra.corp`).

#### 9. Secure the Web Server with a Firewall (`firewall-dmz-security`)
* **Difficulty**: Advanced | **Est. Time**: 20 mins | **Max Score**: 100 pts
* **Objective**: Configure firewall ACL rules to allow incoming HTTP traffic on port 80 to the Web Server, but drop all Telnet (port 23) and ICMP ping probes from the WAN.
* **Validation Rules**: `FIREWALL_RULE` (Allow TCP 80), `FIREWALL_RULE` (Deny TCP 23), `PING_BLOCKED` (Internet $\to$ Web Server).

#### 10. Troubleshoot the Broken Enterprise Network (`troubleshoot-broken-enterprise`)
* **Difficulty**: Advanced | **Est. Time**: 25 mins | **Max Score**: 100 pts
* **Objective**: A multi-subnet network has 3 faults: an IP conflict on PC2, a missing default gateway on Server1, and an inverted ACL on Firewall1. Diagnose and fix all 3 faults.
* **Validation Rules**: `ALL_PASSED` across 3 distinct sub-objectives.

---

## 3. Objective Evaluator Engine

The server-authoritative evaluator (`SimulatorValidationService`) inspects the student's topology submission against each scenario rule:

```python
class SimulatorValidationService:
    def validate_scenario(
        self,
        scenario: SimulatorScenario,
        topology_data: dict,
        hints_used: int = 0
    ) -> ScenarioValidationResult:
        # 1. Parse devices and links into graph
        # 2. Evaluate each rule in scenario.validation_rules
        # 3. Calculate score with progressive hint penalty (-10 pts per hint)
        # 4. Return structured pass/fail feedback for each task
```

### Progressive Hint System
Every scenario provides 2 to 3 hints that reveal progressively more specific guidance:
1. **Hint 1 (-10% score)**: General conceptual direction.
2. **Hint 2 (-20% score)**: Specific IP / interface / port recommendation.
3. **Solution Reveal (-50% score)**: Full step-by-step resolution.
