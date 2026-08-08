<div align='center'>

# 🧙‍♂️ SQL-Wizard | AI Query Generator

> **Talk to your database in plain English. Let AI handle the SQL.**

SQL-Wizard is an AI-powered web application that converts **natural language instructions into SQL queries** using **Google Gemini and LangChain**.

Users can either generate SQL queries without connecting a database or upload their own **SQLite3 database** to view, modify, and manage their data through natural language.

</div>

---

## ✨ Features

### 🤖 Natural Language → SQL

Describe what you want in simple English and SQL-Wizard generates the corresponding SQL query.

**Example:**

```text
Show all employees whose salary is greater than 50000
```

SQL-Wizard generates:

```sql
SELECT * FROM employees
WHERE salary > 50000;
```

---

## 🌐 Live Demo

🚀 **Try SQL-Wizard:**
https://sql-wizard-sus-tushhhh.streamlit.app/

---

### 🗃️ Database Support

Upload your existing **SQLite3 database** and interact with it through the application.

- 📂 Upload SQLite database
- 🔍 View tables and data
- 🤖 Generate SQL using natural language
- ▶️ Execute generated SQL queries
- ✏️ Insert, update and delete records
- 🔄 Rollback changes
- ✅ Commit changes
- 🎨 Easy to use and Appealing UI

### 💬 Query Generation Without a Database

You can also use SQL-Wizard simply as an **AI SQL query generator** without uploading a database.

Just describe your requirement and get an SQL query that you can use in your own application or database environment.

---

## 🛠️ Tech Stack

| Technology               | Purpose                                         |
| ------------------------ | ----------------------------------------------- |
| 🐍 **Python**            | Core application logic                          |
| 🔗 **LangChain**         | LLM integration and SQL workflow                |
| ✨ **Google Gemini API** | Natural language understanding & SQL generation |
| 🗃️ **SQLite3**           | Database management                             |
| 🎨 **Streamlit**         | Web interface                                   |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sus-tushhhh/SQL-Wizard.git
```

```bash
cd SQL-Wizard
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Gemini API

Create the Streamlit secrets file:

```text
.streamlit/
└── secrets.toml
```

Add your Gemini API key:

```toml
GEMINI_API_KEY = "your_api_key_here"
```

> ⚠️ Never commit your API key or `secrets.toml` to GitHub.

### 5. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 💡 Example Use Cases

SQL-Wizard can be useful for:

- 👨‍💻 Developers who frequently work with SQL
- 🎓 Students learning SQL and databases
- 📊 Data analysts exploring datasets
- 🧑‍💼 Non-technical users working with databases
- ⚡ Quickly generating SQL queries from requirements

---

## 🔐 Database Transactions

SQL-Wizard provides transaction control when modifying an uploaded SQLite database.

### Commit

Permanently saves the changes made during the current transaction.

```text
COMMIT
```

### Rollback

Reverts uncommitted changes.

```text
ROLLBACK
```

This gives users greater control over database modifications instead of automatically saving every change.

---

## ⚠️ Important Notes

- SQL-Wizard currently works with **SQLite3 databases**.
- Generated SQL should always be **reviewed before execution**, especially for `UPDATE` and `DELETE` operations.
- Keep your Gemini API key private.
- Always maintain backups of important databases before performing modifications.

---

## 🙏 Acknowledgements

Special thanks to **GRAStech** and **Ankit Mishra** for their guidance and support throughout the learning and development journey.

---

## 👨‍💻 Developer

**Tushant**  
🔗 GitHub: https://github.com/sus-tushhhh

---

⭐ If you found this project interesting, consider giving the repository a **star**!
