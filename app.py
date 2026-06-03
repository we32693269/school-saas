from flask import Flask, request, redirect, session
from werkzeug.utils import secure_filename
import sqlite3
import os
app = Flask(__name__)
app.secret_key = "school_secret_key"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
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
    try:
      cursor.execute("ALTER TABLE students ADD COLUMN photo TEXT")
    except:
         pass

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
#============ INCOME DASHBOARD =============
@app.route("/income_dashboard")
def income_dashboard():

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    # Total income
    cursor.execute("SELECT SUM(amount) FROM payments WHERE status='Paid'")
    total_income = cursor.fetchone()[0]

    if total_income is None:
        total_income = 0

    # Paid students
    cursor.execute("""
    SELECT COUNT(DISTINCT student_id)
    FROM payments
    WHERE status='Paid'
    """)
    paid_students = cursor.fetchone()[0]

    # Total students
    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    unpaid_students = total_students - paid_students

    conn.close()

    return f"""
    <h2>📊 Income Dashboard</h2>

    <hr>

    <h3>💵 Total Income: ${total_income}</h3>

    <p>✅ Paid Students: {paid_students}</p>

    <p>❌ Unpaid Students: {unpaid_students}</p>

    <br>

    <a href='/dashboard'>🏠 Dashboard</a>
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

    cursor.execute("SELECT COUNT(*) FROM payments")
    payments = cursor.fetchone()[0]

    conn.close()

    html = f"""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    <div class="container mt-4">

    <h2 class="mb-4">🏫 School SaaS Dashboard</h2>

    <div class="row">

        <div class="col-md-3">
            <div class="card text-white bg-primary mb-3 shadow">
                <div class="card-body text-center">
                    <h5>👨‍🎓 Students</h5>
                    <h2>{students}</h2>
                </div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card text-white bg-success mb-3 shadow">
                <div class="card-body text-center">
                    <h5>👨‍🏫 Teachers</h5>
                    <h2>{teachers}</h2>
                </div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card text-white bg-warning mb-3 shadow">
                <div class="card-body text-center">
                    <h5>📅 Attendance</h5>
                    <h2>{attendance}</h2>
                </div>
            </div>
        </div>

        <div class="col-md-3">
            <div class="card text-white bg-danger mb-3 shadow">
                <div class="card-body text-center">
                    <h5>💳 Payments</h5>
                    <h2>{payments}</h2>
                </div>
            </div>
        </div>

    </div>

    <hr>

    <div class="row">

        <div class="col-md-4">
            <a href="/list" class="btn btn-outline-primary w-100 mb-2">👨‍🎓 Students</a>
        </div>

        <div class="col-md-4">
            <a href="/teachers" class="btn btn-outline-success w-100 mb-2">👨‍🏫 Teachers</a>
        </div>

        <div class="col-md-4">
            <a href="/attendance_report" class="btn btn-outline-warning w-100 mb-2">📅 Attendance</a>
        </div>

        <div class="col-md-4">
            <a href="/ranking" class="btn btn-outline-dark w-100 mb-2">🏆 Ranking</a>
        </div>
        
        <div class="col-md-4">
             <a href="/payment" class="btn btn-outline-info w-100 mb-2">💳 Payment System</a>
        </div>

        <div class="col-md-4">
            <a href="/payments" class="btn btn-outline-danger w-100 mb-2">💳 Payments</a>
        </div>

        <div class="col-md-4">
            <a href="/logout" class="btn btn-outline-secondary w-100 mb-2">🚪 Logout</a>
        </div>

    </div>

    </div>
    """

    return html   
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
#============== UPLOAD PHOTO ===============
@app.route("/upload_photo/<int:student_id>", methods=["GET", "POST"])
def upload_photo(student_id):

    if request.method == "POST":

        file = request.files["photo"]

        if file.filename:

            filename = secure_filename(file.filename)

            path = os.path.join(
                app.config["UPLOAD_FOLDER"],
                filename
            )

            file.save(path)

            conn = sqlite3.connect("school.db")
            cursor = conn.cursor()

            cursor.execute(
                "UPDATE students SET photo=? WHERE id=?",
                (filename, student_id)
            )

            conn.commit()
            conn.close()

            return redirect(f"/student_profile/{student_id}")

    return """
    <h2>📷 Upload Student Photo</h2>

    <form method="post" enctype="multipart/form-data">
        <input type="file" name="photo">
        <br><br>
        <button>Upload</button>
    </form>
    """
#=============== STUDENT PROFILE ================
@app.route("/student_profile/<int:student_id>")
def student_profile(student_id):

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    # =====================
    # STUDENT INFO
    # =====================
    cursor.execute(
        "SELECT name, grade, photo FROM students WHERE id=?",
        (student_id,)
    )

    student = cursor.fetchone()

    if not student:
        return "Student not found"

    photo = student[2] if student[2] else "default.png"

    # =====================
    # MARKS
    # =====================
    cursor.execute(
        "SELECT subject, score FROM marks WHERE student_id=?",
        (student_id,)
    )
    marks = cursor.fetchall()

    # =====================
    # ATTENDANCE
    # =====================
    cursor.execute("""
        SELECT
        SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END),
        SUM(CASE WHEN status='Absent' THEN 1 ELSE 0 END)
        FROM attendance
        WHERE student_id=?
    """, (student_id,))

    attendance = cursor.fetchone()

    present = attendance[0] or 0
    absent = attendance[1] or 0

    # =====================
    # PAYMENTS
    # =====================
    cursor.execute("""
        SELECT amount, payment_date, status
        FROM payments
        WHERE student_name=?
        ORDER BY id DESC
    """, (student[0],))

    payments = cursor.fetchall()

    conn.close()

    # =====================
    # HTML UI (BOOTSTRAP)
    # =====================
    html = f"""
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">

    <div class="container mt-4">

    <div class="card shadow p-4 text-center">

        <img src="/static/uploads/{photo}"
        width="150" height="150"
        style="border-radius:50%; object-fit:cover;">

        <h2 class="mt-2">{student[0]}</h2>
        <p>Grade: {student[1]}</p>

        <a class="btn btn-primary" href="/upload_photo/{student_id}">
        📷 Upload Photo
        </a>

    </div>

    <br>

    <div class="card p-3 shadow">
        <h4>📅 Attendance</h4>
        <p>✅ Present: {present}</p>
        <p>❌ Absent: {absent}</p>
    </div>

    <br>

    <div class="card p-3 shadow">
        <h4>📝 Marks</h4>
    """

    total = 0

    for m in marks:
        total += int(m[1])
        html += f"<p>{m[0]} : {m[1]}</p>"

    if marks:
        avg = total / len(marks)
        html += f"<h5>Average: {avg:.2f}</h5>"

    html += """
    </div>

    <br>

    <div class="card p-3 shadow">
        <h4>💳 Payments</h4>
    """

    for p in payments:
        html += f"<p>💰 {p[0]} - {p[1]} ({p[2]})</p>"

    html += """
    </div>

    <br>

    <a class="btn btn-secondary" href="/list">⬅ Back</a>

    </div>
    """

    return html
#=============== RECEIPT PAYMENT ================
@app.route("/receipt/<int:payment_id>")
def receipt(payment_id):

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT student_name, amount, payment_date, status
    FROM payments
    WHERE id=?
    """, (payment_id,))

    payment = cursor.fetchone()
    conn.close()

    if not payment:
        return "Receipt not found"

    pdf_file = f"receipt_{payment_id}.pdf"

    c = canvas.Canvas(pdf_file)

    c.setFont("Helvetica-Bold", 18)
    c.drawString(180, 800, "SCHOOL PAYMENT RECEIPT")

    c.setFont("Helvetica", 12)
    c.drawString(50, 740, f"Student: {payment[0]}")
    c.drawString(50, 710, f"Amount: ${payment[1]}")
    c.drawString(50, 680, f"Status: {payment[3]}")
    c.drawString(50, 650, f"Date: {payment[2]}")

    c.drawString(50, 600, "Thank you for your payment.")

    c.save()

    return send_file(
        pdf_file,
        as_attachment=True
    )
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
            <a href="/student_profile/{s[0]}">👤 Profile</a>
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
            <th>Receipt</th>
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
            <td>
            <a href="/receipt/{p[0]}">📄 Receipt</a>
            </td>
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
