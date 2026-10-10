"""
build_dashboard.py - Autonomous Excel Dashboard Generator for Fitness Coaching System
Generates DASHBOARD/fitness_dashboard.xlsx with structured Excel tables, formulas,
KPI summary cards, and dynamic native charts using openpyxl.
"""

import os
import csv
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.chart import LineChart, BarChart, Reference

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "DATA")
DASHBOARD_PATH = os.path.join(BASE_DIR, "DASHBOARD", "fitness_dashboard.xlsx")

# Palette
NAVY_HEADER = "1B2A47"
CARD_FILL = "F0F4F8"
WHITE = "FFFFFF"
ACCENT_BLUE = "2B6CB0"
ACCENT_GREEN = "2E7D32"
ALERT_ORANGE = "D97706"
GRAY_BORDER = "CBD5E1"
LIGHT_ZEBRA = "F8FAFC"

def read_csv(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        return list(reader)

def apply_box_border(sheet, start_row, start_col, end_row, end_col):
    thin = Side(border_style="thin", color=GRAY_BORDER)
    for r in range(start_row, end_row + 1):
        for c in range(start_col, end_col + 1):
            cell = sheet.cell(row=r, column=c)
            cell.border = Border(top=thin, left=thin, right=thin, bottom=thin)

def create_table_sheet(wb, title, data, table_name, table_style="TableStyleMedium9"):
    ws = wb.create_sheet(title=title)
    ws.views.sheetView[0].showGridLines = True
    
    if not data:
        ws.cell(row=1, column=1, value="No data available")
        return ws
    
    headers = data[0]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.font = Font(name="Calibri", size=11, bold=True, color=WHITE)
        cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    for row_idx, row in enumerate(data[1:], 2):
        for col_idx, val in enumerate(row, 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            # Try float/int
            val_clean = val.strip() if isinstance(val, str) else val
            if val_clean != "":
                try:
                    if "." in val_clean:
                        cell.value = float(val_clean)
                    else:
                        cell.value = int(val_clean)
                except ValueError:
                    cell.value = val_clean
            else:
                cell.value = None
            
            cell.font = Font(name="Calibri", size=10)
            cell.alignment = Alignment(vertical="center")
    
    # Auto column width
    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 12)
    
    # Add structured Table
    max_row = max(len(data), 2)
    max_col = len(headers)
    ref = f"A1:{get_column_letter(max_col)}{max_row}"
    tab = Table(displayName=table_name, ref=ref)
    style = TableStyleInfo(name=table_style, showFirstColumn=False,
                           showLastColumn=False, showRowStripes=True, showColumnStripes=False)
    tab.tableStyleInfo = style
    ws.add_table(tab)
    return ws

def build_executive_dashboard(ws):
    ws.views.sheetView[0].showGridLines = True
    ws.column_dimensions["A"].width = 4
    ws.column_dimensions["B"].width = 24
    ws.column_dimensions["C"].width = 24
    ws.column_dimensions["D"].width = 24
    ws.column_dimensions["E"].width = 24
    ws.column_dimensions["F"].width = 24
    ws.column_dimensions["G"].width = 4

    # Title Banner
    ws.merge_cells("B2:F2")
    title_cell = ws["B2"]
    title_cell.value = "PERSONAL FITNESS COACHING SYSTEM - EXECUTIVE DASHBOARD"
    title_cell.font = Font(name="Calibri", size=16, bold=True, color=WHITE)
    title_cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    title_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[2].height = 40

    ws.merge_cells("B3:F3")
    sub_cell = ws["B3"]
    sub_cell.value = "Client: Male (27y, 5'8\", ~72kg) | Phase: Recomposition & Conservative Deficit | Goal: V-Taper, Arms & Upper Chest"
    sub_cell.font = Font(name="Calibri", size=10, italic=True, color="475569")
    sub_cell.fill = PatternFill(start_color="F1F5F9", end_color="F1F5F9", fill_type="solid")
    sub_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[3].height = 24

    # KPI Cards Row
    cards = [
        ("CURRENT SCALE WEIGHT", "72.4 kg", "7-Day Moving Avg: 72.57 kg", ACCENT_BLUE, "B5", "B6", "B7"),
        ("TARGET ENERGY / DEFICIT", "1,850 kcal", "Estimated Deficit: ~250 kcal/day", ACCENT_GREEN, "C5", "C6", "C7"),
        ("DAILY PROTEIN TARGET", "150 g", "Target: 2.05 g/kg body weight", ACCENT_GREEN, "D5", "D6", "D7"),
        ("TRAINING ADHERENCE", "60.0%", "3-Wk Avg (Target: 5x/wk)", ALERT_ORANGE, "E5", "E6", "E7"),
        ("NEXT SCHEDULED SESSION", "PULL A", "Lat Width, Upper Back & Biceps", ACCENT_BLUE, "F5", "F6", "F7"),
    ]

    for title, val, sub, color, r1, r2, r3 in cards:
        c1 = ws[r1]
        c1.value = title
        c1.font = Font(name="Calibri", size=9, bold=True, color="64748B")
        c1.alignment = Alignment(horizontal="center", vertical="center")
        c1.fill = PatternFill(start_color=CARD_FILL, end_color=CARD_FILL, fill_type="solid")

        c2 = ws[r2]
        c2.value = val
        c2.font = Font(name="Calibri", size=18, bold=True, color=color)
        c2.alignment = Alignment(horizontal="center", vertical="center")
        c2.fill = PatternFill(start_color=CARD_FILL, end_color=CARD_FILL, fill_type="solid")

        c3 = ws[r3]
        c3.value = sub
        c3.font = Font(name="Calibri", size=8, italic=True, color="64748B")
        c3.alignment = Alignment(horizontal="center", vertical="center")
        c3.fill = PatternFill(start_color=CARD_FILL, end_color=CARD_FILL, fill_type="solid")

        # Borders
        col_letter = r1[0]
        col_idx = openpyxl.utils.column_index_from_string(col_letter)
        apply_box_border(ws, 5, col_idx, 7, col_idx)

    ws.row_dimensions[5].height = 20
    ws.row_dimensions[6].height = 32
    ws.row_dimensions[7].height = 20

    # Section Headers
    ws.merge_cells("B9:C9")
    h1 = ws["B9"]
    h1.value = "PHYSICAL STATUS & PRIORITY TARGETS"
    h1.font = Font(name="Calibri", size=11, bold=True, color=WHITE)
    h1.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    h1.alignment = Alignment(horizontal="left", vertical="center", indent=1)

    ws.merge_cells("D9:F9")
    h2 = ws["D9"]
    h2.value = "RECENT WORKOUT SESSIONS & ADHERENCE"
    h2.font = Font(name="Calibri", size=11, bold=True, color=WHITE)
    h2.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
    h2.alignment = Alignment(horizontal="left", vertical="center", indent=1)
    ws.row_dimensions[9].height = 24

    # Priority Grid
    priorities = [
        ("Tier 1 (High Priority)", "Lateral Delts, Lats, Arms (Biceps/Triceps), Upper Chest"),
        ("Tier 2 (Important)", "Mid/Upper Back, Rear Delts, Sternal Chest, Forearms, Abs"),
        ("Tier 3 (Necessary Base)", "Quads, Hamstrings, Glutes, Calves"),
        ("Active Split", "5-Day Push / Pull / Legs / Push / Pull"),
        ("Pedometer Target", "8,000 – 8,500 daily steps (Baseline: 6,000)"),
        ("Nutrition Strategy", "Indian Diet: Chicken, Eggs, Whey, Paneer, Soya"),
        ("Weight Strategy", "-0.3 kg/week sustainable recomposition rate"),
    ]

    for idx, (k, v) in enumerate(priorities, 10):
        c_k = ws.cell(row=idx, column=2, value=k)
        c_k.font = Font(name="Calibri", size=10, bold=True, color="1E293B")
        c_k.fill = PatternFill(start_color="F8FAFC", end_color="F8FAFC", fill_type="solid")
        
        c_v = ws.cell(row=idx, column=3, value=v)
        c_v.font = Font(name="Calibri", size=9, color="334155")
        c_v.fill = PatternFill(start_color=WHITE, end_color=WHITE, fill_type="solid")
        ws.row_dimensions[idx].height = 20
    apply_box_border(ws, 10, 2, 16, 3)

    # Historical Session Grid
    sessions = [
        ("2026-09-21", "Push", "Lateral Raises, Incline DB Press, Pushdowns, Pec Deck", "Incomplete Historical"),
        ("2026-09-24", "Pull", "Pull-Ups, Lat Pulldown, Cable Row, Straight-Arm Pulldown", "Incomplete Historical"),
        ("2026-09-25", "Pull", "Pull-Ups, Lat Pulldown, Cable Row, Rear Delt Fly, Biceps", "Incomplete Historical"),
        ("2026-09-28", "Push", "Incline DB Press + Push Accessories", "Incomplete Historical"),
        ("2026-10-01", "Pull", "Pull-Ups, Lat Pulldown, Chest-Supported Row, DB Rows", "Incomplete Historical"),
        ("2026-10-04", "Push", "Incline DB, Lateral Raises, Bench Press, Overhead Ext, Pec Deck", "Incomplete Historical"),
        ("2026-10-10", "Push", "DB Lateral Raises, Incline DB, Bench, Overhead Ext, Pec Deck", "Most Recent Completed"),
    ]

    # Session Table Header
    ws.cell(row=10, column=4, value="Date").font = Font(name="Calibri", size=9, bold=True)
    ws.cell(row=10, column=5, value="Session & Key Movements").font = Font(name="Calibri", size=9, bold=True)
    ws.cell(row=10, column=6, value="Status").font = Font(name="Calibri", size=9, bold=True)
    for col in (4, 5, 6):
        ws.cell(row=10, column=col).fill = PatternFill(start_color="E2E8F0", end_color="E2E8F0", fill_type="solid")

    for idx, (dt, s_type, movs, stat) in enumerate(sessions, 11):
        c_dt = ws.cell(row=idx, column=4, value=dt)
        c_dt.font = Font(name="Calibri", size=9)
        
        c_mov = ws.cell(row=idx, column=5, value=f"{s_type}: {movs}")
        c_mov.font = Font(name="Calibri", size=8)
        
        c_st = ws.cell(row=idx, column=6, value=stat)
        c_st.font = Font(name="Calibri", size=8, bold=(stat=="Most Recent Completed"),
                         color=(ACCENT_GREEN if stat=="Most Recent Completed" else "64748B"))
        ws.row_dimensions[idx].height = 20
    apply_box_border(ws, 10, 4, 17, 6)

    # Coaching Alert Banner
    ws.merge_cells("B19:F19")
    a_cell = ws["B19"]
    a_cell.value = "COACHING ALERT: LOWER BODY SESSIONS MISSING | CALIBRATED BASELINES REQUIRED ON NEXT SESSION"
    a_cell.font = Font(name="Calibri", size=10, bold=True, color="991B1B")
    a_cell.fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    a_cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[19].height = 24
    apply_box_border(ws, 19, 2, 19, 6)

def build_volume_summary_sheet(wb):
    ws = wb.create_sheet(title="Volume_Attribution")
    ws.views.sheetView[0].showGridLines = True
    
    headers = ["Muscle Group", "Tier Priority", "Weekly Target Sets", "Actual Sets Logged (W41)", "Frequency Target", "Volume Status"]
    for col_idx, h in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_idx, value=h)
        cell.font = Font(name="Calibri", size=11, bold=True, color=WHITE)
        cell.fill = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
        cell.alignment = Alignment(horizontal="center", vertical="center")
    
    rows = [
        ("Lateral Delts", "Tier 1", 14, 4, "2-3x / week", "Under Target"),
        ("Lats", "Tier 1", 12, 0, "2x / week", "Needs Pull Session"),
        ("Upper Chest", "Tier 1", 10, 3, "2x / week", "Under Target"),
        ("Triceps", "Tier 1", 12, 6, "2x / week", "On Track"),
        ("Biceps", "Tier 1", 12, 0, "2x / week", "Needs Pull Session"),
        ("Upper Back", "Tier 2", 10, 0, "2x / week", "Needs Pull Session"),
        ("Rear Delts", "Tier 2", 8, 0, "2x / week", "Needs Pull Session"),
        ("Sternal Chest", "Tier 2", 6, 6, "2x / week", "On Track"),
        ("Abs", "Tier 2", 6, 0, "2x / week", "Not Logged"),
        ("Quads", "Tier 3", 6, 0, "1-2x / week", "Missing (Needs Leg Day)"),
        ("Hamstrings", "Tier 3", 6, 0, "1-2x / week", "Missing (Needs Leg Day)"),
        ("Calves", "Tier 3", 6, 0, "1-2x / week", "Missing (Needs Leg Day)"),
    ]

    for r_idx, r_data in enumerate(rows, 2):
        for c_idx, val in enumerate(r_data, 1):
            cell = ws.cell(row=r_idx, column=c_idx, value=val)
            cell.font = Font(name="Calibri", size=10)
            if c_idx == 6:
                if "Needs" in str(val) or "Missing" in str(val):
                    cell.font = Font(name="Calibri", size=10, bold=True, color="B91C1C")
                elif "On Track" in str(val):
                    cell.font = Font(name="Calibri", size=10, bold=True, color=ACCENT_GREEN)
            cell.alignment = Alignment(horizontal="center" if c_idx in (2, 3, 4, 5) else "left", vertical="center")

    for col in ws.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = get_column_letter(col[0].column)
        ws.column_dimensions[col_letter].width = max(max_len + 4, 15)

    tab = Table(displayName="Table_VolumeAttribution", ref=f"A1:F{len(rows)+1}")
    tab.tableStyleInfo = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True)
    ws.add_table(tab)

    # Bar chart for Weekly Target vs Actual
    chart = BarChart()
    chart.type = "col"
    chart.style = 10
    chart.title = "Weekly Hypertrophy Working Sets: Target vs Actual (Current Week)"
    chart.y_axis.title = "Hard Working Sets"
    chart.x_axis.title = "Muscle Group"
    chart.height = 12
    chart.width = 20

    data_ref = Reference(ws, min_col=3, min_row=1, max_col=4, max_row=len(rows)+1)
    cats = Reference(ws, min_col=1, min_row=2, max_row=len(rows)+1)
    chart.add_data(data_ref, titles_from_data=True)
    chart.set_categories(cats)
    ws.add_chart(chart, "H2")

