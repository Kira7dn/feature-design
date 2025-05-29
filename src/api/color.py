from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from src.services.color_service import extract_ui_colors
from src.task_queue import task_queue
from rq.job import Job

router = APIRouter()


def color_task(url):
    try:
        colors = extract_ui_colors(url)
        return {"success": True, "url": url, "colors": colors}
    except Exception as e:
        return {"success": False, "url": url, "error": str(e)}


@router.post("/colors")
def extract_colors_from_url(
    url: str = Query(..., description="Image URL to extract colors from")
):
    job = task_queue.enqueue(color_task, url)
    return {"job_id": job.get_id(), "status": job.get_status()}


@router.get("/colors/status/{job_id}")
def get_color_job_status(job_id: str):
    job = Job.fetch(job_id, connection=task_queue.connection)
    if job.is_finished:
        # Defensive: ensure result is always a dict to avoid attribute errors downstream
        result = job.result
        if not isinstance(result, dict):
            result = {"raw_result": result}
        return {"status": job.get_status(), "result": result}
    else:
        return {"status": job.get_status()}
