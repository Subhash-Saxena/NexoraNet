# NexoraNet Simulator Security & Safety Architecture

The **NexoraNet Interactive Network Simulator** is designed from the ground up as a safe, isolated, purely virtual educational environment.

---

## 1. Safety Boundary & Sandbox Isolation

### No Real Packets or Raw Sockets
* **Zero Socket System Calls**: The simulator does **not** create raw sockets, AF_INET sockets, or AF_PACKET sockets.
* **No External Packet Generators**: No Scapy, tcpdump, or Wireshark hooks are used in Step 9.
* **No Shell Execution**: The backend executes **zero** subprocesses (`os.system`, `subprocess.Popen`) and executes **zero** dynamic string evaluation (`eval()`, `exec()`).
* **Zero Real Network Reachability**: Running a ping or TCP handshake in the simulator transmits data only in memory within the FastAPI application runtime. No IP packet ever touches the host's physical network interface or default gateway.

### Prominent User Interface Disclaimer
Every page render of the Network Simulator displays the persistent disclaimer banner:
> **Educational Sandbox Notice:** NexoraNet Simulator uses a virtual network. Packets shown here are simulated and are not sent onto your real network.

---

## 2. JSON Import Sanitization & Validation

When a user imports an exported topology JSON or submits a topology via the REST API (`POST /api/v1/simulator/simulate/packet`), strict defenses are applied:

1. **Pydantic Schema Enforcement**:
   All incoming payloads are strictly validated against `SimulatePacketRequest` and `TopologyDataSchema`. Extra or unrecognized properties are forbidden or stripped.

2. **Resource & Graph Size Quotas**:
   - **Max Devices**: Limited to a maximum of 50 devices per topology to prevent CPU exhaustion during graph traversal.
   - **Max Links**: Limited to a maximum of 100 links per topology.
   - **Max Payload Size**: API request body size is capped at 512 KB.

3. **String Sanitization & ID Validation**:
   - Device IDs and names are restricted to alphanumeric characters, hyphens, and underscores `^[a-zA-Z0-9_-]{1,64}$`.
   - IP addresses and subnet masks must parse cleanly through Python's `ipaddress.IPv4Network` / `ipaddress.IPv4Address` modules without error.
   - Malformed, octal-padded, or ambiguous IP formats are rejected.

---

## 3. Algorithmic Complexity Bounds & Loop Protection

Simulating packet forwarding across arbitrary user-drawn network graphs could risk infinite loops if cyclical links are created without Spanning Tree Protocol (STP).

To prevent Denial of Service (DoS):

1. **Hard Hop Count Limit**:
   The simulation engine enforces a strict maximum hop count ($H_{\text{max}} = 30$). If a frame traverses more than 30 hops without reaching its destination, simulation halts immediately with status `DROPPED` and explanation `"Exceeded maximum hop threshold (potential Layer 2 switching loop detected)"`.

2. **Visited Interface Cycle Detection**:
   The engine tracks visited interface tuples `(device_id, interface_id, vlan_id)`. If an identical frame visits the same interface twice within a single simulation pass, a loop is detected and reported.

3. **IPv4 TTL Enforcement**:
   Every Layer 3 hop decrements the packet's TTL. Starting from a maximum of 64 or 128, reaching $\text{TTL} = 0$ triggers an immediate drop and generates an educational `ICMP Time Exceeded` event.

---

## 4. Multi-Tenant User Isolation

* **Template vs User Topologies**:
  System prebuilt topologies are marked `is_template = true` and `user_id = NULL`. They are read-only and cannot be altered or deleted by regular users.
* **User Data Ownership**:
  When a logged-in user saves a topology, it is tagged with their `user_id`. Queries filter by `user_id == current_user.id OR is_template == true`.
* **Safe Scenario Validation**:
  Scenario verification runs deterministic rule matchers on the submitted topology state. No user input is interpreted as code.
