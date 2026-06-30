"""Upload storage adapters."""

from dataclasses import dataclass
from os import getenv
from pathlib import Path
from uuid import uuid4


@dataclass(frozen=True)
class StoredUpload:
    original_filename: str
    storage_key: str
    stored_path: str


class LocalUploadStorage:
    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir or getenv("LOCAL_UPLOAD_DIR", "local_uploads"))

    def save(self, filename: str | None, content: bytes) -> StoredUpload:
        original_filename = _safe_filename(filename)
        extension = Path(original_filename).suffix.lower() or ".csv"
        storage_key = f"{uuid4()}{extension}"

        self.base_dir.mkdir(parents=True, exist_ok=True)
        stored_path = self.base_dir / storage_key
        stored_path.write_bytes(content)

        return StoredUpload(
            original_filename=original_filename,
            storage_key=storage_key,
            stored_path=str(stored_path),
        )


def get_upload_storage() -> LocalUploadStorage:
    return LocalUploadStorage()


def _safe_filename(filename: str | None) -> str:
    if not filename:
        return "upload.csv"

    safe_name = Path(filename.replace("\x00", "")).name.strip()
    return safe_name or "upload.csv"
