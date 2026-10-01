"""Database models for PCAP packet capture files, parsed packets, and investigation telemetry."""

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimeStampedModel

if TYPE_CHECKING:
    from app.models.user import User


class Capture(TimeStampedModel):
    """Metadata and status for an uploaded or sample PCAP/PCAPNG capture file."""

    __tablename__ = "captures"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    format: Mapped[str] = mapped_column(String(30), default="pcap", nullable=False)
    packet_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    start_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    end_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    duration: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    status: Mapped[str] = mapped_column(String(30), default="UPLOADED", nullable=False, index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    sample_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary_metadata: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
    packets: Mapped[list["ParsedPacket"]] = relationship(
        "ParsedPacket", back_populates="capture", cascade="all, delete-orphan", lazy="dynamic"
    )
    bookmarks: Mapped[list["CaptureBookmark"]] = relationship(
        "CaptureBookmark", back_populates="capture", cascade="all, delete-orphan"
    )
    notes: Mapped[list["CaptureNote"]] = relationship(
        "CaptureNote", back_populates="capture", cascade="all, delete-orphan"
    )
    findings: Mapped[list["CaptureFinding"]] = relationship(
        "CaptureFinding", back_populates="capture", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Capture id={self.id} name='{self.name}' status='{self.status}' packets={self.packet_count}>"


class ParsedPacket(Base):
    """Normalized packet representation indexed for fast sorting, filtering, and deep layer inspection."""

    __tablename__ = "parsed_packets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    capture_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True
    )
    packet_number: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    timestamp: Mapped[float] = mapped_column(Float, nullable=False)
    relative_time: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    captured_length: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    original_length: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    protocol: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    source_mac: Mapped[str | None] = mapped_column(String(30), nullable=True)
    destination_mac: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source_ip: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    destination_ip: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    source_port: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    destination_port: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    transport_protocol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    application_protocol: Mapped[str | None] = mapped_column(String(20), nullable=True)
    info: Mapped[str] = mapped_column(String(500), nullable=False)
    tcp_flags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    tcp_seq: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    tcp_ack: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    layers: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list
    layer_details: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON dict

    # Relationships
    capture: Mapped["Capture"] = relationship("Capture", back_populates="packets")

    def __repr__(self) -> str:
        return f"<ParsedPacket #{self.packet_number} proto='{self.protocol}' info='{self.info[:30]}'>"


class CaptureBookmark(TimeStampedModel):
    """Student bookmarked packets for investigation reference and SOC reporting."""

    __tablename__ = "capture_bookmarks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    capture_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    packet_number: Mapped[int] = mapped_column(Integer, nullable=False)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array

    # Relationships
    capture: Mapped["Capture"] = relationship("Capture", back_populates="bookmarks")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])


class CaptureNote(TimeStampedModel):
    """Investigation notes attached to a packet, conversation, endpoint, or general capture."""

    __tablename__ = "capture_notes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    capture_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    target_type: Mapped[str] = mapped_column(String(30), default="general", nullable=False)
    target_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    title: Mapped[str | None] = mapped_column(String(200), nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    capture: Mapped["Capture"] = relationship("Capture", back_populates="notes")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])


class CaptureFinding(TimeStampedModel):
    """Structured student SOC findings, evidence packets, hypothesis, and conclusions."""

    __tablename__ = "capture_findings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True, index=True)
    capture_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("captures.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[str] = mapped_column(String(20), default="INFO", nullable=False)
    evidence_packets: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON list of int
    source_endpoint: Mapped[str | None] = mapped_column(String(100), nullable=True)
    destination_endpoint: Mapped[str | None] = mapped_column(String(100), nullable=True)
    hypothesis: Mapped[str | None] = mapped_column(Text, nullable=True)
    conclusion: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    capture: Mapped["Capture"] = relationship("Capture", back_populates="findings")
    user: Mapped["User | None"] = relationship("User", foreign_keys=[user_id])
