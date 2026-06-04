from flask import Flask, request, redirect, render_template
import sqlite3

app = Flask(__name__)
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
        name TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# LOGIN
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
    return render_template("home.html")


# =========================
# ADD STUDENT
# =========================
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]

        conn = sqlite3.connect("school.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO students (name) VALUES (?)",
            (name,)
        )

        conn.commit()
        conn.close()

        return redirect("/list")

    return render_template("add.html")


# =========================
# LIST STUDENTS
# =========================
@app.route("/list")
def list_students():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template(
        "list.html",
        students=students
    )


# =========================
# DELETE STUDENT
# =========================
@app.route("/delete/<int:id>")
def delete_student(id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM students WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/list")
#============= EDIT STUDENT =============   
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_student(id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form["name"]

        cursor.execute(
            "UPDATE students SET name = ? WHERE id = ?",
            (name, id)
        )

        conn.commit()
        conn.close()

        return redirect("/list")

    cursor.execute(
        "SELECT * FROM students WHERE id = ?",
        (id,)
    )

    student = cursor.fetchone()
    conn.close()

    return render_template(
        "edit.html",
        student=student
    )

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)
