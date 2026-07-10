# timeline_data.py

import pandas as pd


class TimelineData:

    def __init__(
        self,
        day,
        visits,
        activities,
        paths,
        selected_path_id=None
    ):
        self.day = day
        self.visits = visits
        self.activities = activities
        self.paths = paths
        self.selected_path_id = selected_path_id

    @property
    def visit_count(self):
        return len(self.visits)

    @property
    def activity_count(self):
        return len(self.activities)

    @property
    def total_distance(self):
        if len(self.activities) == 0:
            return 0

        return self.activities["distance"].sum()

    @property
    def total_distance_km(self):
        return self.total_distance / 1000

    @property
    def average_trip(self):
        if self.activity_count == 0:
            return 0

        return self.total_distance_km / self.activity_count

    def path_id_for_activity(self, activity):
        """
        Find the recorded path whose time range overlaps the activity.

        If several paths overlap, choose the one whose midpoint is
        closest to the activity midpoint.
        """

        if len(self.paths) == 0:
            return None

        path_ranges = (
            self.paths[
                ["path_id", "start_time", "end_time"]
            ]
            .drop_duplicates("path_id")
            .copy()
        )

        activity_start = pd.to_datetime(activity.start_time)
        activity_end = pd.to_datetime(activity.end_time)

        path_ranges["path_start"] = pd.to_datetime(
            path_ranges["start_time"]
        )

        path_ranges["path_end"] = pd.to_datetime(
            path_ranges["end_time"]
        )

        overlapping = path_ranges[
            (path_ranges["path_start"] <= activity_end) &
            (path_ranges["path_end"] >= activity_start)
        ].copy()

        if overlapping.empty:
            return None

        activity_middle = activity_start + (
            activity_end - activity_start
        ) / 2

        overlapping["path_middle"] = (
            overlapping["path_start"] +
            (overlapping["path_end"] - overlapping["path_start"]) / 2
        )

        overlapping["difference"] = (
            overlapping["path_middle"] - activity_middle
        ).abs()

        best = overlapping.sort_values("difference").iloc[0]

        return int(best["path_id"])