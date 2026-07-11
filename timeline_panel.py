# timeline_panel.py

import streamlit as st

from config import ICONS
from utils import duration_minutes, average_speed


class TimelinePanel:

    def __init__(self, data):
        self.data = data

    def summary(self):
        st.subheader("📊 Summary")

        st.metric("Visits", self.data.visit_count)
        st.metric("Activities", self.data.activity_count)
        st.metric(
            "Distance",
            f"{self.data.total_distance_km:.1f} km"
        )

        if self.data.activity_count:
            st.metric(
                "Average trip",
                f"{self.data.average_trip:.1f} km"
            )

        st.divider()

    def build_events(self):
        events = []

        for _, visit in self.data.visits.iterrows():
            minutes = duration_minutes(
                visit.start_time,
                visit.end_time
            )

            place_name = getattr(
                visit,
                "place_name",
                "Visit"
            )

            events.append({
                "kind": "visit",
                "time": visit.start_time,
                "title": f"📍 {place_name}",
                "details":
                    f"{minutes:.0f} min\n"
                    f"{visit.latitude:.5f}, "
                    f"{visit.longitude:.5f}",
                "path_id": None
            })

        for _, activity in self.data.activities.iterrows():
            minutes = duration_minutes(
                activity.start_time,
                activity.end_time
            )

            speed = average_speed(
                activity.distance,
                minutes
            )

            icon = ICONS.get(
                activity.activity_type,
                "➡️"
            )

            path_id = self.data.path_id_for_activity(
                activity
            )

            events.append({
                "kind": "activity",
                "time": activity.start_time,
                "title": (
                    f"{icon} "
                    f"{activity.activity_type}"
                ),
                "details": (
                    f"{activity.distance:.0f} m · "
                    f"{minutes:.0f} min · "
                    f"{speed:.1f} km/h"
                ),
                "path_id": path_id
            })

        events.sort(key=lambda event: event["time"])

        return events

    def timeline(self):
        st.subheader("🕒 Timeline")

        events = self.build_events()

        if not events:
            st.info("No events for this day.")
            return

        for number, event in enumerate(events):
            time_text = event["time"][11:16]

            st.markdown(
                f"**{time_text} — {event['title']}**"
            )

            st.caption(event["details"])

            path_id = event["path_id"]

            if event["kind"] == "activity":
                if path_id is None:
                    st.caption(
                        "No recorded detailed path matched this activity."
                    )
                else:
                    is_selected = (
                        path_id == self.data.selected_path_id
                    )

                    label = (
                        "✓ Highlighted on map"
                        if is_selected
                        else "Show on map"
                    )

                    if st.button(
                        label,
                        key=f"show_path_{path_id}_{number}"
                    ):
                        st.session_state.selected_path_id = path_id
                        st.rerun()

            st.divider()

    def show(self):
        self.summary()
        self.timeline()