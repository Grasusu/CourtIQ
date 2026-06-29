"""Worker entrypoints for upload processing."""

from app.services.upload_service import process_upload_job


def run_upload_job(job_id: int) -> None:
    process_upload_job(job_id)
