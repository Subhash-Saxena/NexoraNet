"""Log Ingestion Service for NexoraNet Step 15.

Provides secure, bounded ingestion of synthetic or imported security logs with
strict protections against CSV injection, oversized uploads, and resource exhaustion.
"""

import csv
import io
import json
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import RawLogFormat
from app.models.siem import (
    LogSource,
    RawLogEvent,
    SecurityEvent,
    SecurityLogDataset,
)
from app.services.siem.normalization_service import LogNormalizationService


class LogIngestionService:
    """Handles controlled ingestion and atomic database storage of security logs."""

    MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
    MAX_EVENTS_PER_IMPORT = 2000
    MAX_FIELD_LENGTH = 1000
    CSV_DANGEROUS_PREFIXES = ("=", "+", "-", "@", "\t", "\r")

    @classmethod
    def sanitize_field(cls, text: str | None) -> str | None:
        """Sanitize field value against CSV formula injection and limit length."""
        if text is None:
            return None
        text_str = str(text)
        if len(text_str) > cls.MAX_FIELD_LENGTH:
            text_str = text_str[: cls.MAX_FIELD_LENGTH]

        # Neutralize spreadsheet formula execution characters
        if text_str.startswith(cls.CSV_DANGEROUS_PREFIXES):
            text_str = f"'{text_str}"
        return text_str

    @classmethod
    def ingest_payload(
        cls,
        db: Session,
        dataset_id: int,
        content: str,
        format_hint: str = RawLogFormat.JSON.value,
        source_id: int | None = None,
    ) -> dict[str, int]:
        """Ingest raw string payload (JSON, JSONL, CSV, or Syslog) into dataset."""
        # 1. Check size limit
        byte_len = len(content.encode("utf-8"))
        if byte_len > cls.MAX_FILE_BYTES:
            raise ValueError(
                f"Payload size ({byte_len} bytes) exceeds maximum allowable limit of {cls.MAX_FILE_BYTES} bytes."
            )

        # 2. Verify dataset exists
        dataset = db.execute(
            select(SecurityLogDataset).where(SecurityLogDataset.id == dataset_id)
        ).scalar_one_or_none()
        if not dataset:
            raise ValueError(f"Dataset with ID {dataset_id} does not exist.")

        # 3. Resolve default source
        source_type = "WINDOWS_SECURITY"
        if source_id:
            src = db.execute(select(LogSource).where(LogSource.id == source_id)).scalar_one_or_none()
            if src:
                source_type = src.source_type

        # 4. Parse raw messages based on format
        format_upper = format_hint.upper()
        raw_entries: list[tuple[str, str]] = []  # (raw_message, format)

        trimmed = content.strip()
        if format_upper == RawLogFormat.JSON.value or trimmed.startswith(("[", "{")):
            cls._parse_json_records(trimmed, raw_entries)
        elif format_upper == RawLogFormat.CSV.value:
            cls._parse_csv_records(trimmed, raw_entries)
        else:
            # Line-by-line (Syslog or text)
            for line in trimmed.splitlines():
                line_str = line.strip()
                if line_str:
                    raw_entries.append((line_str, RawLogFormat.SYSLOG.value))

        # Check record limit
        if len(raw_entries) > cls.MAX_EVENTS_PER_IMPORT:
            raise ValueError(
                f"Record count ({len(raw_entries)}) exceeds maximum import limit of {cls.MAX_EVENTS_PER_IMPORT}."
            )

        # 5. Normalize and create events
        seq = dataset.event_count or 0
        min_ts: datetime | None = dataset.start_time
        max_ts: datetime | None = dataset.end_time
        if min_ts is not None and min_ts.tzinfo is None:
            min_ts = min_ts.replace(tzinfo=timezone.utc)
        if max_ts is not None and max_ts.tzinfo is None:
            max_ts = max_ts.replace(tzinfo=timezone.utc)

        created_count = 0
        for raw_msg, log_fmt in raw_entries:
            seq += 1
            raw_event = RawLogEvent(
                source_id=source_id,
                dataset_id=dataset_id,
                timestamp=datetime.now(timezone.utc),
                raw_message=raw_msg[:5000],
                format=log_fmt,
                sequence_number=seq,
            )
            db.add(raw_event)
            db.flush()  # to obtain raw_event.id

            norm = LogNormalizationService.normalize(
                raw_message=raw_msg,
                log_format=log_fmt,
                default_source_type=source_type,
            )

            ts: datetime = norm["timestamp"]
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if min_ts is None or ts < min_ts:
                min_ts = ts
            if max_ts is None or ts > max_ts:
                max_ts = ts

            event_code = f"EVT-SIEM-{uuid.uuid4().hex[:12].upper()}"

            sec_event = SecurityEvent(
                event_id=event_code,
                timestamp=ts,
                event_type=norm["event_type"],
                event_category=norm["event_category"],
                source_type=norm["source_type"],
                host=cls.sanitize_field(norm.get("host")),
                username=cls.sanitize_field(norm.get("username")),
                source_ip=cls.sanitize_field(norm.get("source_ip")),
                source_port=norm.get("source_port"),
                destination_ip=cls.sanitize_field(norm.get("destination_ip")),
                destination_port=norm.get("destination_port"),
                protocol=cls.sanitize_field(norm.get("protocol")),
                action=cls.sanitize_field(norm.get("action")),
                status=cls.sanitize_field(norm.get("status")),
                severity=norm.get("severity", "INFO"),
                process_name=cls.sanitize_field(norm.get("process_name")),
                parent_process=cls.sanitize_field(norm.get("parent_process")),
                command_summary=cls.sanitize_field(norm.get("command_summary")),
                file_name=cls.sanitize_field(norm.get("file_name")),
                file_hash=cls.sanitize_field(norm.get("file_hash")),
                domain=cls.sanitize_field(norm.get("domain")),
                url=cls.sanitize_field(norm.get("url")),
                authentication_method=cls.sanitize_field(norm.get("authentication_method")),
                result=cls.sanitize_field(norm.get("result")),
                message=cls.sanitize_field(norm.get("message")),
                metadata_json=norm.get("metadata_json"),
                raw_event_id=raw_event.id,
                dataset_id=dataset_id,
                source_id=source_id,
            )
            db.add(sec_event)
            created_count += 1

        # Update dataset totals
        dataset.event_count = (dataset.event_count or 0) + created_count
        dataset.start_time = min_ts
        dataset.end_time = max_ts
        db.commit()

        return {
            "imported_events": created_count,
            "dataset_total": dataset.event_count,
        }

    @classmethod
    def _parse_json_records(cls, content: str, out_list: list[tuple[str, str]]) -> None:
        """Parse JSON array or JSON Lines string."""
        if content.startswith("["):
            try:
                arr = json.loads(content)
                if isinstance(arr, list):
                    for item in arr:
                        if isinstance(item, dict):
                            out_list.append((json.dumps(item), RawLogFormat.JSON.value))
                        else:
                            out_list.append((str(item), RawLogFormat.JSON.value))
                    return
            except json.JSONDecodeError:
                pass

        # Try JSONL
        for line in content.splitlines():
            l_str = line.strip()
            if not l_str:
                continue
            try:
                obj = json.loads(l_str)
                out_list.append((json.dumps(obj), RawLogFormat.JSON.value))
            except json.JSONDecodeError:
                out_list.append((l_str, RawLogFormat.SYSLOG.value))

    @classmethod
    def _parse_csv_records(cls, content: str, out_list: list[tuple[str, str]]) -> None:
        """Parse CSV rows into raw strings."""
        reader = csv.reader(io.StringIO(content))
        header = None
        for row in reader:
            if not row or not any(row):
                continue
            if header is None:
                header = row
                continue
            # Format row as json key-value if header exists
            row_dict = {}
            for i, col in enumerate(row):
                key = header[i] if i < len(header) else f"col_{i}"
                row_dict[key.strip()] = col.strip()
            out_list.append((json.dumps(row_dict), RawLogFormat.CSV.value))
