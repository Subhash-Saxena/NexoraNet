"""Catalog of standard detection rules for the Step 11 Detection Engine.

Contains definitions, declarative matching criteria, educational explanations,
and investigation guides for all 15 core rules.
"""

from typing import Any

from app.models.enums import AlertConfidence, AlertSeverity, RuleCategory, RuleStatus

BUILTIN_RULES: list[dict[str, Any]] = [
    {
        "rule_id": "NET-TCP-001",
        "name": "Repeated TCP Connection Attempts",
        "description": "Identifies multiple consecutive TCP connection attempts (SYN packets) to a single destination and port.",
        "category": RuleCategory.TCP,
        "severity": AlertSeverity.MEDIUM,
        "confidence_default": AlertConfidence.MEDIUM,
        "status": RuleStatus.ENABLED,
        "logic_type": "THRESHOLD",
        "threshold": 5.0,
        "time_window_seconds": 30,
        "mitre_attack_id": "T1046",
        "mitre_technique": "Network Service Discovery",
        "conditions": {
            "protocol": "TCP",
            "tcp_flags": ["SYN"],
            "exclude_flags": ["ACK"],
            "group_by": ["source_ip", "destination_ip", "destination_port"],
            "min_count": 5,
        },
        "explanation_template": (
            "Observed {count} TCP SYN connection requests from {source_ip} to {destination_ip}:{destination_port} "
            "within the analyzed timeframe. In educational networking, repeated connection attempts can occur when a "
            "client retries connecting to an unavailable service, during port reachability diagnostics, or when a "
            "firewall silently drops incoming requests."
        ),
        "investigation_guide": (
            "1. Inspect packet flags to check if SYN-ACK or RST responses were returned by the destination.\n"
            "2. Verify whether the target port is configured to host an active listening service.\n"
            "3. Examine client host retry configuration and network connectivity between endpoints."
        ),
    },
    {
        "rule_id": "NET-TCP-002",
        "name": "SYN Pattern (High SYN Without Handshake Completion)",
        "description": "Detects an elevated ratio of TCP SYN requests where the 3-way handshake is never completed.",
        "category": RuleCategory.TCP,
        "severity": AlertSeverity.MEDIUM,
        "confidence_default": AlertConfidence.HIGH,
        "status": RuleStatus.ENABLED,
        "logic_type": "RATIO",
        "threshold": 0.2,  # completion ratio < 20%
        "time_window_seconds": 60,
        "mitre_attack_id": "T1046",
        "mitre_technique": "Network Service Discovery",
        "conditions": {
            "protocol": "TCP",
            "min_syn_count": 5,
            "max_completion_ratio": 0.2,
            "group_by": ["source_ip"],
        },
        "explanation_template": (
            "An elevated ratio of TCP SYN requests without corresponding three-way handshake completions was observed "
            "for host {source_ip} ({syn_count} SYNs, {completed_count} completed sessions). This pattern indicates "
            "connection attempts are failing to establish, which may happen when targeting closed ports, when intermediate "
            "filters drop traffic, or during systematic port probing."
        ),
        "investigation_guide": (
            "1. Review destination ports targeted by the source host.\n"
            "2. Check if destinations respond with TCP RST or if packets are silently dropped.\n"
            "3. Correlate with firewall access-list rules and target host availability."
        ),
    },
    {
        "rule_id": "NET-TCP-003",
        "name": "TCP Reset Spike",
        "description": "Detects an unusual burst of TCP Reset (RST) packets indicating rejected or abruptly torn-down connections.",
        "category": RuleCategory.TCP,
        "severity": AlertSeverity.LOW,
        "confidence_default": AlertConfidence.MEDIUM,
        "status": RuleStatus.ENABLED,
        "logic_type": "THRESHOLD",
        "threshold": 5.0,
        "time_window_seconds": 30,
        "mitre_attack_id": "T1498",
        "mitre_technique": "Network Denial of Service (Service Degradation)",
        "conditions": {
            "protocol": "TCP",
            "tcp_flags": ["RST"],
            "group_by": ["source_ip", "destination_ip"],
            "min_count": 5,
        },
        "explanation_template": (
            "A burst of {count} TCP Reset (RST) packets was recorded between {source_ip} and {destination_ip}. "
            "TCP resets occur legitimately when an application closes abruptly, when packets arrive for a closed port, "
            "or when a stateful firewall or NAT gateway tears down an expired session."
        ),
        "investigation_guide": (
            "1. Determine whether the source or destination host generated the RST packets.\n"
            "2. Correlate RST sequence numbers with prior TCP data streams.\n"
            "3. Check whether the listening application on the target port crashed or restarted."
        ),
    },
    {
        "rule_id": "NET-CONN-001",
        "name": "Repeated Connection Attempts (Same Destination)",
        "description": "Flags repeated connection initiations to the same destination address across any transport protocol.",
        "category": RuleCategory.CONNECTION_BEHAVIOR,
        "severity": AlertSeverity.LOW,
        "confidence_default": AlertConfidence.LOW,
        "status": RuleStatus.ENABLED,
        "logic_type": "THRESHOLD",
        "threshold": 8.0,
        "time_window_seconds": 60,
        "mitre_attack_id": "T1071",
        "mitre_technique": "Standard Application Layer Protocol",
        "conditions": {
            "group_by": ["source_ip", "destination_ip"],
            "min_count": 8,
        },
        "explanation_template": (
            "Frequent, repeated connection attempts ({count} interactions) were recorded from {source_ip} to {destination_ip}. "
            "This pattern is commonly seen in continuous polling services, monitoring agents, health check pings, or "
            "unsuccessful client reconnection loops."
        ),
        "investigation_guide": (
            "1. Examine the inter-packet arrival timing to see if attempts follow an automated interval.\n"
            "2. Identify the higher-layer protocol (HTTP, DNS, custom service).\n"
            "3. Confirm if the destination IP corresponds to an authorized internal server or external API."
        ),
    },
    {
        "rule_id": "NET-CONN-002",
        "name": "Repeated Connection Failures",
        "description": "Identifies recurring failed connection attempts where sessions fail to establish.",
        "category": RuleCategory.CONNECTION_BEHAVIOR,
        "severity": AlertSeverity.MEDIUM,
        "confidence_default": AlertConfidence.MEDIUM,
        "status": RuleStatus.ENABLED,
        "logic_type": "THRESHOLD",
        "threshold": 5.0,
        "time_window_seconds": 60,
        "mitre_attack_id": "T1046",
        "mitre_technique": "Network Service Discovery",
        "conditions": {
            "failed_state": True,
            "group_by": ["source_ip", "destination_ip"],
            "min_count": 5,
        },
        "explanation_template": (
            "Observed {count} consecutive failed connection initiations from {source_ip} towards {destination_ip}. "
            "Repeated failures typically signify service downtime, misconfigured client ports, network routing "
            "blackholes, or restricted firewall access."
        ),
        "investigation_guide": (
            "1. Check if destination host routing is functioning along intermediate hops.\n"
            "2. Verify whether access-lists or security groups permit traffic between these subnets.\n"
            "3. Inspect server-side daemon status on the destination host."
        ),
    },
    {
        "rule_id": "NET-DNS-001",
        "name": "DNS NXDOMAIN Spike",
        "description": "Detects an unusual cluster of DNS Non-Existent Domain (NXDOMAIN) error responses.",
        "category": RuleCategory.DNS,
        "severity": AlertSeverity.MEDIUM,
        "confidence_default": AlertConfidence.HIGH,
        "status": RuleStatus.ENABLED,
        "logic_type": "THRESHOLD",
        "threshold": 4.0,
        "time_window_seconds": 60,
        "mitre_attack_id": "T1568",
        "mitre_technique": "Dynamic Resolution",
        "conditions": {
            "protocol": "DNS",
            "dns_rcode": 3,  # NXDOMAIN
            "group_by": ["source_ip"],
            "min_count": 4,
        },
        "explanation_template": (
            "Host {source_ip} generated or received {count} DNS NXDOMAIN (Name Error) responses. "
            "In enterprise networks, NXDOMAIN spikes can result from mistyped hostnames, stale internal DNS search "
            "suffixes, retired microservice URLs, or algorithmic domain generation (DGA) lookups."
        ),
        "investigation_guide": (
            "1. Inspect the domain names queried in the attached evidence packets.\n"
            "2. Look for randomized strings, uniform length patterns, or missing top-level domains.\n"
            "3. Verify if client software recently attempted discovery of discontinued services."
        ),
    },
    {
        "rule_id": "NET-DNS-002",
        "name": "High DNS Query Frequency",
        "description": "Flags a high volume of DNS queries originating from a single endpoint within a short window.",
        "category": RuleCategory.DNS,
        "severity": AlertSeverity.LOW,
        "confidence_default": AlertConfidence.LOW,
        "status": RuleStatus.ENABLED,
        "logic_type": "THRESHOLD",
        "threshold": 10.0,
        "time_window_seconds": 30,
        "mitre_attack_id": "T1071.004",
        "mitre_technique": "Application Layer Protocol: DNS",
        "conditions": {
            "protocol": "DNS",
            "is_query": True,
            "group_by": ["source_ip"],
            "min_count": 10,
        },
        "explanation_template": (
            "Recorded {count} DNS queries from host {source_ip} in a short observation window. "
            "Elevated DNS query rates are common when browsing modern websites with dozens of third-party assets, "
            "during software update checks, or when a local DNS resolver cache is disabled."
        ),
        "investigation_guide": (
            "1. Calculate the query rate per second to determine burst intensity.\n"
            "2. Check if the queries target many diverse domains or repeatedly ask for the same record.\n"
            "3. Verify whether a local caching daemon (like systemd-resolved or dnsmasq) is operational on the client."
        ),
    },
    {
        "rule_id": "NET-DNS-003",
        "name": "Unusual DNS Pattern (High Subdomain Diversity)",
        "description": "Identifies queries for multiple distinct subdomains under a single parent domain.",
        "category": RuleCategory.DNS,
        "severity": AlertSeverity.MEDIUM,
        "confidence_default": AlertConfidence.MEDIUM,
        "status": RuleStatus.ENABLED,
        "logic_type": "STATISTICAL",
        "threshold": 4.0,  # 4 or more distinct subdomains
        "time_window_seconds": 60,
        "mitre_attack_id": "T1071.004",
        "mitre_technique": "Application Layer Protocol: DNS",
        "conditions": {
            "protocol": "DNS",
            "min_unique_subdomains": 4,
            "group_by": ["source_ip", "base_domain"],
        },
        "explanation_template": (
            "Host {source_ip} queried {count} distinct subdomains under the domain '{base_domain}'. "
            "While commonly seen with Content Delivery Networks (CDNs) and cloud resource balancing, high subdomain "
            "diversity is also characteristic of DNS tunneling techniques where data is encoded into sublabels."
        ),
        "investigation_guide": (
            "1. Inspect the labels of the subdomains: are they human-readable words or high-entropy encoded strings?\n"
            "2. Check the DNS query types (e.g. TXT, A, CNAME, NULL records).\n"
            "3. Verify ownership and reputation of the parent domain."
        ),
    },
    {
        "rule_id": "NET-ARP-001",
        "name": "ARP Mapping Change (IP with Multiple MACs)",
        "description": "Detects an IP address associated with multiple conflicting hardware MAC addresses.",
        "category": RuleCategory.ARP,
        "severity": AlertSeverity.HIGH,
        "confidence_default": AlertConfidence.HIGH,
        "status": RuleStatus.ENABLED,
        "logic_type": "PATTERN",
        "threshold": 2.0,
        "time_window_seconds": 120,
        "mitre_attack_id": "T1557.002",
        "mitre_technique": "Adversary-in-the-Middle: ARP Poisoning",
        "conditions": {
            "protocol": "ARP",
            "min_mac_count": 2,
            "group_by": ["source_ip"],
        },
        "explanation_template": (
            "IP address {source_ip} was observed claiming multiple distinct MAC addresses ({mac_list}) in captured "
            "ARP traffic. In production networks, this can occur during router redundancy failover (HSRP/VRRP), "
            "network interface migration, or DHCP lease reuse; in security monitoring, it warrants investigation for "
            "ARP spoofing or cache poisoning."
        ),
        "investigation_guide": (
            "1. Verify whether VRRP, HSRP, or CARP failover protocols are active on this subnet.\n"
            "2. Lookup MAC addresses in vendor OUI registries to identify the hardware manufacturers.\n"
            "3. Check switch port-security and Dynamic ARP Inspection (DAI) logs on local network switches."
        ),
    },
    {
        "rule_id": "NET-ICMP-001",
        "name": "ICMP Traffic Burst",
        "description": "Identifies an elevated volume of ICMP Echo Request messages from a single host.",
        "category": RuleCategory.ICMP,
        "severity": AlertSeverity.LOW,
        "confidence_default": AlertConfidence.LOW,
        "status": RuleStatus.ENABLED,
        "logic_type": "THRESHOLD",
        "threshold": 8.0,
        "time_window_seconds": 30,
        "mitre_attack_id": "T1018",
        "mitre_technique": "Remote System Discovery",
        "conditions": {
            "protocol": "ICMP",
            "icmp_type": 8,  # Echo Request
            "group_by": ["source_ip"],
            "min_count": 8,
        },
        "explanation_template": (
            "A burst of {count} ICMP Echo Request messages originated from {source_ip}. "
            "Ping sequences are routine diagnostic tools for path latency and reachability verification, but sudden "
            "bursts can also indicate automated network discovery sweeps across local subnet ranges."
        ),
        "investigation_guide": (
            "1. Inspect destination IP addresses to see if requests are directed at one host or sequential addresses.\n"
            "2. Review the ICMP payload size and data pattern.\n"
            "3. Check if an authorized network management tool was performing diagnostic health monitoring."
        ),
    },
    {
        "rule_id": "NET-PORT-001",
        "name": "Unusual Port Usage",
        "description": "Detects communication directed towards cataloged noteworthy or non-standard network ports.",
        "category": RuleCategory.PROTOCOL_ANOMALY,
        "severity": AlertSeverity.MEDIUM,
        "confidence_default": AlertConfidence.MEDIUM,
        "status": RuleStatus.ENABLED,
        "logic_type": "PATTERN",
        "threshold": 1.0,
        "time_window_seconds": 60,
        "mitre_attack_id": "T1571",
        "mitre_technique": "Non-Standard Port",
        "conditions": {
            "noteworthy_ports": [4444, 1337, 6667, 31337, 8888, 9999, 5555],
            "group_by": ["source_ip", "destination_ip", "destination_port"],
            "min_count": 1,
        },
        "explanation_template": (
            "Communication was detected involving port {destination_port} between {source_ip} and {destination_ip}. "
            "Port {destination_port} is historically associated with non-standard services, test harnesses, or legacy "
            "protocols. While legitimate custom applications often bind to high ports, analyst review is recommended "
            "to confirm the underlying service."
        ),
        "investigation_guide": (
            "1. Examine application layer payload data to identify the protocol running on this port.\n"
            "2. Correlate with listening process tables on destination host {destination_ip}.\n"
            "3. Confirm if developers or lab scenarios utilize this port for custom testing."
        ),
    },
    {
        "rule_id": "NET-TRAFFIC-001",
        "name": "Large Traffic Volume Burst",
        "description": "Flags a high volume of packets concentrated in a single flow or brief timeframe.",
        "category": RuleCategory.TRAFFIC_ANALYSIS,
        "severity": AlertSeverity.LOW,
        "confidence_default": AlertConfidence.LOW,
        "status": RuleStatus.ENABLED,
        "logic_type": "THRESHOLD",
        "threshold": 30.0,
        "time_window_seconds": 60,
        "mitre_attack_id": "T1030",
        "mitre_technique": "Data Transfer Size Limits",
        "conditions": {
            "group_by": ["source_ip", "destination_ip"],
            "min_count": 30,
        },
        "explanation_template": (
            "A high volume of {count} packets was transferred between {source_ip} and {destination_ip}. "
            "Traffic bursts are normal during file downloads, video streaming, database backups, or package updates, "
            "but should be correlated with expected user and system operations."
        ),
        "investigation_guide": (
            "1. Calculate the total byte transfer and flow duration.\n"
            "2. Identify the higher-layer protocol (HTTP/HTTPS, SSH, FTP, SMB).\n"
            "3. Confirm if the endpoints were actively engaged in authorized large-scale data transfer."
        ),
    },
    {
        "rule_id": "NET-TRAFFIC-002",
        "name": "Periodic Network Communication Pattern",
        "description": "Detects communication occurring at remarkably regular, periodic time intervals.",
        "category": RuleCategory.TRAFFIC_ANALYSIS,
        "severity": AlertSeverity.MEDIUM,
        "confidence_default": AlertConfidence.MEDIUM,
        "status": RuleStatus.ENABLED,
        "logic_type": "STATISTICAL",
        "threshold": 0.25,  # relative standard deviation of delta timestamps < 0.25
        "time_window_seconds": 120,
        "mitre_attack_id": "T1071",
        "mitre_technique": "Application Layer Protocol",
        "conditions": {
            "min_packet_count": 4,
            "max_relative_std_dev": 0.25,
            "group_by": ["source_ip", "destination_ip"],
        },
        "explanation_template": (
            "Observed highly regular periodic communication between {source_ip} and {destination_ip} ({count} packets "
            "with regular inter-arrival intervals). Periodic signals are standard for NTP time synchronization, "
            "sensor heartbeats, and cluster keep-alives, but uniform beaconing is also a key indicator of automated "
            "command-and-control communication."
        ),
        "investigation_guide": (
            "1. Measure the average time interval (seconds) between packets.\n"
            "2. Check whether payload length is consistent across successive transmissions.\n"
            "3. Determine if the destination is a known cloud telemetry endpoint or internal heartbeat service."
        ),
    },
    {
        "rule_id": "NET-HTTP-001",
        "name": "Repeated HTTP Error Responses",
        "description": "Identifies recurring HTTP 4xx or 5xx status codes returned by a web server.",
        "category": RuleCategory.HTTP,
        "severity": AlertSeverity.MEDIUM,
        "confidence_default": AlertConfidence.MEDIUM,
        "status": RuleStatus.ENABLED,
        "logic_type": "THRESHOLD",
        "threshold": 4.0,
        "time_window_seconds": 60,
        "mitre_attack_id": "T1190",
        "mitre_technique": "Exploit Public-Facing Application",
        "conditions": {
            "protocol": "HTTP",
            "error_status_codes": [400, 401, 403, 404, 500, 502, 503],
            "group_by": ["source_ip", "destination_ip"],
            "min_count": 4,
        },
        "explanation_template": (
            "Identified {count} HTTP error response messages (e.g. 404 Not Found, 403 Forbidden) sent to {destination_ip} "
            "from server {source_ip}. Repeated HTTP errors can occur due to broken website links, API deprecation, or "
            "automated web application path fuzzing."
        ),
        "investigation_guide": (
            "1. Inspect the requested URI paths and query strings in the evidence packets.\n"
            "2. Check the client User-Agent header for known automated scanners or legitimate web browsers.\n"
            "3. Verify web server access and error logs."
        ),
    },
    {
        "rule_id": "NET-RECON-001",
        "name": "Multi-Destination Connection Pattern",
        "description": "Detects a single source address initiating connections to multiple distinct destination hosts.",
        "category": RuleCategory.RECON_DETECTION,
        "severity": AlertSeverity.HIGH,
        "confidence_default": AlertConfidence.HIGH,
        "status": RuleStatus.ENABLED,
        "logic_type": "STATISTICAL",
        "threshold": 4.0,  # 4 or more distinct destination IPs
        "time_window_seconds": 60,
        "mitre_attack_id": "T1046",
        "mitre_technique": "Network Service Discovery",
        "conditions": {
            "min_distinct_destinations": 4,
            "group_by": ["source_ip"],
        },
        "explanation_template": (
            "Host {source_ip} initiated connections to {dst_count} distinct destination IP addresses across the capture. "
            "While normal for gateway routers, proxies, and multi-threaded web browsers, fan-out to multiple internal "
            "subnets is a common footprint of host discovery or horizontal network scanning."
        ),
        "investigation_guide": (
            "1. Check if destination addresses fall within internal local subnets or public Internet ranges.\n"
            "2. Examine whether identical destination ports are targeted across hosts.\n"
            "3. Check whether the source machine is an authorized inventory scanner, proxy, or standard endpoint."
        ),
    },
]


def get_builtin_rule_by_id(rule_id: str) -> dict[str, Any] | None:
    """Retrieve a built-in rule definition by its code."""
    for rule in BUILTIN_RULES:
        if rule["rule_id"] == rule_id:
            return rule
    return None
