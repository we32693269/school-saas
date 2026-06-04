from flask import Flask, request

app = Flask(__name__)

students = []

# 🔐 LOGIN PAGE
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            return """
            <h2>Login Successful ✅</h2>
            <a href='/home'>Go to School System</a>
            """
        else:
            return """
            <h2>❌ Login Failed</h2>
            <a href='/'>Try Again</a>
            """

    return """
    <h1>Login Page</h1>
    <form method='post'>
        <input name='username' placeholder='Username'><br><br>
        <input name='password' type='password' placeholder='Password'><br><br>
        <button type='submit'>Login</button>
    </form>
    """

# 🏫 SCHOOL HOME
@app.route("/home")
def home():
    return """
    <h1>🏫 School System</h1>
    <a href='/add'>➕ Add Student</a><br>
    <a href='/list'>👀 View Students</a><br>
    <a href='/'>🔐 Logout</a>
    """

# ➕ ADD STUDENT
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        students.append(name)
        return "<h3>Student Added!</h3><a href='/home'>Back</a>"

    return """
    <h2>Add Student</h2>
    <form method='post'>
        <input name='name' placeholder='Student name'>
        <button type='submit'>Add</button>
    </form>
    <a href='/home'>Back</a>
    """

# 👀 LIST STUDENTS
@app.route("/list")
def list_students():
    html = "<h2>Students List</h2>"

    if len(students) == 0:
        html += "<p>No students yet!</p>"
    else:
        for i, s in enumerate(students, 1):
            html += f"<p>{i}. {s}</p>"

    html += "<br><a href='/home'>Back</a>"
    return html

# 🚀 RUN APP
if __name__ == "__main__":
    app.run(debug=True)
