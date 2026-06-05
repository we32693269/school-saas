from flask import Flask, request, redirect, render_template, session
import sqlite3
import os
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"
app.secret_key = "school_secret_key"
# =========================
# DATABASE SETUP
# =========================
def init_db():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        class_name TEXT,
        age INTEGER,
        gender TEXT,
        photo TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect("/home")
        else:
            return "Login Failed"

    return render_template("login.html")


# =========================
# HOME
# =========================
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total_students = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM students WHERE gender='Male'"
    )
    total_males = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM students WHERE gender='Female'"
    )
    total_females = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "home.html",
        total_students=total_students,
        total_males=total_males,
        total_females=total_females
    )
#================ SEARCH ===============
@app.route("/search")
def search():
    if "user" not in session:
        return redirect("/")

    query = request.args.get("q")

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM students
        WHERE name LIKE ?
    """, ('%' + query + '%',))

    students = cursor.fetchall()
    conn.close()

    return render_template("list.html", students=students)
#================ ADD STUDENT ================
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        class_name = request.form["class_name"]
        age = request.form["age"]
        gender = request.form["gender"]

        conn = sqlite3.connect("school.db")
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO students (name, class_name, age, gender)
            VALUES (?, ?, ?, ?)
        """, (name, class_name, age, gender))

        conn.commit()
        conn.close()

        return redirect("/list")

    return render_template("add.html")

# =========================
# LIST STUDENTS
# =========================
@app.route("/list")
def list_students():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template("list.html", students=students)


# =========================
# EDIT STUDENT
# =========================
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]
        class_name = request.form["class"]
        age = request.form["age"]
        gender = request.form["gender"]

        cursor.execute("""
            UPDATE students
            SET name=?, class=?, age=?, gender=?
            WHERE id=?
        """, (name, class_name, age, gender, id))

        conn.commit()
        conn.close()

        return redirect("/list")

    cursor.execute(
        "SELECT * FROM students WHERE id=?",
        (id,)
    )

    student = cursor.fetchone()
    conn.close()

    return render_template(
        "edit.html",
        student=student
    )

# =========================
# DELETE STUDENT
# =========================
@app.route("/delete/<int:id>")
def delete_student(id):
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/list")


# =========================
# LOGOUT
# =========================
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/")


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
