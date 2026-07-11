# viewer.py

import os

import streamlit as st

from calendar_panel import CalendarPanel
from config import APP_NAME
from database import Database
from kpi_panel import KPIPanel
from map_view import TimelineMap
from place_resolver import PlaceResolver
from statistics_panel import StatisticsPanel
from timeline_data import TimelineData
from timeline_panel import TimelinePanel
from photo_panel import PhotoPanel


DB = "timeline.db"


def main():

    # This must be the first Streamlit command.
    st.set_page_config(
        page_title=APP_NAME,
        layout="wide"
    )

    st.title(APP_NAME)

    # Optional development information.
    with st.sidebar:
        st.caption("Database")
        st.write(os.path.abspath(DB))

    # --------------------------------------------------
    # Open database
    # --------------------------------------------------

    db = Database(DB)

    dates_df = db.dates()
    dates = dates_df["d"].tolist()

    if len(dates) == 0:
        st.error("Database contains no Timeline data.")
        db.close()
        return

    # --------------------------------------------------
    # Main application tabs
    # --------------------------------------------------

    timeline_tab, statistics_tab = st.tabs([
        "🗺 Timeline",
        "📊 Statistics"
    ])

    # ==================================================
    # TIMELINE TAB
    # ==================================================

    with timeline_tab:

        # ----------------------------------------------
        # Place-name resolver
        # ----------------------------------------------

        with st.expander("📍 Place names"):

            st.write(
                "Resolve unknown coordinates into place names "
                "and save them in the local cache."
            )

            resolve_limit = st.number_input(
                "Number of unknown places to resolve",
                min_value=1,
                max_value=100,
                value=10,
                step=1
            )

            if st.button(
                "Resolve place names",
                key="resolve_place_names"
            ):

                unknown = db.unknown_places(
                    int(resolve_limit)
                )

                if len(unknown) == 0:
                    st.success(
                        "All available places are already cached."
                    )

                else:
                    resolver = PlaceResolver(db)

                    progress = st.progress(0)
                    status = st.empty()

                    resolved_count = 0

                    for position, (_, place) in enumerate(
                        unknown.iterrows(),
                        start=1
                    ):
                        status.write(
                            f"Resolving place "
                            f"{position} of {len(unknown)}..."
                        )

                        name = resolver.resolve(
                            place.latitude,
                            place.longitude,
                            place.place_id
                        )

                        if name:
                            resolved_count += 1

                        progress.progress(
                            position / len(unknown)
                        )

                    status.empty()

                    st.success(
                        f"Resolved {resolved_count} of "
                        f"{len(unknown)} places."
                    )

                    st.rerun()

        # ----------------------------------------------
        # Selected day
        # ----------------------------------------------

        if "selected_day" not in st.session_state:
            # dates are sorted newest first
            st.session_state.selected_day = dates[0]

        # Ensure selected day still exists.
        if st.session_state.selected_day not in dates:
            st.session_state.selected_day = dates[0]

        selected_day = CalendarPanel(dates).show(
            st.session_state.selected_day
        )

        st.session_state.selected_day = selected_day

        # ----------------------------------------------
        # Clear selected route when day changes
        # ----------------------------------------------

        if "selected_path_id" not in st.session_state:
            st.session_state.selected_path_id = None

        if "previous_selected_day" not in st.session_state:
            st.session_state.previous_selected_day = selected_day

        if (
            st.session_state.previous_selected_day
            != selected_day
        ):
            st.session_state.selected_path_id = None
            st.session_state.previous_selected_day = selected_day
            
            
        #        add button

        with st.expander("📍 Place names for selected day"):

            if st.button(
                f"Resolve places for {selected_day}",
                key="resolve_selected_day"
            ):

                unknown = db.unknown_places_for_day(selected_day)

                if len(unknown) == 0:
                    st.success(
                        "All visits on this day already have cached names."
                    )

                else:
                    resolver = PlaceResolver(db)
                    progress = st.progress(0)

                    resolved_count = 0

                    for position, (_, place) in enumerate(
                        unknown.iterrows(),
                        start=1
                    ):
                        name = resolver.resolve(
                            place.latitude,
                            place.longitude,
                            place.place_id
                        )

                        if name:
                            resolved_count += 1

                        progress.progress(
                            position / len(unknown)
                        )

                    st.success(
                        f"Resolved {resolved_count} of "
                        f"{len(unknown)} places for this day."
                    )

                    st.rerun()
                

        # ----------------------------------------------
        # Load the selected day's data
        # ----------------------------------------------

        visits = db.visits(selected_day)
        activities = db.activities(selected_day)
        paths = db.paths(selected_day)
        photos = db.photos(selected_day)

        # ----------------------------------------------
        # Add cached place names
        # ----------------------------------------------

        if len(visits):

            visits["place_name"] = visits.apply(
                lambda visit: db.get_place_name(
                    visit.latitude,
                    visit.longitude,
                    (
                        visit.place_id
                        if "place_id" in visits.columns
                        else None
                    )
                ) or "Visit",
                axis=1
            )

        else:
            visits["place_name"] = []

        # ----------------------------------------------
        # Create TimelineData
        # ----------------------------------------------

        data = TimelineData(
            selected_day,
            visits,
            activities,
            paths,
            photos,
            st.session_state.selected_path_id
        )

        st.caption(f"Selected day: {selected_day}")

        # ----------------------------------------------
        # Timeline and map layout
        # ----------------------------------------------

        left, right = st.columns(
            [1, 2],
            gap="large"
        )

        with left:
            TimelinePanel(data).show()

        with right:
            TimelineMap(data).show()
            
        st.divider()

        with st.expander(
            f"📷 Photos for {selected_day} ({len(photos)})",
            expanded=False
        ):
            PhotoPanel(data).show()            

    # ==================================================
    # STATISTICS TAB
    # ==================================================

    with statistics_tab:

        KPIPanel(db).show()

        st.divider()

        StatisticsPanel(db).show()

    # --------------------------------------------------
    # Close database
    # --------------------------------------------------

    db.close()


if __name__ == "__main__":
    main()
