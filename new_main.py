import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain.agents import AgentType

# ---------------------------
# 1️⃣  Database Setup
# ---------------------------
db_user = "root"
db_pass = "Roopesh2004"
db_host = "localhost"
db_name = "medical"

engine = create_engine(f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}")
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


# User table
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    gender = Column(String(10))
    age = Column(Integer)


# Chat history table
class ChatHistory(Base):
    __tablename__ = "chat_history"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_email = Column(String(255))
    symptom_input = Column(Text)
    llm_response = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(engine)

# ---------------------------
# 2️⃣  LLM + SQL Agent Setup
# ---------------------------
api_key = "AIzaSyCT3JVnuY-zWlLAtZY266eg3y559sgXcf4"

llm = ChatGoogleGenerativeAI(
    google_api_key=api_key,
    model="gemini-2.5-flash",
    temperature=0.2
)

db = SQLDatabase.from_uri(
    f"mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}",
    include_tables=["conditions"],
    sample_rows_in_table_info=3
)

agent_executor = create_sql_agent(
    llm=llm,
    db=db,
    agent_type=AgentType.OPENAI_FUNCTIONS,
    verbose=True,
    handle_parsing_errors=True
)

# ---------------------------
# 3️⃣  Streamlit UI
# ---------------------------
st.set_page_config(page_title="Healthcare Symptom Checker", page_icon="🩺")
st.title("🩺 Healthcare Symptom Checker")

# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = None
if "user_email" not in st.session_state:
    st.session_state.user_email = None

menu = ["Login", "Create Account", "Check Symptoms", "View History", "Logout"]
choice = st.sidebar.selectbox("Menu", menu)

# ---------------------------
# Create Account
# ---------------------------
if choice == "Create Account":
    st.subheader("Create a New Account")
    name = st.text_input("Full Name")
    email = st.text_input("Email ID")
    password = st.text_input("Password", type="password")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    age = st.number_input("Age", min_value=1, max_value=120, step=1)

    if st.button("Sign Up"):
        if not (name and email and password):
            st.warning("Please fill all required fields")
        else:
            existing_user = session.query(User).filter_by(email=email).first()
            if existing_user:
                st.warning("User with this email already exists")
            else:
                hashed_password = generate_password_hash(password)
                user = User(name=name, email=email, password=hashed_password, gender=gender, age=age)
                session.add(user)
                session.commit()
                st.success("✅ Account created successfully! Please login from sidebar.")

# ---------------------------
# Login
# ---------------------------
elif choice == "Login":
    if not st.session_state.logged_in:
        st.subheader("Login to Your Account")
        email = st.text_input("Email ID")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = session.query(User).filter_by(email=email).first()
            if user and check_password_hash(user.password, password):
                st.session_state.logged_in = True
                st.session_state.user_name = user.name
                st.session_state.user_email = user.email
                st.success(f"Welcome, {user.name}! 👋")
            else:
                st.error("Invalid email or password")

# ---------------------------
# Check Symptoms (Main Feature)
# ---------------------------
elif choice == "Check Symptoms":
    if not st.session_state.logged_in:
        st.warning("Please login first.")
    else:
        st.subheader(f"Hi {st.session_state.user_name}, describe your symptoms below:")
        user_input = st.text_area("Enter your symptoms:", height=150)

        if st.button("Get Probable Conditions"):
            if user_input.strip() == "":
                st.warning("Please enter your symptoms.")
            else:
                with st.spinner("Analyzing symptoms..."):
                    try:
                        response = agent_executor.run(user_input)

                        # ✅ Save chat history
                        new_entry = ChatHistory(
                            user_email=st.session_state.user_email,
                            symptom_input=user_input,
                            llm_response=response
                        )
                        session.add(new_entry)
                        session.commit()

                        st.success("✅ Analysis Complete!")
                        st.write(response)
                    except Exception as e:
                        st.error(f"Error: {e}")

# ---------------------------
# View History
# ---------------------------
elif choice == "View History":
    if not st.session_state.logged_in:
        st.warning("Please login to view your chat history.")
    else:
        st.subheader(f"🕘 Chat History for {st.session_state.user_name}")

        history = (
            session.query(ChatHistory)
            .filter_by(user_email=st.session_state.user_email)
            .order_by(ChatHistory.timestamp.desc())
            .all()
        )

        if not history:
            st.info("No previous chat history found.")
        else:
            for record in history:
                with st.expander(f"🩺 Query on {record.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"):
                    st.markdown(f"**🧠 Symptoms:** {record.symptom_input}")
                    st.markdown(f"**💡 LLM Response:** {record.llm_response}")

# ---------------------------
# Logout
# ---------------------------
elif choice == "Logout":
    if st.session_state.logged_in:
        st.session_state.logged_in = False
        st.session_state.user_name = None
        st.session_state.user_email = None
        st.success("You have been logged out successfully.")
    else:
        st.info("You are not logged in.")
