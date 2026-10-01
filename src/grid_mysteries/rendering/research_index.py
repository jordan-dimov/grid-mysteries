"""The research index at research.a115.co.uk: one sentence and a link per
standing instrument, in the pages' own format. A pure function of the list
below; the same list always renders the same bytes. No script, no external
asset, no hostname (the page is served wherever the site is)."""

from html import escape
from typing import Final

from grid_mysteries.rendering.connection_slippage import CREDIBILITY, CSS, REPO_URL

TITLE: Final = "Grid Mysteries research"
SUBTITLE: Final = (
    "Standing instruments built from Britain's public electricity data, each under a method "
    "sealed before its first figure"
)
CONTACT_EMAIL: Final = "jdimov@a115.co.uk"
#: (path, name, one plain sentence), in the order the index lists them.
INSTRUMENTS: Final[tuple[tuple[str, str, str], ...]] = (
    (
        "/balancing-bill/",
        "The Balancing Bill",
        "Who got paid to keep Britain's grid balanced, day by day, from the settlement "
        "data the market publishes.",
    ),
    (
        "/connection-slippage/",
        "GB Connection Slippage",
        "How far the contract dates in Britain's grid-connection register have moved, in "
        "megawatt-years, rebuilt from every copy of the register since 2014.",
    ),
    (
        "/overdue-queue/",
        "The queue that is past its own date",
        "The entries in the connection register whose own connection date has passed, "
        "counted on each new copy under a method sealed before the count.",
    ),
    (
        "/slippage-by-technology-and-area/",
        "Where the dates move",
        "The slippage series cut by plant type and by transmission area, with the "
        "margin each identity rule decides shown beside the figure.",
    ),
)
METHOD: Final = (
    "Each page is a pure function of evidence committed to a public repository under a "
    "declaration frozen before any figure was computed and witnessed by OpenTimestamps and "
    "two RFC 3161 authorities. A committed row is never rewritten: a figure that would "
    "change is a new declaration beside the old one. Every page says what it never claims."
)
INDEX_CSS: Final = """\
ul.index{list-style:none;padding:0;margin:1.5rem 0;max-width:44rem}
ul.index li{margin:0 0 1.25rem}
ul.index a{font-weight:600;font-size:1.1rem}
"""


def render_index() -> str:
    items = "\n".join(
        f'<li><a href="{escape(path)}">{escape(name)}</a><br>{escape(sentence)}</li>'
        for path, name, sentence in INSTRUMENTS
    )
    return f"""<!doctype html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(TITLE)}</title>
<meta name="description" content="{escape(SUBTITLE)}">
<style>
{CSS}{INDEX_CSS}</style>
</head>
<body>
<header>
<h1>{escape(TITLE)}</h1>
<p class="subtitle">{escape(SUBTITLE)}</p>
</header>
<main>
<ul class="index">
{items}
</ul>
<p class="notes">{escape(METHOD)} Declarations, evidence, code and tests:
<a href="{escape(REPO_URL)}">{escape(REPO_URL.removeprefix("https://"))}</a>.</p>
</main>
<footer>
<p>{escape(CREDIBILITY)}</p>
<p>Questions or challenges: <a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
</footer>
</body>
</html>
"""
