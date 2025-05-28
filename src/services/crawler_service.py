from crawl4ai import CrawlerRunConfig, CacheMode
from fastapi import Request
from src.utils import extract_dribbble_query, extract_design_features
import re


async def run_crawl(url: str, request: Request):
    # Get the crawler instance from app state
    fastapi_crawler = request.app.state.fastapi_crawler
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    result = await fastapi_crawler.arun(url=url, config=run_config)
    if result.success and result.markdown:
        response = {
            "success": True,
            "url": url,
            "content_length": len(result.markdown),
            "markdown": result.markdown,
            "links_count": {
                "internal": len(result.links.get("internal", [])),
                "external": len(result.links.get("external", [])),
            },
        }
        # If the URL matches Dribbble search shots, parse markdown with extract_dribbble_query
        if re.match(r"https://dribbble.com/search/shots/", url):
            response["result"] = extract_dribbble_query(result.markdown)
        # If the URL matches a Dribbble single shot, use extract_design_features
        elif re.match(r"https://dribbble.com/shots/", url):
            response["result"] = extract_design_features(result.markdown)
        return response
    else:
        return {"success": False, "url": url, "error": result.error_message}
