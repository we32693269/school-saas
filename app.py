from flask import Flask, render_template, request, redirect, send_file
import sqlite3
import os
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    return conn


# ================= CREATE TABLES =================
conn = get_db()
c = conn.cursor()

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
    student_id TEXT,
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


# ================= HOME =================
@app.route('/')
def home():
    return redirect('/dashboard')


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

        if photo:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        c.execute("""
            INSERT INTO students (name, age, grade, photo)
            VALUES (?, ?, ?, ?)
        """, (name, age, grade, filename))

        conn.commit()

    students = c.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template("dashboard.html", students=students)


# ================= STUDENT PROFILE =================
@app.route('/student/<int:id>')
def student_profile(id):

    conn = get_db()
    c = conn.cursor()

    student = c.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()

    conn.close()

    if not student:
        return "Student not found"

    return render_template("student_profile.html", student=student)


# ================= DELETE STUDENT =================
@app.route('/delete_student/<int:id>')
def delete_student(id):

    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')


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


# ================= ATTENDANCE =================
@app.route('/attendance', methods=['GET', 'POST'])
def attendance():

    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':

        student_id = request.form['student_id']
        status = request.form['status']
        date = request.form['date']

        c.execute("""
        INSERT INTO attendance (student_id, status, date)
        VALUES (?, ?, ?)
        """, (student_id, status, date))

        conn.commit()

    data = c.execute("SELECT * FROM attendance").fetchall()

    conn.close()

    return render_template("attendance.html", data=data)


# ================= FEE RECEIPT PDF =================
@app.route('/fee_receipt/<int:id>')
def fee_receipt(id):

    conn = get_db()
    c = conn.cursor()

    fee = c.execute("SELECT * FROM fees WHERE id=?", (id,)).fetchone()

    conn.close()

    file_path = "/tmp/receipt.pdf"

    p = canvas.Canvas(file_path)
    p.drawString(100, 800, "SCHOOL FEE RECEIPT")
    p.drawString(100, 760, f"Student: {fee['student_name']}")
    p.drawString(100, 740, f"Amount: {fee['amount']}")
    p.drawString(100, 720, f"Status: {fee['status']}")
    p.save()

    return send_file(file_path, as_attachment=True)


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
