import json
import sqlite3
import os

DB = "timeline.db"

print("Importer folder:", os.getcwd())
print("Importer DB path:", os.path.abspath("timeline.db"))

if os.path.exists("timeline.db"):
    os.remove("timeline.db")
conn = sqlite3.connect(DB)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS visits(
    id INTEGER PRIMARY KEY,
    start_time TEXT,
    end_time TEXT,
    start_timezone_offset INTEGER,
    end_timezone_offset INTEGER,
    latitude REAL,
    longitude REAL,
    place_id TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS activities(
    id INTEGER PRIMARY KEY,
    start_time TEXT,
    end_time TEXT,
    start_timezone_offset INTEGER,
    end_timezone_offset INTEGER,
    start_lat REAL,
    start_lon REAL,
    end_lat REAL,
    end_lon REAL,
    activity_type TEXT,
    distance REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS path_segments(
    id INTEGER PRIMARY KEY,
    start_time TEXT,
    end_time TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS path_points(
    id INTEGER PRIMARY KEY,
    path_id INTEGER,
    sequence INTEGER,
    point_time TEXT,
    latitude REAL,
    longitude REAL
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS place_cache(
    id INTEGER PRIMARY KEY,
    latitude REAL,
    longitude REAL,
    place_id TEXT,
    name TEXT,
    address TEXT,
    city TEXT,
    country TEXT,
    last_updated TEXT,
    UNIQUE(latitude, longitude)
)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_place_cache_latlon
ON place_cache(latitude, longitude)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_place_cache_place_id
ON place_cache(place_id)
""")



cur.execute("""
CREATE INDEX IF NOT EXISTS idx_path_points_path
ON path_points(path_id, sequence)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_path_start
ON path_segments(start_time)
""")






with open("timeline.json","r",encoding="utf-8") as f:
    data=json.load(f)

segments=data["semanticSegments"]

def parse_latlng(text):
    lat,lon=text.replace("°","").split(",")
    return float(lat),float(lon)

for s in segments:

    # --------------------------------------------------
    # Visits
    # --------------------------------------------------

    if "visit" in s:

        p = s["visit"]["topCandidate"]

        lat, lon = parse_latlng(
            p["placeLocation"]["latLng"]
        )

        cur.execute("""
        INSERT INTO visits(
            start_time,
            end_time,
            start_timezone_offset,
            end_timezone_offset,
            latitude,
            longitude,
            place_id
        )
        VALUES(?,?,?,?,?,?,?)
        """, (
            s["startTime"],
            s["endTime"],
            s.get("startTimeTimezoneUtcOffsetMinutes"),
            s.get("endTimeTimezoneUtcOffsetMinutes"),
            lat,
            lon,
            p.get("placeId", "")
        ))

    # --------------------------------------------------
    # Activities
    # --------------------------------------------------

    if "activity" in s:

        a = s["activity"]

        slat, slon = parse_latlng(
            a["start"]["latLng"]
        )

        elat, elon = parse_latlng(
            a["end"]["latLng"]
        )

        cur.execute("""
        INSERT INTO activities(
            start_time,
            end_time,
            start_timezone_offset,
            end_timezone_offset,
            start_lat,
            start_lon,
            end_lat,
            end_lon,
            activity_type,
            distance
        )
        VALUES(?,?,?,?,?,?,?,?,?,?)
        """, (
            s["startTime"],
            s["endTime"],
            s.get("startTimeTimezoneUtcOffsetMinutes"),
            s.get("endTimeTimezoneUtcOffsetMinutes"),
            slat,
            slon,
            elat,
            elon,
            a["topCandidate"]["type"],
            a.get("distanceMeters", 0)
        ))

    # --------------------------------------------------
    # Timeline paths
    # --------------------------------------------------

    if "timelinePath" in s:

        cur.execute("""
        INSERT INTO path_segments(
            start_time,
            end_time
        )
        VALUES(?,?)
        """, (
            s["startTime"],
            s["endTime"]
        ))

        path_id = cur.lastrowid

        for sequence, point in enumerate(s["timelinePath"]):

            lat, lon = parse_latlng(
                point["point"]
            )

            cur.execute("""
            INSERT INTO path_points(
                path_id,
                sequence,
                point_time,
                latitude,
                longitude
            )
            VALUES(?,?,?,?,?)
            """, (
                path_id,
                sequence,
                point.get("time", ""),
                lat,
                lon
            ))

activity_id = cur.lastrowid


cur.execute("""
CREATE INDEX IF NOT EXISTS idx_visit_start
ON visits(start_time)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_activity_start
ON activities(start_time)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_path_start
ON path_segments(start_time)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_path_points_path
ON path_points(path_id, sequence)
""")

conn.commit()
conn.close()




print("Database created.")

