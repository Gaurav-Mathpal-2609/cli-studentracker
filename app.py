import sqlite3

DB_FILE = "student_data_sqlitecli.db"

GRADE_POINTS = {
    "A+": 10, "A": 9, "B+": 8, "B": 7,
    "C+": 6, "C": 5, "D": 4, "F": 0
}

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# --- Teacher login ---
def teacher_login():
    teacher_id = input("Enter Teacher ID: ")
    password = input("Enter Password: ")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Teachers WHERE TeacherID=? AND Password=?", (teacher_id, password))
    teacher = cursor.fetchone()
    cursor.close()
    conn.close()
    if teacher:
        print(f"Welcome, {teacher['Name']}!")
        return teacher_id
    else:
        print("Invalid credentials")
        return None

# --- StudentTracker using DB ---
class StudentTracker:
    def __init__(self, teacher_id):
        self.teacher_id = teacher_id

    def add_student(self, roll_no, name):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Students WHERE RollNo=? AND TeacherID=?", (roll_no, self.teacher_id))
        if cursor.fetchone():
            print("Student with this roll number already exists.")
        else:
            cursor.execute("INSERT INTO Students (RollNo, Name, TeacherID) VALUES (?, ?, ?)",
                           (roll_no, name, self.teacher_id))
            conn.commit()
            print("Student added successfully.")
        cursor.close()
        conn.close()

    def edit_student(self, old_roll_no):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Students WHERE RollNo=? AND TeacherID=?", (old_roll_no, self.teacher_id))
        student = cursor.fetchone()
        if not student:
            print("Student not found.")
            cursor.close()
            conn.close()
            return

        print(f"Current Name: {student['Name']}, Roll No: {student['RollNo']}")
        new_roll_no = int(input("Enter new Roll No: "))
        new_name = input("Enter new Name: ")

        # Check if new roll number already exists for this teacher
        cursor.execute("SELECT * FROM Students WHERE RollNo=? AND TeacherID=?", (new_roll_no, self.teacher_id))
        if cursor.fetchone() and new_roll_no != old_roll_no:
            print("Another student with this roll number already exists.")
        else:
            cursor.execute("UPDATE Students SET RollNo=?, Name=? WHERE RollNo=? AND TeacherID=?",
                           (new_roll_no, new_name, old_roll_no, self.teacher_id))
            conn.commit()
            print("Student details updated successfully.")
        cursor.close()
        conn.close()

    def add_grades(self, roll_no, subject, grade):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT StudentID FROM Students WHERE RollNo=? AND TeacherID=?", (roll_no, self.teacher_id))
        student = cursor.fetchone()
        if not student:
            print("Student not found")
            cursor.close()
            conn.close()
            return
        student_id = student["StudentID"]

        # Get or create subject
        cursor.execute("SELECT SubjectID FROM Subjects WHERE SubjectName=?", (subject,))
        sub = cursor.fetchone()
        if sub:
            subject_id = sub["SubjectID"]
        else:
            cursor.execute("INSERT INTO Subjects (SubjectName) VALUES (?)", (subject,))
            subject_id = cursor.lastrowid
            conn.commit()

        cursor.execute("INSERT OR REPLACE INTO Grades (StudentID, SubjectID, Grade) VALUES (?, ?, ?)",
                       (student_id, subject_id, grade))
        conn.commit()
        print(f"Grade {grade} added for {subject}")
        cursor.close()
        conn.close()

    def view_student(self, roll_no):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT StudentID, Name FROM Students WHERE RollNo=? AND TeacherID=?", (roll_no, self.teacher_id))
        student = cursor.fetchone()
        if not student:
            print("Student not found")
            cursor.close()
            conn.close()
            return

        student_id = student["StudentID"]
        print(f"Roll No: {roll_no}, Name: {student['Name']}")

        cursor.execute("""
            SELECT s.SubjectName, g.Grade
            FROM Grades g
            JOIN Subjects s ON g.SubjectID = s.SubjectID
            WHERE g.StudentID=?
        """, (student_id,))
        grades = cursor.fetchall()
        for g in grades:
            print(f"{g['SubjectName']}: {g['Grade']}")
        cursor.close()
        conn.close()

    def calculate_average(self, roll_no):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT StudentID FROM Students WHERE RollNo=? AND TeacherID=?", (roll_no, self.teacher_id))
        student = cursor.fetchone()
        if not student:
            print("Student not found")
            cursor.close()
            conn.close()
            return
        student_id = student["StudentID"]

        cursor.execute("SELECT Grade FROM Grades WHERE StudentID=?", (student_id,))
        grades = cursor.fetchall()
        cursor.close()
        conn.close()

        if not grades:
            print("No grades found")
            return
        total = sum(GRADE_POINTS.get(g['Grade'], 0) for g in grades)
        avg = total / len(grades)
        print(f"Average grade points: {avg:.2f}")

    def display_all(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT RollNo, Name FROM Students WHERE TeacherID=?", (self.teacher_id,))
        students = cursor.fetchall()
        cursor.close()
        conn.close()
        if not students:
            print("No students found.")
            return
        for s in students:
            print(f"Roll No: {s['RollNo']}, Name: {s['Name']}")

    def subject_topper(self, subject):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SubjectID FROM Subjects WHERE SubjectName=?", (subject,))
        sub = cursor.fetchone()
        if not sub:
            print("No such subject")
            cursor.close()
            conn.close()
            return
        subject_id = sub["SubjectID"]

        cursor.execute("""
            SELECT st.Name, g.Grade
            FROM Grades g
            JOIN Students st ON g.StudentID = st.StudentID
            WHERE g.SubjectID=? AND st.TeacherID=?
        """, (subject_id, self.teacher_id))
        grades = cursor.fetchall()
        cursor.close()
        conn.close()

        if not grades:
            print("No grades for this subject yet")
            return

        top_student = max(grades, key=lambda x: GRADE_POINTS.get(x['Grade'], 0))
        print(f"Topper: {top_student['Name']}, Grade: {top_student['Grade']}")

# --- CLI Menu ---
def main_menu():
    teacher_id = None
    while not teacher_id:
        teacher_id = teacher_login()

    tracker = StudentTracker(teacher_id)

    while True:
        print("\n1. Add Student")
        print("2. Edit Student Details")
        print("3. Add Grades")
        print("4. View Student Details")
        print("5. Calculate Average")
        print("6. Display All Students")
        print("7. Subject Topper")
        print("8. Exit")
        choice = input("Enter choice: ")

        if choice == "1":
            roll = int(input("Roll No: "))
            name = input("Name: ")
            tracker.add_student(roll, name)
        elif choice == "2":
            old_roll = int(input("Enter current Roll No of student to edit: "))
            tracker.edit_student(old_roll)
        elif choice == "3":
            roll = int(input("Roll No: "))
            subject = input("Subject: ")
            grade = input("Grade (A+/A/...): ")
            if grade not in GRADE_POINTS:
                print("Invalid grade")
            else:
                tracker.add_grades(roll, subject, grade)
        elif choice == "4":
            roll = int(input("Roll No: "))
            tracker.view_student(roll)
        elif choice == "5":
            roll = int(input("Roll No: "))
            tracker.calculate_average(roll)
        elif choice == "6":
            tracker.display_all()
        elif choice == "7":
            subject = input("Subject: ")
            tracker.subject_topper(subject)
        elif choice == "8":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main_menu()
