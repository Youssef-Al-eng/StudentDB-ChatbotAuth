from database import Database
from student import Student
import re
import streamlit as st
import random
import pandas as pd
import os

class Chatbot:
    GREETINGS = [
        "Hello! How can I assist you today?",
        "Hi! I'm your student database assistant. How can I help you?",
        "Greetings! Ask me anything about students.",
        "Hey! Ready to manage your student data? Let me know what you need."
    ]

    COMMANDS = {
        'greeting': ['hello', 'hi', 'hey', 'greetings'],
        'add_student': ['add student'],
        'total_students': ['how many students', 'total students', 'number of students'],
        'student_info': ['tell me about', 'information about', 'details of'],
        'all_students': ['show all students', 'list all students', 'all students'],
        'grades': ['what grades', 'grade levels', 'available grades'],
        'report': ['show student count per grade', 'export database', 'download database'],
        'help': ['help', 'what can you do', 'commands', 'how do you work'],
        'exit': ['exit', 'quit', 'goodbye']
    }

    def __init__(self, db: Database):
        self.db = db

    # ---------------- Main Query Handler ----------------
    def handle_queries(self, query: str) -> str:
        query_lower = query.lower().strip()

        # Determine response
        if any(word in query_lower for word in self.COMMANDS['greeting']):
            response = self.generate_greeting()
        elif any(word in query_lower for word in self.COMMANDS['help']):
            response = self.generate_help()
        elif any(word in query_lower for word in self.COMMANDS['add_student']):
            response = self.add_student(query)
        elif any(word in query_lower for word in self.COMMANDS['all_students']):
            response = self.get_all_students()
        elif query_lower.startswith("get student"):
            response = self.get_student_by_id(query)
        elif query_lower.startswith("delete student"):
            response = self.delete_student(query)
        elif query_lower.startswith("update student"):
            response = self.update_student(query)
        elif any(word in query_lower for word in self.COMMANDS['total_students']):
            response = self.get_total_students()
        elif any(word in query_lower for word in self.COMMANDS['grades']):
            response = self.get_available_grades()
        elif any(word in query_lower for word in self.COMMANDS['report']):
            response = self.generate_report(query_lower)
        elif any(word in query_lower for word in self.COMMANDS['exit']):
            response = self.exit()
        else:
            response = self.unknown_command()

        # ---------------- Save chat to database ----------------
        username = st.session_state.get("username", "Guest")
        self.db.save_chat(username, query, response)

        return response

    # ---------------- Commands Implementation ----------------
    def generate_greeting(self):
        if "username" in st.session_state:
            return f"Hello {st.session_state.username}, how can I assist you today?"
        return random.choice(self.GREETINGS)

    def generate_help(self):
        return (
            "Here are the available commands:\n"
            "- Add a student: 'Add student <name> <age> <grade>'\n"
            "- View all students: 'Show all students'\n"
            "- Get student by ID: 'Get student <id>'\n"
            "- Delete a student: 'Delete student <id>'\n"
            "- Update student info: 'Update student <id> <name> <age> <grade>'\n"
            "- Get total students: 'How many students'\n"
            "- Get available grades: 'What grades are available?'\n"
            "- Show student count per grade: 'Show student count per grade'\n"
            "- Export database to CSV/PDF: 'Export database'\n"
            "- Exit: 'Exit'\n"
            "- View saved chats: use the sidebar option 'Saved Chats' if implemented in app.py"
        )

    def add_student(self, query: str):
        match = re.match(r"add student (.+?) (\d+) (\w+)", query)
        if match:
            name, age, grade = match.groups()
            student = Student(name=name, age=int(age), grade=grade)
            admin_user = st.session_state.get("username", None)
            self.db.insert_student(student, admin_user=admin_user)
            return f"✅ Student {name} added successfully."
        return "❌ Please provide the student's name, age, and grade (e.g., 'add student John 20 A')."

    def get_all_students(self):
        students = self.db.get_all_students()
        if not students:
            return "No students found."
        return "\n\n".join(self.format_student(student) for student in students)

    def get_student_by_id(self, query: str):
        student_id = self.extract_student_id(query)
        if student_id:
            student = self.db.get_student_by_id(student_id)
            if student:
                return self.format_student(student)
            return "Student not found."
        return "Please provide a valid student ID."

    def delete_student(self, query: str):
        student_id = self.extract_student_id(query)
        if student_id:
            admin_user = st.session_state.get("username", None)
            self.db.delete_student(student_id, admin_user=admin_user)
            return f"✅ Student with ID {student_id} deleted successfully."
        return "Please provide a valid student ID to delete."

    def update_student(self, query: str):
        match = re.match(r"update student (\d+) (.+?) (\d+) (\w+)", query)
        if match:
            student_id, name, age, grade = match.groups()
            student = Student(student_id=int(student_id), name=name, age=int(age), grade=grade)
            admin_user = st.session_state.get("username", None)
            self.db.update_student(student, admin_user=admin_user)
            return f"✅ Student with ID {student_id} updated successfully."
        return "❌ Format: 'update student 1 John 22 B'."

    def get_total_students(self):
        total = len(self.db.get_all_students())
        return f"There are {total} students in the database."

    def get_available_grades(self):
        grades = self.db.get_all_grades()
        return f"Available grades: {', '.join(grades)}" if grades else "No grades found."

    # ---------------- Report Generation ----------------
    def generate_report(self, query_lower: str):
        if "count" in query_lower:
            counts = self.db.get_student_count_per_grade()
            if counts:
                report = "\n".join([f"{grade}: {count}" for grade, count in counts.items()])
                return f"📊 Student count per grade:\n{report}"
            return "No students found for report."
        elif "export" in query_lower or "download" in query_lower:
            students = self.db.get_all_students()
            if not students:
                return "No students to export."
            # Convert to DataFrame
            df = pd.DataFrame([{
                "ID": s.student_id,
                "Name": s.name,
                "Age": s.age,
                "Grade": s.grade
            } for s in students])
            file_path = "student_database.csv"
            df.to_csv(file_path, index=False)
            return f"✅ Student database exported successfully as {file_path}."
        else:
            return "❌ Unknown report command. Try 'show student count per grade' or 'export database'."

    # ---------------- Saved Chat Helper ----------------
    def get_saved_chats(self):
        """Return all saved chats from database"""
        chats = self.db.get_all_chats()
        formatted = []
        for chat in chats:
            formatted.append(f"[{chat[4]}] {chat[1]}: {chat[2]}\nAssistant: {chat[3]}")
        return formatted

    # ---------------- Helpers ----------------
    @staticmethod
    def extract_student_id(query: str):
        match = re.match(r"\D*(\d+)", query)
        return int(match.group(1)) if match else None

    @staticmethod
    def format_student(student: Student) -> str:
        return f"**ID**: {student.student_id}\n**Name**: {student.name}\n**Age**: {student.age}\n**Grade**: {student.grade}"

    def exit(self):
        st.session_state.clear()
        return "You have logged out successfully. Goodbye!"

    def unknown_command(self):
        return "❌ I didn't understand that. Say 'help' for available commands."
