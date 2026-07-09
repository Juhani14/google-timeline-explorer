# statistics_panel.py

import streamlit as st
import pandas as pd


class StatisticsPanel:

    def __init__(self, db):
        self.db = db

    def activity_summary(self):
        df = pd.read_sql("""
        SELECT
            activity_type,
            COUNT(*) AS trips,
            SUM(distance) / 1000.0 AS km
        FROM activities
        GROUP BY activity_type
        ORDER BY trips DESC
        """, self.db.conn)

        st.subheader("🚶 Transport summary")
        st.dataframe(df, use_container_width=True)

    def yearly_distance(self):
        df = pd.read_sql("""
        SELECT
            substr(start_time,1,4) AS year,
            SUM(distance) / 1000.0 AS km
        FROM activities
        GROUP BY year
        ORDER BY year
        """, self.db.conn)

        st.subheader("📅 Distance by year")
        st.bar_chart(df.set_index("year"))

    def top_days(self):
        df = pd.read_sql("""
        SELECT
            substr(start_time,1,10) AS day,
            SUM(distance) / 1000.0 AS km,
            COUNT(*) AS activities
        FROM activities
        GROUP BY day
        ORDER BY km DESC
        LIMIT 20
        """, self.db.conn)

        st.subheader("🏆 Longest travel days")
        st.dataframe(df, use_container_width=True)
        
        
    def flights(self):
        df = pd.read_sql("""
        SELECT
            substr(start_time,1,10) AS day,
            start_time,
            end_time,
            distance / 1000.0 AS km
        FROM activities
        WHERE activity_type='FLYING'
        ORDER BY km DESC
        """, self.db.conn)

        st.subheader("✈ Flights")

        if len(df) == 0:
            st.write("No flights found.")
            return

        total_km = df["km"].sum()

        c1, c2, c3 = st.columns(3)

        c1.metric("Flights", len(df))
        c2.metric("Total distance", f"{total_km:.0f} km")
        c3.metric("Longest flight", f"{df.iloc[0]['km']:.0f} km")

        st.write("Longest flights")
        st.dataframe(df.head(20), use_container_width=True)        

    def overview(self):
        st.subheader("📊 Overview")

        visits = pd.read_sql("""
        SELECT COUNT(*) AS n
        FROM visits
        """, self.db.conn).iloc[0]["n"]

        activities = pd.read_sql("""
        SELECT COUNT(*) AS n
        FROM activities
        """, self.db.conn).iloc[0]["n"]

        distance = pd.read_sql("""
        SELECT SUM(distance) / 1000.0 AS km
        FROM activities
        """, self.db.conn).iloc[0]["km"]

        flights = pd.read_sql("""
        SELECT COUNT(*) AS n
        FROM activities
        WHERE activity_type='FLYING'
        """, self.db.conn).iloc[0]["n"]

        years = pd.read_sql("""
        SELECT
            MIN(substr(start_time,1,4)) AS first_year,
            MAX(substr(start_time,1,4)) AS last_year
        FROM activities
        """, self.db.conn).iloc[0]

        c1, c2, c3, c4, c5 = st.columns(5)

        c1.metric("Visits", int(visits))
        c2.metric("Activities", int(activities))
        c3.metric("Distance", f"{distance:.0f} km")
        c4.metric("Flights", int(flights))
        c5.metric("Years", f"{years.first_year}–{years.last_year}")

        
    def show(self):
        self.overview()
        st.divider()

        self.activity_summary()
        self.yearly_distance()
        self.top_days()
        self.flights()        
    
    
    