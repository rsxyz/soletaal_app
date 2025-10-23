import sqlite3
import os

# -------------------------------
# Database Location Setup
# -------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # directory of db.py
DB_PATH = os.path.join(BASE_DIR, "studio.db")          # ensures DB is inside fitness/db

# Make sure the db directory exists (important if running from app.py)
os.makedirs(BASE_DIR, exist_ok=True)


# ---------------------------
# DB Setup
# ---------------------------
def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Students
    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        phone TEXT,
        email_id TEXT
    )
    """)


    # Lookup tables
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payment_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS class_passes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        credits INTEGER NOT NULL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS class_names (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    """)


    cur.executemany("INSERT OR IGNORE INTO payment_methods (name) VALUES (?)", [
        ('Cash',), ('Check',), ('Zelle',), ('Free',)
    ])

    cur.executemany("INSERT OR IGNORE INTO class_passes (name, credits) VALUES (?, ?)", [
        ('1-class', 1),
        ('2-class', 2),
        ('3-class', 3),
        ('4-class', 4),
        ('5-class', 5),
        ('6-class', 6),
    ])

    # insert class_names if table empty
    existing = cur.execute("SELECT COUNT(*) FROM class_names").fetchone()[0]
    if existing == 0:
        cur.executemany(
            "INSERT OR IGNORE INTO class_names (name) VALUES (?)",
            [
                ('TUE-7PM',),
                ('TUE-8PM',)
            ]
        )

    # Payments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        payment_date TEXT NOT NULL,
        amount REAL NOT NULL,
        payment_method_id INTEGER NOT NULL,
        class_pass_id INTEGER NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (payment_method_id) REFERENCES payment_methods(id),
        FOREIGN KEY (class_pass_id) REFERENCES class_passes(id)
    )
    """)

    # Attendance
    cur.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        attendance_date TEXT NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(id),
        FOREIGN KEY (class_id) REFERENCES class_names(id)
    )
    """)

    conn.commit()
    conn.close()