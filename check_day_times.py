import sqlite3

DAY = "2026-03-19"  # change to the date you are checking

conn = sqlite3.connect("timeline.db")
cur = conn.cursor()

print("VISITS")
cur.execute("""
SELECT start_time, end_time, latitude, longitude
FROM visits
WHERE substr(start_time, 1, 10) = ?
ORDER BY start_time
""", (DAY,))

for row in cur.fetchall():
    print(row)

print("\nACTIVITIES")
cur.execute("""
SELECT start_time, end_time, activity_type, distance
FROM activities
WHERE substr(start_time, 1, 10) = ?
ORDER BY start_time
""", (DAY,))

for row in cur.fetchall():
    print(row)

conn.close()