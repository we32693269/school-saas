from flask import Flask, request, render_template_string

app = Flask(__name__)

students = []

# ---------------- HOME PAGE ----------------
@app.route("/")
def home():
    return """
    <h1>School System</h1>
    <a href='/add'>Add Student</a><br>
    <a href='/list'>Show Students</a>
    """

# ---------------- ADD STUDENT ----------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        students.append(name)
        return "<h3>Student Added!</h3><a href='/'>Back</a>"

    return """
    <form method='post'>
        <input name='name' placeholder='Student Name'>
        <button type='submit'>Add</button>
    </form>
    """

# ---------------- LIST STUDENTS ----------------
@app.route("/list")
def list_students():
    html = "<h2>Students List</h2>"
    for i, s in enumerate(students, 1):
        html += f"<p>{i}. {s}</p>"
    html += "<a href='/'>Back</a>"
    return html

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
