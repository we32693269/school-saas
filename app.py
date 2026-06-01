from flask import Flask, request, redirect
import sqlite3
import os
import stripe

app = Flask(__name__)

# =========================
# STRIPE SETUP
# =========================
stripe.api_key = "YOUR_SECRET_KEY"  # 🔴 REPLACE THIS

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
        password TEXT,
        plan TEXT DEFAULT 'free'
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
# HOME (LOGIN PAGE)
# =========================
@app.route("/")
def home():
    return """
    <html>
    <body style="font-family:Arial;text-align:center;background:#f2f2f2;">
        <div style="background:white;width:300px;margin:auto;margin-top:100px;padding:20px;border-radius:10px;">
            <h2>🏫 School SaaS Login</h2>
            <form action="/login" method="post">
                <input name="username" placeholder="Username" style="width:90%;padding:8px;"><br><br>
                <input name="password" type="password" placeholder="Password" style="width:90%;padding:8px;"><br><br>
                <button style="padding:10px;background:blue;color:white;">Login</button>
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
        return "❌ Login Failed"

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
    <a href="/list">📋 View Students</a><br><br>
    <a href="/pay">💳 Upgrade to Premium ($5)</a><br><br>
    <a href="/">Logout</a>
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

    html = "<h1>📋 Students List</h1>"

    if not students:
        html += "<p>No students yet</p>"
    else:
        for s in students:
            html += f"<p>{s[0]} - {s[1]}</p>"

    html += "<br><a href='/dashboard'>Back</a>"
    return html

# =========================
# STRIPE PAYMENT
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
        success_url="https://YOUR-RENDER-LINK.onrender.com/success",
        cancel_url="https://YOUR-RENDER-LINK.onrender.com/cancel",
    )

    return redirect(session.url)

# =========================
# SUCCESS
# =========================
@app.route("/success")
def success():
    return "<h1>🎉 Payment Successful! Premium Activated</h1>"

# =========================
# CANCEL
# =========================
@app.route("/cancel")
def cancel():
    return "<h1>❌ Payment Cancelled</h1>"

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
