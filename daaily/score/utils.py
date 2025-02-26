def compute_score(count: int, target_count: int) -> float:
    if count > target_count:
        return 1.0
    elif count == 0:
        return 0.0
    else:
        return 0.8
