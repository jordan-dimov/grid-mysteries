from grid_mysteries.rendering import compensation_pot as page


def results(h3="holds", c4_passes=True):
    run = [{"run": "SF", "value": "100", "movement": "0.08"}, {"run": "R3", "value": "108.70"}]
    return {
        "declaration_sha256": "3ebd9015" + "0" * 56,
        "amendment_1_sha256": "d308b8c1" + "0" * 56,
        "computed_at": "2026-10-03T13:07:12+00:00",
        "leading_byte_order_mark": ["S0142_20260901_SF_20260924075713.gz"],
        "runs_read": {"FEB": ["R3"], "POST": ["SF"]},
        "missing_or_excluded": {
            "missing": {"FEB": [], "POST": []},
            "excluded": {"SERIES": ["S0142_20250924_R3_20260429080153.gz"]},
            "files": {
                "S0142_20250924_R3_20260429080153.gz": {
                    "failed": ["C2 no off-prefix or orphan P415 cell"],
                    "off_prefix": {"22:C__": 11},
                    "orphan_bp7": 0,
                }
            },
        },
        "C4": {
            "days": 28,
            "runs": ["SF"],
            "paid": "5717880.61",
            "vtp_volume": "65020.272",
            "paid_vs_elexon": "0.0254",
            "vtp_vs_elexon": "0.0187",
            "passes": c4_passes,
            "latest_run_beside": {
                "days": 28,
                "runs": ["R3"],
                "paid": "5739130.80",
                "vtp_volume": "65270.615",
                "paid_vs_elexon": "0.0292",
                "vtp_vs_elexon": "0.0226",
            },
        },
        "hypotheses": {
            "H1-FEB": {
                "ratio": "1.31",
                "post_mean": "3046.6",
                "baseline_mean": "2324.5",
                "verdict": "holds",
                "reported": {"supplier_volume_total": "1.31"},
            },
            "H1-PRE": {
                "ratio": "0.56",
                "post_mean": "300195",
                "baseline_mean": "540187",
                "verdict": "holds",
                "reported": {"supplier_cash_total": "0.56"},
            },
            "H2-VTP": {
                "party": "ALMAPERJ",
                "baseline_share": "0.79",
                "post_share": "-0.0000017",
                "verdict": "holds",
            },
            "H2-SUP": {
                "party": "MERCURY",
                "baseline_share": "0.6",
                "post_share": "0.2",
                "verdict": "fails",
            },
            "H3": {"verdict": h3, "days": {"2025-11-05": {"paid": run, "sf_to_latest": "0.08"}}},
        },
        "falsifiers": {"F1 H1-FEB killed": False, "F4 H2-SUP fails": True, "F5 C4 fails": False},
        "context": {
            "window_totals": {
                "POST": {
                    "days": 13,
                    "supplier_cash": "100",
                    "charged": "110",
                    "vtp_volume": "1",
                    "supplier_volume": "1",
                }
            },
            "h2_against_pre": {},
            "pre_almaperj_vtp_volume": {
                "by_day": {"2026-08-10": "1718.98"},
                "share_of_pre": "0.42",
            },
            "largest": {
                "POST": {
                    "vtp_volume": [["AXLEENER", "1", "0.5"]],
                    "paid": [["MERCURY", "1", "0.5"]],
                    "charged": [],
                }
            },
            "series": [
                {
                    "settlement_date": "2025-09-03",
                    "paid": "1",
                    "charged": "1",
                    "vtp_volume": "1",
                    "supplier_volume": "1",
                }
            ],
        },
    }


NAMES = {"MERCURY": "Octopus Energy Limited", "AXLEENER": "Axle Energy Limited"}


def test_c4_leads_both_h1_baselines_share_a_sentence_and_h3_marks_every_verdict():
    text = page.render_results(results(), NAMES, {"register": "r"})
    verdicts = text.split("## The verdicts")[1].split("## Checks")[0]
    assert verdicts.lstrip().startswith("**C4 passes.**")
    (h1,) = [line for line in verdicts.splitlines() if line.startswith("**H1")]
    assert "1.31 times FEB" in h1 and "0.56 times PRE" in h1 and "H1-FEB holds" in h1
    for line in verdicts.splitlines():
        if line.startswith(("**H1", "**H2")):
            assert "provisional until POST reaches R1" in line
    assert "provisional" not in page.render_results(results(h3="fails"), NAMES, {"register": "r"})


def test_names_come_only_from_the_register_and_a_tiny_share_keeps_its_sign():
    text = page.render_results(results(), NAMES, {"register": "r"})
    assert "`MERCURY` (Octopus Energy Limited)" in text
    assert "`ALMAPERJ` (" not in text  # not in the register: the id stands alone
    assert "-0.0002 % of POST's" in text
    assert "| `S0142_20250924_R3_20260429080153.gz` | SERIES | C2 | `22:C__` 11 |" in text
    assert "| F4 H2-SUP fails | **yes** |" in text
    assert page.pounds("-52786.4") == "−£52,786"
    assert (
        "carries `MERCURY` (Octopus Energy Limited). The register does not carry `ALMAPERJ`" in text
    )


def test_a_failed_c4_is_said_first_and_withholds_the_verdicts():
    text = page.render_results(results(c4_passes=False), NAMES, {"register": "r"})
    verdicts = text.split("## The verdicts")[1]
    assert verdicts.lstrip().startswith("**C4 FAILS (F5).**")
    assert "No H verdict is published" in verdicts.split("\n\n")[1]
