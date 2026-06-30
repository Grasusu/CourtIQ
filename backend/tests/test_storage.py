"""Upload storage adapter tests."""

from pathlib import Path

from app.storage.uploads import LocalUploadStorage


def test_local_upload_storage_saves_uploaded_bytes(tmp_path):
    storage = LocalUploadStorage(base_dir=tmp_path)

    stored_upload = storage.save("../box-score.csv", b"game_date,player\n2026-02-12,Alex\n")

    stored_path = Path(stored_upload.stored_path)
    assert stored_upload.original_filename == "box-score.csv"
    assert stored_upload.storage_key.endswith(".csv")
    assert stored_path.parent == tmp_path
    assert stored_path.read_bytes() == b"game_date,player\n2026-02-12,Alex\n"


def test_local_upload_storage_defaults_missing_filename(tmp_path):
    storage = LocalUploadStorage(base_dir=tmp_path)

    stored_upload = storage.save(None, b"")

    assert stored_upload.original_filename == "upload.csv"
    assert stored_upload.storage_key.endswith(".csv")
