import sqlite3
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# -----------------------------
# DATABASE INIT
# -----------------------------
def init_db():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# -----------------------------
# HOME PAGE
# -----------------------------
@app.route('/')
def home():
    return render_template('index.html')

# -----------------------------
# LOGIN
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == "admin@gmail.com" and password == "1234":
            return redirect('/dashboard')

        return "Invalid login ❌"

    return render_template('login.html')

# -----------------------------
# DASHBOARD (SHOW STUDENTS)
# -----------------------------
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    students = c.fetchall()
    conn.close()

    return render_template('dashboard.html', students=students)

# -----------------------------
# ADD STUDENT
# -----------------------------
@app.route('/add_student', methods=['POST'])
def add_student():
    name = request.form['name']
    age = request.form['age']

    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute("INSERT INTO students (name, age) VALUES (?, ?)", (name, age))
    conn.commit()
    conn.close()

    return redirect('/dashboard')

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == '__main__':
    app.run()
