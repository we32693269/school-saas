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
@app.route("/login", methods=["POST"])
def login():
    u = request.form["username"]
    p = request.form["password"]

    if check_user(u, p):
        return redirect("/dashboard")
    return "❌ Wrong login"

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
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, grade FROM students")
    data = cursor.fetchall()

    conn.close()

    html = "<h2>📋 Students</h2>"
    <form action="/search" method="get">
    <input name="q" placeholder="Search student">
    <button>Search</button>
</form>
<hr>
    for s in data:
        html += f"""
        <p>
            {s[1]} - {s[2]}
            <a href="/edit/{s[0]}">✏️ Edit</a>
            <a href="/delete/{s[0]}">🗑️ Delete</a>
        </p>
        """

    html += "<br><a href='/dashboard'>Back</a>"
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
