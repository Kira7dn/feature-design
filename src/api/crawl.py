from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from src.services.crawler_service import run_crawl

router = APIRouter()


@router.post("/crawl")
async def crawl_single(
    url: str = Query(..., description="URL of the web page to crawl")
):
    try:
        result = await run_crawl(url)
        if result["success"]:
            return result
        else:
            return JSONResponse(status_code=400, content=result)
    except Exception as e:
        return JSONResponse(
            status_code=500, content={"success": False, "url": url, "error": str(e)}
        )
