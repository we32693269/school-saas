from flask import Flask, request, redirect

import sqlite3
import os
import stripe

app = Flask(__name__)

# =========================
# STRIPE SETUP
# =========================
stripe.api_key = "sk_test_51TdYS9AreGUdagSrq6ERvY9DSUYfdtqWbVWQKU1e1D5UIZ9o6VH9DIVZW7CxTIBk0IX52hQCR7Sm3reu4kWJPiQY00SCNIQviB"

PUBLIC_KEY = "pk_test_51TdYS9AreGUdagSr8AWr9h9RWdzAFAkDlKttY2cAm6m6QFXatVh3pfb0Bm4szC1C1tW3dnLcz6SZhv77V5gydYUn00aWKvBvdV"

# =========================
# DATABASE
# =========================
def init_db():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT,
        plan TEXT DEFAULT 'free'
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        status TEXT,
        date TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        status TEXT
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
        cursor.execute(
            "INSERT INTO users (username, password, plan) VALUES (?, ?, ?)",
            ("admin", "1234", "premium")
        )

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
# HOME
# =========================
@app.route("/")
def home():
    return """
    <h2>🏫 School SaaS Login</h2>
    <form action="/login" method="post">
        <input name="username" placeholder="Username"><br><br>
        <input name="password" type="password" placeholder="Password"><br><br>
        <button>Login</button>
    </form>
    """

# =========================
# LOGIN
# =========================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["user"] = "admin"
            return redirect("/list")
        else:
            return "❌ Wrong username or password"

    return """
    <h2>🔐 Login</h2>
    <form method="post">
        <input name="username" placeholder="Username"><br><br>
        <input name="password" type="password" placeholder="Password"><br><br>
        <button>Login</button>
    </form>
    """
# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
def dashboard():
    return """
    <h1>🏫 Dashboard</h1>

    <form action="/add" method="post">
        <input name="name" placeholder="Student Name"><br><br>
        <input name="grade" placeholder="Grade"><br><br>
        <button>Add Student</button>
    </form>

    <br>
    <a href="/list">📋 Students</a><br><br>
    <a href="/pay">💳 Upgrade ($5)</a>
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

    cursor.execute("INSERT INTO students (name, grade) VALUES (?, ?)", (name, grade))

    conn.commit()
    conn.close()

    return redirect("/list")
#=============== SEARCH ===============
@app.route("/search")
def search():
    q = request.args.get("q", "")

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, name, grade FROM students WHERE name LIKE ?",
        ('%' + q + '%',)
    )

    data = cursor.fetchall()
    conn.close()

    html = f"<h2>🔍 Search Result: {q}</h2>"

    if not data:
        html += "<p>No student found.</p>"

    for s in data:
        html += f"""
        <p>
            {s[1]} - {s[2]}
            <a href="/edit/{s[0]}">✏️ Edit</a>
            <a href="/delete/{s[0]}">🗑️ Delete</a>
        </p>
        """

    html += "<br><a href='/list'>Back to List</a>"
    return html
#=============== LIST STUDENTS ==================
@app.route("/list")
def list_students():
    if "user" not in session:
    return redirect("/login")
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, grade FROM students")
    data = cursor.fetchall()

    conn.close()

    html = """
    <h2>📋 Students</h2>

    <form action="/search" method="get">
        <input name="q" placeholder="Search student">
        <button type="submit">🔍 Search</button>
    </form>

    <hr>
    """

    for s in data:
        html += f"""
        <p>
            {s[1]} - {s[2]}
            <a href="/edit/{s[0]}">✏️ Edit</a>
            <a href="/delete/{s[0]}">🗑️ Delete</a>
            <a href="/attendance/{s[0]}/Present">✅ Present</a>
            <a href="/attendance/{s[0]}/Absent">❌ Absent</a>
        </p>
        """

    html += "<br><a href='/attendance_report'>📅 Attendance Report</a>"
    html += "<br><a href='/dashboard'>Back</a>"

    return html
#============ ATTENDANCE ==============
from datetime import datetime

@app.route("/attendance/<int:id>/<status>")
def attendance(id, status):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        "INSERT INTO attendance (student_id, status, date) VALUES (?, ?, ?)",
        (id, status, date)
    )

    conn.commit()
    conn.close()

    return redirect("/list")
#=========== ATTENDANCE REPORT ============
@app.route("/attendance_report")
def attendance_report():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT students.name, attendance.status, attendance.date
    FROM attendance
    JOIN students ON students.id = attendance.student_id
    ORDER BY attendance.date DESC
    """)

    records = cursor.fetchall()

    # COUNT
    cursor.execute("""
    SELECT students.name,
    SUM(CASE WHEN attendance.status='Present' THEN 1 ELSE 0 END),
    SUM(CASE WHEN attendance.status='Absent' THEN 1 ELSE 0 END)
    FROM attendance
    JOIN students ON students.id = attendance.student_id
    GROUP BY students.name
    """)

    summary = cursor.fetchall()
    conn.close()

    html = "<h2>📊 Attendance Report (PRO)</h2>"

    html += "<h3>📈 Summary</h3>"
    for s in summary:
        html += f"<p>{s[0]} → ✅ Present: {s[1]} | ❌ Absent: {s[2]}</p>"

    html += "<hr><h3>📅 Details</h3>"

    for r in records:
        html += f"<p>{r[0]} - {r[1]} - {r[2]}</p>"

    html += "<br><a href='/list'>Back</a>"
    return html
#============== EDIT ==============
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        grade = request.form["grade"]

        cursor.execute(
            "UPDATE students SET name=?, grade=? WHERE id=?",
            (name, grade, id)
        )

        conn.commit()
        conn.close()
        return redirect("/list")

    cursor.execute("SELECT name, grade FROM students WHERE id=?", (id,))
    student = cursor.fetchone()
    conn.close()

    return f"""
    <h2>✏️ Edit Student</h2>
    <form method="post">
        <input name="name" value="{student[0]}"><br><br>
        <input name="grade" value="{student[1]}"><br><br>
        <button>Update</button>
    </form>
    """
#============ DELETE ===============
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/list")
# =========================
# STRIPE PAYMENT (FIXED WITH YOUR LINK)
# =========================
@app.route("/pay")
def pay():
    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": "School SaaS Premium"
                },
                "unit_amount": 500,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url="https://school-saas-veqm.onrender.com/success",
        cancel_url="https://school-saas-veqm.onrender.com/cancel",
    )

    return redirect(session.url)

# =========================
# SUCCESS / CANCEL
# =========================
@app.route("/success")
def success():
    return "🎉 Payment Successful! Premium Activated"

@app.route("/cancel")
def cancel():
    return "❌ Payment Cancelled"

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
