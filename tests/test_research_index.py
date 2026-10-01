"""The research index: a pure function of the instrument list, self-contained."""

from html import escape

from grid_mysteries.rendering import research_index as ri


def test_the_index_is_deterministic_self_contained_and_lists_every_instrument():
    html = ri.render_index()
    assert html == ri.render_index()
    assert "<script" not in html
    head = html.split("<main>")[0]
    assert "http" not in head.split("<style>")[1]  # no external asset
    for path, name, sentence in ri.INSTRUMENTS:
        assert f'href="{path}"' in html and escape(name) in html and escape(sentence) in html
    assert "/balancing-bill/" in html and "a115.co.uk" not in head  # no hostname printed
    assert "jdimov@a115.co.uk" in html


def test_every_instrument_path_is_a_directory_the_site_holds():
    from pathlib import Path

    site = Path(__file__).parents[1] / "site"
    for path, _name, _sentence in ri.INSTRUMENTS:
        assert (site / path.strip("/") / "index.html").exists(), path
