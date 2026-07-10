import sqlite3

conn = sqlite3.connect("timeline.db")
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM path_segments")
print("Path segments:", cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM path_points")
print("Path points:", cur.fetchone()[0])

conn.close()