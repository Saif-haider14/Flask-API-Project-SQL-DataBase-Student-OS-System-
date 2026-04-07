from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from database import (
    init_db, get_all_students, get_student_by_id, add_student, update_student, 
    delete_student, search_students,
    create_attendance_table, get_attendance_for_date, bulk_mark_attendance,
    get_attendance_summary, get_student_attendance_history
)

app = Flask(__name__)
app.secret_key = "student_manager_secret_key_2024"

# ──────────────────────────────────────────────
# ADMIN CREDENTIALS (hardcoded)
# ──────────────────────────────────────────────
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")

# Initialize the database when app starts
init_db()
create_attendance_table()

# ──────────────────────────────────────────────
# LOGIN REQUIRED DECORATOR
# ──────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "logged_in" not in session:
            flash("Please login first to access this page.", "error")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ──────────────────────────────────────────────
# LOGIN PAGE
# ──────────────────────────────────────────────
@app.route("/login", methods=["GET", "POST"])
def login():
    if "logged_in" in session:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["logged_in"] = True
            session["username"] = username
            flash("Welcome back, Admin! 👋", "success")
            return redirect(url_for("index"))
        else:
            flash("Invalid username or password.", "error")

    return render_template("login.html")

# ──────────────────────────────────────────────
# LOGOUT
# ──────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))

# ──────────────────────────────────────────────
# MAIN PAGE — show all students
# ──────────────────────────────────────────────
@app.route("/")
@login_required
def index():
    query = request.args.get("q", "").strip()
    if query:
        students = search_students(query)
    else:
        students = get_all_students()
    return render_template("index.html", students=students, query=query)

# ──────────────────────────────────────────────
# ADD STUDENT
# ──────────────────────────────────────────────
@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        roll_no = request.form.get("roll_no", "").strip()
        email   = request.form.get("email", "").strip()
        grade   = request.form.get("grade", "").strip()
        phone   = request.form.get("phone", "").strip()
        dob     = request.form.get("dob", "").strip()

        if not all([name, roll_no, email, grade, phone, dob]):
            flash("All fields are required.", "error")
            return render_template("add.html")

        success, message = add_student(name, roll_no, email, grade, phone, dob)
        if success:
            flash(message, "success")
            return redirect(url_for("index"))
        else:
            flash(message, "error")

    return render_template("add.html")

# ──────────────────────────────────────────────
# EDIT STUDENT
# ──────────────────────────────────────────────
@app.route("/edit/<int:student_id>", methods=["GET", "POST"])
@login_required
def edit(student_id):
    student = get_student_by_id(student_id)
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("index"))

    if request.method == "POST":
        name    = request.form.get("name", "").strip()
        roll_no = request.form.get("roll_no", "").strip()
        email   = request.form.get("email", "").strip()
        grade   = request.form.get("grade", "").strip()
        phone   = request.form.get("phone", "").strip()
        dob     = request.form.get("dob", "").strip()

        if not all([name, roll_no, email, grade, phone, dob]):
            flash("All fields are required.", "error")
            return render_template("edit.html", student=student)

        success, message = update_student(student_id, name, roll_no, email, grade, phone, dob)
        if success:
            flash(message, "success")
            return redirect(url_for("index"))
        else:
            flash(message, "error")

    return render_template("edit.html", student=student)

# ──────────────────────────────────────────────
# DELETE STUDENT
# ──────────────────────────────────────────────
@app.route("/delete/<int:student_id>", methods=["POST"])
@login_required
def delete(student_id):
    success, message = delete_student(student_id)
    flash(message, "success" if success else "error")
    return redirect(url_for("index"))

# ──────────────────────────────────────────────
# ATTENDANCE — Dashboard
# ──────────────────────────────────────────────
@app.route("/attendance")
@login_required
def attendance():
    today = date.today()
    selected_date = request.args.get("date", today.strftime("%Y-%m-%d"))
    attendance_records = get_attendance_for_date(selected_date)
    summary = get_attendance_summary(selected_date)
    return render_template("attendance.html",
                           attendance_records=attendance_records,
                           selected_date=selected_date,
                           today=today.strftime("%Y-%m-%d"),
                           summary=summary)

# ──────────────────────────────────────────────
# ATTENDANCE — Mark Attendance
# ──────────────────────────────────────────────
@app.route("/mark_attendance", methods=["GET", "POST"])
@login_required
def mark_attendance_route():
    if request.method == "POST":
        attendance_date = request.form.get("attendance_date")
        if not attendance_date:
            flash("Please select a date.", "error")
            return redirect(url_for("mark_attendance_route"))

        attendance_data = {}
        for key, value in request.form.items():
            if key.startswith("student_"):
                student_id = int(key.replace("student_", ""))
                attendance_data[student_id] = value

        if attendance_data:
            success = bulk_mark_attendance(attendance_data, attendance_date)
            if success:
                flash(f"Attendance marked successfully for {attendance_date}!", "success")
                return redirect(url_for("attendance"))
            else:
                flash("Error marking attendance. Please try again.", "error")
        else:
            flash("No attendance data submitted.", "error")

    students = get_all_students()
    today = date.today().strftime("%Y-%m-%d")
    return render_template("mark_attendance.html", students=students, today=today)

# ──────────────────────────────────────────────
# ATTENDANCE — Individual Student History
# ──────────────────────────────────────────────
@app.route("/student_attendance/<int:student_id>")
@login_required
def student_attendance(student_id):
    student = get_student_by_id(student_id)
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("index"))

    history = get_student_attendance_history(student_id)
    total = len(history)
    present = sum(1 for r in history if r["status"] == "present")
    percentage = round((present / total * 100), 1) if total > 0 else 0

    return render_template("student_attendance.html",
                           student=student,
                           attendance_history=history,
                           total_days=total,
                           present_days=present,
                           attendance_percentage=percentage)

# ──────────────────────────────────────────────
# API ENDPOINT
# ──────────────────────────────────────────────
@app.route("/api/students")
def api_students():
    students = get_all_students()
    return jsonify([dict(s) for s in students])

# ──────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
