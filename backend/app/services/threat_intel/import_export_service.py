"""Safe Import and Export Service for Threat Intelligence Indicators.

Enforces offline security standards:
- 5MB maximum file payload
- 1,000 indicator batch limit
- CSV injection sanitization (=, +, -, @, \\t, \\r prefix escaping)
- Strict validation and normalization
- Zero external network transmissions
"""

import csv
import io
import json
from datetime import datetime, timezone
from typing import Any

from app.models.threat_intel import Indicator
from app.models.user import User
from app.services.threat_intel.indicator_service import indicator_service
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

MAX_FILE_BYTES = 5 * 1024 * 1024  # 5 MB
MAX_INDICATOR_ROWS = 1000
CSV_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def sanitize_csv_field(value: Any) -> str:
    """Neutralize potential CSV formula injection attacks."""
    if value is None:
        return ""
    str_val = str(value).strip()
    if str_val.startswith(CSV_FORMULA_PREFIXES):
        return f"'{str_val}"
    return str_val


class ImportExportService:
    """Handles safe importing and exporting of threat intelligence data."""

    @classmethod
    def import_indicators(
        cls,
        db: Session,
        raw_content: bytes,
        file_format: str,
        actor: User | None = None,
        source_name: str = "Batch Threat Intel Import",
    ) -> dict[str, Any]:
        """Safely parse, normalize, and ingest indicators from JSON, JSONL, or CSV."""
        if len(raw_content) > MAX_FILE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {MAX_FILE_BYTES // (1024 * 1024)}MB.",
            )

        fmt = file_format.lower().strip()
        rows: list[dict[str, Any]] = []

        try:
            text_data = raw_content.decode("utf-8", errors="replace")
        except UnicodeDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to decode file as UTF-8: {exc}",
            )

        if fmt in ("json", "application/json"):
            try:
                parsed = json.loads(text_data)
                if isinstance(parsed, list):
                    rows = parsed
                elif isinstance(parsed, dict) and "indicators" in parsed:
                    rows = parsed["indicators"]
                else:
                    rows = [parsed]
            except json.JSONDecodeError as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Malformed JSON payload: {exc.msg}",
                )

        elif fmt in ("jsonl", "application/x-ndjson"):
            for line_idx, line in enumerate(text_data.splitlines(), start=1):
                clean_line = line.strip()
                if not clean_line:
                    continue
                try:
                    obj = json.loads(clean_line)
                    if isinstance(obj, dict):
                        rows.append(obj)
                except json.JSONDecodeError:
                    continue

        elif fmt in ("csv", "text/csv"):
            csv_reader = csv.DictReader(io.StringIO(text_data))
            for row in csv_reader:
                rows.append(row)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported format '{file_format}'. Supported formats: json, jsonl, csv.",
            )

        if len(rows) > MAX_INDICATOR_ROWS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Batch size {len(rows)} exceeds maximum allowed limit of {MAX_INDICATOR_ROWS} indicators.",
            )

        imported_count = 0
        skipped_count = 0
        errors: list[dict[str, Any]] = []
        created_indicators: list[dict[str, Any]] = []

        for idx, row in enumerate(rows, start=1):
            val = row.get("value") or row.get("indicator") or row.get("raw_value")
            if not val or not str(val).strip():
                skipped_count += 1
                continue

            raw_val_str = str(val).strip()
            # Strip CSV injection prefix if present
            if raw_val_str.startswith("'") and len(raw_val_str) > 1 and raw_val_str[1] in CSV_FORMULA_PREFIXES:
                raw_val_str = raw_val_str[1:]
            elif raw_val_str.startswith(("=", "+", "@")):
                raw_val_str = raw_val_str.lstrip("=+@")

            itype = row.get("type") or row.get("indicator_type")

            try:
                indicator = indicator_service.get_or_create_indicator(
                    db=db,
                    raw_val=raw_val_str,
                    indicator_type=itype,
                    source_name=source_name,
                    context={"observation_type": "BATCH_IMPORT", "import_index": idx},
                    actor=actor,
                )

                # Update tags or classification if provided in batch
                custom_cls = row.get("classification")
                if custom_cls and custom_cls.upper() in ("BENIGN", "SUSPICIOUS", "MALICIOUS"):
                    indicator.classification = custom_cls.upper()

                custom_tags = row.get("tags")
                if custom_tags:
                    if isinstance(custom_tags, list):
                        indicator.tags = json.dumps(custom_tags)
                    elif isinstance(custom_tags, str):
                        try:
                            parsed_tags = json.loads(custom_tags)
                            indicator.tags = json.dumps(parsed_tags)
                        except (json.JSONDecodeError, TypeError):
                            indicator.tags = json.dumps([t.strip() for t in custom_tags.split(",") if t.strip()])

                db.commit()
                db.refresh(indicator)

                imported_count += 1
                created_indicators.append({
                    "id": indicator.id,
                    "indicator_id": indicator.indicator_id,
                    "type": indicator.indicator_type,
                    "value": indicator.display_value,
                    "classification": indicator.classification,
                })
            except (ValueError, HTTPException) as exc:
                skipped_count += 1
                errors.append({"row_index": idx, "value": raw_val_str, "error": str(exc)})

        return {
            "total_records": len(rows),
            "imported": imported_count,
            "skipped": skipped_count,
            "errors": errors[:50],  # cap reported errors
            "sample_imported": created_indicators[:10],
        }

    @classmethod
    def export_indicators(
        cls,
        db: Session,
        file_format: str = "json",
        classification: str | None = None,
        indicator_type: str | None = None,
    ) -> tuple[str, str]:
        """Export indicators in JSON or sanitized CSV. Returns (content_string, media_type)."""
        query = db.query(Indicator)
        if classification:
            query = query.filter(Indicator.classification == classification.upper())
        if indicator_type:
            query = query.filter(Indicator.indicator_type == indicator_type.upper())

        indicators = query.order_by(Indicator.created_at.desc()).limit(MAX_INDICATOR_ROWS).all()

        fmt = file_format.lower().strip()
        if fmt == "csv":
            output = io.StringIO()
            writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
            writer.writerow([
                "indicator_id",
                "type",
                "value",
                "normalized_value",
                "classification",
                "confidence",
                "severity",
                "status",
                "mitre_attack_id",
                "source_name",
                "first_seen",
                "last_seen",
            ])
            for ind in indicators:
                writer.writerow([
                    sanitize_csv_field(ind.indicator_id),
                    sanitize_csv_field(ind.indicator_type),
                    sanitize_csv_field(ind.display_value),
                    sanitize_csv_field(ind.normalized_value),
                    sanitize_csv_field(ind.classification),
                    sanitize_csv_field(ind.confidence),
                    sanitize_csv_field(ind.severity),
                    sanitize_csv_field(ind.status),
                    sanitize_csv_field(ind.mitre_attack_id or ""),
                    sanitize_csv_field(ind.source_name),
                    sanitize_csv_field(ind.first_seen.isoformat() if ind.first_seen else ""),
                    sanitize_csv_field(ind.last_seen.isoformat() if ind.last_seen else ""),
                ])
            return output.getvalue(), "text/csv"

        # Default: JSON
        data = [
            {
                "indicator_id": ind.indicator_id,
                "type": ind.indicator_type,
                "value": ind.display_value,
                "normalized_value": ind.normalized_value,
                "classification": ind.classification,
                "confidence": ind.confidence,
                "severity": ind.severity,
                "status": ind.status,
                "mitre_attack_id": ind.mitre_attack_id,
                "mitre_technique": ind.mitre_technique,
                "source_name": ind.source_name,
                "tags": json.loads(ind.tags) if ind.tags else [],
                "description": ind.description,
                "first_seen": ind.first_seen.isoformat() if ind.first_seen else None,
                "last_seen": ind.last_seen.isoformat() if ind.last_seen else None,
            }
            for ind in indicators
        ]
        return json.dumps({"indicators": data, "exported_at": datetime.now(timezone.utc).isoformat()}, indent=2), "application/json"


import_export_service = ImportExportService()
