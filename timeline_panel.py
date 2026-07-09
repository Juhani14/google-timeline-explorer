# timeline_panel.py

import streamlit as st

from config import ICONS
from utils import duration_minutes, average_speed


class TimelinePanel:

    def __init__(self, data):
        self.data = data

    def summary(self):
        st.subheader("📊 Summary")

        total_distance = self.data.activities["distance"].sum() / 1000

        st.metric("Visits", len(self.data.visits))
        st.metric("Activities", len(self.data.activities))
        st.metric("Distance", f"{total_distance:.1f} km")

        if len(self.data.activities):
            st.metric(
                "Average trip",
                f"{total_distance / len(self.data.activities):.1f} km"
            )

        st.divider()

    def timeline(self):
        st.subheader("🕒 Timeline")

        events = []

        for _, v in self.data.visits.iterrows():
            minutes = duration_minutes(v.start_time, v.end_time)

            events.append({
                "time": v.start_time,
                "text": f"📍 {v.place_name}\n{minutes:.0f} min"
            })

        for _, a in self.data.activities.iterrows():
            minutes = duration_minutes(a.start_time, a.end_time)
            speed = average_speed(a.distance, minutes)
            icon = ICONS.get(a.activity_type, "➡️")

            events.append({
                "time": a.start_time,
                "text": (
                    f"{icon} {a.activity_type}\n"
                    f"{a.distance:.0f} m\n"
                    f"{minutes:.0f} min\n"
                    f"{speed:.1f} km/h"
                )
            })

        events.sort(key=lambda e: e["time"])

        for e in events:
            st.write(f"**{e['time'][11:16]}**")
            st.write(e["text"])
            st.divider()

    def show(self):
        self.summary()
        self.timeline()