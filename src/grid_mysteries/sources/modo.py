"""Modo Energy's public pages, as discovered from the site's own sitemap and
read only for their shape: pins, dates, spellings and the strings that
look like a pound-per-megawatt figure, each kept as printed.

Nothing here turns a string into a number. The schema pass of 022 lists
every figure-looking string with the sentence around it so that a reading
rule can be declared against the spellings actually in use; the declared
reader lives in ``grid_mysteries.investigations.forecast_record`` and is
written after that report exists. Discovery (A1 to A3 of 022's
``ACQUISITION.md``) is a pure function of the sitemap bytes, so the list of
pages pinned is auditable from the pinned sitemaps alone.
"""

import html as html_module
import re
import xml.etree.ElementTree as ET
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal
from urllib.parse import urljoin, urlsplit

from grid_mysteries.models import SourceArtifact
from grid_mysteries.sources.http import fetch_artifact

SOURCE = "modo-energy"
SITE = "https://modoenergy.com"
ROBOTS_URL = f"{SITE}/robots.txt"
#: Used only when robots.txt names no sitemap (A1).
FALLBACK_SITEMAP_URL = f"{SITE}/sitemap.xml"

#: A2: a sitemap URL is selected when its path, lower-cased, contains one of
#: these; the first token in this order is the recorded reason. Chosen for
#: inclusiveness: pinning a public page that turns out irrelevant costs
#: nothing, while a page missed is a false negative the record cannot see.
SELECTION_TOKENS: tuple[str, ...] = ("forecast", "revenue", "index", "benchmark", "outlook")
#: Asset extensions never selected (images and fonts are not pages).
ASSET_SUFFIXES: tuple[str, ...] = (
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".svg",
    ".webp",
    ".ico",
    ".woff",
    ".woff2",
    ".css",
    ".js",
)

#: The figure-looking string: a pound amount, an optional k/m multiplier,
#: an optional range, then "per MW", "per kW", "per MWh" or "per kWh" in
#: slash or word form (the energy units first, so that "£99/MWh" is never
#: cut to "£99/MW"), and an optional "per year", "per month" or "per hour"
#: in any spelling. Matched case-insensitively on the page's text; the
#: match is kept as printed and never parsed to a value.
FIGURE_PATTERN = re.compile(
    r"£\s?\d[\d,]*(?:\.\d+)?\s?(?:k|m|bn)?"
    r"(?:\s?(?:-|–|—|to)\s?£?\s?\d[\d,]*(?:\.\d+)?\s?(?:k|m|bn)?)?"
    r"\s?(?:/|per)\s?(?:MWh|kWh|MW|kW)"
    r"(?:\s?(?:/|per)\s?(?:year|yr|y\b|annum|a\b|month|mo\b|hour|hr|h\b))?",
    re.IGNORECASE,
)

#: Vocabularies tallied per page (S3). Counts of words, not readings.
DURATION_TOKENS: tuple[str, ...] = (
    "1-hour",
    "one-hour",
    "1h",
    "1hr",
    "2-hour",
    "two-hour",
    "2h",
    "2hr",
    "4-hour",
    "four-hour",
    "4h",
    "4hr",
    "8-hour",
    "eight-hour",
    "8h",
    "8hr",
)
BASIS_TOKENS: tuple[str, ...] = (
    "forecast",
    "forecasts",
    "forecasting",
    "projection",
    "outlook",
    "index",
    "realised",
    "realized",
    "actual",
    "outturn",
    "potential",
    "benchmark",
    "leaderboard",
    "fleet",
    "average",
    "typical",
)
HORIZON_TOKENS: tuple[str, ...] = (
    "full forecast horizon",
    "decade",
    "long-term",
    "long term",
    "annual",
    "monthly",
)
PAYWALL_TOKENS: tuple[str, ...] = (
    "subscribe",
    "subscriber",
    "subscribers",
    "log in",
    "login",
    "sign in",
    "paywall",
    "premium",
    "members only",
    "unlock",
    "free trial",
    "request a demo",
)
YEAR_PATTERN = re.compile(r"\b(20[2-5]\d)\b")
PUBLISHED_META = re.compile(
    r"<meta\s+[^>]*?(?:property|name)=[\"'](article:published_time|article:modified_time|"
    r"datePublished|dateModified|date|pubdate|publish_date|og:updated_time)[\"'][^>]*?"
    r"content=[\"']([^\"']+)[\"']",
    re.IGNORECASE,
)
JSONLD_DATE = re.compile(r"\"(datePublished|dateModified|dateCreated)\"\s*:\s*\"([^\"]+)\"")
TIME_TAG = re.compile(r"<time\b[^>]*\bdatetime=[\"']([^\"']+)[\"']", re.IGNORECASE)
TITLE_TAG = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
OG_TITLE = re.compile(
    r"<meta\s+[^>]*?property=[\"']og:title[\"'][^>]*?content=[\"']([^\"']+)[\"']", re.IGNORECASE
)
ANCHOR = re.compile(
    r"<a\b[^>]*?href=[\"']([^\"'#]+)[\"'][^>]*>(.*?)</a>", re.IGNORECASE | re.DOTALL
)
SCRIPT_OR_STYLE = re.compile(r"<(script|style)\b([^>]*)>(.*?)</\1>", re.IGNORECASE | re.DOTALL)
BLOCK_END = re.compile(
    r"</(?:p|div|h[1-6]|li|ul|ol|title|script|time|td|th|tr|table|section|article|header|"
    r"footer|blockquote|figcaption)\s*>|<br\s*/?>|<hr\s*/?>",
    re.IGNORECASE,
)
TAG = re.compile(r"<[^>]+>")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\n")


