"""POST /report, GET /matches/{id}, POST /matches/{id}/confirm"""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import LostReport, Zone
from app.schemas import ReportRequest, ReportResponse, MatchResult
from app.matching import find_matches

router = APIRouter(tags=["lost_found"])


def _report_to_dict(r: LostReport) -> dict:
    return {
        "id": r.id,
        "type": r.type,
        "reporter_chat_id": r.reporter_chat_id,
        "name": r.name,
        "age": r.age,
        "clothing_color": r.clothing_color,
        "clothing_garment": r.clothing_garment,
        "zone_id": r.zone_id,
        "reported_at": r.reported_at,
        "status": r.status,
    }


@router.post("/report", response_model=ReportResponse)
async def create_report(req: ReportRequest, db: AsyncSession = Depends(get_db)):
    report = LostReport(
        type=req.type,
        reporter_chat_id=req.reporter_chat_id,
        name=req.name,
        age=req.age,
        clothing_color=req.clothing_color,
        clothing_garment=req.clothing_garment,
        zone_id=req.zone_id,
        reported_at=datetime.utcnow(),
        status="open",
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    return ReportResponse(report_id=report.id)


@router.get("/matches/{report_id}", response_model=list[MatchResult])
async def get_matches(report_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(LostReport).where(LostReport.id == report_id))
    lost = result.scalar_one_or_none()
    if lost is None or lost.type != "lost":
        raise HTTPException(status_code=404, detail="Lost report not found")

    found_result = await db.execute(
        select(LostReport).where(LostReport.type == "found", LostReport.status == "open")
    )
    found_reports = [_report_to_dict(r) for r in found_result.scalars().all()]

    # Build adjacency map from DB
    zones_result = await db.execute(select(Zone))
    adjacency_map = {z.id: z.adjacency for z in zones_result.scalars().all()}

    return find_matches(_report_to_dict(lost), found_reports, adjacency_map)


@router.post("/matches/{found_report_id}/confirm")
async def confirm_match(
    found_report_id: int,
    body: dict,
    db: AsyncSession = Depends(get_db),
):
    lost_id = body.get("lost_report_id")
    for rid in [found_report_id, lost_id]:
        result = await db.execute(select(LostReport).where(LostReport.id == rid))
        report = result.scalar_one_or_none()
        if report:
            report.status = "resolved"
    await db.commit()
    return {"ok": True}
