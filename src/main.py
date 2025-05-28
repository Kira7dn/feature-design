"""
FastAPI server for web crawling with Crawl4AI (smart_crawl_url endpoint).

This exposes the smart_crawl_url logic as a REST API endpoint, using the same core logic as the MCP tool.
"""

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

fastapi_crawler = None


@asynccontextmanager
async def lifespan(app):
    global fastapi_crawler
    browser_config = BrowserConfig(headless=True, verbose=False)
    fastapi_crawler = AsyncWebCrawler(config=browser_config)
    await fastapi_crawler.__aenter__()
    logging.info("FastAPI crawler initialized.")
    try:
        yield
    finally:
        if fastapi_crawler:
            await fastapi_crawler.__aexit__(None, None, None)
            logging.info("FastAPI crawler shutdown.")


app = FastAPI(title="Crawl4AI FastAPI Server", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def root():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Feature Extraction API</title>
            <style>
                body { 
                    font-family: Arial, sans-serif;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    line-height: 1.6;
                }
                h1 { color: #2c3e50; }
                .links a {
                    display: inline-block;
                    margin: 10px;
                    padding: 10px 20px;
                    background: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                }
                .links a:hover { background: #2980b9; }
            </style>
        </head>
        <body>
            <h1>Feature Extraction API</h1>
            <p>Welcome to the Low-Level Feature Extraction API. This service provides image analysis capabilities including:</p>
            <ul>
                <li>Color Analysis</li>
                <li>Text Recognition</li>
            </ul>
            <div class="links">
                <a href="/docs">API Documentation</a>
            </div>
            <p><small>Version: 1.0.0</small></p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.post("/crawl")
async def crawl_single(
    url: str = Query(..., description="URL of the web page to crawl")
):
    """
    FastAPI endpoint to crawl a single web page and return its markdown content.
    """
    try:
        crawler = fastapi_crawler
        # Use the same logic as crawl_single_page from MCP, but just return the result
        run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS, stream=False)
        result = await crawler.arun(url=url, config=run_config)
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
            return JSONResponse(
                status_code=400,
                content={"success": False, "url": url, "error": result.error_message},
            )
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "url": url, "error": str(e)}
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