def fetch_pinned(*, url: str, destination: Path, dataset: str) -> SourceArtifact:
    return fetch_artifact(url=url, destination=destination, source=SOURCE, dataset=dataset)


# ------------------------------------------------------------ discovery


def sitemaps_in_robots(text: str) -> list[str]:
    """A1: every ``Sitemap:`` line of robots.txt, in order, duplicates dropped."""
    out: list[str] = []
    for line in text.splitlines():
        key, _, value = line.partition(":")
        if key.strip().lower() == "sitemap" and value.strip() and value.strip() not in out:
            out.append(value.strip())
    return out


def disallowed_prefixes(text: str) -> list[str]:
    """A6: the ``Disallow:`` paths of every ``User-agent: *`` group of
    robots.txt; a selected URL under one of them is listed, never fetched."""
    out: list[str] = []
    applies = False
    for line in text.splitlines():
        key, _, value = line.partition(":")
        key, value = key.strip().lower(), value.split("#")[0].strip()
        if key == "user-agent":
            applies = value == "*"
        elif key == "disallow" and applies and value and value not in out:
            out.append(value)
    return out


def is_disallowed(url: str, prefixes: list[str]) -> bool:
    path = urlsplit(url).path or "/"
    return any(path.startswith(p.rstrip("*")) for p in prefixes)


@dataclass(frozen=True, slots=True)
class SitemapEntry:
    loc: str
    lastmod: str | None


@dataclass(frozen=True, slots=True)
class SitemapParse:
    kind: Literal["index", "urlset", "unknown"]
    entries: tuple[SitemapEntry, ...]


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def parse_sitemap(data: bytes) -> SitemapParse:
    """A sitemap index (its child sitemaps) or a urlset (its pages), with
    each entry's ``lastmod`` as printed; namespace-agnostic."""
    root = ET.fromstring(data)
    kind = _local(root.tag)
    if kind not in ("sitemapindex", "urlset"):
        return SitemapParse("unknown", ())
    entries = []
    for child in root:
        loc = lastmod = None
        for leaf in child:
            if _local(leaf.tag) == "loc":
                loc = (leaf.text or "").strip()
            elif _local(leaf.tag) == "lastmod":
                lastmod = (leaf.text or "").strip() or None
        if loc:
            entries.append(SitemapEntry(loc, lastmod))
    return SitemapParse("index" if kind == "sitemapindex" else "urlset", tuple(entries))


@dataclass(frozen=True, slots=True)
class Selection:
    loc: str
    lastmod: str | None
    selected: bool
    reason: str


def select(
    entries: list[SitemapEntry] | tuple[SitemapEntry, ...],
    tokens: tuple[str, ...] = SELECTION_TOKENS,
) -> list[Selection]:
    """A2: every sitemap URL with its selection and the reason, so what was
    not pinned is as visible as what was."""
    out: list[Selection] = []
    seen: set[str] = set()
    for entry in entries:
        if entry.loc in seen:
            continue
        seen.add(entry.loc)
        path = urlsplit(entry.loc).path.lower()
        if path.endswith(ASSET_SUFFIXES):
            out.append(Selection(entry.loc, entry.lastmod, False, "not selected: asset"))
            continue
        token = next((t for t in tokens if t in path), None)
        if token is None:
            out.append(Selection(entry.loc, entry.lastmod, False, "not selected: no token"))
        else:
            out.append(Selection(entry.loc, entry.lastmod, True, f"token:{token}"))
    return out


