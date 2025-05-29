"""
FastAPI server for web crawling with Crawl4AI (smart_crawl_url endpoint).

This exposes the smart_crawl_url logic as a REST API endpoint, using the same core logic as the MCP tool.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from crawl4ai import AsyncWebCrawler, BrowserConfig
from fastapi.responses import HTMLResponse
import os
from src.api.crawl import router as crawl_router
from src.api.color import router as color_router

fastapi_crawler = None


@asynccontextmanager
async def lifespan(app):
    global fastapi_crawler
    browser_config = BrowserConfig(headless=True, verbose=False)
    fastapi_crawler = AsyncWebCrawler(config=browser_config)
    await fastapi_crawler.__aenter__()
    logging.info("FastAPI crawler initialized.")
    # Attach to app.state so it's available in requests
    app.state.fastapi_crawler = fastapi_crawler
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

app.include_router(crawl_router)
app.include_router(color_router)


@app.get("/", response_class=HTMLResponse)
async def root():
    html_path = os.path.join(os.path.dirname(__file__), "static", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
