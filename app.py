from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import os
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    return conn


# ================= CREATE TABLES =================
def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        grade TEXT,
        photo TEXT
    )
    """)

    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        status TEXT,
        date TEXT
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


init_db()


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

    return render_template("login.html")


# ================= DASHBOARD =================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        grade = request.form["grade"]
        photo = request.files["photo"]

        filename = ""
        if photo:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        c.execute("""
        INSERT INTO students (name, age, grade, photo)
        VALUES (?, ?, ?, ?)
        """, (name, age, grade, filename))

        conn.commit()
        return redirect("/dashboard")

    students = c.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template("dashboard.html", students=students)


# ================= DELETE =================
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/dashboard")


# ================= PROFILE =================
@app.route("/student/<int:id>")
def student_profile(id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("profile.html", student=student)


# ================= ATTENDANCE =================
@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    conn = get_db()

    if request.method == "POST":
        conn.execute("""
        INSERT INTO attendance (student_id, status, date)
        VALUES (?, ?, ?)
        """, (
            request.form["student_id"],
            request.form["status"],
            request.form["date"]
        ))
        conn.commit()

    data = conn.execute("SELECT * FROM attendance").fetchall()
    conn.close()

    return render_template("attendance.html", data=data)


# ================= FEES PDF =================
@app.route("/fee_receipt/<int:id>")
def fee_receipt(id):
    conn = get_db()
    fee = conn.execute("SELECT * FROM fees WHERE id=?", (id,)).fetchone()
    conn.close()

    file_path = f"/tmp/receipt_{id}.pdf"

    p = canvas.Canvas(file_path)
    p.drawString(100, 800, "FEE RECEIPT")
    p.drawString(100, 760, f"Student: {fee['student_name']}")
    p.drawString(100, 740, f"Amount: {fee['amount']}")
    p.drawString(100, 720, f"Status: {fee['status']}")
    p.save()

    return send_file(file_path, as_attachment=True)


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
