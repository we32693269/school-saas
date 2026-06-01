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
# LOGIN PAGE (UI)
# =========================
@app.route("/")
def home():
    return """
    <html>
    <head>
    <style>
        body { font-family:Arial; background:#f2f2f2; text-align:center; }
        .box { background:white; padding:30px; width:320px; margin:auto; margin-top:100px; border-radius:10px; box-shadow:0 0 15px gray; }
        input { width:90%; padding:10px; margin:5px; }
        button { padding:10px 20px; background:blue; color:white; border:none; border-radius:5px; }
    </style>
    </head>
    <body>

    <div class="box">
        <h2>🏫 School SaaS Login</h2>
        <form action="/login" method="post">
            <input name="username" placeholder="Username"><br>
            <input name="password" type="password" placeholder="Password"><br><br>
            <button type="submit">Login</button>
        </form>
    </div>

    </body>
    </html>
    """

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    user = check_user(username, password)

    if user:
        return redirect("/dashboard")
    else:
        return "<h1>❌ Login Failed</h1><a href='/'>Back</a>"

# =========================
# DASHBOARD (UI)
# =========================
@app.route("/dashboard")
def dashboard():
    return """
    <html>
    <head>
    <style>
        body { font-family:Arial; background:#eef2ff; text-align:center; }
        .card { background:white; padding:25px; width:350px; margin:auto; margin-top:50px; border-radius:10px; box-shadow:0 0 15px gray; }
        input { width:90%; padding:10px; margin:5px; }
        button { padding:10px 20px; background:green; color:white; border:none; border-radius:5px; }
        a { display:block; margin-top:10px; }
    </style>
    </head>
    <body>

    <h1>🏫 Dashboard</h1>

    <div class="card">
        <h3>Add Student</h3>
        <form action="/add" method="post">
            <input name="name" placeholder="Name"><br>
            <input name="grade" placeholder="Grade"><br><br>
            <button type="submit">Add</button>
        </form>

        <a href="/list">📋 View Students</a>
        <a href="/">🚪 Logout</a>
    </div>

    </body>
    </html>
    """

# =========================
# ADD STUDENT
# =========================
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

# =========================
# LIST STUDENTS
# =========================
@app.route("/list")
def list_students():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name, grade FROM students")
    students = cursor.fetchall()

    conn.close()

    output = """
    <html>
    <head>
    <style>
        body { font-family:Arial; background:#f9fafb; text-align:center; }
        .box { background:white; width:400px; margin:auto; margin-top:50px; padding:20px; border-radius:10px; box-shadow:0 0 10px gray; }
    </style>
    </head>
    <body>
    <div class="box">
        <h2>📋 Students List</h2>
    """

    if not students:
        output += "<p>No students yet</p>"
    else:
        for s in students:
            output += f"<p>{s[0]} - {s[1]}</p>"

    output += """
        <br><a href="/dashboard">⬅ Back</a>
    </div>
    </body>
    </html>
    """

    return output

# =========================
# DEPLOY READY
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
