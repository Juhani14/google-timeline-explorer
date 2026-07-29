import sqlite3

conn = sqlite3.connect("timeline.db")
cur = conn.cursor()

cur.execute("""
SELECT COUNT(*)
FROM (
    SELECT DISTINCT
        v.latitude,
        v.longitude,
        v.place_id
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
)
""")

print("Unknown unique places:", cur.fetchone()[0])

conn.close()