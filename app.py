from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "school_secret"

# ---------------- DATA ----------------
students = [
    {"id": 1, "name": "Abebe", "age": 16, "grade": "10", "attendance": "Present"}
]

next_id = 2

USERS = {
    "admin": {"password": "1234", "role": "admin"},
    "teacher": {"password": "1234", "role": "teacher"},
    "student": {"password": "1234", "role": "student"}
}

# ---------------- HOME ----------------
@app.route('/')
def home():
    if "user" in session:
        return redirect('/dashboard')
    return redirect('/login')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        if u in USERS and USERS[u]['password'] == p:
            session['user'] = u
            session['role'] = USERS[u]['role']
            return redirect('/dashboard')

        return "❌ Wrong login"

    return render_template('login.html')

# ---------------- DASHBOARD ----------------
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "user" not in session:
        return redirect('/login')

    role = session['role']
    global next_id

    # ➕ ADD STUDENT
    if request.method == 'POST' and "name" in request.form:
        if role in ["admin", "teacher"]:
            students.append({
                "id": next_id,
                "name": request.form['name'],
                "age": request.form.get('age', "N/A"),
                "grade": request.form.get('grade', "N/A"),
                "attendance": "Present"
            })
            next_id += 1

    # 📅 UPDATE ATTENDANCE
    if request.method == 'POST' and "attendance_id" in request.form:
        if role in ["admin", "teacher"]:
            sid = int(request.form['attendance_id'])
            status = request.form['attendance_status']

            for s in students:
                if s["id"] == sid:
                    s["attendance"] = status

    return render_template("dashboard.html", students=students, role=role)

# ---------------- DELETE ----------------
@app.route('/delete/<int:id>')
def delete(id):
    if "user" in session and session['role'] == "admin":
        global students
        students = [s for s in students if s["id"] != id]

    return redirect('/dashboard')

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
