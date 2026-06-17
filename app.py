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

    # ================= TEACHERS =================
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
    CREATE TABLE IF NOT EXISTS teacher_attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        teacher_id INTEGER,
        teacher_name TEXT,
        status TEXT,
        date TEXT
   )
   """)
    c.execute("""
    CREATE TABLE IF NOT EXISTS exams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        exam_name TEXT,
        score REAL,
        total REAL,
        grade TEXT,
        gpa REAL
   )
   """)
    # ================= USERS =================
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

    # ================= ATTENDANCE =================
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        student_name TEXT,
        status TEXT,
        date TEXT
    )
    """)

    # ================= DEFAULT USERS =================
    c.execute("""
    INSERT OR IGNORE INTO users
    (username, password, role)
    VALUES ('admin', '1234', 'admin')
    """)

    c.execute("""
    INSERT OR IGNORE INTO users
    (username, password, role)
    VALUES ('teacher1', '1234', 'teacher')
    """)

    c.execute("""
    INSERT OR IGNORE INTO users
    (username, password, role)
    VALUES ('student1', '1234', 'student')
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

    # ================= DEFAULT SETTINGS =================
    c.execute("""
    INSERT OR IGNORE INTO settings
    (id, school_name, logo, default_fee, admin_password,
     academic_year, phone, email, email_password,
     sms_api_key, footer_message)
    VALUES
    (1, 'MY SCHOOL', 'static/logo.png', 0, '1234',
     '2025/2026', '', '', '', '', '')
    """)

    conn.commit()
    conn.close()

init_db()
#=========== BACKUP =========
import shutil

@app.route('/backup')
def backup():

    backup_file = "school_backup.db"

    shutil.copy(
        "school.db",
        backup_file
    )

    return send_file(
        backup_file,
        as_attachment=True
    )
#============ RESTORE =============
from flask import request
import shutil

@app.route('/restore', methods=['POST'])
def restore():

    file = request.files['dbfile']

    file.save("restore.db")

    shutil.copy(
        "restore.db",
        "school.db"
    )

    return redirect('/dashboard')
#========= RESTORE PAGE =========
@app.route('/restore_page')
def restore_page():
    return render_template("restore.html")
#============= login ==============
@app.route('/login', methods=['GET', 'POST'])
def login():

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

            if user[0] == "admin":
                return redirect('/dashboard')
            elif user[0] == "teacher":
                return redirect('/teacher_dashboard')
            else:
                return redirect('/student_dashboard')

        return "Invalid login ❌"

    return render_template("login.html")
#=============== LOGOUT ==================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')
# ================= HOME =================
@app.route('/')
def home():
    return redirect('/dashboard')
#============ ID CARD ==========
@app.route('/id_card/<int:id>')
def id_card(id):

    pdf_file = f"id_card_{id}.pdf"

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    s = c.fetchone()

    conn.close()

    pdf = canvas.Canvas(pdf_file)

    pdf.rect(50,600,300,150)

    pdf.setFont("Helvetica-Bold",16)

    pdf.drawString(
        100,
        720,
        "STUDENT ID CARD"
    )

    pdf.setFont("Helvetica",12)

    pdf.drawString(
        70,
        680,
        f"ID: {s[0]}"
    )

    pdf.drawString(
        70,
        650,
        f"Name: {s[1]}"
    )

    pdf.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )
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
    if session.get('role') != 'admin':
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
#============ REPORT CARD ==============
@app.route('/report_card/<int:id>')
def report_card(id):

    pdf_file = f"report_card_{id}.pdf"

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()

    c.execute("""
    SELECT subject, exam_name, score, total, grade
    FROM exams
    WHERE student_id=?
    """, (id,))

    exams = c.fetchall()

    pdf = canvas.Canvas(pdf_file)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(180, 800, "Student Report Card")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, 760, f"Student: {student[1]}")

    y = 720

    for e in exams:

        pdf.drawString(
            50,
            y,
            f"{e[0]} | {e[1]} | {e[2]}/{e[3]} | Grade:{e[4]}"
        )

        y -= 20

    pdf.save()

    conn.close()

    return send_file(
        pdf_file,
        as_attachment=True
    )
#========== STUDENT EXAMS ==============
@app.route('/student_exams/<int:id>')
def student_exams(id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # Student info
    c.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )
    student = c.fetchone()

    # Exams
    c.execute("""
    SELECT *
    FROM exams
    WHERE student_id=?
    """, (id,))

    exams = c.fetchall()

    # Average GPA
    c.execute("""
    SELECT AVG(gpa)
    FROM exams
    WHERE student_id=?
    """, (id,))

    avg_gpa = c.fetchone()[0] or 0

    conn.close()

    return render_template(
        "student_exams.html",
        student=student,
        exams=exams,
        avg_gpa=avg_gpa
    )
#=============== STUDENTS PDF =============
@app.route('/students_pdf')
def students_pdf():

    pdf_file = "students_report.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, 800, "Students Report")

    conn = sqlite3.connect("school.db")
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    students = cur.fetchall()

    y = 760

    for s in students:

        c.setFont("Helvetica", 10)

        c.drawString(
            50,
            y,
            f"ID:{s[0]}  Name:{s[1]}"
        )

        y -= 20

        if y < 50:
            c.showPage()
            y = 800

    conn.close()

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )
#=============== EDIT EXAM ===============
@app.route('/edit_exam/<int:exam_id>', methods=['GET', 'POST'])
def edit_exam(exam_id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    if request.method == 'POST':

        subject = request.form['subject']
        exam_name = request.form['exam_name']
        score = float(request.form['score'])
        total = float(request.form['total'])

        if score > total:
            return "❌ Score cannot be greater than Total"

        percent = (score / total) * 100

        if percent >= 90:
            grade = "A+"
            gpa = 4.0
        elif percent >= 80:
            grade = "A"
            gpa = 3.5
        elif percent >= 70:
            grade = "B"
            gpa = 3.0
        elif percent >= 60:
            grade = "C"
            gpa = 2.5
        elif percent >= 50:
            grade = "D"
            gpa = 2.0
        else:
            grade = "F"
            gpa = 0.0

        c.execute("""
        UPDATE exams
        SET subject=?,
            exam_name=?,
            score=?,
            total=?,
            grade=?,
            gpa=?
        WHERE id=?
        """, (
            subject,
            exam_name,
            score,
            total,
            grade,
            gpa,
            exam_id
        ))

        conn.commit()

        c.execute(
            "SELECT student_id FROM exams WHERE id=?",
            (exam_id,)
        )

        student_id = c.fetchone()[0]

        conn.close()

        return redirect(f'/student_exams/{student_id}')

    c.execute("SELECT * FROM exams WHERE id=?", (exam_id,))
    exam = c.fetchone()

    conn.close()

    return render_template(
        "edit_exam.html",
        exam=exam
    )
#============== DELETE ===============
@app.route('/delete_exam/<int:exam_id>/<int:student_id>')
def delete_exam(exam_id, student_id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("DELETE FROM exams WHERE id=?", (exam_id,))

    conn.commit()
    conn.close()

    return redirect(f'/student_exams/{student_id}')

#============ ADD EXAM ==============
@app.route('/add_exam/<int:id>', methods=['POST'])
def add_exam(id):

    subject = request.form['subject']
    exam_name = request.form['exam_name']
    score = float(request.form['score'])
    total = float(request.form['total'])

    # Validation
    if total <= 0:
        return "❌ Total marks must be greater than 0"

    if score > total:
        return "❌ Score cannot be greater than Total Marks"

    percent = (score / total) * 100

    # Grade + GPA
    if percent >= 90:
        grade = "A+"
        gpa = 4.0
    elif percent >= 80:
        grade = "A"
        gpa = 3.5
    elif percent >= 70:
        grade = "B"
        gpa = 3.0
    elif percent >= 60:
        grade = "C"
        gpa = 2.5
    elif percent >= 50:
        grade = "D"
        gpa = 2.0
    else:
        grade = "F"
        gpa = 0.0

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO exams
    (student_id, subject, exam_name, score, total, grade, gpa)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        id,
        subject,
        exam_name,
        score,
        total,
        grade,
        gpa
    ))

    conn.commit()
    conn.close()

    return redirect(f'/student_exams/{id}')
#============= RANKING PDF ==============
@app.route('/ranking_pdf')
def ranking_pdf():

    pdf_file = "ranking.pdf"

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    SELECT students.name,
           AVG(exams.gpa)
    FROM students
    JOIN exams
    ON students.id=exams.student_id
    GROUP BY students.id
    ORDER BY AVG(exams.gpa) DESC
    """)

    rows = c.fetchall()

    pdf = canvas.Canvas(pdf_file)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(180, 800, "Student Ranking")

    y = 760
    rank = 1

    for r in rows:

        pdf.drawString(
            50,
            y,
            f"{rank}. {r[0]} GPA={round(r[1],2)}"
        )

        y -= 25
        rank += 1

    pdf.save()

    conn.close()

    return send_file(
        pdf_file,
        as_attachment=True
    )
