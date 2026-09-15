"""Fetching for the capture job: one small interface, one HTTP implementation.

Strategies take a `Fetcher` so tests run against canned responses. The
HTTP implementation follows redirects, identifies itself, and keeps the
headers the manifest records (Last-Modified, ETag, Content-Type).
"""

from dataclasses import dataclass, field
from typing import Protocol

USER_AGENT = "grid-mysteries-capture/1 (research; jdimov@a115.co.uk)"
KEPT_HEADERS = ("last-modified", "etag", "content-type", "content-length", "date")


@dataclass(frozen=True)
class Response:
    url: str
    status: int
    body: bytes
    headers: dict[str, str] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return 200 <= self.status < 300

    def kept_headers(self) -> dict[str, str]:
        return {k: v for k, v in self.headers.items() if k in KEPT_HEADERS}


class Fetcher(Protocol):
    def get(self, url: str, *, data: bytes | None = None) -> Response: ...


class HttpFetcher:
    def __init__(self, timeout_seconds: float = 120.0) -> None:
        import httpx

        self.client = httpx.Client(
            timeout=timeout_seconds, follow_redirects=True, headers={"User-Agent": USER_AGENT}
        )

    def get(self, url: str, *, data: bytes | None = None) -> Response:
        response = self.client.post(url, content=data) if data is not None else self.client.get(url)
        return Response(
            url=str(response.url),
            status=response.status_code,
            body=response.content,
            headers={k.lower(): v for k, v in response.headers.items()},
        )


class CannedFetcher:
    """Test double: URL to Response, with the calls recorded."""

    def __init__(self, responses: dict[str, Response | bytes]) -> None:
        self.responses = responses
        self.calls: list[tuple[str, bytes | None]] = []

    def get(self, url: str, *, data: bytes | None = None) -> Response:
        self.calls.append((url, data))
        canned = self.responses.get(url)
        if canned is None:
            return Response(url=url, status=404, body=b"", headers={})
        if isinstance(canned, bytes):
            return Response(url=url, status=200, body=canned, headers={})
        return canned
