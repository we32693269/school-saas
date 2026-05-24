from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret123"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ---------------- DATABASE ----------------
def init_db():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    # STUDENTS TABLE
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age TEXT,
            grade TEXT,
            image TEXT
        )
    """)

    # DEFAULT ADMIN
    c.execute("SELECT * FROM users WHERE username='admin'")

    if not c.fetchone():

        c.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (
            "admin",
            generate_password_hash("1234"),
            "admin"
        ))

    conn.commit()
    conn.close()


init_db()


# ---------------- LOGIN ----------------
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("school.db")
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = c.fetchone()

        conn.close()

        if user and check_password_hash(user[2], password):

            session["user"] = username
            session["role"] = user[3]

            return redirect("/dashboard")

    return render_template("login.html")


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        conn = sqlite3.connect("school.db")
        c = conn.cursor()

        c.execute("""
            INSERT INTO users (username, password, role)
            VALUES (?, ?, ?)
        """, (
            username,
            generate_password_hash(password),
            role
        ))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("SELECT * FROM students")
c.execute("""
SELECT grade, COUNT(*) 
FROM students 
GROUP BY grade
""")
grade_analysis = c.fetchall()

c.execute("""
SELECT name, grade, COUNT(*) as total
FROM students
GROUP BY grade
ORDER BY total DESC
""")
top_data = c.fetchall()  students = c.fetchall()

  c.execute("""
SELECT status, COUNT(*) 
FROM attendance 
GROUP BY status
""")
attendance_data = c.fetchall()  c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]

    c.execute("""
        SELECT grade, COUNT(*)
        FROM students
        GROUP BY grade
    """)

    grade_data = c.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        students=students,
        total_students=total_students,
        grade_data=grade_data,
        role=session["role"]
    )


# ---------------- ADD STUDENT ----------------
@app.route("/add", methods=["POST"])
def add():

    if "user" not in session:
        return redirect("/")

    if session["role"] not in ["admin", "teacher"]:
        return "Access denied"

    name = request.form["name"]
    age = request.form["age"]
    grade = request.form["grade"]

    image = request.files.get("image")

    filename = "default.png"

    if image and image.filename != "":

        filename = secure_filename(image.filename)

        image.save(os.path.join(UPLOAD_FOLDER, filename))

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO students (name, age, grade, image)
        VALUES (?, ?, ?, ?)
    """, (name, age, grade, filename))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):

    if session["role"] != "admin":
        return "Only admin can delete"

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------------- EDIT ----------------
@app.route("/edit/<int:id>")
def edit(id):

    if session["role"] not in ["admin", "teacher"]:
        return "Access denied"

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = c.fetchone()

    conn.close()

    return render_template("edit.html", student=student)


# ---------------- UPDATE ----------------
@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    if session["role"] not in ["admin", "teacher"]:
        return "Access denied"

    name = request.form["name"]
    age = request.form["age"]
    grade = request.form["grade"]

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        UPDATE students
        SET name=?, age=?, grade=?
        WHERE id=?
    """, (
        name,
        age,
        grade,
        id
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------------- SEARCH ----------------
@app.route("/search")
def search():

    query = request.args.get("q")

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        SELECT * FROM students
        WHERE name LIKE ?
    """, ('%' + query + '%',))

    students = c.fetchall()

    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]

    c.execute("""
        SELECT grade, COUNT(*)
        FROM students
        GROUP BY grade
    """)

    grade_data = c.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        students=students,
        total_students=total_students,
        grade_data=grade_data,
        role=session["role"]
    )


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
