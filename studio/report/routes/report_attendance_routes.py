from flask import Blueprint, render_template, request
import sqlite3
from datetime import datetime

from studio.db.db import get_connection
from studio.report import report_bp

@report_bp.route("/report/attendance", methods=["GET", "POST"])
def attendance_report():
    conn = get_connection()
    cur = conn.cursor()

    # Distinct years/months from attendance
    cur.execute("SELECT DISTINCT SUBSTR(attendance_date,1,4) AS year FROM attendance ORDER BY year DESC")
    years = [r["year"] for r in cur.fetchall()]
    cur.execute("SELECT DISTINCT SUBSTR(attendance_date,6,2) AS month FROM attendance ORDER BY month")
    months = [r["month"] for r in cur.fetchall()]

    selected_year = request.args.get("year") or datetime.now().strftime("%Y")
    selected_month = request.args.get("month") or datetime.now().strftime("%m")

    # Distinct (date, class_name)
    cur.execute("""
        SELECT a.attendance_date, c.name AS class_name
        FROM attendance a
        JOIN class_names c ON a.class_id = c.id
        WHERE a.attendance_date LIKE ? || '-%'
        GROUP BY a.attendance_date, c.name
        ORDER BY a.attendance_date, c.name
    """, (f"{selected_year}-{selected_month}",))
    date_class_pairs = cur.fetchall()

    # Students
    cur.execute("SELECT id, first_name || ' ' || last_name AS name FROM students ORDER BY name")
    students = cur.fetchall()

    # Attendance mapping (student_id → {(date, class_name)})
    cur.execute("""
        SELECT a.student_id, a.attendance_date, c.name AS class_name
        FROM attendance a
        JOIN class_names c ON a.class_id = c.id
        WHERE a.attendance_date LIKE ? || '-%'
    """, (f"{selected_year}-{selected_month}",))
    attendance_records = cur.fetchall()

    attendance_map = {}
    for rec in attendance_records:
        attendance_map.setdefault(rec["student_id"], set()).add((rec["attendance_date"], rec["class_name"]))

    conn.close()

    return render_template(
        "report_attendance.html",
        years=years,
        months=months,
        selected_year=selected_year,
        selected_month=selected_month,
        students=students,
        date_class_pairs=date_class_pairs,
        attendance_map=attendance_map
    )
