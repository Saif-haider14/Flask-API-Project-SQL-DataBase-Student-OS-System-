import sqlite3

DB_NAME = "students.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # allows dict-like access to rows
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

def get_students_paginated(page, per_page=10):
    conn = get_connection()
    offset = (page - 1) * per_page
    students = conn.execute(
        "SELECT * FROM students ORDER BY id DESC LIMIT ? OFFSET ?",
        (per_page, offset)
    ).fetchall()
    conn.close()
    return students

def get_total_students():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    conn.close()
    return count

def search_students_paginated(query, page, per_page=10):
    conn = get_connection()
    like = f"%{query}%"
    offset = (page - 1) * per_page
    students = conn.execute(
        """SELECT * FROM students
           WHERE name LIKE ? OR roll_no LIKE ? OR email LIKE ? OR grade LIKE ?
           ORDER BY id DESC LIMIT ? OFFSET ?""",
        (like, like, like, like, per_page, offset)
    ).fetchall()
    total = conn.execute(
        """SELECT COUNT(*) FROM students
           WHERE name LIKE ? OR roll_no LIKE ? OR email LIKE ? OR grade LIKE ?""",
        (like, like, like, like)
    ).fetchone()[0]
    conn.close()
    return students, total

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
