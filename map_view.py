# map_view.py

import folium
from streamlit_folium import st_folium

from config import MAP_ZOOM
from utils import duration_minutes


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

        if len(self.data.paths):
            return [
                self.data.paths.iloc[0]["latitude"],
                self.data.paths.iloc[0]["longitude"]
            ]

        if len(self.data.activities):
            return [
                self.data.activities.iloc[0]["start_lat"],
                self.data.activities.iloc[0]["start_lon"]
            ]

        return [0, 0]

    def draw_visits(self):
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

            popup = (
                f"<b>{place_name}</b><br>"
                f"Start: {visit.start_time}<br>"
                f"End: {visit.end_time}<br>"
                f"Duration: {minutes:.0f} min"
            )

            folium.Marker(
                location=[
                    visit.latitude,
                    visit.longitude
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

        selected_bounds = None

        for path_id, group in self.data.paths.groupby("path_id"):
            group = group.sort_values("sequence")

            points = group[
                ["latitude", "longitude"]
            ].values.tolist()

            if len(points) < 2:
                continue

            path_id = int(path_id)

            selected = (
                path_id == self.data.selected_path_id
            )

            if selected:
                color = "red"
                weight = 8
                opacity = 1.0
                selected_bounds = points
            else:
                color = "royalblue"
                weight = 6
                opacity = 0.60

            folium.PolyLine(
                points,
                color=color,
                weight=weight,
                opacity=opacity,
                tooltip=(
                    "Selected Timeline path"
                    if selected
                    else "Recorded Timeline path"
                )
            ).add_to(self.map)

        if selected_bounds:
            self.map.fit_bounds(selected_bounds)

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