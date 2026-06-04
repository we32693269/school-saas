students = []

while True:
    name = input("Enter student name (or type exit): ")

    if name == "exit":
        break

    students.append(name)

print("All Students:")
print(students)
