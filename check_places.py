import sqlite3

DAY = "2026-07-01"   # change this to the day you are viewing

conn = sqlite3.connect("timeline.db")
cur = conn.cursor()

cur.execute("""
SELECT
    v.start_time,
    v.latitude,
    v.longitude,
    v.place_id,
    pc.name,
    pc.address
FROM visits v
LEFT JOIN place_cache pc
    ON (
        pc.place_id = v.place_id
        AND v.place_id <> ''
    )
    OR (
        pc.latitude = v.latitude
        AND pc.longitude = v.longitude
    )
WHERE substr(v.start_time, 1, 10) = ?
ORDER BY v.start_time
""", (DAY,))

rows = cur.fetchall()

if not rows:
    print("No visits found for", DAY)
else:
    for row in rows:
        start_time, lat, lon, place_id, name, address = row

        print("-" * 60)
        print("Time:    ", start_time)
        print("Location:", lat, lon)
        print("Place ID:", place_id)
        print("Name:    ", name)
        print("Address: ", address)

conn.close()