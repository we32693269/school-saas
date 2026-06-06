from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# Home
@app.route('/')
def home():
    return render_template('index.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # simple demo login (later database)
        if email == "admin@gmail.com" and password == "1234":
            return redirect('/dashboard')

    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
