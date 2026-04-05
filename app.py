from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from database import (init_db, get_all_students, get_student_by_id,
                       add_student, update_student, delete_student,
                       search_students, get_students_paginated,
                       get_total_students, search_students_paginated)

app = Flask(__name__)
app.secret_key = "student_manager_secret_key_2024"

# ──────────────────────────────────────────────
# ADMIN CREDENTIALS (hardcoded)
# ──────────────────────────────────────────────
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD_HASH = generate_password_hash("admin123")

# Initialize the database when app starts
init_db()

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
# MAIN PAGE — show all students (with pagination)
# ──────────────────────────────────────────────
PER_PAGE = 10

@app.route("/")
@login_required
def index():
    query = request.args.get("q", "").strip()
    page  = request.args.get("page", 1, type=int)
    if page < 1:
        page = 1

    if query:
        students, total = search_students_paginated(query, page, PER_PAGE)
    else:
        students = get_students_paginated(page, PER_PAGE)
        total    = get_total_students()

    total_pages = max(1, -(-total // PER_PAGE))  # ceiling division
    if page > total_pages:
        page = total_pages

    return render_template(
        "index.html",
        students=students,
        query=query,
        page=page,
        total=total,
        total_pages=total_pages,
        per_page=PER_PAGE
    )

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
# API ENDPOINT — returns JSON (optional use)
# ──────────────────────────────────────────────
@app.route("/api/students")
def api_students():
    students = get_all_students()
    return jsonify([dict(s) for s in students])

# ──────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
