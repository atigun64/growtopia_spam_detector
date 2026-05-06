def weighted(items):
    """
    Convert:
        [("a", 3), ("b", 1)]
    into:
        ["a", "a", "a", "b"]
    """
    out = []
    for value, weight in items:
        out.extend([value] * weight)
    return out