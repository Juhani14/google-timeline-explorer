# photo_importer.py

import os
import sqlite3
from datetime import datetime
from pathlib import Path

from PIL import Image
from PIL.ExifTags import GPSTAGS, TAGS


DB = "timeline.db"
PHOTO_ROOT = Path(r"D:\MyPictures")

PHOTO_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff"
}


def create_table(conn):
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS photos(
        id INTEGER PRIMARY KEY,
        filepath TEXT NOT NULL UNIQUE,
        filename TEXT NOT NULL,
        taken_time TEXT,
        latitude REAL,
        longitude REAL,
        width INTEGER,
        height INTEGER,
        file_modified_time TEXT,
        imported_time TEXT
    )
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_photos_taken_time
    ON photos(taken_time)
    """)

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_photos_lat_lon
    ON photos(latitude, longitude)
    """)

    conn.commit()


def rational_to_float(value):
    try:
        return float(value)
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0


def gps_to_decimal(values, reference):
    degrees = rational_to_float(values[0])
    minutes = rational_to_float(values[1])
    seconds = rational_to_float(values[2])

    result = degrees + minutes / 60 + seconds / 3600

    if reference in ("S", "W"):
        result = -result

    return result


def read_exif(image):
    exif = image.getexif()

    if not exif:
        return {}, {}

    normal = {}
    gps = {}

    for tag_id, value in exif.items():
        tag_name = TAGS.get(tag_id, tag_id)

        if tag_name != "GPSInfo":
            normal[tag_name] = value

    try:
        from PIL.ExifTags import IFD

        gps_ifd = exif.get_ifd(IFD.GPSInfo)

        for gps_id, gps_value in gps_ifd.items():
            gps_name = GPSTAGS.get(gps_id, gps_id)
            gps[gps_name] = gps_value

    except Exception:
        gps = {}

    return normal, gps


def parse_taken_time(exif):
    value = (
        exif.get("DateTimeOriginal")
        or exif.get("DateTimeDigitized")
        or exif.get("DateTime")
    )

    if not value:
        return None

    try:
        dt = datetime.strptime(
            str(value),
            "%Y:%m:%d %H:%M:%S"
        )
        return dt.isoformat(timespec="seconds")

    except ValueError:
        return None


def parse_gps(gps):
    latitude_values = gps.get("GPSLatitude")
    latitude_ref = gps.get("GPSLatitudeRef")

    longitude_values = gps.get("GPSLongitude")
    longitude_ref = gps.get("GPSLongitudeRef")

    if not all([
        latitude_values,
        latitude_ref,
        longitude_values,
        longitude_ref
    ]):
        return None, None

    latitude = gps_to_decimal(
        latitude_values,
        latitude_ref
    )

    longitude = gps_to_decimal(
        longitude_values,
        longitude_ref
    )

    return latitude, longitude


def already_imported(conn, filepath):
    cur = conn.cursor()

    cur.execute("""
    SELECT 1
    FROM photos
    WHERE filepath=?
    """, (str(filepath),))

    return cur.fetchone() is not None


def import_photo(conn, filepath):
    if already_imported(conn, filepath):
        return "skipped"

    try:
        with Image.open(filepath) as image:
            width, height = image.size
            exif, gps = read_exif(image)

        taken_time = parse_taken_time(exif)
        latitude, longitude = parse_gps(gps)

        modified = datetime.fromtimestamp(
            filepath.stat().st_mtime
        ).isoformat(timespec="seconds")

        imported = datetime.now().isoformat(
            timespec="seconds"
        )

        cur = conn.cursor()

        cur.execute("""
        INSERT INTO photos(
            filepath,
            filename,
            taken_time,
            latitude,
            longitude,
            width,
            height,
            file_modified_time,
            imported_time
        )
        VALUES(?,?,?,?,?,?,?,?,?)
        """, (
            str(filepath),
            filepath.name,
            taken_time,
            latitude,
            longitude,
            width,
            height,
            modified,
            imported
        ))

        return "imported"

    except Exception as error:
        print(f"ERROR: {filepath}")
        print(f"       {error}")
        return "error"


def find_photos(root):
    for folder, _, filenames in os.walk(root):
        for filename in filenames:
            filepath = Path(folder) / filename

            if filepath.suffix.lower() in PHOTO_EXTENSIONS:
                yield filepath


def main():
    if not PHOTO_ROOT.exists():
        print("Photo folder does not exist:")
        print(PHOTO_ROOT)
        return

    conn = sqlite3.connect(DB)
    create_table(conn)

    imported = 0
    skipped = 0
    errors = 0

    photos = list(find_photos(PHOTO_ROOT))
    total = len(photos)

    print("Photo folder:", PHOTO_ROOT)
    print("Photos found:", total)
    print()

    for number, filepath in enumerate(photos, start=1):
        result = import_photo(conn, filepath)

        if result == "imported":
            imported += 1
        elif result == "skipped":
            skipped += 1
        else:
            errors += 1

        if number % 100 == 0 or number == total:
            conn.commit()

            print(
                f"{number}/{total}  "
                f"imported={imported}  "
                f"skipped={skipped}  "
                f"errors={errors}"
            )

    conn.commit()
    conn.close()

    print()
    print("Finished.")
    print("Imported:", imported)
    print("Skipped: ", skipped)
    print("Errors:  ", errors)


if __name__ == "__main__":
    main()