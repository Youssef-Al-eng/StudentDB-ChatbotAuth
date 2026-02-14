import streamlit as st
import json
from hashlib import sha256
from chatbot import Chatbot
from database import Database
from student import Student
import time
import random
import pandas as pd
import io

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Student Database Chatbot",
    page_icon="🧑‍🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------- STYLING ----------------
st.markdown("""
<style>
/* GLOBAL */
[data-testid="stAppViewContainer"] {background-color:#ffffff !important;}
[data-testid="stHeader"] {background-color:#ffffff !important; border-bottom:1px solid #e0e0e0;}
section[data-testid="stSidebar"] {background-color:#ffffff !important; border-right:1px solid #e0e0e0;}

/* HEADINGS */
h1,h2,h3,h4,h5,h6 {color:#000000 !important;font-family:'Segoe UI',sans-serif !important;}
h1 {font-size:28px !important; font-weight:700 !important;}
h2 {font-size:22px !important; font-weight:600 !important;}

/* BODY TEXT */
p,label,div,span {color:#000000 !important; font-size:15px !important; font-family:'Segoe UI',sans-serif !important;}

/* CHAT */
.stChatMessage {background-color:#f9f9f9 !important; border-radius:10px; padding:10px; margin-bottom:10px; border:1px solid #e5e5e5;}

/* BUTTONS */
.stButton>button {background-color:#007bff !important; color:white !important; font-weight:600 !important; border-radius:8px !important; border:none !important; font-size:15px !important; padding:10px 20px !important; transition: transform 0.15s ease-in-out, background-color 0.15s;}
.stButton>button:hover {background-color:#0056b3 !important; transform:scale(1.05);}
.stButton>button:active {transform:scale(0.95);}

/* INPUT FIELDS */
input, textarea {border-radius:6px !important;}

/* TABLES */
.stTable {border:1px solid #e0e0e0; border-radius:8px;}
</style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZE ----------------
db = Database()
chatbot = Chatbot(db)
greetings = [
    "Hello! How can I assist you today? 😊",
    "Hi! I'm your student database assistant. How can I help you?",
    "Greetings! Ask me anything about students.",
    "Hey! Ready to manage your student data? 📚"
]

# ---------------- CREDENTIALS ----------------
def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)

def load_users():
    with open('users.json') as f:
        return json.load(f)

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(password):
    return sha256(password.encode()).hexdigest()

# ---------------- LOGIN ----------------
def login_page():
    st.markdown("<h1 style='text-align:center;'>🧑‍🎓 Student Database Chatbot</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>🔒 Login</h2>", unsafe_allow_html=True)
    user_type = st.radio("Login as:", ["Admin", "User"])
    username = st.text_input("👤 Username")
    password = st.text_input("🔑 Password", type="password")
    if st.button("🚪 Login"):
        if user_type == "Admin":
            creds = load_credentials()['admin']
            if username == creds['username'] and hash_password(password) == creds['password']:
                st.session_state.logged_in = True
                st.session_state.user_type = "Admin"
                st.session_state.username = username
                st.success("✅ Logged in as Admin")
                st.rerun()
            else:
                st.error("❌ Invalid Admin credentials")
        else:
            users = load_users()
            if username in users and users[username] == hash_password(password):
                st.session_state.logged_in = True
                st.session_state.user_type = "User"
                st.session_state.username = username
                st.success("✅ Logged in as User")
                st.rerun()
            else:
                st.error("❌ Invalid User credentials")
    if st.button("📝 Register Now"):
        st.session_state.page = "Register"
        st.rerun()

# ---------------- REGISTER ----------------
def register_page():
    st.markdown("<h1 style='text-align:center;'>🧑‍🎓 Student Database Chatbot</h1>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align:center;'>🆕 Register</h2>", unsafe_allow_html=True)
    username = st.text_input("👤 New Username")
    password = st.text_input("🔑 New Password", type="password")
    if st.button("📝 Register"):
        users = load_users()
        if username in users:
            st.error("⚠️ Username exists")
        else:
            users[username] = hash_password(password)
            save_users(users)
            st.session_state.logged_in = True
            st.session_state.user_type = "User"
            st.session_state.username = username
            st.success("✅ Registered successfully! Logging in...")
            st.rerun()

# ---------------- LOGOUT ----------------
def logout_button():
    st.session_state.logged_in = False
    st.session_state.user_type = ""
    st.session_state.username = ""
    st.success("👋 Logged out successfully.")
    st.rerun()

# ---------------- ADMIN DASHBOARD ----------------
def Admin_Dashboard():
    st.markdown("<h2>⚙️ Admin Dashboard</h2>", unsafe_allow_html=True)
    action = st.radio("Select Action", [
        "➕ Add Student", "📖 View Students", "🔍 Search Students", 
        "✏️ Update Student", "🗑️ Delete Student", "🗑️ Bulk Delete", 
        "📈 Statistics", "💬 View Saved Chats", "🗄️ Import CSV", "💾 Export CSV"
    ])

    # ----- ADD STUDENT -----
    if action=="➕ Add Student":
        name = st.text_input("👤 Name")
        age = st.number_input("🎂 Age",18,30)
        grade = st.text_input("🎓 Grade")
        if st.button("➕ Add Student"):
            query = f"add student {name} {age} {grade}"
            response = chatbot.handle_queries(query)
            st.success(response)
            db.save_chat(st.session_state.username,"user",query)
            db.save_chat(st.session_state.username,"assistant",response)

    # ----- VIEW STUDENTS -----
    elif action=="📖 View Students":
        students = db.get_all_students()
        if students:
            st.table([vars(s) for s in students])
        else:
            st.warning("No students in database.")

    # ----- SEARCH STUDENTS -----
    elif action=="🔍 Search Students":
        search_name = st.text_input("Search by Name")
        search_id = st.number_input("Search by ID", min_value=0, step=1)
        filtered = db.get_all_students()
        if search_name:
            filtered = [s for s in filtered if search_name.lower() in s.name.lower()]
        if search_id>0:
            filtered = [s for s in filtered if s.id==search_id]
        if filtered:
            st.table([vars(s) for s in filtered])
        else:
            st.warning("No students found.")

    # ----- UPDATE STUDENT -----
    elif action=="✏️ Update Student":
        student_id = st.number_input("Student ID",1)
        student = db.get_student_by_id(student_id)
        if student:
            new_name = st.text_input("New Name",student.name)
            new_age = st.number_input("New Age",18,100,student.age)
            new_grade = st.text_input("New Grade",student.grade)
            if st.button("Update"):
                query = f"update student {student_id} {new_name} {new_age} {new_grade}"
                response = chatbot.handle_queries(query)
                st.success(response)
                db.save_chat(st.session_state.username,"user",query)
                db.save_chat(st.session_state.username,"assistant",response)
        else:
            st.error("Student not found")

    # ----- DELETE STUDENT -----
    elif action=="🗑️ Delete Student":
        student_id = st.number_input("Student ID",1)
        if st.button("Delete"):
            query = f"delete student {student_id}"
            response = chatbot.handle_queries(query)
            st.success(response)
            db.save_chat(st.session_state.username,"user",query)
            db.save_chat(st.session_state.username,"assistant",response)

    # ----- BULK DELETE -----
    elif action=="🗑️ Bulk Delete":
        grade_filter = st.text_input("Delete students with Grade (leave empty for all)")
        if st.button("Delete All"):
            students = db.get_all_students()
            deleted = 0
            for s in students:
                if not grade_filter or s.grade==grade_filter:
                    query = f"delete student {s.id}"
                    chatbot.handle_queries(query)
                    deleted+=1
            st.success(f"Deleted {deleted} students.")

    # ----- STATISTICS -----
    elif action=="📈 Statistics":
        students = db.get_all_students()
        total = len(students)
        grade_count = {}
        for s in students:
            grade_count[s.grade] = grade_count.get(s.grade,0)+1
        st.write(f"Total Students: {total}")
        st.bar_chart(pd.DataFrame(list(grade_count.items()),columns=["Grade","Count"]))

    # ----- VIEW CHATS -----
    elif action=="💬 View Saved Chats":
        chats = db.get_all_chats()
        if chats:
            for chat in chats[::-1]:
                st.markdown(f"**{chat[1]}** ({chat[2]}): {chat[3]}")
        else:
            st.info("No saved chats.")

    # ----- IMPORT CSV -----
    elif action=="🗄️ Import CSV":
        uploaded_file = st.file_uploader("Upload CSV",type=["csv"])
        if uploaded_file:
            df = pd.read_csv(uploaded_file)
            for _,row in df.iterrows():
                chatbot.handle_queries(f"add student {row['name']} {row['age']} {row['grade']}")
            st.success("CSV Imported!")

    # ----- EXPORT CSV -----
    elif action=="💾 Export CSV":
        students = db.get_all_students()
        df = pd.DataFrame([vars(s) for s in students])
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "students.csv","text/csv")


# ---------------- USER DASHBOARD ----------------
def User_Dashboard():
    st.markdown("<h2>💬 Chat Interface</h2>", unsafe_allow_html=True)
    if "messages" not in st.session_state:
        st.session_state.messages=[]
    if not st.session_state.messages:
        st.session_state.messages.append({"role":"assistant","content":random.choice(greetings)})
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    query = st.chat_input("Enter your message here...")
    if query:
        st.session_state.messages.append({"role":"user","content":query})
        with st.chat_message("user"):
            st.markdown(query)
        with st.chat_message("assistant"):
            placeholder = st.empty()
            with st.spinner("Assistant typing..."):
                time.sleep(1.5)
                response = chatbot.handle_queries(query)
            placeholder.markdown(response)
            st.session_state.messages.append({"role":"assistant","content":response})
            db.save_chat(st.session_state.username,"user",query)
            db.save_chat(st.session_state.username,"assistant",response)


# ---------------- MAIN ----------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in=False
if 'page' not in st.session_state:
    st.session_state.page="Login"

page = st.sidebar.radio("Go to", ["Login","Register"], index=0 if st.session_state.page=="Login" else 1)
if st.sidebar.button("🧹 Clear Conversation"):
    st.session_state.messages=[]
if st.sidebar.button("🚪 Logout"):
    logout_button()
if not st.session_state.logged_in:
    if page=="Login":
        login_page()
    else:
        register_page()
else:
    if st.session_state.user_type=="Admin":
        Admin_Dashboard()
    else:
        User_Dashboard()
