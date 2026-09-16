from datetime import date

from grid_mysteries.investigations import connection_record as cr


def row(
    name="Clash Gour",
    customer="EDF",
    site="Clash Gour 132kV",
    stage="",
    eff="2025-10-30",
    mw="210",
    status="Awaiting Consents",
    agreement="Directly Connected",
    plant="Wind Onshore",
):
    return {
        "Project Name": name,
        "Customer Name": customer,
        "Connection Site": site,
        "Stage": stage,
        "MW Connected": "0",
        "MW Increase / Decrease": mw,
        "Cumulative Total Capacity (MW)": mw,
        "MW Effective From": eff,
        "Project Status": status,
        "Agreement Type": agreement,
        "HOST TO": "SHET",
        "Plant Type": plant,
    }


def vintages(*items):
    return [(t, rows, f"sha-{t}", f"v/{t}") for t, rows in items]


def test_tracking_is_by_project_name_and_stage_not_customer_or_site():
    v = vintages(
        (date(2021, 1, 5), [row(customer="EDF A"), row(name="Other")]),
        (date(2021, 2, 5), [row(customer="EDF B", site="Clash Gour 132kV Substation")]),
    )
    obs = cr.track(v, "clash gour", None)
    assert [o.count for o in obs] == [1, 1]
    assert cr.track(v, "Clash Gour", "2")[0].count == 0


def test_as_of_is_the_latest_vintage_on_or_before_the_date():
    obs = cr.track(
        vintages((date(2021, 1, 5), [row()]), (date(2021, 1, 9), [row()])), "Clash Gour", None
    )
    on_ninth, on_eighth = cr.as_of(obs, date(2021, 1, 9)), cr.as_of(obs, date(2021, 1, 8))
    assert on_ninth is not None and on_ninth.t_public == date(2021, 1, 9)
    assert on_eighth is not None and on_eighth.t_public == date(2021, 1, 5)
    assert cr.as_of(obs, date(2021, 1, 4)) is None


def test_changes_record_each_field_with_the_first_vintage_that_showed_it():
    v = vintages(
        (date(2021, 1, 5), [row(eff="2025-10-30")]),
        (date(2021, 1, 9), [row(eff="30/10/2025")]),  # respelled, not a change
        (date(2021, 1, 12), [row(eff="2027-10-30", plant="Energy Storage System;Wind Onshore")]),
        (
            date(2021, 1, 15),
            [row(eff="2027-10-30", plant="Energy Storage System; Wind Onshore")],
        ),  # whitespace only
        (
            date(2021, 1, 19),
            [
                row(
                    eff="2029/10/30",
                    plant="Energy Storage System; Wind Onshore",
                    agreement="Direct Connection",
                )
            ],
        ),
    )
    obs = cr.track(v, "Clash Gour", None)
    out = cr.changes(obs, date(2021, 1, 5), date(2021, 1, 19))
    assert [(c.field, c.previous, c.current, c.first_shown, c.last_previous) for c in out] == [
        (
            "MW effective from (target date)",
            "30/10/2025",
            "2027-10-30",
            date(2021, 1, 12),
            date(2021, 1, 9),
        ),
        (
            "Plant type",
            "Wind Onshore",
            "Energy Storage System;Wind Onshore",
            date(2021, 1, 12),
            date(2021, 1, 9),
        ),
        (
            "MW effective from (target date)",
            "2027-10-30",
            "2029/10/30",
            date(2021, 1, 19),
            date(2021, 1, 15),
        ),
    ]  # the agreement-type respelling on 2021-01-19 is a declared label variant, not a change
    assert out[0].first_shown_sha256 == "sha-2021-01-12"


def test_declared_label_variants_and_salesforce_id_forms_are_not_changes():
    v = vintages(
        (date(2024, 5, 21), [dict(row(), **{"Project ID": "a0l4L0000005iaa"})]),
        (
            date(2024, 5, 24),
            [dict(row(agreement="Direct Connection"), **{"Project ID": "a0l4L0000005iaaQAA"})],
        ),
        (
            date(2024, 5, 28),
            [dict(row(agreement="Directly Connected"), **{"Project ID": "a0l4L0000005iab"})],
        ),
    )
    obs = cr.track(v, "Clash Gour", None)
    out = cr.changes(obs, date(2024, 5, 21), date(2024, 5, 28))
    assert [(c.field, c.previous, c.current) for c in out] == [
        ("Project ID", "a0l4L0000005iaaQAA", "a0l4L0000005iab"),
    ]
    assert cr.comparable("Direct Connection", "label") == cr.comparable(
        "Directly Connected", "label"
    )
    assert cr.comparable("Bilateral", "label") == "bilateral"


def test_absence_and_ambiguity_are_recorded_as_changes_of_presence():
    v = vintages(
        (date(2021, 1, 5), [row()]),
        (date(2021, 1, 9), []),
        (date(2021, 1, 12), [row(), row(stage="2")]),
        (date(2021, 1, 15), [row()]),
    )
    obs = cr.track(v, "Clash Gour", None)
    out = cr.changes(obs, date(2021, 1, 5), date(2021, 1, 15))
    assert [(c.field, c.previous, c.current, c.first_shown) for c in out] == [
        ("Presence", "present (one row)", "absent", date(2021, 1, 9)),
        ("Presence", "absent", "ambiguous (2 rows)", date(2021, 1, 12)),
        ("Presence", "ambiguous (2 rows)", "present (one row)", date(2021, 1, 15)),
    ]
    rec = cr.record(obs, "Clash Gour", None, (date(2021, 1, 5), date(2021, 1, 15)))
    assert (rec["vintages_consulted"], rec["vintages_absent"], rec["vintages_ambiguous"]) == (
        4,
        1,
        1,
    )


def test_record_states_what_was_published_on_each_date_and_nothing_more():
    v = vintages(
        (date(2021, 1, 5), [row(eff="2025-10-30")]), (date(2021, 6, 5), [row(eff="2027-10-30")])
    )
    obs = cr.track(v, "Clash Gour", None)
    rec = cr.record(obs, "Clash Gour", None, (date(2021, 3, 31), date(2021, 7, 1)))
    assert rec["as_of"][0]["vintage"] == date(2021, 1, 5)
    assert rec["as_of"][0]["state"]["MW effective from (target date)"] == "2025-10-30"
    assert rec["as_of"][1]["vintage"] == date(2021, 6, 5)
    assert rec["as_of"][1]["state"]["Customer name"] == "EDF"
    assert len(rec["changes"]) == 1
    assert set(rec) == {
        "project",
        "stage",
        "dates",
        "as_of",
        "changes",
        "vintages_consulted",
        "vintages_absent",
        "vintages_ambiguous",
        "first_vintage",
        "last_vintage",
    }
    early = cr.record(obs, "Clash Gour", None, (date(2020, 1, 1), date(2021, 7, 1)))
    assert early["as_of"][0]["vintage"] is None
    assert early["changes"] == []
