from flask import Flask, render_template, request, redirect
import sqlite3
import os
from reportlab.pdfgen import canvas
app = Flask(__name__)

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


# ================= HOME =================
@app.route('/')
def home():
    return redirect('/dashboard')


# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("SELECT * FROM students")
    students = c.fetchall()

    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]

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
        total_balance=total_balance
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
@app.route('/receipt/<int:id>')
def receipt(id):

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()
    conn.close()

    if not student:
        return "Student not found"

    file_name = f"receipt_{id}.pdf"

    pdf = canvas.Canvas(file_name)
    pdf.setFont("Helvetica", 12)

    pdf.drawString(100, 800, "🏫 SCHOOL RECEIPT")
    pdf.drawString(100, 770, f"Name: {student[1]}")
    pdf.drawString(100, 750, f"Age: {student[2]}")
    pdf.drawString(100, 730, f"Grade: {student[3]}")
    pdf.drawString(100, 710, f"Fee: {student[4]}")
    pdf.drawString(100, 690, f"Paid: {student[5]}")
    pdf.drawString(100, 670, f"Balance: {student[4] - student[5]}")
    pdf.drawString(100, 650, f"Status: {student[6]}")

    pdf.save()

    return send_file(file_name, as_attachment=True)

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
