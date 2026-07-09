# viewer.py

import streamlit as st

from config import APP_NAME
from database import Database
from timeline_data import TimelineData
from timeline_panel import TimelinePanel
from map_view import TimelineMap
from statistics_panel import StatisticsPanel
from kpi_panel import KPIPanel
from datetime import datetime

DB = "timeline.db"

import os

st.sidebar.write("Viewer DB path:", os.path.abspath(DB))

def main():

    st.set_page_config(
        page_title=APP_NAME,
        layout="wide"
    )

    st.title(APP_NAME)

    db = Database(DB)

    dates = db.dates()["d"].tolist()

    if len(dates) == 0:
        st.error("Database contains no timeline data.")
        db.close()
        return

    tab1, tab2 = st.tabs(["🗺 Timeline", "📊 Statistics"])

    with tab1:

        
        
        # Convert strings to real dates
        date_objects = [
            datetime.fromisoformat(d).date()
            for d in dates
        ]

        min_date = min(date_objects)
        max_date = max(date_objects)

        picked_date = st.date_input(
            "Choose a day",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

        selected_day = picked_date.isoformat()
                
        if selected_day not in dates:
            st.warning("No Timeline data for this day.")
            return 
               

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

        data = TimelineData(
            selected_day,
            visits,
            activities
        )

        left, right = st.columns([1, 2])

        with left:
            TimelinePanel(data).show()

        with right:
            TimelineMap(data).show()

    with tab2:
        KPIPanel(db).show()
        st.divider()
        StatisticsPanel(db).show()

    db.close()
    
if __name__ == "__main__":
    main()