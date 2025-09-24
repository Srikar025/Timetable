import random
from typing import Dict, List, Tuple
import pandas as pd

TimeSlot = Tuple[str, int]


def _build_timeslots(days: List[str], periods_per_day: int) -> List[TimeSlot]:
	return [(d, p) for d in days for p in range(1, periods_per_day + 1)]


def _faculty_available(faculty_row: pd.Series, day: str, period: int) -> bool:
	return (day in set(faculty_row["available_days"])) and (str(period) in set(faculty_row["available_periods"]))


def _room_available(room_row: pd.Series, day: str, period: int) -> bool:
	return (day in set(room_row["available_days"])) and (str(period) in set(room_row["available_periods"]))


def _choose_room(rooms: pd.DataFrame, needed_type: str, needed_capacity: int, day: str, period: int, occupied_rooms: Dict[TimeSlot, set]) -> Tuple[bool, str]:
	candidate_rooms = rooms[(rooms["room_type"].str.lower() == needed_type.lower()) & (rooms["capacity"] >= needed_capacity)]
	for _, r in candidate_rooms.iterrows():
		if not _room_available(r, day, period):
			continue
		if (day, period) in occupied_rooms and r["room_id"] in occupied_rooms[(day, period)]:
			continue
		return True, r["room_id"]
	return False, ""


def generate_timetable(
	courses: pd.DataFrame,
	faculty: pd.DataFrame,
	rooms: pd.DataFrame,
	programs: pd.DataFrame,
	days: List[str],
	periods_per_day: int,
	period_minutes: int,
	seed: int = 42,
):
	random.seed(seed)
	courses = courses.copy()
	faculty = faculty.copy()
	rooms = rooms.copy()
	programs = programs.copy()

	timeslots = _build_timeslots(days, periods_per_day)

	sessions: List[Dict] = []
	for _, c in courses.iterrows():
		program = c["program"]
		semester = c["semester"]
		section = c["section"]
		faculty_id = c["faculty_id"]

		for _i in range(int(c["theory_hours"])):
			sessions.append({
				"course_id": c["course_id"],
				"course_name": c["course_name"],
				"program": program,
				"semester": semester,
				"section": section,
				"faculty_id": faculty_id,
				"session_type": "theory",
				"room_type": "classroom",
				"student_count": int(programs[(programs["program"] == program) & (programs["semester"] == semester) & (programs["section"] == section)]["student_count"].iloc[0]) if not programs.empty else 0,
			})
		for _i in range(int(c["practical_hours"])):
			sessions.append({
				"course_id": c["course_id"],
				"course_name": c["course_name"],
				"program": program,
				"semester": semester,
				"section": section,
				"faculty_id": faculty_id,
				"session_type": "practical",
				"room_type": "lab",
				"student_count": int(programs[(programs["program"] == program) & (programs["semester"] == semester) & (programs["section"] == section)]["student_count"].iloc[0]) if not programs.empty else 0,
			})

	sessions.sort(key=lambda s: (s["room_type"] == "classroom", -s["student_count"]))

	occupied_faculty: Dict[TimeSlot, set] = {}
	occupied_groups: Dict[TimeSlot, set] = {}
	occupied_rooms: Dict[TimeSlot, set] = {}
	faculty_load: Dict[str, int] = {f["faculty_id"]: 0 for _, f in faculty.iterrows()}

	scheduled_rows: List[Dict] = []
	diagnostics: Dict = {"unscheduled": []}

	for s in sessions:
		fid = s["faculty_id"]
		fac_row = faculty[faculty["faculty_id"] == fid]
		if fac_row.empty:
			diagnostics["unscheduled"].append({**s, "reason": "faculty_not_found"})
			continue
		fac_row = fac_row.iloc[0]

		if faculty_load.get(fid, 0) >= int(fac_row["max_load_hours"]):
			diagnostics["unscheduled"].append({**s, "reason": "faculty_load_exceeded"})
			continue

		placed = False
		for day, period in timeslots:
			if not _faculty_available(fac_row, day, period):
				continue
			group_key = f"{s['program']}-{s['semester']}-{s['section']}"
			if (day, period) in occupied_faculty and fid in occupied_faculty[(day, period)]:
				continue
			if (day, period) in occupied_groups and group_key in occupied_groups[(day, period)]:
				continue

			ok, room_id = _choose_room(rooms, s["room_type"], s["student_count"], day, period, occupied_rooms)
			if not ok:
				continue

			scheduled_rows.append({
				"day": day,
				"period": period,
				"program": s["program"],
				"semester": s["semester"],
				"section": s["section"],
				"course_id": s["course_id"],
				"course_name": s["course_name"],
				"session_type": s["session_type"],
				"faculty_id": fid,
				"room_id": room_id,
			})

			occupied_faculty.setdefault((day, period), set()).add(fid)
			occupied_groups.setdefault((day, period), set()).add(group_key)
			occupied_rooms.setdefault((day, period), set()).add(room_id)
			faculty_load[fid] = faculty_load.get(fid, 0) + 1
			placed = True
			break

		if not placed:
			diagnostics["unscheduled"].append({**s, "reason": "no_slot_found"})

	timetable = pd.DataFrame(scheduled_rows)
	if not timetable.empty:
		timetable.sort_values(by=["day", "period", "program", "semester", "section"], inplace=True)

	return timetable, diagnostics
