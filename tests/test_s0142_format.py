import pytest

from grid_mysteries.sources import s0142_format as sf

FILE = [
    b"AAA|S0142013|D|20260922223519|SA|UKDC|PB|PORTAL|41694|OPER|\r\n",
    b"SRH|20260828|SF|2|2|20260828|2|166710|NGC|\r\n",
    b"SPI|1|" + b"|".join([b"0"] * 52) + b"|\r\n",
    b"BPH|20260828|SF|2|2|20260828|2|166710|A|\r\n",
    b"APC|" + b"|".join([b"0"] * 12) + b"|\r\n",
    b"SP7|1|\r\n",
    b"BP7|2__AAAAA001|" + b"|".join([b"0"] * 24) + b"|\r\n",
    b"ZZZ|1|2|\r\n",
]


def test_the_profile_holds_format_and_no_value():
    p = sf.profile(FILE)
    assert p == {
        "leading_byte_order_mark": False,
        "non_ascii_lines": 0,
        "flow_version": "S0142013",
        "field_counts": {
            "AAA": [10],
            "APC": [13],
            "BP7": [26],
            "BPH": [9],
            "SP7": [2],
            "SPI": [54],
            "SRH": [9],
            "ZZZ": [3],
        },
    }
    assert sf.differences(sf.expected_from([p]), p) == []


def test_each_departure_from_the_schema_pass_is_named():
    """2026-10-03: eight of 144 acquired files began with a byte-order mark,
    found by a crash in compute. Each departure the reader depends on is
    named here, between acquisition and compute, with no value read."""
    expected = sf.expected_from([sf.profile(FILE)])
    marked = [sf.BOM + FILE[0], *FILE[1:]]
    assert sf.differences(expected, sf.profile(marked)) == ["leading byte-order mark"]
    other = [
        FILE[0].replace(b"S0142013", b"S0142014"),
        *FILE[1:6],
        FILE[6].replace(b"0|\r", b"0|0|\r"),
        FILE[7],
    ]
    assert sf.differences(expected, sf.profile(other)) == [
        "flow version S0142014 (expected S0142013)",
        "BP7 with 27 field(s)",
    ]
    nbsp = [*FILE[:5], b"SP7|1\xc2\xa0|\r\n", *FILE[6:]]
    assert sf.differences(expected, sf.profile(nbsp)) == [
        "1 line(s) with a non-ASCII byte",
        "no SP7 record",
    ]
    with pytest.raises(ValueError):
        sf.expected_from([sf.profile(FILE), sf.profile(other)])
