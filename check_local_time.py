import sqlite3

conn = sqlite3.connect("timeline.db")
cur = conn.cursor()

cur.execute("""
SELECT
    start_time,
    local_start_time,
    start_timezone_offset,
    latitude,
    longitude
FROM visits
WHERE start_timezone_offset = 60
ORDER BY start_time DESC
LIMIT 20
""")

for row in cur.fetchall():
    print(row)

conn.close()