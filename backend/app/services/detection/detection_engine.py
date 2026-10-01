"""Core deterministic evaluation engine for the Step 11 Detection Engine.

Evaluates normalized network events and flow metrics against active detection rules,
deduplicates matches, computes analytical confidence, generates neutral educational
explanations, and formats concrete packet evidence.
"""

import json
import logging
from typing import Any

from app.models.detection import DetectionRule
from app.models.enums import AlertConfidence, AlertSeverity, EvidenceType
from app.services.detection.feature_service import (
    FeatureExtractionService,
    FlowAggregation,
    HostProfile,
    NormalizedEvent,
)

logger = logging.getLogger(__name__)


class RuleMatchResult:
    """Internal candidate detection alert before database persistence."""

    def __init__(
        self,
        rule: DetectionRule,
        title: str,
        category: str,
        severity: str,
        confidence: str,
        source_ip: str | None,
        destination_ip: str | None,
        source_port: int | None,
        destination_port: int | None,
        protocol: str | None,
        first_seen: float | None,
        last_seen: float | None,
        packet_count: int,
        dedup_key: str,
        explanation: str,
        investigation_steps: list[str],
        evidence_items: list[dict[str, Any]],
    ) -> None:
        self.rule = rule
        self.title = title
        self.category = category
        self.severity = severity
        self.confidence = confidence
        self.source_ip = source_ip
        self.destination_ip = destination_ip
        self.source_port = source_port
        self.destination_port = destination_port
        self.protocol = protocol
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.packet_count = packet_count
        self.dedup_key = dedup_key
        self.explanation = explanation
        self.investigation_steps = investigation_steps
        self.evidence_items = evidence_items


