
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
import sqlite3
import csv
import io
from datetime import datetime

from studio.db.db import get_connection
from studio.expense import expense_bp

@expense_bp.route('/expenses')
def expenses_list():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.id, e.expense_date, t.name AS type, e.amount, e.notes, e.expense_type_id
        FROM expenses e
        JOIN expense_types t ON e.expense_type_id = t.id
        ORDER BY e.expense_date DESC
    """)
    expenses = cur.fetchall()

    cur.execute("SELECT id, name FROM expense_types ORDER BY name")
    types = cur.fetchall()

    conn.close()
    return render_template('expense_list.html', expenses=expenses, types=types)


@expense_bp.route('/expenses/add', methods=['POST'])
def add_expense():
    expense_date = request.form['expense_date']
    expense_type_id = request.form['expense_type_id']
    amount = request.form['amount']
    notes = request.form.get('notes', '')

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO expenses (expense_date, expense_type_id, amount, notes)
        VALUES (?, ?, ?, ?)
    """, (expense_date, expense_type_id, amount, notes))
    conn.commit()
    conn.close()
    flash("Expense added successfully!", "success")
    return redirect(url_for('expense_bp.expenses_list'))


@expense_bp.route('/expenses/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    conn = get_connection()
    cur = conn.cursor()

    if request.method == 'POST':
        expense_date = request.form['expense_date']
        expense_type_id = request.form['expense_type_id']
        amount = request.form['amount']
        notes = request.form.get('notes', '')

        cur.execute("""
            UPDATE expenses
            SET expense_date = ?, expense_type_id = ?, amount = ?, notes = ?
            WHERE id = ?
        """, (expense_date, expense_type_id, amount, notes, id))
        conn.commit()
        conn.close()
        flash("Expense updated successfully!", "success")
        return redirect(url_for('expense_bp.expenses_list'))

    # GET method → load data for edit
    cur.execute("""
        SELECT id, expense_date, expense_type_id, amount, notes
        FROM expenses WHERE id = ?
    """, (id,))
    expense = cur.fetchone()

    cur.execute("SELECT id, name FROM expense_types ORDER BY name")
    types = cur.fetchall()
    conn.close()
    return render_template('expense_form.html', expense=expense, types=types)


@expense_bp.route('/expenses/delete/<int:id>')
def delete_expense(id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Expense deleted.", "info")
    return redirect(url_for('expense_bp.expenses_list'))


@expense_bp.route('/expenses/export')
def export_expenses():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT e.expense_date, t.name, e.amount, e.notes
        FROM expenses e
        JOIN expense_types t ON e.expense_type_id = t.id
        ORDER BY e.expense_date
    """)
    rows = cur.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date', 'Type', 'Amount', 'Notes'])
    writer.writerows(rows)
    output.seek(0)

    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'expenses_{datetime.now().strftime("%Y%m%d")}.csv'
    )


@expense_bp.route('/expenses/import', methods=['POST'])
def import_expenses():
    file = request.files['file']
    if not file:
        flash("No file selected.", "danger")
        return redirect(url_for('expense_bp.expenses_list'))

    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_input = csv.reader(stream)
    next(csv_input)  # Skip header

    conn = get_connection()
    cur = conn.cursor()

    for row in csv_input:
        expense_date, type_name, amount, notes = row
        cur.execute("SELECT id FROM expense_types WHERE name = ?", (type_name,))
        type_row = cur.fetchone()
        if type_row:
            type_id = type_row[0]
        else:
            cur.execute("INSERT INTO expense_types (name) VALUES (?)", (type_name,))
            type_id = cur.lastrowid

        cur.execute("""
            INSERT INTO expenses (expense_date, expense_type_id, amount, notes)
            VALUES (?, ?, ?, ?)
        """, (expense_date, type_id, amount, notes))

    conn.commit()
    conn.close()
    flash("Expenses imported successfully!", "success")
    return redirect(url_for('expense_bp.expenses_list'))