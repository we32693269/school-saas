from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "school_secret"

# ======================
# DATABASE
# ======================
def init_db():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        grade TEXT,
        attendance TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ======================
# USERS
# ======================
USERS = {
    "admin": {"password": "1234", "role": "admin"},
    "teacher": {"password": "1234", "role": "teacher"}
}

# ======================
# LOGIN
# ======================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form.get('username')
        password = request.form.get('password')

        if username in USERS and USERS[username]["password"] == password:
            session['user'] = username
            session['role'] = USERS[username]["role"]
            return redirect('/dashboard')

        return "Invalid login"

    return render_template("login.html")

# ======================
# DASHBOARD
# ======================
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    if "user" not in session:
        return redirect('/login')

    role = session['role']

    # ADD STUDENT
    if request.method == 'POST' and "name" in request.form:

        conn = sqlite3.connect("school.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO students(name, age, grade, attendance)
        VALUES (?, ?, ?, ?)
        """, (
            request.form['name'],
            request.form['age'],
            request.form['grade'],
            "Present"
        ))

        conn.commit()
        conn.close()

    # LOAD STUDENTS
    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html", students=students, role=role)

# ======================
# LOGOUT
# ======================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run(debug=True)
