from flask import Flask, render_template, request, redirect, session, send_file
import sqlite3
import os
from datetime import datetime
from reportlab.pdfgen import canvas
app = Flask(__name__)
app.secret_key = "school_secret_key"
# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # ================= STUDENTS TABLE =================
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

    # ================= PAYMENTS TABLE =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        amount INTEGER,
        date TEXT,
        note TEXT
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
#============= PAYMENT ================
@app.route('/add_payment/<int:id>', methods=['POST'])
def add_payment(id):

    amount = request.form.get('amount')
    note = request.form.get('note')

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO payments (student_id, amount, date, note)
        VALUES (?, ?, datetime('now'), ?)
    """, (id, amount, note))

    conn.commit()
    conn.close()

    return redirect(f'/student/{id}')


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
@app.route('/receipt/<int:id>')
def receipt(id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    s = c.fetchone()

    conn.close()

    if not s:
        return "Student Not Found"

    file_name = f"receipt_{id}.pdf"
    pdf = canvas.Canvas(file_name)

    # ================= BORDER =================
    pdf.rect(30, 30, 540, 780)
    if os.path.exists(logo_path):
    pdf.drawImage(logo_path, 260, 760, width=80, height=80)

    # ================= SCHOOL NAME =================
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawCentredString(300, 740, "MY SCHOOL")

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawCentredString(300, 720, "PAYMENT RECEIPT")

    # ================= HEADER LINE =================
    pdf.line(50, 700, 550, 700)

    pdf.setFont("Helvetica", 10)

    pdf.drawString(
        60,
        680,
        f"Receipt No: R-{id:05d}"
    )

    pdf.drawString(
        400,
        680,
        f"Date: {datetime.now().strftime('%Y-%m-%d')}"
    )

    # ================= STUDENT BOX =================
    pdf.rect(50, 560, 500, 100)

    pdf.setFont("Helvetica", 12)

    pdf.drawString(
        70,
        630,
        f"Student Name: {s[1]}"
    )

    pdf.drawString(
        70,
        610,
        f"Age: {s[2]}"
    )

    pdf.drawString(
        70,
        590,
        f"Grade: {s[3]}"
    )

    # ================= PAYMENT TABLE =================
    pdf.rect(50, 420, 500, 120)

    pdf.line(50, 510, 550, 510)
    pdf.line(50, 480, 550, 480)
    pdf.line(50, 450, 550, 450)

    pdf.line(350, 420, 350, 540)

    pdf.setFont("Helvetica-Bold", 12)

    pdf.drawString(70, 520, "Description")
    pdf.drawString(400, 520, "Amount")

    pdf.setFont("Helvetica", 12)

    pdf.drawString(70, 490, "School Fee")
    pdf.drawString(400, 490, str(s[4]))

    pdf.drawString(70, 460, "Paid")
    pdf.drawString(400, 460, str(s[5]))

    balance = s[4] - s[5]

    pdf.drawString(70, 430, "Balance")
    pdf.drawString(400, 430, str(balance))

    # ================= STATUS =================
    pdf.setFont("Helvetica-Bold", 12)

    pdf.drawString(
        70,
        380,
        f"Status: {s[6]}"
    )

    # ================= STAMP =================
    pdf.circle(120, 170, 40)

    pdf.drawCentredString(
        120,
        170,
        "STAMP"
    )

    # ================= SIGNATURE =================
    pdf.line(380, 180, 520, 180)

    pdf.drawString(
        390,
        160,
        "Authorized Signature"
    )

    # ================= FOOTER =================
    pdf.setFont("Helvetica-Oblique", 10)

    pdf.drawCentredString(
        300,
        50,
        "Thank you for your payment"
    )

    pdf.save()

    return send_file(
        file_name,
        as_attachment=True
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
