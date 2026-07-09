# viewer.py

import streamlit as st

from config import APP_NAME
from database import Database
from timeline_data import TimelineData
from timeline_panel import TimelinePanel
from map_view import TimelineMap
from statistics_panel import StatisticsPanel

DB = "timeline.db"

import os
st.sidebar.write("Current folder:", os.getcwd())
st.sidebar.write("DB path:", os.path.abspath(DB))

def main():

    st.set_page_config(
        page_title=APP_NAME,
        layout="wide"
    )

    st.title(APP_NAME)

    # -----------------------------------------
    # Open database
    # -----------------------------------------

    db = Database(DB)

    dates = db.dates()["d"].tolist()

    if len(dates) == 0:

        st.error("Database contains no timeline data.")

        db.close()
        return

    # -----------------------------------------
    # Select day
    # -----------------------------------------

    selected_day = st.selectbox(
        "Choose a day",
        dates
    )

    # -----------------------------------------
    # Load one day
    # -----------------------------------------

    visits = db.visits(selected_day)

    activities = db.activities(selected_day)
    
    visits["place_name"] = visits.apply(
        lambda v: db.get_place_name(
            v.latitude,
            v.longitude,
            v.place_id if "place_id" in visits.columns else None
        ) or "Visit",
        axis=1
    )
    
    db.close()

    # -----------------------------------------
    # Create TimelineData object
    # -----------------------------------------

    data = TimelineData(
        selected_day,
        visits,
        activities
    )

    # -----------------------------------------
    # Layout
    # -----------------------------------------

    left, right = st.columns([1, 2])

    with left:

        panel = TimelinePanel(data)
        panel.show()

    with right:

        m = TimelineMap(data)
        m.show()


if __name__ == "__main__":
    main()