from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "school_secret"

# 👇 users with roles
USERS = {
    "admin": {"password": "1234", "role": "admin"},
    "teacher": {"password": "1234", "role": "teacher"},
    "student": {"password": "1234", "role": "student"}
}

students = ["Abebe", "Selam"]

@app.route('/')
def home():
    if "user" in session:
        return redirect('/dashboard')
    return redirect('/login')

# 🔐 LOGIN
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

    return render_template("login.html")

# 🏫 DASHBOARD
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "user" not in session:
        return redirect('/login')

    role = session['role']

    # only admin + teacher can add
    if request.method == 'POST':
        if role in ["admin", "teacher"]:
            name = request.form['name']
            students.append(name)

    return render_template("dashboard.html", students=students, role=role)

# ❌ DELETE (only admin)
@app.route('/delete/<name>')
def delete(name):
    if "user" in session and session['role'] == "admin":
        if name in students:
            students.remove(name)

    return redirect('/dashboard')

# 🚪 LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
