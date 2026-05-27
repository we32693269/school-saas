from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
from datetime import datetime
import os
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "secret"

# DATABASE
def get_db():
    conn = sqlite3.connect("school.db")
    return conn

# CREATE TABLES
conn = get_db()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT,
    grade TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    status TEXT,
    date TEXT
)
""")

conn.commit()
conn.close()

# LOGIN
@app.route('/', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        user = c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')

    return render_template('login.html')

# REGISTER
@app.route('/register', methods=['GET','POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():

    conn = get_db()
    c = conn.cursor()

    students = c.execute("SELECT * FROM students").fetchall()
    attendance = c.execute("SELECT * FROM attendance").fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        students=students,
        attendance=attendance
    )

# ADD STUDENT
@app.route('/add_student', methods=['POST'])
def add_student():

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']

    conn = get_db()
    c = conn.cursor()

    c.execute(
        "INSERT INTO students(name,age,grade) VALUES(?,?,?)",
        (name, age, grade)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ATTENDANCE WITH DATE
@app.route('/attendance/<int:id>/<status>')
def attendance(id, status):

    date = datetime.now().strftime("%Y-%m-%d")

    conn = get_db()
    c = conn.cursor()

    c.execute(
        "INSERT INTO attendance(student_id,status,date) VALUES(?,?,?)",
        (id, status, date)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# REPORTS
@app.route('/reports')
def reports():

    conn = get_db()
    c = conn.cursor()

    students = c.execute("SELECT * FROM students").fetchall()
    attendance = c.execute("SELECT * FROM attendance").fetchall()

    conn.close()

    return render_template(
        'reports.html',
        students=students,
        attendance=attendance
    )

# EDIT
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):

    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']

        c.execute(
            "UPDATE students SET name=?,age=?,grade=? WHERE id=?",
            (name, age, grade, id)
        )

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    student = c.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template('edit.html', student=student)

# DELETE
@app.route('/delete/<int:id>')
def delete(id):

    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# PROFILE
@app.route('/profile')
def profile():
    return render_template('profile.html')

# SETTINGS
@app.route('/settings')
def settings():
    return render_template('settings.html')

# PDF DOWNLOAD
@app.route('/download_pdf')
def download_pdf():

    conn = get_db()
    c = conn.cursor()

    students = c.execute("SELECT * FROM students").fetchall()
    attendance = c.execute("SELECT * FROM attendance").fetchall()

    conn.close()

    file = "report.pdf"
    p = canvas.Canvas(file)

    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 800, "School Report")

    y = 760

    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Students")
    y -= 20

    p.setFont("Helvetica", 10)

    for s in students:
        p.drawString(50, y, f"{s[0]} {s[1]} {s[2]} {s[3]}")
        y -= 15

    y -= 20
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Attendance")
    y -= 20

    p.setFont("Helvetica", 10)

    for a in attendance:
        p.drawString(50, y, f"{a[1]} {a[2]} {a[3]}")
        y -= 15

    p.save()

    return send_file(file, as_attachment=True)

# RUN
if __name__ == '__main__':
    app.run(debug=True)
