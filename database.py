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

    def close(self):

        self.conn.close()