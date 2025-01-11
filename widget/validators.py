from django.core.exceptions import ValidationError
from datetime import time


def validate_time_ranges(value):
    if not isinstance(value, list):
        raise ValidationError('"time_range" should be a list.')
    if len(value) != 2:
        raise ValidationError('"time_range" must contain exactly two time strings.')
    try:
        time.fromisoformat(value[0])
        time.fromisoformat(value[1])
    except ValueError:
        raise ValidationError(
            '"timeRange" values must be valid ISO 8601 time strings (e.g., "22:00").'
        )
