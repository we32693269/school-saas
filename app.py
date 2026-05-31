from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"


# ================= DB =================
def get_db():
    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    return conn


# ================= CREATE TABLES =================
conn = get_db()
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT DEFAULT 'user'
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    status TEXT,
    date TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT,
    grade TEXT
)
""")
c.execute("""
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    amount TEXT,
    status TEXT
)
""")
conn.commit()
conn.close()


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = username
            session["user"] = role
            return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()

        existing = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if existing:
            conn.close()
            return "Username already exists"

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, "user")
        )
        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# ================= DASHBOARD =================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect("/")
    role = session.get("role")
    conn = get_db()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        grade = request.form["grade"]

        conn.execute(
            "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)",
            (name, age, grade)
        )
        conn.commit()

    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template("dashboard.html", students=students, role=role )
#============== FEES ================
@app.route("/fees", methods=["GET", "POST"])
def fees():

    if "user" not in session:
        return redirect("/")

    conn = get_db()

    if request.method == "POST":

        student_name = request.form["student_name"]
        amount = request.form["amount"]
        status = request.form["status"]

        conn.execute("""
            INSERT INTO fees (student_name, amount, status)
            VALUES (?, ?, ?)
        """, (student_name, amount, status))

        conn.commit()

    fees = conn.execute("SELECT * FROM fees").fetchall()
    conn.close()

    return render_template("fees.html", fees=fees)
#================= RECEIPT ===============
from reportlab.pdfgen import canvas
from flask import send_file
import os

@app.route("/receipt/<int:id>")
def receipt(id):

    conn = get_db()

    fee = conn.execute(
        "SELECT * FROM fees WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    file_path = f"receipt_{id}.pdf"

    p = canvas.Canvas(file_path)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "FEE RECEIPT")

    p.setFont("Helvetica", 12)
    p.drawString(100, 750, f"Student: {fee['student_name']}")
    p.drawString(100, 730, f"Amount: {fee['amount']}")
    p.drawString(100, 710, f"Status: {fee['status']}")

    p.save()

    return send_file(file_path, as_attachment=True)
#============== ATTENDANCE =================
@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    if "user" not in session:
        return redirect("/")

    conn = get_db()

    if request.method == "POST":

        student_name = request.form["student_name"]
        status = request.form["status"]
        date = request.form["date"]

        conn.execute("""
            INSERT INTO attendance (student_name, status, date)
            VALUES (?, ?, ?)
        """, (student_name, status, date))

        conn.commit()

    data = conn.execute("SELECT * FROM attendance ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("attendance.html", data=data)
#============ ATTENDANCE REPORT ===============
@app.route("/attendance_report")
def attendance_report():

    if "user" not in session:
        return redirect("/")

    conn = get_db()

    total = conn.execute("SELECT COUNT(*) as total FROM attendance").fetchone()

    present = conn.execute(
        "SELECT COUNT(*) as p FROM attendance WHERE status='Present'"
    ).fetchone()

    absent = conn.execute(
        "SELECT COUNT(*) as a FROM attendance WHERE status='Absent'"
    ).fetchone()

    conn.close()

    return render_template(
        "attendance_report.html",
        total=total["total"],
        present=present["p"],
        absent=absent["a"]
    )
# ================= EDIT =================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if "user" not in session:
        return redirect("/")

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        grade = request.form["grade"]

        conn.execute("""
            UPDATE students
            SET name=?, age=?, grade=?
            WHERE id=?
        """, (name, age, grade, id))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    conn.close()

    return render_template("edit.html", student=student)


# ================= DELETE =================
@app.route("/delete/<int:id>")
def delete(id):

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
