"""Where captured bytes go: an object store with a local and an S3 form.

The job writes and reads keys; it never lists a bucket to decide what to
do (the status object carries what it needs). `LocalStore` is the test
double and the laptop mirror; `S3Store` is production. Neither deletes.
"""

import shutil
from collections.abc import Iterator
from pathlib import Path
from typing import Any, Protocol


class ObjectStore(Protocol):
    def put(
        self, key: str, data: bytes, *, content_type: str = "application/octet-stream"
    ) -> None: ...

    def put_file(
        self, key: str, path: Path, *, content_type: str = "application/octet-stream"
    ) -> None: ...

    def get(self, key: str) -> bytes | None: ...

    def exists(self, key: str) -> bool: ...

    def keys(self, prefix: str) -> Iterator[str]: ...


class LocalStore:
    """Keys as paths under a root directory."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def _path(self, key: str) -> Path:
        if key.startswith("/") or ".." in key.split("/"):
            raise ValueError(f"unsafe key {key!r}")
        return self.root / key

    def put(self, key: str, data: bytes, *, content_type: str = "application/octet-stream") -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def put_file(
        self, key: str, path: Path, *, content_type: str = "application/octet-stream"
    ) -> None:
        target = self._path(key)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)

    def get(self, key: str) -> bytes | None:
        path = self._path(key)
        return path.read_bytes() if path.exists() else None

    def exists(self, key: str) -> bool:
        return self._path(key).exists()

    def keys(self, prefix: str) -> Iterator[str]:
        base = self._path(prefix)
        if not base.exists():
            return
        for path in sorted(p for p in base.rglob("*") if p.is_file()):
            yield path.relative_to(self.root).as_posix()


class S3Store:
    """One bucket; the credential in the environment decides what is allowed."""

    def __init__(self, bucket: str, client: Any | None = None) -> None:
        if client is None:
            import boto3

            client = boto3.client("s3")
        self.bucket = bucket
        self.client = client

    def put(self, key: str, data: bytes, *, content_type: str = "application/octet-stream") -> None:
        self.client.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)

    def put_file(
        self, key: str, path: Path, *, content_type: str = "application/octet-stream"
    ) -> None:
        with path.open("rb") as handle:
            self.client.upload_fileobj(
                handle, self.bucket, key, ExtraArgs={"ContentType": content_type}
            )

    def get(self, key: str) -> bytes | None:
        try:
            return self.client.get_object(Bucket=self.bucket, Key=key)["Body"].read()
        except self.client.exceptions.NoSuchKey:
            return None

    def exists(self, key: str) -> bool:
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except Exception:  # noqa: BLE001 - botocore raises a ClientError with 404 inside
            return False

    def keys(self, prefix: str) -> Iterator[str]:
        paginator = self.client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for item in page.get("Contents", []):
                yield item["Key"]


def store_from_url(url: str) -> ObjectStore:
    """`s3://bucket` or a local directory path."""
    if url.startswith("s3://"):
        return S3Store(url.removeprefix("s3://").strip("/"))
    return LocalStore(Path(url))
