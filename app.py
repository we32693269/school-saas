from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# 🏠 Home (Login page)
@app.route('/')
def home():
    return render_template('index.html')

# 📊 Dashboard
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# 👨‍🎓 Add student page
@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        grade = request.form['grade']
        age = request.form['age']

        print("Student Saved:", name, grade, age)
        return redirect('/dashboard')

    return render_template('add-student.html')

# 📋 Students list (simple static for now)
@app.route('/students')
def students():
    return render_template('list.html')

if __name__ == '__main__':
    app.run(debug=True)
