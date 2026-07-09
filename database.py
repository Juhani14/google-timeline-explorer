# database.py

import sqlite3
import pandas as pd


class Database:

    def __init__(self, filename):

        self.conn = sqlite3.connect(filename)

    def dates(self):

        return pd.read_sql("""

        SELECT DISTINCT
            substr(start_time,1,10) AS d

        FROM visits

        ORDER BY d DESC

        """, self.conn)

    def visits(self, day):

        return pd.read_sql("""

        SELECT *

        FROM visits

        WHERE substr(start_time,1,10)=?

        ORDER BY start_time

        """, self.conn, params=(day,))

    def activities(self, day):

        return pd.read_sql("""

        SELECT *

        FROM activities

        WHERE substr(start_time,1,10)=?

        ORDER BY start_time

        """, self.conn, params=(day,))
        
    def get_place_name(self, latitude, longitude, place_id=None):
        cur = self.conn.cursor()

        if place_id:
            cur.execute("""
            SELECT name, address, city, country
            FROM place_cache
            WHERE place_id=?
            """, (place_id,))

            row = cur.fetchone()

            if row:
                name, address, city, country = row
                return name or address or city or country

        cur.execute("""
        SELECT name, address, city, country
        FROM place_cache
        WHERE latitude=? AND longitude=?
        """, (latitude, longitude))

        row = cur.fetchone()

        if row:
            name, address, city, country = row
            return name or address or city or country

        return None

    def save_place_name(
        self,
        latitude,
        longitude,
        name=None,
        address=None,
        place_id=None,
        city=None,
        country=None,
        last_updated=None
    ):
        cur = self.conn.cursor()

        cur.execute("""
        INSERT OR REPLACE INTO place_cache(
            latitude,
            longitude,
            place_id,
            name,
            address,
            city,
            country,
            last_updated
        )
        VALUES(?,?,?,?,?,?,?,?)
        """, (
            latitude,
            longitude,
            place_id,
            name,
            address,
            city,
            country,
            last_updated
        ))

        self.conn.commit()    
        
    def close(self):

        self.conn.close()