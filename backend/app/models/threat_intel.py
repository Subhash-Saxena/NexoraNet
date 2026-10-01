"""Database models for Step 13 Threat Intelligence & IOC Investigation."""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.db.base import Base


class ThreatIntelSource(Base):
    """Threat intelligence origin and collection source."""

    __tablename__ = "threat_intel_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    source_type = Column(String(50), nullable=False, default="SYNTHETIC")
    description = Column(Text, nullable=True)
    reliability = Column(String(50), nullable=False, default="HIGH")
    enabled = Column(Boolean, nullable=False, default=True)
    is_synthetic = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    indicators = relationship("Indicator", back_populates="source", cascade="all, delete-orphan")


class Indicator(Base):
    """Indicator of Compromise (IOC) or Indicator of Interest."""

    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(String(50), unique=True, nullable=False, index=True)
    indicator_type = Column(String(50), nullable=False, index=True)
    hash_type = Column(String(20), nullable=True)
    value = Column(Text, nullable=False)
    normalized_value = Column(String(512), nullable=False, index=True)
    display_value = Column(Text, nullable=False)
    source_id = Column(Integer, ForeignKey("threat_intel_sources.id", ondelete="SET NULL"), nullable=True)
    source_name = Column(String(100), nullable=False, default="NexoraNet Synthetic Threat Intelligence")
    classification = Column(String(50), nullable=False, default="UNKNOWN", index=True)
    confidence = Column(String(50), nullable=False, default="MEDIUM")
    severity = Column(String(50), nullable=False, default="INFO")
    status = Column(String(50), nullable=False, default="ACTIVE", index=True)
    false_positive_reason = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(Text, nullable=True)  # JSON-encoded array of tag strings
    mitre_attack_id = Column(String(50), nullable=True)
    mitre_technique = Column(String(150), nullable=True)
    is_synthetic = Column(Boolean, nullable=False, default=True)
    first_seen = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    source = relationship("ThreatIntelSource", back_populates="indicators")
    observations = relationship("IndicatorObservation", back_populates="indicator", cascade="all, delete-orphan")
    outgoing_relationships = relationship(
        "IndicatorRelationship",
        foreign_keys="IndicatorRelationship.source_indicator_id",
        back_populates="source_indicator",
        cascade="all, delete-orphan",
    )
    incoming_relationships = relationship(
        "IndicatorRelationship",
        foreign_keys="IndicatorRelationship.target_indicator_id",
        back_populates="target_indicator",
        cascade="all, delete-orphan",
    )
    timeline_events = relationship("IndicatorTimeline", back_populates="indicator", cascade="all, delete-orphan")
    notes = relationship("IndicatorNote", back_populates="indicator", cascade="all, delete-orphan")
    watchlist_entries = relationship("WatchlistItem", back_populates="indicator", cascade="all, delete-orphan")


class IndicatorRelationship(Base):
    """Structural correlation between two threat indicators."""

    __tablename__ = "indicator_relationships"

    id = Column(Integer, primary_key=True, index=True)
    source_indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False, index=True)
    target_indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False, index=True)
    relationship_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    confidence = Column(String(50), nullable=False, default="MEDIUM")
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    source_indicator = relationship("Indicator", foreign_keys=[source_indicator_id], back_populates="outgoing_relationships")
    target_indicator = relationship("Indicator", foreign_keys=[target_indicator_id], back_populates="incoming_relationships")


