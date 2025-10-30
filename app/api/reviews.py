import json
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, validator
from datetime import datetime
from app.database import get_db

router = APIRouter(prefix="/api/events", tags=["reviews"])

# Review Request Model
class ReviewRequest(BaseModel):
    status: str  # "approved" or "rejected"
    notes: str | None = None
    reviewed_by: str  # User ID of reviewer

    @validator("status")
    def validate_status(cls, v):
        if v not in ["approved", "rejected"]:
            raise ValueError("Status must be 'approved' or 'rejected'")
        return v

    @validator("reviewed_by")
    def validate_reviewed_by(cls, v):
        if not v or not isinstance(v, str) or not v.strip():
            raise ValueError("reviewed_by must be a non-empty string")
        return v

# Edit Request Model
class EditRequest(BaseModel):
    event_data: dict  # Updated event data (JSON)

    @validator("event_data")
    def validate_event_data(cls, v):
        if not isinstance(v, dict) or not v:
            raise ValueError("event_data must be a non-empty dictionary")
        return v

# Review Response Model
class ReviewResponse(BaseModel):
    review_status: str
    reviewed_by: str | None
    review_notes: str | None
    reviewed_at: str | None
    published_at: str | None

@router.post("/{event_id}/review", response_model=ReviewResponse)
async def review_event(event_id: str, request: ReviewRequest):
    """Approve or reject an event with optional notes"""
    db = get_db()
    
    # Fetch existing event
    event = await db.event.find_unique(where={"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.reviewStatus != "pending":
        raise HTTPException(status_code=400, detail=f"Event already reviewed with status: {event.reviewStatus}")
    
    # Prepare update data
    update_data = {
        "reviewStatus": request.status,
        "reviewedBy": request.reviewed_by,
        "reviewNotes": request.notes,
        "reviewedAt": datetime.utcnow()
    }
    
    # Set published_at if approved
    if request.status == "approved":
        update_data["publishedAt"] = datetime.utcnow()
    
    # Update event in database
    try:
        updated_event = await db.event.update(
            where={"id": event_id},
            data=update_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database update failed: {str(e)}")
    
    return ReviewResponse(
        review_status=updated_event.reviewStatus,
        reviewed_by=updated_event.reviewedBy,
        review_notes=updated_event.reviewNotes,
        reviewed_at=updated_event.reviewedAt.isoformat() if updated_event.reviewedAt else None,
        published_at=updated_event.publishedAt.isoformat() if updated_event.publishedAt else None
    )

@router.put("/{event_id}/edit", response_model=dict)
async def edit_event(event_id: str, request: EditRequest):
    """Edit event data (e.g., correct AI-extracted fields)"""
    db = get_db()
    
    # Fetch existing event
    event = await db.event.find_unique(where={"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Update event_data
    try:
        current_data = json.loads(event.eventData) if event.eventData else {}
        updated_data = {**current_data, **request.event_data}  # Merge dictionaries
        updated_event = await db.event.update(
            where={"id": event_id},
            data={"eventData": json.dumps(updated_data)}
        )
        return {"message": "Event updated successfully", "id": updated_event.id}
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail="Invalid JSON in event data")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")

@router.get("/{event_id}/review", response_model=ReviewResponse)
async def get_review_status(event_id: str):
    """Get review status for an event"""
    db = get_db()
    
    # Fetch event
    event = await db.event.find_unique(where={"id": event_id})
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return ReviewResponse(
        review_status=event.reviewStatus,
        reviewed_by=event.reviewedBy,
        review_notes=event.reviewNotes,
        reviewed_at=event.reviewedAt.isoformat() if event.reviewedAt else None,
        published_at=event.publishedAt.isoformat() if event.publishedAt else None
    )