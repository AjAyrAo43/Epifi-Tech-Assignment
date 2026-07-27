import os
import time
import asyncio
import logging
from datetime import datetime, timezone
import httpx
from sqlalchemy.orm import Session
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .database import SessionLocal
from .models import URL, Check

logger = logging.getLogger(__name__)

CHECK_INTERVAL_SECONDS = int(os.getenv("CHECK_INTERVAL_SECONDS", "60"))
TIMEOUT_SECONDS = float(os.getenv("CHECK_TIMEOUT_SECONDS", "5.0"))

scheduler = AsyncIOScheduler()


async def check_url_instance(url_id: int, url_str: str, db: Session) -> Check:
    start_time = time.perf_counter()
    status_code = None
    is_up = False
    response_time_ms = None

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS, follow_redirects=True) as client:
            response = await client.get(url_str)
            elapsed = time.perf_counter() - start_time
            response_time_ms = int(elapsed * 1000)
            status_code = response.status_code
            is_up = 200 <= status_code < 400
    except (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError, Exception) as exc:
        elapsed = time.perf_counter() - start_time
        response_time_ms = int(elapsed * 1000)
        is_up = False
        status_code = None
        logger.info(f"Check failed for {url_str}: {exc}")

    check = Check(
        url_id=url_id,
        status_code=status_code,
        response_time_ms=response_time_ms,
        is_up=is_up,
        checked_at=datetime.now(timezone.utc)
    )
    db.add(check)
    db.commit()
    db.refresh(check)
    return check


async def run_all_checks():
    db = SessionLocal()
    try:
        urls = db.query(URL).all()
        if not urls:
            return
        tasks = [check_url_instance(u.id, u.url, db) for u in urls]
        await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        db.close()


def start_scheduler():
    scheduler.add_job(
        run_all_checks,
        "interval",
        seconds=CHECK_INTERVAL_SECONDS,
        id="check_all_urls_job",
        replace_existing=True
    )
    scheduler.start()
    logger.info(f"Scheduler started with interval {CHECK_INTERVAL_SECONDS}s")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
