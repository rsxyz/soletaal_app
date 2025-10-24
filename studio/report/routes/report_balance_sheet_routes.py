
from flask import Blueprint, render_template, request
import sqlite3
from studio.db.db import get_connection
from studio.report import report_bp

@report_bp.route('/balance_sheet')
def balance_sheet():
    """Show year-month level summary of income, expense, and net profit."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # --- Income: from payments table ---
    cur.execute("""
        SELECT
            strftime('%Y', payment_date) AS year,
            strftime('%m', payment_date) AS month,
            SUM(amount) AS income
        FROM payments
        GROUP BY year, month
    """)
    income_rows = cur.fetchall()

    # --- Expenses ---
    cur.execute("""
        SELECT
            strftime('%Y', expense_date) AS year,
            strftime('%m', expense_date) AS month,
            SUM(amount) AS expense
        FROM expenses
        GROUP BY year, month
    """)
    expense_rows = cur.fetchall()

    # Merge income + expense by year-month
    summary = {}

    for r in income_rows:
        key = (r['year'], r['month'])
        summary[key] = {'year': r['year'], 'month': r['month'], 'income': r['income'], 'expense': 0.0}

    for r in expense_rows:
        key = (r['year'], r['month'])
        if key not in summary:
            summary[key] = {'year': r['year'], 'month': r['month'], 'income': 0.0, 'expense': r['expense']}
        else:
            summary[key]['expense'] = r['expense']

    # Calculate net profit
    for val in summary.values():
        val['net'] = (val['income'] or 0) - (val['expense'] or 0)

    # Sort by year, month
    rows = sorted(summary.values(), key=lambda x: (x['year'], x['month']))

    conn.close()
    return render_template('report_balance_sheet.html', rows=rows)
