## NEP 2020 Timetable Generator (Streamlit)

A minimal, extensible Streamlit app to generate conflict-free academic timetables aligned with NEP 2020 structures (FYUP, B.Ed., M.Ed., ITEP).

### Quickstart

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Prepare your CSVs based on the templates under `samples/`.

3. Run the app:

```bash
streamlit run app.py
```

### CSV Templates

- `courses.csv`:
  - columns: `course_id,program,semester,section,course_name,credits,course_type,theory_hours,practical_hours,faculty_id`
- `faculty.csv`:
  - columns: `faculty_id,faculty_name,max_load_hours,expertise,available_days,available_periods`
  - `available_days` like `Mon;Tue;Wed`. `available_periods` like `1;2;3;4`.
- `rooms.csv`:
  - columns: `room_id,room_name,capacity,room_type,available_days,available_periods`
  - `room_type` one of `classroom`, `lab`.
- `programs.csv`:
  - columns: `program,semester,section,student_count`

### Constraints handled

- No double-booking of faculty, rooms, or program-section groups per slot
- Faculty availability and max weekly load
- Room type and capacity suitability

Extend `src/scheduler.py` to add: teaching practice windows, internships, field work blocks, soft constraints (e.g., spread across days), and course priorities.

### Export

Excel download includes `Overview` and per-group sheets, plus a `Diagnostics` sheet listing unscheduled sessions and reasons.

### License

MIT
