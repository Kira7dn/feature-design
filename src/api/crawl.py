from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from src.services.crawler_service import run_crawl_sync
from src.task_queue import task_queue
from rq.job import Job
from crawl4ai.models import MarkdownGenerationResult
import json

router = APIRouter()


def serialize_result(result):
    if isinstance(result, dict) and isinstance(
        result.get("markdown"), MarkdownGenerationResult
    ):
        result["markdown"] = {
            "raw_markdown": result["markdown"].raw_markdown,
            "markdown_with_citations": result["markdown"].markdown_with_citations,
            "references_markdown": result["markdown"].references_markdown,
            "fit_markdown": result["markdown"].fit_markdown,
            "fit_html": result["markdown"].fit_html,
        }
    return json.dumps(result)


def deserialize_result(result_str):
    result = json.loads(result_str)
    if isinstance(result, dict) and isinstance(result.get("markdown"), dict):
        result["markdown"] = MarkdownGenerationResult(
            raw_markdown=result["markdown"].get("raw_markdown"),
            markdown_with_citations=result["markdown"].get("markdown_with_citations"),
            references_markdown=result["markdown"].get("references_markdown"),
            fit_markdown=result["markdown"].get("fit_markdown"),
            fit_html=result["markdown"].get("fit_html"),
        )
    return result


def crawl_task(url):
    try:
        result = run_crawl_sync(url)
        return serialize_result(result)
    except Exception as e:
        return serialize_result({"success": False, "url": url, "error": str(e)})


@router.post("/crawl")
def crawl_single(url: str = Query(..., description="URL of the web page to crawl")):
    job = task_queue.enqueue(crawl_task, url)
    return {"job_id": job.get_id(), "status": job.get_status()}


@router.get("/crawl/status/{job_id}")
def get_crawl_job_status(job_id: str):
    try:
        job = Job.fetch(job_id, connection=task_queue.connection)
    except Exception as e:
        return {"status": "not_found", "error": str(e)}

    if job.is_finished:
        result = deserialize_result(job.result)
        if result is None:
            exc_info = getattr(job, "exc_info", None)
            return {
                "status": "failed",
                "error": exc_info or "Job failed with no result.",
            }
        return {"status": job.get_status(), "result": result}

    elif job.is_failed:
        exc_info = getattr(job, "exc_info", None)
        return {"status": "failed", "error": exc_info or "Job failed."}

    return {"status": job.get_status()}
