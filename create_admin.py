from werkzeug.security import generate_password_hash
import sqlite3

# connect database
conn = sqlite3.connect("school.db")
c = conn.cursor()

# create admin user
username = "admin"
password = generate_password_hash("admin123")
role = "admin"

# insert admin
try:
    c.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
    """, (username, password, role))

    conn.commit()
    print("✅ Admin created successfully!")

except sqlite3.IntegrityError:
    print("⚠️ Admin already exists!")

conn.close()
