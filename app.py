from flask import Flask, request, redirect
import sqlite3
import os
import stripe

app = Flask(__name__)

# =========================
# STRIPE
# =========================
stripe.api_key = "sk_test_51TdYS9AreGUdagSrq6ERvY9DSUYfdtqWbVWQKU1e1D5UIZ9o6VH9DIVZW7CxTIBk0IX52hQCR7Sm3reu4kWJPiQY00SCNIQviB"

# =========================
# DB INIT
# =========================
def init_db():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        grade TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =========================
# HOME
# =========================
@app.route("/")
def home():
    return "<h1>🏫 School SaaS</h1><a href='/list'>Go to Students</a>"

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

# =========================
# LIST STUDENTS (EDIT + DELETE)
# =========================
@app.route("/list")
def list_students():
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, grade FROM students")
    data = cursor.fetchall()

    conn.close()

    html = """
    <h2>📋 Students List</h2>

    <form action="/add" method="post">
        <input name="name" placeholder="Name">
        <input name="grade" placeholder="Grade">
        <button>Add</button>
    </form>
    <hr>
    """

    for s in data:
        html += f"""
        <p>
            {s[1]} - {s[2]}
            <a href="/edit/{s[0]}">✏️ Edit</a>
            <a href="/delete/{s[0]}">🗑️ Delete</a>
        </p>
        """

    return html

# =========================
# EDIT STUDENT
# =========================
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

# =========================
# DELETE STUDENT
# =========================
@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect("school.db")
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/list")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
