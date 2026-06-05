from flask import Flask, render_template, request, redirect, session

app = Flask(__name__)
app.secret_key = "school123"

# demo user (admin)
USER = "admin"
PASS = "1234"

@app.route('/')
def home():
    if "user" in session:
        return render_template("dashboard.html")
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == USER and password == PASS:
            session["user"] = username
            return redirect('/')
        else:
            return "❌ Wrong username or password"

    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
