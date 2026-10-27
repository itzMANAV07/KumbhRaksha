"""GET /events — Server-Sent Events endpoint."""
from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.sim import engine

router = APIRouter()


@router.get("/events")
async def events():
    return EventSourceResponse(engine.subscribe())