def page_filename(url: str) -> str:
    """A stable, readable file name for a pinned page: the URL path's
    segments joined by ``__``, non-path characters replaced; ``.html``."""
    path = urlsplit(url).path.strip("/") or "root"
    safe = re.sub(r"[^A-Za-z0-9._-]+", "-", path.replace("/", "__"))
    return safe[:180] + ".html"


# -------------------------------------------------------------- the shape


def visible_text(html: str) -> str:
    """The page as text: tags stripped, entities unescaped, whitespace
    collapsed, the end of a block element kept as a line break so that a
    sentence never runs across two blocks. Scripts and styles are dropped except JSON payloads
    (``application/json``, ``application/ld+json``), whose strings carry a
    client-rendered page's content and are kept as text."""

    def keep_json(match: re.Match[str]) -> str:
        attrs = match.group(2).lower()
        if match.group(1).lower() == "script" and "application/" in attrs and "json" in attrs:
            return " " + match.group(3) + " "
        return " "

    text = SCRIPT_OR_STYLE.sub(keep_json, html)
    text = BLOCK_END.sub("\x00", text)  # a block boundary, kept through the collapse
    text = TAG.sub(" ", text)
    text = html_module.unescape(text)
    text = text.replace("\\u00a3", "£").replace("\\n", " ")
    text = " ".join(text.split())  # source newlines are whitespace, not boundaries
    return re.sub(r"\s*(?:\x00\s*)+", "\n", text).strip()


def title_of(html: str) -> str | None:
    og = OG_TITLE.search(html)
    if og:
        return html_module.unescape(og.group(1)).strip()
    t = TITLE_TAG.search(html)
    return " ".join(html_module.unescape(t.group(1)).split()) if t else None


RNS_HEADER_RE = re.compile(
    r"RNS Number\s*:[^\n]*\n(?:[^\n]*\n){0,3}?\s*(\d{1,2}\s+[A-Z][a-z]+\s+20\d\d)\b"
)


def rns_header_date(text: str) -> str | None:
    """S1: the date an RNS announcement page prints in its header, the
    first `D Month YYYY` line within three lines after `RNS Number :`, as
    printed."""
    m = RNS_HEADER_RE.search(text)
    return m.group(1) if m else None


def pdf_info_dates(data: bytes) -> dict[str, list[str]]:
    """S1: a PDF's CreationDate and ModDate as `pdfinfo` prints them."""
    import shutil
    import subprocess

    if not shutil.which("pdfinfo"):
        return {}
    done = subprocess.run(["pdfinfo", "-"], input=data, capture_output=True, check=False)
    out: dict[str, list[str]] = {}
    for line in done.stdout.decode("utf-8", errors="replace").splitlines():
        key, _, value = line.partition(":")
        if key.strip() in ("CreationDate", "ModDate") and value.strip():
            out[f"pdf:{key.strip()}"] = [value.strip()]
    return out


def date_strings(html: str) -> dict[str, list[str]]:
    """Every date-like declaration the page makes about itself, by where
    it was found, as printed. Which one is the publication date is a
    reading rule, declared later."""
    out: dict[str, list[str]] = {}
    for name, value in PUBLISHED_META.findall(html):
        out.setdefault(f"meta:{name.lower()}", []).append(value)
    for name, value in JSONLD_DATE.findall(html):
        out.setdefault(f"json:{name}", []).append(value)
    for value in TIME_TAG.findall(html):
        out.setdefault("time:datetime", []).append(value)
    return {k: list(dict.fromkeys(v)) for k, v in out.items()}


@dataclass(frozen=True, slots=True)
class FigureString:
    """One figure-looking string as printed, with the sentence it sits in
    and the vocabulary that sentence uses: what the sentence says about
    duration, basis, horizon and years, counted, not read."""

    as_printed: str
    shape: str
    offset: int
    sentence: str
    duration: dict[str, int]
    basis: dict[str, int]
    horizon: dict[str, int]
    years: dict[str, int]


def shape_of(figure: str) -> str:
    """The spelling with every digit run replaced by ``9`` and whitespace
    collapsed, so spellings can be tallied across pages."""
    return " ".join(re.sub(r"\d[\d,]*(?:\.\d+)?", "9", figure).split()).lower()


def sentence_around(text: str, start: int, end: int) -> str:
    bounds = [0] + [m.end() for m in SENTENCE_END.finditer(text)] + [len(text)]
    lo = max(b for b in bounds if b <= start)
    hi = min(b for b in bounds if b >= end)
    return text[lo:hi].strip()


