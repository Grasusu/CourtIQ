"""Upload storage adapters."""

from dataclasses import dataclass
from os import getenv
from pathlib import Path
from typing import Protocol
from urllib.parse import quote
from uuid import uuid4

import httpx


@dataclass(frozen=True)
class StoredUpload:
    original_filename: str
    storage_key: str
    stored_path: str


class UploadStorage(Protocol):
    def save(
        self,
        filename: str | None,
        content: bytes,
        namespace: str | None = None,
    ) -> StoredUpload: ...

    def read(self, stored_path: str) -> bytes: ...


class LocalUploadStorage:
    def __init__(self, base_dir: str | Path | None = None) -> None:
        self.base_dir = Path(base_dir or getenv("LOCAL_UPLOAD_DIR", "local_uploads"))

    def save(
        self,
        filename: str | None,
        content: bytes,
        namespace: str | None = None,
    ) -> StoredUpload:
        original_filename = _safe_filename(filename)
        storage_key = _storage_key(original_filename, namespace)

        stored_path = self.base_dir / storage_key
        stored_path.parent.mkdir(parents=True, exist_ok=True)
        stored_path.write_bytes(content)

        return StoredUpload(
            original_filename=original_filename,
            storage_key=storage_key,
            stored_path=str(stored_path),
        )

    def read(self, stored_path: str) -> bytes:
        return Path(stored_path).read_bytes()


class SupabaseUploadStorage:
    def __init__(
        self,
        supabase_url: str,
        secret_key: str,
        bucket: str = "courtiq-uploads",
        timeout_seconds: float = 30.0,
    ) -> None:
        self.supabase_url = supabase_url.rstrip("/")
        self.secret_key = secret_key
        self.bucket = bucket
        self.timeout_seconds = timeout_seconds

    def save(
        self,
        filename: str | None,
        content: bytes,
        namespace: str | None = None,
    ) -> StoredUpload:
        original_filename = _safe_filename(filename)
        storage_key = _storage_key(original_filename, namespace)
        response = self._request(
            "POST",
            storage_key,
            content=content,
            extra_headers={"Content-Type": "text/csv", "x-upsert": "false"},
        )
        _raise_for_storage_error(response, "upload")

        return StoredUpload(
            original_filename=original_filename,
            storage_key=storage_key,
            stored_path=storage_key,
        )

    def read(self, stored_path: str) -> bytes:
        response = self._request("GET", stored_path, authenticated=True)
        _raise_for_storage_error(response, "download")
        return response.content

    def _request(
        self,
        method: str,
        storage_key: str,
        *,
        content: bytes | None = None,
        extra_headers: dict[str, str] | None = None,
        authenticated: bool = False,
    ) -> httpx.Response:
        route = "object/authenticated" if authenticated else "object"
        bucket = quote(self.bucket, safe="")
        object_path = quote(storage_key, safe="/")
        url = f"{self.supabase_url}/storage/v1/{route}/{bucket}/{object_path}"
        headers = {"apikey": self.secret_key}
        if not self.secret_key.startswith("sb_secret_"):
            headers["Authorization"] = f"Bearer {self.secret_key}"
        if extra_headers:
            headers.update(extra_headers)

        try:
            return httpx.request(
                method,
                url,
                headers=headers,
                content=content,
                timeout=self.timeout_seconds,
            )
        except httpx.HTTPError as exc:
            raise RuntimeError("Supabase Storage is unavailable") from exc


def get_upload_storage() -> UploadStorage:
    backend = getenv("UPLOAD_STORAGE_BACKEND", "local").strip().lower()
    if backend == "local":
        return LocalUploadStorage()

    if backend == "supabase":
        supabase_url = getenv("SUPABASE_URL", "").strip()
        secret_key = getenv("SUPABASE_SECRET_KEY", "").strip()
        bucket = getenv("SUPABASE_STORAGE_BUCKET", "courtiq-uploads").strip()
        if not supabase_url or not secret_key or not bucket:
            raise RuntimeError("Supabase upload storage is not fully configured")

        return SupabaseUploadStorage(supabase_url, secret_key, bucket)

    raise RuntimeError(f"Unsupported upload storage backend: {backend}")


def _safe_filename(filename: str | None) -> str:
    if not filename:
        return "upload.csv"

    safe_name = Path(filename.replace("\x00", "")).name.strip()
    return safe_name or "upload.csv"


def _storage_key(filename: str, namespace: str | None) -> str:
    extension = Path(filename).suffix.lower() or ".csv"
    generated_name = f"{uuid4()}{extension}"
    if not namespace:
        return generated_name

    namespace_parts = [part for part in namespace.strip("/").split("/") if part]
    if any(part in {".", ".."} for part in namespace_parts):
        raise ValueError("Invalid upload storage namespace")

    return "/".join([*namespace_parts, generated_name])


def _raise_for_storage_error(response: httpx.Response, action: str) -> None:
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"Supabase Storage {action} failed with status {response.status_code}"
        ) from exc
