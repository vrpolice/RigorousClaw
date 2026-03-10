import asyncio
from langchain_core.tools import tool
from crawl4ai import AsyncWebCrawler

@tool
def robust_web_crawler(url: str, instruction: str = "Extract all text content.") -> str:
    """
    Crawl a complex dynamic website or web app using crawl4ai.
    Use this when standard HTTP requests or Jina reader fail to get the page content, or when specific data needs extraction.
    """
    async def extract_data():
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=url,
                word_count_threshold=10,
                extraction_strategy=None,
                chunking_strategy=None,
                bypass_cache=True,
            )
            return result.markdown

    # Since this is a synchronous tool wrapper for LangChain, we run the async loop
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    if loop.is_running():
        # Handle if already in an event loop (e.g., inside FastAPI or Telegram bot)
        # Note: In a real async-first agent, we'd define the tool as async natively.
        import nest_asyncio
        nest_asyncio.apply()
        return loop.run_until_complete(extract_data())
    else:
        return loop.run_until_complete(extract_data())
