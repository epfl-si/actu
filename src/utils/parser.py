def _safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return None


def _safe_int_set(values):
    return {
        parsed
        for parsed in (_safe_int(value) for value in values)
        if parsed is not None
    }
