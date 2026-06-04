from flask import Flask, render_template, request

app = Flask(__name__)

students = []

@app.route("/")
def login():
    return render_template("login.html")

@app.route("/home")
def home():
    return render_template("home.html")

@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        students.append(name)
    return render_template("add.html")

@app.route("/list")
def list_students():
    return render_template("list.html", students=students)

if __name__ == "__main__":
    app.run(debug=True)
