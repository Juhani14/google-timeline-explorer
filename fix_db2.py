import sqlite3

conn = sqlite3.connect("timeline.db")
cur = conn.cursor()

# Add place_id column if it does not already exist
try:
    cur.execute("ALTER TABLE place_cache ADD COLUMN place_id TEXT")
    print("Added place_id column.")
except sqlite3.OperationalError:
    print("place_id column already exists.")

try:
    cur.execute("ALTER TABLE place_cache ADD COLUMN city TEXT")
    print("Added city column.")
except sqlite3.OperationalError:
    print("city column already exists.")

try:
    cur.execute("ALTER TABLE place_cache ADD COLUMN country TEXT")
    print("Added country column.")
except sqlite3.OperationalError:
    print("country column already exists.")

try:
    cur.execute("ALTER TABLE place_cache ADD COLUMN last_updated TEXT")
    print("Added last_updated column.")
except sqlite3.OperationalError:
    print("last_updated column already exists.")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_place_cache_place_id
ON place_cache(place_id)
""")

conn.commit()
conn.close()

print("Database upgraded.")