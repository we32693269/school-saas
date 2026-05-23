from flask import Flask, render_template, request, redirect, session
app = Flask(__name__)
app.secret_key = "secret123"


# ---------------- DATABASE ----------------

def init_db():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    # users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    """)

    # students table
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age TEXT,
            grade TEXT
        )
    """)

    # default admin user
    c.execute("""
        INSERT OR IGNORE INTO users (id, username, password)
        VALUES (1, 'admin', '1234')
    """)

    conn.commit()
    conn.close()


init_db()


# ---------------- LOGIN ----------------

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("school.db")
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = c.fetchone()

        conn.close()

        if user:
            session["user"] = username
            return redirect("/dashboard")

        return "Invalid Login ❌"

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
        "INSERT INTO students(name, age, grade) VALUES (?, ?, ?)",
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

    if request.method == "GET":

        c.execute("SELECT * FROM students WHERE id=?", (id,))
        student = c.fetchone()

        conn.close()

        return render_template("edit.html", student=student)

    name = request.form["name"]
    age = request.form["age"]
    grade = request.form["grade"]

    c.execute(
        "UPDATE students SET name=?, age=?, grade=? WHERE id=?",
        (name, age, grade, id)
    )

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
