

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
from studio.student import student_bp


# -----------------------------
# List Students
# -----------------------------
@student_bp.route("/")
def student_list():
    conn = get_connection()
    conn.row_factory = lambda c, r: {col[0]: r[i] for i, col in enumerate(c.description)}
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY last_name, first_name")
    students = cur.fetchall()
    conn.close()
    return render_template("student_list.html", students=students)

# -----------------------------
# Add/Edit Student
# -----------------------------
@student_bp.route("/add", methods=["GET", "POST"])
@student_bp.route("/edit/<int:id>", methods=["GET", "POST"])
def student_form(id=None):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == "POST":
        first_name = request.form["first_name"]
        last_name = request.form["last_name"]
        phone = request.form["phone"]
        email_id = request.form["email_id"]

        if id:
            cur.execute("""
                UPDATE students
                SET first_name=?, last_name=?, phone=?, email_id=?
                WHERE id=?
            """, (first_name, last_name, phone, email_id, id))
            flash("✅ Student updated successfully!", "success")
        else:
            cur.execute("""
                INSERT INTO students (first_name, last_name, phone, email_id)
                VALUES (?, ?, ?, ?)
            """, (first_name, last_name, phone, email_id))
            flash("✅ Student added successfully!", "success")

        conn.commit()
        conn.close()
        return redirect(url_for("student_bp.student_list"))

    student = None
    if id:
        cur.execute("SELECT * FROM students WHERE id=?", (id,))
        student = cur.fetchone()

    conn.close()
    return render_template("student_form.html", student=student)

# -----------------------------
# Delete
# -----------------------------
@student_bp.route("/delete/<int:id>")
def student_delete(id):
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("🗑️ Student deleted!", "info")
    return redirect(url_for("student_bp.student_list"))

# -----------------------------
# Export CSV
# -----------------------------
@student_bp.route("/export/csv")
def export_csv():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    conn.close()

    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow(["id", "first_name", "last_name", "phone", "email_id"])
    cw.writerows(data)

    output = io.BytesIO()
    output.write(si.getvalue().encode("utf-8"))
    output.seek(0)
    return send_file(output, mimetype="text/csv", as_attachment=True, download_name="students.csv")

# -----------------------------
# Export JSON
# -----------------------------
@student_bp.route("/export/json")
def export_json():
    conn = get_connection()
    conn.row_factory = lambda c, r: {col[0]: r[i] for i, col in enumerate(c.description)}
    cur = conn.cursor()
    cur.execute("SELECT * FROM students")
    data = cur.fetchall()
    conn.close()
    return jsonify(data)

# -----------------------------
# Import CSV
# -----------------------------
@student_bp.route("/import/csv", methods=["POST"])
def import_csv():
    file = request.files["file"]
    if not file:
        flash("❌ No file selected", "danger")
        return redirect(url_for("student_bp.student_list"))

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    reader = csv.DictReader(stream)
    conn = get_connection()
    cur = conn.cursor()

    for row in reader:
        cur.execute("""
            INSERT INTO students (first_name, last_name, phone, email_id)
            VALUES (?, ?, ?, ?)
        """, (row["first_name"], row["last_name"], row["phone"], row["email_id"]))

    conn.commit()
    conn.close()
    flash("✅ CSV imported successfully!", "success")
    return redirect(url_for("student_bp.student_list"))
