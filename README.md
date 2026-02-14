# 🧑‍🎓 Student Database Chatbot

A Streamlit-based chatbot application for managing a student database with admin and user roles. Admins can add, update, delete, import/export students, and view statistics. Users can interact via a conversational chat interface.

---

## Features

### ✅ Admin Features
- Add, update, and delete students individually or in bulk.
- View all students or search by name/ID.
- Import students from CSV files.
- Export student database to CSV.
- View statistics (total students, count per grade).
- View saved chat history.
- Audit log of admin actions.

### 💬 User Features
- Chat-based interface for querying student info.
- Get total number of students.
- View all available grades.
- Export reports via chat commands.
- Friendly chatbot responses and guidance.

---

## Project Structure
.
├── app.py            # Main Streamlit app
├── chatbot.py        # Chatbot class and command handling
├── database.py       # SQLite database handling and audit logging
├── student.py        # Student class
├── credentials.json  # Admin/user credentials (hashed passwords)
├── users.json        # Registered users
├── hash_test.py      # Script to generate SHA256 hashed passwords
├── requirements.txt  # Python dependencies

---

## Installation

1. Clone the repository:
```bash
git clone <repo_url>
cd student-database-chatbot

2. Install dependencies:

pip install -r requirements.txt


3.Run the app:

streamlit run app.py



## Usage

### Admin Login
- Default admin credentials are stored in `credentials.json`.
- After login, select actions from the dashboard:
  - Add Student
  - View Students
  - Search Students
  - Update/Delete Student
  - Bulk Delete
  - Statistics
  - View Saved Chats
  - Import/Export CSV

### User Login
- Users can register or login.
- Interact with the chatbot to:
  - Ask for student info
  - List all students
  - Check total students
  - Get available grades
  - Export reports

### Chatbot Commands
- `add student <name> <age> <grade>`
- `show all students`
- `get student <id>`
- `delete student <id>`
- `update student <id> <name> <age> <grade>`
- `how many students`
- `what grades are available?`
- `show student count per grade`
- `export database`
- `help`
- `exit`

---

## Security
- Passwords are hashed with SHA256.
- Admin actions are logged in an audit log.
- Separate user/admin roles.

---

## Dependencies
- Python 3.10+
- Streamlit
- Pandas
- SQLite3 (built-in)
- Other packages as listed in `requirements.txt`

---

## Author
Youssef Alaa  
Contact: [youssefalaa.1356@gmail.com]
