from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "school123"


# =========================
# DATABASE INIT
# =========================
def init_db():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        grade TEXT,
        gender TEXT,
        phone TEXT,
        address TEXT
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

    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


# =========================
# HOME
# =========================
@app.route('/')
def home():
    return redirect('/login')


# =========================
# LOGIN
# =========================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("school.db")
        c = conn.cursor()

        user = c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')

        return "Wrong username/password"

    return render_template("login.html")


# =========================
# REGISTER
# =========================
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect("school.db")
        c = conn.cursor()

        exist = c.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if exist:
            return "User already exists"

        c.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("register.html")

# =========================
# REPORTS
# =========================
@app.route('/reports')
def reports():

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    students = c.execute("SELECT * FROM students").fetchall()

    attendance = c.execute("SELECT * FROM attendance").fetchall()

    conn.close()

    return render_template(
        "reports.html",
        students=students,
        attendance=attendance
    )
# =========================
# DASHBOARD
# =========================
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    students = c.execute("SELECT * FROM students").fetchall()

    present = c.execute(
        "SELECT * FROM attendance WHERE status='present'"
    ).fetchall()

    absent = c.execute(
        "SELECT * FROM attendance WHERE status='absent'"
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        students=students,
        total_students=len(students),
        present=len(present),
        absent=len(absent)
    )


# =========================
# ADD STUDENT
# =========================
@app.route('/add_student', methods=['POST'])
def add_student():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO students(name,age,grade,gender,phone,address)
    VALUES(?,?,?,?,?,?)
    """, (
        request.form['name'],
        request.form['age'],
        request.form['grade'],
        request.form['gender'],
        request.form['phone'],
        request.form['address']
    ))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# =========================
# ATTENDANCE
# =========================
@app.route('/mark/<int:id>/<status>')
def mark(id, status):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
    INSERT INTO attendance(student_id,status,date)
    VALUES(?,?,?)
    """, (
        id,
        status,
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# =========================
# EDIT
# =========================
@app.route('/edit/<int:id>', methods=['GET','POST'])
def edit(id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    if request.method == 'POST':

        c.execute("""
        UPDATE students SET
        name=?, age=?, grade=?, gender=?, phone=?, address=?
        WHERE id=?
        """, (
            request.form['name'],
            request.form['age'],
            request.form['grade'],
            request.form['gender'],
            request.form['phone'],
            request.form['address'],
            id
        ))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    student = c.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template("edit.html", student=student)


# =========================
# DELETE
# =========================
@app.route('/delete/<int:id>')
def delete(id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# =========================
# PROFILE
# =========================
@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect('/login')

    return render_template(
        "profile.html",
        username=session['user']
    )

# =========================
# SETTINGS
# =========================
@app.route('/settings')
def settings():

    if 'user' not in session:
        return redirect('/login')

    return render_template("settings.html")

# =========================
# LOGOUT
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
