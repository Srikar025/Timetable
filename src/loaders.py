import pandas as pd
from typing import Optional

REQUIRED_COURSE_COLS = [
	"course_id", "program", "semester", "section", "course_name", "credits", "course_type", "theory_hours", "practical_hours", "faculty_id"
]

REQUIRED_FACULTY_COLS = [
	"faculty_id", "faculty_name", "max_load_hours", "expertise", "available_days", "available_periods"
]

REQUIRED_ROOMS_COLS = [
	"room_id", "room_name", "capacity", "room_type", "available_days", "available_periods"
]

REQUIRED_PROGRAMS_COLS = [
	"program", "semester", "section", "student_count"
]

def _coerce_list(series: pd.Series) -> pd.Series:
	return series.fillna("").astype(str).apply(lambda s: [x.strip() for x in s.split(";") if x.strip()])


def _validate(df: pd.DataFrame, required_cols: list) -> pd.DataFrame:
	missing = [c for c in required_cols if c not in df.columns]
	if missing:
		raise ValueError(f"Missing columns: {missing}")
	return df[required_cols].copy()


def load_courses_csv(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
	if df is None:
		return None
	df = _validate(df, REQUIRED_COURSE_COLS)
	df["credits"] = pd.to_numeric(df["credits"], errors="coerce").fillna(0).astype(int)
	df["theory_hours"] = pd.to_numeric(df["theory_hours"], errors="coerce").fillna(0).astype(int)
	df["practical_hours"] = pd.to_numeric(df["practical_hours"], errors="coerce").fillna(0).astype(int)
	return df


def load_faculty_csv(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
	if df is None:
		return None
	df = _validate(df, REQUIRED_FACULTY_COLS)
	df["available_days"] = _coerce_list(df["available_days"])  # e.g., Mon;Tue;Wed
	df["available_periods"] = _coerce_list(df["available_periods"])  # e.g., 1;2;3;4
	df["max_load_hours"] = pd.to_numeric(df["max_load_hours"], errors="coerce").fillna(0).astype(int)
	return df


def load_rooms_csv(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
	if df is None:
		return None
	df = _validate(df, REQUIRED_ROOMS_COLS)
	df["available_days"] = _coerce_list(df["available_days"])  # e.g., Mon;Tue;Wed
	df["available_periods"] = _coerce_list(df["available_periods"])  # e.g., 1;2;3;4
	df["capacity"] = pd.to_numeric(df["capacity"], errors="coerce").fillna(0).astype(int)
	return df


def load_programs_csv(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
	if df is None:
		return None
	df = _validate(df, REQUIRED_PROGRAMS_COLS)
	df["student_count"] = pd.to_numeric(df["student_count"], errors="coerce").fillna(0).astype(int)
	return df
