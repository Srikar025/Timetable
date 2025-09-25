import io
import pandas as pd
import streamlit as st

from src.loaders import (
	load_courses_csv,
	load_faculty_csv,
	load_rooms_csv,
	load_programs_csv,
)
from src.scheduler import generate_timetable
from src.exporters import export_timetable_excel

st.set_page_config(page_title="NEP Timetable Generator", layout="wide")

st.title("NEP 2020 Timetable Generator v1.2")
st.caption("Generate conflict-free timetables for FYUP, B.Ed., M.Ed., ITEP")

with st.sidebar:
	st.header("Inputs")
	st.write("Upload CSVs using provided templates.")
	courses_file = st.file_uploader("Courses CSV", type=["csv"])
	faculty_file = st.file_uploader("Faculty CSV", type=["csv"])
	rooms_file = st.file_uploader("Rooms CSV", type=["csv"])
	programs_file = st.file_uploader("Programs/Sections CSV", type=["csv"])

	st.divider()
	st.header("Parameters")
	days = st.multiselect("Teaching Days", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"], default=["Mon", "Tue", "Wed", "Thu", "Fri"])
	periods_per_day = st.number_input("Periods per day", min_value=3, max_value=12, value=6, step=1)
	period_minutes = st.number_input("Period length (minutes)", min_value=30, max_value=120, value=60, step=5)

	st.divider()
	seed = st.number_input("Random seed (for tie-breaks)", min_value=0, max_value=999999, value=42, step=1)
	generate_btn = st.button("Generate Timetable", type="primary")

@st.cache_data(show_spinner=False)
def read_uploaded_csv(file):
	if file is None:
		return None
	return pd.read_csv(file)

col1, col2 = st.columns(2)
with col1:
	st.subheader("Preview: Courses")
	courses_df = load_courses_csv(read_uploaded_csv(courses_file)) if courses_file else None
	st.dataframe(courses_df if courses_df is not None else pd.DataFrame())

	st.subheader("Preview: Programs/Sections")
	programs_df = load_programs_csv(read_uploaded_csv(programs_file)) if programs_file else None
	st.dataframe(programs_df if programs_df is not None else pd.DataFrame())

with col2:
	st.subheader("Preview: Faculty")
	faculty_df = load_faculty_csv(read_uploaded_csv(faculty_file)) if faculty_file else None
	st.dataframe(faculty_df if faculty_df is not None else pd.DataFrame())

	st.subheader("Preview: Rooms/Labs")
	rooms_df = load_rooms_csv(read_uploaded_csv(rooms_file)) if rooms_file else None
	st.dataframe(rooms_df if rooms_df is not None else pd.DataFrame())

error_placeholder = st.empty()

if generate_btn:
	if any(x is None for x in [courses_df, faculty_df, rooms_df, programs_df]):
		error_placeholder.error("Please upload all four CSV files.")
	else:
		try:
			with st.spinner("Generating timetable..."):
				timetable, diagnostics = generate_timetable(
					courses=courses_df,
					faculty=faculty_df,
					rooms=rooms_df,
					programs=programs_df,
					days=days,
					periods_per_day=int(periods_per_day),
					period_minutes=int(period_minutes),
					seed=int(seed),
				)

			st.success("Generation complete.")

			st.subheader("Diagnostics")
			st.json(diagnostics)

			st.subheader("Timetable")
			st.dataframe(timetable)

			buf = io.BytesIO()
			export_timetable_excel(timetable, diagnostics, buf)
			st.download_button(
				label="Download Excel",
				data=buf.getvalue(),
				file_name="timetable.xlsx",
				mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
			)
		except Exception as ex:
			error_placeholder.error(f"Failed to generate timetable: {ex}")