from typing import List, Optional, Dict, Tuple
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from ..database import get_db
from ..models import URL, Check
from ..schemas import URLCreate, URLOut, CheckOut
from ..scheduler import check_url_instance

router = APIRouter(prefix="/api/urls", tags=["urls"])


def _compute_stats(url_id: int, db: Session) -> Tuple[int, Optional[float]]:
    """Returns (total_checks, uptime_percentage) for a URL. SQLite-compatible."""
    total = db.query(func.count(Check.id)).filter(Check.url_id == url_id).scalar() or 0
    if total == 0:
        return 0, None
    up_count = (
        db.query(func.count(Check.id))
        .filter(Check.url_id == url_id, Check.is_up == True)  # noqa: E712
        .scalar()
        or 0
    )
    return total, round((up_count / total) * 100, 1)


def _latest_checks_map(url_ids: List[int], db: Session) -> Dict[int, Check]:
    """Fetch the latest Check for each URL id in a single batched query."""
    if not url_ids:
        return {}
    subq = (
        db.query(Check.url_id, func.max(Check.checked_at).label("max_ts"))
        .filter(Check.url_id.in_(url_ids))
        .group_by(Check.url_id)
        .subquery()
    )
    rows = (
        db.query(Check)
        .join(
            subq,
            (Check.url_id == subq.c.url_id) & (Check.checked_at == subq.c.max_ts),
        )
        .all()
    )
    return {c.url_id: c for c in rows}


def _build_url_out(
    url_item: URL,
    latest_check: Optional[Check] = None,
    total_checks: int = 0,
    uptime_percentage: Optional[float] = None,
) -> URLOut:
    return URLOut(
        id=url_item.id,
        name=url_item.name,
        url=url_item.url,
        created_at=url_item.created_at,
        is_up=latest_check.is_up if latest_check else None,
        last_status_code=latest_check.status_code if latest_check else None,
        last_response_time_ms=latest_check.response_time_ms if latest_check else None,
        last_checked_at=latest_check.checked_at if latest_check else None,
        uptime_percentage=uptime_percentage,
        total_checks=total_checks,
    )


# ---------------------------------------------------------------------------
# POST /api/urls  — Register a new URL for monitoring
# ---------------------------------------------------------------------------
@router.post("", response_model=URLOut, status_code=status.HTTP_201_CREATED)
async def create_url(url_in: URLCreate, db: Session = Depends(get_db)):
    existing = db.query(URL).filter(URL.url == url_in.url).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is already being monitored.",
        )

    db_url = URL(url=url_in.url, name=url_in.name)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    # Immediate initial ping so the UI never sits at "PENDING"
    initial_check = await check_url_instance(db_url.id, db_url.url, db)
    total, uptime_pct = _compute_stats(db_url.id, db)
    return _build_url_out(db_url, initial_check, total, uptime_pct)


# ---------------------------------------------------------------------------
# GET /api/urls  — List all monitored URLs with latest check stats
# ---------------------------------------------------------------------------
@router.get("", response_model=List[URLOut])
def list_urls(db: Session = Depends(get_db)):
    urls = db.query(URL).all()
    if not urls:
        return []

    url_ids = [u.id for u in urls]
    latest_map = _latest_checks_map(url_ids, db)

    results = []
    for u in urls:
        total, uptime_pct = _compute_stats(u.id, db)
        results.append(_build_url_out(u, latest_map.get(u.id), total, uptime_pct))
    return results


# ---------------------------------------------------------------------------
# GET /api/urls/{url_id}  — Single URL detail
# ---------------------------------------------------------------------------
@router.get("/{url_id}", response_model=URLOut)
def get_url(url_id: int, db: Session = Depends(get_db)):
    db_url = db.query(URL).filter(URL.id == url_id).first()
    if not db_url:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Monitored URL not found.")
    latest_check = (
        db.query(Check)
        .filter(Check.url_id == url_id)
        .order_by(desc(Check.checked_at))
        .first()
    )
    total, uptime_pct = _compute_stats(url_id, db)
    return _build_url_out(db_url, latest_check, total, uptime_pct)


# ---------------------------------------------------------------------------
# DELETE /api/urls/{url_id}  — Remove a monitored URL (cascade deletes checks)
# ---------------------------------------------------------------------------
@router.delete("/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(url_id: int, db: Session = Depends(get_db)):
    db_url = db.query(URL).filter(URL.id == url_id).first()
    if not db_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitored URL not found.",
        )
    db.delete(db_url)
    db.commit()
    return None


# ---------------------------------------------------------------------------
# GET /api/urls/{url_id}/checks  — Paginated check history
# ---------------------------------------------------------------------------
@router.get("/{url_id}/checks", response_model=List[CheckOut])
def get_url_checks(
    url_id: int,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    db_url = db.query(URL).filter(URL.id == url_id).first()
    if not db_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitored URL not found.",
        )
    checks = (
        db.query(Check)
        .filter(Check.url_id == url_id)
        .order_by(desc(Check.checked_at))
        .limit(limit)
        .all()
    )
    return checks
