from flask import Flask, request, redirect
import sqlite3
import os

app = Flask(__name__)

# =========================
# DATABASE INIT
# =========================
def init_db():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        grade TEXT
    )
    """)

    # default admin
    cursor.execute("SELECT * FROM users WHERE username=?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       ("admin", "1234"))

    conn.commit()
    conn.close()

init_db()

# =========================
# LOGIN CHECK
# =========================
def check_user(username, password):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cursor.fetchone()
    conn.close()

    return user

# =========================
# ROUTES
# =========================
@app.route("/")
def home():
    return """
    <h1>🏫 School SaaS Login</h1>
    <form action="/login" method="post">
        Username: <input name="username"><br><br>
        Password: <input name="password" type="password"><br><br>
        <button type="submit">Login</button>
    </form>
    """

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = check_user(username, password)

    if user:
        return redirect("/dashboard")
    else:
        return "❌ Login Failed"

@app.route("/dashboard")
def dashboard():
    return """
    <h1>🏫 Dashboard</h1>

    <form action="/add" method="post">
        Name: <input name="name"><br><br>
        Grade: <input name="grade"><br><br>
        <button>Add Student</button>
    </form>

    <br>
    <a href="/list">View Students</a>
    """

@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    grade = request.form["grade"]

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, grade) VALUES (?, ?)",
        (name, grade)
    )

    conn.commit()
    conn.close()

    return redirect("/list")

@app.route("/list")
def list_students():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, grade FROM students")
    students = cursor.fetchall()

    conn.close()

    output = "<h1>📋 Students List</h1>"

    if not students:
        output += "<p>No students yet</p>"
    else:
        for s in students:
            output += f"<p>{s[0]} - {s[1]}</p>"

    output += "<br><a href='/dashboard'>Back</a>"
    return output

# =========================
# 🔥 DEPLOY READY PART
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
