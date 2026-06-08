import sqlite3
from flask import Flask, render_template, request, redirect
from datetime import date

app = Flask(__name__)

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        grade TEXT,
        fee INTEGER DEFAULT 0,
        paid INTEGER DEFAULT 0,
        status TEXT DEFAULT 'Not Marked'
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

    conn.commit()
    conn.close()

init_db()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            return redirect('/dashboard')
        return "Wrong login"
    return render_template('login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    # 👨‍🎓 STUDENTS
    c.execute("SELECT * FROM students")
    students = c.fetchall()

    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]

    # 💰 FINANCE
    c.execute("SELECT SUM(fee) FROM students")
    total_fee = c.fetchone()[0] or 0

    c.execute("SELECT SUM(paid) FROM students")
    total_paid = c.fetchone()[0] or 0

    total_balance = total_fee - total_paid

    # 📊 ATTENDANCE
    c.execute("SELECT COUNT(*) FROM attendance WHERE status='Present'")
    present_students = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM attendance WHERE status='Absent'")
    absent_students = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM attendance WHERE status='Late'")
    late_students = c.fetchone()[0]

    conn.close()

    return render_template(
        'dashboard.html',
        students=students,
        total_students=total_students,
        total_fee=total_fee,
        total_paid=total_paid,
        total_balance=total_balance,
        present_students=present_students,
        absent_students=absent_students,
        late_students=late_students
    )
# ---------------- ADD STUDENT ----------------
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    fee = request.form['fee']
    paid = request.form['paid']

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO students
        (name, age, grade, fee, paid)
        VALUES (?, ?, ?, ?, ?)
    """, (name, age, grade, fee, paid))

    conn.commit()
    conn.close()

    return redirect('/dashboard')
#========== RECEIPT =============
@app.route('/receipt/<int:id>')
def receipt(id):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()

    conn.close()

    return render_template('receipt.html', student=student)
#============ PDF ================
from reportlab.pdfgen import canvas
from flask import send_file
import sqlite3
import datetime

@app.route('/receipt/pdf/<int:id>')
def receipt_pdf(id):

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    s = c.fetchone()
    conn.close()

    # ❗ SAFE CHECK
    if not s:
        return "Student not found"

    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    file_path = f"receipt_{id}.pdf"

    pdf = canvas.Canvas(file_path)

    # 🏫 LOGO (FIXED)
    logo_path = "logo.jpg"
    try:
        pdf.drawImage(logo_path, 50, 760, width=60, height=60)
    except:
        pass  # ignore logo error

    # 🏫 HEADER
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(120, 800, "Bright Future School")

    pdf.setFont("Helvetica", 10)
    pdf.drawString(120, 780, "📞 09xxxxxxxx | 📍 Addis Ababa")

    pdf.line(50, 750, 550, 750)

    # 🧾 INFO
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 720, f"Receipt No: R-{id:04d}")
    pdf.drawString(350, 720, f"Date: {date}")

    pdf.line(50, 710, 550, 710)

    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, 680, f"Name: {s[1]}")
    pdf.drawString(50, 660, f"Age: {s[2]}")
    pdf.drawString(50, 640, f"Grade: {s[3]}")

    pdf.line(50, 630, 550, 630)

    pdf.drawString(50, 600, f"Total Fee: {s[4]}")
    pdf.drawString(50, 580, f"Paid: {s[5]}")
    pdf.drawString(50, 560, f"Balance: {s[4]-s[5]}")

    pdf.line(50, 540, 550, 540)

    pdf.drawString(200, 500, "Thank you 🙏")

    pdf.save()

    return send_file(file_path, as_attachment=True)
# ---------------- EDIT STUDENT ----------------
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    if request.method == 'POST':
        try:
            name = request.form.get('name')
            age = request.form.get('age')
            grade = request.form.get('grade')
            fee = request.form.get('fee')
            paid = request.form.get('paid')

            if not name:
                return "Name is required"

            c.execute("""
                UPDATE students
                SET name=?, age=?, grade=?, fee=?, paid=?
                WHERE id=?
            """, (name, age, grade, fee, paid, id))

            conn.commit()
            conn.close()

            return redirect('/dashboard')

        except Exception as e:
            return f"Error: {str(e)}"

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()
    conn.close()

    return render_template('edit.html', student=student)

# ---------------- DELETE ----------------
@app.route('/delete_student/<int:id>')
def delete_student(id):
    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ---------------- MARK ATTENDANCE ----------------
@app.route('/mark_attendance/<int:id>', methods=['POST'])
def mark_attendance(id):
    status = request.form['status']
    today = str(date.today())

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("""
        SELECT id
        FROM attendance
        WHERE student_id=? AND date=?
    """, (id, today))

    existing = c.fetchone()

    if existing:
        c.execute("""
            UPDATE attendance
            SET status=?
            WHERE student_id=? AND date=?
        """, (status, id, today))
    else:
        c.execute("""
            INSERT INTO attendance(student_id, status, date)
            VALUES(?, ?, ?)
        """, (id, status, today))

    c.execute(
        "UPDATE students SET status=? WHERE id=?",
        (status, id)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ---------------- ATTENDANCE REPORT ----------------
@app.route('/attendance')
def attendance():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    SELECT attendance.id, students.name, attendance.status, attendance.date
    FROM attendance
    JOIN students ON students.id = attendance.student_id
    ORDER BY attendance.id DESC
    """)

    data = c.fetchall()

    conn.close()
    return render_template('attendance.html', data=data)

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