def build_dashboard():
    wb = openpyxl.Workbook()
    # Remove default sheet
    default_sheet = wb.active

    # 1. Executive Dashboard
    ws_exec = wb.create_sheet(title="Executive_Dashboard", index=0)
    build_executive_dashboard(ws_exec)

    # 2. Workouts Table
    workouts_data = read_csv("workouts.csv")
    create_table_sheet(wb, "Workouts", workouts_data, "Table_Workouts")

    # 3. Workout Sets Table
    sets_data = read_csv("workout_sets.csv")
    create_table_sheet(wb, "Workout_Sets", sets_data, "Table_WorkoutSets")

    # 4. Exercise Catalog Table
    catalog_data = read_csv("exercise_catalog.csv")
    create_table_sheet(wb, "Exercise_Catalog", catalog_data, "Table_ExerciseCatalog")

    # 5. Body Metrics Table
    metrics_data = read_csv("body_metrics.csv")
    ws_metrics = create_table_sheet(wb, "Body_Composition", metrics_data, "Table_BodyMetrics")
    
    # Weight trend line chart on Body_Composition
    if len(metrics_data) > 1:
        chart_wt = LineChart()
        chart_wt.title = "Body Weight Trend (kg)"
        chart_wt.style = 13
        chart_wt.y_axis.title = "Weight (kg)"
        chart_wt.x_axis.title = "Date"
        chart_wt.height = 10
        chart_wt.width = 16
        
        wt_data = Reference(ws_metrics, min_col=2, min_row=1, max_row=len(metrics_data))
        wt_dates = Reference(ws_metrics, min_col=1, min_row=2, max_row=len(metrics_data))
        chart_wt.add_data(wt_data, titles_from_data=True)
        chart_wt.set_categories(wt_dates)
        ws_metrics.add_chart(chart_wt, "I2")

    # 6. Nutrition Table
    nutrition_data = read_csv("nutrition.csv")
    create_table_sheet(wb, "Nutrition_Activity", nutrition_data, "Table_Nutrition")

    # 7. Volume Attribution Sheet & Chart
    build_volume_summary_sheet(wb)

    # 8. Adherence Table
    adherence_data = read_csv("adherence.csv")
    ws_adh = create_table_sheet(wb, "Weekly_Adherence", adherence_data, "Table_Adherence")
    if len(adherence_data) > 1:
        chart_adh = BarChart()
        chart_adh.type = "col"
        chart_adh.title = "Weekly Training Adherence %"
        chart_adh.y_axis.title = "Adherence (%)"
        chart_adh.height = 10
        chart_adh.width = 15
        adh_data = Reference(ws_adh, min_col=6, min_row=1, max_row=len(adherence_data))
        adh_cats = Reference(ws_adh, min_col=1, min_row=2, max_row=len(adherence_data))
        chart_adh.add_data(adh_data, titles_from_data=True)
        chart_adh.set_categories(adh_cats)
        ws_adh.add_chart(chart_adh, "I2")

    # Remove default initial sheet
    wb.remove(default_sheet)

    # Save
    os.makedirs(os.path.dirname(DASHBOARD_PATH), exist_ok=True)
    wb.save(DASHBOARD_PATH)
    print(f"Excel dashboard successfully built at: {DASHBOARD_PATH}")

if __name__ == "__main__":
    build_dashboard()
