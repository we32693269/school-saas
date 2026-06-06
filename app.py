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

    # 👇 add photo column safely
    try:
        cursor.execute("ALTER TABLE students ADD COLUMN photo TEXT")
    except:
        pass

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

    total_students = len(students)

    present_count = sum(
        1 for s in students
        if s["attendance"] == "Present"
    )

    absent_count = sum(
        1 for s in students
        if s["attendance"] == "Absent"
    )

    conn.close()

    return render_template(
        "dashboard.html",
        students=students,
        role=role,
        total_students=total_students,
        present_count=present_count,
        absent_count=absent_count
    )
#============== SEARCH =================
@app.route('/search', methods=['GET', 'POST'])
def search():

    if "user" not in session:
        return redirect('/login')

    role = session['role']
    students = []

    if request.method == 'POST':
        keyword = request.form['keyword']

        conn = sqlite3.connect("school.db")
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM students
        WHERE name LIKE ?
        """, ('%' + keyword + '%',))

        students = cursor.fetchall()
        conn.close()

    return render_template("search.html", students=students, role=role)  
#============= LIVE-SEARCH =================
@app.route('/live-search')
def live_search():

    if "user" not in session:
        return redirect('/login')

    keyword = request.args.get('q', '')

    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
    SELECT * FROM students
    WHERE name LIKE ?
    """, ('%' + keyword + '%',))

    students = cursor.fetchall()
    conn.close()

    results = ""

    for s in students:
        results += f"""
        <tr>
            <td>{s['id']}</td>
            <td>{s['name']}</td>
            <td>{s['age']}</td>
            <td>{s['grade']}</td>
            <td>{s['attendance']}</td>
        </tr>
        """

    return results
#================ EDIT ================
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    if "user" not in session:
        return redirect('/login')

    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if request.method == 'POST':

        cursor.execute("""
        UPDATE students
        SET name=?, age=?, grade=?, attendance=?
        WHERE id=?
        """, (
            request.form['name'],
            request.form['age'],
            request.form['grade'],
            request.form['attendance'],
            id
        ))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()

    conn.close()

    return render_template(
        "edit.html",
        student=student
    )

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):

    if "user" not in session:
        return redirect('/login')

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
