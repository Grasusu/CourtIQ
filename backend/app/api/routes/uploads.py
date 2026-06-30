"""Upload routes."""

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.jobs.upload_queue import get_upload_queue
from app.models.user import User
from app.schemas.upload import UploadJobRead
from app.services.upload_service import (
    create_upload_job,
    get_upload_job,
    list_team_upload_jobs,
)
from app.storage.uploads import get_upload_storage


router = APIRouter(tags=["uploads"])


@router.post("/teams/{team_id}/uploads/box-score", response_model=UploadJobRead, status_code=201)
async def upload_box_score_route(
    team_id: int,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.filename and not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV uploads are supported")

    stored_upload = get_upload_storage().save(file.filename, await file.read())

    try:
        job = create_upload_job(
            db=db,
            team_id=team_id,
            filename=stored_upload.original_filename,
            stored_path=stored_upload.stored_path,
            owner_id=current_user.id,
        )
    except ValueError as exc:
        if "does not exist" in str(exc):
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        raise HTTPException(status_code=400, detail=str(exc)) from exc

    get_upload_queue(background_tasks).enqueue(job.id)
    return job


@router.get("/uploads/jobs/{job_id}", response_model=UploadJobRead)
def get_upload_job_route(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = get_upload_job(db, job_id, owner_id=current_user.id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Upload job {job_id} does not exist")

    return job


@router.get("/teams/{team_id}/uploads/jobs", response_model=list[UploadJobRead])
def list_team_upload_jobs_route(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        return list_team_upload_jobs(db, team_id, owner_id=current_user.id)
    except ValueError as exc:
        if "does not exist" in str(exc):
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        raise HTTPException(status_code=400, detail=str(exc)) from exc
