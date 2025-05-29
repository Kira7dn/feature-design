from crawl4ai import CrawlerRunConfig, CacheMode, AsyncWebCrawler, BrowserConfig
from fastapi import Request
from src.utils import extract_dribbble_query, extract_design_features
import re
import asyncio


def create_markdown_generation_result(raw_markdown: str):
    from crawl4ai.models import MarkdownGenerationResult

    return MarkdownGenerationResult(
        raw_markdown=raw_markdown,
        markdown_with_citations="",
        references_markdown="",
        fit_markdown="",
        fit_html="",
    )


async def run_crawl(url: str, request: Request):
    # Get the crawler instance from app state
    fastapi_crawler = request.app.state.fastapi_crawler
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
    result = await fastapi_crawler.arun(url=url, config=run_config)
    if result.success and result.markdown:
        if isinstance(result.markdown, str):
            from crawl4ai.models import MarkdownGenerationResult

            # Use a helper function to construct the MarkdownGenerationResult object.
            result.markdown_generation_result = create_markdown_generation_result(
                result.markdown
            )

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
        if re.match(r"https://dribbble.com/shots/", url):
            response["result"] = extract_design_features(result.markdown)

        return response
    else:
        return {"success": False, "url": url, "error": result.error_message}


def run_crawl_sync(url: str):
    # This function is for RQ worker (sync context)
    browser_config = BrowserConfig(headless=True, verbose=False)
    fastapi_crawler = AsyncWebCrawler(config=browser_config)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(fastapi_crawler.arun(url=url, config=run_config))
    loop.close()

    if result.success and result.markdown:
        if isinstance(result.markdown, str):
            from crawl4ai.models import MarkdownGenerationResult

            result._markdown = MarkdownGenerationResult(
                raw_markdown=result.markdown,
                markdown_with_citations="",
                references_markdown="",
                fit_markdown="",
                fit_html="",
            )

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

        if re.match(r"https://dribbble.com/search/shots/", url):
            response["result"] = extract_dribbble_query(result.markdown)
        elif re.match(r"https://dribbble.com/shots/", url):
            response["result"] = extract_design_features(result.markdown)

        return response

    return {"success": False, "url": url, "error": result.error_message}
