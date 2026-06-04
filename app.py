# =========================
# LOGIN SYSTEM
# =========================
print("=== SCHOOL SYSTEM LOGIN ===")

username = input("Username: ")
password = input("Password: ")

if username == "admin" and password == "1234":
    print("\nLogin successful!\n")

    # =========================
    # SCHOOL SYSTEM
    # =========================
    students = []

    while True:
        print("\n1. Add Student")
        print("2. Show Students")
        print("3. Delete Student")
        print("4. Exit")

        choice = input("Choose option: ")

        # ➕ Add student
        if choice == "1":
            name = input("Enter student name: ")
            students.append(name)
            print("Student added!")

        # 👀 Show students
        elif choice == "2":
            if len(students) == 0:
                print("No students yet!")
            else:
                print("\n--- Students List ---")
                for i, s in enumerate(students, 1):
                    print(i, s)

        # 🗑️ Delete student
        elif choice == "3":
            if len(students) == 0:
                print("No students to delete!")
            else:
                for i, s in enumerate(students, 1):
                    print(i, s)

                num = int(input("Enter number to delete: "))
                if 1 <= num <= len(students):
                    removed = students.pop(num - 1)
                    print("Deleted:", removed)
                else:
                    print("Invalid number!")

        # 🚪 Exit
        elif choice == "4":
            # 💾 Save before exit
            with open("students.txt", "w") as f:
                for s in students:
                    f.write(s + "\n")

            print("Saved to file. Goodbye!")
            break

        else:
            print("Invalid choice!")

else:
    print("Login failed! Wrong username or password")
