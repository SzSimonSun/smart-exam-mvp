"""Storage helpers for handling answer sheet uploads."""

from __future__ import annotations

import io
import logging
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse
from uuid import uuid4

from minio import Minio
from minio.error import S3Error

from .config import settings

logger = logging.getLogger(__name__)


def _build_client() -> Minio:
    parsed = urlparse(settings.minio_endpoint)
    if not parsed.scheme or not parsed.netloc:
        raise RuntimeError("Invalid MinIO endpoint configuration")

    secure = parsed.scheme == "https"
    return Minio(
        parsed.netloc,
        access_key=settings.minio_access_key,
        secret_key=settings.minio_secret_key,
        secure=secure,
    )


@lru_cache(maxsize=1)
def get_minio_client() -> Minio:
    """Return a cached MinIO client instance."""

    client = _build_client()
    try:
        if not client.bucket_exists(settings.minio_bucket_name):
            client.make_bucket(settings.minio_bucket_name)
    except S3Error as exc:
        logger.error("MinIO bucket bootstrap failed: %s", exc, exc_info=True)
        raise RuntimeError("Unable to prepare storage bucket") from exc

    return client


def _sanitise_filename(filename: str) -> str:
    stem = Path(filename).name
    cleaned = re.sub(r"[^A-Za-z0-9_.-]", "_", stem)
    return cleaned or "upload.bin"


def store_answer_sheet_file(
    *, original_filename: str, data: bytes, content_type: str | None
) -> str:
    """Persist an uploaded answer sheet to MinIO and return the object key."""

    client = get_minio_client()

    object_key = f"answer-sheets/{uuid4().hex}_{_sanitise_filename(original_filename)}"

    try:
        client.put_object(
            settings.minio_bucket_name,
            object_key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
    except S3Error as exc:
        logger.error("Failed to upload answer sheet to MinIO: %s", exc, exc_info=True)
        raise RuntimeError("Unable to store uploaded file") from exc

    return object_key

