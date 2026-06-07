import sqlite3
from flask import Flask, render_template, request, redirect
from datetime import date

app = Flask(__name__)

# -----------------------------
# INIT DATABASE
# -----------------------------
def init_db():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
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

# -----------------------------
# HOME
# -----------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -----------------------------
# LOGIN
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username == 'admin' and password == '1234':
            return redirect('/dashboard')
        else:
            return "Invalid login"

    return render_template('login.html')

# -----------------------------
# DASHBOARD
# -----------------------------
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("SELECT * FROM students")
    students = c.fetchall()

    conn.close()

    return render_template('dashboard.html', students=students)
#============ STUDENTS =============
@app.route('/students')
def students():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("SELECT * FROM students")
    data = c.fetchall()

    conn.close()

    return render_template('students.html', students=data)
# -----------------------------
# ADD STUDENT
# -----------------------------
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    age = request.form['age']
    fee = request.form['fee']
    paid = request.form['paid']

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO students (name, age, fee, paid)
        VALUES (?, ?, ?, ?)
    """, (name, age, fee, paid))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# -----------------------------
# EDIT STUDENT
# -----------------------------
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        fee = request.form['fee']
        paid = request.form['paid']
        status = request.form.get('status', 'Not Marked')

        c.execute("""
            UPDATE students
            SET name=?, age=?, fee=?, paid=?, status=?
            WHERE id=?
        """, (name, age, fee, paid, status, id))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()

    conn.close()

    return render_template('edit_student.html', student=student)

# -----------------------------
# DELETE STUDENT
# -----------------------------
@app.route('/delete_student/<int:id>')
def delete_student(id):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# -----------------------------
# MARK ATTENDANCE
# -----------------------------
@app.route('/mark_attendance/<int:id>', methods=['POST'])
def mark_attendance(id):
    status = request.form.get('status')

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO attendance (student_id, status, date)
        VALUES (?, ?, ?)
    """, (id, status, str(date.today())))

    # also update student status
    c.execute("""
        UPDATE students SET status=? WHERE id=?
    """, (status, id))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# -----------------------------
# ATTENDANCE REPORT
# -----------------------------
@app.route('/attendance')
def attendance():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("""
        SELECT students.name, attendance.status, attendance.date
        FROM attendance
        JOIN students ON students.id = attendance.student_id
        ORDER BY attendance.id DESC
    """)

    data = c.fetchall()

    conn.close()

    return render_template('attendance.html', data=data)
# -----------------------------
# RUN APP
# -----------------------------
init_db()

if __name__ == '__main__':
    app.run()
