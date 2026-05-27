from flask import Flask, render_template, request, redirect, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "secret"

# PHOTO UPLOAD
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# DATABASE
def get_db():
    conn = sqlite3.connect("school.db")
    return conn


# CREATE TABLES
conn = get_db()
c = conn.cursor()

# USERS
c.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# STUDENTS
c.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT,
    grade TEXT,
    photo TEXT
)
""")

# ATTENDANCE
c.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    status TEXT
)
""")

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

    return render_template("login.html")


# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        c = conn.cursor()

        c.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect('/')

    return render_template("register.html")


# DASHBOARD
@app.route('/dashboard')
def dashboard():

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
        "dashboard.html",
        students=students,
        attendance=attendance
    )


# ADD STUDENT
@app.route('/add_student', methods=['POST'])
def add_student():

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']

    photo = request.files['photo']

filename = ""

if photo and photo.filename != "":

    filename = secure_filename(photo.filename)

    photo.save(
        os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )
    )  filename = secure_filename(photo.filename)

    photo.save(
        os.path.join(
            app.config['UPLOAD_FOLDER'],
            filename
        )
    )

    conn = get_db()
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO students(name, age, grade, photo)
        VALUES(?,?,?,?)
        """,
        (name, age, grade, filename)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ATTENDANCE
@app.route('/attendance/<int:id>/<status>')
def attendance(id, status):

    conn = get_db()
    c = conn.cursor()

    c.execute(
        "INSERT INTO attendance(student_id,status) VALUES(?,?)",
        (id, status)
    )

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
        "reports.html",
        students=students,
        attendance=attendance
    )


# EDIT STUDENT
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    conn = get_db()
    c = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']

        c.execute(
            """
            UPDATE students
            SET name=?, age=?, grade=?
            WHERE id=?
            """,
            (name, age, grade, id)
        )

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    student = c.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template(
        "edit.html",
        student=student
    )


# DELETE STUDENT
@app.route('/delete/<int:id>')
def delete(id):

    conn = get_db()
    c = conn.cursor()

    c.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# PROFILE
@app.route('/profile')
def profile():
    return render_template("profile.html")


# SETTINGS
@app.route('/settings')
def settings():
    return render_template("settings.html")


# LOGOUT
@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')


if __name__ == '__main__':

    os.makedirs('static/uploads', exist_ok=True)

    app.run(debug=True)
