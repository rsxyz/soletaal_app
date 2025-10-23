


from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
import sqlite3
from contextlib import closing
from io import StringIO, BytesIO
import os
import io
from werkzeug.utils import secure_filename
import sqlite3
import csv
from datetime import datetime

from studio.db.db import get_connection
from studio.attendance import attendance_bp

@attendance_bp.route("/attendance", methods=["GET", "POST"])
def attendance_dashboard():
    conn = get_connection()
    cur = conn.cursor()

    # Fetch all classes and unique dates from attendance
    cur.execute("SELECT id, name FROM class_names ORDER BY name")
    classes = cur.fetchall()

    cur.execute("SELECT DISTINCT attendance_date FROM attendance ORDER BY attendance_date DESC")
    dates = [row[0] for row in cur.fetchall()]

    conn.close()
    return render_template("attendance_list.html", classes=classes, dates=dates)


@attendance_bp.route("/attendance/manage", methods=["GET", "POST"])
def manage_attendance():
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        class_id = request.form.get("class_id")
        attendance_date = request.form.get("attendance_date")
        student_ids = request.form.getlist("students")

        # Clear existing attendance for that date & class
        cur.execute("""
            DELETE FROM attendance WHERE class_id = ? AND attendance_date = ?
        """, (class_id, attendance_date))

        # Insert new attendance records
        for sid in student_ids:
            cur.execute("""
                INSERT INTO attendance (student_id, class_id, attendance_date)
                VALUES (?, ?, ?)
            """, (sid, class_id, attendance_date))

        conn.commit()
        conn.close()
        flash("Attendance updated successfully.", "success")
        return redirect(url_for("attendance_bp.attendance_dashboard"))

    else:
        class_id = request.args.get("class_id")
        attendance_date = request.args.get("attendance_date")

        # Get class and student data
        cur.execute("SELECT id, name FROM class_names ORDER BY name")
        classes = cur.fetchall()

        cur.execute("SELECT id, first_name || ' ' || last_name AS name FROM students ORDER BY name")
        students = cur.fetchall()

        # Get students already marked present
        cur.execute("""
            SELECT student_id FROM attendance
            WHERE class_id = ? AND attendance_date = ?
        """, (class_id, attendance_date))
        attended = [str(row[0]) for row in cur.fetchall()]

        conn.close()

        return render_template(
            "attendance_manage.html",
            classes=classes,
            students=students,
            attended=attended,
            selected_class=class_id,
            selected_date=attendance_date
        )


@attendance_bp.route("/attendance/delete", methods=["POST"])
def delete_attendance():
    conn = get_connection()
    cur = conn.cursor()
    class_id = request.form["class_id"]
    attendance_date = request.form["attendance_date"]

    cur.execute("DELETE FROM attendance WHERE class_id = ? AND attendance_date = ?", (class_id, attendance_date))
    conn.commit()
    conn.close()
    flash("Attendance deleted successfully.", "info")
    return redirect(url_for("attendance_bp.attendance_dashboard"))