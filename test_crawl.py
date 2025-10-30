import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, DefaultMarkdownGenerator, PruningContentFilter

async def test_crawl():
    """Test crawling the ConnectJew event page"""

    url = "https://hottrix.in/"

    # Configure browser
    browser_config = BrowserConfig(
        headless=False,  # Show browser to see what's happening
        verbose=True,
    )
 

    # Try different configurations
    configs = [
        {
            "name": "Config 1: domcontentloaded + 10s delay",
            "config": CrawlerRunConfig(
                wait_until="domcontentloaded",
                delay_before_return_html=10.0,
                page_timeout=90000,
                verbose=True,
            )
        },
        {
            "name": "Config 2: commit + 5s delay",
            "config": CrawlerRunConfig(
                wait_until="commit",
                delay_before_return_html=5.0,
                page_timeout=90000,
                verbose=True,
            )
        },
    ]

    async with AsyncWebCrawler(config=browser_config) as crawler:
        for test_config in configs:
            print(f"\n{'='*60}")
            print(f"Testing: {test_config['name']}")
            print(f"{'='*60}\n")

            try:
                result = await crawler.arun(url=url, config=test_config['config'])

                if result.success:
                    print(f"✅ SUCCESS!")
                    print(f"Status: {result.status_code}")
                    print(f"HTML length: {len(result.html)} chars")
                    print(f"Markdown length: {len(result.markdown.raw_markdown)} chars")
                    print(f"\nFirst 500 chars of markdown:")
                    print("-" * 60)
                    print(result.markdown.raw_markdown[:500])
                    print("-" * 60)

                    # Save full markdown
                    with open(f"test_output_{test_config['name'].replace(' ', '_').replace(':', '')}.md", "w") as f:
                        f.write(result.markdown.raw_markdown)
                    print(f"\nSaved full markdown to test_output_*.md")
                else:
                    print(f"❌ FAILED: {result.error_message}")

            except Exception as e:
                print(f"❌ EXCEPTION: {str(e)}")

            print("\n")
            await asyncio.sleep(2)  # Wait between tests

if __name__ == "__main__":
    asyncio.run(test_crawl())
