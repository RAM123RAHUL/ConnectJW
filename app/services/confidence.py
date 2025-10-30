def calculate_overall(field_confidences: dict) -> float:
    """
    Calculate overall confidence from field confidences

    Args:
        field_confidences: Dict mapping field paths to confidence scores (0-100)

    Returns:
        Overall confidence score (0-100)
    """
    if not field_confidences:
        return 0.0

    scores = []
    for value in field_confidences.values():
        # Handle nested dicts (for nested structures like location.venue)
        if isinstance(value, dict):
            scores.extend(_flatten_scores(value))
        else:
            scores.append(float(value))

    return round(sum(scores) / len(scores), 2) if scores else 0.0


def _flatten_scores(nested_dict: dict) -> list:
    """Recursively flatten nested confidence scores"""
    scores = []
    for value in nested_dict.values():
        if isinstance(value, dict):
            scores.extend(_flatten_scores(value))
        else:
            scores.append(float(value))
    return scores
