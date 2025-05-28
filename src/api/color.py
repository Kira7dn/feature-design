from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from src.services.color_service import extract_ui_colors

router = APIRouter()


@router.post("/colors")
async def extract_colors_from_url(
    url: str = Query(..., description="Image URL to extract colors from")
):
    try:
        colors = extract_ui_colors(url)
        return {"success": True, "url": url, "colors": colors}
    except Exception as e:
        return JSONResponse(
            status_code=400, content={"success": False, "url": url, "error": str(e)}
        )
