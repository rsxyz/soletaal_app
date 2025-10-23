from flask import Blueprint, render_template, jsonify, Response
import sqlite3
import csv
import io
from studio.db.db import get_connection
from studio.report import report_bp


def get_credit_data():
    conn = get_connection()
    cur = conn.cursor()

    # --- Sum payments and credits purchased ---
    cur.execute("""
        SELECT s.id,
               s.first_name || ' ' || s.last_name AS student_name,
               IFNULL(SUM(p.amount), 0) AS amount_paid,
               IFNULL(SUM(cp.credits), 0) AS credits_paid
        FROM students s
        LEFT JOIN payments p ON s.id = p.student_id
        LEFT JOIN class_passes cp ON p.class_pass_id = cp.id
        GROUP BY s.id
    """)
    payments_data = cur.fetchall()

    # --- Attendance count (credits used) ---
    cur.execute("""
        SELECT student_id, COUNT(*) AS credits_used
        FROM attendance
        GROUP BY student_id
    """)
    attendance_data = {row[0]: row[1] for row in cur.fetchall()}
    conn.close()

    # --- Merge data ---
    data = []
    for student_id, student_name, amount_paid, credits_paid in payments_data:
        credits_used = attendance_data.get(student_id, 0)
        balance = credits_paid - credits_used
        data.append({
            "student_name": student_name,
            "amount_paid": amount_paid,
            "credits_paid": credits_paid,
            "credits_used": credits_used,
            "balance": balance
        })
    return data


@report_bp.route("/report/credits")
def report_credits():
    data = get_credit_data()
    return render_template("report_credits.html", data=data)


@report_bp.route("/report/credits/export/csv")
def export_credits_csv():
    data = get_credit_data()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Student", "Amount Paid", "Credits Purchased", "Credits Used", "Credit Balance"])
    for row in data:
        writer.writerow([
            row["student_name"],
            row["amount_paid"],
            row["credits_paid"],
            row["credits_used"],
            row["balance"]
        ])

    output.seek(0)
    return Response(output, mimetype="text/csv",
                    headers={"Content-Disposition": "attachment; filename=credit_balance_report.csv"})


@report_bp.route("/report/credits/export/json")
def export_credits_json():
    data = get_credit_data()
    return jsonify(data)