def figure_strings(text: str) -> list[FigureString]:
    out = []
    for m in FIGURE_PATTERN.finditer(text):
        sentence = sentence_around(text, m.start(), m.end())
        out.append(
            FigureString(
                as_printed=m.group(0),
                shape=shape_of(m.group(0)),
                offset=m.start(),
                sentence=sentence,
                duration=tally(sentence, DURATION_TOKENS),
                basis=tally(sentence, BASIS_TOKENS),
                horizon=tally(sentence, HORIZON_TOKENS),
                years=year_tally(sentence),
            )
        )
    return out


def tally(text: str, tokens: tuple[str, ...]) -> dict[str, int]:
    """Occurrences of each token as a whole word (case-insensitive); only
    tokens that occur are listed."""
    lowered = text.lower()
    out = {}
    for token in tokens:
        n = len(re.findall(rf"(?<![a-z0-9]){re.escape(token)}(?![a-z0-9])", lowered))
        if n:
            out[token] = n
    return out


def year_tally(text: str) -> dict[str, int]:
    return dict(sorted(Counter(YEAR_PATTERN.findall(text)).items()))


#: A7(iii) of 022's amendment 1: reading order, not ``-layout``, so a
#: two-column page's sentences stay whole. The report names the mode.
PDF_MODE = "pdftotext reading order (no -layout)"


def pdf_text(data: bytes) -> str:
    """A PDF's text as `pdftotext` prints it in reading order (poppler, on
    PATH), so that an RNS report's figures are scanned as text; empty when
    the tool is absent, and the report says so with a flag."""
    import shutil
    import subprocess

    if not shutil.which("pdftotext"):
        return ""
    done = subprocess.run(["pdftotext", "-", "-"], input=data, capture_output=True, check=False)
    return done.stdout.decode("utf-8", errors="replace")


@dataclass(slots=True)
class PageReport:
    url: str
    path: str
    sha256: str
    bytes: int
    format: str
    title: str | None
    dates: dict[str, list[str]]
    text_chars: int
    figures: list[FigureString]
    figure_shapes: dict[str, int]
    duration: dict[str, int]
    basis: dict[str, int]
    horizon: dict[str, int]
    paywall: dict[str, int]
    years: dict[str, int]
    flags: list[str] = field(default_factory=list)


def page_report(*, url: str, path: str, sha256: str, data: bytes) -> PageReport:
    """S1 to S4 for one pinned page. Computes no figure: every number
    stays the string it was printed as."""
    is_pdf = data.startswith(b"%PDF")
    if is_pdf:
        html = ""
        text = " ".join(pdf_text(data).split())
        dates = pdf_info_dates(data)
    else:
        html = data.decode("utf-8", errors="replace")
        text = visible_text(html)
        dates = date_strings(html)
        header = rns_header_date(text)
        if header:
            dates["text:rns-header"] = [header]
    figures = figure_strings(text)
    report = PageReport(
        url=url,
        path=path,
        sha256=sha256,
        bytes=len(data),
        format=f"pdf ({PDF_MODE})" if is_pdf else "html",
        title=title_of(html) if html else None,
        dates=dates,
        text_chars=len(text),
        figures=figures,
        figure_shapes=dict(Counter(f.shape for f in figures).most_common()),
        duration=tally(text, DURATION_TOKENS),
        basis=tally(text, BASIS_TOKENS),
        horizon=tally(text, HORIZON_TOKENS),
        paywall=tally(text, PAYWALL_TOKENS),
        years=year_tally(text),
    )
    if is_pdf and not text:
        report.flags.append("pdf with no extractable text")
    if not report.dates:
        report.flags.append("no date declared")
    if not figures:
        report.flags.append("no figure-looking string")
    if report.text_chars < 500:
        report.flags.append("under 500 characters of text")
    return report


def links(html: str, base_url: str, text_pattern: str) -> list[tuple[str, str]]:
    """Anchors whose visible text matches ``text_pattern``
    (case-insensitive), as (absolute href, text), in page order, duplicates
    by href dropped. A5's link rule for the RNS listings."""
    pattern = re.compile(text_pattern, re.IGNORECASE)
    out: list[tuple[str, str]] = []
    seen: set[str] = set()
    for href, inner in ANCHOR.findall(html):
        text = " ".join(html_module.unescape(TAG.sub(" ", inner)).split())
        if not pattern.search(text):
            continue
        absolute = urljoin(base_url, html_module.unescape(href.strip()))
        if absolute in seen:
            continue
        seen.add(absolute)
        out.append((absolute, text))
    return out
