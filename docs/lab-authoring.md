# NexoraNet Lab Authoring Guide

> **Audience**: Networking Instructors, Cybersecurity Engineers, and Curriculum Authors  
> **Platform**: NexoraNet Hands-on Networking Lab Engine

---

## 1. Lab Design Principles

When authoring a NexoraNet lab, strictly follow the **LEARN → DO → OBSERVE → EXPLAIN → VALIDATE → CHALLENGE** pedagogical pattern:

1. **Safety First**: Labs targeting `LOCAL_SYSTEM` must **only** use safe, non-destructive, read-only interrogation utilities (`ipconfig`, `ip addr`, `netstat -ano`, `ss -tuln`, `route print`, `ip route`, `ping 127.0.0.1`, `nslookup`). Never instruct students to modify registry entries, disable firewalls, or bind malicious payloads.
2. **Platform Inclusivity**: Always provide commands for **Windows (PowerShell / CMD)**, **Linux (Bash / Zsh)**, and **macOS (Terminal)**.
3. **Zero Answer Leaks**: Never put plaintext answers or raw answer hashes into the frontend-facing fields. All correct answers reside exclusively within `answer_data` in the database seed files.
4. **Actionable Hints**: Hints must unblock students without trivially revealing the final answer.
5. **Defensive Relevance**: Always connect the operational skill to a real-world cybersecurity or network defense scenario.

---

## 2. Lab Schema Reference

Every lab is defined as a Python dictionary within `backend/app/seed/data_labs_*.py`:

```python
{
    "title": "Find Your Local IPv4 Address",
    "slug": "find-your-local-ipv4-address",
    "description": "Inspect your local host network interface and record your private IPv4 address.",
    "difficulty": "BEGINNER",  # "BEGINNER" | "INTERMEDIATE" | "ADVANCED"
    "estimated_minutes": 15,
    "environment_type": "LOCAL_SYSTEM",  # "LOCAL_SYSTEM" | "CONCEPTUAL" | "CONTAINER" | "PCAP" | "SIMULATOR" | "LOG_ANALYSIS"
    "topic_slug": "ip-addressing-and-subnetting",
    "status": "PUBLISHED",  # "PUBLISHED" | "DRAFT" | "ARCHIVED"
    "instructions": (
        "### Lab Overview\n\n"
        "Every network device requires an IP address to communicate across a network..."
    ),
    "objectives": [
        "Execute operating system command-line networking tools",
        "Locate and verify your host IPv4 address",
        "Classify RFC 1918 private address ranges",
    ],
    "prerequisites": [
        "Basic familiarity with opening a command terminal",
        "Understanding of IPv4 dotted-decimal format",
    ],
    "steps": [
        # List of step blueprints
    ]
}
```

---

## 3. Step Blueprint Schema

Each step in the `steps` array contains:

```python
{
    "step_number": 1,
    "title": "Execute Network Configuration Command",
    "description": "Run the appropriate network interrogation utility for your operating system.",
    "instructions": (
        "Open your terminal and run the network configuration command corresponding to your OS:\n\n"
        "* **Windows (PowerShell or CMD)**: `ipconfig`\n"
        "* **Linux**: `ip addr` or `ip a`\n"
        "* **macOS**: `ifconfig`\n\n"
        "Observe the output list of network adapters."
    ),
    "hint": "On Windows, typing 'ipconfig' and pressing Enter displays all active network adapters.",
    "expected_observation": "A list of adapters with IPv4 addresses, subnet masks, and default gateways.",
    "validation_type": "SINGLE_CHOICE",
    "points": 10,
    "is_required": True,
    "question": {
        "question_text": "Which command-line utility did you use to inspect your network adapter configuration?",
        "question_type": "SINGLE_CHOICE",
        "points": 10,
        "answer_data": {
            "options": ["ipconfig", "ip addr", "ifconfig", "traceroute"],
            "correct_options": ["ipconfig", "ip addr", "ifconfig"],
            "explanation": "ipconfig (Windows), ip addr (Linux), and ifconfig (macOS/legacy Linux) query the OS network stack."
        }
    }
}
```

---

## 4. Supported Validation Types & `answer_data` Formats

### 1. `SINGLE_CHOICE`
Requires the student to select one option.
```python
"answer_data": {
    "options": ["TCP", "UDP", "ICMP", "ARP"],
    "correct_answer": "TCP",
    "explanation": "TCP provides reliable, ordered stream delivery."
}
```

### 2. `MULTIPLE_CHOICE`
Requires the student to select all matching options.
```python
"answer_data": {
    "options": [
        "10.0.0.0/8",
        "172.16.0.0/12",
        "192.168.0.0/16",
        "8.8.8.0/24"
    ],
    "correct_options": ["10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"],
    "explanation": "RFC 1918 defines the three private address spaces."
}
```

### 3. `TEXT` & `SHORT_ANSWER`
String comparison with case-insensitivity, whitespace trimming, and optional synonyms or regex.
```python
"answer_data": {
    "correct_answer": "SYN-ACK",
    "synonyms": ["SYN/ACK", "SYN ACK"],
    "explanation": "The server responds to SYN with a combined SYN-ACK."
}
```

### 4. `NUMERICAL`
Validates exact integers or floating point values with optional tolerance.
```python
"answer_data": {
    "correct_number": 62,
    "tolerance": 0,
    "explanation": "A /26 subnet reserves 2 addresses, leaving 2^6 - 2 = 62 usable host addresses."
}
```

### 5. `IP_ADDRESS`
Validates IPv4 or IPv6 format, or verifies that the IP belongs to a required RFC space (e.g. `requires_private: True`).
```python
"answer_data": {
    "requires_private": True,
    "explanation": "RFC 1918 private IPv4 addresses are reserved for internal networks."
}
```

### 6. `CIDR`
Validates CIDR prefix notation (`IP/prefix`).
```python
"answer_data": {
    "correct_cidr": "192.168.10.0/24",
    "explanation": "The network address with prefix /24 identifies the subnet."
}
```

### 7. `SUBNET`
Validates subnet masks or structured multi-field calculations (`network_address`, `broadcast_address`, `usable_hosts`).
```python
"answer_data": {
    "fields": ["network", "broadcast"],
    "correct_network": "192.168.1.0",
    "correct_broadcast": "192.168.1.255",
    "explanation": "Network is all host bits 0; broadcast is all host bits 1."
}
```

### 8. `PORT`
Validates standard TCP/UDP port numbers (1 - 65535).
```python
"answer_data": {
    "correct_port": 53,
    "explanation": "DNS operates over UDP port 53 for standard queries."
}
```

---

## 5. Adding New Labs to NexoraNet

1. Open `backend/app/seed/data_labs_beginner.py` (or `data_labs_intermediate.py`).
2. Add your lab definition dictionary to the corresponding array (`BEGINNER_LABS` or `INTERMEDIATE_LABS`).
3. Re-run database seeding:
   ```bash
   python -m app.seed.seed_db
   ```
4. Run the automated test suite to ensure schema and validation compliance:
   ```bash
   pytest tests/test_lab_engine.py
   ```
