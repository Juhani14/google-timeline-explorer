import sqlite3

DAY = "2026-03-21"  # use a Finland or France date

conn = sqlite3.connect("timeline.db")
cur = conn.cursor()

cur.execute("""
SELECT
    start_time,
    start_timezone_offset,
    end_time,
    end_timezone_offset
FROM visits
WHERE substr(start_time, 1, 10) = ?
ORDER BY start_time
LIMIT 20
""", (DAY,))

for row in cur.fetchall():
    print(row)

conn.close()