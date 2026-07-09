import streamlit as st
import pandas as pd


class KPIPanel:

    def __init__(self, db):
        self.db = db

    def show(self):

        visits = pd.read_sql(
            "SELECT COUNT(*) n FROM visits",
            self.db.conn
        ).iloc[0]["n"]

        activities = pd.read_sql(
            "SELECT COUNT(*) n FROM activities",
            self.db.conn
        ).iloc[0]["n"]

        distance = pd.read_sql(
            """
            SELECT SUM(distance)/1000 km
            FROM activities
            """,
            self.db.conn
        ).iloc[0]["km"]

        flights = pd.read_sql(
            """
            SELECT COUNT(*) n
            FROM activities
            WHERE activity_type='FLYING'
            """,
            self.db.conn
        ).iloc[0]["n"]

        years = pd.read_sql(
            """
            SELECT
                MIN(substr(start_time,1,4)) first,
                MAX(substr(start_time,1,4)) last
            FROM activities
            """,
            self.db.conn
        ).iloc[0]

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("📍 Visits", f"{visits:,}")
        c2.metric("🚶 Activities", f"{activities:,}")
        c3.metric("🌍 Distance", f"{distance:,.0f} km")
        c4.metric("✈ Flights", f"{flights:,}")
        c5.metric("📅 Years", f"{years.first}-{years.last}")