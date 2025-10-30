import asyncio
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CrawlerRunConfig,
    DefaultMarkdownGenerator,
    PruningContentFilter,
)
from playwright.async_api import async_playwright
from app.config import MAX_RETRIES
import logging

# Configure logging
logger = logging.getLogger(__name__)

async def crawl(url: str, use_javascript: bool = False, config: dict = None) -> str:
    """
    Fetch HTML from URL using Crawl4AI with Playwright.
    Args:
        url (str): Target URL
        use_javascript (bool): Enable JS rendering via headless browser
        config (dict): Optional runtime configuration overrides
    Returns:
        str: Extracted HTML content
    """
    logger.info(f"Starting crawl for URL: {url}, JS: {use_javascript}")
    loop = asyncio.get_running_loop()
    logger.info(f"Using event loop: {loop} (running={loop.is_running()}, closed={loop.is_closed()})")

    # Browser configuration
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        viewport_width=1920,
        viewport_height=1080,
    )
    # Default crawler configuration
    default_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter()
        ),
        wait_until="networkidle" if use_javascript else "commit",
        delay_before_return_html=10.0,  # Increased for stability
        wait_for="article, main, [role='main'], .event, [class*='event']",
        excluded_tags=[
            "nav",
            "footer",
            "header",
            "aside",
            "script",
            "style",
            "noscript",
        ],
        exclude_external_links=False,
        page_timeout=240000,  # Increased to 4 minutes
        process_iframes=False,
    )
    # Apply any user overrides
    if config:
        for key, value in config.items():
            if hasattr(default_config, key):
                setattr(default_config, key, value)

    # Pre-initialize Playwright browser if JS is enabled
    if use_javascript:
        logger.info("Pre-initializing Playwright browser...")
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                logger.info("Playwright browser launched successfully")
                await browser.close()
        except Exception as e:
            logger.error(f"Playwright pre-launch failed: {str(e)}")
            raise

    # Retry mechanism with detailed logging
    for attempt in range(MAX_RETRIES):
        try:
            async with AsyncWebCrawler(config=browser_config) as crawler:
                logger.info(f"Attempt {attempt + 1}/{MAX_RETRIES} to launch crawler for {url}")
                logger.info("Initiating browser connection...")
                result = await crawler.arun(url=url, config=default_config)
                if not result.success:
                    err = result.error_message or "Unknown error"
                    if attempt < MAX_RETRIES - 1:
                        logger.warning(f"[RETRY {attempt + 1}/{MAX_RETRIES}] Crawl failed: {err}")
                        await asyncio.sleep(2 ** attempt)
                        continue
                    raise Exception(err)
                logger.info(f"[SUCCESS] Crawled: {url}")
                logger.info(f"[INFO] Final URL: {result.url}")
                logger.info(f"[INFO] Status: {result.status_code}")
                logger.info(f"[INFO] HTML length: {len(result.html)}")
                logger.info(f"[INFO] Markdown length: {len(result.markdown.raw_markdown)}")
                if result.url != url and (
                    "scrapingbee" in result.url.lower()
                    or "cloudflare" in result.url.lower()
                ):
                    raise Exception(
                        f"Redirected to {result.url} — possible bot detection"
                    )
                return result.html
        except Exception as e:
            logger.error(f"Exception during attempt {attempt + 1}: {str(e)}")
            if attempt == MAX_RETRIES - 1:
                logger.error(f"Failed after {MAX_RETRIES} attempts: {str(e)}")
                raise Exception(f"Failed after {MAX_RETRIES} attempts: {str(e)}")
            logger.warning(f"[RETRY {attempt + 1}/{MAX_RETRIES}] Retrying after error: {str(e)}")
            await asyncio.sleep(2 ** attempt)
    raise Exception(f"Failed to crawl {url} after {MAX_RETRIES} attempts")