class DetectionEngine:
    """Evaluates network telemetry against declarative rule specifications."""

    def __init__(self) -> None:
        self.feature_service = FeatureExtractionService()

    def evaluate(
        self,
        packets: list[Any],
        rules: list[DetectionRule],
        capture_id: int | None = None,
        user_id: int | None = None,
        run_id: int = 0,
    ) -> list[RuleMatchResult]:
        """Run all active rules against the packet set and return deduplicated matches."""
        events, flows, hosts = self.feature_service.extract_features(packets)
        matches: list[RuleMatchResult] = []

        for rule in rules:
            if rule.status != "ENABLED":
                continue

            try:
                rule_matches = self._evaluate_single_rule(rule, events, flows, hosts)
                matches.extend(rule_matches)
            except Exception:
                logger.exception("Error evaluating rule %s", rule.rule_id)

        # Deduplicate matches
        deduped = self._deduplicate_matches(matches)
        return deduped

    def _evaluate_single_rule(
        self,
        rule: DetectionRule,
        events: list[NormalizedEvent],
        flows: dict[Any, FlowAggregation],
        hosts: dict[str, HostProfile],
    ) -> list[RuleMatchResult]:
        """Dispatch evaluation to appropriate rule handler."""
        code = rule.rule_id

        if code == "NET-TCP-001":
            return self._eval_net_tcp_001(rule, flows)
        elif code == "NET-TCP-002":
            return self._eval_net_tcp_002(rule, hosts)
        elif code == "NET-TCP-003":
            return self._eval_net_tcp_003(rule, flows)
        elif code == "NET-CONN-001":
            return self._eval_net_conn_001(rule, flows)
        elif code == "NET-CONN-002":
            return self._eval_net_conn_002(rule, flows)
        elif code == "NET-DNS-001":
            return self._eval_net_dns_001(rule, hosts)
        elif code == "NET-DNS-002":
            return self._eval_net_dns_002(rule, hosts)
        elif code == "NET-DNS-003":
            return self._eval_net_dns_003(rule, hosts)
        elif code == "NET-ARP-001":
            return self._eval_net_arp_001(rule, hosts)
        elif code == "NET-ICMP-001":
            return self._eval_net_icmp_001(rule, hosts)
        elif code == "NET-PORT-001":
            return self._eval_net_port_001(rule, flows)
        elif code == "NET-TRAFFIC-001":
            return self._eval_net_traffic_001(rule, flows)
        elif code == "NET-TRAFFIC-002":
            return self._eval_net_traffic_002(rule, flows)
        elif code == "NET-HTTP-001":
            return self._eval_net_http_001(rule, hosts, events)
        elif code == "NET-RECON-001":
            return self._eval_net_recon_001(rule, hosts)
        else:
            return self._eval_generic_rule(rule, events, flows, hosts)

    # ------------------------------------------------------------------------
    # Specific Rule Evaluators
    # ------------------------------------------------------------------------

    def _eval_net_tcp_001(
        self, rule: DetectionRule, flows: dict[Any, FlowAggregation]
    ) -> list[RuleMatchResult]:
        """NET-TCP-001: Repeated TCP Connection Attempts."""
        threshold = int(rule.threshold or 5)
        results: list[RuleMatchResult] = []

        for fl in flows.values():
            if fl.protocol == "TCP" and fl.syn_count >= threshold:
                syn_events = [e for e in fl.events if "SYN" in e.tcp_flags and "ACK" not in e.tcp_flags]
                confidence = (
                    AlertConfidence.HIGH
                    if fl.syn_count >= threshold * 3
                    else AlertConfidence.MEDIUM
                    if fl.syn_count >= threshold * 1.5
                    else AlertConfidence.LOW
                )

                time_bucket = int(fl.start_time // 300)
                dedup_key = f"{rule.rule_id}:{fl.source_ip}:{fl.destination_ip}:{fl.destination_port}:{time_bucket}"

                explanation = rule.explanation_template.format(
                    count=fl.syn_count,
                    source_ip=fl.source_ip or "Unknown",
                    destination_ip=fl.destination_ip or "Unknown",
                    destination_port=fl.destination_port or 0,
                )

                evidence: list[dict[str, Any]] = []
                for ev in syn_events[:15]:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.TCP_EVENT,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"TCP SYN packet #{ev.packet_number} directed at port {fl.destination_port}",
                            "evidence_data": {
                                "flags": ev.tcp_flags,
                                "source_port": ev.source_port,
                                "destination_port": ev.destination_port,
                            },
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"Repeated TCP Connection Attempts to Port {fl.destination_port} ({fl.syn_count} SYNs)",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=fl.source_ip,
                        destination_ip=fl.destination_ip,
                        source_port=None,
                        destination_port=fl.destination_port,
                        protocol="TCP",
                        first_seen=fl.start_time,
                        last_seen=fl.end_time,
                        packet_count=fl.syn_count,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_tcp_002(
        self, rule: DetectionRule, hosts: dict[str, HostProfile]
    ) -> list[RuleMatchResult]:
        """NET-TCP-002: SYN Pattern (High SYN Without Handshake Completion)."""
        max_ratio = float(rule.threshold or 0.2)
        results: list[RuleMatchResult] = []

        for hp in hosts.values():
            if hp.syn_count >= 5:
                ratio = hp.handshake_completed_count / hp.syn_count
                if ratio <= max_ratio:
                    confidence = AlertConfidence.HIGH if hp.syn_count >= 10 else AlertConfidence.MEDIUM
                    time_bucket = int((hp.events[0].timestamp if hp.events else 0) // 300)
                    dedup_key = f"{rule.rule_id}:{hp.ip}:any:0:{time_bucket}"

                    explanation = rule.explanation_template.format(
                        source_ip=hp.ip,
                        syn_count=hp.syn_count,
                        completed_count=hp.handshake_completed_count,
                    )

                    evidence: list[dict[str, Any]] = []
                    syn_evts = [e for e in hp.events if "SYN" in e.tcp_flags and "ACK" not in e.tcp_flags]
                    for ev in syn_evts[:10]:
                        evidence.append(
                            {
                                "evidence_type": EvidenceType.TCP_EVENT,
                                "packet_id": ev.packet_id,
                                "packet_number": ev.packet_number,
                                "timestamp": ev.timestamp,
                                "description": f"Uncompleted TCP SYN #{ev.packet_number} to {ev.destination_ip}:{ev.destination_port}",
                                "evidence_data": {
                                    "target_ip": ev.destination_ip,
                                    "target_port": ev.destination_port,
                                    "flags": ev.tcp_flags,
                                },
                            }
                        )

                    results.append(
                        RuleMatchResult(
                            rule=rule,
                            title=f"High SYN Ratio Without Handshake Completion ({hp.syn_count} SYNs, {hp.handshake_completed_count} Completed)",
                            category=rule.category,
                            severity=rule.severity,
                            confidence=confidence,
                            source_ip=hp.ip,
                            destination_ip=None,
                            source_port=None,
                            destination_port=None,
                            protocol="TCP",
                            first_seen=hp.events[0].timestamp if hp.events else None,
                            last_seen=hp.events[-1].timestamp if hp.events else None,
                            packet_count=hp.syn_count,
                            dedup_key=dedup_key,
                            explanation=explanation,
                            investigation_steps=self._parse_steps(rule.investigation_guide),
                            evidence_items=evidence,
                        )
                    )

        return results

    def _eval_net_tcp_003(
        self, rule: DetectionRule, flows: dict[Any, FlowAggregation]
    ) -> list[RuleMatchResult]:
        """NET-TCP-003: TCP Reset Spike."""
        threshold = int(rule.threshold or 5)
        results: list[RuleMatchResult] = []

        for fl in flows.values():
            if fl.rst_count >= threshold:
                confidence = AlertConfidence.HIGH if fl.rst_count >= threshold * 2 else AlertConfidence.MEDIUM
                time_bucket = int(fl.start_time // 300)
                dedup_key = f"{rule.rule_id}:{fl.source_ip}:{fl.destination_ip}:0:{time_bucket}"

                explanation = rule.explanation_template.format(
                    count=fl.rst_count,
                    source_ip=fl.source_ip or "Unknown",
                    destination_ip=fl.destination_ip or "Unknown",
                )

                rst_events = [e for e in fl.events if "RST" in e.tcp_flags]
                evidence: list[dict[str, Any]] = []
                for ev in rst_events[:10]:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.TCP_EVENT,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"TCP RST packet #{ev.packet_number} ({ev.source_port} -> {ev.destination_port})",
                            "evidence_data": {"flags": ev.tcp_flags, "info": ev.info},
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"TCP Reset Spike ({fl.rst_count} RST packets)",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=fl.source_ip,
                        destination_ip=fl.destination_ip,
                        source_port=None,
                        destination_port=fl.destination_port,
                        protocol="TCP",
                        first_seen=fl.start_time,
                        last_seen=fl.end_time,
                        packet_count=fl.rst_count,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_conn_001(
        self, rule: DetectionRule, flows: dict[Any, FlowAggregation]
    ) -> list[RuleMatchResult]:
        """NET-CONN-001: Repeated Connection Attempts (Same Destination)."""
        threshold = int(rule.threshold or 8)
        results: list[RuleMatchResult] = []

        # Aggregate flows between (source_ip, destination_ip)
        pair_counts: dict[tuple[str, str], list[FlowAggregation]] = {}
        for fl in flows.values():
            if fl.source_ip and fl.destination_ip:
                pair = (fl.source_ip, fl.destination_ip)
                if pair not in pair_counts:
                    pair_counts[pair] = []
                pair_counts[pair].append(fl)

        for (src, dst), fl_list in pair_counts.items():
            total_pkts = sum(f.packet_count for f in fl_list)
            if total_pkts >= threshold:
                start = min(f.start_time for f in fl_list)
                end = max(f.end_time for f in fl_list)
                confidence = AlertConfidence.MEDIUM if total_pkts >= threshold * 2 else AlertConfidence.LOW
                time_bucket = int(start // 300)
                dedup_key = f"{rule.rule_id}:{src}:{dst}:0:{time_bucket}"

                explanation = rule.explanation_template.format(
                    count=total_pkts,
                    source_ip=src,
                    destination_ip=dst,
                )

                all_evts = [e for f in fl_list for e in f.events]
                evidence: list[dict[str, Any]] = []
                for ev in all_evts[:10]:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.FLOW,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"Connection attempt #{ev.packet_number} {ev.protocol} to {dst}:{ev.destination_port}",
                            "evidence_data": {"protocol": ev.protocol, "port": ev.destination_port},
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"Repeated Connections to {dst} ({total_pkts} attempts)",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=src,
                        destination_ip=dst,
                        source_port=None,
                        destination_port=None,
                        protocol=fl_list[0].protocol,
                        first_seen=start,
                        last_seen=end,
                        packet_count=total_pkts,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_conn_002(
        self, rule: DetectionRule, flows: dict[Any, FlowAggregation]
    ) -> list[RuleMatchResult]:
        """NET-CONN-002: Repeated Connection Failures."""
        threshold = int(rule.threshold or 5)
        results: list[RuleMatchResult] = []

        for fl in flows.values():
            is_failed = (fl.syn_count >= threshold and not fl.handshake_complete) or (
                fl.rst_count >= threshold
            )
            if is_failed and fl.source_ip and fl.destination_ip:
                confidence = AlertConfidence.HIGH if fl.syn_count >= threshold * 2 else AlertConfidence.MEDIUM
                time_bucket = int(fl.start_time // 300)
                dedup_key = f"{rule.rule_id}:{fl.source_ip}:{fl.destination_ip}:{fl.destination_port}:{time_bucket}"

                explanation = rule.explanation_template.format(
                    count=fl.syn_count or fl.rst_count,
                    source_ip=fl.source_ip,
                    destination_ip=fl.destination_ip,
                )

                evidence: list[dict[str, Any]] = []
                for ev in fl.events[:10]:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.FLOW,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"Failed connection attempt #{ev.packet_number} {ev.protocol} {ev.info}",
                            "evidence_data": {"flags": ev.tcp_flags, "port": ev.destination_port},
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"Repeated Connection Failures towards {fl.destination_ip}:{fl.destination_port}",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=fl.source_ip,
                        destination_ip=fl.destination_ip,
                        source_port=None,
                        destination_port=fl.destination_port,
                        protocol=fl.protocol,
                        first_seen=fl.start_time,
                        last_seen=fl.end_time,
                        packet_count=fl.packet_count,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_dns_001(
        self, rule: DetectionRule, hosts: dict[str, HostProfile]
    ) -> list[RuleMatchResult]:
        """NET-DNS-001: DNS NXDOMAIN Spike."""
        threshold = int(rule.threshold or 4)
        results: list[RuleMatchResult] = []

        for hp in hosts.values():
            if len(hp.dns_nxdomains) >= threshold:
                count = len(hp.dns_nxdomains)
                confidence = AlertConfidence.HIGH if count >= threshold * 2 else AlertConfidence.MEDIUM
                first_seen = hp.dns_nxdomains[0].timestamp
                last_seen = hp.dns_nxdomains[-1].timestamp
                time_bucket = int(first_seen // 300)
                dedup_key = f"{rule.rule_id}:{hp.ip}:any:53:{time_bucket}"

                explanation = rule.explanation_template.format(count=count, source_ip=hp.ip)

                evidence: list[dict[str, Any]] = []
                for ev in hp.dns_nxdomains[:12]:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.DNS_EVENT,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"DNS NXDOMAIN response for query '{ev.dns_qname or 'unknown'}'",
                            "evidence_data": {
                                "domain": ev.dns_qname,
                                "rcode": ev.dns_rcode,
                                "qtype": ev.dns_qtype,
                            },
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"DNS NXDOMAIN Spike ({count} Non-Existent Domain responses)",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=hp.ip,
                        destination_ip=None,
                        source_port=None,
                        destination_port=53,
                        protocol="DNS",
                        first_seen=first_seen,
                        last_seen=last_seen,
                        packet_count=count,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_dns_002(
        self, rule: DetectionRule, hosts: dict[str, HostProfile]
    ) -> list[RuleMatchResult]:
        """NET-DNS-002: High DNS Query Frequency."""
        threshold = int(rule.threshold or 10)
        results: list[RuleMatchResult] = []

        for hp in hosts.values():
            if len(hp.dns_queries) >= threshold:
                count = len(hp.dns_queries)
                confidence = (
                    AlertConfidence.HIGH
                    if count >= threshold * 2.5
                    else AlertConfidence.MEDIUM
                    if count >= threshold * 1.5
                    else AlertConfidence.LOW
                )
                first_seen = hp.dns_queries[0].timestamp
                last_seen = hp.dns_queries[-1].timestamp
                time_bucket = int(first_seen // 300)
                dedup_key = f"{rule.rule_id}:{hp.ip}:any:53:{time_bucket}"

                explanation = rule.explanation_template.format(count=count, source_ip=hp.ip)

                evidence: list[dict[str, Any]] = []
                for ev in hp.dns_queries[:12]:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.DNS_EVENT,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"DNS Query #{ev.packet_number} for {ev.dns_qname or 'domain'}",
                            "evidence_data": {"qname": ev.dns_qname, "qtype": ev.dns_qtype},
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"High DNS Query Frequency ({count} Queries from {hp.ip})",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=hp.ip,
                        destination_ip=None,
                        source_port=None,
                        destination_port=53,
                        protocol="DNS",
                        first_seen=first_seen,
                        last_seen=last_seen,
                        packet_count=count,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_dns_003(
        self, rule: DetectionRule, hosts: dict[str, HostProfile]
    ) -> list[RuleMatchResult]:
        """NET-DNS-003: Unusual DNS Pattern (High Subdomain Diversity)."""
        threshold = int(rule.threshold or 4)
        results: list[RuleMatchResult] = []

        for hp in hosts.values():
            for base_dom, subdomains in hp.subdomains_by_base_domain.items():
                if len(subdomains) >= threshold:
                    count = len(subdomains)
                    confidence = AlertConfidence.HIGH if count >= threshold * 2 else AlertConfidence.MEDIUM
                    first_seen = hp.dns_queries[0].timestamp if hp.dns_queries else 0.0
                    last_seen = hp.dns_queries[-1].timestamp if hp.dns_queries else 0.0
                    time_bucket = int(first_seen // 300)
                    dedup_key = f"{rule.rule_id}:{hp.ip}:{base_dom}:53:{time_bucket}"

                    explanation = rule.explanation_template.format(
                        source_ip=hp.ip, count=count, base_domain=base_dom
                    )

                    matching_evts = [
                        e
                        for e in hp.dns_queries
                        if e.dns_qname and e.dns_qname.lower().endswith(base_dom)
                    ]
                    evidence: list[dict[str, Any]] = []
                    for ev in matching_evts[:10]:
                        evidence.append(
                            {
                                "evidence_type": EvidenceType.DNS_EVENT,
                                "packet_id": ev.packet_id,
                                "packet_number": ev.packet_number,
                                "timestamp": ev.timestamp,
                                "description": f"Query #{ev.packet_number} for subdomain '{ev.dns_qname}'",
                                "evidence_data": {"full_domain": ev.dns_qname, "base_domain": base_dom},
                            }
                        )

                    results.append(
                        RuleMatchResult(
                            rule=rule,
                            title=f"High Subdomain Diversity under {base_dom} ({count} unique subdomains)",
                            category=rule.category,
                            severity=rule.severity,
                            confidence=confidence,
                            source_ip=hp.ip,
                            destination_ip=None,
                            source_port=None,
                            destination_port=53,
                            protocol="DNS",
                            first_seen=first_seen,
                            last_seen=last_seen,
                            packet_count=len(matching_evts),
                            dedup_key=dedup_key,
                            explanation=explanation,
                            investigation_steps=self._parse_steps(rule.investigation_guide),
                            evidence_items=evidence,
                        )
                    )

        return results

    def _eval_net_arp_001(
        self, rule: DetectionRule, hosts: dict[str, HostProfile]
    ) -> list[RuleMatchResult]:
        """NET-ARP-001: ARP Mapping Change (IP with Multiple MACs)."""
        results: list[RuleMatchResult] = []

        for hp in hosts.values():
            if len(hp.arp_macs) >= 2:
                mac_list = ", ".join(sorted(hp.arp_macs))
                first_seen = hp.events[0].timestamp if hp.events else 0.0
                last_seen = hp.events[-1].timestamp if hp.events else 0.0
                time_bucket = int(first_seen // 300)
                dedup_key = f"{rule.rule_id}:{hp.ip}:any:0:{time_bucket}"

                explanation = rule.explanation_template.format(source_ip=hp.ip, mac_list=mac_list)

                evidence: list[dict[str, Any]] = []
                for ev in hp.events:
                    if ev.protocol == "ARP" or ev.source_mac:
                        evidence.append(
                            {
                                "evidence_type": EvidenceType.ARP_EVENT,
                                "packet_id": ev.packet_id,
                                "packet_number": ev.packet_number,
                                "timestamp": ev.timestamp,
                                "description": f"ARP packet #{ev.packet_number} claiming IP {hp.ip} with MAC {ev.source_mac}",
                                "evidence_data": {
                                    "claimed_ip": hp.ip,
                                    "hardware_mac": ev.source_mac,
                                    "info": ev.info,
                                },
                            }
                        )
                        if len(evidence) >= 8:
                            break

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"Conflicting ARP Hardware Mapping for {hp.ip} ({len(hp.arp_macs)} MACs)",
                        category=rule.category,
                        severity=AlertSeverity.HIGH,
                        confidence=AlertConfidence.HIGH,
                        source_ip=hp.ip,
                        destination_ip=None,
                        source_port=None,
                        destination_port=None,
                        protocol="ARP",
                        first_seen=first_seen,
                        last_seen=last_seen,
                        packet_count=len(evidence),
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_icmp_001(
        self, rule: DetectionRule, hosts: dict[str, HostProfile]
    ) -> list[RuleMatchResult]:
        """NET-ICMP-001: ICMP Traffic Burst."""
        threshold = int(rule.threshold or 8)
        results: list[RuleMatchResult] = []

        for hp in hosts.values():
            if len(hp.icmp_requests) >= threshold:
                count = len(hp.icmp_requests)
                confidence = AlertConfidence.MEDIUM if count >= threshold * 2 else AlertConfidence.LOW
                first_seen = hp.icmp_requests[0].timestamp
                last_seen = hp.icmp_requests[-1].timestamp
                time_bucket = int(first_seen // 300)
                dedup_key = f"{rule.rule_id}:{hp.ip}:any:0:{time_bucket}"

                explanation = rule.explanation_template.format(count=count, source_ip=hp.ip)

                evidence: list[dict[str, Any]] = []
                for ev in hp.icmp_requests[:10]:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.ICMP_EVENT,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"ICMP Echo Request #{ev.packet_number} towards {ev.destination_ip}",
                            "evidence_data": {
                                "type": ev.icmp_type,
                                "code": ev.icmp_code,
                                "destination_ip": ev.destination_ip,
                            },
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"ICMP Echo Request Burst ({count} pings from {hp.ip})",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=hp.ip,
                        destination_ip=None,
                        source_port=None,
                        destination_port=None,
                        protocol="ICMP",
                        first_seen=first_seen,
                        last_seen=last_seen,
                        packet_count=count,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_port_001(
        self, rule: DetectionRule, flows: dict[Any, FlowAggregation]
    ) -> list[RuleMatchResult]:
        """NET-PORT-001: Unusual Port Usage."""
        noteworthy = {4444, 1337, 6667, 31337, 8888, 9999, 5555}
        try:
            conds = json.loads(rule.conditions) if isinstance(rule.conditions, str) else rule.conditions
            if isinstance(conds, dict) and "noteworthy_ports" in conds:
                noteworthy = set(conds["noteworthy_ports"])
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

        results: list[RuleMatchResult] = []

        for fl in flows.values():
            if fl.destination_port in noteworthy and fl.packet_count >= 1:
                confidence = (
                    AlertConfidence.HIGH
                    if fl.destination_port in {4444, 31337, 1337}
                    else AlertConfidence.MEDIUM
                )
                time_bucket = int(fl.start_time // 300)
                dedup_key = f"{rule.rule_id}:{fl.source_ip}:{fl.destination_ip}:{fl.destination_port}:{time_bucket}"

                explanation = rule.explanation_template.format(
                    source_ip=fl.source_ip or "Unknown",
                    destination_ip=fl.destination_ip or "Unknown",
                    destination_port=fl.destination_port,
                )

                evidence: list[dict[str, Any]] = []
                for ev in fl.events[:8]:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.PACKET,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"Packet #{ev.packet_number} {ev.protocol} to noteworthy port {fl.destination_port}",
                            "evidence_data": {
                                "source_port": ev.source_port,
                                "destination_port": ev.destination_port,
                                "protocol": ev.protocol,
                            },
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"Noteworthy Non-Standard Port Communication (Port {fl.destination_port})",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=fl.source_ip,
                        destination_ip=fl.destination_ip,
                        source_port=None,
                        destination_port=fl.destination_port,
                        protocol=fl.protocol,
                        first_seen=fl.start_time,
                        last_seen=fl.end_time,
                        packet_count=fl.packet_count,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_traffic_001(
        self, rule: DetectionRule, flows: dict[Any, FlowAggregation]
    ) -> list[RuleMatchResult]:
        """NET-TRAFFIC-001: Large Traffic Volume Burst."""
        threshold = int(rule.threshold or 30)
        results: list[RuleMatchResult] = []

        for fl in flows.values():
            if fl.packet_count >= threshold and fl.source_ip and fl.destination_ip:
                confidence = AlertConfidence.HIGH if fl.packet_count >= threshold * 3 else AlertConfidence.LOW
                time_bucket = int(fl.start_time // 300)
                dedup_key = f"{rule.rule_id}:{fl.source_ip}:{fl.destination_ip}:{fl.destination_port}:{time_bucket}"

                explanation = rule.explanation_template.format(
                    count=fl.packet_count,
                    source_ip=fl.source_ip,
                    destination_ip=fl.destination_ip,
                )

                evidence: list[dict[str, Any]] = []
                # Include first 3, middle 2, and last 3 packets
                sample_evts = fl.events[:3] + fl.events[len(fl.events) // 2 : len(fl.events) // 2 + 2] + fl.events[-3:]
                for ev in sample_evts:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.STATISTICAL_OBSERVATION,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"Flow packet #{ev.packet_number} ({ev.length} bytes)",
                            "evidence_data": {
                                "byte_count": fl.byte_count,
                                "duration_seconds": fl.duration,
                            },
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"Large Traffic Volume Burst ({fl.packet_count} packets to {fl.destination_ip})",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=fl.source_ip,
                        destination_ip=fl.destination_ip,
                        source_port=None,
                        destination_port=fl.destination_port,
                        protocol=fl.protocol,
                        first_seen=fl.start_time,
                        last_seen=fl.end_time,
                        packet_count=fl.packet_count,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_traffic_002(
        self, rule: DetectionRule, flows: dict[Any, FlowAggregation]
    ) -> list[RuleMatchResult]:
        """NET-TRAFFIC-002: Periodic Network Communication Pattern."""
        max_rsd = float(rule.threshold or 0.25)
        results: list[RuleMatchResult] = []

        for fl in flows.values():
            if (
                fl.packet_count >= 4
                and fl.duration >= 2.0
                and fl.relative_std_dev <= max_rsd
                and fl.source_ip
                and fl.destination_ip
            ):
                confidence = AlertConfidence.HIGH if fl.relative_std_dev < 0.1 else AlertConfidence.MEDIUM
                time_bucket = int(fl.start_time // 300)
                dedup_key = f"{rule.rule_id}:{fl.source_ip}:{fl.destination_ip}:{fl.destination_port}:{time_bucket}"

                explanation = rule.explanation_template.format(
                    count=fl.packet_count,
                    source_ip=fl.source_ip,
                    destination_ip=fl.destination_ip,
                )

                evidence: list[dict[str, Any]] = []
                for ev in fl.events[:8]:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.STATISTICAL_OBSERVATION,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"Periodic packet #{ev.packet_number} (mean interval ~ {fl.mean_inter_arrival:.2f}s)",
                            "evidence_data": {
                                "mean_interval_sec": round(fl.mean_inter_arrival, 3),
                                "relative_std_dev": round(fl.relative_std_dev, 3),
                            },
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"Periodic Communication Pattern ({fl.packet_count} regular packets, ~{fl.mean_inter_arrival:.1f}s period)",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=fl.source_ip,
                        destination_ip=fl.destination_ip,
                        source_port=None,
                        destination_port=fl.destination_port,
                        protocol=fl.protocol,
                        first_seen=fl.start_time,
                        last_seen=fl.end_time,
                        packet_count=fl.packet_count,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_http_001(
        self,
        rule: DetectionRule,
        hosts: dict[str, HostProfile],
        events: list[NormalizedEvent],
    ) -> list[RuleMatchResult]:
        """NET-HTTP-001: Repeated HTTP Error Responses."""
        threshold = int(rule.threshold or 4)
        error_evts = [
            e
            for e in events
            if (e.http_status_code and e.http_status_code >= 400)
            or (" 404 " in e.info or " 403 " in e.info or " 500 " in e.info)
        ]

        if len(error_evts) < threshold:
            return []

        # Group by (source_ip, destination_ip)
        server_client_pairs: dict[tuple[str | None, str | None], list[NormalizedEvent]] = {}
        for ev in error_evts:
            pair = (ev.source_ip, ev.destination_ip)
            if pair not in server_client_pairs:
                server_client_pairs[pair] = []
            server_client_pairs[pair].append(ev)

        results: list[RuleMatchResult] = []
        for (src, dst), evts in server_client_pairs.items():
            if len(evts) >= threshold:
                count = len(evts)
                confidence = AlertConfidence.HIGH if count >= threshold * 2 else AlertConfidence.MEDIUM
                first_seen = evts[0].timestamp
                last_seen = evts[-1].timestamp
                time_bucket = int(first_seen // 300)
                dedup_key = f"{rule.rule_id}:{src}:{dst}:80:{time_bucket}"

                explanation = rule.explanation_template.format(
                    count=count,
                    source_ip=src or "Web Server",
                    destination_ip=dst or "Client",
                )

                evidence: list[dict[str, Any]] = []
                for ev in evts[:10]:
                    evidence.append(
                        {
                            "evidence_type": EvidenceType.HTTP_EVENT,
                            "packet_id": ev.packet_id,
                            "packet_number": ev.packet_number,
                            "timestamp": ev.timestamp,
                            "description": f"HTTP Error #{ev.packet_number}: {ev.info}",
                            "evidence_data": {
                                "status_code": ev.http_status_code,
                                "uri": ev.http_uri,
                            },
                        }
                    )

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"Repeated HTTP Error Responses ({count} Errors to {dst})",
                        category=rule.category,
                        severity=rule.severity,
                        confidence=confidence,
                        source_ip=src,
                        destination_ip=dst,
                        source_port=None,
                        destination_port=80,
                        protocol="HTTP",
                        first_seen=first_seen,
                        last_seen=last_seen,
                        packet_count=count,
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_net_recon_001(
        self, rule: DetectionRule, hosts: dict[str, HostProfile]
    ) -> list[RuleMatchResult]:
        """NET-RECON-001: Multi-Destination Connection Pattern."""
        threshold = int(rule.threshold or 4)
        results: list[RuleMatchResult] = []

        for hp in hosts.values():
            if len(hp.distinct_destinations) >= threshold:
                dst_count = len(hp.distinct_destinations)
                confidence = AlertConfidence.HIGH if dst_count >= threshold * 2 else AlertConfidence.MEDIUM
                first_seen = hp.events[0].timestamp if hp.events else 0.0
                last_seen = hp.events[-1].timestamp if hp.events else 0.0
                time_bucket = int(first_seen // 300)
                dedup_key = f"{rule.rule_id}:{hp.ip}:multi:0:{time_bucket}"

                explanation = rule.explanation_template.format(
                    source_ip=hp.ip,
                    dst_count=dst_count,
                )

                evidence: list[dict[str, Any]] = []
                seen_targets: set[str] = set()
                for ev in hp.events:
                    if ev.destination_ip and ev.destination_ip not in seen_targets:
                        seen_targets.add(ev.destination_ip)
                        evidence.append(
                            {
                                "evidence_type": EvidenceType.ENDPOINT,
                                "packet_id": ev.packet_id,
                                "packet_number": ev.packet_number,
                                "timestamp": ev.timestamp,
                                "description": f"Outbound probe #{ev.packet_number} to target {ev.destination_ip}:{ev.destination_port} ({ev.protocol})",
                                "evidence_data": {
                                    "target_ip": ev.destination_ip,
                                    "target_port": ev.destination_port,
                                    "protocol": ev.protocol,
                                },
                            }
                        )
                        if len(evidence) >= 12:
                            break

                results.append(
                    RuleMatchResult(
                        rule=rule,
                        title=f"Multi-Destination Probe Pattern ({dst_count} Distinct Targets)",
                        category=rule.category,
                        severity=AlertSeverity.HIGH,
                        confidence=confidence,
                        source_ip=hp.ip,
                        destination_ip=None,
                        source_port=None,
                        destination_port=None,
                        protocol="IP",
                        first_seen=first_seen,
                        last_seen=last_seen,
                        packet_count=len(hp.events),
                        dedup_key=dedup_key,
                        explanation=explanation,
                        investigation_steps=self._parse_steps(rule.investigation_guide),
                        evidence_items=evidence,
                    )
                )

        return results

    def _eval_generic_rule(
        self,
        rule: DetectionRule,
        events: list[NormalizedEvent],
        flows: dict[Any, FlowAggregation],
        hosts: dict[str, HostProfile],
    ) -> list[RuleMatchResult]:
        """Generic fallback evaluator for custom rules."""
        # Simple protocol threshold matching
        threshold = int(rule.threshold or 5)
        results: list[RuleMatchResult] = []
        matching_evts = [e for e in events if e.protocol.upper() == rule.category.upper()]
        if len(matching_evts) >= threshold:
            ev0 = matching_evts[0]
            explanation = rule.explanation_template
            results.append(
                RuleMatchResult(
                    rule=rule,
                    title=f"{rule.name} ({len(matching_evts)} matching packets)",
                    category=rule.category,
                    severity=rule.severity,
                    confidence=rule.confidence_default,
                    source_ip=ev0.source_ip,
                    destination_ip=ev0.destination_ip,
                    source_port=ev0.source_port,
                    destination_port=ev0.destination_port,
                    protocol=rule.category,
                    first_seen=matching_evts[0].timestamp,
                    last_seen=matching_evts[-1].timestamp,
                    packet_count=len(matching_evts),
                    dedup_key=f"{rule.rule_id}:{ev0.source_ip}:{ev0.destination_ip}:0",
                    explanation=explanation,
                    investigation_steps=self._parse_steps(rule.investigation_guide),
                    evidence_items=[
                        {
                            "evidence_type": EvidenceType.PACKET,
                            "packet_id": e.packet_id,
                            "packet_number": e.packet_number,
                            "timestamp": e.timestamp,
                            "description": f"Packet #{e.packet_number}: {e.info}",
                            "evidence_data": {},
                        }
                        for e in matching_evts[:10]
                    ],
                )
            )
        return results

    # ------------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------------

    def _parse_steps(self, guide_text: str) -> list[str]:
        """Parse structured investigation guide lines or JSON list into string items."""
        if not guide_text:
            return []
        try:
            parsed = json.loads(guide_text)
            if isinstance(parsed, list):
                return [str(s).strip() for s in parsed if s]
        except (json.JSONDecodeError, TypeError, ValueError):
            pass

        # Split lines and remove leading numbers (1. / - )
        lines = guide_text.strip().split("\n")
        cleaned_steps = []
        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue
            if trimmed[0].isdigit() and "." in trimmed[:4]:
                trimmed = trimmed.split(".", 1)[1].strip()
            elif trimmed.startswith(("- ", "* ")):
                trimmed = trimmed[2:].strip()
            if trimmed:
                cleaned_steps.append(trimmed)
        return cleaned_steps

    def _deduplicate_matches(self, matches: list[RuleMatchResult]) -> list[RuleMatchResult]:
        """Merge identical dedup_keys into single alerts with consolidated evidence."""
        by_key: dict[str, RuleMatchResult] = {}
        for m in matches:
            if m.dedup_key not in by_key:
                by_key[m.dedup_key] = m
            else:
                existing = by_key[m.dedup_key]
                existing.packet_count += m.packet_count
                if m.last_seen and (not existing.last_seen or m.last_seen > existing.last_seen):
                    existing.last_seen = m.last_seen
                # Combine evidence items without duplicating packet numbers
                seen_pkt_nums = {ev.get("packet_number") for ev in existing.evidence_items}
                for new_ev in m.evidence_items:
                    if new_ev.get("packet_number") not in seen_pkt_nums:
                        existing.evidence_items.append(new_ev)
                        seen_pkt_nums.add(new_ev.get("packet_number"))

        return list(by_key.values())
