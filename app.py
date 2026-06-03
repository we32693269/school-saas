from flask import Flask, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "school_secret_key"
import stripe
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
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        grade TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        subject TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        student_name TEXT,
        amount REAL,
        status TEXT,
        payment_date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        score INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT,
        amount REAL,
        status TEXT,
        payment_date TEXT
    )
    """)

    cursor.execute(
        "SELECT * FROM users WHERE username=?",
        ("admin",)
    )

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
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    students = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teachers")
    teachers = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attendance")
    attendance = cursor.fetchone()[0]

    conn.close()

    return f"""
    <h1>🏫 School Management Dashboard</h1>

    <hr>

    <h2>📊 Overview</h2>

    <div style="display:flex; gap:20px;">
        <div>👨‍🎓 Students: {students}</div>
        <div>👨‍🏫 Teachers: {teachers}</div>
        <div>📅 Attendance Records: {attendance}</div>
    </div>

    <hr>

    <h2>📌 Menu</h2>

    <p><a href="/list">👨‍🎓 Students</a></p>
    <p><a href="/teachers">👨‍🏫 Teachers</a></p>
    <p><a href="/attendance_report">📅 Attendance</a></p>
    <p><a href="/ranking">🏆 rank</a></p>
    <p><a href="/payments">💳 Payments Report</a></p>
    <p><a href="/payment">💰 Payment System</a></p>
    <p><a href="/fee_status">💰 Fee Status</a></p>
   <hr>

    <p><a href="/logout">🚪 Logout</a></p>
    """
#============== FEE STATUS ============
@app.route("/fee_status")
def fee_status():

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()

    html = "<h2>💰 Fee Status Report</h2>"

    for student in students:

        cursor.execute(
            "SELECT COUNT(*) FROM payments WHERE student_id=? AND status='Paid'",
            (student[0],)
        )

        paid = cursor.fetchone()[0]

        if paid > 0:
            status = "✅ Paid"
        else:
            status = "❌ Unpaid"

        html += f"<p>{student[1]} → {status}</p>"

    conn.close()

    html += "<br><a href='/dashboard'>🏠 Dashboard</a>"

    return html
    

#========== ADD MARK ===========
@app.route("/add_mark/<int:student_id>", methods=["GET", "POST"])
def add_mark(student_id):
    if request.method == "POST":
        subject = request.form["subject"]
        score = request.form["score"]

        conn = sqlite3.connect("school.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO marks (student_id, subject, score) VALUES (?, ?, ?)",
            (student_id, subject, score)
        )

        conn.commit()
        conn.close()

        return redirect(f"/marks/{student_id}")

    return """
    <h2>📝 Add Mark</h2>
    <form method="post">
        <input name="subject" placeholder="Subject"><br><br>
        <input name="score" placeholder="Score"><br><br>
        <button>Add Mark</button>
    </form>
    """
#========== MARKS ==========
@app.route("/marks/<int:student_id>")
def marks(student_id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT subject, score FROM marks WHERE student_id=?",
        (student_id,)
    )

    data = cursor.fetchall()
    conn.close()

    html = f"<h2>📝 Student Marks</h2>"

    html += f"""
    <a href="/add_mark/{student_id}">➕ Add Mark</a>
    <hr>
    """

    total = 0

    for m in data:
        total += int(m[1])
        html += f"<p>{m[0]} : {m[1]}</p>"

    if len(data) > 0:
        average = total / len(data)
        html += f"<h3>📊 Average: {average:.2f}</h3>"

    html += "<br><a href='/list'>Back</a>"

    return html
#========== RANKING ==============
@app.route("/ranking")
def ranking():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT students.name, AVG(marks.score) as avg_score
    FROM students
    JOIN marks ON students.id = marks.student_id
    GROUP BY students.id
    ORDER BY avg_score DESC
    """)

    data = cursor.fetchall()
    conn.close()

    html = "<h2>🏆 Top Students Ranking</h2><hr>"

    rank = 1

    for student in data:
        medal = ""

        if rank == 1:
            medal = "🥇"
        elif rank == 2:
            medal = "🥈"
        elif rank == 3:
            medal = "🥉"

        html += f"""
        <p>
            {medal} #{rank} - {student[0]}
            (Average: {student[1]:.2f})
        </p>
        """

        rank += 1

    html += "<br><a href='/dashboard'>🏠 Dashboard</a>"

    return html
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
<form action="/add" method="post">
    <input name="name" placeholder="Student Name">
    <input name="grade" placeholder="Grade">
    <button>Add Student</button>
</form>

