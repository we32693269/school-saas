from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import os
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# ================= DATABASE =================
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


# ================= DASHBOARD =================
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']

        photo = request.files['photo']
        filename = ""

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        c.execute("""
        INSERT INTO students (name, age, grade, photo)
        VALUES (?, ?, ?, ?)
        """, (name, age, grade, filename))

        conn.commit()
        return redirect('/dashboard')

    students = c.execute("SELECT * FROM students").fetchall()

    conn.close()

    return render_template("dashboard.html", students=students)


# ================= STUDENT PROFILE =================
@app.route('/student/<int:id>')
def student_profile(id):

    conn = get_db()
    c = conn.cursor()

    student = c.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return "Student not found"

    return render_template("student_profile.html", student=student)


# ================= FEES =================
@app.route('/fees', methods=['GET', 'POST'])
def fees():

    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':

        student_name = request.form['student_name']
        amount = request.form['amount']
        status = request.form['status']

        c.execute("""
        INSERT INTO fees (student_name, amount, status)
        VALUES (?, ?, ?)
        """, (student_name, amount, status))

        conn.commit()

    fees_data = c.execute("SELECT * FROM fees").fetchall()

    conn.close()

    return render_template("fees.html", fees=fees_data)


# ================= TIMETABLE =================
@app.route('/timetable')
def timetable():
    return render_template("timetable.html")


# ================= PDF DOWNLOAD =================
@app.route('/download_report')
def download_report():

    file_path = "/tmp/report.pdf"

    conn = get_db()
    c = conn.cursor()

    students = c.execute("SELECT * FROM students").fetchall()
    conn.close()

    p = canvas.Canvas(file_path)

    y = 800
    p.drawString(100, y, "SCHOOL FULL REPORT")
    y -= 30

    for s in students:
        p.drawString(100, y, f"{s['id']} - {s['name']} - {s['grade']}")
        y -= 20

    p.save()

    return send_file(file_path, as_attachment=True)


# ================= HOME =================
@app.route('/')
def home():
    return redirect('/dashboard')


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
