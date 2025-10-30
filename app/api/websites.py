from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.database import get_db

router = APIRouter(prefix="/api/websites", tags=["websites"])


class WebsiteCreate(BaseModel):
    name: str
    base_url: HttpUrl
    notes: str | None = None


class WebsiteResponse(BaseModel):
    id: str
    name: str
    baseUrl: str
    notes: str | None
    active: bool
    createdAt: str


@router.post("", response_model=WebsiteResponse)
async def create_website(website: WebsiteCreate):
    """Register a new website to crawl"""
    db = get_db()

    result = await db.targetwebsite.create(
        data={
            "name": website.name,
            "baseUrl": str(website.base_url),
            "notes": website.notes,
            "active": True
        }
    )

    return WebsiteResponse(
        id=result.id,
        name=result.name,
        baseUrl=result.baseUrl,
        notes=result.notes,
        active=result.active,
        createdAt=result.createdAt.isoformat()
    )


@router.get("", response_model=list[WebsiteResponse])
async def list_websites(active_only: bool = True):
    """List all registered websites"""
    db = get_db()

    where = {"active": True} if active_only else {}
    results = await db.targetwebsite.find_many(
        where=where,
        order={"createdAt": "desc"}
    )

    return [
        WebsiteResponse(
            id=w.id,
            name=w.name,
            baseUrl=w.baseUrl,
            notes=w.notes,
            active=w.active,
            createdAt=w.createdAt.isoformat()
        )
        for w in results
    ]


@router.get("/{website_id}", response_model=WebsiteResponse)
async def get_website(website_id: str):
    """Get a specific website"""
    db = get_db()

    result = await db.targetwebsite.find_unique(where={"id": website_id})

    if not result:
        raise HTTPException(status_code=404, detail="Website not found")

    return WebsiteResponse(
        id=result.id,
        name=result.name,
        baseUrl=result.baseUrl,
        notes=result.notes,
        active=result.active,
        createdAt=result.createdAt.isoformat()
    )


@router.delete("/{website_id}")
async def delete_website(website_id: str):
    """Delete a website"""
    db = get_db()

    try:
        await db.targetwebsite.delete(where={"id": website_id})
        return {"message": "Website deleted successfully"}
    except:
        raise HTTPException(status_code=404, detail="Website not found")
