# timeline_panel.py

import streamlit as st

from config import ICONS
from pathlib import Path
from utils import (
    duration_minutes,
    average_speed,
    local_time_text
)


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

            visit_photos = self.data.photos_for_visit(visit)

            events.append({
                "kind": "visit",
                "time": visit.start_time,
                "timezone_offset": visit.start_timezone_offset,
                "title": f"📍 {place_name}",
                "details": f"{minutes:.0f} min",
                "path_id": None,
                "photos": visit_photos
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
                "timezone_offset": activity.start_timezone_offset,
                "title": f"{icon} {activity.activity_type}",
                "details": (
                    f"{activity.distance:.0f} m · "
                    f"{minutes:.0f} min · "
                    f"{speed:.1f} km/h"
                ),
                "path_id": path_id,
                "photos": None
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
            time_text = local_time_text(
                event["time"],
                event.get("timezone_offset")
            )

            st.markdown(
                f"**{time_text} — {event['title']}**"
            )

            st.caption(event["details"])
            
            photos = event.get("photos")

            if photos is not None and len(photos) > 0:

                st.caption(f"📷 {len(photos)} photos")

                photo_columns = st.columns(
                    min(3, len(photos))
                )

                for position, (_, photo) in enumerate(
                    photos.head(6).iterrows()
                ):
                    filepath = Path(photo.filepath)

                    if not filepath.exists():
                        continue

                    with photo_columns[
                        position % len(photo_columns)
                    ]:
                        st.image(
                            str(filepath),
                            use_container_width=True
                        )

                        photo_time = (
                            photo.taken_time[11:16]
                            if photo.taken_time
                            else ""
                        )

                        st.caption(photo_time)

                if len(photos) > 6:
                    st.caption(
                        f"+ {len(photos) - 6} more photos "
                        "in the photo gallery below"
                    )            

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