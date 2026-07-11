# photo_panel.py

from pathlib import Path

import streamlit as st


class PhotoPanel:

    def __init__(self, data):
        self.data = data

    def show(self):
        st.subheader("📷 Photos")

        if len(self.data.photos) == 0:
            st.info("No photos found for this day.")
            return

        st.write(
            f"{len(self.data.photos)} photos found "
            f"for {self.data.day}."
        )

        columns = st.columns(4)

        for position, (_, photo) in enumerate(
            self.data.photos.iterrows()
        ):
            filepath = Path(photo.filepath)
            column = columns[position % 4]

            with column:
                if filepath.exists():
                    st.image(
                        str(filepath),
                        use_container_width=True
                    )

                    time_text = (
                        photo.taken_time[11:19]
                        if photo.taken_time
                        else ""
                    )

                    st.caption(
                        f"{time_text}\n{photo.filename}"
                    )

                else:
                    st.warning(
                        f"File missing:\n{photo.filename}"
                    )