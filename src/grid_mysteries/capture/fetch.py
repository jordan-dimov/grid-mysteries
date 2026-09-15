"""Fetching for the capture job: one small interface, one HTTP implementation.

Strategies take a `Fetcher` so tests run against canned responses. The
HTTP implementation follows redirects, identifies itself, and keeps the
headers the manifest records (Last-Modified, ETag, Content-Type).
"""

import hashlib
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

USER_AGENT = "grid-mysteries-capture/1 (research; jdimov@a115.co.uk)"
KEPT_HEADERS = ("last-modified", "etag", "content-type", "content-length", "date")
#: Responses larger than this are streamed to a temporary file, never held whole
#: in memory: the job runs in 512 MB and one NESO dump is 192 MB.
SPOOL_THRESHOLD = 8 * 1024 * 1024
CHUNK = 1024 * 1024


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    body: bytes = b""
    headers: dict[str, str] = field(default_factory=dict)
    #: Set instead of `body` for a large response spooled to disk.
    path: Path | None = None
    size: int = 0
    sha256: str = ""

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    def kept_headers(self) -> dict[str, str]:
        return {k: v for k, v in self.headers.items() if k in KEPT_HEADERS}

    def text(self) -> str:
        """The body as text; only for responses that are parsed (small ones)."""
        if self.path is not None:
            return self.path.read_text(encoding="utf-8", errors="replace")
        return self.body.decode("utf-8", errors="replace")

    def digest(self) -> str:
        return self.sha256 or hashlib.sha256(self.body).hexdigest()

    def length(self) -> int:
        return self.size if self.path is not None else len(self.body)


class Fetcher(Protocol):
    def get(
        self, url: str, *, data: bytes | None = None, content_type: str | None = None
    ) -> Response: ...


class HttpFetcher:
    def __init__(self, timeout_seconds: float = 120.0) -> None:
        import httpx

        self.client = httpx.Client(
            timeout=timeout_seconds, follow_redirects=True, headers={"User-Agent": USER_AGENT}
        )

    def get(
        self, url: str, *, data: bytes | None = None, content_type: str | None = None
    ) -> Response:
        headers = {"Content-Type": content_type} if content_type else {}
        if data is not None:
            response = self.client.post(url, content=data, headers=headers)
            return Response(
                url=str(response.url),
                status=response.status_code,
                body=response.content,
                headers={k.lower(): v for k, v in response.headers.items()},
            )
        with self.client.stream("GET", url) as stream:
            kept = {k.lower(): v for k, v in stream.headers.items()}
            digest = hashlib.sha256()
            size = 0
            with tempfile.NamedTemporaryFile(prefix="capture-", delete=False) as spool:
                for chunk in stream.iter_bytes(CHUNK):
                    spool.write(chunk)
                    digest.update(chunk)
                    size += len(chunk)
                name = spool.name
            path = Path(name)
            if size <= SPOOL_THRESHOLD:
                body = path.read_bytes()
                path.unlink()
                return Response(
                    url=str(stream.url), status=stream.status_code, body=body, headers=kept
                )
            return Response(
                url=str(stream.url),
                status=stream.status_code,
                headers=kept,
                path=path,
                size=size,
                sha256=digest.hexdigest(),
            )


class CannedFetcher:
    """Test double: URL to Response, with the calls recorded."""

    def __init__(self, responses: dict[str, Response | bytes]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, bytes | None]] = []
        self.content_types: list[str | None] = []

    def get(
        self, url: str, *, data: bytes | None = None, content_type: str | None = None
    ) -> Response:
        self.calls.append((url, data))
        self.content_types.append(content_type)
        canned = self.responses.get(url)
        if canned is None:
            return Response(url=url, status=404, body=b"", headers={})
        if isinstance(canned, bytes):
            return Response(url=url, status=200, body=canned, headers={})
        return canned