class IndicatorObservation(Base):
    """Observation telemetry linking an indicator to network packets, alerts, and investigations."""

    __tablename__ = "indicator_observations"

    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False, index=True)
    capture_id = Column(Integer, ForeignKey("captures.id", ondelete="SET NULL"), nullable=True, index=True)
    packet_number = Column(Integer, nullable=True)
    alert_id = Column(Integer, ForeignKey("detection_alerts.id", ondelete="SET NULL"), nullable=True, index=True)
    investigation_id = Column(Integer, ForeignKey("investigations.id", ondelete="SET NULL"), nullable=True, index=True)
    case_id = Column(Integer, ForeignKey("cases.id", ondelete="SET NULL"), nullable=True, index=True)
    observation_type = Column(String(50), nullable=False)
    context_data = Column(Text, nullable=True)  # JSON-encoded contextual telemetry details
    observed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    indicator = relationship("Indicator", back_populates="observations")
    capture = relationship("Capture")
    alert = relationship("DetectionAlert")
    investigation = relationship("Investigation")
    case = relationship("Case")


class IndicatorTimeline(Base):
    """Chronological event in the lifecycle of an indicator."""

    __tablename__ = "indicator_timelines"

    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    actor_name = Column(String(100), nullable=False, default="System")
    event_timestamp = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    indicator = relationship("Indicator", back_populates="timeline_events")


class IndicatorNote(Base):
    """Analyst note attached to an indicator."""

    __tablename__ = "indicator_notes"

    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    author_name = Column(String(100), nullable=False, default="SOC Analyst")
    note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    indicator = relationship("Indicator", back_populates="notes")
    user = relationship("User")


class WatchlistItem(Base):
    """Student watchlist entry for monitoring an indicator."""

    __tablename__ = "indicator_watchlists"

    id = Column(Integer, primary_key=True, index=True)
    indicator_id = Column(Integer, ForeignKey("indicators.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reason = Column(Text, nullable=False)
    added_by = Column(String(100), nullable=False, default="SOC Analyst")
    expires_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    indicator = relationship("Indicator", back_populates="watchlist_entries")
    user = relationship("User")


class ThreatIntelChallenge(Base):
    """Educational threat intelligence scenario challenge."""

    __tablename__ = "threat_intel_challenges"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    difficulty = Column(String(50), nullable=False, default="BEGINNER")
    category = Column(String(50), nullable=False)
    objective = Column(Text, nullable=False)
    scenario_description = Column(Text, nullable=False)
    target_indicator_value = Column(String(255), nullable=False)
    expected_classification = Column(String(50), nullable=False)
    expected_observations = Column(Text, nullable=True)  # JSON-encoded array of observation strings
    rubric_description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    attempts = relationship("ThreatIntelChallengeAttempt", back_populates="challenge", cascade="all, delete-orphan")


class ThreatIntelChallengeAttempt(Base):
    """Student evaluation attempt for a threat intelligence challenge."""

    __tablename__ = "threat_intel_challenge_attempts"

    id = Column(Integer, primary_key=True, index=True)
    challenge_id = Column(Integer, ForeignKey("threat_intel_challenges.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_classification = Column(String(50), nullable=False)
    hypothesis_text = Column(Text, nullable=False)
    evidence_notes = Column(Text, nullable=False)
    conclusion = Column(Text, nullable=False)
    score = Column(Float, nullable=False, default=0.0)
    passed = Column(Boolean, nullable=False, default=False)
    feedback = Column(Text, nullable=True)  # JSON-encoded rubric feedback & tips
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    challenge = relationship("ThreatIntelChallenge", back_populates="attempts")
    user = relationship("User")


class EnrichmentCache(Base):
    """Cache for indicator reputation lookups to prevent redundant computation."""

    __tablename__ = "threat_intel_enrichment_cache"

    id = Column(Integer, primary_key=True, index=True)
    indicator_type = Column(String(50), nullable=False, index=True)
    normalized_value = Column(String(512), nullable=False, index=True)
    provider = Column(String(100), nullable=False)
    classification = Column(String(50), nullable=False)
    confidence = Column(String(50), nullable=False)
    categories = Column(Text, nullable=True)  # JSON
    tags = Column(Text, nullable=True)  # JSON
    raw_metadata = Column(Text, nullable=True)  # JSON
    retrieved_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    expires_at = Column(DateTime(timezone=True), nullable=True)
