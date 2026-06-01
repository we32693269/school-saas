from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DB =================
def get_db():
    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    return conn


# ================= CREATE TABLES =================
conn = get_db()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT DEFAULT 'user'
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT,
    grade TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER,
    amount TEXT,
    status TEXT,
    date TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    status TEXT,
    date TEXT
)
""")

conn.commit()
conn.close()


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user"] = user["username"]
            session["role"] = user["role"]
            return redirect("/dashboard")

        return "Invalid Login"

    return render_template("login.html")


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    return render_template("dashboard.html")


# ================= FEES (ADMIN ONLY) =================
@app.route("/fees", methods=["GET", "POST"])
def fees():

    if "user" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        return "Access Denied (Admin Only)"

    conn = get_db()

    students = conn.execute("SELECT * FROM students").fetchall()

    if request.method == "POST":

        student_id = request.form["student_id"]
        amount = request.form["amount"]
        status = request.form["status"]
        date = request.form["date"]

        conn.execute("""
            INSERT INTO fees (student_id, amount, status, date)
            VALUES (?, ?, ?, ?)
        """, (student_id, amount, status, date))

        conn.commit()

    fees = conn.execute("""
        SELECT fees.id, students.name, fees.amount, fees.status, fees.date
        FROM fees
        JOIN students ON students.id = fees.student_id
        ORDER BY fees.id DESC
    """).fetchall()

    conn.close()

    return render_template("fees.html", fees=fees, students=students)


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
