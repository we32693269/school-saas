from flask import Flask, render_template, request, redirect

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

# 🔐 LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # demo users (later database)
        if email == "admin@gmail.com" and password == "1234":
            return redirect('/dashboard')

        return "Invalid login ❌"

    return render_template('login.html')

# 📊 DASHBOARD
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run()
