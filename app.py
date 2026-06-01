from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"


# ================= DB =================
def get_db():
    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    return conn


# ================= TABLES =================
conn = get_db()
c = conn.cursor()
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
CREATE TABLE IF NOT EXISTS attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    status TEXT,
    date TEXT
)
""")

c.execute("""
CREATE TABLE IF NOT EXISTS fees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_name TEXT,
    amount TEXT,
    status TEXT,
    date TEXT
)
""")

conn.commit()
conn.close()


# ================= ADMIN CHECK =================
def is_admin():
    return session.get("role") == "admin"


# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        conn.close()

        if user:
            session["user"] = user["username"]
            session["role"] = user["role"]
            return redirect("/dashboard")

        return "Invalid Login"

    return render_template("login.html")


# ================= REGISTER =================
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()

        conn.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")
#============== FORGOT PASSWORD ==============
@app.route("/forgot_password", methods=["GET", "POST"])
def forgot_password()
    if request.method == "POST":

        username = request.form["username"]
        new_password = request.form["new_password"]

        conn = get_db()

        user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if not user:
            conn.close()
            return "User not found"

        conn.execute("""
            UPDATE users
            SET password=?
            WHERE username=?
        """, (new_password, username))

        conn.commit()
        conn.close()

        return "Password updated successfully"

    return render_template("forgot_password.html")
# ================= DASHBOARD =================
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    
    if "user" not in session:
        return redirect("/")

    conn = get_db()

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        grade = request.form["grade"]

        conn.execute(
            "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)",
            (name, age, grade)
        )
        conn.commit()

    students = conn.execute(
        "SELECT * FROM students"
    ).fetchall()

    conn.close()

    return render_template("dashboard.html", students=students)


# ================= EDIT =================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if "user" not in session:
        return redirect("/")

    conn = get_db()

    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    ).fetchone()

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        grade = request.form["grade"]

        conn.execute("""
            UPDATE students
            SET name=?, age=?, grade=?
            WHERE id=?
        """, (name, age, grade, id))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    conn.close()

    return render_template("edit.html", student=student)


# ================= DELETE =================
@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db()

    conn.execute(
        "DELETE FROM students WHERE id=?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ================= ATTENDANCE =================
@app.route("/attendance", methods=["GET", "POST"])
def attendance():

    if "user" not in session:
        return redirect("/")

    conn = get_db()

    if request.method == "POST":

        student_name = request.form["student_name"]
        status = request.form["status"]
        date = request.form["date"]

        conn.execute("""
            INSERT INTO attendance (student_name, status, date)
            VALUES (?, ?, ?)
        """, (student_name, status, date))

        conn.commit()

    records = conn.execute(
        "SELECT * FROM attendance"
    ).fetchall()

    conn.close()

    return render_template("attendance.html", records=records)


# ================= FEES (only admin =================
@app.route("/fees", methods=["GET", "POST"])
def fees():

    if "user" not in session:
        return redirect("/")

    if session.get("role") != "admin":
        return "Access Denied (Admin Only)"

    conn = get_db()

    # GET students for dropdown
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
#============= FEE RECEIPT ================
from reportlab.pdfgen import canvas
from flask import send_file
import os
@app.route("/fee_receipt/<int:id>")
def fee_receipt(id):

    if "user" not in session:
        return redirect("/")

    conn = get_db()

    fee = conn.execute("""
        SELECT fees.id, students.name, fees.amount, fees.status, fees.date
        FROM fees
        JOIN students ON students.id = fees.student_id
        WHERE fees.id=?
    """, (id,)).fetchone()

    conn.close()

    if not fee:
        return "Receipt Not Found"

    file_name = f"receipt_{id}.pdf"

    pdf = canvas.Canvas(file_name)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(180, 800, "SCHOOL FEE RECEIPT")

    pdf.setFont("Helvetica", 12)
    pdf.drawString(100, 750, f"Receipt ID: {fee['id']}")
    pdf.drawString(100, 730, f"Student Name: {fee['name']}")
    pdf.drawString(100, 710, f"Amount Paid: {fee['amount']}")
    pdf.drawString(100, 690, f"Status: {fee['status']}")
    pdf.drawString(100, 670, f"Date: {fee['date']}")

    pdf.drawString(100, 630, "Thank you for your payment!")

    pdf.save()

    return send_file(file_name, as_attachment=True)
# ================= LOGOUT =================
@app.route("/logout")
def logout():

    session.clear()
    return redirect("/")


# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
