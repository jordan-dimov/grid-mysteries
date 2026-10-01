"""022's discovery and shape rules over Modo Energy's public pages: pure
functions of bytes, no network."""

from grid_mysteries.sources import modo

ROBOTS = """User-agent: *
Allow: /
Disallow: /api/
Disallow: /account   # members
User-agent: other-bot
Disallow: /research/
Sitemap: https://modoenergy.com/sitemap.xml
sitemap: https://modoenergy.com/sitemap-2.xml
Sitemap: https://modoenergy.com/sitemap.xml
"""

INDEX = b"""<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap><loc>https://modoenergy.com/sitemap-research.xml</loc><lastmod>2026-09-30</lastmod></sitemap>
  <sitemap><loc>https://modoenergy.com/sitemap-pages.xml</loc></sitemap>
</sitemapindex>"""

URLSET = b"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://modoenergy.com/research/gb-bess-revenue-forecast-2030</loc><lastmod>2025-02-01T10:00:00+00:00</lastmod></url>
  <url><loc>https://modoenergy.com/research/gb-bess-index-september-2026</loc><lastmod>2026-10-01</lastmod></url>
  <url><loc>https://modoenergy.com/research/how-to-value-a-battery</loc></url>
  <url><loc>https://modoenergy.com/static/forecast-chart.png</loc></url>
  <url><loc>https://modoenergy.com/research/gb-bess-revenue-forecast-2030</loc></url>
