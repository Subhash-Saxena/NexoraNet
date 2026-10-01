"""Database models for Step 15 SIEM & Security Log Analysis Engine.

Includes LogSource, SecurityLogDataset, RawLogEvent, SecurityEvent,
LogCorrelationRule, CorrelationAlert, SavedSearch, SearchHistory, and SIEMLabScenario.
"""

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import TimeStampedModel
from app.models.enums import (
    CorrelationAlertStatus,
    LogCorrelationRuleStatus,
    LogSourceStatus,
    RawLogFormat,
    SecurityEventSeverity,
    SecurityLogDatasetType,
)

if TYPE_CHECKING:
    from app.models.user import User


class LogSource(TimeStampedModel):
    """Educational security log source representing telemetry origin."""

    __tablename__ = "log_sources"

    stable_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    platform: Mapped[str] = mapped_column(String(64), nullable=False)
    vendor: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(
        String(32), default=LogSourceStatus.ACTIVE.value, nullable=False, index=True
    )
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    events: Mapped[list["SecurityEvent"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )
    raw_logs: Mapped[list["RawLogEvent"]] = relationship(
        back_populates="source", cascade="all, delete-orphan"
    )


class SecurityLogDataset(TimeStampedModel):
    """Collection of synthetic security logs for SIEM analysis and training."""

    __tablename__ = "security_log_datasets"

    stable_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    dataset_type: Mapped[str] = mapped_column(
        String(64), default=SecurityLogDatasetType.BEGINNER.value, nullable=False, index=True
    )
    difficulty: Mapped[str] = mapped_column(String(32), default="BEGINNER", nullable=False)
    event_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_synthetic: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    events: Mapped[list["SecurityEvent"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )
    raw_logs: Mapped[list["RawLogEvent"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )
    correlation_alerts: Mapped[list["CorrelationAlert"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )
    scenarios: Mapped[list["SIEMLabScenario"]] = relationship(
        back_populates="dataset", cascade="all, delete-orphan"
    )


class RawLogEvent(TimeStampedModel):
    """Raw, untrusted log message as captured or generated before normalization."""

    __tablename__ = "raw_log_events"

    source_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("log_sources.id", ondelete="SET NULL"), nullable=True, index=True
    )
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("security_log_datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    raw_message: Mapped[str] = mapped_column(Text, nullable=False)
    format: Mapped[str] = mapped_column(
        String(32), default=RawLogFormat.JSON.value, nullable=False
    )
    sequence_number: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    source: Mapped["LogSource | None"] = relationship(back_populates="raw_logs")
    dataset: Mapped["SecurityLogDataset"] = relationship(back_populates="raw_logs")
    normalized_event: Mapped["SecurityEvent | None"] = relationship(
        back_populates="raw_event", uselist=False
    )


class SecurityEvent(TimeStampedModel):
    """Normalized security event mapped to standardized taxonomy schema."""

    __tablename__ = "security_events"

    event_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    event_category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Entity dimensions
    host: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    source_ip: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_port: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    destination_ip: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    destination_port: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    protocol: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)

    # Action and state
    action: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    status: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    severity: Mapped[str] = mapped_column(
        String(32), default=SecurityEventSeverity.INFO.value, nullable=False, index=True
    )

    # Process and execution context
    process_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_process: Mapped[str | None] = mapped_column(String(255), nullable=True)
    command_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # File and web artifacts
    file_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Authentication & message
    authentication_method: Mapped[str | None] = mapped_column(String(64), nullable=True)
    result: Mapped[str | None] = mapped_column(String(64), nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Foreign keys
    raw_event_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("raw_log_events.id", ondelete="SET NULL"), nullable=True, index=True
    )
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("security_log_datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("log_sources.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # Relationships
    raw_event: Mapped["RawLogEvent | None"] = relationship(back_populates="normalized_event")
    dataset: Mapped["SecurityLogDataset"] = relationship(back_populates="events")
    source: Mapped["LogSource | None"] = relationship(back_populates="events")


class LogCorrelationRule(TimeStampedModel):
    """Deterministic, structured rule evaluated across security logs."""

    __tablename__ = "log_correlation_rules"

    stable_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    severity: Mapped[str] = mapped_column(
        String(32), default=SecurityEventSeverity.MEDIUM.value, nullable=False
    )
    confidence: Mapped[str] = mapped_column(String(32), default="HIGH", nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default=LogCorrelationRuleStatus.ENABLED.value, nullable=False, index=True
    )
    version: Mapped[str] = mapped_column(String(32), default="1.0.0", nullable=False)
    logic: Mapped[str] = mapped_column(Text, nullable=False)  # JSON logic description
    time_window_seconds: Mapped[int] = mapped_column(Integer, default=300, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    alerts: Mapped[list["CorrelationAlert"]] = relationship(
        back_populates="rule", cascade="all, delete-orphan"
    )


class CorrelationAlert(TimeStampedModel):
    """Alert synthesized when a correlation rule matches across log events."""

    __tablename__ = "correlation_alerts"

    alert_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    rule_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("log_correlation_rules.id", ondelete="CASCADE"), nullable=False, index=True
    )
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("security_log_datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence: Mapped[str] = mapped_column(String(32), default="HIGH", nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default=CorrelationAlertStatus.NEW.value, nullable=False, index=True
    )
    event_count: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    source_context: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    evidence_summary: Mapped[str] = mapped_column(Text, nullable=False)
    matched_event_ids: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    soc_alert_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    rule: Mapped["LogCorrelationRule"] = relationship(back_populates="alerts")
    dataset: Mapped["SecurityLogDataset"] = relationship(back_populates="correlation_alerts")


class SavedSearch(TimeStampedModel):
    """Saved query filter definition for the SIEM search workbench."""

    __tablename__ = "saved_searches"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    query_definition: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    owner_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    owner: Mapped["User | None"] = relationship()


class SearchHistory(TimeStampedModel):
    """Audit and recent history log of executed SIEM searches."""

    __tablename__ = "search_history"

    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    query_definition: Mapped[str] = mapped_column(Text, nullable=False)  # JSON
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )
    dataset_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    result_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    execution_time_ms: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # Relationships
    user: Mapped["User | None"] = relationship()


class SIEMLabScenario(TimeStampedModel):
    """Structured educational lab scenario for SIEM log investigation."""

    __tablename__ = "siem_lab_scenarios"

    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(32), default="BEGINNER", nullable=False)
    dataset_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("security_log_datasets.id", ondelete="CASCADE"), nullable=False, index=True
    )
    objectives: Mapped[str] = mapped_column(Text, nullable=False)  # JSON list
    expected_event_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    hints: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    recommended_query: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON

    # Relationships
    dataset: Mapped["SecurityLogDataset"] = relationship(back_populates="scenarios")
