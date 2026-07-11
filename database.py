# database.py

import sqlite3
import pandas as pd


class Database:

    def __init__(self, filename):

        self.conn = sqlite3.connect(filename)

        
    def dates(self):
        return pd.read_sql("""
        SELECT DISTINCT substr(local_start_time,1,10) AS d
        FROM visits
        WHERE local_start_time IS NOT NULL

        UNION

        SELECT DISTINCT substr(local_start_time,1,10) AS d
        FROM activities
        WHERE local_start_time IS NOT NULL

        ORDER BY d DESC
        """, self.conn)        
        
        
        
    def visits(self, day):
        return pd.read_sql("""
        SELECT *
        FROM visits
        WHERE substr(local_start_time,1,10)=?
        ORDER BY local_start_time
        """, self.conn, params=(day,))        
        
    def activities(self, day):
        return pd.read_sql("""
        SELECT *
        FROM activities
        WHERE substr(local_start_time,1,10)=?
        ORDER BY local_start_time
        """, self.conn, params=(day,))        
        


    def paths(self, day):
        return pd.read_sql("""
        SELECT
            ps.id AS path_id,
            ps.start_time,
            ps.end_time,
            pp.sequence,
            pp.point_time,
            pp.latitude,
            pp.longitude
        FROM path_segments ps
        JOIN path_points pp
            ON pp.path_id = ps.id
        WHERE substr(ps.start_time,1,10)=?
        ORDER BY ps.start_time, pp.sequence
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
        
    def unknown_places_for_day(self, day):
        return pd.read_sql("""
        SELECT DISTINCT
            v.latitude,
            v.longitude,
            v.place_id
        FROM visits v

        LEFT JOIN place_cache pc
          ON (
              pc.place_id = v.place_id
              AND v.place_id <> ''
          )
          OR (
              pc.latitude = v.latitude
              AND pc.longitude = v.longitude
          )

        WHERE substr(v.start_time, 1, 10) = ?
          AND pc.id IS NULL

        ORDER BY v.start_time
        """, self.conn, params=(day,))
        
        
    def unknown_places(self, limit=20):
        return pd.read_sql("""
        SELECT DISTINCT
            v.latitude,
            v.longitude,
            v.place_id
        FROM visits v

        LEFT JOIN place_cache pc
          ON (
              pc.place_id = v.place_id
              AND v.place_id <> ''
          )
          OR (
              pc.latitude = v.latitude
              AND pc.longitude = v.longitude
          )

        WHERE pc.id IS NULL

        LIMIT ?
        """, self.conn, params=(limit,))  

    def photos(self, day):
        return pd.read_sql("""
        SELECT
            id,
            filepath,
            filename,
            taken_time,
            latitude,
            longitude,
            width,
            height
        FROM photos
        WHERE substr(taken_time, 1, 10) = ?
        ORDER BY taken_time
        """, self.conn, params=(day,))        

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