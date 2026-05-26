from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "school_secret"


# DATABASE
def get_db():
    conn = sqlite3.connect("school.db")
    return conn


# CREATE TABLES
conn = get_db()
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT,
    grade TEXT,
    gender TEXT,
    phone TEXT,
    address TEXT
)
''')

c.execute('''
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    status TEXT
)
''')

conn.commit()
conn.close()


# LOGIN
@app.route('/', methods=['GET', 'POST'])
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

    return render_template('login.html')


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        existing = c.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if existing:
            conn.close()
            return "User already exists"

        c.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('register.html')


# DASHBOARD
@app.route('/dashboard')
def dashboard():

    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    c = conn.cursor()

    students = c.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    total_students = len(students)

    present = c.execute(
        "SELECT * FROM attendance WHERE status='present'"
    ).fetchall()

    absent = c.execute(
        "SELECT * FROM attendance WHERE status='absent'"
    ).fetchall()

    conn.close()

    return render_template(
        'dashboard.html',
        students=students,
        total_students=total_students,
        present=len(present),
        absent=len(absent)
    )


# ADD STUDENT
@app.route('/add_student', methods=['POST'])
def add_student():

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    gender = request.form['gender']
    phone = request.form['phone']
    address = request.form['address']

    conn = get_db()
    c = conn.cursor()

    c.execute(
        '''
        INSERT INTO students
        (name, age, grade, gender, phone, address)
        VALUES (?, ?, ?, ?, ?, ?)
        ''',
        (name, age, grade, gender, phone, address)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# DELETE
@app.route('/delete/<int:id>')
def delete(id):

    conn = get_db()
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# EDIT
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

        c.execute(
            '''
            UPDATE students
            SET name=?, age=?, grade=?, gender=?, phone=?, address=?
            WHERE id=?
            ''',
            (name, age, grade, gender, phone, address, id)
        )

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    student = c.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template('edit.html', student=student)


# ATTENDANCE
@app.route('/attendance/<int:id>/<status>')
def attendance(id, status):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO attendance(student_id, status)
        VALUES (?, ?)
    """, (id, status))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# REPORTS
@app.route('/reports')
def reports():

    conn = get_db()
    c = conn.cursor()

    students = c.execute(
        "SELECT * FROM students"
    ).fetchall()

    attendance = c.execute(
        "SELECT * FROM attendance"
    ).fetchall()

    conn.close()

    return render_template(
        'reports.html',
        students=students,
        attendance=attendance
    )


# PROFILE
@app.route('/profile')
def profile():

    if 'user' not in session:
        return redirect('/')

    return render_template('profile.html')


# SETTINGS
@app.route('/settings')
def settings():

    if 'user' not in session:
        return redirect('/')

    return render_template('settings.html')


# LOGOUT
@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
