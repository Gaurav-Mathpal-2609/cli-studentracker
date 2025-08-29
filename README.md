# cli-studentracker

Python CLI app to manage students, grades, and subjects with teacher login. Uses SQLite. It is the CLI version of the webapp. 

## Teachers
- `TeacherID: gaurav123`, `Password: 1234`  
- `TeacherID: aditya123`, `Password: 6666`

## Features
- Teacher login
- Add/Edit Students
- Add/View Grades
- Calculate average
- Display all students
- Find subject toppers

## DB Structure
- Teachers(TeacherID, Name, Password)  
- Students(StudentID, RollNo, Name, TeacherID)  
- Subjects(SubjectID, SubjectName)  
- Grades(GradeID, StudentID, SubjectID, Grade)

## Run
```bash

#1. Make sure `student_data_sqlitecli.db` exists with the tables above.

#2. Run:  

    python student_tracker_cli.py

#3. Login with one of the teacher IDs.

#4. Use the menu to manage students and grades.
