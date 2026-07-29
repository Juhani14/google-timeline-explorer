# resolve_all_places.py

import sqlite3
import time
from datetime import datetime

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim


DB = "timeline.db"

# Public Nominatim requires a meaningful application User-Agent.
USER_AGENT = "google_timeline_explorer_juhani"

# Stay below the one-request-per-second limit.
DELAY_SECONDS = 1.1

# Commit regularly, so progress is preserved.
COMMIT_EVERY = 10

# Retry temporary failures.
MAX_RETRIES = 3


def get_unknown_places(conn):
    """
    Return unique visit locations not yet present in place_cache.
    """

    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT
            v.latitude,
            v.longitude,
            COALESCE(v.place_id, '') AS place_id
        FROM visits v

        LEFT JOIN place_cache pc
          ON (
              v.place_id <> ''
              AND pc.place_id = v.place_id
          )
          OR (
              pc.latitude = v.latitude
              AND pc.longitude = v.longitude
          )

        WHERE pc.id IS NULL
          AND v.latitude IS NOT NULL
          AND v.longitude IS NOT NULL

        ORDER BY v.latitude, v.longitude
    """)

    return cur.fetchall()


def save_place(
    conn,
    latitude,
    longitude,
    place_id,
    name,
    address,
    city,
    country
):
    cur = conn.cursor()

    cur.execute("""
        INSERT OR REPLACE INTO place_cache(
            latitude,
            longitude,
            place_id,
            name,
            address,
            city,
            country,
            last_updated
        )
        VALUES(?,?,?,?,?,?,?,?)
    """, (
        latitude,
        longitude,
        place_id or None,
        name,
        address,
        city,
        country,
        datetime.now().isoformat(timespec="seconds")
    ))


def save_failed_place(
    conn,
    latitude,
    longitude,
    place_id
):
    """
    Save an empty cache entry so permanently unresolved coordinates
    are not requested repeatedly every time the script runs.
    """

    save_place(
        conn=conn,
        latitude=latitude,
        longitude=longitude,
        place_id=place_id,
        name=None,
        address=None,
        city=None,
        country=None
    )


def reverse_geocode(
    geolocator,
    latitude,
    longitude
):
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return geolocator.reverse(
                (latitude, longitude),
                exactly_one=True,
                language="en",
                addressdetails=True
            )

        except (GeocoderTimedOut, GeocoderServiceError) as error:
            print(
                f"  Attempt {attempt}/{MAX_RETRIES} failed: "
                f"{error}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(5)

    return None


def extract_place_data(location):
    raw = location.raw or {}
    details = raw.get("address", {})

    name = (
        raw.get("name")
        or details.get("amenity")
        or details.get("tourism")
        or details.get("shop")
        or details.get("building")
        or details.get("office")
        or details.get("leisure")
        or details.get("road")
    )

    city = (
        details.get("city")
        or details.get("town")
        or details.get("village")
        or details.get("municipality")
        or details.get("county")
    )

    country = details.get("country")
    address = location.address

    return name, address, city, country


def main():
    conn = sqlite3.connect(DB)

    try:
        unknown_places = get_unknown_places(conn)
        total = len(unknown_places)

        print("Database:", DB)
        print("Unknown unique places:", total)
        print()

        if total == 0:
            print("All places are already cached.")
            return

        geolocator = Nominatim(
            user_agent=USER_AGENT,
            timeout=20
        )

        resolved = 0
        unresolved = 0

        for number, (
            latitude,
            longitude,
            place_id
        ) in enumerate(unknown_places, start=1):

            print(
                f"[{number}/{total}] "
                f"{latitude:.7f}, {longitude:.7f}"
            )

            location = reverse_geocode(
                geolocator,
                latitude,
                longitude
            )

            if location is None:
                print("  No result.")

                save_failed_place(
                    conn,
                    latitude,
                    longitude,
                    place_id
                )

                unresolved += 1

            else:
                name, address, city, country = (
                    extract_place_data(location)
                )

                save_place(
                    conn=conn,
                    latitude=latitude,
                    longitude=longitude,
                    place_id=place_id,
                    name=name,
                    address=address,
                    city=city,
                    country=country
                )

                resolved += 1

                print("  Name:   ", name)
                print("  City:   ", city)
                print("  Country:", country)

            # Save progress regularly.
            if number % COMMIT_EVERY == 0:
                conn.commit()

                print(
                    f"  Progress saved. "
                    f"Resolved={resolved}, "
                    f"unresolved={unresolved}"
                )

            # Required delay for the public server.
            time.sleep(DELAY_SECONDS)

        conn.commit()

        print()
        print("Finished.")
        print("Resolved:  ", resolved)
        print("Unresolved:", unresolved)
        print("Processed: ", total)

    except KeyboardInterrupt:
        conn.commit()

        print()
        print("Stopped by user.")
        print("Progress was saved.")
        print(
            "Run the program again later to continue "
            "with the remaining places."
        )

    finally:
        conn.close()


if __name__ == "__main__":
    main()