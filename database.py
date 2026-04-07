import sqlite3
from datetime import datetime

DB_NAME = "students.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT    NOT NULL,
            roll_no   TEXT    NOT NULL UNIQUE,
            email     TEXT    NOT NULL,
            grade     TEXT    NOT NULL,
            phone     TEXT    NOT NULL,
            dob       TEXT    NOT NULL,
            created_at TEXT   DEFAULT (datetime('now'))
        )
    ''')
    conn.commit()
    conn.close()

def get_all_students():
    conn = get_connection()
    students = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    conn.close()
    return students

def get_student_by_id(student_id):
    conn = get_connection()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return student

def add_student(name, roll_no, email, grade, phone, dob):
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO students (name, roll_no, email, grade, phone, dob) VALUES (?, ?, ?, ?, ?, ?)",
            (name, roll_no, email, grade, phone, dob)
        )
        conn.commit()
        return True, "Student added successfully."
    except sqlite3.IntegrityError:
        return False, "Roll number already exists."
    finally:
        conn.close()

def update_student(student_id, name, roll_no, email, grade, phone, dob):
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE students SET name=?, roll_no=?, email=?, grade=?, phone=?, dob=? WHERE id=?",
            (name, roll_no, email, grade, phone, dob, student_id)
        )
        conn.commit()
        return True, "Student updated successfully."
    except sqlite3.IntegrityError:
        return False, "Roll number already exists for another student."
    finally:
        conn.close()

def delete_student(student_id):
    conn = get_connection()
    conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
    conn.commit()
    conn.close()
    return True, "Student deleted successfully."

def search_students(query):
    conn = get_connection()
    like = f"%{query}%"
    students = conn.execute(
        "SELECT * FROM students WHERE name LIKE ? OR roll_no LIKE ? OR email LIKE ? OR grade LIKE ?",
        (like, like, like, like)
    ).fetchall()
    conn.close()
    return students

# ──────────────────────────────────────────────
# ATTENDANCE FUNCTIONS
# ──────────────────────────────────────────────

def create_attendance_table():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id   INTEGER NOT NULL,
            date         DATE    NOT NULL,
            status       TEXT    NOT NULL CHECK (status IN ('present', 'absent', 'late')),
            time_marked  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id),
            UNIQUE(student_id, date)
        )
    """)
    conn.commit()
    conn.close()

def bulk_mark_attendance(attendance_data, attendance_date):
    conn = get_connection()
    try:
        for student_id, status in attendance_data.items():
            conn.execute("""
                INSERT OR REPLACE INTO attendance (student_id, date, status, time_marked)
                VALUES (?, ?, ?, ?)
            """, (student_id, attendance_date, status, datetime.now()))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def get_attendance_for_date(attendance_date):
    conn = get_connection()
    records = conn.execute("""
        SELECT s.id, s.name, s.roll_no, s.grade,
               COALESCE(a.status, 'not_marked') as status,
               a.time_marked
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id AND a.date = ?
        ORDER BY s.name
    """, (attendance_date,)).fetchall()
    conn.close()
    return records

def get_attendance_summary(attendance_date):
    conn = get_connection()
    total = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    present = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date=? AND status='present'", (attendance_date,)
    ).fetchone()[0]
    absent = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date=? AND status='absent'", (attendance_date,)
    ).fetchone()[0]
    late = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date=? AND status='late'", (attendance_date,)
    ).fetchone()[0]
    conn.close()
    return {"total_students": total, "total_present": present, "total_absent": absent, "total_late": late}

def get_student_attendance_history(student_id, limit=50):
    conn = get_connection()
    records = conn.execute("""
        SELECT date, status, time_marked
        FROM attendance
        WHERE student_id = ?
        ORDER BY date DESC
        LIMIT ?
    """, (student_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in records]
