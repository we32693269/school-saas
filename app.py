from flask import Flask, request

app = Flask(__name__)

students = []

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            return "<h1>Login Success</h1><a href='/home'>Enter</a>"
        else:
            return "<h1>Login Failed</h1><a href='/'>Try Again</a>"

    return """
    <h1>Login Page</h1>
    <form method='post'>
        <input name='username' placeholder='Username'>
        <input name='password' type='password' placeholder='Password'>
        <button>Login</button>
    </form>
    """

@app.route("/home")
def home():
    return """
    <h1>School System</h1>
    <a href='/add'>Add Student</a><br>
    <a href='/list'>View Students</a>
    """

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        students.append(name)
        return "<h3>Student Added!</h3><a href='/home'>Back</a>"

    return """
    <form method='post'>
        <input name='name' placeholder='Student Name'>
        <button>Add</button>
    </form>
    """

@app.route("/list")
def list_students():
    html = "<h2>Students List</h2>"
    if not students:
        html += "<p>No students yet</p>"
    else:
        for i, s in enumerate(students, 1):
            html += f"<p>{i}. {s}</p>"
    return html + "<br><a href='/home'>Back</a>"

if __name__ == "__main__":
    app.run()
