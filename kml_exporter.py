# kml_exporter.py

from html import escape
from pathlib import Path


class KMLExporter:

    def __init__(self, data):
        self.data = data

    @staticmethod
    def _safe(value):
        if value is None:
            return ""

        return escape(str(value))

    def _visit_placemarks(self):
        parts = []

        for _, visit in self.data.visits.iterrows():
            place_name = getattr(
                visit,
                "place_name",
                "Visit"
            )

            start_time = getattr(
                visit,
                "local_start_time",
                visit.start_time
            )

            end_time = getattr(
                visit,
                "local_end_time",
                visit.end_time
            )

            description = (
                f"Start: {self._safe(start_time)}<br/>"
                f"End: {self._safe(end_time)}<br/>"
                f"Latitude: {visit.latitude}<br/>"
                f"Longitude: {visit.longitude}"
            )

            parts.append(f"""
            <Placemark>
                <name>{self._safe(place_name)}</name>

                <description>
                    <![CDATA[
                    {description}
                    ]]>
                </description>

                <styleUrl>#visitStyle</styleUrl>

                <Point>
                    <coordinates>
                        {visit.longitude},{visit.latitude},0
                    </coordinates>
                </Point>
            </Placemark>
            """)

        return "\n".join(parts)

    def _path_placemarks(self):
        if len(self.data.paths) == 0:
            return ""

        parts = []

        for path_id, group in self.data.paths.groupby(
            "path_id"
        ):
            group = group.sort_values("sequence")

            coordinates = []

            for _, point in group.iterrows():
                coordinates.append(
                    f"{point.longitude},"
                    f"{point.latitude},0"
                )

            if len(coordinates) < 2:
                continue

            start_time = group.iloc[0]["start_time"]
            end_time = group.iloc[0]["end_time"]

            parts.append(f"""
            <Placemark>
                <name>Recorded path {int(path_id)}</name>

                <description>
                    <![CDATA[
                    Start: {self._safe(start_time)}<br/>
                    End: {self._safe(end_time)}
                    ]]>
                </description>

                <styleUrl>#pathStyle</styleUrl>

                <LineString>
                    <tessellate>1</tessellate>
                    <altitudeMode>clampToGround</altitudeMode>

                    <coordinates>
                        {' '.join(coordinates)}
                    </coordinates>
                </LineString>
            </Placemark>
            """)

        return "\n".join(parts)

    def _photo_placemarks(self):
        if len(self.data.photos) == 0:
            return ""

        parts = []

        for _, photo in self.data.photos.iterrows():
            if photo.latitude is None:
                continue

            if photo.longitude is None:
                continue

            filename = self._safe(photo.filename)
            taken_time = self._safe(photo.taken_time)
            filepath = self._safe(photo.filepath)

            parts.append(f"""
            <Placemark>
                <name>{filename}</name>

                <description>
                    <![CDATA[
                    Taken: {taken_time}<br/>
                    File: {filepath}
                    ]]>
                </description>

                <styleUrl>#photoStyle</styleUrl>

                <Point>
                    <coordinates>
                        {photo.longitude},{photo.latitude},0
                    </coordinates>
                </Point>
            </Placemark>
            """)

        return "\n".join(parts)

    def build(self):
        day = self._safe(self.data.day)

        return f"""<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">

<Document>

    <name>Google Timeline Explorer — {day}</name>

    <Style id="visitStyle">
        <IconStyle>
            <scale>1.1</scale>
            <Icon>
                <href>
                    http://maps.google.com/mapfiles/kml/pushpin/red-pushpin.png
                </href>
            </Icon>
        </IconStyle>
    </Style>

    <Style id="photoStyle">
        <IconStyle>
            <scale>0.9</scale>
            <Icon>
                <href>
                    http://maps.google.com/mapfiles/kml/shapes/camera.png
                </href>
            </Icon>
        </IconStyle>
    </Style>

    <Style id="pathStyle">
        <LineStyle>
            <color>ffff0000</color>
            <width>5</width>
        </LineStyle>
    </Style>

    <Folder>
        <name>Visits</name>
        {self._visit_placemarks()}
    </Folder>

    <Folder>
        <name>Recorded paths</name>
        {self._path_placemarks()}
    </Folder>

    <Folder>
        <name>Photos</name>
        {self._photo_placemarks()}
    </Folder>

</Document>

</kml>
"""