"""ETL pipeline: fetch data from the autochecker API and load it into the database.

The autochecker dashboard API provides two endpoints:
- GET /api/items — lab/task catalog
- GET /api/logs  — anonymized check results (supports ?since= and ?limit= params)

Both require HTTP Basic Auth (email + password from settings).
"""

import logging
from datetime import datetime

import httpx
from sqlmodel import select, func
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.interaction import InteractionLog
from app.models.item import ItemRecord
from app.models.learner import Learner
from app.settings import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Extract — fetch data from the autochecker API
# ---------------------------------------------------------------------------


async def fetch_items() -> list[dict]:
    """Fetch the lab/task catalog from the autochecker API."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.get(
            f"{settings.autochecker_api_url}/api/items",
            auth=(settings.autochecker_email, settings.autochecker_password),
        )
        resp.raise_for_status()
        return resp.json()


async def fetch_logs(since: datetime | None = None) -> list[dict]:
    """Fetch check results from the autochecker API with pagination."""
    import asyncio

    all_logs: list[dict] = []
    max_retries = 3
    base_delay = 2.0  # seconds between requests

    async with httpx.AsyncClient(
        timeout=120.0,
        headers={
            "Accept": "application/json",
            "Connection": "keep-alive",
        },
    ) as client:
        cursor = since
        iteration = 0
        while True:
            iteration += 1
            params: dict[str, str | int] = {"limit": 100}
            if cursor is not None:
                params["since"] = cursor.isoformat()

            logger.info(f"Fetching logs iteration {iteration}, since={cursor}")
            
            # Retry logic with exponential backoff
            for attempt in range(max_retries):
                try:
                    resp = await client.get(
                        f"{settings.autochecker_api_url}/api/logs",
                        params=params,
                        auth=(settings.autochecker_email, settings.autochecker_password),
                    )
                    resp.raise_for_status()
                    break  # Success, exit retry loop
                except httpx.RemoteProtocolError as e:
                    logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                    if attempt < max_retries - 1:
                        retry_delay = base_delay * (2 ** attempt)  # Exponential backoff
                        logger.info(f"Retrying in {retry_delay}s...")
                        await asyncio.sleep(retry_delay)
                    else:
                        raise  # All retries exhausted
            
            data = resp.json()

            logs = data["logs"]
            all_logs.extend(logs)
            
            logger.info(f"Got {len(logs)} logs, total={len(all_logs)}, has_more={data.get('has_more')}")

            if not data.get("has_more") or not logs:
                break

            cursor = datetime.fromisoformat(logs[-1]["submitted_at"])
            
            # Add delay between requests to avoid rate limiting
            await asyncio.sleep(base_delay)

    return all_logs


# ---------------------------------------------------------------------------
# Load — insert fetched data into the local database
# ---------------------------------------------------------------------------


async def load_items(items: list[dict], session: AsyncSession) -> int:
    """Load items (labs and tasks) into the database."""
    created = 0
    lab_map: dict[str, ItemRecord] = {}

    # Process labs first
    for item in items:
        if item["type"] != "lab":
            continue
        title = item["title"]
        existing = (
            await session.exec(
                select(ItemRecord).where(
                    ItemRecord.type == "lab", ItemRecord.title == title
                )
            )
        ).first()
        if existing:
            lab_map[item["lab"]] = existing
        else:
            record = ItemRecord(type="lab", title=title)
            session.add(record)
            await session.flush()
            lab_map[item["lab"]] = record
            created += 1

    # Process tasks
    for item in items:
        if item["type"] != "task":
            continue
        parent = lab_map.get(item["lab"])
        if not parent:
            continue
        title = item["title"]
        existing = (
            await session.exec(
                select(ItemRecord).where(
                    ItemRecord.title == title, ItemRecord.parent_id == parent.id
                )
            )
        ).first()
        if not existing:
            record = ItemRecord(type="task", title=title, parent_id=parent.id)
            session.add(record)
            created += 1

    await session.commit()
    return created


async def load_logs(
    logs: list[dict], items_catalog: list[dict], session: AsyncSession
) -> int:
    """Load interaction logs into the database."""
    # Build lookup: (lab_short_id, task_short_id) → title
    title_lookup: dict[tuple[str, str | None], str] = {}
    for item in items_catalog:
        key = (item["lab"], item.get("task"))
        title_lookup[key] = item["title"]

    created = 0
    for log in logs:
        # Find or create learner
        learner = (
            await session.exec(
                select(Learner).where(Learner.external_id == str(log["student_id"]))
            )
        ).first()
        if not learner:
            learner = Learner(
                external_id=str(log["student_id"]),
                student_group=log.get("group", ""),
            )
            session.add(learner)
            await session.flush()

        # Find item
        title = title_lookup.get((log["lab"], log.get("task")))
        if not title:
            continue
        item = (
            await session.exec(select(ItemRecord).where(ItemRecord.title == title))
        ).first()
        if not item:
            continue

        # Skip if already exists (idempotent upsert)
        existing = (
            await session.exec(
                select(InteractionLog).where(
                    InteractionLog.external_id == log["id"]
                )
            )
        ).first()
        if existing:
            continue

        # Use API score if available; otherwise compute from passed/total
        score = log.get("score")
        if score is None:
            passed = log.get("passed")
            total = log.get("total")
            if passed is not None and total and total > 0:
                score = round((passed / total) * 100, 1)

        interaction = InteractionLog(
            external_id=log["id"],
            learner_id=learner.id,
            item_id=item.id,
            kind="attempt",
            score=score,
            checks_passed=log.get("passed"),
            checks_total=log.get("total"),
            created_at=datetime.fromisoformat(log["submitted_at"]),
        )
        session.add(interaction)
        created += 1

    await session.commit()
    return created


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


async def sync(session: AsyncSession) -> dict:
    """Run the full ETL pipeline."""
    # Fetch and load items
    api_items = await fetch_items()
    await load_items(api_items, session)

    # Determine last sync point
    result = (
        await session.exec(
            select(func.max(InteractionLog.created_at))
        )
    ).first()
    since = result if result else None

    # Fetch and load logs
    logs = await fetch_logs(since)
    new_count = await load_logs(logs, api_items, session)

    # Total count
    total = (await session.exec(select(func.count(InteractionLog.id)))).one()

    return {"new_records": new_count, "total_records": total}
