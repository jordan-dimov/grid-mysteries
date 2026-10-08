"""The engines' trust file is exactly the two committed TSA roots, in the
order the authorities are asked, and the witnesses the engines ask are the
same two as every freeze and the research record."""

from grid_mysteries import record
from grid_mysteries.capture.timestamp import TSAS
from grid_mysteries.corpus import REPO_ROOT

TSA_DIR = REPO_ROOT / "trust" / "tsa"


def test_roots_file_is_the_two_roots_concatenated() -> None:
    freetsa = (TSA_DIR / "freetsa-cacert.pem").read_bytes()
    digicert = (TSA_DIR / "digicert-trusted-root-g4.pem").read_bytes()
    assert record.TSA_ROOTS == TSA_DIR / "roots.pem"
    assert record.TSA_ROOTS.read_bytes() == freetsa + digicert
    assert record.TSA_ROOTS.read_text().count("BEGIN CERTIFICATE") == 2


def test_engines_ask_both_authorities_in_the_freeze_order() -> None:
    assert record.WITNESSES == (
        "rfc3161:https://freetsa.org/tsr",
        "rfc3161:http://timestamp.digicert.com",
    )
    assert [w.removeprefix("rfc3161:") for w in record.WITNESSES] == [url for _, url in TSAS]
