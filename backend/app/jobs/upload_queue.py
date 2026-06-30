"""Upload job queue adapters."""

from fastapi import BackgroundTasks

from app.workers.upload_worker import run_upload_job


class BackgroundUploadQueue:
    def __init__(self, background_tasks: BackgroundTasks) -> None:
        self.background_tasks = background_tasks

    def enqueue(self, upload_job_id: int) -> None:
        self.background_tasks.add_task(run_upload_job, upload_job_id)


def get_upload_queue(background_tasks: BackgroundTasks) -> BackgroundUploadQueue:
    return BackgroundUploadQueue(background_tasks)
