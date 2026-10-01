"""MITRE ATT&CK Framework Service for Step 17.

Handles tactic/technique catalog queries, incident technique mapping,
and matrix heat map / coverage calculation.
"""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import MitreMappingConfidence
from app.models.incident import Incident
from app.models.mitre import AttackTactic, AttackTechnique, IncidentTechniqueMapping


class MitreService:
    """Provides MITRE ATT&CK Enterprise navigation and incident mapping."""

    @classmethod
    def list_tactics(cls, db: Session) -> list[AttackTactic]:
        query = select(AttackTactic).options(
            selectinload(AttackTactic.techniques)
        ).order_by(AttackTactic.display_order.asc())
        return list(db.execute(query).scalars().all())

    @classmethod
    def list_techniques(
        cls,
        db: Session,
        tactic_id: str | None = None,
        search: str | None = None,
    ) -> list[AttackTechnique]:
        query = select(AttackTechnique).options(
            selectinload(AttackTechnique.tactic)
        )
        if tactic_id:
            query = query.join(AttackTactic).where(
                or_(AttackTactic.tactic_id == tactic_id, AttackTactic.name.ilike(f"%{tactic_id}%"))
            )
        if search:
            search_fmt = f"%{search}%"
            query = query.where(
                or_(
                    AttackTechnique.technique_id.ilike(search_fmt),
                    AttackTechnique.name.ilike(search_fmt),
                    AttackTechnique.description.ilike(search_fmt),
                )
            )

        return list(db.execute(query.order_by(AttackTechnique.technique_id.asc())).scalars().all())

    @classmethod
    def get_technique(cls, db: Session, technique_id_or_int: str | int) -> AttackTechnique | None:
        query = select(AttackTechnique).options(selectinload(AttackTechnique.tactic))
        if isinstance(technique_id_or_int, int) or str(technique_id_or_int).isdigit():
            query = query.where(AttackTechnique.id == int(technique_id_or_int))
        else:
            query = query.where(AttackTechnique.technique_id == str(technique_id_or_int))

        return db.execute(query).scalar_one_or_none()

    @classmethod
    def map_technique_to_incident(
        cls,
        db: Session,
        incident_id: int,
        technique_id_or_code: str | int,
        mapping_confidence: str = MitreMappingConfidence.OBSERVED_EVIDENCE,
        evidence_summary: str | None = None,
        phase: str | None = None,
        user_id: int | None = None,
    ) -> IncidentTechniqueMapping:
        technique = cls.get_technique(db, technique_id_or_code)
        if not technique:
            raise ValueError(f"Technique {technique_id_or_code} not found")

        incident = db.get(Incident, incident_id)
        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        existing = db.execute(
            select(IncidentTechniqueMapping).where(
                IncidentTechniqueMapping.incident_id == incident.id,
                IncidentTechniqueMapping.technique_id == technique.id,
            )
        ).scalar_one_or_none()

        if existing:
            existing.mapping_confidence = mapping_confidence
            existing.evidence_summary = evidence_summary
            existing.phase = phase
            existing.mapped_by_id = user_id
            existing.mapped_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
            return existing

        mapping = IncidentTechniqueMapping(
            incident_id=incident.id,
            technique_id=technique.id,
            mapping_confidence=mapping_confidence,
            evidence_summary=evidence_summary,
            phase=phase,
            mapped_by_id=user_id,
            mapped_at=datetime.now(timezone.utc),
        )
        db.add(mapping)
        db.commit()
        db.refresh(mapping)
        return mapping

    @classmethod
    def unmap_technique(cls, db: Session, incident_id: int, technique_id_or_code: str | int) -> bool:
        technique = cls.get_technique(db, technique_id_or_code)
        if not technique:
            return False

        mapping = db.execute(
            select(IncidentTechniqueMapping).where(
                IncidentTechniqueMapping.incident_id == incident_id,
                IncidentTechniqueMapping.technique_id == technique.id,
            )
        ).scalar_one_or_none()

        if mapping:
            db.delete(mapping)
            db.commit()
            return True
        return False

    @classmethod
    def get_matrix_coverage(cls, db: Session, incident_id: int | None = None) -> dict[str, Any]:
        """Calculates matrix coverage and heat map counts for all tactics."""
        tactics = cls.list_tactics(db)

        # Query all technique mappings for the given incident or overall
        mapping_query = select(IncidentTechniqueMapping).options(
            selectinload(IncidentTechniqueMapping.technique).selectinload(AttackTechnique.tactic)
        )
        if incident_id:
            mapping_query = mapping_query.where(IncidentTechniqueMapping.incident_id == incident_id)

        mappings = db.execute(mapping_query).scalars().all()
        mapped_technique_ids = {m.technique.technique_id for m in mappings if m.technique}

        tactic_columns = []
        total_techniques_count = 0
        covered_techniques_count = len(mapped_technique_ids)

        for tactic in tactics:
            tech_list = []
            for tech in tactic.techniques:
                total_techniques_count += 1
                is_mapped = tech.technique_id in mapped_technique_ids
                tech_list.append({
                    "id": tech.id,
                    "technique_id": tech.technique_id,
                    "name": tech.name,
                    "is_subtechnique": tech.is_subtechnique,
                    "is_mapped": is_mapped,
                })

            tactic_columns.append({
                "tactic_id": tactic.tactic_id,
                "name": tactic.name,
                "display_order": tactic.display_order,
                "techniques": tech_list,
                "mapped_count": sum(1 for t in tech_list if t["is_mapped"]),
                "total_count": len(tech_list),
            })

        coverage_percentage = (
            round((covered_techniques_count / total_techniques_count) * 100, 1)
            if total_techniques_count > 0
            else 0.0
        )

        return {
            "incident_id": incident_id,
            "tactics": tactic_columns,
            "total_techniques": total_techniques_count,
            "covered_techniques": covered_techniques_count,
            "coverage_percentage": coverage_percentage,
        }
