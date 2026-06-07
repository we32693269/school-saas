import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# -----------------------------
# DATABASE INIT
# -----------------------------
import os
import sqlite3

if os.path.exists("school.db"):
    os.remove("school.db")

def init_db():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age INTEGER,
        fee INTEGER DEFAULT 0,
        paid INTEGER DEFAULT 0
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        status TEXT,
        date TEXT
    )
    ''')

    conn.commit()
    conn.close()

# -----------------------------
# HOME PAGE
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
        email = request.form['email']
        password = request.form['password']

        if email == "admin@gmail.com" and password == "1234":
            return redirect('/dashboard')

        return "Invalid login ❌"

    return render_template('login.html')

# -----------------------------
# DASHBOARD (SHOW STUDENTS)
# -----------------------------
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()

    return render_template('dashboard.html', students=students)

# -----------------------------
# ADD STUDENT
# -----------------------------
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    age = request.form['age']
    fee = int(request.form['fee'])
    paid = int(request.form['paid'])

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO students (name, age, fee, paid) VALUES (?, ?, ?, ?)",
        (name, age, fee, paid)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')
#============== EDIT STUDENT ==============
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        fee = request.form['fee']
        paid = request.form['paid']

        c.execute("""
            UPDATE students 
            SET name=?, age=?, fee=?, paid=? 
            WHERE id=?
        """, (name, age, fee, paid, id))

        conn.commit()
        conn.close()
        return redirect('/dashboard')

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()
    conn.close()

    return render_template('edit_student.html', student=student)
#============ DELETE STUDENT ===============
@app.route('/delete_student/<int:id>')
def delete_student(id):
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect('/dashboard')
# -----------------------------
# RUN APP
# -----------------------------
if __name__ == '__main__':
    app.run()
