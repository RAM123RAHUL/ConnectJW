import json
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from app.database import get_db

router = APIRouter(prefix="/api/events", tags=["events"])


class EventResponse(BaseModel):
    id: str
    crawlJobId: str
    websiteId: str
    eventData: dict
    overallConfidence: float
    fieldConfidences: dict
    aiNotes: str
    sourceUrl: str
    createdAt: str


@router.get("", response_model=list[EventResponse])
async def list_events(
    website_id: str | None = None,
    min_confidence: float = Query(default=0, ge=0, le=100),
    limit: int = Query(default=50, ge=1, le=500)
):
    """List events with optional filters"""
    db = get_db()

    where = {}
    if website_id:
        where["websiteId"] = website_id
    if min_confidence > 0:
        where["overallConfidence"] = {"gte": min_confidence}

    results = await db.event.find_many(
        where=where,
        order={"createdAt": "desc"},
        take=limit
    )

    return [
        EventResponse(
            id=e.id,
            crawlJobId=e.crawlJobId,
            websiteId=e.websiteId,
            eventData=json.loads(e.eventData),  # Deserialize JSON string
            overallConfidence=e.overallConfidence,
            fieldConfidences=json.loads(e.fieldConfidences),  # Deserialize JSON string
            aiNotes=e.aiNotes,
            sourceUrl=e.sourceUrl,
            createdAt=e.createdAt.isoformat()
        )
        for e in results
    ]


@router.get("/{event_id}", response_model=EventResponse)
async def get_event(event_id: str):
    """Get a specific event with full details"""
    db = get_db()

    result = await db.event.find_unique(where={"id": event_id})

    if not result:
        raise HTTPException(status_code=404, detail="Event not found")

    return EventResponse(
        id=result.id,
        crawlJobId=result.crawlJobId,
        websiteId=result.websiteId,
        eventData=json.loads(result.eventData),  # Deserialize JSON string
        overallConfidence=result.overallConfidence,
        fieldConfidences=json.loads(result.fieldConfidences),  # Deserialize JSON string
        aiNotes=result.aiNotes,
        sourceUrl=result.sourceUrl,
        createdAt=result.createdAt.isoformat()
    )


@router.delete("/{event_id}")
async def delete_event(event_id: str):
    """Delete an event"""
    db = get_db()

    try:
        await db.event.delete(where={"id": event_id})
        return {"message": "Event deleted successfully"}
    except:
        raise HTTPException(status_code=404, detail="Event not found")
