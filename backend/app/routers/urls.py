from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models import URL, Check
from ..schemas import URLCreate, URLOut, CheckOut
from ..scheduler import check_url_instance

router = APIRouter(prefix="/api/urls", tags=["urls"])


def build_url_out(url_item: URL, latest_check: Optional[Check] = None) -> URLOut:
    return URLOut(
        id=url_item.id,
        url=url_item.url,
        created_at=url_item.created_at,
        is_up=latest_check.is_up if latest_check else None,
        last_status_code=latest_check.status_code if latest_check else None,
        last_response_time_ms=latest_check.response_time_ms if latest_check else None,
        last_checked_at=latest_check.checked_at if latest_check else None,
    )


@router.post("", response_model=URLOut, status_code=status.HTTP_201_CREATED)
async def create_url(url_in: URLCreate, db: Session = Depends(get_db)):
    existing = db.query(URL).filter(URL.url == url_in.url).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is already being monitored."
        )

    db_url = URL(url=url_in.url)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)

    # Perform immediate initial ping check
    initial_check = await check_url_instance(db_url.id, db_url.url, db)
    return build_url_out(db_url, initial_check)


@router.get("", response_model=List[URLOut])
def list_urls(db: Session = Depends(get_db)):
    urls = db.query(URL).all()
    results = []
    for u in urls:
        latest_check = (
            db.query(Check)
            .filter(Check.url_id == u.id)
            .order_by(desc(Check.checked_at))
            .first()
        )
        results.append(build_url_out(u, latest_check))
    return results


@router.delete("/{url_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_url(url_id: int, db: Session = Depends(get_db)):
    db_url = db.query(URL).filter(URL.id == url_id).first()
    if not db_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitored URL not found."
        )
    db.delete(db_url)
    db.commit()
    return None


@router.get("/{url_id}/checks", response_model=List[CheckOut])
def get_url_checks(
    url_id: int,
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    db_url = db.query(URL).filter(URL.id == url_id).first()
    if not db_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Monitored URL not found."
        )
    checks = (
        db.query(Check)
        .filter(Check.url_id == url_id)
        .order_by(desc(Check.checked_at))
        .limit(limit)
        .all()
    )
    return checks
