from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("school.db")
    conn.row_factory = sqlite3.Row
    return conn


# ---------------- AUTO CREATE TABLES ----------------
conn = get_db()
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    role TEXT
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

conn.commit()
conn.close()


# ---------------- AUTO ADMIN ----------------
conn = sqlite3.connect("school.db")
c = conn.cursor()

c.execute("SELECT * FROM users WHERE username=?", ("admin",))
if not c.fetchone():
    c.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
    """, ("admin", generate_password_hash("admin123"), "admin"))

conn.commit()
conn.close()


# ---------------- LOGIN ----------------
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


# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()

        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, "user")
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")


# ---------------- DASHBOARD ----------------
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

    students = conn.execute("SELECT * FROM students").fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        students=students,
        role=session.get("role")
    )


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
