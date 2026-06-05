from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "school_secret_key"

USER = "admin"
PASS = "1234"

students = []

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

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if "user" not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        if name:
            students.append(name)

    return render_template("dashboard.html", students=students)

@app.route('/delete/<name>')
def delete(name):
    if "user" in session and name in students:
        students.remove(name)
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
