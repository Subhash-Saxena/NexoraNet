# NexoraNet SOC Analyst Investigation Methodology

> **Target Audience:** Cybersecurity Students, Aspiring SOC Analysts  
> **Module:** Step 11 — Network Detection Engine

---

## 1. The Educational SOC Workflow

When an alert is flagged by the detection engine, a SOC analyst must determine whether it represents a genuine security concern, an IT misconfiguration, or benign background network activity.

Follow the **O-I-V-D** methodology:

```text
  OBSERVE           INVESTIGATE         VALIDATE             DOCUMENT
+------------+     +-------------+     +---------------+     +---------------+
| Read alert | --> | Inspect     | --> | Determine true| --> | Change status |
| title,     |     | packets,    |     | positive vs   |     | and record    |
| severity & |     | flow stats  |     | false positive|     | rationale     |
| flow box   |     | & checklist |     |               |     | in notes      |
+------------+     +-------------+     +---------------+     +---------------+
```

---

## 2. Step-by-Step Investigation Guide

### Step 1: Review Context & 5-Tuple
Look at the **Flow Box** at the top of the Alert Details page:
- **Source IP & Port:** What kind of device is the sender? (Workstation, server, DNS resolver, gateway?)
- **Destination IP & Port:** What service is being addressed? (Web port 80/443, DNS port 53, or an uncommon port like 4444?)
- **Protocol:** Is the protocol standard for this port?

### Step 2: Work Through the Investigation Checklist
Each alert provides tailored **Investigation Steps**. Check off each step in the interactive checklist as you complete it:
1. Examine packet flags (e.g. check whether SYN packets receive RST or SYN-ACK).
2. Check temporal spacing (is the traffic bursty or periodic?).
3. Inspect DNS resolutions or HTTP request URIs if applicable.

### Step 3: Inspect Linked Evidence Artifacts
Review the **Linked Evidence Table**:
- Look at the `evidence_payload` for individual packets.
- For TCP alerts: check sequence numbers and flag combinations.
- For DNS alerts: check the query domain name and entropy score.
- For ARP alerts: check both conflicting MAC addresses against vendor OUI prefixes.

### Step 4: Differentiate True Positives from Benign False Positives

| Symptom / Pattern | Likely True Positive | Likely False Positive |
| :--- | :--- | :--- |
| **Repeated TCP SYNs (`NET-TCP-001`)** | Single host probing many ports across subnet | Local application reconnecting to web server undergoing restart |
| **DNS NXDOMAIN Spikes (`NET-DNS-001`)** | Randomized subdomains queried periodically (DGA) | Typo in corporate intranet search domain suffix |
| **Conflicting MACs (`NET-ARP-001`)** | Man-in-the-Middle ARP cache poisoning | High-availability failover router (VRRP/HSRP) |
| **Beaconing Pattern (`NET-CONN-001`)** | Cobalt Strike / C2 check-in to external IP | NTP clock synchronization or RSS update check |
| **Suspicious Port 4444 (`NET-PORT-001`)** | Metasploit default listener | Local developer testing an internal mock server |

### Step 5: Document and Conclude
1. Select the appropriate **Lifecycle Status**:
   - `CLOSED`: If verified as a notable anomaly, simulation flag, or threat requiring documentation.
   - `FALSE_POSITIVE`: If verified as legitimate, benign background communication.
2. Enter a clear **Triage Rationale** explaining your conclusion.
3. Add any relevant Wireshark display filters or IP notes to the **Analyst Notes** thread.
