"""Upload routes."""

from os import getenv
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.upload import UploadResult
from app.services.upload_service import import_box_score_csv


router = APIRouter(tags=["uploads"])


@router.post("/teams/{team_id}/uploads/box-score", response_model=UploadResult, status_code=201)
async def upload_box_score_route(
    team_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.filename and not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV uploads are supported")

    upload_dir = Path(getenv("LOCAL_UPLOAD_DIR", "local_uploads"))
    upload_dir.mkdir(parents=True, exist_ok=True)
    upload_path = upload_dir / f"{uuid4()}.csv"
    upload_path.write_bytes(await file.read())

    try:
        return import_box_score_csv(db, team_id, upload_path)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
