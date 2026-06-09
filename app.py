from flask import Flask, render_template, request, redirect, session
from reportlab.pdfgen import canvas
from flask import send_file
import sqlite3
import io
app = Flask(__name__)
app.secret_key = "school_secret_key"
# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        grade TEXT,
        fee INTEGER,
        paid INTEGER,
        status TEXT DEFAULT 'Not Marked'
    )
    """)

    conn.commit()
    conn.close()

init_db()
#============= login ==============
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if username == "admin" and password == "1234":
            session['admin'] = True
            return redirect('/dashboard')

        return "Invalid Username or Password"

    return render_template('login.html')
#=============== LOGOUT ==================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
# ================= HOME =================
@app.route('/')
def home():
    return redirect('/dashboard')
#========== STUDENT PROFILE ===============
@app.route('/student/<int:id>')
def student_profile(id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()

    conn.close()

    return render_template("student_profile.html", student=student)
@app.route('/test')
def test():
    return "Receipt Route Working"
# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():

    if not session.get('admin'):
        return redirect('/login')

    search = request.args.get('search', '')

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    if search:
        c.execute(
            "SELECT * FROM students WHERE name LIKE ?",
            ('%' + search + '%',)
        )
    else:
        c.execute("SELECT * FROM students")

    students = c.fetchall()

    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM students WHERE status='Present'")
    present_students = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM students WHERE status='Absent'")
    absent_students = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM students WHERE status='Late'")
    late_students = c.fetchone()[0]

    c.execute("SELECT SUM(fee) FROM students")
    total_fee = c.fetchone()[0] or 0

    c.execute("SELECT SUM(paid) FROM students")
    total_paid = c.fetchone()[0] or 0

    total_balance = total_fee - total_paid

    conn.close()
    return render_template(
    "dashboard.html",
    students=students,
    total_students=total_students,
    total_fee=total_fee,
    total_paid=total_paid,
    total_balance=total_balance,
    present_students=present_students,
    absent_students=absent_students,
    late_students=late_students
)



# ================= ADD STUDENT =================
@app.route('/add_student', methods=['POST'])
def add_student():

    name = request.form.get('name')
    age = request.form.get('age')
    grade = request.form.get('grade')
    fee = request.form.get('fee')
    paid = request.form.get('paid')

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO students
        (name, age, grade, fee, paid, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, age, grade, fee, paid, "Not Marked"))

    conn.commit()
    conn.close()

    return redirect('/dashboard')
#============ RECEIPT ==============

import sqlite3
from flask import send_file
from reportlab.pdfgen import canvas
from io import BytesIO
from datetime import datetime
import os

@app.route('/receipt/<int:id>')
def receipt(id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()
    c.execute("SELECT * FROM students WHERE id=?", (id,))
    s = c.fetchone()
    conn.close()

    # ✅ FIX: avoid crash
    if not s:
        return "Student Not Found"

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    # BORDER
    pdf.rect(40, 40, 520, 760)

    # TITLE
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawCentredString(300, 800, "SCHOOL RECEIPT")

    # DATE
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 770, "School ERP")
    pdf.drawString(420, 770, datetime.now().strftime("%Y-%m-%d"))

    # LINE
    pdf.line(40, 760, 560, 760)

    # RECEIPT NO
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 740, f"Receipt No: R-{id:05d}")

    # LOGO SAFE
    logo_path = "static/logo.png"
    if os.path.exists(logo_path):
        pdf.drawImage(logo_path, 450, 780, width=60, height=50)

    # DATA
    pdf.setFont("Helvetica", 12)
    pdf.drawString(120, 700, f"Name: {s[1]}")
    pdf.drawString(120, 680, f"Age: {s[2]}")
    pdf.drawString(120, 660, f"Grade: {s[3]}")
    pdf.drawString(120, 640, f"Fee: {s[4]}")
    pdf.drawString(120, 620, f"Paid: {s[5]}")

    balance = s[4] - s[5]
    pdf.drawString(120, 600, f"Balance: {balance}")
    pdf.drawString(120, 580, f"Status: {s[6]}")

    pdf.save()

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"receipt_{id}.pdf",
        mimetype="application/pdf"
    )


# ================= EDIT =================
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()

    if student is None:
        conn.close()
        return "Student Not Found"

    if request.method == 'POST':

        name = request.form.get('name')
        age = request.form.get('age')
        grade = request.form.get('grade')
        fee = request.form.get('fee')
        paid = request.form.get('paid')
        status = request.form.get('status')

        c.execute("""
            UPDATE students
            SET name=?, age=?, grade=?, fee=?, paid=?, status=?
            WHERE id=?
        """, (name, age, grade, fee, paid, status, id))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    conn.close()

    return render_template("edit_student.html", student=student)


# ================= DELETE =================
@app.route('/delete_student/<int:id>')
def delete_student(id):

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ================= RUN =================
if __name__ == "__main__":
    print("APP STARTING...")
    app.run(host="0.0.0.0", port=5000, debug=True)
