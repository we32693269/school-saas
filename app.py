from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "school_secret123"

# ================= DATABASE =================
def get_db():
    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    return conn


# ================= INIT DATABASE =================
def init_db():

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    """)

    # STUDENTS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        grade TEXT,
        gender TEXT,
        phone TEXT,
        address TEXT
    )
    """)

    # ATTENDANCE TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        status TEXT,
        attendance_date TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()

# ================= LOGIN =================
@app.route('/', methods=['GET', 'POST'])
def login():

    error = None

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = c.fetchone()

        conn.close()

        if user:

            session['user'] = user['username']
            session['role'] = user['role']

            return redirect('/dashboard')

        else:
            error = "Wrong username or password"

    return render_template("login.html", error=error)

# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():

    error = None

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db()
        c = conn.cursor()

        try:

            c.execute("""
            INSERT INTO users(username,password,role)
            VALUES(?,?,?)
            """, (username, password, role))

            conn.commit()
            conn.close()

            return redirect('/')

        except:

            conn.close()
            error = "User already exists"

    return render_template("register.html", error=error)

# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    c = conn.cursor()

    # TOTAL USERS
    c.execute("SELECT COUNT(*) FROM users")
    users = c.fetchone()[0]

    # TOTAL STUDENTS
    c.execute("SELECT COUNT(*) FROM students")
    students = c.fetchone()[0]

    # PRESENT
    c.execute("""
    SELECT COUNT(*) FROM attendance
    WHERE status='present'
    """)
    present = c.fetchone()[0]

    # ABSENT
    c.execute("""
    SELECT COUNT(*) FROM attendance
    WHERE status='absent'
    """)
    absent = c.fetchone()[0]

    # STUDENT LIST
    c.execute("SELECT * FROM students")
    student_data = c.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        users=users,
        students=students,
        present=present,
        absent=absent,
        student_data=student_data
    )

# ================= ADD STUDENT =================
@app.route('/add_student', methods=['POST'])
def add_student():

    if 'user' not in session:
        return redirect('/')

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    gender = request.form['gender']
    phone = request.form['phone']
    address = request.form['address']

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO students(name,age,grade,gender,phone,address)
    VALUES(?,?,?,?,?,?)
    """, (name, age, grade, gender, phone, address))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ================= EDIT STUDENT =================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        gender = request.form['gender']
        phone = request.form['phone']
        address = request.form['address']

        c.execute("""
        UPDATE students
        SET name=?,
            age=?,
            grade=?,
            gender=?,
            phone=?,
            address=?
        WHERE id=?
        """, (name, age, grade, gender, phone, address, id))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()

    conn.close()

    return render_template("edit.html", student=student)

# ================= DELETE STUDENT =================
@app.route('/delete/<int:id>')
def delete(id):

    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ================= ATTENDANCE =================
@app.route('/attendance/<int:id>/<status>')
def attendance(id, status):

    date = datetime.now().strftime("%Y-%m-%d")

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO attendance(student_id,status,attendance_date)
    VALUES(?,?,?)
    """, (id, status, date))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# ================= REPORT =================
@app.route('/report')
def report():

    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT students.name,
           attendance.status,
           attendance.attendance_date
    FROM attendance
    JOIN students
    ON students.id = attendance.student_id
    ORDER BY attendance.id DESC
    """)

    reports = c.fetchall()

    c.execute("""
    SELECT COUNT(*) FROM attendance
    WHERE status='present'
    """)
    present = c.fetchone()[0]

    c.execute("""
    SELECT COUNT(*) FROM attendance
    WHERE status='absent'
    """)
    absent = c.fetchone()[0]

    conn.close()

    return render_template(
        "report.html",
        reports=reports,
        present=present,
        absent=absent
    )

# ================= PROFILE =================
@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    SELECT * FROM users
    WHERE username=?
    """, (session['user'],))

    user = c.fetchone()

    conn.close()

    return render_template("profile.html", user=user)

# ================= SETTINGS =================
@app.route('/settings')
def settings():

    if 'user' not in session:
        return redirect('/')

    return render_template("settings.html")

# ================= LOGOUT =================
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# ================= RUN APP =================
if __name__ == "__main__":
    app.run(debug=True)
