from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "school_secret"

# Create database and table
def init_db():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age TEXT,
        grade TEXT,
        attendance TEXT
    )
    """)

    conn.commit()
    conn.close()

# Run database setup
init_db()

# Users
USERS = {
    "admin": {"password": "1234", "role": "admin"},
    "teacher": {"password": "1234", "role": "teacher"},
    "student": {"password": "1234", "role": "student"}
}
#---------------- HOME ----------------
@app.route('/')
def home():
    if "user" in session:
        return redirect('/dashboard')
    return redirect('/login')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        if u in USERS and USERS[u]['password'] == p:
            session['user'] = u
            session['role'] = USERS[u]['role']
            return redirect('/dashboard')

        return "❌ Wrong login"

    return render_template('login.html')

# ---------------- DASHBOARD ----------------
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

    return render_template(
        "dashboard.html",
        students=students,
        role=role
    )
#================ EDIT ================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    if "user" not in session:
        return redirect('/login')

    student = None

    for s in students:
        if s["id"] == id:
            student = s
            break

    if request.method == 'POST':
        if student:
            student["name"] = request.form['name']
            student["age"] = request.form['age']
            student["grade"] = request.form['grade']
            student["attendance"] = request.form['attendance']

        return redirect('/dashboard')

    return render_template("edit.html", student=student)

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    if "user" in session and session['role'] == "admin":
        global students
        students = [s for s in students if s["id"] != id]

    return redirect('/dashboard')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
