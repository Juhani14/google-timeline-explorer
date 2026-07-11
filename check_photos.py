import sqlite3

conn = sqlite3.connect("timeline.db")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM photos")
print("All imported photos:", cur.fetchone()[0])

cur.execute("""
SELECT COUNT(*)
FROM photos
WHERE taken_time IS NOT NULL
""")
print("Photos with timestamp:", cur.fetchone()[0])

cur.execute("""
SELECT COUNT(*)
FROM photos
WHERE latitude IS NOT NULL
  AND longitude IS NOT NULL
""")
print("Photos with GPS:", cur.fetchone()[0])

cur.execute("""
SELECT
    filename,
    taken_time,
    latitude,
    longitude
FROM photos
WHERE taken_time IS NOT NULL
LIMIT 10
""")

print()
for row in cur.fetchall():
    print(row)

conn.close()