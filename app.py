from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "erp_secret_key"

# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("SELECT * FROM students")
    students = c.fetchall()

    c.execute("SELECT COUNT(*) FROM students")
    total_students = c.fetchone()[0]

    c.execute("SELECT SUM(fee) FROM students")
    total_fee = c.fetchone()[0] or 0

    c.execute("SELECT SUM(paid) FROM students")
    total_paid = c.fetchone()[0] or 0

    balance = total_fee - total_paid

    conn.close()

    return render_template(
        "dashboard.html",
        students=students,
        total_students=total_students,
        total_fee=total_fee,
        total_paid=total_paid,
        total_balance=balance
    )


# ---------------- ADD STUDENT ----------------
@app.route('/add_student', methods=['POST'])
def add_student():

    name = request.form['name']
    age = request.form['age']
    grade = request.form['grade']
    fee = request.form['fee']
    paid = request.form['paid']

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("""
        INSERT INTO students (name, age, grade, fee, paid, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, age, grade, fee, paid, "Not Marked"))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


# ---------------- EDIT ----------------
@app.route('/edit_student/<int:id>', methods=['GET', 'POST'])
def edit_student(id):

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    if request.method == 'POST':

        name = request.form['name']
        age = request.form['age']
        grade = request.form['grade']
        fee = request.form['fee']
        paid = request.form['paid']
        status = request.form['status']

        c.execute("""
        UPDATE students
        SET name=?, age=?, grade=?, fee=?, paid=?, status=?
        WHERE id=?
        """, (name, age, grade, fee, paid, status, id))

        conn.commit()
        conn.close()

        return redirect('/dashboard')

    c.execute("SELECT * FROM students WHERE id=?", (id,))
    student = c.fetchone()

    conn.close()

    return render_template("edit_student.html", student=student)


# ---------------- DELETE ----------------
@app.route('/delete_student/<int:id>')
def delete_student(id):

    conn = sqlite3.connect('school.db')
    c = conn.cursor()

    c.execute("DELETE FROM students WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/dashboard')


if __name__ == "__main__":
    app.run(debug=True)
