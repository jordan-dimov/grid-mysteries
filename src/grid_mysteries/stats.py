"""Small shared numerics for study aggregation."""


def percentile(sorted_values: list, fraction: float):
    """Nearest-rank percentile over an already-sorted list (the convention
    declared and used by the method studies)."""
    index = min(len(sorted_values) - 1, int(fraction * len(sorted_values)))
    return sorted_values[index]


def _average_ranks(values: list) -> list[float]:
    """1-based ranks with ties sharing their mean rank."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranked = [0.0] * len(values)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        average = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranked[order[k]] = average
        i = j + 1
    return ranked


def spearman(pairs: list[tuple]) -> float | None:
    """Spearman rank correlation with tie-averaged ranks; None when fewer
    than three pairs or either side is constant (undefined, not zero)."""
    if len(pairs) < 3:
        return None
    xs, ys = _average_ranks([p[0] for p in pairs]), _average_ranks([p[1] for p in pairs])
    n = len(pairs)
    mean_x, mean_y = sum(xs) / n, sum(ys) / n
    cov = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    var_x = sum((x - mean_x) ** 2 for x in xs)
    var_y = sum((y - mean_y) ** 2 for y in ys)
    return cov / (var_x * var_y) ** 0.5 if var_x and var_y else None
