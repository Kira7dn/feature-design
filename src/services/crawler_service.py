from crawl4ai import CrawlerRunConfig, CacheMode
from fastapi import Request


async def run_crawl(url: str, request: Request):
    # Get the crawler instance from app state
    fastapi_crawler = request.app.state.fastapi_crawler
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    result = await fastapi_crawler.arun(url=url, config=run_config)
    if result.success and result.markdown:
        return {
            "success": True,
            "url": url,
            "content_length": len(result.markdown),
            "markdown": result.markdown,
            "links_count": {
                "internal": len(result.links.get("internal", [])),
                "external": len(result.links.get("external", [])),
            },
        }
    else:
        return {"success": False, "url": url, "error": result.error_message}
