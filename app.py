from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------

conn = sqlite3.connect("school.db", check_same_thread=False)
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS students(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    age TEXT,
    grade TEXT
)
""")

conn.commit()
conn.close()

# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":

            session["user"] = username

            return redirect("/dashboard")

    return render_template("login.html")

# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("SELECT * FROM students")

    students = c.fetchall()

    conn.close()

    return render_template("dashboard.html", students=students)

# ---------------- ADD STUDENT ----------------

@app.route("/add", methods=["POST"])
def add():

    if "user" not in session:
        return redirect("/")

    name = request.form["name"]
    age = request.form["age"]
    grade = request.form["grade"]

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute(
        "INSERT INTO students(name, age, grade) VALUES(?,?,?)",
        (name, age, grade)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------------- DELETE ----------------

@app.route("/delete/<int:id>")
def delete(id):

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

# ---------------- EDIT ----------------

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    if "user" not in session:
        return redirect("/")

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    if request.method == "POST":

        name = request.form["name"]
        age = request.form["age"]
        grade = request.form["grade"]

        c.execute("""
        UPDATE students
        SET name=?, age=?, grade=?
        WHERE id=?
        """, (name, age, grade, id))

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()

    conn.close()

    return render_template("edit.html", student=student)

# ---------------- LOGOUT ----------------

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/")

# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)
