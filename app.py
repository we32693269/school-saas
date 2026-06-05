from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# 🗄️ DATABASE SETUP
def init_db():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            grade TEXT NOT NULL,
            age INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# 🏠 Home
@app.route('/')
def home():
    return render_template('index.html')

# 📊 Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# ➕ Add Student
@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        grade = request.form['grade']
        age = request.form['age']

        conn = sqlite3.connect('school.db')
        c = conn.cursor()
        c.execute("INSERT INTO students (name, grade, age) VALUES (?, ?, ?)",
                  (name, grade, age))
        conn.commit()
        conn.close()

        return redirect('/students')

    return render_template('add-student.html')

# 📋 View Students (from DB)
@app.route('/students')
def students():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    data = c.fetchall()
    conn.close()

    return render_template('list.html', students=data)

if __name__ == '__main__':
    app.run(debug=True)
