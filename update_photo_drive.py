import sqlite3

DB = "timeline.db"

OLD_PREFIX = r"D:\MyPictures"
NEW_PREFIX = r"F:\MyPictures"


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM photos
        WHERE filepath LIKE ?
        """,
        (OLD_PREFIX + "%",)
    )

    count = cur.fetchone()[0]

    print("Paths to update:", count)

    cur.execute(
        """
        UPDATE photos
        SET filepath =
            ? || substr(filepath, ?)
        WHERE filepath LIKE ?
        """,
        (
            NEW_PREFIX,
            len(OLD_PREFIX) + 1,
            OLD_PREFIX + "%"
        )
    )

    conn.commit()

    print("Updated rows:", cur.rowcount)

    conn.close()


if __name__ == "__main__":
    main()