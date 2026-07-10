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

        if len(self.data.paths):
            return [
                self.data.paths.iloc[0]["latitude"],
                self.data.paths.iloc[0]["longitude"]
            ]

        return [0, 0]

    def draw_visits(self):

        for _, v in self.data.visits.iterrows():

            minutes = duration_minutes(
                v.start_time,
                v.end_time
            )

            place_name = getattr(v, "place_name", "Visit")

            popup = (
                f"{place_name}<br>"
                f"Start: {v.start_time}<br>"
                f"End: {v.end_time}<br>"
                f"Duration: {minutes:.0f} min"
            )

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

    def draw_paths(self):

        if len(self.data.paths) == 0:
            return

        for _, group in self.data.paths.groupby("path_id"):

            group = group.sort_values("sequence")

            points = group[
                ["latitude", "longitude"]
            ].values.tolist()

            if len(points) < 2:
                continue

            folium.PolyLine(
                points,
                color="darkblue",
                weight=4,
                opacity=0.8,
                tooltip="Recorded Timeline path"
            ).add_to(self.map)

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
                f"{a.activity_type} | "
                f"{a.distance:.0f} m | "
                f"{minutes:.0f} min | "
                f"{speed:.1f} km/h"
            )

            folium.PolyLine(
                [
                    [a.start_lat, a.start_lon],
                    [a.end_lat, a.end_lon]
                ],
                color=color,
                weight=3,
                opacity=0.5,
                tooltip=tooltip
            ).add_to(self.map)

    def build(self):
        self.draw_visits()
        self.draw_paths()

    def show(self):
        self.build()

        st_folium(
            self.map,
            width=900,
            height=700
        )