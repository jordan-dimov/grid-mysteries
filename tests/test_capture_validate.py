from datetime import date

from grid_mysteries.capture import validate as v


def kind(body: bytes, content_type: str = "", url: str = "https://x/y", strategy: str = "ckan"):
    return v.artefact(body, content_type=content_type, url=url, strategy=strategy).valid


def test_each_kind_of_artefact_is_read_for_what_it_claims_to_be():
    """Kinds as the archive holds them (calibrated on all 10,935 artefacts of
    2026-09-15 to 2026-10-03, none invalid): NESO serves CSV as
    octet-stream or event-stream, Opendatasoft exports are ';'-separated
    behind a byte-order mark, workbooks are zip containers."""
    assert kind(b'{"success": true}', "application/json")
    assert kind(b"a,b\n1,2\n", "application/octet-stream")
    assert kind(b"a,b\n1,2\n", "text/event-stream")
    assert kind(b"\xef\xbb\xbftechnology;status\r\nSolar;x\r\n", "text/csv")
    assert kind(
        b"PK\x03\x04rest", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert kind(b"%PDF-1.7", "application/pdf")
    assert kind(b'{"success": tr', "application/json") is False
    assert kind(b"just words", "text/csv") is False
    assert kind(b"<html>not a workbook</html>", "application/vnd.ms-excel") is False
    assert kind(b"", "text/csv") is False


def test_a_page_is_untested_but_html_from_a_data_endpoint_or_a_challenge_never_passes():
    page = b"<!DOCTYPE html><html><title>Agile</title></html>"
    assert kind(page, "text/html", "https://octopus.energy/smart/agile/", "url") is None
    assert kind(page, "text/html", "https://a/api/explore/x/exports/csv", "url") is False
    assert kind(page, "text/html", "https://a/b/c", "ckan") is False
    challenge = b"<html><title>Just a moment...</title></html>"
    assert kind(challenge, "text/html", "https://octopus.energy/smart/agile/", "url") is False


def test_an_ocds_day_is_whole_only_if_its_pages_chain_to_the_end_inside_the_window():
    day = date(2026, 10, 2)
    one = b'{"releases": [{"date": "2026-10-02T09:00:00Z"}]}'
    more = b'{"releases": [{"date": "2026-10-02T09:00:00Z"}], "links": {"next": "u"}}'
    assert v.ocds_run([("P001", one)], day).valid
    assert v.ocds_run([("P001", more), ("P002", one)], day).valid
    assert v.ocds_run([("P001", more)], day).valid is False  # stopped with a next page
    assert v.ocds_run([("P001", one), ("P002", one)], day).valid is False  # a gap in the chain
    assert v.ocds_run([("P001", one)], date(2026, 10, 1)).valid is False  # another day
    assert v.ocds_run([], day).valid is False
