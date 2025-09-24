import pandas as pd
from io import BytesIO


def export_timetable_excel(timetable: pd.DataFrame, diagnostics: dict, buffer: BytesIO) -> None:
	with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
		if not timetable.empty:
			timetable.to_excel(writer, sheet_name="Overview", index=False)
			group_cols = ["program", "semester", "section"]
			for keys, df_group in timetable.groupby(group_cols):
				sheet = f"{keys[0]}-S{keys[1]}-{keys[2]}"
				df_group.sort_values(["day", "period"]).to_excel(writer, sheet_name=sheet[:31], index=False)
		else:
			pd.DataFrame({"info": ["No sessions scheduled"]}).to_excel(writer, sheet_name="Overview", index=False)

		unscheduled = pd.DataFrame(diagnostics.get("unscheduled", []))
		if unscheduled is None or unscheduled.empty:
			unscheduled = pd.DataFrame({"info": ["All sessions scheduled"]})
		unscheduled.to_excel(writer, sheet_name="Diagnostics", index=False)

	buffer.seek(0)
