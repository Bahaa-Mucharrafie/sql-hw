import sqlite3

# Connect to SQLite (in memory for testing)
conn = sqlite3.connect(':memory:')

# this is important because foreign keys are OFF by default in SQLite
conn.execute("PRAGMA foreign_keys = ON;")

cursor = conn.cursor()

# Helper function to inspect table contents
def print_table(cursor, table_name):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    print(f"\nTable: {table_name}")
    print(" | ".join(columns))
    print("-" * 30)

    for row in rows:
        print(" | ".join(str(value) for value in row))

# Create tables
cursor.execute("""
CREATE TABLE student (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    age INTEGER
)
""")

cursor.execute("""
CREATE TABLE registered_courses (
    student_id INTEGER,
    course_id INTEGER,
    PRIMARY KEY (student_id, course_id),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
)
""")

cursor.execute("""
CREATE TABLE grades (
    student_id INTEGER,
    course_id INTEGER,
    grade INTEGER,
    FOREIGN KEY (student_id) REFERENCES student(student_id),
    FOREIGN KEY (student_id, course_id) REFERENCES registered_courses(student_id, course_id)
)
""")

# Insert students
students = [
    (1, 'Alice', 20),
    (2, 'Bob', 22),
    (3, 'Charlie', 21)
]
cursor.executemany("INSERT INTO student VALUES (?, ?, ?)", students)

# Insert registered courses (must exist before inserting grades)
registered = [
    (1, 101), (1, 102),
    (2, 101), (2, 103),
    (3, 102), (3, 103)
]
cursor.executemany("INSERT INTO registered_courses VALUES (?, ?)", registered)

# Insert grades (must match a (student_id, course_id) in registered_courses)
grades = [
    (1, 101, 80), (1, 102, 90),
    (2, 101, 95), (2, 103, 88),
    (3, 102, 70), (3, 103, 95)  # tie max grade example
]
cursor.executemany("INSERT INTO grades VALUES (?, ?, ?)", grades)

conn.commit()

# Print tables
print_table(cursor, "student")
print_table(cursor, "registered_courses")
print_table(cursor, "grades")

# 1) Get the maximum grade a student has obtained along with course_id and student_id
cursor.execute("""
SELECT student_id, course_id, grade AS max_grade
FROM grades
WHERE grade = (SELECT MAX(grade) FROM grades)
""")
max_rows = cursor.fetchall()
print("\nMax grade row(s):")
for r in max_rows:
    print(r)

# 2) Get the average grade of the student(s) who got the max grade
# (If there is a tie, we compute average for each student in the tie)
for student_id, course_id, max_grade in max_rows:
    cursor.execute("SELECT AVG(grade) FROM grades WHERE student_id = ?", (student_id,))
    avg_grade = cursor.fetchone()[0]
    print(f"Student {student_id} average grade = {avg_grade:.2f}")

conn.close()