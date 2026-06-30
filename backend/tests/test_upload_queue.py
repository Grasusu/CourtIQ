"""Upload queue adapter tests."""

from app.jobs.upload_queue import BackgroundUploadQueue
from app.workers.upload_worker import run_upload_job


class FakeBackgroundTasks:
    def __init__(self) -> None:
        self.tasks: list[tuple[object, tuple[object, ...]]] = []

    def add_task(self, task, *args) -> None:
        self.tasks.append((task, args))


def test_background_upload_queue_enqueues_worker_task():
    background_tasks = FakeBackgroundTasks()
    queue = BackgroundUploadQueue(background_tasks)  # type: ignore[arg-type]

    queue.enqueue(42)

    assert background_tasks.tasks == [(run_upload_job, (42,))]
