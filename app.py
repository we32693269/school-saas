import os
import sqlite3
from flask import Flask, render_template, request, redirect, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "school123"

app.config["UPLOAD_FOLDER"] = "static/uploads"

# -------------------------
# DB INIT
# -------------------------
def init_db():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        class TEXT,
        age INTEGER,
        gender TEXT,
        photo TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# -------------------------
# LOGIN
# -------------------------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = request.form["username"]
        return redirect("/home")
    return render_template("login.html")

# -------------------------
# HOME
# -------------------------
@app.route("/home")
def home():
    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM students")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM students WHERE gender='Male'")
    boys = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM students WHERE gender='Female'")
    girls = cursor.fetchone()[0]

    conn.close()

    return render_template("home.html",
        total_students=total,
        total_males=boys,
        total_females=girls
    )

# -------------------------
# ADD STUDENT
# -------------------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        class_name = request.form["class"]
        age = request.form["age"]
        gender = request.form["gender"]

        photo = request.files.get("photo")
        filename = None

        if photo and photo.filename != "":
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        conn = sqlite3.connect("school.db")
        cursor = conn.cursor()

        cursor.execute("""
        INSERT INTO students (name, class, age, gender, photo)
        VALUES (?, ?, ?, ?, ?)
        """, (name, class_name, age, gender, filename))

        conn.commit()
        conn.close()

        return redirect("/list")

    return render_template("add.html")

# -------------------------
# LIST
# -------------------------
@app.route("/list")
def list_students():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    students = cursor.fetchall()

    conn.close()

    return render_template("list.html", students=students)

# -------------------------
# LOGOUT
# -------------------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
