

## 🩺 Healthcare Symptom Checker

### 📘 **Overview**

The **Healthcare Symptom Checker** is an AI-powered web application that helps users identify **possible medical conditions** and **recommended next steps** based on their entered symptoms.
This tool is designed **for educational purposes only**, providing users with informative suggestions — not professional medical diagnoses.

The system combines a **medical conditions database (scraped from the NHS website)** with the reasoning capabilities of **Google Gemini LLM** to generate context-aware responses.

---

## 🚀 **Features**

✅ User Account System — Create account, login/logout securely
✅ Symptom-based condition analysis using **Gemini 2.5 Flash**
✅ Structured data from **NHS (UK) conditions**
✅ Chat History — Automatically saves and displays previous queries
✅ Clean and responsive **Streamlit UI**
✅ MySQL backend integration via SQLAlchemy ORM

---

## 🧠 **System Architecture**

```
                ┌─────────────────────────────┐
                │         User (UI)           │
                │  ─ Streamlit Frontend ─      │
                └─────────────┬───────────────┘
                              │
                              ▼
                ┌─────────────────────────────┐
                │     Flask + LangChain        │
                │  LLM (Gemini 2.5 Flash)      │
                │  SQL Agent for Querying DB   │
                └─────────────┬───────────────┘
                              │
                              ▼
                ┌─────────────────────────────┐
                │        MySQL Database        │
                │ Tables:                      │
                │  • users                     │
                │  • conditions                │
                │  • chat_history              │
                └─────────────────────────────┘
```

---

## 🧩 **Tech Stack**

| Component        | Technology                            |
| ---------------- | ------------------------------------- |
| **Frontend**     | Streamlit                             |
| **LLM**          | Google Gemini 2.5 Flash via LangChain |
| **Backend ORM**  | SQLAlchemy                            |
| **Database**     | MySQL                                 |
| **Web Scraping** | BeautifulSoup                         |
| **Security**     | Password Hashing (Werkzeug)           |

---

## ⚙️ **Installation & Setup**

### **1️⃣ Clone the Repository**

```bash
git clone https://github.com/yourusername/healthcare-symptom-checker.git
cd healthcare-symptom-checker
```

### **2️⃣ Install Dependencies**

```bash
pip install -r requirements.txt
```

Your `requirements.txt` should include:

```
streamlit
sqlalchemy
pymysql
langchain-google-genai
langchain-community
beautifulsoup4
requests
werkzeug
```

### **3️⃣ Set Up MySQL Database**

Open MySQL and run:

```sql
CREATE DATABASE medical;
USE medical;

-- Users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    gender VARCHAR(10),
    age INT
);

-- Conditions table (filled using scraper)
CREATE TABLE conditions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255),
    symptoms TEXT,
    recommendations TEXT
);

-- Chat history table
CREATE TABLE chat_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_email VARCHAR(255),
    symptom_input TEXT,
    llm_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### **4️⃣ Run the Web Scraper**

Before running the app, populate your conditions table:

```bash
python scraper.py
```

This script scrapes condition details from the **NHS website** and stores them in MySQL.

### **5️⃣ Run the Streamlit App**

```bash
streamlit run app.py
```

---

## 💬 **How It Works**

1. **User Registration & Login**
   Users sign up with their details — email, password, name, gender, and age. Passwords are securely hashed.

2. **Symptom Input**
   Users type their symptoms in natural language, such as:
   *“I have a headache and sore throat.”*

3. **AI Analysis (Gemini LLM)**
   The LLM interprets the text, queries the medical database, and provides probable conditions with advice.

4. **Chat History Storage**
   Each conversation (symptoms + LLM response) is automatically saved in the `chat_history` table.

5. **View Past Queries**
   Users can open “View History” to review all previous interactions.

---

## 📽️ **Demo Flow**

1. **Login or Create Account**
2. **Enter Symptoms**
3. **Click “Get Probable Conditions”**
4. **View AI Output + Educational Disclaimer**
5. **Check Chat History in Sidebar**

---

## 🔒 **Safety Disclaimer**

> ⚠️ This project is **for educational and informational purposes only**.
> It is **not a substitute for professional medical advice, diagnosis, or treatment**.
> Always consult a qualified healthcare provider for any medical concerns.

---

## 📈 **Future Scope**

* Integrate **voice-based symptom input**
* Add **disease prediction models** using ML
* Suggest **nearby hospitals or doctors**
* Enable **multilingual support**


