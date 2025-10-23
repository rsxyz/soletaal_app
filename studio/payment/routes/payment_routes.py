from flask import render_template, request, redirect, url_for, flash, jsonify, send_file
from studio.db.db import get_connection
from studio.payment import payment_bp
import csv, io, json
from datetime import datetime


# -----------------------------
# LIST PAYMENTS
# -----------------------------
@payment_bp.route('/payments')
def payment_list():
    conn = get_connection()
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    cur = conn.cursor()

    payments = cur.execute("""
        SELECT p.id, s.first_name || ' ' || s.last_name AS student_name,
               p.payment_date, p.amount,
               pm.name AS payment_method,
               cp.name AS class_pass
        FROM payments p
        JOIN students s ON p.student_id = s.id
        JOIN payment_methods pm ON p.payment_method_id = pm.id
        JOIN class_passes cp ON p.class_pass_id = cp.id
        ORDER BY p.payment_date DESC
    """).fetchall()

    conn.close()
    return render_template('payment_list.html', payments=payments)


# -----------------------------
# ADD / EDIT PAYMENT
# -----------------------------
@payment_bp.route('/payment_form', methods=['GET', 'POST'])
@payment_bp.route('/payment_form/<int:payment_id>', methods=['GET', 'POST'])
def payment_form(payment_id=None):
    conn = get_connection()
    cur = conn.cursor()

    students = cur.execute("SELECT id, first_name || ' ' || last_name AS name FROM students ORDER BY name").fetchall()
    methods = cur.execute("SELECT id, name FROM payment_methods ORDER BY name").fetchall()
    passes = cur.execute("SELECT id, name FROM class_passes ORDER BY id").fetchall()

    payment = None
    if payment_id:
        payment = cur.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()

    if request.method == 'POST':
        data = (
            request.form['student_id'],
            request.form['payment_date'],
            request.form['amount'],
            request.form['payment_method_id'],
            request.form['class_pass_id']
        )

        if payment_id:
            cur.execute("""
                UPDATE payments
                SET student_id=?, payment_date=?, amount=?, payment_method_id=?, class_pass_id=?
                WHERE id=?
            """, data + (payment_id,))
            flash("Payment updated successfully", "success")
        else:
            cur.execute("""
                INSERT INTO payments (student_id, payment_date, amount, payment_method_id, class_pass_id)
                VALUES (?, ?, ?, ?, ?)
            """, data)
            flash("Payment added successfully", "success")

        conn.commit()
        conn.close()
        return redirect(url_for('payment_bp.payment_list'))

    conn.close()
    return render_template('payment_form.html', students=students, methods=methods, passes=passes, payment=payment)


# -----------------------------
# DELETE PAYMENT
# -----------------------------
@payment_bp.route('/delete_payment/<int:payment_id>')
def delete_payment(payment_id):
    conn = get_connection()
    conn.execute("DELETE FROM payments WHERE id=?", (payment_id,))
    conn.commit()
    conn.close()
    flash("Payment deleted successfully", "info")
    return redirect(url_for('payment_bp.payment_list'))


# -----------------------------
# EXPORT PAYMENTS
# -----------------------------
@payment_bp.route('/export_payments/<string:fmt>')
def export_payments(fmt):
    conn = get_connection()
    conn.row_factory = lambda cursor, row: dict(zip([col[0] for col in cursor.description], row))
    cur = conn.cursor()

    rows = cur.execute("""
        SELECT p.*, s.first_name || ' ' || s.last_name AS student_name,
               pm.name AS payment_method, cp.name AS class_pass
        FROM payments p
        JOIN students s ON p.student_id = s.id
        JOIN payment_methods pm ON p.payment_method_id = pm.id
        JOIN class_passes cp ON p.class_pass_id = cp.id
    """).fetchall()
    conn.close()

    if fmt == 'csv':
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode('utf-8')),
                         mimetype='text/csv', as_attachment=True, download_name='payments.csv')

    elif fmt == 'json':
        return jsonify(rows)

    flash("Unsupported format", "danger")
    return redirect(url_for('payment_bp.payment_list'))


# -----------------------------
# IMPORT PAYMENTS
# -----------------------------
@payment_bp.route('/import_payments', methods=['GET', 'POST'])
def import_payments():
    if request.method == 'POST':
        file = request.files['file']
        if not file:
            flash("No file uploaded", "danger")
            return redirect(request.url)

        conn = get_connection()
        cur = conn.cursor()

        if file.filename.endswith('.csv'):
            csv_data = csv.DictReader(io.StringIO(file.stream.read().decode('utf-8')))
            for row in csv_data:
                cur.execute("""
                    INSERT INTO payments (student_id, payment_date, amount, payment_method_id, class_pass_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['student_id'], row['payment_date'], row['amount'], row['payment_method_id'], row['class_pass_id']))

        elif file.filename.endswith('.json'):
            data = json.load(file)
            for row in data:
                cur.execute("""
                    INSERT INTO payments (student_id, payment_date, amount, payment_method_id, class_pass_id)
                    VALUES (?, ?, ?, ?, ?)
                """, (row['student_id'], row['payment_date'], row['amount'], row['payment_method_id'], row['class_pass_id']))

        conn.commit()
        conn.close()
        flash("Payments imported successfully", "success")
        return redirect(url_for('payment_bp.payment_list'))

    return render_template('import_payments.html')