#============== RANKING ===================
@app.route('/ranking')
def ranking():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # safe query (no crash)
    c.execute("""
    SELECT student_id, AVG(gpa)
    FROM exams
    GROUP BY student_id
    ORDER BY AVG(gpa) DESC
    """)

    rows = c.fetchall()

    result = []

    for r in rows:

        student_id = r[0]
        avg_gpa = r[1] or 0

        c.execute("SELECT name FROM students WHERE id=?", (student_id,))
        student = c.fetchone()

        if student:
            result.append({
                "name": student[0],
                "gpa": round(avg_gpa, 2)
            })

    conn.close()

    return render_template("ranking.html", students=result)
#=============== TEACHER DASHBOARD =================
@app.route('/teacher_dashboard')
def teacher_dashboard():

    if session.get('role') != 'teacher':
        return redirect('/login')

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # Teacher info (for demo teacher1)
    c.execute("SELECT * FROM teachers LIMIT 1")
    teacher = c.fetchone()

    # Students summary
    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM students WHERE status='Present'")
    present = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM students WHERE status='Absent'")
    absent = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM students WHERE status='Late'")
    late = c.fetchone()[0]

    conn.close()

    return render_template(
        "teacher_dashboard.html",
        teacher=teacher,
        total_students=total_students,
        present=present,
        absent=absent,
        late=late
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
#=========== TEACHER ATTENDANCE =================
@app.route('/mark_teacher_attendance/<int:id>/<status>')
def mark_teacher_attendance(id, status):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # get teacher
    c.execute("SELECT name FROM teachers WHERE id=?", (id,))
    teacher = c.fetchone()

    if teacher:

        # remove old record for today (optional)
        c.execute("""
        DELETE FROM teacher_attendance
        WHERE teacher_id=? AND date=date('now')
        """, (id,))

        # insert new record
        c.execute("""
        INSERT INTO teacher_attendance
        (teacher_id, teacher_name, status, date)
        VALUES (?, ?, ?, date('now'))
        """, (id, teacher[0], status))

        conn.commit()

    conn.close()

    return redirect('/teachers')
#============== TEACHERS PDF ===============
@app.route('/teachers_pdf')
def teachers_pdf():

    pdf_file = "teachers_report.pdf"

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("SELECT * FROM teachers")
    teachers = c.fetchall()

    pdf = canvas.Canvas(pdf_file)

    pdf.setFont("Helvetica-Bold",18)
    pdf.drawString(180,800,"Teachers Report")

    y = 760

    for t in teachers:

        pdf.drawString(
            50,
            y,
            f"{t[1]} | {t[2]} | {t[3]}"
        )

        y -= 20

    pdf.save()

    conn.close()

    return send_file(
        pdf_file,
        as_attachment=True
    )
#========== TEACHER ATTENDANCE REPORT ==============
@app.route('/teacher_attendance_report')
def teacher_attendance_report():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    SELECT teacher_name, status, date
    FROM teacher_attendance
    ORDER BY id DESC
    """)

    data = c.fetchall()
    conn.close()

    return render_template("teacher_attendance.html", data=data)

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
# ================= STUDENT DASHBOARD =================
@app.route('/student_dashboard')
def student_dashboard():

    if session.get('role') != 'student':
        return redirect('/login')

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # ለጊዜው student1 እንደ ተማሪ እንወስዳለን
    c.execute("SELECT * FROM students LIMIT 1")
    student = c.fetchone()

    conn.close()

    if not student:
        return "No student found"

    return render_template(
        "student_dashboard.html",
        student_name=student[1],
        grade=student[3],
        paid=student[5],
        balance=student[4] - student[5]
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
#===========  RECEIPT PDF ==============
@app.route('/receipt_pdf/<int:id>')
def receipt_pdf(id):

    pdf_file = f"receipt_{id}.pdf"

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    s = c.fetchone()

    pdf = canvas.Canvas(pdf_file)

    pdf.setFont("Helvetica-Bold",18)
    pdf.drawString(180,800,"Fee Receipt")

    pdf.drawString(50,740,f"Student: {s[1]}")
    pdf.drawString(50,710,f"ID: {s[0]}")

    pdf.save()

    conn.close()

    return send_file(
        pdf_file,
        as_attachment=True
    )
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
