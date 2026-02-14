from student import Student
import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_name="student_db.sqlite"):
        """Initialize the database and create tables if they don't exist"""
        self._connection = sqlite3.connect(db_name)
        self._cursor = self._connection.cursor()
        self._create_student_table()
        self._create_chat_table()
        self._create_audit_table()

    # -------------------- Table Creation --------------------

    def _create_student_table(self):
        """Create students table if it doesn't already exist"""
        query = '''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            grade TEXT NOT NULL
        );
        '''
        self._cursor.execute(query)
        self._connection.commit()

    def _create_chat_table(self):
        """Create chats table if it doesn't already exist"""
        query = '''
        CREATE TABLE IF NOT EXISTS chats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT NOT NULL,
            message TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
        self._cursor.execute(query)
        self._connection.commit()

    def _create_audit_table(self):
        """Create audit logs table to track admin actions"""
        query = '''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            admin_user TEXT NOT NULL,
            action TEXT NOT NULL,
            target_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        '''
        self._cursor.execute(query)
        self._connection.commit()

    # -------------------- Student Methods --------------------

    def insert_student(self, student: Student, admin_user=None):
        """Insert a student record into the database"""
        query = "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)"
        self._cursor.execute(query, (student.name, student.age, student.grade))
        self._connection.commit()
        student_id = self._cursor.lastrowid
        student.student_id = student_id

        if admin_user:
            self.log_action(admin_user, "insert_student", student_id)
        return student_id

    def get_all_students(self):
        """Return all students as a list of Student objects"""
        query = "SELECT * FROM students"
        self._cursor.execute(query)
        rows = self._cursor.fetchall()
        return [Student(student_id=row[0], name=row[1], age=row[2], grade=row[3]) for row in rows]

    def get_student_by_id(self, student_id):
        """Fetch student by ID"""
        query = "SELECT * FROM students WHERE id = ?"
        self._cursor.execute(query, (student_id,))
        row = self._cursor.fetchone()
        if row:
            return Student(student_id=row[0], name=row[1], age=row[2], grade=row[3])
        return None

    def get_student_by_name(self, student_name):
        """Fetch student by name"""
        query = "SELECT * FROM students WHERE name = ?"
        self._cursor.execute(query, (student_name,))
        row = self._cursor.fetchone()
        if row:
            return Student(student_id=row[0], name=row[1], age=row[2], grade=row[3])
        return None

    def update_student(self, student: Student, admin_user=None):
        """Update a student's information"""
        query = "UPDATE students SET name = ?, age = ?, grade = ? WHERE id = ?"
        self._cursor.execute(query, (student.name, student.age, student.grade, student.student_id))
        self._connection.commit()
        if admin_user:
            self.log_action(admin_user, "update_student", student.student_id)

    def delete_student(self, student_id, admin_user=None):
        """Delete student by ID"""
        query = "DELETE FROM students WHERE id = ?"
        self._cursor.execute(query, (student_id,))
        self._connection.commit()
        if admin_user:
            self.log_action(admin_user, "delete_student", student_id)

    def get_all_grades(self):
        """Return distinct grades from the students table"""
        query = "SELECT DISTINCT grade FROM students"
        self._cursor.execute(query)
        rows = self._cursor.fetchall()
        return [row[0] for row in rows]

    # -------------------- Report Methods --------------------

    def get_student_count_per_grade(self):
        """Return a dictionary of student count per grade"""
        query = "SELECT grade, COUNT(*) FROM students GROUP BY grade"
        self._cursor.execute(query)
        rows = self._cursor.fetchall()
        return {row[0]: row[1] for row in rows}

    # -------------------- Chat Methods --------------------

    def save_chat(self, user, message, response):
        """Save a user chat with the assistant"""
        query = "INSERT INTO chats (user, message, response) VALUES (?, ?, ?)"
        self._cursor.execute(query, (user, message, response))
        self._connection.commit()

    def get_all_chats(self):
        """Fetch all chats, newest first"""
        query = "SELECT * FROM chats ORDER BY timestamp DESC"
        self._cursor.execute(query)
        return self._cursor.fetchall()

    # -------------------- Audit Log Methods --------------------

    def log_action(self, admin_user, action, target_id=None):
        """Record an admin action in the audit logs"""
        query = "INSERT INTO audit_logs (admin_user, action, target_id) VALUES (?, ?, ?)"
        self._cursor.execute(query, (admin_user, action, target_id))
        self._connection.commit()

    def get_audit_logs(self):
        """Fetch all audit logs"""
        query = "SELECT * FROM audit_logs ORDER BY timestamp DESC"
        self._cursor.execute(query)
        return self._cursor.fetchall()

    # -------------------- Cleanup --------------------

    def close(self):
        """Close the database connection"""
        self._cursor.close()
        self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
