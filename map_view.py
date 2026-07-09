# map_view.py

import folium
from streamlit_folium import st_folium

from config import COLORS, MAP_ZOOM
from utils import duration_minutes, average_speed


class TimelineMap:

    def __init__(self, data):

        self.data = data

        self.map = folium.Map(
            location=self._center(),
            zoom_start=MAP_ZOOM
        )

    # ----------------------------------------
    # Determine centre of map
    # ----------------------------------------

    def _center(self):

        if len(self.data.visits):

            return [
                self.data.visits.iloc[0]["latitude"],
                self.data.visits.iloc[0]["longitude"]
            ]

        if len(self.data.activities):

            return [
                self.data.activities.iloc[0]["start_lat"],
                self.data.activities.iloc[0]["start_lon"]
            ]

        return [0, 0]

    # ----------------------------------------
    # Draw visit markers
    # ----------------------------------------

    def draw_visits(self):

        for _, v in self.data.visits.iterrows():

            minutes = duration_minutes(
                v.start_time,
                v.end_time
            )

            popup = f"""
Visit

Start:
{v.start_time}

End:
{v.end_time}

Duration:
{minutes:.0f} min
"""

            folium.Marker(
                location=[
                    v.latitude,
                    v.longitude
                ],
                popup=popup,
                icon=folium.Icon(
                    color="red",
                    icon="home"
                )
            ).add_to(self.map)

    # ----------------------------------------
    # Draw activity lines
    # ----------------------------------------

    def draw_activities(self):

        for _, a in self.data.activities.iterrows():

            minutes = duration_minutes(
                a.start_time,
                a.end_time
            )

            speed = average_speed(
                a.distance,
                minutes
            )

            color = COLORS.get(
                a.activity_type,
                "gray"
            )

            tooltip = (
                f"{a.activity_type}\n"
                f"{a.distance:.0f} m\n"
                f"{minutes:.0f} min\n"
                f"{speed:.1f} km/h"
            )

            folium.PolyLine(
                [
                    [a.start_lat, a.start_lon],
                    [a.end_lat, a.end_lon]
                ],
                color=color,
                weight=5,
                tooltip=tooltip
            ).add_to(self.map)

    # ----------------------------------------
    # Draw everything
    # ----------------------------------------

    def build(self):

        self.draw_visits()
        self.draw_activities()

    # ----------------------------------------
    # Show map in Streamlit
    # ----------------------------------------

    def show(self):

        self.build()

        st_folium(
            self.map,
            width=900,
            height=700
        )