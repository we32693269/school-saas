from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "school_secret_key"
# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_tables():
    conn = get_db()
    c = conn.cursor()

    # USERS TABLE
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # STUDENTS TABLE
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

    # ATTENDANCE TABLE
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


create_tables()


# =========================
# HOME
# =========================

@app.route('/')
def home():
    return redirect('/login')


# =========================
# REGISTER
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        user = c.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if user:
            conn.close()
            return "User already exists"

        c.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        user = c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')

        else:
            return "Wrong username or password"

    return render_template('login.html')


# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()

    # ALL STUDENTS
    students = c.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    # TOTAL STUDENTS
    total_students = c.execute(
        "SELECT COUNT(*) as total FROM students"
    ).fetchone()['total']

    # TOTAL USERS
    total_users = c.execute(
        "SELECT COUNT(*) as total FROM users"
    ).fetchone()['total']

    # PRESENT COUNT
    present_count = c.execute(
        "SELECT COUNT(*) as total FROM attendance WHERE status='present'"
    ).fetchone()['total']

    # ABSENT COUNT
    absent_count = c.execute(
        "SELECT COUNT(*) as total FROM attendance WHERE status='absent'"
    ).fetchone()['total']

    conn.close()

    return render_template(
        'dashboard.html',
        students=students,
        total_students=total_students,
        total_users=total_users,
        present=present_count,
        absent=absent_count,
        username=session['user']
    )


# =========================
# ADD STUDENT
# =========================

@app.route('/add_student', methods=['POST'])
def add_student():

    if 'user' not in session:
        return redirect('/login')

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    gender = request.form['gender']
    phone = request.form['phone']
    address = request.form['address']

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO students
    (name, age, grade, gender, phone, address)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (name, age, grade, gender, phone, address))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# EDIT STUDENT
# =========================

@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    if 'user' not in session:
        return redirect('/login')

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
        SET
        name=?,
        age=?,
        grade=?,
        gender=?,
        phone=?,
        address=?
        WHERE id=?
        """, (
            name,
            age,
            grade,
            gender,
            phone,
            address,
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

    return render_template(
        'edit.html',
        student=student
    )


# =========================
# MARK PRESENT
# =========================

@app.route('/present/<int:id>')
def present(id):

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO attendance(student_id, status, date)
    VALUES (?, ?, ?)
    """, (
        id,
        'present',
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# =========================
# MARK ABSENT
# =========================

@app.route('/absent/<int:id>')
def absent(id):

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()

    c.execute("""
    INSERT INTO attendance(student_id, status, date)
    VALUES (?, ?, ?)
    """, (
        id,
        'absent',
        datetime.now().strftime("%Y-%m-%d")
    ))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# =========================
# REPORTS
# =========================

@app.route('/reports')
def reports():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()

    students = c.execute("""
    SELECT * FROM students
    ORDER BY id DESC
    """).fetchall()

    attendance = c.execute("""
    SELECT attendance.id,
           students.name,
           attendance.status,
           attendance.date
    FROM attendance
    JOIN students
    ON attendance.student_id = students.id
    ORDER BY attendance.id DESC
    """).fetchall()

    conn.close()

    return render_template(
        'reports.html',
        students=students,
        attendance=attendance
    )


# =========================
# PROFILE
# =========================

@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect('/login')

    return render_template(
        'profile.html',
        username=session['user']
    )


# =========================
# SETTINGS
# =========================

@app.route('/settings')
def settings():

    if 'user' not in session:
        return redirect('/login')

    return render_template(
        'settings.html'
    )


# =========================
# SEARCH
# =========================

@app.route('/search', methods=['POST'])
def search():

    if 'user' not in session:
        return redirect('/login')

    keyword = request.form['keyword']

    conn = get_db()
    c = conn.cursor()

    students = c.execute("""
    SELECT * FROM students
    WHERE name LIKE ?
    """, ('%' + keyword + '%',)).fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        students=students,
        total_students=len(students),
        total_users=1,
        present=0,
        absent=0,
        username=session['user']
    )


# =========================
# CLEAR ATTENDANCE
# =========================

@app.route('/clear_attendance')
def clear_attendance():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM attendance")

    conn.commit()
    conn.close()

    return redirect('/reports')


# =========================
# RESET DATABASE
# =========================

@app.route('/reset_database')
def reset_database():

    if 'user' not in session:
        return redirect('/login')

    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM students")
    c.execute("DELETE FROM attendance")

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# =========================
# ABOUT PAGE
# =========================

@app.route('/about')
def about():

    return """
    <h1>School SaaS System</h1>
    <p>Fully Working Flask + SQLite Project</p>
    """


# =========================
# CONTACT PAGE
# =========================

@app.route('/contact')
def contact():

    return """
    <h1>Contact</h1>
    <p>Email: school@gmail.com</p>
    """


# =========================
# TEST DATABASE
# =========================

@app.route('/test_db')
def test_db():

    conn = get_db()
    c = conn.cursor()

    users = c.execute(
        "SELECT COUNT(*) as total FROM users"
    ).fetchone()['total']

    students = c.execute(
        "SELECT COUNT(*) as total FROM students"
    ).fetchone()['total']

    attendance = c.execute(
        "SELECT COUNT(*) as total FROM attendance"
    ).fetchone()['total']

    conn.close()

    return f"""
    <h1>Database Working</h1>

    <p>Users: {users}</p>

    <p>Students: {students}</p>

    <p>Attendance: {attendance}</p>
    """

# =========================
# DELETE STUDENT
# =========================
@app.route('/delete_users')
def delete_users():
if 'user' not in session:
return redirect('/login')  conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM users")

    conn.commit()
    conn.close()

    return "All users deleted"
# =========================
# RUN APP
# =========================

if __name__ == '__main__':
    app.run(debug=True)
