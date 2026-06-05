from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "school_secret"

USER = "admin"
PASS = "1234"

# 📦 DB setup
def init_db():
    conn = sqlite3.connect("school.db")
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS students (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if "user" in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USER and request.form['password'] == PASS:
            session['user'] = USER
            return redirect('/dashboard')
        return "❌ Wrong login"

    return render_template("login.html")

# 📚 Dashboard (DB students)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "user" not in session:
        return redirect('/login')

    conn = sqlite3.connect("school.db")
    c = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        c.execute("INSERT INTO students (name) VALUES (?)", (name,))
        conn.commit()

    c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()

    return render_template("dashboard.html", students=students)

# ❌ Delete student
@app.route('/delete/<int:id>')
def delete(id):
    if "user" in session:
        conn = sqlite3.connect("school.db")
        c = conn.cursor()
        c.execute("DELETE FROM students WHERE id=?", (id,))
        conn.commit()
        conn.close()

    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
