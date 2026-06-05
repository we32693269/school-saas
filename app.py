from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "school_secret_key"

# 🗄️ INIT DATABASE
def init_db():
    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    # Students table
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            grade TEXT,
            age INTEGER
        )
    ''')

    # Users table (LOGIN)
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            password TEXT
        )
    ''')

    # Create default admin (only once)
    c.execute("SELECT * FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  ('admin', '1234'))

    conn.commit()
    conn.close()

init_db()

# 🏠 LOGIN PAGE
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('school.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user'] = username
            return redirect('/dashboard')
        else:
            return "Invalid login ❌"

    return render_template('index.html')

# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

# 📊 DASHBOARD (PROTECTED)
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    return render_template('dashboard.html')

# ➕ ADD STUDENT
@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if 'user' not in session:
        return redirect('/')

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

# 📋 STUDENTS LIST
@app.route('/students')
def students():
    if 'user' not in session:
        return redirect('/')

    conn = sqlite3.connect('school.db')
    c = conn.cursor()
    c.execute("SELECT * FROM students")
    data = c.fetchall()
    conn.close()

    return render_template('list.html', students=data)

if __name__ == '__main__':
    app.run(debug=True)
