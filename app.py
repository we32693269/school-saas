from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "test_secret"

# ======================
# SIMPLE USERS
# ======================
USERS = {
    "admin": "1234"
}

# ======================
# LOGIN
# ======================
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username in USERS and USERS[username] == password:
            session['user'] = username
            return redirect('/dashboard')

        return "Wrong username or password"

    return render_template("login.html")

# ======================
# DASHBOARD
# ======================
@app.route('/dashboard')
def dashboard():

    if "user" not in session:
        return redirect('/login')

    return f"Welcome {session['user']} 🎉"

# ======================
# LOGOUT
# ======================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ======================
# RUN
# ======================
if __name__ == "__main__":
    app.run(debug=True)