</urlset>"""

PAGE = """<html><head>
<title>GB BESS revenue forecast: &pound;60k/MW/year by 2030 | Modo Energy</title>
<meta property="og:title" content="GB BESS revenue forecast to 2030" />
<meta property="article:published_time" content="2025-02-01T09:30:00.000Z" />
<script type="application/ld+json">{"@type":"Article",
"datePublished":"2025-02-01T09:30:00Z","dateModified":"2025-02-03"}</script>
<style>.x{color:red}</style>
<script>window.analytics = "£999/MW/year should not be read";</script>
</head><body>
<time datetime="2025-02-01">1 February 2025</time>
<p>Two-hour systems earned &pound;61,500/MW/year in 2024. We forecast
&pound;60k/MW/yr for 2025 and &pound;70 - 80k per MW per year across the full forecast horizon.</p>
<p>Subscribe to read the 4-hour view.</p>
<script id="__NEXT_DATA__" type="application/json">
{"props":{"text":"1h systems: \\u00a355k/MW/year in 2026."}}</script>
<a href="/research/annual-results-2025">Annual Results 2025</a>
<a href="https://x.invalid/interim">Interim <b>Results</b></a>
<a href="/news/other">Other news</a>
</body></html>""".encode()


def test_a1_every_sitemap_line_of_robots_once_in_order() -> None:
    assert modo.sitemaps_in_robots(ROBOTS) == [
        "https://modoenergy.com/sitemap.xml",
        "https://modoenergy.com/sitemap-2.xml",
    ]
    assert modo.sitemaps_in_robots("User-agent: *\n") == []


def test_sitemap_index_and_urlset_parse_with_lastmod_as_printed() -> None:
    index = modo.parse_sitemap(INDEX)
    assert index.kind == "index"
    assert index.entries[0].loc == "https://modoenergy.com/sitemap-research.xml"
    assert index.entries[0].lastmod == "2026-09-30"
    assert index.entries[1].lastmod is None
    urlset = modo.parse_sitemap(URLSET)
    assert urlset.kind == "urlset"
    assert urlset.entries[0].lastmod == "2025-02-01T10:00:00+00:00"
    assert modo.parse_sitemap(b"<other/>").kind == "unknown"


def test_a2_selection_records_a_reason_for_every_url_and_drops_duplicates() -> None:
    selected = modo.select(modo.parse_sitemap(URLSET).entries)
    reasons = {s.loc.rsplit("/", 1)[-1]: s.reason for s in selected}
    assert reasons == {
        "gb-bess-revenue-forecast-2030": "token:forecast",
        "gb-bess-index-september-2026": "token:index",
        "how-to-value-a-battery": "not selected: no token",
        "forecast-chart.png": "not selected: asset",
    }
    assert [s.selected for s in selected] == [True, True, False, False]
    assert len(selected) == 4  # the duplicate loc is listed once


def test_page_filename_is_stable_and_readable() -> None:
    assert (
        modo.page_filename("https://modoenergy.com/research/gb-bess-index?x=1")
        == "research__gb-bess-index.html"
    )
    assert modo.page_filename("https://modoenergy.com/") == "root.html"


def test_visible_text_keeps_json_payloads_and_drops_other_scripts() -> None:
    text = modo.visible_text(PAGE.decode())
    assert "£61,500/MW/year" in text
    assert "£55k/MW/year" in text  # the \\u00a3 inside __NEXT_DATA__
    assert "£999/MW/year" not in text  # a plain script is not page text
    assert "color:red" not in text


def test_figure_strings_are_kept_as_printed_with_shape_and_sentence() -> None:
    text = modo.visible_text(PAGE.decode())
    figures = modo.figure_strings(text)
    printed = [f.as_printed for f in figures]
    assert printed == [
        "£60k/MW/year",
        "£61,500/MW/year",
        "£60k/MW/yr",
        "£70 - 80k per MW per year",
        "£55k/MW/year",
    ]
    assert [f.shape for f in figures] == [
        "£9k/mw/year",
        "£9/mw/year",
        "£9k/mw/yr",
        "£9 - 9k per mw per year",
        "£9k/mw/year",
    ]
    assert figures[1].sentence.startswith("Two-hour systems earned")
    assert figures[1].sentence.endswith("in 2024.")


def test_page_report_tallies_vocabularies_and_dates_and_computes_no_value() -> None:
    report = modo.page_report(
        url="https://modoenergy.com/research/x", path="p", sha256="0" * 64, data=PAGE
    )
    assert report.title == "GB BESS revenue forecast to 2030"
    assert report.dates["meta:article:published_time"] == ["2025-02-01T09:30:00.000Z"]
    assert report.dates["json:datePublished"] == ["2025-02-01T09:30:00Z"]
    assert report.dates["json:dateModified"] == ["2025-02-03"]
    assert report.dates["time:datetime"] == ["2025-02-01"]
    assert report.duration == {"1h": 1, "two-hour": 1, "4-hour": 1}
    assert report.basis["forecast"] == 3
    assert report.horizon == {"full forecast horizon": 1, "annual": 1}
    assert report.paywall == {"subscribe": 1}
    assert report.years == {"2024": 1, "2025": 5, "2026": 1, "2030": 1}
    assert report.figure_shapes["£9k/mw/year"] == 2
    assert report.flags == ["under 500 characters of text"]
    assert all(isinstance(f.as_printed, str) for f in report.figures)


def test_page_report_flags_a_page_with_no_date_and_no_figure() -> None:
    report = modo.page_report(
        url="u", path="p", sha256="0" * 64, data=b"<html><body>hello</body></html>"
    )
    assert "no date declared" in report.flags
    assert "no figure-looking string" in report.flags


def test_a5_links_match_on_visible_text_and_resolve_against_the_base() -> None:
    found = modo.links(PAGE.decode(), "https://www.investegate.co.uk/company/GRID", r"results")
    assert found == [
        ("https://www.investegate.co.uk/research/annual-results-2025", "Annual Results 2025"),
        ("https://x.invalid/interim", "Interim Results"),
    ]


def test_a6_disallowed_paths_of_robots_are_honoured_for_the_wildcard_agent() -> None:
    prefixes = modo.disallowed_prefixes(ROBOTS)
    assert prefixes == ["/api/", "/account"]
    assert modo.is_disallowed("https://modoenergy.com/api/v1/x", prefixes)
    assert modo.is_disallowed("https://modoenergy.com/account/login", prefixes)
    assert not modo.is_disallowed("https://modoenergy.com/research/forecast", prefixes)
    assert modo.disallowed_prefixes("User-agent: *\nDisallow:\n") == []


def test_s2_each_figure_string_carries_the_tokens_of_its_own_sentence() -> None:
    text = modo.visible_text(PAGE.decode())
    figures = modo.figure_strings(text)
    earned = figures[1]
    assert earned.as_printed == "£61,500/MW/year"
    assert earned.duration == {"two-hour": 1}
    assert earned.years == {"2024": 1}
    assert earned.basis == {}
    forecast = figures[2]
    assert forecast.as_printed == "£60k/MW/yr"
    assert forecast.basis == {"forecast": 2}
    assert forecast.horizon == {"full forecast horizon": 1}
    assert forecast.years == {"2025": 1}