<hr>

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
            <a href="/marks/{s[0]}">📝 Marks</a>
        </p>
        """
    html += "<br><a href='/attendance_report'>📅 Attendance Report</a>"
    html += "<br><a href='/dashboard'>Back</a>"
    html += "<br><a href='/logout'>🚪 Logout</a>"

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
#============= EDIT TEACHER =============
@app.route("/edit_teacher/<int:id>", methods=["GET", "POST"])
def edit_teacher(id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        subject = request.form["subject"]

        cursor.execute(
            "UPDATE teachers SET name=?, subject=? WHERE id=?",
            (name, subject, id)
        )

        conn.commit()
        conn.close()

        return redirect("/teachers")

    cursor.execute(
        "SELECT name, subject FROM teachers WHERE id=?",
        (id,)
    )

    teacher = cursor.fetchone()
    conn.close()

    return f"""
    <h2>✏️ Edit Teacher</h2>

    <form method="post">
        <input name="name" value="{teacher[0]}"><br><br>
        <input name="subject" value="{teacher[1]}"><br><br>
        <button>Update</button>
    </form>
    """
#========== DELETE TEACHER ============
@app.route("/delete_teacher/<int:id>")
def delete_teacher(id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM teachers WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/teachers")
#============= TEACHERS ============
@app.route("/teachers")
def teachers():
    if "user" not in session:
        return redirect("/login")

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, subject FROM teachers")
    data = cursor.fetchall()

    conn.close()

    html = """
    <h2>👨‍🏫 Teachers</h2>

    <form action="/add_teacher" method="post">
        <input name="name" placeholder="Teacher Name">
        <input name="subject" placeholder="Subject">
        <button>Add Teacher</button>
    </form>

    <hr>
    """

    for t in data:
        html += f"""
        <p>
            {t[1]} - {t[2]}
            <a href="/edit_teacher/{t[0]}">✏️ Edit</a>
            <a href="/delete_teacher/{t[0]}">🗑️ Delete</a>
        </p>
        """

    html += "<br><a href='/dashboard'>Back</a>"
    return html
#=========== ADD TEACHER ==============
@app.route("/add_teacher", methods=["POST"])
def add_teacher():
    name = request.form["name"]
    subject = request.form["subject"]

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO teachers (name, subject) VALUES (?, ?)",
        (name, subject)
    )

    conn.commit()
    conn.close()

    return redirect("/teachers")
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
@app.route("/create-checkout-session", methods=["POST"])
def create_checkout_session():

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": "School Fee"
                },
                "unit_amount": 1000
            },
            "quantity": 1
        }],
        mode="payment",
        success_url="https://school-saas-veqm.onrender.com/success",
        cancel_url="https://school-saas-veqm.onrender.com/cancel"
    )

    return redirect(checkout_session.url)
#========= PAYMENT ===========
@app.route("/payment")
def payment():

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM students")
    students = cursor.fetchall()
    conn.close()

    html = "<h2>💳 Select Student to Pay</h2>"

    for s in students:
        html += f"""
        <p>
            {s[1]}
            <a href="/pay/{s[0]}">Pay Fee</a>
        </p>
        """

    html += "<br><a href='/dashboard'>Back</a>"
    return html
    
#======== payments ==========
@app.route("/payments")
def payments():

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, student_name, amount, status, payment_date
    FROM payments
    ORDER BY id DESC
    """)

    data = cursor.fetchall()
    conn.close()

    html = """
    <h2>💳 Payments Report</h2>

    <table border="1" cellpadding="8">
        <tr>
            <th>ID</th>
            <th>Student</th>
            <th>Amount</th>
            <th>Status</th>
            <th>Date</th>
        </tr>
    """

    for p in data:
        html += f"""
        <tr>
            <td>{p[0]}</td>
            <td>{p[1]}</td>
            <td>{p[2]}</td>
            <td>{p[3]}</td>
            <td>{p[4]}</td>
        </tr>
        """

    html += "</table>"
    html += "<br><a href='/dashboard'>🏠 Back</a>"

    return html
#=========== PAY PER STUDENT ===============
@app.route("/pay/<int:student_id>")
def pay(student_id):

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM students WHERE id=?", (student_id,))
    student = cursor.fetchone()
    conn.close()

    session["student_id"] = student_id
    session["student_name"] = student[0]

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
                "currency": "usd",
                "product_data": {
                    "name": f"School Fee - {student[0]}"
                },
                "unit_amount": 1000
            },
            "quantity": 1
        }],
        mode="payment",
        success_url="https://school-saas-veqm.onrender.com/success",
        cancel_url="https://school-saas-veqm.onrender.com/cancel"
    )

    return redirect(checkout_session.url)
# =========================
# SUCCESS / CANCEL
# =========================
from datetime import datetime

@app.route("/success")
def success():

    student_id = session.get("student_id", 0)
    student_name = session.get("student_name", "Unknown")

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO payments (student_id, student_name, amount, status, payment_date)
        VALUES (?, ?, ?, ?, ?)
    """, (
        student_id,
        student_name,
        10,
        "Paid",
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))

    conn.commit()
    conn.close()

    return """
    <h2>✅ Payment Successful</h2>
    <a href="/payments">View Payments</a>
    """

@app.route("/cancel")
def cancel():
    return "❌ Payment Cancelled"

#========= LOGOUT =========== 
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")
# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
