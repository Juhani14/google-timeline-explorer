# calendar_panel.py

import calendar
from datetime import date

import streamlit as st


class CalendarPanel:

    def __init__(self, available_days):
        self.available_days = set(available_days)

    def show(self, selected_day):
        selected = date.fromisoformat(selected_day)

        if "calendar_year" not in st.session_state:
            st.session_state.calendar_year = selected.year

        if "calendar_month" not in st.session_state:
            st.session_state.calendar_month = selected.month

        year = st.session_state.calendar_year
        month = st.session_state.calendar_month

        c1, c2, c3 = st.columns([1, 3, 1])

        with c1:
            if st.button("⬅ Previous month"):
                month -= 1
                if month == 0:
                    month = 12
                    year -= 1
                st.session_state.calendar_year = year
                st.session_state.calendar_month = month

        with c2:
            years = sorted({
                int(d[:4]) for d in self.available_days
            })

            selected_year = st.selectbox(
                "Year",
                years,
                index=years.index(year) if year in years else len(years) - 1,
                key="calendar_year_select"
            )

            st.session_state.calendar_year = selected_year
            year = selected_year

        st.subheader(f"📅 {calendar.month_name[month]} {year}")

        with c3:
            if st.button("Next month ➡"):
                month += 1
                if month == 13:
                    month = 1
                    year += 1
                st.session_state.calendar_year = year
                st.session_state.calendar_month = month

        weeks = calendar.monthcalendar(year, month)

        cols = st.columns(7)
        for col, name in zip(cols, ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]):
            col.write(f"**{name}**")

        new_day = selected_day

        for week in weeks:
            cols = st.columns(7)

            for col, day in zip(cols, week):
                if day == 0:
                    col.write("")
                    continue

                d = date(year, month, day).isoformat()
                has_data = d in self.available_days

                if d == selected_day:
                    label = f"🔵 {day}"
                elif has_data:
                    label = f"🟢 {day}"
                else:
                    label = f"⚪ {day}"

                if col.button(label, key=f"cal_{d}", disabled=not has_data):
                    new_day = d
                    st.session_state.selected_day = d

        return new_day