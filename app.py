from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "school_secret"

# Grades and Attendance
grades = {}
attendance = {}

# Users with roles
USERS = {
    "admin": {"password": "1234", "role": "admin"},
    "teacher": {"password": "1234", "role": "teacher"},
    "student": {"password": "1234", "role": "student"}
}

# Student list
students = ["Abebe", "Selam"]

@app.route('/')
def home():
    if "user" in session:
        return redirect('/dashboard')
    return redirect('/login')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['role'] = USERS[username]['role']
            return redirect('/dashboard')

        return "❌ Wrong username or password"

    return render_template('login.html')

# Dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "user" not in session:
        return redirect('/login')

    role = session['role']

    # Add student
    if request.method == 'POST' and "name" in request.form:
        if role in ["admin", "teacher"]:
            students.append(request.form['name'])

    # Add grade
    if request.method == 'POST' and "grade_name" in request.form:
        if role in ["admin", "teacher"]:
            grades[request.form['grade_name']] = request.form['grade_value']

    # Add attendance
    if request.method == 'POST' and "attendance_name" in request.form:
        if role in ["admin", "teacher"]:
            attendance[request.form['attendance_name']] = request.form['attendance_status']

    return render_template(
        'dashboard.html',
        students=students,
        grades=grades,
        attendance=attendance,
        role=role
    )

# Delete student (Admin only)
@app.route('/delete/<name>')
def delete(name):
    if "user" in session and session['role'] == "admin":
        if name in students:
            students.remove(name)

    return redirect('/dashboard')

# Report Card
@app.route('/report/<name>')
def report(name):
    if "user" not in session:
        return redirect('/login')

    grade = grades.get(name, "N/A")
    status = attendance.get(name, "N/A")

    return render_template(
        'report.html',
        name=name,
        grade=grade,
        status=status
    )

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
