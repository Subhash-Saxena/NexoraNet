"""Watchlist Service for tracking high-priority or suspicious indicators."""

from datetime import datetime, timezone

from app.models.threat_intel import Indicator, IndicatorTimeline, WatchlistItem
from app.models.user import User
from fastapi import HTTPException, status
from sqlalchemy.orm import Session


class WatchlistService:
    """Manages analyst watchlist entries for active monitoring of indicators."""

    @classmethod
    def add_to_watchlist(
        cls,
        db: Session,
        indicator_id: int,
        user: User,
        reason: str,
        expires_at: datetime | None = None,
    ) -> WatchlistItem:
        """Add an indicator to the analyst's watchlist."""
        indicator = db.query(Indicator).filter(Indicator.id == indicator_id).first()
        if not indicator:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found.")

        existing = (
            db.query(WatchlistItem)
            .filter(WatchlistItem.indicator_id == indicator_id, WatchlistItem.user_id == user.id)
            .first()
        )
        if existing:
            existing.reason = reason
            existing.expires_at = expires_at
            db.commit()
            db.refresh(existing)
            return existing

        item = WatchlistItem(
            indicator_id=indicator_id,
            user_id=user.id,
            reason=reason,
            added_by=user.display_name or user.username,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
        )
        db.add(item)

        timeline = IndicatorTimeline(
            indicator_id=indicator_id,
            event_type="WATCHLIST_ADDED",
            title="Added to Watchlist",
            description=f"Added by {user.display_name or user.username}. Reason: {reason}",
            actor_name=user.display_name or user.username,
            event_timestamp=datetime.now(timezone.utc),
        )
        db.add(timeline)

        db.commit()
        db.refresh(item)
        return item

    @classmethod
    def remove_from_watchlist(
        cls,
        db: Session,
        watchlist_id: int,
        user: User,
    ) -> bool:
        """Remove an entry from the analyst's watchlist."""
        item = db.query(WatchlistItem).filter(WatchlistItem.id == watchlist_id).first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Watchlist entry not found.")

        if item.user_id != user.id and not getattr(user, "is_superuser", False):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        indicator_id = item.indicator_id
        db.delete(item)

        timeline = IndicatorTimeline(
            indicator_id=indicator_id,
            event_type="WATCHLIST_REMOVED",
            title="Removed from Watchlist",
            description=f"Removed by {user.display_name or user.username}.",
            actor_name=user.display_name or user.username,
            event_timestamp=datetime.now(timezone.utc),
        )
        db.add(timeline)

        db.commit()
        return True

    @classmethod
    def list_watchlist(
        cls,
        db: Session,
        user_id: int | None = None,
        include_expired: bool = False,
    ) -> list[WatchlistItem]:
        """List active watchlist items."""
        query = db.query(WatchlistItem)
        if user_id is not None:
            query = query.filter(WatchlistItem.user_id == user_id)

        if not include_expired:
            now_utc = datetime.now(timezone.utc)
            query = query.filter((WatchlistItem.expires_at.is_(None)) | (WatchlistItem.expires_at > now_utc))

        return query.order_by(WatchlistItem.created_at.desc()).all()

    @classmethod
    def is_watched(cls, db: Session, indicator_id: int, user_id: int) -> bool:
        """Check if an indicator is currently on a user's watchlist."""
        now_utc = datetime.now(timezone.utc)
        item = (
            db.query(WatchlistItem)
            .filter(
                WatchlistItem.indicator_id == indicator_id,
                WatchlistItem.user_id == user_id,
                (WatchlistItem.expires_at.is_(None)) | (WatchlistItem.expires_at > now_utc),
            )
            .first()
        )
        return item is not None


watchlist_service = WatchlistService()
