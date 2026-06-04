students = []

while True:
    name = input("Enter student name (or type exit): ")

    if name == "exit":
        break

    students.append(name)

print("\nStudents:")
for i, s in enumerate(students, 1):
    print(i, s)

# delete part
delete = input("Enter number to delete (or press enter): ")

if delete:
    index = int(delete) - 1
    if 0 <= index < len(students):
        removed = students.pop(index)
        print("Deleted:", removed)

print("Final List:", students)
