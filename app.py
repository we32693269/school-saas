from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # users
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        role TEXT
    )
    """)

    # students
    c.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        age TEXT,
        grade TEXT
    )
    """)

    # attendance
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        date TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("school.db")
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and user[2] == password:
            session["user"] = user[1]
            session["role"] = user[3]
            return redirect("/dashboard")

        return "Invalid login"

    return render_template("login.html")


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]

        conn = sqlite3.connect("school.db")
        c = conn.cursor()

        c.execute("INSERT INTO users(username,password,role) VALUES (?,?,?)",
                  (username, password, role))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # 📌 students
    c.execute("SELECT * FROM students")
    students = c.fetchall()

    # 📌 total students
    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]

    # 📌 attendance DATA (IMPORTANT FIX)
    c.execute("""
        SELECT status, COUNT(*) 
        FROM attendance 
        GROUP BY status
    """)
    attendance_data = c.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        students=students,
        total_students=total_students,
        attendance_data=attendance_data,
        role=session.get("role"),
        user=session.get("user")
    )


# ================= ADD STUDENT =================
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    age = request.form["age"]
    grade = request.form["grade"]

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("INSERT INTO students(name,age,grade) VALUES (?,?,?)",
              (name, age, grade))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ================= DELETE =================
@app.route("/delete/<int:id>")
def delete(id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ================= EDIT =================
@app.route("/edit/<int:id>")
def edit(id):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()

    conn.close()

    return render_template("edit.html", student=student)


# ================= UPDATE =================
@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    name = request.form["name"]
    age = request.form["age"]
    grade = request.form["grade"]

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        UPDATE students 
        SET name=?, age=?, grade=? 
        WHERE id=?
    """, (name, age, grade, id))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ================= ATTENDANCE =================
@app.route("/attendance/<int:student_id>/<status>")
def attendance(student_id, status):

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("""
        INSERT INTO attendance(student_id, date, status)
        VALUES (?, datetime('now'), ?)
    """, (student_id, status))

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
