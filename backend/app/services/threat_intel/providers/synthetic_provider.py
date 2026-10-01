"""Synthetic Threat Intelligence Provider for NexoraNet Educational Labs.

Serves strictly safe, deterministic, offline intelligence data.
All indicators are synthetic or from documentation RFC ranges (RFC 5737, RFC 3849).
Zero external network calls.
"""

from datetime import datetime, timezone
from typing import Any, ClassVar

from app.models.enums import (
    IndicatorClassification,
    IndicatorType,
    SourceReliability,
    ThreatIntelConfidence,
)
from app.services.threat_intel.providers.base import ProviderResult, ThreatIntelProvider


class SyntheticThreatIntelProvider(ThreatIntelProvider):
    """Primary offline educational provider."""

    PROVIDER_NAME: str = "NexoraNet Synthetic Threat Intelligence"

    # Static synthetic intelligence database
    SYNTHETIC_DATA: ClassVar[dict[str, dict[str, Any]]] = {
        # --- IP Addresses ---
        "198.51.100.25": {
            "indicator_type": IndicatorType.IP_ADDRESS.value,
            "classification": IndicatorClassification.SUSPICIOUS.value,
            "confidence": ThreatIntelConfidence.MEDIUM.value,
            "severity": "HIGH",
            "categories": ["Port Reconnaissance", "Scanning"],
            "tags": ["scanner", "recon", "training", "tcp-syn"],
            "mitre_attack_id": "T1046",
            "mitre_technique": "Network Service Discovery",
            "explanation": "Indicator appears in the synthetic training dataset associated with repeated connection attempts and port sweeps.",
        },
        "203.0.113.10": {
            "indicator_type": IndicatorType.IP_ADDRESS.value,
            "classification": IndicatorClassification.MALICIOUS.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "CRITICAL",
            "categories": ["Phishing", "Credential Harvesting"],
            "tags": ["phishing", "credential-harvesting", "training", "c2"],
            "mitre_attack_id": "T1566",
            "mitre_technique": "Phishing",
            "explanation": "Synthetic training dataset flags this host as a simulated credential harvesting server targeting employee portals.",
        },
        "192.0.2.50": {
            "indicator_type": IndicatorType.IP_ADDRESS.value,
            "classification": IndicatorClassification.SUSPICIOUS.value,
            "confidence": ThreatIntelConfidence.MEDIUM.value,
            "severity": "MEDIUM",
            "categories": ["DNS Anomaly", "Fast-Flux Simulation"],
            "tags": ["dns", "tunneling", "fast-flux", "training"],
            "mitre_attack_id": "T1071.004",
            "mitre_technique": "Application Layer Protocol: DNS",
            "explanation": "Associated with high-entropy DNS resolution bursts and frequent NXDOMAIN response patterns in the DNS lab.",
        },
        "192.168.1.1": {
            "indicator_type": IndicatorType.IP_ADDRESS.value,
            "classification": IndicatorClassification.BENIGN.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "INFO",
            "categories": ["Local Gateway", "Infrastructure"],
            "tags": ["gateway", "lan", "benign", "training"],
            "explanation": "Classified as benign internal default gateway router in local training subnets.",
        },
        "10.0.0.1": {
            "indicator_type": IndicatorType.IP_ADDRESS.value,
            "classification": IndicatorClassification.BENIGN.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "INFO",
            "categories": ["Internal Server", "DMZ"],
            "tags": ["server", "dmz", "benign", "training"],
            "explanation": "Authorized internal corporate web server in the training DMZ.",
        },
        "172.16.0.5": {
            "indicator_type": IndicatorType.IP_ADDRESS.value,
            "classification": IndicatorClassification.BENIGN.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "LOW",
            "categories": ["Monitoring Agent", "Vulnerability Scanner"],
            "tags": ["agent", "monitoring", "false-positive", "training"],
            "explanation": "Internal network health monitoring scanner that routinely triggers port scan threshold rules (known false positive).",
        },

        # --- Domains ---
        "scanner.training.test": {
            "indicator_type": IndicatorType.DOMAIN.value,
            "classification": IndicatorClassification.SUSPICIOUS.value,
            "confidence": ThreatIntelConfidence.MEDIUM.value,
            "severity": "HIGH",
            "categories": ["Reconnaissance Infrastructure"],
            "tags": ["scanner", "recon", "training"],
            "mitre_attack_id": "T1046",
            "mitre_technique": "Network Service Discovery",
            "explanation": "Synthetic training domain associated with automated port sweeps across training host subnets.",
        },
        "dns-anomaly.training.test": {
            "indicator_type": IndicatorType.DOMAIN.value,
            "classification": IndicatorClassification.SUSPICIOUS.value,
            "confidence": ThreatIntelConfidence.MEDIUM.value,
            "severity": "MEDIUM",
            "categories": ["DNS Tunneling Simulation"],
            "tags": ["dns", "tunneling", "training"],
            "mitre_attack_id": "T1071.004",
            "mitre_technique": "Application Layer Protocol: DNS",
            "explanation": "Domain exhibiting high Shannon entropy subdomains and elevated NXDOMAIN query rates in synthetic DNS captures.",
        },
        "phishing.training.test": {
            "indicator_type": IndicatorType.DOMAIN.value,
            "classification": IndicatorClassification.MALICIOUS.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "CRITICAL",
            "categories": ["Phishing Simulation"],
            "tags": ["phishing", "credential-harvesting", "training"],
            "mitre_attack_id": "T1566.002",
            "mitre_technique": "Phishing: Spearphishing Link",
            "explanation": "Synthetic phishing domain simulated for junior analyst triage exercises.",
        },
        "benign.training.test": {
            "indicator_type": IndicatorType.DOMAIN.value,
            "classification": IndicatorClassification.BENIGN.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "INFO",
            "categories": ["Legitimate Training Infrastructure"],
            "tags": ["benign", "internal", "training"],
            "explanation": "Standard benign educational web application domain.",
        },
        "portal.training.test": {
            "indicator_type": IndicatorType.DOMAIN.value,
            "classification": IndicatorClassification.BENIGN.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "INFO",
            "categories": ["Corporate Portal"],
            "tags": ["portal", "intranet", "benign", "training"],
            "explanation": "Simulated intranet student portal with routine HTTP and HTTPS traffic.",
        },

        # --- Hashes (Synthetic SHA-256 strings) ---
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855": {
            "indicator_type": IndicatorType.FILE_HASH.value,
            "classification": IndicatorClassification.BENIGN.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "INFO",
            "categories": ["Zero-Byte File Hash"],
            "tags": ["hash", "empty-file", "benign", "training"],
            "explanation": "Standard cryptographic SHA-256 hash of an empty file (0 bytes). Common benign artifact.",
        },
        "a1b2c3d4e5f60718293a4b5c6d7e8f90123456789abcdef0123456789abcdef0": {
            "indicator_type": IndicatorType.FILE_HASH.value,
            "classification": IndicatorClassification.SUSPICIOUS.value,
            "confidence": ThreatIntelConfidence.MEDIUM.value,
            "severity": "HIGH",
            "categories": ["Dropper Simulation"],
            "tags": ["dropper", "synthetic-artifact", "training"],
            "mitre_attack_id": "T1059",
            "mitre_technique": "Command and Scripting Interpreter",
            "explanation": "Synthetic training hash representing a staging payload analyzed during defensive forensics exercises.",
        },
        "f0e1d2c3b4a5968778695a4b3c2d1e0ffeeddccbbaa99887766554433221100f": {
            "indicator_type": IndicatorType.FILE_HASH.value,
            "classification": IndicatorClassification.MALICIOUS.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "CRITICAL",
            "categories": ["Trojan Telemetry"],
            "tags": ["trojan", "c2", "training"],
            "mitre_attack_id": "T1204",
            "mitre_technique": "User Execution",
            "explanation": "Synthetic training hash representing an educational trojan payload.",
        },

        # --- URLs ---
        "http://phishing.training.test/login.php": {
            "indicator_type": IndicatorType.URL.value,
            "classification": IndicatorClassification.MALICIOUS.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "CRITICAL",
            "categories": ["Phishing Landing Page"],
            "tags": ["phishing", "url", "training"],
            "mitre_attack_id": "T1566",
            "mitre_technique": "Phishing",
            "explanation": "Simulated credential harvesting URL designed for threat intelligence investigation exercises.",
        },
        "http://benign.training.test/index.html": {
            "indicator_type": IndicatorType.URL.value,
            "classification": IndicatorClassification.BENIGN.value,
            "confidence": ThreatIntelConfidence.HIGH.value,
            "severity": "INFO",
            "categories": ["Documentation"],
            "tags": ["benign", "url", "training"],
            "explanation": "Legitimate documentation endpoint for local training labs.",
        },
        "http://198.51.100.25:8080/probe": {
            "indicator_type": IndicatorType.URL.value,
            "classification": IndicatorClassification.SUSPICIOUS.value,
            "confidence": ThreatIntelConfidence.MEDIUM.value,
            "severity": "HIGH",
            "categories": ["Reconnaissance Probe"],
            "tags": ["probe", "scanner", "url", "training"],
            "mitre_attack_id": "T1595",
            "mitre_technique": "Active Scanning",
            "explanation": "Synthetic URL observed during multi-port vertical and horizontal scanning exercises.",
        },
    }

    def get_provider_name(self) -> str:
        return self.PROVIDER_NAME

    def lookup_indicator(
        self,
        indicator_type: IndicatorType | str,
        normalized_value: str,
    ) -> ProviderResult | None:
        """Query synthetic knowledge base for normalized indicator."""
        key = normalized_value.strip().lower()

        record = self.SYNTHETIC_DATA.get(key)
        if not record:
            return None

        return ProviderResult(
            provider=self.PROVIDER_NAME,
            indicator_type=record["indicator_type"],
            indicator_value=normalized_value,
            normalized_value=key,
            classification=record.get("classification", IndicatorClassification.UNKNOWN.value),
            confidence=record.get("confidence", ThreatIntelConfidence.MEDIUM.value),
            severity=record.get("severity", "INFO"),
            source_reliability=SourceReliability.HIGH.value,
            categories=record.get("categories", []),
            tags=record.get("tags", []),
            mitre_attack_id=record.get("mitre_attack_id"),
            mitre_technique=record.get("mitre_technique"),
            references=["NexoraNet Offline Knowledge Base", "RFC 5737 / RFC 3849 Documentation Prefix"],
            explanation=record.get("explanation", "Synthetic training intelligence entry."),
            retrieved_at=datetime.now(timezone.utc),
            raw_metadata={"source": "NexoraNet Synthetic Feed", "synthetic": True},
            is_synthetic=True,
        )


synthetic_threat_intel_provider = SyntheticThreatIntelProvider()
