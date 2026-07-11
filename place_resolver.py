# place_resolver.py

import time
from datetime import datetime

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim


class PlaceResolver:

    def __init__(self, database):
        self.db = database

        self.geolocator = Nominatim(
            user_agent="google_timeline_explorer_juhani",
            timeout=15
        )

    def resolve(self, latitude, longitude, place_id=None):
        cached = self.db.get_place_name(
            latitude,
            longitude,
            place_id
        )

        if cached:
            return cached

        try:
            location = self.geolocator.reverse(
                (latitude, longitude),
                exactly_one=True,
                language="en",
                addressdetails=True
            )

        except (GeocoderTimedOut, GeocoderServiceError):
            return None

        if location is None:
            return None

        raw = location.raw
        address_data = raw.get("address", {})

        name = (
            raw.get("name")
            or address_data.get("amenity")
            or address_data.get("shop")
            or address_data.get("building")
            or address_data.get("road")
        )

        city = (
            address_data.get("city")
            or address_data.get("town")
            or address_data.get("village")
            or address_data.get("municipality")
        )

        country = address_data.get("country")
        address = location.address

        self.db.save_place_name(
            latitude=latitude,
            longitude=longitude,
            place_id=place_id,
            name=name,
            address=address,
            city=city,
            country=country,
            last_updated=datetime.now().isoformat(
                timespec="seconds"
            )
        )

        # Respect Nominatim public-service limit.
        time.sleep(1.1)

        return name or address or city or country