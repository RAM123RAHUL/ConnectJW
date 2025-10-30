import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.database import get_db

router = APIRouter(prefix="/api/structure", tags=["structure"])


class StructureCreate(BaseModel):
    structure: dict


class StructureResponse(BaseModel):
    id: str
    version: int
    isActive: bool
    structure: dict
    createdAt: str


@router.post("", response_model=StructureResponse)
async def create_structure(data: StructureCreate):
    """Define your event structure (do this once)"""
    db = get_db()

    # Deactivate previous structures
    await db.eventstructure.update_many(
        where={"isActive": True},
        data={"isActive": False}
    )

    # Get next version number
    latest = await db.eventstructure.find_first(
        order={"version": "desc"}
    )
    next_version = (latest.version + 1) if latest else 1

    # Create new structure
    result = await db.eventstructure.create(
        data={
            "version": next_version,
            "isActive": True,
            "structure": json.dumps(data.structure)  # Serialize to JSON string
        }
    )

    return StructureResponse(
        id=result.id,
        version=result.version,
        isActive=result.isActive,
        structure=json.loads(result.structure),  # Deserialize from JSON string
        createdAt=result.createdAt.isoformat()
    )


@router.get("", response_model=StructureResponse)
async def get_active_structure():
    """Get the current active event structure"""
    db = get_db()

    result = await db.eventstructure.find_first(
        where={"isActive": True}
    )

    if not result:
        raise HTTPException(status_code=404, detail="No active structure found. Please create one first.")

    return StructureResponse(
        id=result.id,
        version=result.version,
        isActive=result.isActive,
        structure=json.loads(result.structure),  # Deserialize from JSON string
        createdAt=result.createdAt.isoformat()
    )


@router.get("/versions", response_model=list[StructureResponse])
async def list_structures():
    """List all structure versions"""
    db = get_db()

    results = await db.eventstructure.find_many(
        order={"version": "desc"}
    )

    return [
        StructureResponse(
            id=s.id,
            version=s.version,
            isActive=s.isActive,
            structure=json.loads(s.structure),  # Deserialize from JSON string
            createdAt=s.createdAt.isoformat()
        )
        for s in results
    ]
