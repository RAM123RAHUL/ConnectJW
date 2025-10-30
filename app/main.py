import sys
import asyncio
import nest_asyncio
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import connect_db, disconnect_db
from app.api import websites, structure, crawl, events, reviews
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Force WindowsSelectorEventLoopPolicy for Playwright compatibility
if sys.platform.startswith("win"):
    try:
        logger.info("Forcing WindowsSelectorEventLoopPolicy for Playwright compatibility")
        policy = asyncio.WindowsSelectorEventLoopPolicy()
        asyncio.set_event_loop_policy(policy)
        # Set the current event loop to use the new policy
        loop = policy.new_event_loop()
        asyncio.set_event_loop(loop)
    except Exception as e:
        logger.error(f"Failed to set WindowsSelectorEventLoopPolicy: {e}")
        raise

# Patch for nested asyncio loops (important for FastAPI + Playwright)
nest_asyncio.apply()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup & Shutdown events"""
    logger.info("Connecting to database...")
    await connect_db()
    yield
    logger.info("Disconnecting from database...")
    await disconnect_db()

# Create FastAPI app
app = FastAPI(
    title="AI Event Scraper",
    description="Simple AI-powered event scraper using Playwright + GPT",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers
app.include_router(websites.router)
app.include_router(structure.router)
app.include_router(crawl.router)
app.include_router(events.router)
app.include_router(reviews.router)

@app.get("/")
async def root():
    return {"status": "ok", "message": "AI Event Scraper API running", "docs": "/docs"}

@app.get("/health")
async def health():
    return {"status": "healthy"}