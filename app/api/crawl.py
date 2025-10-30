import json
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from app.database import get_db
from app.services.crawler import crawl
from app.services.ai_mapper import map_to_structure
from app.services.confidence import calculate_overall

router = APIRouter(prefix="/api/crawl", tags=["crawl"])


class CrawlRequest(BaseModel):
    website_id: str
    url: HttpUrl
    use_javascript: bool = False


class BatchCrawlRequest(BaseModel):
    website_id: str
    urls: list[HttpUrl]
    use_javascript: bool = False


class CrawlJobResponse(BaseModel):
    job_id: str
    status: str


class CrawlJobDetail(BaseModel):
    id: str
    websiteId: str
    url: str
    status: str
    error: str | None
    createdAt: str
    completedAt: str | None


async def process_crawl(job_id: str, website_id: str, url: str, use_javascript: bool):
    """Background task to process a single crawl job"""
    db = get_db()

    try:
        # Update status to processing
        await db.crawljob.update(
            where={"id": job_id},
            data={"status": "processing"}
        )

        # Get website info
        website = await db.targetwebsite.find_unique(where={"id": website_id})
        if not website:
            raise Exception("Website not found")

        # Get active structure
        structure = await db.eventstructure.find_first(where={"isActive": True})
        if not structure:
            raise Exception("No active event structure found")

        # Crawl the page
        raw_html = await crawl(url, use_javascript)

        # Validate we got the right content (basic check)
        if "scrapingbee" in raw_html.lower() or "cloudflare" in raw_html.lower():
            # Check if we got blocked or redirected
            if "scrapingbee" in raw_html.lower():
                raise Exception("Got redirected to ScrapingBee page - possible bot detection")
            if "challenge" in raw_html.lower() and "cloudflare" in raw_html.lower():
                raise Exception("Cloudflare challenge detected - bot protection active")

        # Save raw HTML (first 50k chars to avoid huge database entries)
        await db.crawljob.update(
            where={"id": job_id},
            data={"rawHtml": raw_html[:50000] if len(raw_html) > 50000 else raw_html}
        )

        # Map with AI
        ai_result = await map_to_structure(
            raw_html,
            json.loads(structure.structure),  # Deserialize JSON string
            website.notes or ""
        )

        # Calculate overall confidence
        overall_confidence = calculate_overall(ai_result["field_confidences"])

        # Save event
        await db.event.create(
            data={
                "crawlJobId": job_id,
                "websiteId": website_id,
                "eventData": json.dumps(ai_result["event_data"]),  # Serialize to JSON string
                "overallConfidence": overall_confidence,
                "fieldConfidences": json.dumps(ai_result["field_confidences"]),  # Serialize to JSON string
                "aiNotes": ai_result["notes"],
                "sourceUrl": url
            }
        )

        # Mark job as completed
        await db.crawljob.update(
            where={"id": job_id},
            data={
                "status": "completed",
                "completedAt": datetime.utcnow()
            }
        )

    except Exception as e:
        # Mark job as failed
        await db.crawljob.update(
            where={"id": job_id},
            data={
                "status": "failed",
                "error": str(e),
                "completedAt": datetime.utcnow()
            }
        )


@router.post("", response_model=CrawlJobResponse)
async def trigger_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """Trigger a single crawl job"""
    db = get_db()

    # Verify website exists
    website = await db.targetwebsite.find_unique(where={"id": request.website_id})
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    # Create job
    job = await db.crawljob.create(
        data={
            "websiteId": request.website_id,
            "url": str(request.url),
            "status": "pending"
        }
    )

    # Queue background task
    background_tasks.add_task(
        process_crawl,
        job.id,
        request.website_id,
        str(request.url),
        request.use_javascript
    )

    return CrawlJobResponse(job_id=job.id, status="pending")


@router.post("/batch", response_model=list[CrawlJobResponse])
async def trigger_batch_crawl(request: BatchCrawlRequest, background_tasks: BackgroundTasks):
    """Trigger multiple crawl jobs"""
    db = get_db()

    # Verify website exists
    website = await db.targetwebsite.find_unique(where={"id": request.website_id})
    if not website:
        raise HTTPException(status_code=404, detail="Website not found")

    jobs = []

    for url in request.urls:
        # Create job
        job = await db.crawljob.create(
            data={
                "websiteId": request.website_id,
                "url": str(url),
                "status": "pending"
            }
        )

        jobs.append(CrawlJobResponse(job_id=job.id, status="pending"))

        # Queue background task
        background_tasks.add_task(
            process_crawl,
            job.id,
            request.website_id,
            str(url),
            request.use_javascript
        )

    return jobs


@router.get("/{job_id}", response_model=CrawlJobDetail)
async def get_crawl_job(job_id: str):
    """Get crawl job status and details"""
    db = get_db()

    result = await db.crawljob.find_unique(where={"id": job_id})

    if not result:
        raise HTTPException(status_code=404, detail="Crawl job not found")

    return CrawlJobDetail(
        id=result.id,
        websiteId=result.websiteId,
        url=result.url,
        status=result.status,
        error=result.error,
        createdAt=result.createdAt.isoformat(),
        completedAt=result.completedAt.isoformat() if result.completedAt else None
    )
