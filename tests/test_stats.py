import pytest

from grid_mysteries.stats import percentile, spearman


def test_percentile_is_nearest_rank_over_a_sorted_list() -> None:
    values = [1, 2, 3, 4]
    assert percentile(values, 0.0) == 1
    assert percentile(values, 0.5) == 3
    assert percentile(values, 1.0) == 4


def test_spearman_on_monotone_and_reversed_series() -> None:
    assert spearman([(1, 10), (2, 20), (3, 30)]) == pytest.approx(1.0)
    assert spearman([(1, 30), (2, 20), (3, 10)]) == pytest.approx(-1.0)


def test_spearman_averages_tied_ranks() -> None:
    # x ranks: 1, 2.5, 2.5, 4; y ranks: 1, 2, 3, 4.
    assert spearman([(1, 1), (2, 2), (2, 3), (3, 4)]) == pytest.approx(0.9486832980505138)


def test_spearman_is_undefined_below_three_pairs_or_on_a_constant_side() -> None:
    assert spearman([(1, 1), (2, 2)]) is None
    assert spearman([(5, 1), (5, 2), (5, 3)]) is None
