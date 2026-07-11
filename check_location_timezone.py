from utils import (
    timezone_from_coordinates,
    local_time_text
)

tests = [
    (
        "Paris",
        48.8566,
        2.3522,
        "2025-07-10T14:00:00+07:00",
        120
    ),
    (
        "London",
        51.5074,
        -0.1278,
        "2025-07-10T14:00:00+07:00",
        60
    ),
    (
        "Helsinki",
        60.1699,
        24.9384,
        "2025-07-10T14:00:00+07:00",
        180
    ),
    (
        "Bangkok",
        13.7563,
        100.5018,
        "2025-07-10T14:00:00+07:00",
        420
    )
]

for name, lat, lon, timestamp, offset in tests:
    timezone_name = timezone_from_coordinates(lat, lon)

    converted = local_time_text(
        timestamp,
        timezone_name=timezone_name,
        offset_minutes=offset
    )

    print(name)
    print("Timezone:", timezone_name)
    print("Local time:", converted)
    print()