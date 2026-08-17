from decimal import Decimal

import pytest
from hypothesis import given
from hypothesis import strategies as st

from grid_mysteries.investigations.event_ledger import (
    LedgerEntry,
    ordered,
    parse_ebocf_record,
    period_gaps,
)


def ebocf_row(pairs: dict[str, str | None], total: str) -> dict:
    return {
        "bmUnit": "E_STOR-1",
        "settlementDate": "2026-05-10",
        "settlementPeriod": 21,
        "bidOfferPairCashflows": {
            k: (Decimal(v) if v is not None else None) for k, v in pairs.items()
        },
        "totalCashflow": Decimal(total),
        "createdDateTime": "2026-08-17T09:00:00Z",
    }


def test_ebocf_pairs_reconcile_to_total_or_refuse() -> None:
    good = parse_ebocf_record(
        ebocf_row(
            {"negative1": "-4606.55613", "positive1": "0.0", "negative2": None}, "-4606.55613"
        )
    )
    assert good.reconciled_total() == Decimal("-4606.55613")
    assert good.pair_cashflows == {-1: Decimal("-4606.55613"), 1: Decimal("0.0")}

    # Float-serialisation noise (picopounds, observed in real EBOCF data)
    # reconciles under the declared micro-GBP tolerance...
    noisy = parse_ebocf_record(
        ebocf_row({"positive1": "11474.013765740228045331"}, "11474.013765740226517664")
    )
    assert noisy.reconciled_total() == Decimal("11474.013765740226517664")

    # ...but a real discrepancy refuses.
    bad = parse_ebocf_record(ebocf_row({"negative1": "-100"}, "-99"))
    with pytest.raises(ValueError, match="do not reconcile"):
        bad.reconciled_total()


def test_supported_inference_requires_its_assumption() -> None:
    with pytest.raises(ValueError, match="assumption"):
        LedgerEntry("2026-05-10", 21, "E_STOR-1", "re-traded intraday", "supported_inference")
    entry = LedgerEntry(
        "2026-05-10",
        21,
        "E_STOR-1",
        "energy retained after curtailment",
        "supported_inference",
        assumption="curtailed export energy remains in the store absent any observable discharge",
    )
    assert entry.assumption


def test_money_must_be_labelled_and_never_attaches_to_the_unobservable() -> None:
    with pytest.raises(ValueError, match="labelled"):
        LedgerEntry(
            "2026-05-10", 21, "E_STOR-1", "bid-down", "observed", amount_gbp=Decimal("-4606")
        )
    with pytest.raises(ValueError, match="question mark"):
        LedgerEntry(
            "2026-05-10",
            21,
            "E_STOR-1",
            "intraday re-sale",
            "not_publicly_observable",
            amount_gbp=Decimal("100"),
            money_kind="acceptance_notional",
        )
    ok = LedgerEntry(
        "2026-05-10",
        21,
        "E_STOR-1",
        "bid-down cashflow",
        "observed",
        amount_gbp=Decimal("-4606.55613"),
        money_kind="published_indicative_bm_cashflow",
    )
    assert ok.money_kind == "published_indicative_bm_cashflow"


@given(seed=st.randoms(), n=st.integers(2, 12))
def test_timeline_order_is_deterministic_under_permutation(seed, n):
    entries = [
        LedgerEntry("2026-05-10", 1 + (i * 7) % 48, f"U{i % 3}", f"step {i}", "observed")
        for i in range(n)
    ]
    shuffled = list(entries)
    seed.shuffle(shuffled)
    assert ordered(shuffled) == ordered(entries)


def test_gaps_are_surfaced_never_smoothed() -> None:
    entries = [
        LedgerEntry("2026-05-10", 20, "E_STOR-1", "curtailed", "observed"),
        LedgerEntry("2026-05-10", 23, "E_STOR-1", "curtailed again", "observed"),
    ]
    assert period_gaps(entries) == [("2026-05-10", 21), ("2026-05-10", 22)]
