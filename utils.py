# utils.py

from datetime import datetime


def parse_time(text):
    return datetime.fromisoformat(text)


def duration_minutes(start, end):
    return (
        parse_time(end) - parse_time(start)
    ).total_seconds() / 60


def average_speed(distance_m, minutes):
    if minutes <= 0:
        return 0

    return (distance_m / 1000) / (minutes / 60)