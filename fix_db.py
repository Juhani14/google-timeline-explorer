import sqlite3

import os
print("Current folder:", os.getcwd())
print("DB path:", os.path.abspath("timeline.db"))

conn = sqlite3.connect("timeline.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS place_cache(
    id INTEGER PRIMARY KEY,
    latitude REAL,
    longitude REAL,
    name TEXT,
    address TEXT,
    UNIQUE(latitude, longitude)
)
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_place_cache_latlon
ON place_cache(latitude, longitude)
""")

conn.commit()
conn.close()

print("place_cache table created.")