from flask import Flask, render_template, request, redirect, session, send_file
from werkzeug.utils import secure_filename
import os
import sqlite3
from datetime import datetime
from reportlab.pdfgen import canvas

app = Flask(__name__)
app.secret_key = "secret"
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect("school.db")
    return conn

# ================= CREATE TABLES =================
conn = get_db()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
c.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT,
    grade TEXT,
    photo TEXT
)
''')
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    status TEXT,
    date TEXT
)
""")
c.execute('''
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    amount TEXT,
    status TEXT
)
''')
conn.commit()
conn.close()

# ================= LOGIN =================
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

# ================= REGISTER =================
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
@app.route('/upload_profile', methods=['POST'])
def upload_profile():

    file = request.files['profile_pic']

    if file:
        filename = secure_filename(file.filename)

        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        session['profile_pic'] = filename

    return redirect('/dashboard')
# ================= DASHBOARD =================
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    conn = get_db()
    c = conn.cursor()

    # create table if not exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age TEXT,
            grade TEXT
        )
    """)

    # add student
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        photo = request.files['photo']

filename = ''

if photo:
    filename = secure_filename(photo.filename)

    photo.save(
        os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )
    )

 c.execute(
    "INSERT INTO students (name, age, grade, photo) VALUES (?, ?, ?, ?)",
    (name, age, grade, filename)
)

        conn.commit()
        return redirect('/dashboard')

    # get students
    c.execute("SELECT * FROM students")
    students = c.fetchall()

    conn.close()

    return render_template('dashboard.html', students=students)
# ================= FEES =================
@app.route('/fees', methods=['GET', 'POST'])
def fees():

    conn = get_db()
    c = conn.cursor()

    # CREATE TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS fees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        amount TEXT,
        status TEXT
    )
    """)

    # ADD FEES
    if request.method == 'POST':

        student_name = request.form['student_name']
        amount = request.form['amount']
        status = request.form['status']

        c.execute(
            "INSERT INTO fees(student_name, amount, status) VALUES(?, ?, ?)",
            (student_name, amount, status)
        )

        conn.commit()

    # GET FEES
    c.execute("SELECT * FROM fees")
    fees = c.fetchall()

    conn.close()

    return render_template('fees.html', fees=fees)
#================ Receipt ==================
from reportlab.pdfgen import canvas
@app.route('/receipt/<int:id>')
def receipt(id):

    conn = get_db()
    c = conn.cursor()

    fee = c.execute(
        "SELECT * FROM fees WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    file = f"receipt_{id}.pdf"

    p = canvas.Canvas(file)

    # TITLE
    p.setFont("Helvetica-Bold", 22)
    p.drawString(180, 800, "FEE RECEIPT")

    # SCHOOL
    p.setFont("Helvetica", 14)
    p.drawString(50, 760, "School SaaS System")

    # RECEIPT INFO
    p.drawString(50, 700, f"Receipt ID: {fee[0]}")
    p.drawString(50, 670, f"Student Name: {fee[1]}")
    p.drawString(50, 640, f"Amount Paid: {fee[2]} Birr")
    p.drawString(50, 610, f"Status: {fee[3]}")

    # FOOTER
    p.drawString(50, 500, "Thank you for your payment!")

    p.save()

    return send_file(file, as_attachment=True)
 # ================= TIMETABLE =================
@app.route('/timetable')
def timetable():

    return render_template('timetable.html')
# ================= ADD STUDENT =================
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

# ================= ATTENDANCE =================
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

# ================= REPORTS =================
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

# ================= EDIT =================
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

# ================= DELETE =================
@app.route('/delete/<int:id>')
def delete(id):

    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ================= PDF REPORT (PRO MAX) =================

from flask import send_file
from reportlab.pdfgen import canvas
from datetime import datetime

@app.route('/download_pdf')
def download_pdf():

    conn = get_db()
    c = conn.cursor()

    students = c.execute("SELECT * FROM students").fetchall()

    conn.close()

    file = "report.pdf"

    p = canvas.Canvas(file)

    # TITLE
    p.setFont("Helvetica-Bold", 20)
    p.drawString(180, 800, "SCHOOL REPORT")

    # DATE
    p.setFont("Helvetica", 12)
    p.drawString(50, 770, f"Generated: {datetime.now()}")

    # TABLE HEADER
    p.setFont("Helvetica-Bold", 13)

    p.drawString(50, 730, "ID")
    p.drawString(100, 730, "Name")
    p.drawString(250, 730, "Age")
    p.drawString(320, 730, "Grade")

    y = 700

    # STUDENTS DATA
    p.setFont("Helvetica", 12)

    for s in students:

        p.drawString(50, y, str(s[0]))
        p.drawString(100, y, str(s[1]))
        p.drawString(250, y, str(s[2]))
        p.drawString(320, y, str(s[3]))

        y -= 25

        # NEW PAGE
        if y < 50:
            p.showPage()
            y = 800

    # FOOTER
    p.setFont("Helvetica-Bold", 11)
    p.drawString(180, 30, "School SaaS System")

    p.save()

    return send_file(file, as_attachment=True)

    # ================= HEADER =================
    p.setFillColorRGB(0, 0, 0.6)
    p.rect(0, 780, 600, 50, fill=1)

    p.setFillColorRGB(1, 1, 1)
    p.setFont("Helvetica-Bold", 20)
    p.drawString(200, 800, "SCHOOL REPORT")

    p.setFont("Helvetica", 10)
    p.drawString(230, 785, f"Date: {date_today}")

    # reset color
    p.setFillColorRGB(0, 0, 0)

    # ================= STUDENTS =================
    y = 740

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "STUDENTS")

    y -= 25

    # HEADER ROW (colored)
    p.setFillColorRGB(0.9, 0.9, 0.9)
    p.rect(50, y, 500, 20, fill=1)

    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(60, y+5, "ID")
    p.drawString(120, y+5, "NAME")
    p.drawString(280, y+5, "AGE")
    p.drawString(400, y+5, "GRADE")

    y -= 20
    p.setFont("Helvetica", 11)

    for s in students:

        if y < 120:
            p.showPage()
            y = 750

        p.rect(50, y, 500, 20)

        p.drawString(60, y+5, str(s[0]))
        p.drawString(120, y+5, str(s[1]))
        p.drawString(280, y+5, str(s[2]))
        p.drawString(400, y+5, str(s[3]))

        y -= 20

    # ================= ATTENDANCE =================
    y -= 40

    if y < 120:
        p.showPage()
        y = 750

    p.setFont("Helvetica-Bold", 14)
    p.drawString(50, y, "ATTENDANCE")

    y -= 25

    # HEADER ROW (colored)
    p.setFillColorRGB(0.9, 0.9, 0.9)
    p.rect(50, y, 500, 20, fill=1)

    p.setFillColorRGB(0, 0, 0)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(60, y+5, "STUDENT ID")
    p.drawString(220, y+5, "STATUS")
    p.drawString(400, y+5, "DATE")

    y -= 20
    p.setFont("Helvetica", 11)

    for a in attendance:

        if y < 120:
            p.showPage()
            y = 750

        p.rect(50, y, 500, 20)

        p.drawString(60, y+5, str(a[1]))
        p.drawString(220, y+5, str(a[2]))
        p.drawString(400, y+5, str(a[3]))

        y -= 20

    # ================= FOOTER =================
    p.setFont("Helvetica-Oblique", 9)
    p.drawString(200, 40, "Powered by School SaaS System")

    p.save()

    return send_file(file, as_attachment=True)
@app.route('/profile')
def profile():
    return render_template("profile.html")


@app.route('/settings')
def settings():
    return render_template("settings.html")


@app.route('/logout')
def logout():
    return redirect('/')
# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)
