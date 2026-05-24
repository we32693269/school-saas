from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

DATABASE = "school.db"

# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# =====================================================
# INIT DATABASE
# =====================================================

def init_db():

    conn = get_db()
    c = conn.cursor()

    # USERS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT,
        created_at TEXT
    )
    ''')

    # STUDENTS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        grade TEXT,
        gender TEXT,
        phone TEXT,
        address TEXT,
        created_at TEXT
    )
    ''')

    # ATTENDANCE TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS attendance(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        status TEXT,
        attendance_date TEXT
    )
    ''')

    # NOTIFICATIONS TABLE
    c.execute('''
    CREATE TABLE IF NOT EXISTS notifications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        message TEXT,
        created_at TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ================= LOGIN =================

@app.route('/', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        c.execute(
            'SELECT * FROM users WHERE username=? AND password=?',
            (username, password)
        )

        user = c.fetchone()

        conn.close()

        # ✅ LOGIN SUCCESS
        if user:

            session['user'] = user['username']
            session['role'] = user['role']

            return redirect('/dashboard')

        else:
            return "Wrong username or password"

    return render_template('login.html')
# REGISTER
# =====================================================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = get_db()
        c = conn.cursor()

        try:

            c.execute('''
            INSERT INTO users(username, password, role, created_at)
            VALUES (?, ?, ?, ?)
            ''', (
                username,
                password,
                role,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ))

            conn.commit()
            flash('Registration successful')

            return redirect('/')

        except:
            flash('Username already exists')

        conn.close()

    return render_template('register.html')

# =====================================================
# DASHBOARD
# =====================================================

@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    c = conn.cursor()

    # ALL STUDENTS
    c.execute('SELECT * FROM students ORDER BY id DESC')
    students = c.fetchall()

    # TOTAL STUDENTS
    c.execute('SELECT COUNT(*) as total FROM students')
    total_students = c.fetchone()['total']

    # TOTAL USERS
    c.execute('SELECT COUNT(*) as total FROM users')
    total_users = c.fetchone()['total']

    # PRESENT COUNT
    c.execute("SELECT COUNT(*) as total FROM attendance WHERE status='present'")
    present_count = c.fetchone()['total']

    # ABSENT COUNT
    c.execute("SELECT COUNT(*) as total FROM attendance WHERE status='absent'")
    absent_count = c.fetchone()['total']

    # ATTENDANCE DATA
    c.execute('''
    SELECT status, COUNT(*) as total
    FROM attendance
    GROUP BY status
    ''')
    attendance_data = c.fetchall()

    # GRADE ANALYSIS
    c.execute('''
    SELECT grade, COUNT(*) as total
    FROM students
    GROUP BY grade
    ''')
    grade_analysis = c.fetchall()

    # RECENT STUDENTS
    c.execute('''
    SELECT * FROM students
    ORDER BY id DESC
    LIMIT 5
    ''')
    recent_students = c.fetchall()

    # AI STYLE INSIGHTS
    ai_message = "System running normally"

    if total_students > 50:
        ai_message = "Large school detected"

    if absent_count > present_count:
        ai_message = "High absence detected"

    conn.close()

    return render_template(
        'dashboard.html',
        students=students,
        total_students=total_students,
        total_users=total_users,
        present_count=present_count,
        absent_count=absent_count,
        attendance_data=attendance_data,
        grade_analysis=grade_analysis,
        recent_students=recent_students,
        ai_message=ai_message,
        user=session['user'],
        role=session['role']
    )

# =====================================================
# ADD STUDENT
# =====================================================

@app.route('/add', methods=['POST'])
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

    c.execute('''
    INSERT INTO students(
        name,
        age,
        grade,
        gender,
        phone,
        address,
        created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        name,
        age,
        grade,
        gender,
        phone,
        address,
        datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    ))

    conn.commit()
    conn.close()

    flash('Student added successfully')

    return redirect('/dashboard')

# =====================================================
# EDIT STUDENT
# =====================================================

@app.route('/edit/<int:id>')
def edit_student(id):

    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    c = conn.cursor()

    c.execute('SELECT * FROM students WHERE id=?', (id,))
    student = c.fetchone()

    conn.close()

    return render_template('edit.html', student=student)

# =====================================================
# UPDATE STUDENT
# =====================================================

@app.route('/update/<int:id>', methods=['POST'])
def update_student(id):

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

    c.execute('''
    UPDATE students
    SET
        name=?,
        age=?,
        grade=?,
        gender=?,
        phone=?,
        address=?
    WHERE id=?
    ''', (
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

    flash('Student updated successfully')

    return redirect('/dashboard')

# =====================================================
# DELETE STUDENT
# =====================================================

@app.route('/delete/<int:id>')
def delete_student(id):

    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    c = conn.cursor()

    c.execute('DELETE FROM students WHERE id=?', (id,))

    conn.commit()
    conn.close()

    flash('Student deleted')

    return redirect('/dashboard')

# =====================================================
# ATTENDANCE
# =====================================================

@app.route('/attendance/<int:student_id>/<status>')
def attendance(student_id, status):

    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    c = conn.cursor()

    c.execute('''
    INSERT INTO attendance(
        student_id,
        status,
        attendance_date
    )
    VALUES (?, ?, ?)
    ''', (
        student_id,
        status,
        datetime.now().strftime('%Y-%m-%d')
    ))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# =====================================================
# REPORTS
# =====================================================
@app.route('/report')
def report():

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM attendance")
    attendance_data = c.fetchall()

    conn.close()

    return render_template('report.html', attendance_data=attendance_data)
# =====================================================
# SEARCH
# =====================================================

@app.route('/search', methods=['POST'])
def search():

    keyword = request.form['keyword']

    conn = get_db()
    c = conn.cursor()

    c.execute('''
    SELECT * FROM students
    WHERE name LIKE ?
    ''', ('%' + keyword + '%',))

    students = c.fetchall()

    conn.close()

    return render_template('dashboard.html', students=students)

# =====================================================
# PROFILE
# =====================================================
@app.route('/profile')
def profile():

    conn = get_db()
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=?",
              (session.get('user'),))

    user = c.fetchone()

    conn.close()

    return render_template('profile.html', user=user)

# =====================================================
# SETTINGS
# =====================================================
@app.route('/settings')
def settings():
    return render_template('settings.html')
# =====================================================
# LOGOUT
# =====================================================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# =====================================================
# MAIN
# =====================================================

if __name__ == '__main__':
    app.run(debug=True)
