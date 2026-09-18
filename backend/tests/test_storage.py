"""Upload storage adapter tests."""

from pathlib import Path

import httpx
import pytest

from app.storage.uploads import LocalUploadStorage, SupabaseUploadStorage, get_upload_storage


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


def test_local_upload_storage_uses_namespace_and_reads_bytes(tmp_path):
    storage = LocalUploadStorage(base_dir=tmp_path)

    stored_upload = storage.save(
        "box-score.csv",
        b"game_date,player\n2026-02-12,Alex\n",
        namespace="users/4/teams/9",
    )

    assert stored_upload.storage_key.startswith("users/4/teams/9/")
    assert storage.read(stored_upload.stored_path) == b"game_date,player\n2026-02-12,Alex\n"


def test_supabase_upload_storage_uploads_and_downloads_private_object(monkeypatch):
    requests: list[tuple[str, str, dict[str, str], bytes | None]] = []

    def fake_request(method, url, *, headers, content, timeout):
        requests.append((method, url, headers, content))
        request = httpx.Request(method, url)
        if method == "POST":
            return httpx.Response(200, request=request, json={"Key": "stored.csv"})
        return httpx.Response(200, request=request, content=b"stored csv")

    monkeypatch.setattr("app.storage.uploads.httpx.request", fake_request)
    storage = SupabaseUploadStorage(
        "https://project.supabase.co/",
        "sb_secret_test",
        bucket="courtiq-uploads",
    )

    stored_upload = storage.save("stats.csv", b"stored csv", namespace="users/2/teams/7")
    downloaded = storage.read(stored_upload.stored_path)

    assert stored_upload.storage_key.startswith("users/2/teams/7/")
    assert downloaded == b"stored csv"
    assert requests[0][0] == "POST"
    assert "/storage/v1/object/courtiq-uploads/users/2/teams/7/" in requests[0][1]
    assert requests[0][2]["apikey"] == "sb_secret_test"
    assert "Authorization" not in requests[0][2]
    assert requests[0][3] == b"stored csv"
    assert requests[1][0] == "GET"
    assert "/storage/v1/object/authenticated/courtiq-uploads/" in requests[1][1]


def test_get_upload_storage_selects_supabase_from_environment(monkeypatch):
    monkeypatch.setenv("UPLOAD_STORAGE_BACKEND", "supabase")
    monkeypatch.setenv("SUPABASE_URL", "https://project.supabase.co")
    monkeypatch.setenv("SUPABASE_SECRET_KEY", "sb_secret_test")
    monkeypatch.setenv("SUPABASE_STORAGE_BUCKET", "court-data")

    storage = get_upload_storage()

    assert isinstance(storage, SupabaseUploadStorage)
    assert storage.bucket == "court-data"


def test_get_upload_storage_rejects_incomplete_supabase_config(monkeypatch):
    monkeypatch.setenv("UPLOAD_STORAGE_BACKEND", "supabase")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SECRET_KEY", raising=False)

    with pytest.raises(RuntimeError, match="not fully configured"):
        get_upload_storage()


def test_supabase_storage_error_includes_safe_api_detail(monkeypatch):
    def fake_request(method, url, *, headers, content, timeout):
        request = httpx.Request(method, url)
        return httpx.Response(
            400,
            request=request,
            json={"error": "InvalidRequest", "message": "Unsupported content type"},
        )

    monkeypatch.setattr("app.storage.uploads.httpx.request", fake_request)
    storage = SupabaseUploadStorage(
        "https://project.supabase.co",
        "sb_secret_test",
        bucket="courtiq-uploads",
    )

    with pytest.raises(
        RuntimeError,
        match="400: InvalidRequest - Unsupported content type",
    ):
        storage.save("stats.csv", b"game_date,player\n")
