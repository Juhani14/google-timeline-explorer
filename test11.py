import sqlite3

conn = sqlite3.connect("timeline.db")
cur = conn.cursor()

cur.execute("""
SELECT latitude, longitude, place_id, name, address
FROM place_cache
LIMIT 20
""")

for row in cur.fetchall():
    print(row)

conn.close()