# StudentOS — Student Management System

A beginner-friendly web app built with **Flask + SQLite + HTML/CSS/JS**.

---

## Project Structure

```
student_manager/
├── app.py            ← Flask app & all routes
├── database.py       ← SQLite database logic
├── requirements.txt  ← Python dependencies
├── students.db       ← SQLite database (auto-created on first run)
├── static/
│   ├── style.css     ← All styles
│   └── main.js       ← JavaScript (delete confirm, flash hide)
└── templates/
    ├── base.html     ← Shared layout (header, footer, nav)
    ├── index.html    ← Dashboard / student list
    ├── add.html      ← Add new student form
    └── edit.html     ← Edit student form
```

---

## Setup & Run (Step by Step)

### 1. Make sure Python is installed
```
python --version
```
Should show Python 3.8 or higher.

### 2. Install Flask
```
pip install flask
```

### 3. Go into the project folder
```
cd student_manager
```

### 4. Run the app
```
python app.py
```

### 5. Open in your browser
```
http://127.0.0.1:5000
```

That's it! The SQLite database (`students.db`) is created automatically.

---

## Features

| Feature | Route | Method |
|---|---|---|
| View all students | `/` | GET |
| Search students | `/?q=name` | GET |
| Add student | `/add` | GET / POST |
| Edit student | `/edit/<id>` | GET / POST |
| Delete student | `/delete/<id>` | POST |
| JSON API | `/api/students` | GET |

---

## Switching to MySQL (XAMPP) Later

1. Install PyMySQL: `pip install pymysql`
2. In `database.py`, replace `sqlite3.connect(...)` with:

```python
import pymysql
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='',
    database='student_db'
)
```

3. Create the `student_db` database in phpMyAdmin and run the CREATE TABLE SQL.
