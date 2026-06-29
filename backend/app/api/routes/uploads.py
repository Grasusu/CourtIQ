"""Upload routes."""

from os import getenv
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.upload import UploadJobRead
from app.services.upload_service import (
    create_upload_job,
    get_upload_job,
    list_team_upload_jobs,
    process_upload_job,
)


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

    upload_dir = Path(getenv("LOCAL_UPLOAD_DIR", "local_uploads"))
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_path = upload_dir / f"{uuid4()}.csv"
    upload_path.write_bytes(await file.read())

    try:
        job = create_upload_job(
            db=db,
            team_id=team_id,
            filename=file.filename or upload_path.name,
            stored_path=upload_path,
            owner_id=current_user.id,
        )
    except ValueError as exc:
        if "does not exist" in str(exc):
            raise HTTPException(status_code=404, detail=str(exc)) from exc

        raise HTTPException(status_code=400, detail=str(exc)) from exc

    background_tasks.add_task(process_upload_job, job.id)
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
