"""Abstract Base Class for Threat Intelligence Providers.

Step 13 implements an offline, modular threat intelligence architecture.
External providers remain disabled by default, ensuring offline resilience and strict safety.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.models.enums import (
    IndicatorClassification,
    IndicatorType,
    SourceReliability,
    ThreatIntelConfidence,
)


@dataclass
class ProviderResult:
    """Standardized intelligence result returned by a threat intel provider."""

    provider: str
    indicator_type: str
    indicator_value: str
    normalized_value: str
    classification: str = IndicatorClassification.UNKNOWN.value
    confidence: str = ThreatIntelConfidence.MEDIUM.value
    severity: str = "INFO"
    source_reliability: str = SourceReliability.HIGH.value
    categories: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    mitre_attack_id: str | None = None
    mitre_technique: str | None = None
    references: list[str] = field(default_factory=list)
    explanation: str = "No intelligence assessment available."
    retrieved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    raw_metadata: dict[str, Any] = field(default_factory=dict)
    is_synthetic: bool = True


class ThreatIntelProvider(ABC):
    """Abstract interface for threat intelligence feeds and lookup providers."""

    @abstractmethod
    def get_provider_name(self) -> str:
        """Return the unique human-readable name of the provider."""
        ...

    @abstractmethod
    def lookup_indicator(
        self,
        indicator_type: IndicatorType | str,
        normalized_value: str,
    ) -> ProviderResult | None:
        """Query reputation and threat context for an indicator."""
        ...

    def lookup_ip(self, ip: str) -> ProviderResult | None:
        return self.lookup_indicator(IndicatorType.IP_ADDRESS, ip)

    def lookup_domain(self, domain: str) -> ProviderResult | None:
        return self.lookup_indicator(IndicatorType.DOMAIN, domain)

    def lookup_url(self, url: str) -> ProviderResult | None:
        return self.lookup_indicator(IndicatorType.URL, url)

    def lookup_hash(self, hash_val: str) -> ProviderResult | None:
        return self.lookup_indicator(IndicatorType.FILE_HASH, hash_val)
