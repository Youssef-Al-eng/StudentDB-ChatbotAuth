class Student:
    def __init__(self, student_id=None, name=None, age=None, grade=None):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.grade = grade

    def update(self, name=None, age=None, grade=None):
        """Update student information if provided"""
        updated = False

        if name:
            self.name = name
            updated = True
        if age:
            self.age = age
            updated = True
        if grade:
            self.grade = grade
            updated = True

        if updated:
            print(f"✅ Updated student: {self.name}, Age: {self.age}, Grade: {self.grade}")
        else:
            print("ℹ️ No updates made.")

    def __repr__(self):
        """For debugging and easy printout of student object"""
        return f"<Student(id={self.student_id}, name={self.name}, age={self.age}, grade={self.grade})>"


