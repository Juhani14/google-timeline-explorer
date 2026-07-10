# timeline_data.py

class TimelineData:


    def __init__(self, day, visits, activities, paths):
        self.day = day
        self.visits = visits
        self.activities = activities
        self.paths = paths

    # ---------------------------------
    # Statistics
    # ---------------------------------

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

    # ---------------------------------
    # Activity types
    # ---------------------------------

    @property
    def activity_types(self):

        if len(self.activities) == 0:
            return []

        return sorted(
            self.activities["activity_type"].unique().tolist()
        )