from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# simple database (temporary memory)
students = ["Abebe", "Selam", "Daniel"]

@app.route('/')
def home():
    return render_template("index.html", students=students)

@app.route('/add', methods=['POST'])
def add_student():
    name = request.form.get("name")
    if name:
        students.append(name)
    return redirect(url_for('home'))

@app.route('/delete/<name>')
def delete_student(name):
    if name in students:
        students.remove(name)
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
