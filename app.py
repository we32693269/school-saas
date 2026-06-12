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

    # ================= STUDENTS =================
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
    c.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        subject TEXT,
        phone TEXT,
        salary INTEGER,
        date TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)
    # ================= PAYMENTS =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        amount INTEGER,
        date TEXT,
        note TEXT
    )
    """)

    # ================= ATTENDANCE (ONLY ONCE) =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        student_name TEXT,
        status TEXT,
        date TEXT
    )
    """)

    # ================= SETTINGS =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        id INTEGER PRIMARY KEY,
        school_name TEXT,
        logo TEXT,
        default_fee INTEGER,
        admin_password TEXT,
        academic_year TEXT,
        phone TEXT,
        email TEXT,
        email_password TEXT,
        sms_api_key TEXT,
        footer_message TEXT
    )
    """)

    # DEFAULT SETTINGS
    c.execute("""
    INSERT OR IGNORE INTO settings
    (id, school_name, logo, default_fee, admin_password, academic_year,
     phone, email, email_password, sms_api_key, footer_message)
    VALUES
    (1, 'MY SCHOOL', 'static/logo.png', 0, '1234', '2025/2026',
     '', '', '', '', '')
    """)

    conn.commit()
    conn.close()

init_db()

#============= login ==============
@app.route('/login', methods=['GET', 'POST'])
def login():

    try:
        if request.method == 'POST':

            username = request.form.get('username')
            password = request.form.get('password')

            conn = sqlite3.connect("school.db")
            c = conn.cursor()

            c.execute("""
            SELECT role FROM users
            WHERE username=? AND password=?
            """, (username, password))

            user = c.fetchone()
            conn.close()

            if user:
                session['role'] = user[0]
                return redirect('/dashboard')

            return "Invalid login"

        return render_template('login.html')

    except Exception as e:
        return str(e)
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

    # Student info
    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()

    # Payment history
    c.execute("SELECT * FROM payments WHERE student_id=?", (id,))
    payments = c.fetchall()

    c.execute("SELECT SUM(amount) FROM payments WHERE student_id=?", (id,))
    total_paid = c.fetchone()[0] or 0

    balance = student[4] - total_paid

    conn.close()

    return render_template(
        "student_profile.html",
        student=student,
        payments=payments,
        total_paid=total_paid,
        balance=balance
    )
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
# ================= SETTINGS =================
@app.route('/settings', methods=['GET', 'POST'])
def settings():

    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':

        c.execute("""
        UPDATE settings SET
            school_name=?,
            default_fee=?,
            admin_password=?,
            phone=?,
            email=?,
            footer_message=?
        WHERE id=1
        """, (
            request.form.get('school_name'),
            request.form.get('default_fee'),
            request.form.get('admin_password'),
            request.form.get('phone'),
            request.form.get('email'),
            request.form.get('footer_message')
        ))

        conn.commit()

    c.execute("SELECT * FROM settings WHERE id=1")
    data = c.fetchone()

    conn.close()

    return render_template("settings.html", settings=data)

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
#=============== TEACHER DASHBOARD =================
@app.route('/teacher_dashboard')
def teacher_dashboard():

    if session.get('role') != 'teacher':
        return redirect('/login')

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # teacher info
    c.execute("""
    SELECT * FROM teachers
    """)
    teachers = c.fetchall()

    # students count
    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]

    # attendance today
    c.execute("""
    SELECT COUNT(*) FROM attendance
    WHERE date(date) = date('now')
    """)
    today_attendance = c.fetchone()[0]

    conn.close()

    return render_template(
        "teacher_dashboard.html",
        teachers=teachers,
        total_students=total_students,
        today_attendance=today_attendance
    )
#=============== TEACHERS ================
@app.route('/teachers')
def teachers():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("SELECT * FROM teachers")
    data = c.fetchall()

    conn.close()

    return render_template("teachers.html", teachers=data)

#================ ADD TEACHER ======================
@app.route('/add_teacher', methods=['POST'])
def add_teacher():

    name = request.form['name']
    subject = request.form['subject']
    phone = request.form['phone']
    salary = request.form['salary']

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO teachers (name, subject, phone, salary)
        VALUES (?, ?, ?, ?)
    """, (name, subject, phone, salary))

    conn.commit()
    conn.close()

    return redirect('/teachers')
#================= EDIT TEACHER ==================
@app.route('/edit_teacher/<int:id>', methods=['GET', 'POST'])
def edit_teacher(id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("SELECT * FROM teachers WHERE id=?", (id,))
    teacher = c.fetchone()

    if request.method == 'POST':

        name = request.form['name']
        subject = request.form['subject']
        phone = request.form['phone']
        salary = request.form['salary']

        c.execute("""
            UPDATE teachers
            SET name=?, subject=?, phone=?, salary=?
            WHERE id=?
        """, (name, subject, phone, salary, id))

        conn.commit()
        conn.close()

        return redirect('/teachers')

    conn.close()

    return render_template("edit_teacher.html", teacher=teacher)
#============= DELETE TEACHER ===============
@app.route('/delete_teacher/<int:id>')
def delete_teacher(id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("DELETE FROM teachers WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/teachers')
    

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
@app.route('/test')
def test():
    return "WORKING"
#============== ATTENDANCE PDF =================
from flask import send_file
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
import io
import sqlite3

@app.route('/attendance_pdf')
def attendance_pdf():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        SELECT student_id, student_name, status, date
        FROM attendance
        ORDER BY id DESC
    """)

    data = c.fetchall()
    conn.close()

    # PDF in memory
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer)

    # Table data
    table_data = []
    table_data.append(["ID", "Student", "Status", "Date"])

    for row in data:
        table_data.append(list(row))

    table = Table(table_data)

    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))

    pdf.build([table])

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name="attendance_report.pdf",
        mimetype='application/pdf'
    )
# ================= MARK ATTENDANCE =================

@app.route('/mark_attendance/<int:id>/<status>')
def mark_attendance(id, status):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # Get student
    c.execute("SELECT name FROM students WHERE id=?", (id,))
    student = c.fetchone()

    if student:

        # keep only one record per student
        c.execute("DELETE FROM attendance WHERE student_id=?", (id,))

        # insert new record
        c.execute("""
            INSERT INTO attendance
            (student_id, student_name, status, date)
            VALUES (?, ?, ?, datetime('now'))
        """, (id, student[0], status))

        # update dashboard status
        c.execute("""
            UPDATE students
            SET status=?
            WHERE id=?
        """, (status, id))

        conn.commit()

    conn.close()

    return redirect('/dashboard')
# ================= ATTENDANCE REPORT =================
@app.route('/attendance')
def attendance():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    SELECT student_id, student_name, status, date
    FROM attendance
    ORDER BY id DESC
    """)

    data = c.fetchall()

    conn.close()

    return render_template("attendance.html", data=data)


# ================= PRESENT STUDENTS =================
@app.route('/present_students')
def present_students():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    SELECT * FROM students
    WHERE status='Present'
    """)

    students = c.fetchall()

    conn.close()

    return render_template("present_students.html", students=students)


# ================= ABSENT STUDENTS =================
@app.route('/absent_students')
def absent_students():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    SELECT * FROM students
    WHERE status='Absent'
    """)

    students = c.fetchall()

    conn.close()

    return render_template("absent_students.html", students=students)


# ================= LATE STUDENTS =================
@app.route('/late_students')
def late_students():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    SELECT * FROM students
    WHERE status='Late'
    """)

    students = c.fetchall()

    conn.close()

    return render_template("late_students.html", students=students)


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
