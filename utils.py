# utils.py

from datetime import datetime, timedelta, timezone


def parse_time(text):
    return datetime.fromisoformat(text)


def duration_minutes(start, end):
    start_dt = parse_time(start)
    end_dt = parse_time(end)

    return (
        end_dt - start_dt
    ).total_seconds() / 60


def average_speed(distance_m, minutes):
    if minutes <= 0:
        return 0

    return (
        distance_m / 1000
    ) / (
        minutes / 60
    )


def local_datetime(timestamp, offset_minutes=None):
    """
    Convert the timestamp to the local timezone offset stored
    by Google Timeline.

    Example:
    timestamp has +07:00, but Finland offset is 180 minutes.
    The result is converted to UTC+03:00.
    """

    dt = datetime.fromisoformat(timestamp)

    if offset_minutes is None:
        return dt

    target_timezone = timezone(
        timedelta(minutes=int(offset_minutes))
    )

    return dt.astimezone(target_timezone)


def local_time_text(timestamp, offset_minutes=None):
    return local_datetime(
        timestamp,
        offset_minutes
    ).strftime("%H:%M")