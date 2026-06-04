from flask import Flask, request, redirect
import sqlite3

app = Flask(__name__)

# =========================
# DATABASE SETUP
# =========================
def init_db():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            return redirect("/home")
        else:
            return "<h1>Login Failed</h1>"

    return """
    <h1>Login Page</h1>
    <form method='post'>
        <input name='username' placeholder='Username'><br><br>
        <input name='password' type='password' placeholder='Password'><br><br>
        <button>Login</button>
    </form>
    """

# =========================
# HOME
# =========================
@app.route("/home")
def home():
    return """
    <h1>School System</h1>
    <a href='/add'>Add Student</a><br>
    <a href='/list'>View Students</a>
    """

# =========================
# ADD STUDENT
# =========================
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]

        conn = sqlite3.connect("school.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()
        conn.close()

        return "<h3>Student Added!</h3><a href='/home'>Back</a>"

    return """
    <h2>Add Student</h2>
    <form method='post'>
        <input name='name' placeholder='Student Name'>
        <button>Add</button>
    </form>
    """
#=========== delete student ==========
@app.route("/delete/<int:id>")
def delete_student(id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    return redirect("/list")
# =========================
# LIST STUDENTS
# =========================
@app.route("/list")
def list_students():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()
    conn.close()

    html = "<h2>Students List</h2>"

    if not data:
        html += "<p>No students yet</p>"
    else:
        for row in data:
            html += f"<p>{row[0]}. {row[1]}</p>"

    html += "<br><a href='/home'>Back</a>"
    return html

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run()
